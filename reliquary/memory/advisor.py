from reliquary.schemas.ticket import TicketSpec
from reliquary.schemas.memory import MemoryAdvice
from reliquary.memory.pattern_matcher import find_similar_tasks, find_failure_patterns, find_regression_risks


def get_memory_advice(ticket: TicketSpec, repo_path: str) -> MemoryAdvice:
    """
    Get memory-based advice for a task.

    Args:
        ticket: TicketSpec for current task
        repo_path: Repository path

    Returns:
        MemoryAdvice with recommendations
    """
    # Find similar successful and failed tasks
    similar_successes = find_similar_tasks(ticket, repo_path)
    similar_failures = find_failure_patterns(ticket, repo_path)
    regression_risks = find_regression_risks(ticket, repo_path)

    # Generate recommendations
    recommendations = []

    if similar_successes:
        recommendations.append(
            f"Found {len(similar_successes)} similar successful tasks. "
            f"Most similar: '{similar_successes[0].ticket_title}' "
            f"(completed in {similar_successes[0].key_lessons[0]})"
        )

    if similar_failures:
        recommendations.append(
            f"Warning: {len(similar_failures)} similar tasks failed. "
            f"Most similar failure: '{similar_failures[0].ticket_title}' "
            f"({similar_failures[0].key_lessons[1]})"
        )

    if regression_risks:
        recommendations.append(
            f"Identified {len(regression_risks)} potential regression risks. "
            f"Review carefully."
        )

    if not similar_successes and not similar_failures:
        recommendations.append("No similar tasks found in memory. Proceeding with standard workflow.")

    return MemoryAdvice(
        similar_successes=similar_successes,
        similar_failures=similar_failures,
        regression_risks=regression_risks,
        recommendations=recommendations
    )
