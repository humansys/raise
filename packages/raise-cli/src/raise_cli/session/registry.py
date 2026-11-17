"""Local SessionRegistry — file-based session lifecycle management.

Implements the SessionRegistry protocol (ADR-038) as a facade over
existing session index and active-session pointer infrastructure.

gc() is deprecated in favor of SessionDoctor (S1248.5) which provides
consent-based cleanup instead of silent deletion. The method remains
for protocol compatibility and programmatic use (server backend 3.0).

Architecture: E1248 (Git-First Session State), S1248.2
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.config.paths import get_personal_dir
from raise_cli.schemas.session_state import SessionInfo, SessionOutcome
from raise_cli.session.index import (
    ActiveSessionPointer,
    clear_active_session,
    read_active_session,
    read_all_active_sessions,
    write_active_session,
)

logger = logging.getLogger(__name__)


class LocalSessionRegistry:
    """File-based session registry — the community (2.4) backend.

    Implements ``SessionRegistry`` protocol. Wraps existing session/index.py
    functions behind a cohesive lifecycle API.

    Args:
        project: Project root path. Used to resolve personal dir.
    """

    def __init__(self, project: Path) -> None:
        self._project = project

    def register(self, session: SessionInfo) -> None:
        """Register a new active session.

        Writes the active-session pointer so close can find the session.
        """
        pointer = ActiveSessionPointer(
            id=session.session_id,
            name=f"{session.developer}@{session.branch}",
            started=session.started,
        )
        write_active_session(pointer, project_root=self._project)
        logger.info("Session registered: %s", session.session_id)

    def active(self, project: Path | None = None) -> list[SessionInfo]:
        """List active sessions, optionally filtered by project.

        Reads the active-session pointer and converts to SessionInfo.
        """
        pointer = read_active_session(project_root=self._project)
        if pointer is None:
            return []

        info = SessionInfo(
            session_id=pointer.id,
            developer="",  # pointer doesn't carry developer
            project=self._project,
            branch="",  # pointer doesn't carry branch
            started=pointer.started,
        )

        # Filter by project if requested
        if project is not None and self._project != project:
            return []

        return [info]

    def close(self, session_id: str, outcome: SessionOutcome) -> None:
        """Close a session — clear pointer, log outcome.

        The actual index entry writing and profile update are handled
        by the caller (session close command) for now. This method
        handles the pointer cleanup.
        """
        clear_active_session(session_id=session_id, project_root=self._project)
        logger.info(
            "Session closed: %s — %s",
            session_id,
            outcome.summary[:80] if outcome.summary else "(no summary)",
        )

    def gc(self, max_age_hours: int = 48) -> list[str]:
        """Garbage collect stale sessions and old directories.

        .. deprecated:: 2.4.0
            Use ``SessionDoctor.diagnose()`` + ``execute()`` instead.
            gc() silently deletes without consent. SessionDoctor (S1248.5)
            provides consent-based cleanup. This method remains for
            protocol compatibility and programmatic use.

        One cleanup operation:
        1. Zombie pointer: if active-session is older than max_age_hours, remove it

        Returns list of cleaned session IDs / paths.
        """
        import warnings

        warnings.warn(
            "gc() is deprecated — use SessionDoctor.diagnose() + execute() "
            "for consent-based cleanup",
            DeprecationWarning,
            stacklevel=2,
        )
        cleaned: list[str] = []

        # 1. Zombie active-session pointers (all agents)
        for pointer in read_all_active_sessions(project_root=self._project):
            age_hours = (
                datetime.now(UTC) - pointer.started.replace(tzinfo=UTC)
            ).total_seconds() / 3600
            if age_hours > max_age_hours:
                clear_active_session(
                    project_root=self._project,
                    cc_session_id=pointer.cc_session_id,
                )
                cleaned.append(pointer.id)
                logger.info(
                    "GC: reaped zombie session %s (%.1fh old, agent=%s)",
                    pointer.id,
                    age_hours,
                    pointer.cc_session_id,
                )

        return cleaned

    def _personal_dir(self) -> Path:
        """Resolve the personal dir for this project."""
        return get_personal_dir(self._project)
