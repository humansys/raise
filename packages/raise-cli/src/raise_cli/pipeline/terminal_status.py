"""Shared terminal-status helper (S14559.1 T1, RAISE-14588).

Extracted from ``epic_story_iteration._is_story_terminal`` so any pipeline
that needs to classify an issue's status text as "done" can reuse the same
token set instead of cloning it (design AG2 mitigation). Adds ``archived``,
which the epic-only helper lacked — needed by ``ChildEpicsCompleteGate``
(T3) to treat Jira's Archived status as terminal for child Epics.
"""

from __future__ import annotations

TERMINAL_TOKENS: tuple[str, ...] = (
    "done",
    "complete",
    "completed",
    "closed",
    "cancelled",
    "canceled",
    "archived",
)


def is_terminal_status(status: str) -> bool:
    """Treat done/complete/closed/cancelled/archived statuses as terminal.

    Substring match against ``TERMINAL_TOKENS``, case-insensitive — same
    semantics as the original ``epic_story_iteration._is_story_terminal``.
    """
    raw = status.strip().lower()
    return any(token in raw for token in TERMINAL_TOKENS)
