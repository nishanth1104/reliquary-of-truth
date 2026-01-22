from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from .ticket import TicketSpec
from .evidence import Evidence
from .help import HelpRequest, HelpResponse, DecisionLogEntry
from .delivery import DeliveryConfig, DeliveryResult
from .memory import MemoryAdvice
from .policy import PolicyEvaluation
from .security import SecurityScanResult


Status = Literal[
    "INTAKE",
    "NEEDS_INFO",
    "PLANNING",
    "IMPLEMENTING",
    "NEED_HELP",
    "VERIFYING",
    "IN_REVIEW",
    "CHANGES_REQUESTED",
    "APPROVED",
    "DELIVERING",
    "DELIVERED",
    "BLOCKED",
]


class WorkItemState(BaseModel):
    work_item_id: str
    repo_path: str
    task_raw: str

    status: Status = "INTAKE"

    ticket: Optional[TicketSpec] = None
    plan: List[str] = Field(default_factory=list)

    # Patch artifacts
    patch_unified_diff: Optional[str] = None
    patch_applied: bool = False

    evidence: Evidence = Field(default_factory=Evidence)

    # Review findings
    review_findings: List[str] = Field(default_factory=list)

    # Loop controls
    implement_attempts: int = 0
    max_implement_attempts: int = 4

    # Week 2: Collaboration + truth-preserving escalation
    help_requests: List[HelpRequest] = Field(default_factory=list)
    help_responses: List[HelpResponse] = Field(default_factory=list)
    decision_log: List[DecisionLogEntry] = Field(default_factory=list)
    help_cycles: int = 0
    max_help_cycles: int = 3

    blocked_reason: Optional[str] = None
    blocked_needs: List[str] = Field(default_factory=list)

    # Phase 3: Delivery & Auditability
    delivery_config: Optional[DeliveryConfig] = None
    delivery_result: Optional[DeliveryResult] = None

    # Phase 4: Organizational Memory & Learning
    memory_advice: Optional[MemoryAdvice] = None

    # Phase 5: Safety, Policy & Governance
    policy_evaluation: Optional[PolicyEvaluation] = None
    security_scans: List[SecurityScanResult] = Field(default_factory=list)
