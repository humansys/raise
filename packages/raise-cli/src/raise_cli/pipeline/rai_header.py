"""Structured [RAI:] header for pipeline subagent prompt signaling.

Enables deterministic classification of JSONL transcripts by injecting
a machine-readable header in the first user message of pipeline agents.
"""

from __future__ import annotations

import re

RAI_HEADER_RE = re.compile(
    r"\[RAI:"
    r"type=(?P<type>[^,\]]+),"
    r"skill=(?P<skill>[^,\]]+),"
    r"phase=(?P<phase>[^,\]]+),"
    r"run_id=(?P<run_id>[^,\]]+),"
    r"parent_session=(?P<parent_session>[^,\]]+)"
    r"\]"
)


def build_rai_header(
    *,
    type: str | None,
    skill: str | None,
    phase: str | None,
    run_id: str | None,
    parent_session: str | None,
) -> str | None:
    """Build a ``[RAI:...]`` header string.

    Returns ``None`` if any required field is missing — callers should
    omit the header entirely rather than emit a partial one.
    """
    if any(v is None for v in (type, skill, phase, run_id, parent_session)):
        return None
    return (
        f"[RAI:type={type},skill={skill},phase={phase},"
        f"run_id={run_id},parent_session={parent_session}]"
    )


def parse_rai_header(text: str) -> dict[str, str] | None:
    """Extract ``[RAI:...]`` fields from *text*.

    Returns a dict with keys ``type``, ``skill``, ``phase``, ``run_id``,
    ``parent_session`` on match, or ``None`` if no valid header found.
    """
    m = RAI_HEADER_RE.search(text)
    return m.groupdict() if m else None
