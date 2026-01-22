from typing import Dict, Any
import uuid

from langgraph.graph import StateGraph, END

from reliquary.schemas.state import WorkItemState
from reliquary.schemas.delivery import DeliveryConfig
from reliquary.agents.intake import intake
from reliquary.agents.owner import make_plan, generate_patch, maybe_request_help
from reliquary.agents.review import quick_requirements_review
from reliquary.agents.helpers import provide_help
from reliquary.schemas.help import DecisionLogEntry

from reliquary.tools.git_tools import create_patch_file, apply_patch, get_diff
from reliquary.tools.exec_tools import run_command
from reliquary.storage.run_store import new_run_dir, write_json, write_text
from reliquary.storage.audit_store import log_audit_event
from reliquary.policy.rules import evidence_gate_can_finalize
from reliquary.delivery.deliverer import deliver_local_patch, deliver_github_pr, deliver_direct_push
from reliquary.memory.indexer import index_run
from reliquary.memory.store import save_run_summary
from reliquary.memory.advisor import get_memory_advice
from reliquary.policy.engine import evaluate_policy
from reliquary.security.scanners import run_bandit, detect_secrets


def build_graph():
    g = StateGraph(WorkItemState)

    def n_intake(state: WorkItemState) -> Dict[str, Any]:
        r = intake(state.task_raw)
        if r.needs_info:
            return {
                "status": "NEEDS_INFO",
                "ticket": r.ticket,
                "blocked_reason": "Need clarification from user",
                "blocked_needs": r.clarification_questions,
            }
        return {"ticket": r.ticket, "status": "PLANNING"}

    def n_plan(state: WorkItemState) -> Dict[str, Any]:
        # Get memory advice
        memory_advice = get_memory_advice(state.ticket, state.repo_path)

        # Log memory consultation
        dl = state.decision_log + [
            DecisionLogEntry(
                event="MEMORY_CONSULTED",
                actor="system",
                details={
                    "similar_successes_count": len(memory_advice.similar_successes),
                    "similar_failures_count": len(memory_advice.similar_failures),
                    "recommendations": memory_advice.recommendations
                }
            )
        ]

        plan = make_plan(state.ticket)
        return {
            "plan": plan,
            "memory_advice": memory_advice,
            "decision_log": dl,
            "status": "POLICY_CHECK"
        }

    def n_policy_check(state: WorkItemState) -> Dict[str, Any]:
        # Policy check happens before implementation
        # For now, we'll do a basic check; full check after patch generation
        return {"status": "IMPLEMENTING"}

    def n_security_scan(state: WorkItemState) -> Dict[str, Any]:
        # Run security scans on patch
        secrets_scan = detect_secrets(state.patch_unified_diff or "")

        scans = [secrets_scan]

        # Log scan results
        dl = state.decision_log + [
            DecisionLogEntry(
                event="SECURITY_SCAN_COMPLETED",
                actor="system",
                details={
                    "scans_run": len(scans),
                    "all_passed": all(s.passed for s in scans),
                    "findings_count": sum(len(s.findings) for s in scans)
                }
            )
        ]

        # Block if critical findings
        if not secrets_scan.passed:
            return {
                "security_scans": scans,
                "decision_log": dl,
                "status": "BLOCKED",
                "blocked_reason": "Security scans failed - potential secrets detected",
                "blocked_needs": ["Review and remove secrets from patch"]
            }

        return {
            "security_scans": scans,
            "decision_log": dl,
            "status": "VERIFYING"
        }

    def n_implement(state: WorkItemState) -> Dict[str, Any]:
        if state.implement_attempts >= state.max_implement_attempts:
            dl = state.decision_log + [
                DecisionLogEntry(
                    event="BLOCKED",
                    actor="system",
                    details={"reason": "Exceeded max implementation attempts"},
                )
            ]
            return {
                "status": "BLOCKED",
                "blocked_reason": "Exceeded max implementation attempts",
                "blocked_needs": ["Human review / adjust ticket scope"],
                "decision_log": dl,
            }

        # If there is a help request that hasn't been answered, route to help.
        pending_help = len(state.help_requests) > len(state.help_responses)
        if pending_help:
            return {"status": "NEED_HELP"}

        # Week 2: Ask for specialist help BEFORE guessing.
        if state.help_cycles < state.max_help_cycles:
            help_req = maybe_request_help(state.repo_path, state.ticket, state.implement_attempts + 1)
            if help_req is not None:
                dl = state.decision_log + [
                    DecisionLogEntry(
                        event="HELP_REQUESTED",
                        actor="owner",
                        details={
                            "request_id": help_req.request_id,
                            "domain": help_req.domain,
                            "question": help_req.question,
                            "attempt": help_req.attempt,
                        },
                    )
                ]
                return {
                    "help_requests": state.help_requests + [help_req],
                    "decision_log": dl,
                    "status": "NEED_HELP",
                }

        # Otherwise proceed with patch generation.
        patch = generate_patch(state.repo_path, state.ticket)
        dl = state.decision_log + [
            DecisionLogEntry(
                event="PATCH_PROPOSED",
                actor="owner",
                details={"attempt": state.implement_attempts + 1},
            )
        ]
        return {
            "patch_unified_diff": patch,
            "implement_attempts": state.implement_attempts + 1,
            "decision_log": dl,
            "status": "VERIFYING",
        }

    def n_help(state: WorkItemState) -> Dict[str, Any]:
        # Find newest help request without a response.
        if len(state.help_requests) <= len(state.help_responses):
            return {"status": "IMPLEMENTING"}

        if state.help_cycles >= state.max_help_cycles:
            dl = state.decision_log + [
                DecisionLogEntry(
                    event="BLOCKED",
                    actor="system",
                    details={"reason": "Exceeded max help cycles"},
                )
            ]
            return {
                "status": "BLOCKED",
                "blocked_reason": "Exceeded max help cycles",
                "blocked_needs": ["Human input on repo stack / requirements"],
                "decision_log": dl,
            }

        req = state.help_requests[len(state.help_responses)]
        resp = provide_help(req)

        dl = state.decision_log + [
            DecisionLogEntry(
                event="HELP_RECEIVED",
                actor=f"helper:{resp.domain}",
                details={
                    "request_id": resp.request_id,
                    "confidence": resp.confidence,
                    "needs_more_info": resp.needs_more_info,
                },
            )
        ]

        return {
            "help_responses": state.help_responses + [resp],
            "help_cycles": state.help_cycles + 1,
            "decision_log": dl,
            "status": "IMPLEMENTING",
        }

    def n_verify(state: WorkItemState) -> Dict[str, Any]:
        from pathlib import Path

        run_dir = new_run_dir("runs", state.work_item_id)
        artifacts = f"{run_dir}\\artifacts"
        write_json(f"{run_dir}\\state_before_verify.json", state.model_dump())

        # Quick requirements sanity check
        findings = quick_requirements_review(state.ticket, state.patch_unified_diff)
        if findings:
            return {
                "review_findings": state.review_findings + findings,
                "status": "IMPLEMENTING",
            }

        patch_path = str(Path(f"{artifacts}\\change.patch").resolve())
        create_patch_file(patch_path, state.patch_unified_diff)

        try:
            apply_patch(state.repo_path, patch_path)
        except Exception as e:
            return {
                "review_findings": state.review_findings + [f"Patch apply failed: {e}"],
                "status": "IMPLEMENTING",
            }

        # Proof: run tests
        test_run = run_command(
            repo_path=state.repo_path,
            command=".venv/Scripts/python -m pytest -q",
            out_dir=artifacts,
            label=f"pytest_attempt_{state.implement_attempts}",
        )

        new_evidence = state.evidence.model_copy(deep=True)
        new_evidence.test_runs.append(test_run)

        diff_text = get_diff(state.repo_path)
        write_text(f"{artifacts}\\git.diff.txt", diff_text)

        # Save artifacts
        write_json(f"{run_dir}\\evidence.json", new_evidence.model_dump())
        write_json(f"{run_dir}\\decision_log.json", [e.model_dump() for e in state.decision_log])
        write_json(f"{run_dir}\\help_requests.json", [r.model_dump() for r in state.help_requests])
        write_json(f"{run_dir}\\help_responses.json", [r.model_dump() for r in state.help_responses])

        if evidence_gate_can_finalize(test_run.exit_code):
            dl = state.decision_log + [
                DecisionLogEntry(
                    event="TESTS_PASSED",
                    actor="system",
                    details={"exit_code": test_run.exit_code},
                )
            ]
            # Log audit event
            log_audit_event(run_dir, state.work_item_id, "TESTS_PASSED", "system", {"exit_code": test_run.exit_code})
            return {"evidence": new_evidence, "patch_applied": True, "decision_log": dl, "status": "DELIVERING"}

        dl = state.decision_log + [
            DecisionLogEntry(
                event="TESTS_FAILED",
                actor="system",
                details={"exit_code": test_run.exit_code},
            )
        ]
        # Log audit event
        log_audit_event(run_dir, state.work_item_id, "TESTS_FAILED", "system", {"exit_code": test_run.exit_code})
        return {
            "evidence": new_evidence,
            "decision_log": dl,
            "review_findings": state.review_findings + ["Tests failed; see evidence logs."],
            "status": "IMPLEMENTING",
        }

    def n_deliver(state: WorkItemState) -> Dict[str, Any]:
        run_dir = new_run_dir("runs", state.work_item_id)

        # Log delivery start
        log_audit_event(run_dir, state.work_item_id, "DELIVERY_STARTED", "system", {"mode": state.delivery_config.mode if state.delivery_config else "local_patch"})

        # Determine delivery mode
        config = state.delivery_config or DeliveryConfig()

        # Execute delivery
        if config.mode == "local_patch":
            result = deliver_local_patch(state, run_dir, config)
        elif config.mode == "github_pr":
            result = deliver_github_pr(state, run_dir, config)
        elif config.mode == "direct_push":
            result = deliver_direct_push(state, run_dir, config)
        else:
            result = deliver_local_patch(state, run_dir, config)

        # Save delivery result
        write_json(f"{run_dir}\\delivery_result.json", result.model_dump())

        # Log delivery completion
        log_audit_event(run_dir, state.work_item_id, "DELIVERY_COMPLETED", "system", {"status": result.status, "mode": result.mode})

        # Index run to memory
        run_summary = index_run(state, run_dir)
        save_run_summary(run_summary)

        return {
            "delivery_result": result,
            "status": "DELIVERED" if result.status == "delivered" else "BLOCKED"
        }

    g.add_node("intake", n_intake)
    g.add_node("plan", n_plan)
    g.add_node("policy_check", n_policy_check)
    g.add_node("implement", n_implement)
    g.add_node("help", n_help)
    g.add_node("security_scan", n_security_scan)
    g.add_node("verify", n_verify)
    g.add_node("deliver", n_deliver)

    g.set_entry_point("intake")

    def route_after_intake(state: WorkItemState):
        if state.status == "NEEDS_INFO":
            return END
        return "plan"

    def route_after_plan(state: WorkItemState):
        if state.status == "POLICY_CHECK":
            return "policy_check"
        return "implement"

    def route_after_policy_check(state: WorkItemState):
        if state.status == "BLOCKED":
            return END
        return "implement"

    def route_after_implement(state: WorkItemState):
        if state.status == "NEED_HELP":
            return "help"
        if state.status == "BLOCKED":
            return END
        return "security_scan"

    def route_after_security_scan(state: WorkItemState):
        if state.status == "BLOCKED":
            return END
        return "verify"

    def route_after_help(state: WorkItemState):
        if state.status in ("BLOCKED", "NEEDS_INFO"):
            return END
        return "implement"

    def route_after_verify(state: WorkItemState):
        if state.status == "DELIVERING":
            return "deliver"
        if state.status in ("BLOCKED", "NEEDS_INFO"):
            return END
        return "implement"

    def route_after_deliver(state: WorkItemState):
        return END

    g.add_conditional_edges("intake", route_after_intake)
    g.add_conditional_edges("plan", route_after_plan)
    g.add_conditional_edges("policy_check", route_after_policy_check)
    g.add_conditional_edges("implement", route_after_implement)
    g.add_conditional_edges("help", route_after_help)
    g.add_conditional_edges("security_scan", route_after_security_scan)
    g.add_conditional_edges("verify", route_after_verify)
    g.add_conditional_edges("deliver", route_after_deliver)

    return g.compile()


def new_state(repo_path: str, task_raw: str) -> WorkItemState:
    return WorkItemState(
        work_item_id=str(uuid.uuid4())[:8],
        repo_path=repo_path,
        task_raw=task_raw,
        status="INTAKE",
    )
