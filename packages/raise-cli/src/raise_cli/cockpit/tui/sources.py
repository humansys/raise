"""Concrete data sources for the Textual cockpit — protocol implementations."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from raise_cli.cockpit.data import (
    PreviewData,
    fetch_preview_data,
    load_all_worktrees,
    main_repo_root,
)
from raise_cli.cockpit.sessions import SessionRow, collect_session_rows
from raise_cli.cockpit.tui.services import SourceHealth
from raise_cli.storage.worktrees import Worktree
from raise_cli.workspace.readiness import WorkspaceReadinessReport


class SqliteSessionSource:
    """SessionSource implementation backed by SQLite lease + session stores."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or main_repo_root()
        self._rows: list[SessionRow] = []
        self._health = SourceHealth()

    @property
    def health(self) -> SourceHealth:
        """Health of the most recent ``refresh()`` (D-S3.3)."""
        return self._health

    def list_sessions(self) -> list[SessionRow]:
        """Return current session rows."""
        return self._rows

    def refresh(self) -> None:
        """Reload session rows from SQLite; keep the cache on failure (D-S3.3)."""
        try:
            self._rows = collect_session_rows(self._root)
            self._health = SourceHealth(ok=True, last_sync=datetime.now(UTC))
        except Exception as exc:  # noqa: BLE001 — degraded mode keeps cache (AC3)
            self._health = SourceHealth(
                ok=False, last_sync=self._health.last_sync, error=str(exc)
            )


class SqliteWorktreeDataSource:
    """WorktreeDataSource implementation backed by SQLite + git."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or main_repo_root()
        self._worktrees: list[Worktree] = []
        self._preview_cache: dict[str, PreviewData] = {}
        self._health = SourceHealth()

    @property
    def health(self) -> SourceHealth:
        """Health of the most recent ``refresh()`` (D-S3.3)."""
        return self._health

    def list_worktrees(self) -> list[Worktree]:
        """Return registered worktrees."""
        return self._worktrees

    def preview(self, worktree_id: str) -> dict[str, object]:
        """Return preview data for a worktree."""
        if worktree_id not in self._preview_cache:
            wt = next(
                (w for w in self._worktrees if w.worktree_id == worktree_id), None
            )
            if wt is None:
                return {}
            self._preview_cache[worktree_id] = fetch_preview_data(wt, self._root)
        pd = self._preview_cache[worktree_id]
        return {
            "dirty_count": pd.dirty_count,
            "behind_count": pd.behind_count,
            "commits": pd.commits,
            "path_exists": pd.path_exists,
            "relative_path": pd.relative_path,
            "last_commit_ts": pd.last_commit_ts,
        }

    def readiness(self, worktree_id: str) -> WorkspaceReadinessReport | None:
        """Evaluate workspace readiness for a worktree."""
        wt = next((w for w in self._worktrees if w.worktree_id == worktree_id), None)
        if wt is None:
            return None
        from raise_cli.cockpit.data import evaluate_readiness_cached

        return evaluate_readiness_cached(Path(wt.path))

    def refresh(self) -> None:
        """Reload worktree list from SQLite + git; keep cache on failure (D-S3.3).

        The preview cache is only cleared on a *successful* refresh — on
        failure it (and ``self._worktrees``) is left untouched so the
        detail panel keeps rendering the last known-good data.
        """
        try:
            self._worktrees = load_all_worktrees()
            self._health = SourceHealth(ok=True, last_sync=datetime.now(UTC))
            self._preview_cache.clear()
        except Exception as exc:  # noqa: BLE001 — degraded mode keeps cache (AC3)
            self._health = SourceHealth(
                ok=False, last_sync=self._health.last_sync, error=str(exc)
            )
