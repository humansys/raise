"""Local SessionRegistry — file-based session lifecycle management.

Implements the SessionRegistry protocol (ADR-038) as a facade over
existing session index and active-session pointer infrastructure.

Delegates to session/index.py for persistence. Adds gc() for zombie
reaping, directory retention, and stale output cleanup.

Architecture: E1248 (Git-First Session State), S1248.2
"""

from __future__ import annotations

import logging
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.config.paths import get_personal_dir
from raise_cli.schemas.session_state import SessionInfo, SessionOutcome
from raise_cli.session.index import (
    ActiveSessionPointer,
    clear_active_session,
    read_active_session,
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

        Three cleanup operations:
        1. Zombie pointer: if active-session is older than max_age_hours, remove it
        2. Session dir retention: keep max 20 dirs or 30 days (T2)
        3. Stale output: remove session-output.yaml older than 24h (T2)

        Returns list of cleaned session IDs / paths.
        """
        cleaned: list[str] = []

        # 1. Zombie active-session pointer
        pointer = read_active_session(project_root=self._project)
        if pointer is not None:
            age_hours = (
                datetime.now(UTC) - pointer.started.replace(tzinfo=UTC)
            ).total_seconds() / 3600
            if age_hours > max_age_hours:
                clear_active_session(project_root=self._project)
                cleaned.append(pointer.id)
                logger.info(
                    "GC: reaped zombie session %s (%.1fh old)",
                    pointer.id,
                    age_hours,
                )

        # 2. Session dir retention (keep max 20)
        cleaned.extend(self._gc_session_dirs())

        # 3. Stale output cleanup (>24h)
        cleaned.extend(self._gc_stale_output())

        return cleaned

    def _gc_session_dirs(self, max_dirs: int = 20) -> list[str]:
        """Remove oldest session dirs beyond retention limit."""
        cleaned: list[str] = []
        personal = self._personal_dir()
        sessions_dir = personal / "sessions"
        if not sessions_dir.is_dir():
            return cleaned

        # Collect all session dirs (direct children that are dirs)
        dirs = sorted(
            (d for d in sessions_dir.iterdir() if d.is_dir()),
            key=lambda d: d.stat().st_mtime,
        )

        if len(dirs) <= max_dirs:
            return cleaned

        # Remove oldest dirs beyond limit
        to_remove = dirs[: len(dirs) - max_dirs]
        for d in to_remove:
            try:
                shutil.rmtree(d)
                cleaned.append(f"dir:{d.name}")
                logger.info("GC: removed session dir %s", d.name)
            except OSError as exc:
                logger.warning("GC: failed to remove %s: %s", d.name, exc)

        return cleaned

    def _gc_stale_output(self, max_age_hours: int = 24) -> list[str]:
        """Remove session-output.yaml if older than max_age_hours."""
        cleaned: list[str] = []
        personal = self._personal_dir()
        output = personal / "session-output.yaml"
        if not output.exists():
            return cleaned

        age_hours = (time.time() - output.stat().st_mtime) / 3600
        if age_hours > max_age_hours:
            try:
                output.unlink()
                cleaned.append("session-output.yaml")
                logger.info("GC: removed stale session-output.yaml (%.1fh old)", age_hours)
            except OSError as exc:
                logger.warning("GC: failed to remove session-output.yaml: %s", exc)

        return cleaned

    def _personal_dir(self) -> Path:
        """Resolve the personal dir for this project."""
        return get_personal_dir(self._project)
