"""Git worktrees under ``.worktree/`` that have no registry row — RAISE-18991.

``rai worktree prune`` only sees registered worktrees; these are invisible to
it. They are reported as proposals with evidence and never removed.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from raise_cli.worktree.prune import is_branch_landed, is_working_tree_clean


@dataclass(frozen=True)
class GitWorktree:
    """A linked git worktree as reported by ``git worktree list --porcelain``."""

    path: Path
    branch: str | None  # None when detached


@dataclass(frozen=True)
class UnregisteredWorktree:
    """Evidence for an unregistered worktree proposal."""

    path: Path
    branch: str | None
    landed: bool
    clean: bool
    age_days: int | None


def main_checkout(repo: Path) -> Path:
    """Primary checkout root (parent of the common git dir); ``repo`` on error."""
    r = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        stdin=subprocess.DEVNULL,  # RAISE-18871: prevent Win32 handle inheritance
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return repo
    return Path(r.stdout.strip()).parent


def list_git_worktrees_under(repo: Path) -> list[GitWorktree]:
    """Linked worktrees whose path is under ``<main checkout>/.worktree/``."""
    root = (main_checkout(repo) / ".worktree").resolve()
    r = subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
        stdin=subprocess.DEVNULL,  # RAISE-18871: prevent Win32 handle inheritance
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        return []
    found: list[GitWorktree] = []
    for block in r.stdout.split("\n\n"):
        path: Path | None = None
        branch: str | None = None
        for line in block.splitlines():
            if line.startswith("worktree "):
                path = Path(line[len("worktree ") :]).resolve()
            elif line.startswith("branch "):
                branch = line[len("branch ") :].removeprefix("refs/heads/")
        if path is not None and path.parent == root:
            found.append(GitWorktree(path=path, branch=branch))
    return found


def last_commit_age_days(path: Path) -> int | None:
    """Whole days since the HEAD commit of ``path``; None if unknown."""
    r = subprocess.run(
        ["git", "-C", str(path), "log", "-1", "--format=%ct"],
        stdin=subprocess.DEVNULL,  # RAISE-18871: prevent Win32 handle inheritance
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return max(0, int((time.time() - int(r.stdout.strip())) // 86400))
    except ValueError:
        return None


def find_unregistered(
    repo: Path, registered_paths: set[str], target: str
) -> list[UnregisteredWorktree]:
    """Unregistered ``.worktree/*`` git worktrees, with prune-style evidence."""
    known = {Path(p).resolve() for p in registered_paths}
    out: list[UnregisteredWorktree] = []
    for gw in list_git_worktrees_under(repo):
        if gw.path in known:
            continue
        landed = (
            gw.branch is not None
            and is_branch_landed(repo, gw.branch, target) is not None
        )
        out.append(
            UnregisteredWorktree(
                path=gw.path,
                branch=gw.branch,
                landed=landed,
                clean=is_working_tree_clean(gw.path),
                age_days=last_commit_age_days(gw.path),
            )
        )
    return out
