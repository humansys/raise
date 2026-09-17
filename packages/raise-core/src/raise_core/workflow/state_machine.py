"""Workflow state machine — pure domain model, no I/O.

Story: S2 (RAISE-15029) — State Machine Builder
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateSpec:
    """Immutable specification for a single workflow state."""

    slug: str
    """Normalized slug (lowercase, hyphenated)."""

    name: str
    """Display name as-is from config or adapter."""

    native_id: str | None = None
    """Jira transition ID or adapter-specific ID."""

    status_category: str | None = None
    """Workflow category: "new", "indeterminate", "done", or None."""


@dataclass
class WorkflowStateMachine:
    """Immutable directed graph of legal backlog transitions.

    states:            slug → StateSpec  (all known states)
    transitions:       from_slug → frozenset[to_slug]  (declared legal moves)
    unmanaged_states:  slugs not governed by the pipeline (advisory only)
    """

    states: dict[str, StateSpec]
    transitions: dict[str, frozenset[str]]
    unmanaged_states: frozenset[str]

    def resolve(self, raw_status: str) -> str | None:
        """Case-insensitive slug resolution.

        Tries:
        1. Exact slug match (after lowercase + space-to-hyphen normalization).
        2. Case-insensitive display name match.

        Returns None if not found.
        """
        if not raw_status:
            return None

        normalized = raw_status.lower().replace(" ", "-")
        if normalized in self.states:
            return normalized

        # Try matching by display name
        lower_raw = raw_status.lower()
        for slug, spec in self.states.items():
            if spec.name.lower() == lower_raw:
                return slug

        return None

    def is_legal(self, from_slug: str, to_slug: str) -> bool:
        """Return True if the transition from_slug → to_slug is declared legal."""
        allowed = self.transitions.get(from_slug, frozenset())
        return to_slug in allowed

    def suggest_candidates(self, raw_status: str) -> list[str]:
        """Return slugs whose slug or display name partially matches *raw_status*.

        Used by the edge wizard to produce a structured diagnostic when
        ``resolve()`` returns None — i.e. the exact target is not in the machine
        but the operator may have made a typo or used a partial name.

        Empty input or empty machine always returns [].
        Matching is case-insensitive; both slug substring and display-name
        substring are checked.
        """
        if not raw_status or not self.states:
            return []

        needle = raw_status.lower().replace(" ", "-")
        needle_display = raw_status.lower()
        candidates = []
        for slug, spec in self.states.items():
            slug_match = needle in slug or slug in needle
            name_match = (
                needle_display in spec.name.lower()
                or spec.name.lower() in needle_display
            )
            if slug_match or name_match:
                candidates.append(slug)
        return candidates
