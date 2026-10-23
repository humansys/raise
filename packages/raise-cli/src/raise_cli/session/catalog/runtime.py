"""Runtime session identity binding — create/bind rows in runtime_sessions (schema v70)."""

from __future__ import annotations

import os
import sqlite3

RAI_RUNTIME_SESSION_ID = "RAI_RUNTIME_SESSION_ID"


def create_runtime_session(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    project_id: str,
    worktree_id: str,
    alias: str,
    harness: str,
) -> None:
    """Insert a provisioning-state row into runtime_sessions."""
    conn.execute(
        """
        INSERT INTO runtime_sessions
            (session_id, project_id, worktree_id, alias, harness, state)
        VALUES (?, ?, ?, ?, ?, 'provisioning')
        """,
        (session_id, project_id, worktree_id, alias, harness),
    )
    conn.commit()


def bind_governance_session_id(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    governance_session_id: str,
) -> None:
    """Set governance_session_id on an existing runtime_sessions row.

    Fail-open: no-op when the row does not exist (provisioning was interrupted).
    """
    conn.execute(
        """
        UPDATE runtime_sessions
           SET governance_session_id = ?,
               updated_at = datetime('now')
         WHERE session_id = ?
        """,
        (governance_session_id, session_id),
    )
    conn.commit()


def read_runtime_session_id() -> str | None:
    """Return the runtime session ID from the environment, or None."""
    return os.environ.get(RAI_RUNTIME_SESSION_ID) or None
