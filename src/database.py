import sqlite3
from contextlib import contextmanager

from src.config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_jobs (
                job_id TEXT PRIMARY KEY,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def was_sent(job_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sent_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        return row is not None


def mark_sent(job_id: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sent_jobs (job_id) VALUES (?)", (job_id,)
        )
