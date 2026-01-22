from typing import List
from reliquary.schemas.ticket import TicketSpec
from reliquary.schemas.memory import PatternMatch
from reliquary.memory.store import query_runs


def find_similar_tasks(ticket: TicketSpec, repo_path: str) -> List[PatternMatch]:
    """
    Find similar tasks from past runs using keyword matching.

    Args:
        ticket: TicketSpec for current task
        repo_path: Repository path

    Returns:
        List of PatternMatch objects for similar successful tasks
    """
    import os

    repo_name = os.path.basename(repo_path)

    # Get successful runs from same repo
    runs = query_runs(repo_name=repo_name, status="DELIVERED", limit=50)

    # Simple keyword-based similarity
    task_keywords = set(ticket.title.lower().split())

    matches = []
    for run in runs:
        run_keywords = set(run.ticket_title.lower().split())
        common_keywords = task_keywords & run_keywords

        if len(common_keywords) > 0:
            similarity_score = len(common_keywords) / len(task_keywords | run_keywords)

            # Extract key lessons (simplified)
            key_lessons = [
                f"Completed in {run.implement_attempts} attempts",
                f"Test exit code: {run.test_exit_code}"
            ]

            matches.append(PatternMatch(
                work_item_id=run.work_item_id,
                similarity_score=similarity_score,
                ticket_title=run.ticket_title,
                final_status=run.final_status,
                key_lessons=key_lessons
            ))

    # Sort by similarity score
    matches.sort(key=lambda x: x.similarity_score, reverse=True)

    return matches[:5]  # Return top 5


def find_failure_patterns(ticket: TicketSpec, repo_path: str) -> List[PatternMatch]:
    """
    Find similar tasks that failed.

    Args:
        ticket: TicketSpec for current task
        repo_path: Repository path

    Returns:
        List of PatternMatch objects for similar failed tasks
    """
    import os

    repo_name = os.path.basename(repo_path)

    # Get blocked runs from same repo
    runs = query_runs(repo_name=repo_name, status="BLOCKED", limit=50)

    # Simple keyword-based similarity
    task_keywords = set(ticket.title.lower().split())

    matches = []
    for run in runs:
        run_keywords = set(run.ticket_title.lower().split())
        common_keywords = task_keywords & run_keywords

        if len(common_keywords) > 0:
            similarity_score = len(common_keywords) / len(task_keywords | run_keywords)

            # Extract key lessons
            key_lessons = [
                f"Failed after {run.implement_attempts} attempts",
                f"Failure mode: {run.failure_mode or 'unknown'}"
            ]

            matches.append(PatternMatch(
                work_item_id=run.work_item_id,
                similarity_score=similarity_score,
                ticket_title=run.ticket_title,
                final_status=run.final_status,
                key_lessons=key_lessons
            ))

    # Sort by similarity score
    matches.sort(key=lambda x: x.similarity_score, reverse=True)

    return matches[:5]  # Return top 5


def find_regression_risks(ticket: TicketSpec, repo_path: str) -> List[dict]:
    """
    Identify potential regression risks based on domain tags.

    Args:
        ticket: TicketSpec for current task
        repo_path: Repository path

    Returns:
        List of regression risk warnings
    """
    risks = []

    # Simple heuristics for regression risks
    if ticket.domain_tags:
        if "auth" in ticket.domain_tags:
            risks.append({
                "risk": "Authentication changes may affect existing login flows",
                "recommendation": "Ensure all auth tests pass"
            })

        if "database" in ticket.domain_tags or "migration" in ticket.domain_tags:
            risks.append({
                "risk": "Database changes may cause data compatibility issues",
                "recommendation": "Test with realistic data and verify backward compatibility"
            })

        if "api" in ticket.domain_tags:
            risks.append({
                "risk": "API changes may break existing clients",
                "recommendation": "Verify API contract compatibility"
            })

    return risks
