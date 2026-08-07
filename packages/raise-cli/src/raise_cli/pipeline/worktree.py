"""Git worktree management for pipeline branch isolation.

Story: S1064.7 — Worktree Management
Epic: E1064 — Pipeline Engine Core
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Final

from pydantic import BaseModel

logger = logging.getLogger(__name__)

WORKTREE_BASE_DIR: Final[str] = ".rai-worktrees"


class WorktreeError(Exception):
    """Raised when a git worktree operation fails."""


class WorktreeInfo(BaseModel, frozen=True):
    """Immutable snapshot of a git worktree."""

    path: Path
    branch: str | None = None


def parse_porcelain(output: str) -> list[WorktreeInfo]:
    """Parse ``git worktree list --porcelain`` output into WorktreeInfo list."""
    if not output.strip():
        return []

    results: list[WorktreeInfo] = []
    # Split on blank lines (double newline)
    blocks = output.strip().split("\n\n")
    for block in blocks:
        if not block.strip():
            continue
        path: Path | None = None
        branch: str | None = None
        for line in block.strip().splitlines():
            if line.startswith("worktree "):
                path = Path(line.removeprefix("worktree ").strip())
            elif line.startswith("branch "):
                raw = line.removeprefix("branch ").strip()
                branch = raw.removeprefix("refs/heads/")
        if path is not None:
            results.append(WorktreeInfo(path=path, branch=branch))
    return results


class WorktreeManager:
    """Manage git worktrees for pipeline branch isolation."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def branch_to_path(self, branch: str) -> Path:
        """Convert a branch name to a deterministic worktree directory path."""
        return self._repo_root / WORKTREE_BASE_DIR / branch.replace("/", "--")

    async def _run_git(self, *args: str, cwd: Path | None = None) -> str:
        """Run a git command asynchronously, raising WorktreeError on failure."""
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=cwd or self._repo_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60.0)
        except BaseException:
            proc.kill()
            await proc.wait()
            raise
        if proc.returncode != 0:
            raise WorktreeError(f"git {' '.join(args)}: {stderr.decode().strip()}")
        return stdout.decode()

    async def create(self, branch: str, base: str) -> Path:
        """Create a worktree for *branch* from *base*, returning the path.

        Idempotent: returns existing path if worktree already exists.
        Symlinks ``repo_root/.raise/`` into the worktree when present.
        """
        path = self.branch_to_path(branch)
        if path.is_dir():
            logger.info("Worktree already exists at %s", path)
            return path
        try:
            await self._run_git("worktree", "add", "-b", branch, str(path), base)
        except WorktreeError:
            if path.is_dir():
                return path
            raise
        # Symlink .raise/ if it exists in the main repo
        raise_dir = self._repo_root / ".raise"
        if raise_dir.is_dir():
            (path / ".raise").symlink_to(raise_dir)
        return path

    async def cleanup(self, branch: str) -> None:
        """Remove the worktree for *branch* without deleting the branch.

        Blocked when the branch belongs to a worktree leased by another
        live session (S8170.7, branch-operation guard).
        """
        path = self.branch_to_path(branch)
        if not path.exists():
            logger.warning("Worktree not found at %s, skipping cleanup", path)
            return
        from raise_cli.pipeline.branch_guard import guard_branch_operation

        decision = await asyncio.to_thread(
            guard_branch_operation, "remove", branch, str(self._repo_root)
        )
        if decision.status == "blocked":
            raise WorktreeError(decision.message)
        if decision.status == "warning" and decision.message:
            logger.warning("%s", decision.message)
        await self._run_git("worktree", "remove", "--force", str(path))

    async def list_active(self) -> list[WorktreeInfo]:
        """List all active worktrees in the repository."""
        output = await self._run_git("worktree", "list", "--porcelain")
        return parse_porcelain(output)
