import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from reliquary.schemas.help import HelpDomain, HelpRequest, HelpResponse

load_dotenv()

HELPER_SYSTEM = """You are a specialist Software Engineer in the Reliquary of Truth.

You are NOT allowed to generate patches or code diffs. You must ONLY provide advice.

Your job:
1) Answer the question with practical guidance.
2) Provide a small set of checks (commands/tests/logs) the owning engineer can run.
3) Call out risks and footguns.
4) If information is missing, list exactly what is missing.
5) Provide an optional confidence: low|medium|high.

Return JSON ONLY in the following schema:
{
  "advice": ["..."],
  "checks": ["..."],
  "risks": ["..."],
  "needs_more_info": ["..."],
  "confidence": "low|medium|high"
}
"""


def _llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)


def _strip_code_fences(txt: str) -> str:
    txt = (txt or "").strip()
    if txt.startswith("```"):
        lines = [l for l in txt.split("\n") if l.strip() not in ("```", "```json")]
        txt = "\n".join(lines).strip()
    return txt


def provide_help(req: HelpRequest) -> HelpResponse:
    llm = _llm()
    user = {
        "domain": req.domain,
        "question": req.question,
        "context": req.context,
        "attempt": req.attempt,
    }
    resp = llm.invoke([("system", HELPER_SYSTEM), ("user", json.dumps(user))])
    txt = _strip_code_fences(resp.content)
    data = json.loads(txt)

    conf = data.get("confidence")
    if conf not in (None, "low", "medium", "high"):
        conf = None

    return HelpResponse(
        request_id=req.request_id,
        domain=req.domain,
        advice=data.get("advice", []) or [],
        checks=data.get("checks", []) or [],
        risks=data.get("risks", []) or [],
        needs_more_info=data.get("needs_more_info", []) or [],
        confidence=conf,
    )


def pick_domain_from_ticket_text(text: str) -> HelpDomain:
    t = (text or "").lower()

    if any(k in t for k in ["react", "ui", "frontend", "css", "html", "component", "nextjs", "vite"]):
        return "frontend"

    if any(k in t for k in ["api", "endpoint", "database", "backend", "server", "fastapi", "flask", "express"]):
        return "backend"

    if any(k in t for k in ["auth", "security", "csrf", "xss", "injection", "secrets", "vulnerability", "oauth"]):
        return "security"

    if any(k in t for k in ["docker", "ci", "pipeline", "deploy", "k8s", "kubernetes", "devops", "terraform"]):
        return "devops"

    return "general"
