"""Cockpit data layer — extracted from app.py monolith (RAISE-16704).

Data loading functions for worktrees, preview stats, and readiness.
No rendering logic — consumed by both Rich and Textual paths via protocols.
"""

from __future__ import annotations

import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.cockpit.filter import filter_open_worktrees
from raise_cli.project_config import resolve_dev_branch
from raise_cli.storage.worktrees import Worktree
from raise_cli.workspace.readiness import (
    WorkspaceReadinessReport,
    evaluate_workspace_readiness,
)
from raise_cli.worktree.provision import git_worktree_readiness_policy

# ---------------------------------------------------------------------------
# Preview data — git stats fetched per selection
# ---------------------------------------------------------------------------


@dataclass
class PreviewData:
    """Git stats for the selected worktree."""

    dirty_count: int
    behind_count: int
    commits: list[str]
    path_exists: bool
    relative_path: str
    last_commit_ts: float | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Git stat helpers
# ---------------------------------------------------------------------------


def _git_dirty_count(path: Path) -> int:
    """Count dirty (modified/untracked) files via `git status --short --porcelain`."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "status", "--short", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode != 0:
            return 0
        return len([ln for ln in result.stdout.splitlines() if ln.strip()])
    except Exception:  # noqa: BLE001
        return 0


def _git_behind_count(path: Path, merge_target: str) -> int:
    """Count commits behind origin/<merge_target> via `git rev-list --count`."""
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(path),
                "rev-list",
                f"HEAD..origin/{merge_target}",
                "--count",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode != 0:
            return 0
        stripped = result.stdout.strip()
        return int(stripped) if stripped.isdigit() else 0
    except Exception:  # noqa: BLE001
        return 0


def _git_last_commit_ts(path: Path) -> float | None:
    """Return the unix timestamp of the most recent commit, or None."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        stripped = result.stdout.strip()
        if result.returncode == 0 and stripped.isdigit():
            return float(stripped)
    except Exception:  # noqa: BLE001,S110
        pass
    return None


