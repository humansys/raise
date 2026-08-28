"""Git attribution helpers for portfolio suggest (RAISE-15255).

Provides thin wrappers around ``git log`` and ``git diff-tree`` to map a
Jira key to the commits and changed files associated with it, and a
heuristic for inferring ``change_mode`` from numstat deletions.

All functions are pure (no I/O side effects beyond subprocess) and accept
``repo_root`` so they are trivially patchable in tests.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_commits_for_key(key: str, repo_root: Path) -> list[str]:
    """Return commit SHAs whose message mentions *key*.

    Searches all branches via ``--all``.  Returns an empty list when no
    commits match or when ``git log`` exits non-zero (e.g. outside a repo).

    Args:
        key: Jira key to search for (e.g. ``"RAISE-15255"``).
        repo_root: Absolute path to the repository root.

    Returns:
        Sorted (by git log order) list of full commit SHAs.
    """
    result = subprocess.run(
        ["git", "log", "--all", "--grep", key, "--format=%H"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_changed_files_for_commits(shas: list[str], repo_root: Path) -> list[str]:
    """Return unique repo-relative file paths changed across *shas*.

    Uses ``git diff-tree`` per commit.  Commits that fail (e.g. merge
    commits with unusual formats) are silently skipped so a single bad
    SHA never aborts the whole set.

    Args:
        shas: List of full commit SHAs.
        repo_root: Absolute path to the repository root.

    Returns:
        Sorted, deduplicated list of repo-relative file paths.
    """
    files: set[str] = set()
    for sha in shas:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            continue
        files.update(
            line.strip() for line in result.stdout.splitlines() if line.strip()
        )
    return sorted(files)


def infer_change_mode(shas: list[str], repo_root: Path, *, has_contracts: bool) -> str:
    """Infer ``change_mode`` from numstat deletions.

    Heuristic:
    - ``breaking`` — when *has_contracts* is True (contract surfaces touched).
    - ``additive`` — when no deletions are recorded across all *shas*.
    - ``evolutionary`` — when at least one deletion is found.

    Args:
        shas: Commit SHAs to inspect.
        repo_root: Absolute path to the repository root.
        has_contracts: Whether any contract symbol nodes were found in the
            changed files (from graph DB lookup).

    Returns:
        One of ``"breaking"``, ``"additive"``, ``"evolutionary"``, or ``""``
        when *shas* is empty and *has_contracts* is False.
    """
    if has_contracts:
        return "breaking"
    if not shas:
        return ""
    total_del = 0
    for sha in shas:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--numstat", sha],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1].isdigit():
                total_del += int(parts[1])
    return "additive" if total_del == 0 else "evolutionary"
