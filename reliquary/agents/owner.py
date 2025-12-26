import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from reliquary.tools.fs_tools import list_tree, read_text
from reliquary.schemas.ticket import TicketSpec

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
    plan_json = resp.content
    # simple parse without extra deps
    import json
    return json.loads(plan_json)["plan"]

def generate_patch(repo_path: str, ticket: TicketSpec) -> str:
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0)

    files = list_tree(repo_path, max_files=200)

    # Provide key file contents if they exist (week1: keep small)
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
    content = resp.content.strip()

    # Remove markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        lines = [l for l in lines if not l.strip() in ("```", "```json")]
        content = "\n".join(lines)

    # Parse JSON response
    data = json.loads(content)

    # Generate diff for each file using git diff --no-index
    all_diffs = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for file_mod in data["files"]:
            file_path = file_mod["path"]
            file_content = file_mod["content"]

            # Write new content to temp file
            temp_file = Path(tmpdir) / "new"
            temp_file.write_text(file_content, encoding="utf-8")

            # Get original file path
            orig_file = Path(repo_path) / file_path

            # Generate diff
            result = subprocess.run(
                ["git", "diff", "--no-index", str(orig_file), str(temp_file)],
                capture_output=True,
                text=True
            )

            # git diff --no-index returns exit code 1 when there are differences (which is expected)
            if result.stdout:
                # Fix the paths in the diff to use proper git format
                diff_lines = result.stdout.split("\n")
                fixed_diff = []
                for line in diff_lines:
                    if line.startswith("---"):
                        fixed_diff.append(f"--- a/{file_path}")
                    elif line.startswith("+++"):
                        fixed_diff.append(f"+++ b/{file_path}")
                    elif line.startswith("diff --git"):
                        fixed_diff.append(f"diff --git a/{file_path} b/{file_path}")
                    else:
                        fixed_diff.append(line)
                all_diffs.append("\n".join(fixed_diff))

    return "\n".join(all_diffs) if all_diffs else "No changes detected"
