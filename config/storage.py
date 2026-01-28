"""
SQLite storage helpers for Remarkable OCR.
Keeps user config and processed message state persistent across restarts.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def get_db_path() -> str:
    """Resolve DB path from env or default."""
    return os.getenv("DB_PATH", "./data/remarkable.db")


def _ensure_parent_dir(db_path: str) -> None:
    parent = Path(db_path).expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    """Open a SQLite connection with row access by name."""
    db_path = get_db_path()
    _ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                config_json TEXT NOT NULL,
                status TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS processed_messages (
                email TEXT NOT NULL,
                message_id TEXT NOT NULL,
                processed_at TEXT DEFAULT (datetime('now')),
                UNIQUE(email, message_id)
            );
            """
        )
        conn.commit()


def get_user_config(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user config by email. Returns dict or None."""
    import json

    with get_conn() as conn:
        row = conn.execute(
            "SELECT config_json FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if not row:
            return None
        return json.loads(row["config_json"])


def set_user_config(email: str, config: Dict[str, Any], status: Optional[str] = None) -> None:
    """Insert or update user config."""
    import json

    status_value = status if status is not None else config.get("status")
    payload = json.dumps(config)
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (email, config_json, status, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(email) DO UPDATE SET
                config_json = excluded.config_json,
                status = excluded.status,
                updated_at = datetime('now')
            """,
            (email, payload, status_value),
        )
        conn.commit()


def list_users() -> Iterable[str]:
    """List configured user emails."""
    with get_conn() as conn:
        rows = conn.execute("SELECT email FROM users ORDER BY email").fetchall()
        return [row["email"] for row in rows]


def is_message_processed(email: str, message_id: str) -> bool:
    """Check if a message was processed for a user."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM processed_messages WHERE email = ? AND message_id = ? LIMIT 1",
            (email, message_id),
        ).fetchone()
        return row is not None


def mark_message_processed(email: str, message_id: str) -> None:
    """Mark a message as processed for a user."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO processed_messages (email, message_id)
            VALUES (?, ?)
            """,
            (email, message_id),
        )
        conn.commit()


def list_recent_processed(email: Optional[str] = None, limit: int = 20) -> Iterable[Dict[str, Any]]:
    """List recent processed messages."""
    with get_conn() as conn:
        if email:
            rows = conn.execute(
                """
                SELECT email, message_id, processed_at
                FROM processed_messages
                WHERE email = ?
                ORDER BY processed_at DESC
                LIMIT ?
                """,
                (email, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT email, message_id, processed_at
                FROM processed_messages
                ORDER BY processed_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {"email": row["email"], "message_id": row["message_id"], "processed_at": row["processed_at"]}
            for row in rows
        ]


def has_users() -> bool:
    """Check if any users exist in storage."""
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        return row is not None


def count_processed_messages(email: Optional[str] = None) -> int:
    """Count processed messages (optionally filtered by email)."""
    with get_conn() as conn:
        if email:
            row = conn.execute(
                "SELECT COUNT(1) AS cnt FROM processed_messages WHERE email = ?",
                (email,),
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(1) AS cnt FROM processed_messages").fetchone()
        return int(row["cnt"]) if row else 0


def check_db() -> tuple[bool, str]:
    """Simple DB health check."""
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1").fetchone()
        return True, "ok"
    except Exception as e:
        return False, str(e)
