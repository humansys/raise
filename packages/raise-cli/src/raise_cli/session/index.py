"""Session index and active session pointer — SQLite backend.

The session index stores session records in the global SQLite database
(~/.rai/raise.db, project_id-scoped). Replaces the previous JSONL+flock
persistence (S2780.3).

The active session pointer tracks which session is running in this
terminal, stored in the active_sessions table.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import cast

from pydantic import BaseModel, Field

from raise_cli.exceptions import ConfigurationError
from raise_cli.session.scope import SessionScope
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.counter import next_counter
from raise_cli.storage.schema import create_all

logger = logging.getLogger(__name__)


class SessionIndexEntry(BaseModel, frozen=True):
    """A single session record in the shared index."""

    id: str
    name: str
    started: datetime
    closed: datetime | None = None
    type: str = "feature"
    summary: str = ""
    outcomes: list[str] = Field(default_factory=list)
    branch: str = ""
    story_points: int | None = None
    session_number: int | None = None


class ActiveSessionPointer(BaseModel, frozen=True):
    """Active session state stored in SQLite.

    Carries session metadata that needs to survive from start to close:
    session ID, human-readable name, exact start timestamp, and the
    worktree this session is associated with ('' for main-checkout sessions).
    """

    id: str
    name: str
    started: datetime
    cc_session_id: str = ""
    worktree_id: str = ""


def write_session_entry(
    prefix: str,
    entry: SessionIndexEntry,
    *,
    project_root: Path | None = None,
) -> Path:
    """Append a session entry to the SQLite index.

    Args:
        prefix: Developer prefix (e.g., "E").
        entry: Session index entry to write.
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to the database file.
    """
    normalized_prefix = prefix.strip()
    if not normalized_prefix:
        msg = "Session developer prefix cannot be empty for normal writes"
        raise ConfigurationError(msg)

    root = (project_root or Path.cwd()).resolve()
    pid = get_project_id(root)
    conn = get_project_db(root)
    create_all(conn)

    # Scope attribution (S15456.1): resolved once, stored with the row so
    # continuity selection can later filter by worktree+agent. Empty agent
    # id stays '' — never a matchable key (D1); main checkout is '' (D3).
    from raise_cli.session.scope import resolve_scope

    scope = resolve_scope(root)

    existing = conn.execute(
        "SELECT state_json, session_number FROM sessions WHERE project_id = ? AND session_id = ?",
        (pid, entry.id),
    ).fetchone()
    state_json = existing["state_json"] if existing else "{}"

    if existing is None:
        session_number: int | None = next_counter(
            conn,
            "session",
            seed_fn=lambda: conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE project_id = ?", (pid,)
            ).fetchone()[0],
            project_id=pid,
        )
    else:
        session_number = existing["session_number"]

    conn.execute(
        """INSERT OR REPLACE INTO sessions
           (project_id, session_id, name, started, closed, type, summary, branch, prefix, state_json, outcomes, story_points, session_number, worktree_id, agent_session_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            pid,
            entry.id,
            entry.name,
            entry.started.isoformat(),
            entry.closed.isoformat() if entry.closed else None,
            entry.type,
            entry.summary,
            entry.branch,
            normalized_prefix,
            state_json,
            json.dumps(entry.outcomes),
            entry.story_points,
            session_number,
            scope.worktree_id,
            scope.agent_session_id,
        ),
    )
    conn.commit()

    db_path = Path(conn.execute("PRAGMA database_list").fetchone()[2])
    conn.close()
    logger.debug("Session %s written to SQLite", entry.id)
    return db_path


