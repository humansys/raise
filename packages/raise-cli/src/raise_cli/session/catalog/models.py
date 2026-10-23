"""Core domain models for the session catalog."""

from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel

from raise_cli.session.catalog.scope import HostScope, ScopeSpec


class SessionState(str, enum.Enum):
    """Lifecycle state of a runtime session row."""

    PROVISIONING = "provisioning"
    LIVE = "live"
    EXITED = "exited"


_ACTIVE_STATES = frozenset({SessionState.PROVISIONING, SessionState.LIVE})


class RuntimeSessionRecord(BaseModel, frozen=True):
    """A harness process tracked in runtime_sessions (schema v70).

    ``session_id`` is the raw ID without the ``rai-`` tmux prefix.
    ``worktree_id`` matches the value in the worktree registry;
    empty string means the main checkout (D3).
    """

    session_id: str
    project_id: str
    worktree_id: str
    alias: str
    harness: str
    state: SessionState
    governance_session_id: str | None
    created_at: datetime
    updated_at: datetime

    def source_qualified_alias(self, source_id: str) -> str:
        """Return alias qualified by source, e.g. ``calm-finch@local``."""
        return f"{self.alias}@{source_id}"

    @property
    def last_activity_at(self) -> datetime:
        """Most-recent activity timestamp (alias for updated_at until dedicated column added)."""
        return self.updated_at

    @property
    def is_active(self) -> bool:
        """True when state is provisioning or live."""
        return self.state in _ACTIVE_STATES


class CatalogFilter(BaseModel, frozen=True):
    """Query filter for ``SessionCatalog.query()``."""

    scope: ScopeSpec = HostScope()
    states: frozenset[SessionState] = frozenset(
        {SessionState.LIVE, SessionState.PROVISIONING}
    )
    limit: int | None = None
