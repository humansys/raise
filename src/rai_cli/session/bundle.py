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

import json
import logging
from collections.abc import Callable
from datetime import date
from pathlib import Path

from pydantic import BaseModel

from rai_cli.graph.backends import get_active_backend
from rai_cli.onboarding.profile import DeveloperProfile
from rai_cli.schemas.session_state import SessionState
from rai_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"
# Sessions index path relative to project root (personal = developer-specific)
SESSIONS_INDEX_REL_PATH = (
    Path(".raise") / "rai" / "personal" / "sessions" / "index.jsonl"
)


def get_foundational_patterns(project_path: Path) -> list[GraphNode]:
    """Query memory graph for foundational patterns.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of pattern GraphNodes with foundational=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = get_active_backend(graph_path).load()
    except Exception:
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node
        for node in graph.iter_concepts()
        if node.type == "pattern" and node.metadata.get("foundational") is True
    ]


def get_always_on_primes(project_path: Path) -> list[GraphNode]:
    """Query memory graph for all always_on nodes (governance + identity).

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of GraphNodes with always_on=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = get_active_backend(graph_path).load()
    except Exception:
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node for node in graph.iter_concepts() if node.metadata.get("always_on") is True
    ]


def _format_developer_section(profile: DeveloperProfile) -> str:
    """Format developer identity line with non-default communication prefs."""
    line = f"Developer: {profile.name} ({profile.experience_level.value})"

    # Surface communication preferences that deviate from defaults
    comm = profile.communication
    prefs: list[str] = []
    if comm.language != "en":
        prefs.append(f"language: {comm.language}")
    if comm.style.value != "balanced":
        prefs.append(f"style: {comm.style.value}")
    if comm.skip_praise:
        prefs.append("skip_praise")
    if comm.redirect_when_dispersing:
        prefs.append("redirect_when_dispersing")

    if prefs:
        line += f"\nCommunication: {', '.join(prefs)}"

    return line


def _find_release_for_current_epic(
    project_path: Path, epic_id: str
) -> GraphNode | None:
    """Find release node for the current epic from the memory graph.

    Args:
        project_path: Absolute path to the project root.
        epic_id: Epic identifier (e.g., "E19").

    Returns:
        The release GraphNode, or None if not found or graph unavailable.
    """
    if not epic_id:
        return None

    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        return None

    try:
        from rai_cli.graph.backends import get_active_backend
        from rai_core.graph.query import QueryEngine

        graph = get_active_backend(graph_path).load()
        engine = QueryEngine(graph)
        return engine.find_release_for(f"epic-{epic_id.lower()}")
    except Exception:
        logger.debug("Failed to query release for epic %s", epic_id)
        return None


def _format_work_section(
    state: SessionState | None,
    release_node: GraphNode | None = None,
) -> str:
    """Format current work state."""
    if state is None:
        return "Work: (no previous session state)"

    lines: list[str] = []

    if release_node:
        release_id = release_node.metadata.get("release_id", release_node.id)
        name = release_node.metadata.get("name", "")
        target = release_node.metadata.get("target", "")
        release_parts = [f"Release: {release_id}"]
        if name:
            release_parts.append(f"({name})")
        if target:
            release_parts.append(f"— Target: {target}")
        lines.append(" ".join(release_parts))

    lines.extend([
        f"Story: {state.current_work.story} [{state.current_work.phase}]",
        f"Epic: {state.current_work.epic}",
        f"Branch: {state.current_work.branch}",
    ])
    return "\n".join(lines)


def _format_last_session(state: SessionState | None) -> str:
    """Format last session summary."""
    if state is None:
        return ""
    s = state.last_session
    return f"Last: {s.id} ({s.date}, {s.developer}) — {s.summary}"


def _format_deadlines(profile: DeveloperProfile) -> str:
    """Format deadlines with days remaining."""
    if not profile.deadlines:
        return ""

    today = date.today()
    lines = ["# Deadlines"]
    for d in profile.deadlines:
        days = (d.date - today).days
        if days < 0:
            suffix = f"({abs(days)}d overdue)"
        elif days == 0:
            suffix = "(today)"
        elif days == 1:
            suffix = "(1 day)"
        else:
            suffix = f"({days} days)"
        line = f"{d.name}: {d.date.strftime('%b %d')} {suffix}"
        if d.notes:
            line += f" — {d.notes}"
        lines.append(line)
    return "\n".join(lines)


