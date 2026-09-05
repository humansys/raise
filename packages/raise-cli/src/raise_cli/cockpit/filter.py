"""Filtering and sorting utilities for the cockpit worktree list (E14777)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from raise_cli.storage.worktrees import Worktree

T = TypeVar("T")


def fuzzy_filter(items: list[T], query: str, *, key: Callable[[T], str]) -> list[T]:
    """Return items matching query using prefix-then-subsequence strategy.

    Args:
        items: The items to filter.
        query: The search string. Empty string returns all items.
        key: Function to extract the string to match against.

    Returns:
        Filtered list, prefix matches first, then subsequence matches.
    """
    if not query:
        return list(items)

    q = query.lower()

    prefix: list[T] = []
    subseq: list[T] = []

    for item in items:
        text = key(item).lower()
        if text.startswith(q):
            prefix.append(item)
        elif _is_subsequence(q, text):
            subseq.append(item)

    return prefix + subseq


def _is_subsequence(needle: str, haystack: str) -> bool:
    """Return True if every character of needle appears in haystack in order."""
    it = iter(haystack)
    return all(ch in it for ch in needle)


def filter_open_worktrees(worktrees: list[Worktree]) -> list[Worktree]:
    """Return only open worktrees, sorted by recency (last_session_id desc).

    Worktrees with a last_session_id sort before those without.
    Within each group, order is preserved from the input (typically creation
    order desc from SqliteWorktreeStore.list_worktrees).

    Args:
        worktrees: Raw list from SqliteWorktreeStore.

    Returns:
        Open worktrees sorted most-recently-used first.
    """
    open_wts = [w for w in worktrees if w.status == "open"]
    # Sort: worktrees with a session_id first (truthy), then without (None)
    # Within the "has session" group, sort by session_id desc (lexicographic;
    # session IDs are UUIDs with time-prefix ordering)
    return sorted(
        open_wts,
        key=lambda w: (w.last_session_id is None, w.last_session_id or ""),
        reverse=False,
    )
