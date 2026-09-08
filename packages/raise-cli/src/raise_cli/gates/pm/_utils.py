"""Shared utilities for PM discipline gates.

Module is package-private (``_utils``). Functions are public within the package.

Architecture: RAISE-11404, S11404.4
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_branch(working_dir: Path) -> str:
    """Return current git branch name, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def find_active_scope(working_dir: Path) -> Path | None:
    """Return the most recently modified EPIC-level scope.md, or None.

    Matches only ``work/epics/{epic-dir}/scope.md`` — one path segment below
    ``work/epics/``, exact filename ``scope.md``. Story-level scope files
    live one level deeper (``work/epics/{epic-dir}/stories/s{N}.{M}-scope.md``)
    and must NOT match here: a recursive ``**/*scope.md`` glob previously
    matched them too, so a freshly-touched story scope could shadow the
    epic's own scope.md for epic-design-time gates (RAISE-14588).
    """
    scope_files = list(working_dir.glob("work/epics/*/scope.md"))
    if not scope_files:
        return None
    return max(scope_files, key=lambda p: p.stat().st_mtime)


def extract_section_content(content: str, heading: str) -> str:
    """Extract text under a level-2 heading (``## {heading}``), stripped.

    Parses line-by-line: collects lines after ``## {heading}`` until the next
    level-2 heading (``## ``) or end of file.
    """
    in_section = False
    result: list[str] = []
    for line in content.splitlines():
        if line.startswith("## ") and heading in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            result.append(line)
    return "\n".join(result).strip()
