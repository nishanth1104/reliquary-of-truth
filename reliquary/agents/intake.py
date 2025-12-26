import json
from dataclasses import dataclass
from typing import List

from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field

from reliquary.schemas.ticket import TicketSpec


@dataclass
class IntakeResult:
    ticket: TicketSpec
    needs_info: bool
    clarification_questions: List[str]


class _LLMOutWrapped(BaseModel):
    ticket: TicketSpec
    needs_info: bool = False
    clarification_questions: List[str] = Field(default_factory=list)


class _LLMOutFlat(BaseModel):
    # When the model returns TicketSpec directly (flat JSON)
    title: str
    problem_statement: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    out_of_scope: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    domain_tags: List[str] = Field(default_factory=list)

    needs_info: bool = False
    clarification_questions: List[str] = Field(default_factory=list)


def _parse_intake_json(txt: str) -> _LLMOutWrapped:
    """
    Accept both:
      1) Wrapped output: { "ticket": {...}, "needs_info": ..., "clarification_questions": [...] }
      2) Flat output:   { "title": ..., "description": ..., ... }  (TicketSpec fields at top level)
    """
    data = json.loads(txt)

    # Wrapped format
    if isinstance(data, dict) and "ticket" in data:
        return _LLMOutWrapped.model_validate(data)

    # Flat format -> wrap it
    flat = _LLMOutFlat.model_validate(data)
    ticket = TicketSpec(
        title=flat.title,
        problem_statement=flat.problem_statement,
        acceptance_criteria=flat.acceptance_criteria,
        constraints=flat.constraints,
        out_of_scope=flat.out_of_scope,
        risk_level=flat.risk_level,
        domain_tags=flat.domain_tags,
    )
    return _LLMOutWrapped(
        ticket=ticket,
        needs_info=flat.needs_info,
        clarification_questions=flat.clarification_questions,
    )


def intake(task_raw: str) -> IntakeResult:
    """
    Stage 1: Turn user task into a structured TicketSpec.
    """
    model = "gpt-4o-mini"
    llm = ChatOpenAI(model=model, temperature=0.0)

    prompt = f"""
You are an Intake Agent in a software engineering organization.
Convert USER_TASK into a JSON object.

Return either:
A) Wrapped format:
{{
  "ticket": {{
    "title": "...",
    "problem_statement": "...",
    "acceptance_criteria": ["..."],
    "constraints": ["..."],
    "out_of_scope": ["..."],
    "risk_level": "low|medium|high",
    "domain_tags": ["..."]
  }},
  "needs_info": false,
  "clarification_questions": []
}}

OR
B) Flat format (Ticket fields at top level) if you cannot wrap.

Rules:
- Output JSON ONLY. No markdown, no commentary.
- Keep acceptance criteria concrete and testable.
- If missing critical info, set needs_info=true and ask specific questions.

USER_TASK:
{task_raw}
""".strip()

    resp = llm.invoke(prompt)
    txt = resp.content.strip()

    parsed = _parse_intake_json(txt)

    return IntakeResult(
        ticket=parsed.ticket,
        needs_info=parsed.needs_info,
        clarification_questions=parsed.clarification_questions,
    )
