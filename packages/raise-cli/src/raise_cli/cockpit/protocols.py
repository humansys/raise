"""Cockpit data source protocols — structural contracts for E2/E3.

These protocols define the boundary between the cockpit TUI and its data
sources. Concrete implementations live in data.py (E1/S2) and fleet
modules (post-MVP). Downstream code imports protocols, never implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from raise_cli.cockpit.sessions import SessionRow
    from raise_cli.storage.worktrees import Worktree
    from raise_cli.workspace.readiness import WorkspaceReadinessReport


@runtime_checkable
class SessionSource(Protocol):
    """Provides session rows for the cockpit Session Rail."""

    def list_sessions(self) -> list[SessionRow]:
        """Return current session rows."""
        ...

    def refresh(self) -> None:
        """Invalidate cached data and reload from source."""
        ...


@runtime_checkable
class WorktreeDataSource(Protocol):
    """Provides worktree data for the cockpit list and detail panel."""

    def list_worktrees(self) -> list[Worktree]:
        """Return registered worktrees."""
        ...

    def preview(self, worktree_id: str) -> dict[str, object]:
        """Return preview data (branch, commits, dirty state) for a worktree."""
        ...

    def readiness(self, worktree_id: str) -> WorkspaceReadinessReport | None:
        """Evaluate workspace readiness for a worktree."""
        ...


@runtime_checkable
class FleetSource(Protocol):
    """Provides fleet agent data for the fleet tab (post-MVP)."""

    def list_agents(self) -> list[dict[str, object]]:
        """Return active fleet agents."""
        ...

    def refresh(self) -> None:
        """Invalidate cached data and reload from source."""
        ...
