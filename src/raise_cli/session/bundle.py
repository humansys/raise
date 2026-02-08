"""Context bundle assembly for session start.

Assembles a token-optimized context bundle (~150 tokens) from multiple sources:
1. ~/.rai/developer.yaml → developer model + coaching + deadlines
2. .raise/rai/session-state.yaml → current work state
3. Memory graph → foundational patterns (metadata query)
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode
from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import SessionState

logger = logging.getLogger(__name__)

# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"


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


def _format_developer_section(profile: DeveloperProfile) -> str:
    """Format the developer identity line."""
    return f"Developer: {profile.name} ({profile.experience_level.value})"


def _format_work_section(state: SessionState | None) -> str:
    """Format current work state."""
    if state is None:
        return "Work: (no previous session state)"

    lines = [
        f"Story: {state.current_work.story} [{state.current_work.phase}]",
        f"Epic: {state.current_work.epic}",
        f"Branch: {state.current_work.branch}",
    ]
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
    if not coaching.strengths and not coaching.corrections and not coaching.growth_edge:
        return ""

    lines = ["# Coaching"]
    if coaching.strengths:
        lines.append(f"Strengths: {', '.join(coaching.strengths)}")
    if coaching.growth_edge:
        lines.append(f"Growth edge: {coaching.growth_edge}")
    if coaching.corrections:
        lines.append("Recent corrections:")
        for c in coaching.corrections[-3:]:  # Last 3 for brevity
            lines.append(f"- {c.session}: {c.what} → {c.lesson}")
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
        Plain text context bundle, ~150 tokens.
    """
    patterns = get_foundational_patterns(project_path)

    sections = [
        "# Session Context",
        _format_developer_section(profile),
        _format_work_section(state),
        _format_last_session(state),
    ]

    deadlines = _format_deadlines(profile)
    if deadlines:
        sections.append(deadlines)

    primes = _format_primes(patterns)
    if primes:
        sections.append(primes)

    coaching = _format_coaching(profile)
    if coaching:
        sections.append(coaching)

    pending = _format_pending(state)
    if pending:
        sections.append(pending)

    # Filter empty sections, join with blank lines
    return "\n\n".join(s for s in sections if s)