def _format_governance_primes(always_on_nodes: list[GraphNode]) -> str:
    """Format governance primes (guardrails + non-identity principles).

    Args:
        always_on_nodes: All always_on nodes from the graph.

    Returns:
        Formatted governance primes section, or empty string if none.
    """
    governance = [
        n
        for n in always_on_nodes
        if not n.id.startswith("RAI-VAL-") and not n.id.startswith("RAI-BND-")
    ]
    if not governance:
        return ""

    lines = ["# Governance Primes"]
    for n in governance:
        content = n.content
        if len(content) > 80:
            content = content[:77] + "..."
        lines.append(f"- {n.id}: {content}")
    return "\n".join(lines)



def _format_progress(state: SessionState | None) -> str:
    """Format epic progress section.

    Args:
        state: Session state (may be None).

    Returns:
        Formatted progress section, or empty string if no progress.
    """
    if state is None or state.progress is None:
        return ""

    p = state.progress
    pct = round(p.sp_done / p.sp_total * 100) if p.sp_total > 0 else 0
    lines = [
        f"Progress: {p.epic} — {p.stories_done}/{p.stories_total} stories, {p.sp_done}/{p.sp_total} SP ({pct}%)"
    ]

    if state.completed_epics:
        lines.append(f"Completed: {', '.join(state.completed_epics)}")

    return "\n".join(lines)


def _format_recent_sessions(project_path: Path, limit: int = 3) -> str:
    """Format recent sessions from sessions/index.jsonl.

    Args:
        project_path: Absolute path to the project root.
        limit: Number of recent sessions to include.

    Returns:
        Formatted recent sessions section, or empty string if none.
    """
    index_path = project_path / SESSIONS_INDEX_REL_PATH
    if not index_path.exists():
        return ""

    try:
        text = index_path.read_text(encoding="utf-8").strip()
        if not text:
            return ""
        sessions = [json.loads(line) for line in text.splitlines() if line.strip()]
    except Exception:
        logger.warning("Failed to read sessions index: %s", index_path)
        return ""

    if not sessions:
        return ""

    recent = sessions[-limit:]
    recent.reverse()  # Most recent first

    lines = ["Recent:"]
    for s in recent:
        topic = s.get("topic", "")
        if len(topic) > 80:
            topic = topic[:77] + "..."
        lines.append(f"- {s['id']}: {topic}")
    return "\n".join(lines)


def _format_narrative(state: SessionState | None) -> str:
    """Format session narrative for cross-session continuity.

    Narrative is loaded verbatim — no truncation. It contains structured
    context (decisions, research, artifacts, branch state) that makes the
    next session immediately resumable.

    Args:
        state: Session state (may be None).

    Returns:
        Formatted narrative section, or empty string if no narrative.
    """
    if state is None or not state.narrative:
        return ""

    return f"# Session Narrative\n{state.narrative}"


def _format_next_session_prompt(state: SessionState | None) -> str:
    """Format next session prompt for cross-session continuity.

    This is forward-looking guidance from Rai to her future self,
    written during session-close and presented at session-start.

    Args:
        state: Session state (may be None).

    Returns:
        Formatted prompt section, or empty string if no prompt.
    """
    if state is None or not state.next_session_prompt:
        return ""

    return f"# Next Session Prompt\n{state.next_session_prompt}"


def _format_primes(patterns: list[GraphNode]) -> str:
    """Format foundational patterns as behavioral primes."""
    if not patterns:
        return ""

    lines = ["# Behavioral Primes"]
    for p in patterns:
        # Compact: PAT-ID: first sentence
        content = p.content.split("—")[0].strip() if "—" in p.content else p.content
        # Truncate long content
        if len(content) > 80:
            content = content[:77] + "..."
        lines.append(f"- {p.id}: {content}")
    return "\n".join(lines)


def _format_coaching(profile: DeveloperProfile) -> str:
    """Format coaching context."""
    coaching = profile.coaching
    has_content = (
        coaching.strengths
        or coaching.growth_edge
        or coaching.trust_level != "new"
        or coaching.autonomy
        or coaching.relationship.quality != "new"
    )
    if not has_content:
        return ""

    lines = ["# Coaching"]
    if coaching.trust_level != "new":
        lines.append(f"Trust: {coaching.trust_level}")
    if coaching.strengths:
        lines.append(f"Strengths: {', '.join(coaching.strengths)}")
    if coaching.growth_edge:
        lines.append(f"Growth edge: {coaching.growth_edge}")
    if coaching.autonomy:
        lines.append(f"Autonomy: {coaching.autonomy}")
    if coaching.relationship.quality != "new":
        rel = coaching.relationship
        lines.append(f"Relationship: {rel.quality} ({rel.trajectory})")
    # Corrections suppressed from session context — noise without specific
    # consumption point. Revisit when /rai-story-review integrates them.
    return "\n".join(lines)


