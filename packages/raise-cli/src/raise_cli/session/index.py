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

from raise_cli.compat import file_lock, file_unlock
from raise_cli.config.paths import (
    ACTIVE_SESSION_FILE,
    get_developer_sessions_dir,
    get_personal_dir,
)
from raise_cli.core.files import atomic_write

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


class ActiveSessionPointer(BaseModel, frozen=True):
    """Active session state stored locally (gitignored).

    Carries session metadata that needs to survive from start to close:
    session ID, human-readable name, and exact start timestamp.
    """

    id: str
    name: str
    started: datetime


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
        file_lock(f)
        try:
            f.write(line)
        finally:
            file_unlock(f)

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
    pointer_data: ActiveSessionPointer,
    *,
    project_root: Path | None = None,
) -> None:
    """Write the active session pointer.

    Stores session ID, name, and start timestamp as JSON so that
    close can build a complete SessionIndexEntry.

    Args:
        pointer_data: Active session metadata.
        project_root: Project root path. Defaults to current directory.
    """
    pointer = get_personal_dir(project_root) / ACTIVE_SESSION_FILE
    atomic_write(pointer, pointer_data.model_dump_json() + "\n")
    logger.debug("Active session pointer: %s", pointer_data.id)


def read_active_session(
    *,
    project_root: Path | None = None,
) -> ActiveSessionPointer | None:
    """Read the active session pointer.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        ActiveSessionPointer if found and valid, None otherwise.
    """
    pointer = get_personal_dir(project_root) / ACTIVE_SESSION_FILE
    if not pointer.exists():
        return None
    content = pointer.read_text(encoding="utf-8").strip()
    if not content:
        return None
    try:
        return ActiveSessionPointer.model_validate_json(content)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Malformed active session pointer, ignoring")
        return None


def clear_active_session(
    *,
    session_id: str | None = None,
    project_root: Path | None = None,
) -> None:
    """Remove the active session pointer.

    If session_id is provided, only clears if the active pointer matches.
    This prevents one session from clearing another's pointer.

    No-op if the pointer doesn't exist.

    Args:
        session_id: Only clear if this ID matches the active pointer.
        project_root: Project root path. Defaults to current directory.
    """
    pointer = get_personal_dir(project_root) / ACTIVE_SESSION_FILE
    if not pointer.exists():
        return
    if session_id is not None:
        current = read_active_session(project_root=project_root)
        if current is not None and current.id != session_id:
            logger.debug(
                "Not clearing pointer: active=%s, requested=%s",
                current.id,
                session_id,
            )
            return
    pointer.unlink()
    logger.debug("Active session pointer cleared")
