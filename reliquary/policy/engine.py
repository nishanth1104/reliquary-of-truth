import json
import os
from datetime import datetime
from typing import List
from reliquary.schemas.policy import PolicyRule, PolicyEvaluation
from reliquary.schemas.ticket import TicketSpec
from reliquary.schemas.state import WorkItemState


def load_policy(version: str = "latest") -> List[PolicyRule]:
    """
    Load policy rules from configuration file.

    Args:
        version: Policy version to load (default: "latest")

    Returns:
        List of PolicyRule objects
    """
    policy_dir = "policies"
    policy_file = f"{policy_dir}/v1.0.json" if version == "latest" else f"{policy_dir}/{version}.json"

    if not os.path.exists(policy_file):
        # Return empty policy if file doesn't exist
        return []

    with open(policy_file, 'r') as f:
        policy_data = json.load(f)

    rules = []
    for rule_data in policy_data.get("rules", []):
        rules.append(PolicyRule(**rule_data))

    return rules


def evaluate_policy(ticket: TicketSpec, patch: str, state: WorkItemState) -> PolicyEvaluation:
    """
    Evaluates policy rules against current state.

    Args:
        ticket: TicketSpec
        patch: Patch content
        state: WorkItemState

    Returns:
        PolicyEvaluation with results
    """
    from reliquary.policy.risk_classifier import classify_risk

    # Load policy rules
    policy_version = os.getenv("RELIQUARY_POLICY_VERSION", "latest")
    rules = load_policy(policy_version)

    # Classify risk
    risk_factors = classify_risk(ticket, patch)

    # Prepare evaluation context
    context = {
        "risk_factors": risk_factors,
        "evidence": state.evidence,
        "ticket": ticket,
        "patch": patch,
        "state": state
    }

    violations = []

    # Evaluate each rule
    for rule in rules:
        try:
            # Safely evaluate condition
            result = safe_eval(rule.condition, context)

            if result:
                violations.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "action": rule.action,
                    "rule_type": rule.rule_type,
                    "details": f"Condition '{rule.condition}' evaluated to True"
                })
        except Exception as e:
            violations.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "action": "warn",
                "rule_type": "audit",
                "details": f"Error evaluating rule: {str(e)}"
            })

    # Determine if passed (no blocking violations)
    blocking_violations = [v for v in violations if v["action"] == "block"]
    passed = len(blocking_violations) == 0

    return PolicyEvaluation(
        policy_version=policy_version,
        evaluated_at=datetime.utcnow().isoformat(),
        violations=violations,
        passed=passed
    )


def safe_eval(condition: str, context: dict) -> bool:
    """
    Safely evaluates a Python expression with restricted context.

    Args:
        condition: Python expression to evaluate
        context: Dictionary of variables

    Returns:
        Boolean result
    """
    # Create a safe namespace with only allowed functions
    safe_globals = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "bool": bool,
            "True": True,
            "False": False,
            "None": None
        }
    }

    try:
        result = eval(condition, safe_globals, context)
        return bool(result)
    except Exception:
        # If evaluation fails, return False
        return False
