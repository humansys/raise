"""Session protocol contracts for state derivation, registry, and monitoring.

Defines the typed interfaces that session backends must satisfy.
All Protocols are ``@runtime_checkable`` for isinstance() checks.

**Backends:**
- Git/local (2.4): ``GitStateDeriver``, ``LocalSessionRegistry``, ``LocalWorkstreamMonitor``
- Server (3.0): registered via raise-pro/raise-server entry points

Architecture: ADR-038 (Session Protocols with Derived State)
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from raise_cli.schemas.session_state import (
    ActivityEntry,
    CurrentWork,
    Improvement,
    SessionInfo,
    SessionInsights,
    SessionOutcome,
)


@runtime_checkable
class StateDeriver(Protocol):
    """Derives current work context from available sources.

    Git backend: parses branch, scope.md frontmatter, git log.
    Server backend: real-time tracking with heartbeats.
    """

    def current_work(self, project: Path) -> CurrentWork: ...

    def recent_activity(
        self, project: Path, limit: int = 10
    ) -> list[ActivityEntry]: ...


@runtime_checkable
class SessionRegistry(Protocol):
    """Tracks active sessions across a developer's workstreams.

    Git backend: local files (active-session, index.jsonl) with zombie gc.
    Server backend: centralized DB, cross-repo, cross-machine.
    """

    def register(self, session: SessionInfo) -> None: ...

    def active(self, project: Path | None = None) -> list[SessionInfo]: ...

    def close(self, session_id: str, outcome: SessionOutcome) -> None: ...

    def gc(self, max_age_hours: int = 48) -> list[str]: ...


@runtime_checkable
class WorkstreamMonitor(Protocol):
    """Observes session patterns and suggests improvements.

    Git backend: heuristics from journal + git log.
    Server backend: async agent with pattern recognition across team.
    """

    def analyze_session(self, session_id: str) -> SessionInsights: ...

    def suggest_improvements(self, last_n: int = 5) -> list[Improvement]: ...
