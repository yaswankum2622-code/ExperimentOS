import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "events.db"


def get_connection() -> sqlite3.Connection:
    """Open SQLite connection with dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT query and return rows as dictionaries."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def get_experiment_summary() -> dict:
    """Summarize users, purchasers, conversion, and revenue by variant."""
    sql = """
    SELECT
        variant,
        COUNT(DISTINCT user_id)                                    AS users,
        COUNT(DISTINCT CASE WHEN event_type='purchase'
              THEN user_id END)                                    AS purchasers,
        ROUND(COUNT(DISTINCT CASE WHEN event_type='purchase'
              THEN user_id END) * 100.0 /
              COUNT(DISTINCT user_id), 2)                         AS conversion_rate,
        ROUND(SUM(CASE WHEN event_type='purchase'
              THEN revenue ELSE 0 END), 2)                        AS total_revenue
    FROM events
    GROUP BY variant
    """
    return run_query(sql)
