import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List


def log_audit_event(
    run_dir: str,
    work_item_id: str,
    event_type: str,
    actor: str,
    details: Dict[str, Any]
):
    """
    Logs an audit event to the append-only audit log.

    Args:
        run_dir: Path to the run directory
        work_item_id: Work item identifier
        event_type: Type of event (e.g., "DELIVERY_STARTED", "PROOF_VERIFIED")
        actor: Actor performing the action (e.g., "system", "owner", "human:user@example.com")
        details: Additional event details
    """
    audit_log_path = os.path.join(run_dir, "audit_events.jsonl")

    # Read existing events to compute hash chain
    previous_hash = "genesis"
    if os.path.exists(audit_log_path):
        with open(audit_log_path, 'r') as f:
            lines = f.readlines()
            if lines:
                last_event = json.loads(lines[-1])
                previous_hash = last_event.get("event_hash", "genesis")

    # Create event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "work_item_id": work_item_id,
        "event_type": event_type,
        "actor": actor,
        "details": details,
        "previous_hash": previous_hash
    }

    # Compute hash of this event (excluding event_hash field)
    event_json = json.dumps(event, sort_keys=True)
    event_hash = hashlib.sha256(event_json.encode()).hexdigest()
    event["event_hash"] = event_hash

    # Append to log
    with open(audit_log_path, 'a') as f:
        f.write(json.dumps(event) + '\n')


def verify_audit_integrity(run_dir: str) -> bool:
    """
    Verifies the integrity of the audit log by checking hash chain.

    Args:
        run_dir: Path to the run directory

    Returns:
        True if audit log is valid, False otherwise
    """
    audit_log_path = os.path.join(run_dir, "audit_events.jsonl")

    if not os.path.exists(audit_log_path):
        return True  # No audit log yet

    with open(audit_log_path, 'r') as f:
        lines = f.readlines()

    if not lines:
        return True

    previous_hash = "genesis"
    for line in lines:
        event = json.loads(line)

        # Check that previous_hash matches
        if event.get("previous_hash") != previous_hash:
            return False

        # Verify event hash
        stored_hash = event.pop("event_hash")
        event_json = json.dumps(event, sort_keys=True)
        computed_hash = hashlib.sha256(event_json.encode()).hexdigest()

        if stored_hash != computed_hash:
            return False

        previous_hash = stored_hash
        event["event_hash"] = stored_hash  # Restore for next iteration

    return True


def get_audit_events(run_dir: str) -> List[Dict[str, Any]]:
    """
    Retrieves all audit events from the log.

    Args:
        run_dir: Path to the run directory

    Returns:
        List of audit events
    """
    audit_log_path = os.path.join(run_dir, "audit_events.jsonl")

    if not os.path.exists(audit_log_path):
        return []

    events = []
    with open(audit_log_path, 'r') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    return events
