import json
from datetime import datetime
from reliquary.schemas.state import WorkItemState
from reliquary.schemas.human_interaction import HumanAction
from reliquary.storage.run_store import write_json


def process_info_provision(work_item_id: str, answer: str, run_dir: str) -> WorkItemState:
    """
    Process information provided by human.

    Args:
        work_item_id: Work item ID
        answer: Human-provided answer
        run_dir: Run directory path

    Returns:
        Updated WorkItemState
    """
    # Load state
    state_file = f"{run_dir}/state_paused.json"
    with open(state_file, 'r') as f:
        state_data = json.load(f)

    state = WorkItemState.model_validate(state_data)

    # Update ticket with provided info
    if state.ticket:
        state.ticket.description += f"\n\nAdditional Info: {answer}"

    # Change status to resume workflow
    state.status = "PLANNING"
    state.blocked_reason = None
    state.blocked_needs = []

    # Log human action
    action = HumanAction(
        action_id=f"{work_item_id}_info",
        work_item_id=work_item_id,
        actor="human",
        action_type="provide_info",
        timestamp=datetime.utcnow().isoformat(),
        details={"answer": answer}
    )

    # Save updated state
    write_json(f"{run_dir}/state_resumed.json", state.model_dump())

    return state


def process_approval(work_item_id: str, approved: bool, reason: str, run_dir: str) -> WorkItemState:
    """
    Process human approval/rejection.

    Args:
        work_item_id: Work item ID
        approved: Whether approved
        reason: Reason for decision
        run_dir: Run directory path

    Returns:
        Updated WorkItemState
    """
    # Load state
    state_file = f"{run_dir}/state_paused.json"
    with open(state_file, 'r') as f:
        state_data = json.load(f)

    state = WorkItemState.model_validate(state_data)

    # Log human action
    action = HumanAction(
        action_id=f"{work_item_id}_approval",
        work_item_id=work_item_id,
        actor="human",
        action_type="approve" if approved else "reject",
        timestamp=datetime.utcnow().isoformat(),
        details={"reason": reason}
    )

    if approved:
        state.status = "DELIVERING"
    else:
        state.status = "BLOCKED"
        state.blocked_reason = f"Human rejected: {reason}"

    # Save updated state
    write_json(f"{run_dir}/state_after_approval.json", state.model_dump())

    return state
