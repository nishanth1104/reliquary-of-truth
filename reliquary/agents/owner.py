import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from reliquary.tools.fs_tools import list_tree, read_text
from reliquary.schemas.ticket import TicketSpec
from reliquary.schemas.help import HelpRequest
from reliquary.agents.helpers import pick_domain_from_ticket_text

load_dotenv()

PLAN_SYSTEM = """You are the Owning Software Engineer in the Reliquary of Truth.
Create a short execution plan (5-10 steps max) to satisfy the ticket.
Do NOT write code. Do NOT mention tools you don't have.
Keep steps verifiable. Output as JSON: {"plan": ["step1", ...]} only.
"""

PATCH_SYSTEM = """You are the Owning Software Engineer in the Reliquary of Truth.
You must generate complete modified file contents to implement the ticket.
Rules:
- Only modify files that exist unless you need to add a new file.
- Add/modify tests when appropriate.
- Keep changes minimal.
- Output JSON ONLY in this format:
{
  "files": [
    {"path": "app.py", "content": "full file content here..."},
    {"path": "tests/test_app.py", "content": "full file content here..."}
  ]
}
- Do NOT include markdown or code fences.
- Include the COMPLETE file content for each file you modify.
"""

HELP_DECIDER_SYSTEM = """You are the Owning Software Engineer in the Reliquary of Truth.

Decide if you have enough information to safely implement the ticket with minimal changes.

If the repository appears to be a skeleton (missing key files) OR the ticket requires framework-specific
knowledge not present in the provided context, you should request help from the appropriate specialist.

Return JSON ONLY:
{
  "need_help": true|false,
  "question": "A single, concrete question to ask a specialist (no code).",
  "why": "Short reason"
}
"""


def _strip_code_fences(txt: str) -> str:
    txt = (txt or "").strip()
    if txt.startswith("```"):
        lines = [l for l in txt.split("\n") if l.strip() not in ("```", "```json")]
        txt = "\n".join(lines).strip()
    return txt


def maybe_request_help(repo_path: str, ticket: TicketSpec, attempt: int) -> HelpRequest | None:
    """Week 2: Ask whether we should request specialist help before writing a patch.

    Goal: avoid 'guessing under pressure'. If we are missing repo context, we ask a specialist.
    """
    import json

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0)

    files = list_tree(repo_path, max_files=200)
    ticket_text = (
        f"TITLE: {ticket.title}\n"
        f"PROBLEM: {ticket.problem_statement}\n"
        f"ACCEPTANCE: {ticket.acceptance_criteria}\n"
        f"CONSTRAINTS: {ticket.constraints}\n"
        f"OUT_OF_SCOPE: {ticket.out_of_scope}\n"
    )

    user = {
        "ticket": ticket_text,
        "repo_files": files,
        "note": "If key entrypoints/framework are unclear, request help.",
    }

    resp = llm.invoke([("system", HELP_DECIDER_SYSTEM), ("user", json.dumps(user))])
    txt = _strip_code_fences(resp.content)
    data = json.loads(txt)

    if not data.get("need_help"):
        return None

    domain = pick_domain_from_ticket_text(ticket.problem_statement + " " + " ".join(ticket.domain_tags))
    question = (data.get("question") or "").strip() or "What is the expected tech stack / key entrypoint files for this repo?"
    why = (data.get("why") or "Need more context").strip()

    context = f"WHY: {why}\n\nTICKET:\n{ticket_text}\n\nREPO_FILES:\n{files}"

    return HelpRequest(
        request_id=f"help_{attempt}",
        domain=domain,
        question=question,
        context=context,
        attempt=attempt,
    )


def make_plan(ticket: TicketSpec) -> list[str]:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0)

    payload = {
        "title": ticket.title,
        "problem_statement": ticket.problem_statement,
        "acceptance_criteria": ticket.acceptance_criteria,
        "constraints": ticket.constraints,
        "out_of_scope": ticket.out_of_scope,
    }
    resp = llm.invoke([("system", PLAN_SYSTEM), ("user", str(payload))])

    import json
    return json.loads(resp.content)["plan"]


def generate_patch(repo_path: str, ticket: TicketSpec) -> str:
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0)

    files = list_tree(repo_path, max_files=200)

    # Provide key file contents if they exist (Week 1-style: keep small)
    context_parts = []
    for rel in files:
        if rel in ("app.py", "tests/test_app.py"):
            context_parts.append(f"FILE: {rel}\n---\n{read_text(repo_path, rel)}\n---\n")

    ctx = "\n".join(context_parts) if context_parts else "No file contents provided."

    ticket_text = (
        f"TITLE: {ticket.title}\n"
        f"PROBLEM: {ticket.problem_statement}\n"
        f"ACCEPTANCE: {ticket.acceptance_criteria}\n"
        f"CONSTRAINTS: {ticket.constraints}\n"
        f"OUT_OF_SCOPE: {ticket.out_of_scope}\n"
    )

    user_msg = f"{ticket_text}\n\nREPO_FILES:\n{files}\n\nCONTEXT:\n{ctx}\n\nReturn JSON with modified files."
    resp = llm.invoke([("system", PATCH_SYSTEM), ("user", user_msg)])
    content = _strip_code_fences(resp.content)

    data = json.loads(content)

    # Generate unified diffs using git diff --no-index for each file
    all_diffs = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for file_mod in data["files"]:
            file_path = file_mod["path"]
            file_content = file_mod["content"]

            temp_file = Path(tmpdir) / "new"
            temp_file.write_text(file_content, encoding="utf-8")

            orig_file = Path(repo_path) / file_path

            result = subprocess.run(
                ["git", "diff", "--no-index", str(orig_file), str(temp_file)],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                diff_lines = result.stdout.split("\n")
                fixed = []
                for line in diff_lines:
                    if line.startswith("diff --git"):
                        fixed.append(f"diff --git a/{file_path} b/{file_path}")
                    elif line.startswith("--- "):
                        fixed.append(f"--- a/{file_path}")
                    elif line.startswith("+++ "):
                        fixed.append(f"+++ b/{file_path}")
                    else:
                        fixed.append(line)
                all_diffs.append("\n".join(fixed))

    return "\n".join(all_diffs) if all_diffs else "No changes detected"
