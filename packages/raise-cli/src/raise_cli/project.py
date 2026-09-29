"""Shared project identity root resolution — git-aware, worktree-safe.

Single source of truth for resolving the main project root from any
working directory, including git worktrees. Pipeline, session, and
storage code should use ``resolve_project_root()`` instead of bare
``Path.cwd()`` to ensure consistent paths across worktrees.

Use ``raise_cli.config.paths.resolve_checkout_root()`` when the active
linked worktree path matters.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _git_common_dir(cwd: Path) -> str:
    """Run ``git rev-parse --git-common-dir`` and return stdout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise RuntimeError(f"git rev-parse failed: {exc}") from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"git rev-parse failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def resolve_project_root(cwd: Path | None = None) -> Path:
    """Resolve the main project root, handling git worktrees.

    In a worktree, ``git rev-parse --git-common-dir`` points to the
    main repo's ``.git/`` directory. We derive the project root from that.

    Falls back to *cwd* (or ``Path.cwd()``) when not inside a git repo.
    """
    effective_cwd = cwd or Path.cwd()

    try:
        common_dir = _git_common_dir(effective_cwd)
    except RuntimeError:
        return effective_cwd

    common_path = Path(common_dir)
    if not common_path.is_absolute():
        common_path = (effective_cwd / common_path).resolve()

    if common_path.name == ".git":
        return common_path.parent
    return effective_cwd
