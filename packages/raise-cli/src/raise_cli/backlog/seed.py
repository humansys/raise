"""Git-history backfill for work_items (RAISE-15143).

Extracts all RAISE-XXXXX keys from git log subjects and returns a sorted
deduplicated list for use by ``WorkItemStore.seed_jira_keys``.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_RAISE_KEY_RE = re.compile(r"\bRAISE-\d+\b")


def extract_raise_keys(
    project_root: Path,
    limit: int | None = None,
) -> list[str]:
    """Return sorted unique RAISE-XXXXX keys found in git log subjects.

    Args:
        project_root: Path to the git repository root.
        limit: If set, restrict to the most recent ``limit`` commits.

    Returns:
        Sorted list of unique RAISE-XXXXX key strings.
    """
    cmd = ["git", "log", "--all", "--no-merges", "--pretty=format:%s"]
    if limit is not None:
        cmd.append(f"-{limit}")
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    keys = set(_RAISE_KEY_RE.findall(result.stdout))
    return sorted(keys)
