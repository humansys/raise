"""Shared terminal-status helper (S14559.1 T1, RAISE-14588; RAISE-16985).

Extracted from ``epic_story_iteration._is_story_terminal`` so any pipeline
that needs to classify an issue's status text as "done" can reuse the same
classifier instead of cloning it (design AG2 mitigation, and RAISE-16985
design §2 D-A: this is the single implementation — ``backlog/merge_gate.py``
no longer carries a second one).

Two paths, in this order:

1. **Category (primary).** ``status_category`` is Jira's (or an adapter's)
   language-independent classification — ``new``, ``indeterminate``, or
   ``done``. When a caller passes a *present, non-empty* category, it
   decides outright: ``done`` is terminal, anything else is not. A missing
   or blank category (``None``, ``""``, whitespace-only) falls through to
   the token path instead of being read as "not terminal" — the
   RAISE-16941 empty-category defect this story exists to fix.
2. **Whole-token (degradation).** Used only when no category is available.
   Matches whole tokens (``[a-z0-9]+`` runs, casefolded) against
   ``TERMINAL_TOKENS``. This path is unsound in *both* directions: it
   misses non-English terminal names such as ``TERMINADO`` (no English
   token appears), and — before this story tightened substring matching to
   whole-token matching — it falsely matched ``Abandoned``/``undone``/
   ``redone`` (each contains the substring ``done``). One known accepted
   residual remains on the token path: ``"Not Done"`` reads as terminal
   because ``done`` is a token in it and there is no negation guard. This
   is deliberate (RAISE-16985 design §2 D-B / S4) — the string does not
   occur in the measured 1793-row status corpus, and adding a negation
   guard would flip 5 genuinely-Done rows to non-terminal.

No I/O, no imports beyond ``re`` — this module must stay importable from
anywhere (fleet, gates, backlog) without cycle risk.
"""

from __future__ import annotations

import re

TERMINAL_CATEGORY = "done"

_TOKEN_RE = re.compile(r"[a-z0-9]+")

TERMINAL_TOKENS: frozenset[str] = frozenset(
    {"done", "complete", "completed", "closed", "cancelled", "canceled", "archived"}
)


def is_terminal_status(status: str, *, status_category: str | None = None) -> bool:
    """Classify ``status`` as terminal — category primary, tokens fallback.

    Args:
        status: Display name or slug (used for logging and for the token
            fallback only).
        status_category: Jira (or adapter) status category — ``new``,
            ``indeterminate``, ``done``, or empty/``None`` when unresolved.
            A present, non-empty category always wins over any token match
            in ``status`` (see module docstring).

    Returns:
        True when ``status_category`` (normalised) equals ``"done"``, or —
        when no category is available — when ``status`` contains a whole
        token from ``TERMINAL_TOKENS``.
    """
    category = (status_category or "").strip().casefold()
    if category:  # a PRESENT category decides — RAISE-16941
        return category == TERMINAL_CATEGORY
    return _has_terminal_token(status)  # degradation: no category available


def _has_terminal_token(status: str) -> bool:
    """Whole-token match, casefolded, ASCII-alphanumeric tokens only."""
    return any(tok in TERMINAL_TOKENS for tok in _TOKEN_RE.findall(status.casefold()))
