"""Context bundle assembly for session start.

Assembles a token-optimized context bundle (~600 tokens) from multiple sources:
1. ~/.rai/developer.yaml → developer model + coaching + deadlines
2. .raise/rai/session-state.yaml → current work state
3. Memory graph → foundational patterns, governance primes
4. .raise/rai/personal/sessions/index.jsonl → recent sessions

Note: Identity primes (RAI-VAL-*, RAI-BND-*) are no longer emitted here.
They live in CLAUDE.md as always-on content (ADR-012).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import CurrentWork, SessionState
from raise_core.graph.models import GraphNode

from .bundle_data import (
    SectionManifest,
    fetch_live_status,
    find_release_for_current_epic,
    get_always_on_primes,
    get_foundational_patterns,
)
from .bundle_formatters import (
    format_coaching,
    format_deadlines,
    format_developer_section,
    format_governance_primes,
    format_last_session,
    format_manifest,
    format_narrative,
    format_next_session_prompt,
    format_pending,
    format_primes,
    format_progress,
    format_recent_sessions,
    format_work_section,
)

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Section registry and manifest
# ---------------------------------------------------------------------------

# Average tokens per item, estimated from real data
_TOKENS_PER_ITEM: dict[str, int] = {
    "governance": 25,
    "behavioral": 20,
    "coaching": 80,
    "deadlines": 30,
    "progress": 40,
}


def derive_current_work(project_path: Path) -> CurrentWork | None:
    """Try to derive current work from git. Returns None on failure.

    Uses GitStateDeriver (ADR-038) to read branch, epic, story, and phase
    from git state. Falls back gracefully — never raises.
    """
    try:
        from raise_cli.session.derive import GitStateDeriver

        return GitStateDeriver().current_work(project_path)
    except Exception:
        _logger.debug("Git state derivation failed — using YAML fallback", exc_info=True)
        return None


def _count_governance(project_path: Path) -> int:
    """Count governance items (always_on nodes minus identity)."""
    nodes = get_always_on_primes(project_path)
    return len(
        [
            n
            for n in nodes
            if not n.id.startswith("RAI-VAL-") and not n.id.startswith("RAI-BND-")
        ]
    )


def _count_behavioral(project_path: Path) -> int:
    """Count foundational pattern items."""
    return len(get_foundational_patterns(project_path))


def _count_coaching(profile: DeveloperProfile) -> int:
    """Count coaching items (1 if content exists, 0 otherwise)."""
    coaching = profile.coaching
    has_content = (
        coaching.strengths
        or coaching.growth_edge
        or coaching.trust_level != "new"
        or coaching.autonomy
        or coaching.relationship.quality != "new"
    )
    return 1 if has_content else 0


def _count_deadlines(profile: DeveloperProfile) -> int:
    """Count deadline items."""
    return len(profile.deadlines)


def _count_progress(state: SessionState | None) -> int:
    """Count progress items (1 if exists, 0 otherwise)."""
    if state is None or state.progress is None:
        return 0
    return 1


# Registry: section name → format function
# Format functions have heterogeneous signatures; the registry maps names
# for validation and dispatch. Actual calling happens in assemble_sections().
SECTION_REGISTRY: dict[str, Callable[..., str]] = {
    "governance": format_governance_primes,
    "behavioral": format_primes,
    "coaching": format_coaching,
    "deadlines": format_deadlines,
    "progress": format_progress,
}


def count_section_items(
    section: str,
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
) -> int:
    """Count items in a named section.

    Args:
        section: Section name from SECTION_REGISTRY.
        project_path: Absolute path to the project root.
        profile: Developer profile.
        state: Session state (may be None).

    Returns:
        Number of items in the section.

    Raises:
        ValueError: If section name is not in SECTION_REGISTRY.
    """
    if section not in SECTION_REGISTRY:
        raise ValueError(
            f"Unknown section: '{section}'. Valid: {sorted(SECTION_REGISTRY.keys())}"
        )

    if section == "governance":
        return _count_governance(project_path)
    if section == "behavioral":
        return _count_behavioral(project_path)
    if section == "coaching":
        return _count_coaching(profile)
    if section == "deadlines":
        return _count_deadlines(profile)
    if section == "progress":
        return _count_progress(state)

    return 0  # unreachable but satisfies pyright


def _format_section(
    name: str,
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
) -> str:
    """Format a single section by name. Assumes name is valid."""
    if name == "governance":
        return format_governance_primes(get_always_on_primes(project_path))
    if name == "behavioral":
        return format_primes(get_foundational_patterns(project_path))
    if name == "coaching":
        return format_coaching(profile)
    if name == "deadlines":
        return format_deadlines(profile)
    if name == "progress":
        return format_progress(state)
    return ""


def assemble_sections(
    sections: list[str],
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
) -> str:
    """Assemble formatted output for selected priming sections.

    Each section independently loads its data source (graph, profile, or state)
    and formats the output. Section names are validated against SECTION_REGISTRY.

    Args:
        sections: List of section names to load (e.g., ["governance", "behavioral"]).
        project_path: Absolute path to the project root.
        profile: Developer profile.
        state: Session state (may be None).

    Returns:
        Formatted sections joined by blank lines, or empty string if no content.

    Raises:
        ValueError: If any section name is not in SECTION_REGISTRY.
    """
    if not sections:
        return ""

    for name in sections:
        if name not in SECTION_REGISTRY:
            raise ValueError(
                f"Unknown section: '{name}'. Valid: {sorted(SECTION_REGISTRY.keys())}"
            )

    parts = [
        part
        for name in sections
        if (part := _format_section(name, project_path, profile, state))
    ]
    return "\n\n".join(parts)


def assemble_orientation(
    profile: DeveloperProfile,
    state: SessionState | None,
    project_path: Path,
    session_id: str | None = None,
) -> str:
    """Assemble orientation-only context (always-on sections).

    Orientation = "where are we?" — work state, continuity, pending.
    Does NOT include priming sections (governance, behavioral, coaching,
    deadlines, progress). Those are loaded separately via assemble_sections().

    Args:
        profile: Developer profile from ~/.rai/developer.yaml.
        state: Session state from .raise/rai/session-state.yaml (may be None).
        project_path: Absolute path to the project root.
        session_id: Optional session identifier (e.g., "SES-177").

    Returns:
        Plain text orientation context.
    """
    # Derive current work from git (ADR-038); fallback to YAML state
    try:
        derived_work = derive_current_work(project_path)
    except Exception:
        _logger.debug("derive_current_work raised — using YAML fallback", exc_info=True)
        derived_work = None

    # Resolve release context for current epic
    epic_id = (
        (derived_work.epic if derived_work else None)
        or (state.current_work.epic if state else None)
        or ""
    )
    release_node: GraphNode | None = None
    if epic_id:
        release_node = find_release_for_current_epic(project_path, epic_id)

    # Session Context header
    parts: list[str] = [
        "# Session Context",
        format_developer_section(profile),
    ]

    # Add session ID with name if available
    if session_id:
        from raise_cli.session.index import read_active_session

        active_pointer = read_active_session(project_root=project_path)
        if active_pointer is not None and active_pointer.name:
            parts.append(f"Session: {session_id} — {active_pointer.name}")
        else:
            parts.append(f"Session: {session_id}")

    # Fetch live backlog status (never blocks — degrades gracefully)
    live = fetch_live_status(state)

    parts.append(
        format_work_section(
            state, release_node=release_node, live=live, current_work=derived_work
        )
    )

    # Last session + recent sessions
    parts.append(format_last_session(state))
    dev_prefix = profile.get_pattern_prefix()
    recent = format_recent_sessions(project_path, developer_prefix=dev_prefix)
    if recent:
        parts.append(recent)

    # Session narrative (cross-session continuity — not truncated)
    narrative = format_narrative(state)
    if narrative:
        parts.append(narrative)

    # Next session prompt (forward-looking guidance from Rai to future self)
    next_prompt = format_next_session_prompt(state)
    if next_prompt:
        parts.append(next_prompt)

    # Pending
    pending = format_pending(state)
    if pending:
        parts.append(pending)

    # Filter empty sections, join with blank lines
    return "\n\n".join(s for s in parts if s)


def assemble_context_bundle(
    profile: DeveloperProfile,
    state: SessionState | None,
    project_path: Path,
    session_id: str | None = None,
) -> str:
    """Assemble lean context bundle: orientation + manifest.

    Emits always-on orientation sections plus a manifest of available
    priming sections (with counts and token estimates). Priming sections
    are loaded separately via `rai session context --sections`.

    Args:
        profile: Developer profile from ~/.rai/developer.yaml.
        state: Session state from .raise/rai/session-state.yaml (may be None).
        project_path: Absolute path to the project root.
        session_id: Optional session identifier (e.g., "SES-177").

    Returns:
        Plain text context bundle: orientation + manifest.
    """
    # Orientation (always-on sections)
    orientation = assemble_orientation(profile, state, project_path, session_id)

    # Build manifest for available priming sections
    manifests: list[SectionManifest] = []
    for section_name in SECTION_REGISTRY:
        count = count_section_items(section_name, project_path, profile, state)
        tokens = count * _TOKENS_PER_ITEM.get(section_name, 20)
        manifests.append(
            SectionManifest(
                name=section_name,
                count=count,
                token_estimate=tokens,
            )
        )

    manifest = format_manifest(manifests)

    parts = [orientation]
    if manifest:
        parts.append(manifest)

    return "\n\n".join(parts)
