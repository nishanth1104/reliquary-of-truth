from pydantic import BaseModel
from typing import List, Optional, Literal

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


class RunSummary(BaseModel):
    work_item_id: str
    repo_name: str
    task_raw: str
    ticket_title: str
    domain_tags: List[str]
    risk_level: str
    final_status: Status
    implement_attempts: int
    test_exit_code: Optional[int]
    failure_mode: Optional[str]  # "tests_failed", "patch_apply_failed", etc.
    completed_at: str
    run_dir: str


class PatternMatch(BaseModel):
    work_item_id: str
    similarity_score: float
    ticket_title: str
    final_status: Status
    key_lessons: List[str]


class MemoryAdvice(BaseModel):
    similar_successes: List[PatternMatch]
    similar_failures: List[PatternMatch]
    regression_risks: List[dict]
    recommendations: List[str]