def read_session_entries(
    prefix: str,
    *,
    project_root: Path | None = None,
    scope: SessionScope | None = None,
) -> list[SessionIndexEntry]:
    """Read all session entries for a developer prefix.

    Args:
        prefix: Developer prefix (e.g., "E").
        project_root: Project root path. Defaults to current directory.
        scope: Caller scope filter (E15456): same worktree_id only,
            unattributable rows (worktree_id='' AND agent_session_id='')
            excluded. ``None`` is the explicit wider-scope opt-in — the
            unfiltered project-wide read kept for `rai session list` (D3).

    Returns:
        List of session entries ordered by start time. Empty list if
        no entries exist for this prefix.
    """
    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return []

    pid = get_project_id(root)
    if scope is None:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE project_id = ? AND prefix = ? ORDER BY started",
            (pid, prefix),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE project_id = ? AND prefix = ? "
            "AND worktree_id = ? "
            "AND NOT (worktree_id = '' AND agent_session_id = '') "
            "ORDER BY started",
            (pid, prefix, scope.worktree_id),
        ).fetchall()
    conn.close()

    entries: list[SessionIndexEntry] = []
    for row in rows:
        try:
            row_dict = dict(row)
            outcomes_raw = row_dict.get("outcomes", "[]")
            entries.append(
                SessionIndexEntry(
                    id=row["session_id"],
                    name=row["name"],
                    started=datetime.fromisoformat(row["started"]),
                    closed=datetime.fromisoformat(row["closed"])
                    if row["closed"]
                    else None,
                    type=row["type"],
                    summary=row["summary"],
                    outcomes=json.loads(outcomes_raw),
                    branch=row["branch"],
                    session_number=row_dict.get("session_number"),
                )
            )
        except (ValueError, KeyError) as exc:
            logger.warning("Skipping malformed session row: %s", exc)

    return entries


def count_missing_prefix_sessions(*, project_root: Path | None = None) -> int:
    """Count project sessions whose developer prefix is missing."""
    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return 0

    pid = get_project_id(root)
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM sessions WHERE project_id = ? AND prefix = ''",
        (pid,),
    ).fetchone()
    conn.close()
    return int(row["count"]) if row is not None else 0


def find_last_closed_in_scope(
    prefix: str,
    scope: SessionScope,
    *,
    project_root: Path | None = None,
) -> str | None:
    """Find the most recently closed session ID within *scope*.

    Closed donor chain (E15456 design v2): same worktree_id only (main is
    '' and donates only to main); a non-empty caller agent_session_id breaks
    ties in favour of the same agent (D1: '' never matches anything);
    rows with both keys empty are unattributable history and excluded (D6).

    Args:
        prefix: Developer prefix (e.g., "E").
        scope: Caller's resolved scope identity.
        project_root: Project root path. Defaults to current directory.

    Returns:
        Session ID string of the most recently closed in-scope session, or
        None if no eligible closed session exists.
    """
    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return None

    pid = get_project_id(root)
    row = conn.execute(
        """SELECT session_id FROM sessions
           WHERE project_id = ? AND prefix = ? AND closed IS NOT NULL
             AND worktree_id = ?
             AND NOT (worktree_id = '' AND agent_session_id = '')
           ORDER BY CASE
                      WHEN ? <> '' AND agent_session_id = ? THEN 0
                      ELSE 1
                    END,
                    closed DESC
           LIMIT 1""",
        (
            pid,
            prefix,
            scope.worktree_id,
            scope.agent_session_id,
            scope.agent_session_id,
        ),
    ).fetchone()
    conn.close()

    if row is None:
        return None
    return cast("str", row["session_id"])


def write_active_session(
    pointer_data: ActiveSessionPointer,
    *,
    project_root: Path | None = None,
    cc_session_id: str | None = None,
) -> None:
    """Write the active session pointer to SQLite.

    Args:
        pointer_data: Active session metadata.
        project_root: Project root path. Defaults to current directory.
        cc_session_id: Agent/CC session ID to scope the pointer.
            When None, falls back to ``discover_agent_session_id()``.
    """
    from raise_cli._agent_session import discover_agent_session_id

    root = (project_root or Path.cwd()).resolve()
    pid = get_project_id(root)
    cc_sid = cc_session_id or discover_agent_session_id() or ""
    conn = get_project_db(root)
    create_all(conn)

    conn.execute(
        "DELETE FROM active_sessions WHERE project_id = ? AND cc_session_id = ?",
        (pid, cc_sid),
    )
    conn.execute(
        "INSERT INTO active_sessions"
        " (project_id, session_id, name, started, cc_session_id, worktree_id)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (
            pid,
            pointer_data.id,
            pointer_data.name,
            pointer_data.started.isoformat(),
            cc_sid,
            pointer_data.worktree_id,
        ),
    )
    conn.commit()
    conn.close()
    logger.debug(
        "Active session pointer: %s (agent=%s, worktree=%s)",
        pointer_data.id,
        cc_sid,
        pointer_data.worktree_id,
    )


