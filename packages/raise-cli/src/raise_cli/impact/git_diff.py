"""Git changed-file collection for impact analysis."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitDiffError(RuntimeError):
    """Raised when changed files cannot be collected from Git."""


def collect_changed_files(
    base_ref: str,
    head_ref: str | None,
    cwd: Path,
) -> list[Path]:
    """Return changed files between base and head as sorted relative paths."""
    revision_range = f"{base_ref}...{head_ref or 'HEAD'}"
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", revision_range],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise GitDiffError(f"git diff failed: {exc}") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise GitDiffError(f"git diff failed: {detail}")

    return sorted(
        {Path(line.strip()) for line in result.stdout.splitlines() if line.strip()},
        key=lambda path: path.as_posix(),
    )
