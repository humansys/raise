"""Shared branch-drift guard (RAISE-11103).

All direct-commit paths (task complete, story scope commit, release) had a
pre-commit branch assertion but no re-check after the ``git commit`` itself,
leaving a TOCTOU window where a concurrent checkout/branch-switch in another
session could land a commit on the wrong branch undetected. This module
gives every call site one place to read and compare the current branch.

Deliberately a plain ``(bool, str)`` return, not a ``CheckResult`` — the
call sites are not homogeneous (two use ``CheckResult``, ``release.py``
uses ``cli_error``), so each caller wraps this result in its own existing
error-handling shape rather than a forced uniform contract (architecture
review, H6/H8).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_GIT_TIMEOUT_S = 10


def current_branch(cwd: Path) -> str:
    """Read the current branch name via ``git branch --show-current``.

    The simpler, porcelain-stable read (its own historical rationale, see
    module docstring) rather than ``rev-parse --abbrev-ref HEAD`` — it
    already returns ``""`` uniformly for both "no git" and "detached HEAD",
    with no separate ``"HEAD"``-literal special-case to handle.

    Returns:
        The branch name, or ``""`` when git is unavailable, times out,
        exits non-zero, or HEAD is detached.
    """
    try:
        proc = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def assert_head_branch(cwd: Path, expected: str) -> tuple[bool, str]:
    """Read the current branch and compare it to *expected*.

    Returns:
        ``(True, current_branch)`` when it matches *expected*.
        ``(False, current_branch)`` on drift.
        ``(False, "")`` when git is unavailable, times out, or exits
        non-zero — never matches a real expected branch name, so callers
        treat it as drift without needing a separate error path.
    """
    current = current_branch(cwd)
    return current == expected, current
