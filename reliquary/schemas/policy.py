from pydantic import BaseModel
from typing import Literal, List


class PolicyRule(BaseModel):
    rule_id: str
    name: str
    rule_type: Literal["gate", "warning", "audit"]
    condition: str  # Python expression
    action: Literal["block", "warn", "log"]


class PolicyEvaluation(BaseModel):
    policy_version: str
    evaluated_at: str
    violations: List[dict]
    passed: bool
