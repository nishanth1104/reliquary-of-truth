from reliquary.schemas.ticket import TicketSpec

def quick_requirements_review(ticket: TicketSpec, diff_text: str) -> list[str]:
    findings = []
    if not diff_text.strip().startswith("diff --git"):
        findings.append("Patch is not a valid unified diff starting with 'diff --git'.")
    if "/health" in ticket.problem_statement.lower() or any("/health" in a.lower() for a in ticket.acceptance_criteria):
        if "/health" not in diff_text:
            findings.append("Ticket mentions /health but diff does not mention '/health'.")
    return findings
