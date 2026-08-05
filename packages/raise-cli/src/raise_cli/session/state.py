"""Session state persistence — SQLite backend.

Reads and writes session state to the global SQLite database
(~/.rai/raise.db, project_id-scoped). Replaces the previous YAML-based
persistence (S2780.2).

Legacy migration: migrate_flat_to_session() still reads YAML files
for one-time migration into per-session directories. Full cleanup
deferred to S2780.6.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from sqlite3 import Connection
from typing import TYPE_CHECKING, cast

import yaml
from pydantic import ValidationError

from raise_cli._agent_session import discover_agent_runtime
from raise_cli.config.paths import get_session_dir
from raise_cli.schemas.session_state import CurrentWork, LastSession, SessionState
from raise_cli.session.scope import resolve_scope
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all

if TYPE_CHECKING:
    from raise_cli.session.close import CloseInput

logger = logging.getLogger(__name__)

_RAISE_DIR_NAME = ".raise"
_SESSION_STATE_YAML = "session-state.yaml"


def _load_state_from_session_record(
    conn: Connection, project_id: str, session_id: str
) -> SessionState | None:
    """Rebuild continuity fields from a project-scoped durable close record."""
    row = conn.execute(
        """SELECT records.closed_at, records.summary, records.epic,
                  records.narrative, records.next_session_prompt, records.notes,
                  records.completed_epics_json, records.branch, sessions.prefix
           FROM session_records AS records
           LEFT JOIN sessions
             ON sessions.project_id = records.project_id
            AND sessions.session_id = records.session_id
           WHERE records.project_id = ? AND records.session_id = ?""",
        (project_id, session_id),
    ).fetchone()
    if row is None:
        return None

    try:
        closed_at = datetime.fromisoformat(row["closed_at"])
    except (TypeError, ValueError):
        logger.debug("Ignoring session record with invalid close time: %s", session_id)
        return None

    try:
        completed_raw = json.loads(row["completed_epics_json"])
    except (TypeError, json.JSONDecodeError):
        completed_raw = []
    completed_epics = (
        [epic for epic in completed_raw if isinstance(epic, str)]
        if isinstance(completed_raw, list)
        else []
    )

    return SessionState(
        current_work=CurrentWork(
            epic=row["epic"] or "",
            branch=row["branch"] or "",
        ),
        last_session=LastSession(
            id=session_id,
            date=closed_at.date(),
            developer=row["prefix"] or "",
            summary=row["summary"] or "",
        ),
        narrative=row["narrative"] or "",
        next_session_prompt=row["next_session_prompt"] or "",
        notes=row["notes"] or "",
        completed_epics=completed_epics,
        last_modified=row["closed_at"],
    )


def load_session_state(
    project_path: Path, session_id: str | None = None
) -> SessionState | None:
    """Load session state from SQLite.

    Args:
        project_path: Absolute path to the project root.
        session_id: Optional session ID for per-session isolation.

    Returns:
        SessionState if found and valid, None otherwise.
    """
    conn = get_project_db(project_path)
    create_all(conn)
    pid = get_project_id(project_path)
    key = session_id or "flat"
    row = conn.execute(
        "SELECT state_json FROM sessions WHERE project_id = ? AND session_id = ?",
        (pid, key),
    ).fetchone()
    if row is not None and row["state_json"] not in ("", "{}"):
        try:
            result = SessionState.model_validate_json(row["state_json"])
        except ValidationError:
            conn.execute(
                "UPDATE sessions SET state_json = '{}' WHERE project_id = ? AND session_id = ?",
                (pid, key),
            )
            conn.commit()
            logger.debug("Quarantined invalid session state: session=%s", key)
        else:
            conn.close()
            return result

    result = _load_state_from_session_record(conn, pid, key)
    conn.close()
    return result


def save_session_state(
    project_path: Path, state: SessionState, session_id: str | None = None
) -> None:
    """Save session state to SQLite.

    Args:
        project_path: Absolute path to the project root.
        state: The session state to save.
        session_id: Optional session ID for per-session isolation.
    """
    project_path = project_path.resolve()
    state = state.model_copy(update={"last_modified": datetime.now(UTC).isoformat()})
    key = session_id or "flat"

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    # Scope attribution (S15456.1): this INSERT OR REPLACE runs at close and
    # must carry worktree_id or it would wipe the open-time attribution.
    # Discovery is owned by resolve_scope (S15456.4 O5) — the stored agent key
    # reuses scope.agent_session_id so the two can never diverge.
    scope = resolve_scope(project_path)

    existing = conn.execute(
        "SELECT prefix, outcomes, session_number, story_points FROM sessions WHERE project_id = ? AND session_id = ?",
        (pid, key),
    ).fetchone()
    prefix = existing["prefix"] if existing else ""
    outcomes = existing["outcomes"] if existing else "[]"
    # INSERT OR REPLACE below omits nothing it should keep: session_number
    # and story_points would reset to NULL on every close otherwise (SH-1).
    session_number = existing["session_number"] if existing else None
    story_points = existing["story_points"] if existing else None

    conn.execute(
        """INSERT OR REPLACE INTO sessions
           (project_id, session_id, name, started, closed, type, summary, branch, prefix, state_json, outcomes,
            agent_session_id, agent_runtime, worktree_id, session_number, story_points)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            pid,
            key,
            state.last_session.id,
            state.last_session.date.isoformat(),
            state.last_modified,
            "feature",
            state.last_session.summary,
            state.current_work.branch,
            prefix,
            state.model_dump_json(),
            outcomes,
            scope.agent_session_id,
            discover_agent_runtime(),
            scope.worktree_id,
            session_number,
            story_points,
        ),
    )
    conn.commit()
    conn.close()
    logger.debug("Saved session state to SQLite: %s", key)


