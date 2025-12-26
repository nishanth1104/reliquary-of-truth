from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from .ticket import TicketSpec
from .evidence import Evidence

Status = Literal[
    "INTAKE",
    "NEEDS_INFO",
    "PLANNING",
    "IMPLEMENTING",
    "VERIFYING",
    "IN_REVIEW",
    "CHANGES_REQUESTED",
    "APPROVED",
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

    blocked_reason: Optional[str] = None
    blocked_needs: List[str] = Field(default_factory=list)
