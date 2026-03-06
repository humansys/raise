"""Interactive conflict resolution for skill file updates.

When both upstream and user have modified a skill file, this module
provides an interactive prompt (TTY) or safe default (non-TTY) to
resolve the conflict.

Inspired by Rails Thor [Ynaqdhm] pattern, adapted for our use case.
Default action is KEEP (protect user work).
"""

from __future__ import annotations

import difflib
import sys
from enum import StrEnum


class ConflictAction(StrEnum):
    """User's chosen action for a conflicting skill file."""

    KEEP = "keep"
    OVERWRITE = "overwrite"
    DIFF = "diff"
    BACKUP_OVERWRITE = "backup_overwrite"
    KEEP_ALL = "keep_all"
    OVERWRITE_ALL = "overwrite_all"


_INPUT_MAP: dict[str, ConflictAction] = {
    "k": ConflictAction.KEEP,
    "o": ConflictAction.OVERWRITE,
    "d": ConflictAction.DIFF,
    "b": ConflictAction.BACKUP_OVERWRITE,
    "K": ConflictAction.KEEP_ALL,
    "O": ConflictAction.OVERWRITE_ALL,
    "": ConflictAction.KEEP,  # Enter = keep (safe default)
}


def format_skill_diff(skill_name: str, old_content: str, new_content: str) -> str:
    """Format a unified diff between old and new skill content.

    Args:
        skill_name: Name of the skill for display.
        old_content: Current on-disk content.
        new_content: New upstream content.

    Returns:
        Formatted unified diff string.
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{skill_name}/SKILL.md (yours)",
        tofile=f"{skill_name}/SKILL.md (upstream)",
    )
    return "".join(diff)


def prompt_skill_conflict(
    skill_name: str,
    old_content: str,
    new_content: str,
) -> ConflictAction:
    """Prompt user to resolve a skill file conflict.

    In non-TTY environments, returns KEEP without prompting.

    Args:
        skill_name: Name of the conflicting skill.
        old_content: Current on-disk content (user's version).
        new_content: New upstream content.

    Returns:
        The user's chosen ConflictAction.
    """
    if not sys.stdin.isatty():
        return ConflictAction.KEEP

    print(f"\n  {skill_name}/SKILL.md — both upstream and local changes")

    while True:
        choice = input(
            "  [d]iff  [o]verwrite  [k]eep (default)  "
            "[b]ackup+overwrite  [O]verwrite-all  [K]eep-all: "
        )

        action = _INPUT_MAP.get(choice)
        if action is None:
            print(f"  Invalid choice: '{choice}'. Try again.")
            continue

        if action == ConflictAction.DIFF:
            diff = format_skill_diff(skill_name, old_content, new_content)
            print(diff if diff else "  (no differences)")
            continue  # Re-prompt after showing diff

        return action