def _git_recent_commits(path: Path) -> list[str]:
    """Return last 3 commits as 'sha7 · message' strings."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "log", "--oneline", "-3"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode != 0:
            return []
        commits: list[str] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            sha, _, rest = line.partition(" ")
            commits.append(f"{sha[:7]} · {rest}")
        return commits
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------------------
# Preview data fetching
# ---------------------------------------------------------------------------


def fetch_preview_data(
    worktree: Worktree,
    repo_root: Path,
) -> PreviewData:
    """Fetch git stats for a worktree via subprocess.

    Each subprocess.run call uses timeout=2 to avoid UI freezes.

    Args:
        worktree: The worktree to inspect.
        repo_root: Repository root used to compute a relative display path.

    Returns:
        PreviewData with git stats, or error info if path missing.
    """
    path = Path(worktree.path)
    try:
        rel = path.relative_to(repo_root)
        relative_path = str(rel)
    except ValueError:
        relative_path = worktree.path

    if not path.exists():
        return PreviewData(
            dirty_count=0,
            behind_count=0,
            commits=[],
            path_exists=False,
            relative_path=relative_path,
            error="path not found",
        )

    dirty_count = _git_dirty_count(path)
    behind_count = _git_behind_count(path, worktree.merge_target)
    commits = _git_recent_commits(path)
    last_commit_ts = _git_last_commit_ts(path)

    return PreviewData(
        dirty_count=dirty_count,
        behind_count=behind_count,
        commits=commits,
        path_exists=True,
        relative_path=relative_path,
        last_commit_ts=last_commit_ts,
    )


# ---------------------------------------------------------------------------
# Workspace readiness cache — dual-layer
# ---------------------------------------------------------------------------

_READINESS_CACHE_TTL_S: int = 30
_readiness_cache: dict[tuple[str, int], WorkspaceReadinessReport | None] = {}


def evaluate_readiness_cached(wt_path: Path) -> WorkspaceReadinessReport | None:
    """Return workspace readiness, cached for 30 seconds per path (synchronous)."""
    bucket = int(time.monotonic() // _READINESS_CACHE_TTL_S)
    cache_key = (str(wt_path), bucket)
    if cache_key not in _readiness_cache:
        try:
            policy = git_worktree_readiness_policy()
            _readiness_cache[cache_key] = evaluate_workspace_readiness(wt_path, policy)
        except Exception:  # noqa: BLE001
            _readiness_cache[cache_key] = None
    return _readiness_cache[cache_key]


_readiness_bg_cache: dict[str, WorkspaceReadinessReport | None] = {}
_readiness_bg_pending: set[str] = set()
_readiness_bg_lock = threading.Lock()


def evaluate_readiness_async(wt_path: Path) -> WorkspaceReadinessReport | None:
    """Return cached readiness or None while background evaluation runs."""
    key = str(wt_path)
    if key in _readiness_bg_cache:
        return _readiness_bg_cache[key]

    with _readiness_bg_lock:
        if key in _readiness_bg_pending:
            return None
        _readiness_bg_pending.add(key)

    def _worker() -> None:
        try:
            policy = git_worktree_readiness_policy()
            _readiness_bg_cache[key] = evaluate_workspace_readiness(wt_path, policy)
        except Exception:  # noqa: BLE001
            _readiness_bg_cache[key] = None
        finally:
            with _readiness_bg_lock:
                _readiness_bg_pending.discard(key)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return None


# ---------------------------------------------------------------------------
# Git worktree parsing
# ---------------------------------------------------------------------------


@dataclass
class GitWorktreeEntry:
    """A git worktree entry from `git worktree list --porcelain`."""

    path: Path
    branch: str | None
    slug: str


def _slug_from_path(wt_path: Path, repo_root: Path) -> str:
    """Infer worktree slug from its directory name."""
    name = wt_path.name
    prefix = repo_root.name + "-"
    return name.removeprefix(prefix)


def parse_git_worktrees(repo_root: Path) -> list[GitWorktreeEntry]:
    """Return all git worktrees except the main checkout, from --porcelain output."""
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return []
    except Exception:  # noqa: BLE001
        return []

    entries: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if cur:
                entries.append(cur)
            cur = {"path": line[9:]}
        elif line.startswith("branch "):
            cur["branch"] = line[7:].removeprefix("refs/heads/")
        elif not line.strip() and cur:
            entries.append(cur)
            cur = {}
    if cur:
        entries.append(cur)

    result_list: list[GitWorktreeEntry] = []
    for entry in entries[1:]:
        path = Path(entry["path"])
        branch = entry.get("branch")
        slug = _slug_from_path(path, repo_root)
        result_list.append(GitWorktreeEntry(path=path, branch=branch, slug=slug))
    return result_list


def _make_unregistered_worktree(
    git_wt: GitWorktreeEntry, merge_target: str
) -> Worktree:
    """Create a synthetic Worktree for a git worktree not present in the DB."""
    return Worktree(
        worktree_id=git_wt.slug,
        project_id="",
        path=str(git_wt.path),
        branch=git_wt.branch or "",
        merge_target=merge_target,
        stories=[],
        status="unregistered",
        last_session_id=None,
        created_at=datetime.now(UTC).isoformat(),
    )


def main_repo_root() -> Path:
    """Return the main repo root, even when called from inside a git worktree."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            git_common = Path(result.stdout.strip())
            if not git_common.is_absolute():
                git_common = (Path.cwd() / git_common).resolve()
            return git_common.parent
    except Exception:  # noqa: BLE001,S110
        pass
    return Path.cwd()


def load_all_worktrees() -> list[Worktree]:
    """Load and reconcile worktrees from git (source of truth) and the local DB.

    Returns a unified list ordered: registered (by recency) → unregistered → orphans.
    """
    from dataclasses import replace as dc_replace

    from raise_cli.storage.worktrees import SqliteWorktreeStore

    repo_root = main_repo_root()
    merge_target = resolve_dev_branch(repo_root)

    git_wts = parse_git_worktrees(repo_root)
    git_by_path = {wt.path.resolve(): wt for wt in git_wts}

    try:
        store = SqliteWorktreeStore(repo_root)
        db_wts = filter_open_worktrees(store.list_worktrees(include_closed=False))
    except Exception:  # noqa: BLE001
        db_wts = []
    db_by_path = {Path(wt.path).resolve(): wt for wt in db_wts}

    registered = [wt for path, wt in db_by_path.items() if path in git_by_path]
    orphans = [wt for path, wt in db_by_path.items() if path not in git_by_path]
    unregistered = [
        _make_unregistered_worktree(gwt, merge_target)
        for path, gwt in git_by_path.items()
        if path not in db_by_path
    ]

    orphans = [dc_replace(wt, status="orphan") for wt in orphans]

    return registered + unregistered + orphans
