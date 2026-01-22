import sqlite3
import json
import os
from typing import List, Optional
from reliquary.schemas.memory import RunSummary


def get_db_path() -> str:
    """Get the path to the memory database."""
    db_path = os.getenv("RELIQUARY_DB_PATH", "memory.db")
    return db_path


def init_database():
    """Initialize the memory database with required schema."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_summaries (
            work_item_id TEXT PRIMARY KEY,
            repo_name TEXT,
            task_raw TEXT,
            ticket_title TEXT,
            domain_tags TEXT,
            risk_level TEXT,
            final_status TEXT,
            implement_attempts INTEGER,
            test_exit_code INTEGER,
            failure_mode TEXT,
            completed_at TEXT,
            run_dir TEXT
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_name ON run_summaries(repo_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_final_status ON run_summaries(final_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_failure_mode ON run_summaries(failure_mode)")

    conn.commit()
    conn.close()


def save_run_summary(summary: RunSummary):
    """
    Save a run summary to the database.

    Args:
        summary: RunSummary object to save
    """
    init_database()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO run_summaries
        (work_item_id, repo_name, task_raw, ticket_title, domain_tags, risk_level,
         final_status, implement_attempts, test_exit_code, failure_mode, completed_at, run_dir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.work_item_id,
        summary.repo_name,
        summary.task_raw,
        summary.ticket_title,
        json.dumps(summary.domain_tags),
        summary.risk_level,
        summary.final_status,
        summary.implement_attempts,
        summary.test_exit_code,
        summary.failure_mode,
        summary.completed_at,
        summary.run_dir
    ))

    conn.commit()
    conn.close()


def query_runs(
    repo_name: Optional[str] = None,
    status: Optional[str] = None,
    failure_mode: Optional[str] = None,
    limit: int = 10
) -> List[RunSummary]:
    """
    Query run summaries from the database.

    Args:
        repo_name: Filter by repository name
        status: Filter by final status
        failure_mode: Filter by failure mode
        limit: Maximum number of results

    Returns:
        List of RunSummary objects
    """
    init_database()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM run_summaries WHERE 1=1"
    params = []

    if repo_name:
        query += " AND repo_name = ?"
        params.append(repo_name)

    if status:
        query += " AND final_status = ?"
        params.append(status)

    if failure_mode:
        query += " AND failure_mode = ?"
        params.append(failure_mode)

    query += " ORDER BY completed_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    summaries = []
    for row in rows:
        summaries.append(RunSummary(
            work_item_id=row[0],
            repo_name=row[1],
            task_raw=row[2],
            ticket_title=row[3],
            domain_tags=json.loads(row[4]),
            risk_level=row[5],
            final_status=row[6],
            implement_attempts=row[7],
            test_exit_code=row[8],
            failure_mode=row[9],
            completed_at=row[10],
            run_dir=row[11]
        ))

    conn.close()
    return summaries


def get_stats() -> dict:
    """
    Get aggregate statistics from the database.

    Returns:
        Dictionary with statistics
    """
    init_database()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total runs
    cursor.execute("SELECT COUNT(*) FROM run_summaries")
    total_runs = cursor.fetchone()[0]

    # Success rate
    cursor.execute("SELECT COUNT(*) FROM run_summaries WHERE final_status = 'DELIVERED'")
    successful_runs = cursor.fetchone()[0]

    # Average attempts
    cursor.execute("SELECT AVG(implement_attempts) FROM run_summaries")
    avg_attempts = cursor.fetchone()[0] or 0

    # Failure modes
    cursor.execute("""
        SELECT failure_mode, COUNT(*) as count
        FROM run_summaries
        WHERE failure_mode IS NOT NULL
        GROUP BY failure_mode
        ORDER BY count DESC
    """)
    failure_modes = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
        "avg_attempts": round(avg_attempts, 2),
        "failure_modes": failure_modes
    }
