import os
from datetime import datetime
from typing import Optional
from reliquary.schemas.state import WorkItemState
from reliquary.schemas.memory import RunSummary


def extract_failure_mode(state: WorkItemState) -> Optional[str]:
    """
    Classifies the failure mode based on state.

    Args:
        state: WorkItemState

    Returns:
        Failure mode string or None if successful
    """
    if state.status == "DELIVERED":
        return None

    if state.status == "BLOCKED":
        if "max implementation attempts" in (state.blocked_reason or "").lower():
            return "max_attempts_exceeded"
        if "max help cycles" in (state.blocked_reason or "").lower():
            return "help_exhausted"
        return "blocked_unknown"

    if state.status == "NEEDS_INFO":
        return "needs_clarification"

    # Check review findings
    if state.review_findings:
        for finding in state.review_findings:
            if "patch apply failed" in finding.lower():
                return "patch_apply_failed"
            if "tests failed" in finding.lower():
                return "tests_failed"

    return "unknown"


def index_run(state: WorkItemState, run_dir: str) -> RunSummary:
    """
    Extracts key features from a run and creates a RunSummary.

    Args:
        state: WorkItemState
        run_dir: Path to run directory

    Returns:
        RunSummary object
    """
    # Extract repo name from path
    repo_name = os.path.basename(state.repo_path)

    # Extract ticket title
    ticket_title = state.ticket.title if state.ticket else state.task_raw[:100]

    # Extract domain tags (simplified - could be enhanced with NLP)
    domain_tags = []
    if state.ticket and state.ticket.domain_tags:
        domain_tags = state.ticket.domain_tags
    else:
        # Simple keyword extraction
        keywords = ["auth", "api", "database", "frontend", "backend", "test"]
        task_lower = state.task_raw.lower()
        domain_tags = [kw for kw in keywords if kw in task_lower]

    # Determine risk level
    risk_level = "low"
    if state.ticket and hasattr(state.ticket, 'risk_level'):
        risk_level = state.ticket.risk_level
    elif state.implement_attempts > 2:
        risk_level = "medium"

    # Get test exit code
    test_exit_code = None
    if state.evidence.test_runs:
        test_exit_code = state.evidence.test_runs[-1].exit_code

    return RunSummary(
        work_item_id=state.work_item_id,
        repo_name=repo_name,
        task_raw=state.task_raw,
        ticket_title=ticket_title,
        domain_tags=domain_tags,
        risk_level=risk_level,
        final_status=state.status,
        implement_attempts=state.implement_attempts,
        test_exit_code=test_exit_code,
        failure_mode=extract_failure_mode(state),
        completed_at=datetime.utcnow().isoformat(),
        run_dir=run_dir
    )
