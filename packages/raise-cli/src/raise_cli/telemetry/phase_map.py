"""Canonical pipeline-phase → normalized-phase mapping for WorkLifecycle telemetry.

Skills pass their natural pipeline phase (e.g. "triage" for bugfix).
normalize_phase() converts it to the canonical normalized phase ("design")
before it is stored in a WorkLifecycle event.

Unknown work types or unknown phases pass through unchanged.
"""

from __future__ import annotations

PHASE_MAP: dict[str, dict[str, str]] = {
    "story": {
        "start": "init",
        "design": "design",
        "plan": "plan",
        "implement": "implement",
        # RAISE-8347: review phases keep their identity — review telemetry
        # must be distinguishable from implement for flow/cost analysis.
        "architecture-review": "architecture-review",
        "quality-review": "quality-review",
        "review": "review",
        "close": "close",
    },
    "bugfix": {
        "start": "init",
        "triage": "design",
        "analyse": "design",
        "plan": "plan",
        "architecture-review": "plan",
        "fix": "implement",
        "quality-review": "implement",
        "review": "review",
        "pir": "review",
        "close": "close",
    },
    "epic": {
        "start": "init",
        "design": "design",
        "plan": "plan",
        "story-iteration": "implement",
        "docs": "implement",
        "journal": "review",
        "close": "close",
    },
}


def normalize_phase(work_type: str, raw_phase: str) -> str:
    """Return the normalized phase for a given work type and raw pipeline phase.

    Falls back to raw_phase when work_type is unknown or raw_phase has no mapping.
    """
    return PHASE_MAP.get(work_type, {}).get(raw_phase, raw_phase)
