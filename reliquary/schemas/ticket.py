from pydantic import BaseModel, Field
from typing import List, Literal, Optional

RiskLevel = Literal["low", "medium", "high"]

class TicketSpec(BaseModel):
    title: str
    problem_statement: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    out_of_scope: List[str] = Field(default_factory=list)
    domain_tags: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = "low"
    missing_info: List[str] = Field(default_factory=list)

class IntakeResult(BaseModel):
    ticket: TicketSpec
    needs_info: bool = False
    clarification_questions: List[str] = Field(default_factory=list)
