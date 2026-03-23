"""Shared session index — committed to git, per-developer.

The session registry lives at `.raise/rai/sessions/{prefix}/index.jsonl`
and travels with the repo, enabling cross-environment session continuity.

The active session pointer lives at `.raise/rai/personal/active-session`
(gitignored) and tracks which session is running in this terminal.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.config.paths import (
    ACTIVE_SESSION_FILE,
    get_developer_sessions_dir,
    get_personal_dir,
)

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


def write_session_entry(
    prefix: str,
    entry: SessionIndexEntry,
    *,
    project_root: Path | None = None,
) -> Path:
    """Append a session entry to the shared index.

    Creates the prefix directory and index file if they don't exist.

    Args:
        prefix: Developer prefix (e.g., "E").
        entry: Session index entry to append.
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to the index file written.
    """
    dev_dir = get_developer_sessions_dir(prefix, project_root)
    dev_dir.mkdir(parents=True, exist_ok=True)
    index_path = dev_dir / "index.jsonl"

    line = entry.model_dump_json() + "\n"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(line)

    logger.debug("Session %s appended to %s", entry.id, index_path)
    return index_path


def read_session_entries(
    prefix: str,
    *,
    project_root: Path | None = None,
) -> list[SessionIndexEntry]:
    """Read all session entries from the shared index.

    Args:
        prefix: Developer prefix (e.g., "E").
        project_root: Project root path. Defaults to current directory.

    Returns:
        List of session entries in file order. Empty list if index
        doesn't exist or is empty.
    """
    dev_dir = get_developer_sessions_dir(prefix, project_root)
    index_path = dev_dir / "index.jsonl"

    if not index_path.exists():
        return []

    entries: list[SessionIndexEntry] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            entries.append(SessionIndexEntry.model_validate(data))
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Skipping malformed index entry: %s", exc)

    return entries


def write_active_session(
    session_id: str,
    *,
    project_root: Path | None = None,
) -> None:
    """Write the active session pointer.

    Args:
        session_id: Session ID to mark as active.
        project_root: Project root path. Defaults to current directory.
    """
    personal_dir = get_personal_dir(project_root)
    personal_dir.mkdir(parents=True, exist_ok=True)
    pointer = personal_dir / ACTIVE_SESSION_FILE
    pointer.write_text(session_id + "\n", encoding="utf-8")
    logger.debug("Active session pointer: %s", session_id)


def read_active_session(
    *,
    project_root: Path | None = None,
) -> str | None:
    """Read the active session pointer.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Session ID string, or None if no active session.
    """
    pointer = get_personal_dir(project_root) / ACTIVE_SESSION_FILE
    if not pointer.exists():
        return None
    content = pointer.read_text(encoding="utf-8").strip()
    return content if content else None


def clear_active_session(
    *,
    project_root: Path | None = None,
) -> None:
    """Remove the active session pointer.

    No-op if the pointer doesn't exist.

    Args:
        project_root: Project root path. Defaults to current directory.
    """
    pointer = get_personal_dir(project_root) / ACTIVE_SESSION_FILE
    if pointer.exists():
        pointer.unlink()
        logger.debug("Active session pointer cleared")
