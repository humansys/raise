"""Idle worktree detection — RAISE-18991.

A worktree is idle when neither a commit nor a session touched it for N days
and no live session holds its lease. Applies to registered and unregistered
``.worktree/*`` worktrees alike. Detection only: nothing is ever removed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from raise_cli.worktree.prune import has_active_lease
from raise_cli.worktree.unregistered import (
    last_commit_age_days,
    list_git_worktrees_under,
)

DEFAULT_IDLE_DAYS = 14
IDLE_DAYS_ENV = "RAI_WORKTREE_IDLE_DAYS"


@dataclass(frozen=True)
class IdleWorktree:
    """An idle worktree and the evidence for it."""

    name: str
    path: Path
    registered: bool
    commit_age_days: int


def idle_days_from_env() -> int:
    """N from ``RAI_WORKTREE_IDLE_DAYS``; invalid or non-positive -> 14."""
    raw = os.environ.get(IDLE_DAYS_ENV, "").strip()
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_IDLE_DAYS
    return value if value > 0 else DEFAULT_IDLE_DAYS


def is_idle(
    path: Path,
    last_session: datetime | None,
    idle_days: int,
    *,
    now: datetime | None = None,
) -> int | None:
    """Commit age in days if the last commit AND last session are older than N.

    Returns None when not idle or when the commit age cannot be determined
    (conservative: unknown is never reported idle).
    """
    age = last_commit_age_days(path)
    if age is None or age <= idle_days:
        return None
    if last_session is not None:
        current = now or datetime.now(UTC)
        if last_session.tzinfo is None:
            last_session = last_session.replace(tzinfo=UTC)
        if current - last_session <= timedelta(days=idle_days):
            return None
    return age


def find_idle_worktrees(project: Path, idle_days: int) -> list[IdleWorktree]:
    """Idle registered + unregistered worktrees without a live lease."""
    from raise_cli.session.open_service import (
        _worktree_last_active,  # pyright: ignore[reportPrivateUsage]
    )
    from raise_cli.storage.connection import get_project_db
    from raise_cli.storage.worktrees import SqliteWorktreeStore

    store = SqliteWorktreeStore(project)
    conn = get_project_db(project)
    idle: list[IdleWorktree] = []
    seen: set[Path] = set()

    for wt in store.list_worktrees():
        path = Path(wt.path)
        seen.add(path.resolve())
        if not path.exists() or has_active_lease(wt.worktree_id, project):
            continue
        age = is_idle(path, _worktree_last_active(conn, wt), idle_days)
        if age is not None:
            idle.append(IdleWorktree(wt.worktree_id, path, True, age))

    for gw in list_git_worktrees_under(project):
        if gw.path in seen:
            continue
        age = is_idle(gw.path, None, idle_days)
        if age is not None:
            idle.append(IdleWorktree(gw.path.name, gw.path, False, age))
    return idle
