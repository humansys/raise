"""Formatting functions for context bundle sections.

Pure formatters — no data fetching, no side effects. Each function takes
pre-loaded data and returns a formatted string.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import CurrentWork, SessionState
from raise_core.graph.models import GraphNode

from .bundle_data import SESSIONS_INDEX_REL_PATH, LiveBacklogStatus, SectionManifest

logger = logging.getLogger(__name__)


def format_developer_section(profile: DeveloperProfile) -> str:
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


def format_work_section(
    state: SessionState | None,
    release_node: GraphNode | None = None,
    live: LiveBacklogStatus | None = None,
    current_work: CurrentWork | None = None,
) -> str:
    """Format current work state with optional live backlog annotations.

    Args:
        state: Session state from YAML (may be None).
        release_node: Optional graph node for release context.
        live: Optional live backlog status annotations.
        current_work: Optional override for current_work — when provided,
            takes precedence over state.current_work. Used by git-derived
            state (S1248.3 / ADR-038).
    """
    if state is None and current_work is None:
        return "Work: (no previous session state)"

    # Resolve current_work: override > state > empty
    work = current_work or (state.current_work if state else CurrentWork())

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

    # Story line with optional live annotation
    story_line = f"Story: {work.story} [{work.phase}]"
    if live and live.story_status:
        story_line += f" — {live.story_status} (live)"
    lines.append(story_line)

    # Epic line with optional live annotation
    epic_line = f"Epic: {work.epic}"
    if live and live.epic_status:
        epic_line += f" — {live.epic_status} (live)"
    lines.append(epic_line)

    lines.append(f"Branch: {work.branch}")

    # Warning line for degraded live status
    if live and live.warning:
        lines.append(f"⚠ {live.warning}")

    return "\n".join(lines)


def format_last_session(state: SessionState | None) -> str:
    """Format last session summary."""
    if state is None:
        return ""
    s = state.last_session
    return f"Last: {s.id} ({s.date}, {s.developer}) — {s.summary}"


def format_deadlines(profile: DeveloperProfile) -> str:
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


def format_governance_primes(always_on_nodes: list[GraphNode]) -> str:
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


def format_progress(state: SessionState | None) -> str:
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


def format_recent_sessions(  # noqa: C901
    project_path: Path,
    limit: int = 3,
    developer_prefix: str | None = None,
) -> str:
    """Format recent sessions from the session index.

    Reads from personal/sessions/{prefix}/index.jsonl (new format with names).
    Falls back to personal/sessions/index.jsonl (legacy format without prefix dir).

    Args:
        project_path: Absolute path to the project root.
        limit: Number of recent sessions to include.
        developer_prefix: Developer prefix for per-developer index lookup.

    Returns:
        Formatted recent sessions section, or empty string if none.
    """
    # New format: per-developer index with names and timestamps
    if developer_prefix:
        from raise_cli.session.index import read_session_entries

        entries = read_session_entries(developer_prefix, project_root=project_path)
        if entries:
            recent = list(reversed(entries[-limit:]))
            lines = ["Recent:"]
            for entry in recent:
                name = entry.name or entry.summary or entry.id
                if len(name) > 80:
                    name = name[:77] + "..."
                duration_str = ""
                if entry.closed and entry.started:
                    mins = int((entry.closed - entry.started).total_seconds() / 60)
                    if mins >= 60:
                        duration_str = f", {mins // 60}h{mins % 60:02d}m"
                    else:
                        duration_str = f", {mins}m"
                lines.append(f"- {entry.id}: {name} ({entry.type}{duration_str})")
            return "\n".join(lines)

    # Legacy format: flat index without prefix directory
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


def format_narrative(state: SessionState | None) -> str:
    """Format session narrative for cross-session continuity.

    Narrative is loaded verbatim — no truncation. It contains structured
    context (decisions, research, artifacts, branch state) that makes the
    next session immediately resumable.

    Adds a staleness caveat so the reader knows to verify volatile
    state (git status, branch, uncommitted files) before acting on it.

    Args:
        state: Session state (may be None).

    Returns:
        Formatted narrative section, or empty string if no narrative.
    """
    if state is None or not state.narrative:
        return ""

    captured_date = state.last_session.date
    caveat = (
        f"(Captured at session close on {captured_date}. "
        "Git/branch state may be stale — verify before acting.)"
    )
    return f"# Session Narrative\n{caveat}\n{state.narrative}"


def format_next_session_prompt(state: SessionState | None) -> str:
    """Format next session prompt for cross-session continuity.

    This is forward-looking guidance from Rai to her future self,
    written during session-close and presented at session-start.

    Adds a staleness caveat so the reader knows to verify volatile
    state (git status, branch, uncommitted files) before acting on it.

    Args:
        state: Session state (may be None).

    Returns:
        Formatted prompt section, or empty string if no prompt.
    """
    if state is None or not state.next_session_prompt:
        return ""

    captured_date = state.last_session.date
    caveat = (
        f"(Captured at session close on {captured_date}. "
        "Git/branch state may be stale — verify before acting.)"
    )
    return f"# Next Session Prompt\n{caveat}\n{state.next_session_prompt}"


def format_primes(patterns: list[GraphNode]) -> str:
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


def format_coaching(profile: DeveloperProfile) -> str:
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


def format_pending(state: SessionState | None) -> str:
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


def format_manifest(manifests: list[SectionManifest]) -> str:
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
