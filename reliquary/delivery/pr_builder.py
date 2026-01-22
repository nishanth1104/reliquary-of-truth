import os
from reliquary.schemas.state import WorkItemState


def create_pr_description(state: WorkItemState, proof_path: str) -> str:
    """
    Creates a GitHub PR description with proof artifacts summary.

    Args:
        state: Current work item state
        proof_path: Path to the proof bundle ZIP

    Returns:
        Markdown-formatted PR description
    """
    ticket = state.ticket
    evidence = state.evidence

    description = f"""## Summary

**Work Item ID:** {state.work_item_id}

{ticket.description if ticket else state.task_raw}

"""

    # Add acceptance criteria if available
    if ticket and ticket.acceptance_criteria:
        description += "## Acceptance Criteria\n\n"
        for i, criterion in enumerate(ticket.acceptance_criteria, 1):
            description += f"{i}. {criterion}\n"
        description += "\n"

    # Add test results summary
    description += "## Test Results\n\n"
    if evidence.test_runs:
        last_run = evidence.test_runs[-1]
        description += f"- **Exit Code:** {last_run.exit_code}\n"
        description += f"- **Test Runs:** {len(evidence.test_runs)}\n"
        description += f"- **Status:** {'✅ PASSED' if last_run.exit_code == 0 else '❌ FAILED'}\n"
        description += f"- **Implementation Attempts:** {state.implement_attempts}\n"
    else:
        description += "No test runs recorded.\n"

    description += "\n"

    # Add decision log summary
    if state.decision_log:
        description += "## Decision Log\n\n"
        description += f"Total events: {len(state.decision_log)}\n\n"

        # Show key events
        key_events = [e for e in state.decision_log if e.event in ["HELP_REQUESTED", "HELP_RECEIVED", "TESTS_PASSED", "TESTS_FAILED"]]
        if key_events:
            description += "### Key Events\n\n"
            for event in key_events[-5:]:  # Show last 5 key events
                description += f"- **{event.event}** (by {event.actor})\n"
        description += "\n"

    # Add proof bundle reference
    description += "## Proof Bundle\n\n"
    description += f"All proof artifacts are bundled in: `{os.path.basename(proof_path)}`\n\n"
    description += "This bundle contains:\n"
    description += "- `evidence.json` - Test execution results\n"
    description += "- `decision_log.json` - Complete decision trail\n"
    description += "- `artifacts/` - Test outputs and diffs\n\n"

    # Add footer
    description += "---\n\n"
    description += "🤖 Generated with [Reliquary of Truth](https://github.com/yourusername/reliquary-of-truth)\n"

    return description