def read_active_session(
    *,
    project_root: Path | None = None,
    cc_session_id: str | None = None,
) -> ActiveSessionPointer | None:
    """Read the active session pointer from SQLite.

    Args:
        project_root: Project root path. Defaults to current directory.
        cc_session_id: Agent/CC session ID to scope the lookup.
            When None, falls back to ``discover_agent_session_id()``.

    Returns:
        ActiveSessionPointer if found, None otherwise.
    """
    from raise_cli._agent_session import discover_agent_session_id

    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return None

    pid = get_project_id(root)
    cc_sid = cc_session_id or discover_agent_session_id() or ""
    row = conn.execute(
        "SELECT * FROM active_sessions WHERE project_id = ? AND cc_session_id = ? LIMIT 1",
        (pid, cc_sid),
    ).fetchone()
    conn.close()

    if row is None:
        return None
    try:
        cols = set(row.keys())
        return ActiveSessionPointer(
            id=row["session_id"],
            name=row["name"],
            started=datetime.fromisoformat(row["started"]),
            cc_session_id=row["cc_session_id"] if "cc_session_id" in cols else "",
            worktree_id=row["worktree_id"] if "worktree_id" in cols else "",
        )
    except (ValueError, KeyError):
        logger.warning("Malformed active session pointer, ignoring")
        return None


def read_all_active_sessions(
    *,
    project_root: Path | None = None,
) -> list[ActiveSessionPointer]:
    """Read ALL active session pointers for a project (all agents).

    Used by doctor/gc to find zombie pointers regardless of which agent
    created them.
    """
    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return []

    pid = get_project_id(root)
    rows = conn.execute(
        "SELECT * FROM active_sessions WHERE project_id = ?", (pid,)
    ).fetchall()
    conn.close()

    first_cols = set(rows[0].keys()) if rows else set()
    has_cc_col = "cc_session_id" in first_cols
    has_wt_col = "worktree_id" in first_cols

    results: list[ActiveSessionPointer] = []
    for row in rows:
        try:
            results.append(
                ActiveSessionPointer(
                    id=row["session_id"],
                    name=row["name"],
                    started=datetime.fromisoformat(row["started"]),
                    cc_session_id=row["cc_session_id"] if has_cc_col else "",
                    worktree_id=row["worktree_id"] if has_wt_col else "",
                )
            )
        except (ValueError, KeyError):
            logger.warning("Malformed active session pointer, skipping")
    return results


def clear_active_session(
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
    cc_session_id: str | None = None,
) -> None:
    """Remove the active session pointer for this agent.

    If session_id is provided, clears only a matching pointer in the same
    SQL statement. This prevents an older close from deleting a pointer
    replaced by a newer session between a read and delete.

    No-op if no active session exists.

    Args:
        session_id: Only clear if this ID matches the active pointer.
        project_root: Project root path. Defaults to current directory.
        cc_session_id: Agent/CC session ID to scope the deletion.
            When None, falls back to ``discover_agent_session_id()``.
    """
    from raise_cli._agent_session import discover_agent_session_id

    root = (project_root or Path.cwd()).resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return

    cc_sid = cc_session_id or discover_agent_session_id() or ""

    pid = get_project_id(root)
    if session_id is None:
        conn.execute(
            "DELETE FROM active_sessions WHERE project_id = ? AND cc_session_id = ?",
            (pid, cc_sid),
        )
    else:
        conn.execute(
            "DELETE FROM active_sessions"
            " WHERE project_id = ? AND cc_session_id = ? AND session_id = ?",
            (pid, cc_sid, session_id),
        )
    conn.commit()
    conn.close()
    logger.debug("Active session pointer cleared (agent=%s)", cc_sid)
