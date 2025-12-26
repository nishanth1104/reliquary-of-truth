from typing import Dict, Any
import uuid

from langgraph.graph import StateGraph, END

from reliquary.schemas.state import WorkItemState
from reliquary.agents.intake import intake
from reliquary.agents.owner import make_plan, generate_patch
from reliquary.agents.review import quick_requirements_review

from reliquary.tools.git_tools import create_patch_file, apply_patch, get_diff
from reliquary.tools.exec_tools import run_command
from reliquary.storage.run_store import new_run_dir, write_json, write_text
from reliquary.policy.rules import evidence_gate_can_finalize

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
        plan = make_plan(state.ticket)
        return {"plan": plan, "status": "IMPLEMENTING"}

    def n_implement(state: WorkItemState) -> Dict[str, Any]:
        if state.implement_attempts >= state.max_implement_attempts:
            return {
                "status": "BLOCKED",
                "blocked_reason": "Exceeded max implementation attempts",
                "blocked_needs": ["Human review / adjust ticket scope"],
            }

        patch = generate_patch(state.repo_path, state.ticket)
        return {
            "patch_unified_diff": patch,
            "implement_attempts": state.implement_attempts + 1,
            "status": "VERIFYING",
        }

    def n_verify(state: WorkItemState) -> Dict[str, Any]:
        # Create run dir and artifacts
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

        # Run pytest (proof) - use python -m pytest to ensure it uses the venv
        test_run = run_command(
            repo_path=state.repo_path,
            command=".venv/Scripts/python -m pytest -q",
            out_dir=artifacts,
            label=f"pytest_attempt_{state.implement_attempts}",
        )

        new_evidence = state.evidence.model_copy(deep=True)
        new_evidence.test_runs.append(test_run)

        # Save diff + report
        diff_text = get_diff(state.repo_path)
        write_text(f"{artifacts}\\git.diff.txt", diff_text)
        write_json(f"{run_dir}\\evidence.json", new_evidence.model_dump())

        if evidence_gate_can_finalize(test_run.exit_code):
            return {"evidence": new_evidence, "patch_applied": True, "status": "DELIVERED"}
        else:
            return {
                "evidence": new_evidence,
                "review_findings": state.review_findings + ["Tests failed; see evidence logs."],
                "status": "IMPLEMENTING",
            }

    g.add_node("intake", n_intake)
    g.add_node("plan", n_plan)
    g.add_node("implement", n_implement)
    g.add_node("verify", n_verify)

    g.set_entry_point("intake")

    def route_after_intake(state: WorkItemState):
        if state.status == "NEEDS_INFO":
            return END
        return "plan"

    def route_after_plan(state: WorkItemState):
        return "implement"

    def route_after_implement(state: WorkItemState):
        if state.status == "BLOCKED":
            return END
        return "verify"

    def route_after_verify(state: WorkItemState):
        if state.status == "DELIVERED":
            return END
        if state.status in ("BLOCKED", "NEEDS_INFO"):
            return END
        return "implement"

    g.add_conditional_edges("intake", route_after_intake)
    g.add_conditional_edges("plan", route_after_plan)
    g.add_conditional_edges("implement", route_after_implement)
    g.add_conditional_edges("verify", route_after_verify)

    return g.compile()

def new_state(repo_path: str, task_raw: str) -> WorkItemState:
    return WorkItemState(
        work_item_id=str(uuid.uuid4())[:8],
        repo_path=repo_path,
        task_raw=task_raw,
        status="INTAKE",
    )
