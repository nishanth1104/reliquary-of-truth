from reliquary.schemas.ticket import TicketSpec


def classify_risk(ticket: TicketSpec, patch: str) -> dict:
    """
    Classifies risk factors based on ticket and patch content.

    Args:
        ticket: TicketSpec
        patch: Unified diff patch content

    Returns:
        Dictionary with risk factors
    """
    risk_factors = {
        "modifies_auth": False,
        "modifies_migrations": False,
        "modifies_critical_paths": False,
        "large_change": False,
        "touches_many_files": False
    }

    # Check if patch modifies authentication-related files
    auth_keywords = ["auth", "login", "password", "token", "session", "credential"]
    for keyword in auth_keywords:
        if keyword in patch.lower():
            risk_factors["modifies_auth"] = True
            break

    # Check if patch modifies migrations
    if "migration" in patch.lower() or "/migrations/" in patch:
        risk_factors["modifies_migrations"] = True

    # Check if patch modifies critical paths
    critical_paths = ["/models/", "/schemas/", "/database/", "/security/"]
    for path in critical_paths:
        if path in patch:
            risk_factors["modifies_critical_paths"] = True
            break

    # Check if change is large (>500 lines modified)
    lines_changed = len([line for line in patch.split('\n') if line.startswith('+') or line.startswith('-')])
    if lines_changed > 500:
        risk_factors["large_change"] = True

    # Check if touches many files
    file_count = patch.count("diff --git")
    if file_count > 10:
        risk_factors["touches_many_files"] = True

    return risk_factors