def write_session_record(
    project_path: Path,
    session_id: str,
    close_input: CloseInput,
    pattern_ids: list[str],
    *,
    token_summary: dict[str, int] | None = None,
) -> None:
    """Persist full CloseInput payload to session_records, session_patterns, session_corrections.

    Additive — does not replace SQLite pattern writes or developer.yaml writes.
    Uses INSERT OR REPLACE so re-close is idempotent on session_records.
    """
    now = datetime.now(UTC).isoformat()
    epic = close_input.current_work.epic if close_input.current_work else ""

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    token_json = json.dumps(token_summary) if token_summary else "{}"

    # Scope attribution (S15456.1): same resolve_scope identity as the open
    # path; branch comes from the close payload (mirrors sessions.branch).
    # Discovery is owned by resolve_scope (S15456.4 O5).
    scope = resolve_scope(project_path)
    branch = close_input.current_work.branch if close_input.current_work else ""

    conn.execute(
        """INSERT OR REPLACE INTO session_records
           (project_id, session_id, closed_at, summary, session_type, epic,
            narrative, next_session_prompt, notes,
            outcomes_json, completed_epics_json, token_summary_json,
            worktree_id, agent_session_id, branch)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            pid,
            session_id,
            now,
            close_input.summary,
            close_input.session_type,
            epic,
            close_input.narrative,
            close_input.next_session_prompt,
            close_input.notes,
            json.dumps(close_input.outcomes),
            json.dumps(close_input.completed_epics),
            token_json,
            scope.worktree_id,
            scope.agent_session_id,
            branch,
        ),
    )

    for pat_id in pattern_ids:
        conn.execute(
            """INSERT OR IGNORE INTO session_patterns
               (project_id, id, session_id, content, sub_type, context_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pid, pat_id, session_id, "", "process", "[]", now),
        )

    for corr in close_input.corrections:
        what = corr.get("what", "")
        lesson = corr.get("lesson", "")
        if what and lesson:
            exists = conn.execute(
                "SELECT 1 FROM session_corrections WHERE project_id = ? AND session_id = ? AND what = ? AND lesson = ?",
                (pid, session_id, what, lesson),
            ).fetchone()
            if not exists:
                conn.execute(
                    """INSERT INTO session_corrections
                       (project_id, session_id, what, lesson, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (pid, session_id, what, lesson, now),
                )

    conn.commit()
    conn.close()
    logger.debug("Wrote session record to SQLite: %s", session_id)


def cleanup_session_dir(project_path: Path, session_id: str) -> None:
    """Remove per-session directory after session close.

    Only removes the specific session directory. Does NOT remove
    shared files (index.jsonl, memory/).

    Args:
        project_path: Absolute path to the project root.
        session_id: Session ID whose directory to remove.
    """
    session_dir = get_session_dir(session_id, project_path)
    if session_dir.exists():
        shutil.rmtree(session_dir)
        logger.info("Cleaned up session dir: %s", session_dir)


def migrate_flat_to_session(project_path: Path, session_id: str) -> bool:
    """One-time migration from flat layout to per-session directory.

    Moves:
    - personal/session-state.yaml → personal/sessions/{target_id}/state.yaml
    - personal/telemetry/signals.jsonl → personal/sessions/{target_id}/signals.jsonl

    The target directory is determined by last_session.id in the flat state file.
    Falls back to session_id if last_session.id is not available.

    Args:
        project_path: Absolute path to the project root.
        session_id: Fallback session ID when last_session.id is unavailable.

    Returns:
        True if migration occurred, False if nothing to migrate.
    """
    personal_dir = project_path / _RAISE_DIR_NAME / "rai" / "personal"
    flat_state = personal_dir / _SESSION_STATE_YAML
    flat_signals = personal_dir / "telemetry" / "signals.jsonl"

    if not flat_state.exists() and not flat_signals.exists():
        return False

    target_id = session_id
    if flat_state.exists():
        try:
            content = yaml.safe_load(flat_state.read_text(encoding="utf-8"))
            if isinstance(content, dict) and "last_session" in content:
                last = cast("object", content["last_session"])
                if isinstance(last, dict) and "id" in last:
                    last_id = cast("object", last["id"])
                    if isinstance(last_id, str) and last_id:
                        target_id = last_id
        except (yaml.YAMLError, OSError):
            pass

    session_dir = get_session_dir(target_id, project_path)
    if session_dir.exists():
        return False

    session_dir.mkdir(parents=True, exist_ok=True)

    if flat_state.exists():
        shutil.move(str(flat_state), str(session_dir / "state.yaml"))
        logger.info("Migrated state: %s → %s/state.yaml", flat_state, session_dir)

    if flat_signals.exists():
        shutil.move(str(flat_signals), str(session_dir / "signals.jsonl"))
        logger.info(
            "Migrated signals: %s → %s/signals.jsonl", flat_signals, session_dir
        )

    return True
