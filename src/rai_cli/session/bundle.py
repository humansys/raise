"""Context bundle assembly for session start.

Assembles a token-optimized context bundle (~600 tokens) from multiple sources:
1. ~/.rai/developer.yaml → developer model + coaching + deadlines
2. .raise/rai/session-state.yaml → current work state
3. Memory graph → foundational patterns, governance primes, identity primes
4. .raise/rai/personal/sessions/index.jsonl → recent sessions
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import ConceptNode
from rai_cli.onboarding.profile import DeveloperProfile
from rai_cli.schemas.session_state import SessionState

logger = logging.getLogger(__name__)

# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"
# Sessions index path relative to project root (personal = developer-specific)
SESSIONS_INDEX_REL_PATH = (
    Path(".raise") / "rai" / "personal" / "sessions" / "index.jsonl"
)


def get_foundational_patterns(project_path: Path) -> list[ConceptNode]:
    """Query memory graph for foundational patterns.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of pattern ConceptNodes with foundational=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = UnifiedGraph.load(graph_path)
    except Exception:
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node
        for node in graph.iter_concepts()
        if node.type == "pattern" and node.metadata.get("foundational") is True
    ]


def get_always_on_primes(project_path: Path) -> list[ConceptNode]:
    """Query memory graph for all always_on nodes (governance + identity).

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of ConceptNodes with always_on=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = UnifiedGraph.load(graph_path)
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
) -> ConceptNode | None:
    """Find release node for the current epic from the memory graph.

    Args:
        project_path: Absolute path to the project root.
        epic_id: Epic identifier (e.g., "E19").

    Returns:
        The release ConceptNode, or None if not found or graph unavailable.
    """
    if not epic_id:
        return None

    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        return None

    try:
        from rai_cli.context.query import UnifiedQueryEngine

        engine = UnifiedQueryEngine.from_file(graph_path)
        return engine.find_release_for(f"epic-{epic_id.lower()}")
    except Exception:
        logger.debug("Failed to query release for epic %s", epic_id)
        return None


def _format_work_section(
    state: SessionState | None,
    release_node: ConceptNode | None = None,
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


def _format_governance_primes(always_on_nodes: list[ConceptNode]) -> str:
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


def _format_identity_primes(always_on_nodes: list[ConceptNode]) -> str:
    """Format identity primes (RAI-VAL-* values + RAI-BND-* boundaries).

    Args:
        always_on_nodes: All always_on nodes from the graph.

    Returns:
        Formatted identity primes section, or empty string if none.
    """
    identity = [
        n
        for n in always_on_nodes
        if n.id.startswith("RAI-VAL-") or n.id.startswith("RAI-BND-")
    ]
    if not identity:
        return ""

    lines = ["# Identity Primes"]
    for n in identity:
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
        text = index_path.read_text().strip()
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


def _format_primes(patterns: list[ConceptNode]) -> str:
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


def assemble_context_bundle(
    profile: DeveloperProfile,
    state: SessionState | None,
    project_path: Path,
) -> str:
    """Assemble token-optimized context bundle from multiple sources.

    Args:
        profile: Developer profile from ~/.rai/developer.yaml.
        state: Session state from .raise/rai/session-state.yaml (may be None).
        project_path: Absolute path to the project root.

    Returns:
        Plain text context bundle, ~600 tokens.
    """
    patterns = get_foundational_patterns(project_path)
    always_on = get_always_on_primes(project_path)

    # Resolve release context for current epic
    release_node: ConceptNode | None = None
    if state and state.current_work.epic:
        release_node = _find_release_for_current_epic(
            project_path, state.current_work.epic
        )

    # Session Context header
    sections = [
        "# Session Context",
        _format_developer_section(profile),
        _format_work_section(state, release_node=release_node),
    ]

    # Progress (epic SP, completed epics)
    progress = _format_progress(state)
    if progress:
        sections.append(progress)

    # Last session + recent sessions
    sections.append(_format_last_session(state))
    recent = _format_recent_sessions(project_path)
    if recent:
        sections.append(recent)

    # Session narrative (cross-session continuity — not truncated)
    narrative = _format_narrative(state)
    if narrative:
        sections.append(narrative)

    # Deadlines
    deadlines = _format_deadlines(profile)
    if deadlines:
        sections.append(deadlines)

    # Governance primes (guardrails + principles, not identity)
    gov_primes = _format_governance_primes(always_on)
    if gov_primes:
        sections.append(gov_primes)

    # Identity primes (RAI-VAL-*, RAI-BND-*)
    id_primes = _format_identity_primes(always_on)
    if id_primes:
        sections.append(id_primes)

    # Behavioral primes (foundational patterns)
    primes = _format_primes(patterns)
    if primes:
        sections.append(primes)

    # Coaching
    coaching = _format_coaching(profile)
    if coaching:
        sections.append(coaching)

    # Pending
    pending = _format_pending(state)
    if pending:
        sections.append(pending)

    # Filter empty sections, join with blank lines
    return "\n\n".join(s for s in sections if s)