def _format_pending(state: SessionState | None) -> str:
    """Format pending items."""
    if state is None:
        return ""

    pending = state.pending
    if not pending.decisions and not pending.blockers and not pending.next_actions:
        return ""

    lines = ["# Pending"]
    if pending.decisions:
        lines.append("Decisions:")
        for d in pending.decisions:
            lines.append(f"- {d}")
    if pending.blockers:
        lines.append("Blockers:")
        for b in pending.blockers:
            lines.append(f"- {b}")
    if pending.next_actions:
        lines.append("Next:")
        for n in pending.next_actions:
            lines.append(f"- {n}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section registry and manifest
# ---------------------------------------------------------------------------


class SectionManifest(BaseModel):
    """Manifest entry for a queryable context section."""

    name: str
    count: int
    token_estimate: int


def _count_governance(project_path: Path) -> int:
    """Count governance items (always_on nodes minus identity)."""
    nodes = get_always_on_primes(project_path)
    return len([
        n for n in nodes
        if not n.id.startswith("RAI-VAL-") and not n.id.startswith("RAI-BND-")
    ])


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


# Average tokens per item, estimated from real data
_TOKENS_PER_ITEM: dict[str, int] = {
    "governance": 25,
    "behavioral": 20,
    "coaching": 80,
    "deadlines": 30,
    "progress": 40,
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
        raise ValueError(f"Unknown section: '{section}'. Valid: {sorted(SECTION_REGISTRY.keys())}")

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


# Registry: section name → format function
# Format functions have heterogeneous signatures; the registry maps names
# for validation and dispatch. Actual calling happens in assemble_sections().
SECTION_REGISTRY: dict[str, Callable[..., str]] = {
    "governance": _format_governance_primes,
    "behavioral": _format_primes,
    "coaching": _format_coaching,
    "deadlines": _format_deadlines,
    "progress": _format_progress,
}


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

    # Validate all section names first
    for name in sections:
        if name not in SECTION_REGISTRY:
            raise ValueError(
                f"Unknown section: '{name}'. "
                f"Valid: {sorted(SECTION_REGISTRY.keys())}"
            )

    parts: list[str] = []
    for name in sections:
        if name == "governance":
            always_on = get_always_on_primes(project_path)
            part = _format_governance_primes(always_on)
        elif name == "behavioral":
            patterns = get_foundational_patterns(project_path)
            part = _format_primes(patterns)
        elif name == "coaching":
            part = _format_coaching(profile)
        elif name == "deadlines":
            part = _format_deadlines(profile)
        elif name == "progress":
            part = _format_progress(state)
        else:
            continue  # unreachable due to validation above

        if part:
            parts.append(part)

    return "\n\n".join(parts)


def _format_manifest(manifests: list[SectionManifest]) -> str:
    """Format manifest of available context sections.

    Args:
        manifests: List of section manifest entries.

    Returns:
        Formatted manifest section, or empty string if no manifests.
    """
    if not manifests:
        return ""

    lines = ["# Available Context"]
    for m in manifests:
        if m.count == 0:
            lines.append(f"- {m.name}: 0 items")
        else:
            lines.append(f"- {m.name}: {m.count} items (~{m.token_estimate} tokens)")
    return "\n".join(lines)


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
    # Resolve release context for current epic
    release_node: GraphNode | None = None
    if state and state.current_work.epic:
        release_node = _find_release_for_current_epic(
            project_path, state.current_work.epic
        )

    # Session Context header
    sections: list[str] = [
        "# Session Context",
        _format_developer_section(profile),
    ]

    # Add session ID if provided
    if session_id:
        sections.append(f"Session: {session_id}")

    sections.append(_format_work_section(state, release_node=release_node))

    # Last session + recent sessions
    sections.append(_format_last_session(state))
    recent = _format_recent_sessions(project_path)
    if recent:
        sections.append(recent)

    # Session narrative (cross-session continuity — not truncated)
    narrative = _format_narrative(state)
    if narrative:
        sections.append(narrative)

    # Next session prompt (forward-looking guidance from Rai to future self)
    next_prompt = _format_next_session_prompt(state)
    if next_prompt:
        sections.append(next_prompt)

    # Pending
    pending = _format_pending(state)
    if pending:
        sections.append(pending)

    # Filter empty sections, join with blank lines
    return "\n\n".join(s for s in sections if s)


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
        manifests.append(SectionManifest(
            name=section_name,
            count=count,
            token_estimate=tokens,
        ))

    manifest = _format_manifest(manifests)

    parts = [orientation]
    if manifest:
        parts.append(manifest)

    return "\n\n".join(parts)
