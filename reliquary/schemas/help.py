from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


HelpDomain = Literal["frontend", "backend", "security", "devops", "general"]


class HelpRequest(BaseModel):
    request_id: str
    domain: HelpDomain = "general"
    question: str
    context: str = ""
    attempt: int = 0


class HelpResponse(BaseModel):
    request_id: str
    domain: HelpDomain = "general"
    advice: List[str] = Field(default_factory=list)
    checks: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    needs_more_info: List[str] = Field(default_factory=list)
    # Optional confidence if the model provides it; safe default.
    confidence: Optional[Literal["low", "medium", "high"]] = None


DecisionEvent = Literal[
    "HELP_REQUESTED",
    "HELP_RECEIVED",
    "PATCH_PROPOSED",
    "PATCH_APPLIED",
    "TESTS_PASSED",
    "TESTS_FAILED",
    "BLOCKED",
]


class DecisionLogEntry(BaseModel):
    event: DecisionEvent
    actor: str
    details: Dict[str, Any] = Field(default_factory=dict)
