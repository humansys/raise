"""Context bundle assembly for session start.

Assembles a token-optimized context bundle (~600 tokens) from multiple sources:
1. ~/.rai/developer.yaml → developer model + coaching + deadlines
2. .raise/rai/session-state.yaml → current work state
3. Memory graph → foundational patterns, governance primes
4. .raise/rai/personal/sessions/index.jsonl → recent sessions

Note: Identity primes (RAI-VAL-*, RAI-BND-*) are no longer emitted here.
They live in AGENTS.md as always-on content (ADR-012).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.storage.worktrees import Worktree

from raise_cli.exceptions import ConfigurationError
from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_ledger import LedgerEntry
from raise_cli.schemas.session_state import CurrentWork, SessionState
from raise_cli.session.donor import ContinuityDonorDecision, DonorSource
from raise_core.graph.models import GraphNode

from .bundle_data import (
    BundleProvenance,
    SectionManifest,
    fetch_live_status,
    find_release_for_current_epic,
    get_always_on_primes,
    get_foundational_patterns,
)
from .bundle_formatters import (
    format_cli_reference,
    format_coaching,
    format_code_context,
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
    format_provenance,
    format_recent_sessions,
    format_work_section,
    format_worktree_section,
)
from .ledger import render_sections as format_ledger

_logger = logging.getLogger(__name__)

# AR F2 (RAISE-13146): the write path fails loud on an unresolvable
# session_id (AC7). The read/surface path must not swallow the same
# condition into a silently-empty section — "silently empty" is the
# mission's named anti-goal.
_LEDGER_UNAVAILABLE_MARKER = "_Ledger unavailable: no resolvable session id_"

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
    "code_context": 15,
    "cli_reference": 3,
    "ledger": 20,
}


def derive_current_work(project_path: Path) -> CurrentWork | None:
    """Try to derive current work from git. Returns None on failure.

    Uses GitStateDeriver (ADR-038) to read branch, epic, story, and phase
    from git state. Falls back gracefully — never raises.
    """
    try:
        from raise_cli.session.derive import GitStateDeriver

        return GitStateDeriver().current_work(project_path)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _logger.debug(
            "Git state derivation failed — using YAML fallback", exc_info=True
        )
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


def _read_ledger_entries(
    project_path: Path, agent_session_id: str | None = None
) -> list[LedgerEntry]:
    """Read the current session's ledger entries, resolving session_id in-process.

    Resolves session_id via ``discover_agent_session_id(override=agent_session_id)``
    (env-based, worktree-proof) — NEVER via ``profile.active_sessions`` or
    path-equality (MUST-NOT #9). Returns [] when the session_id is unresolvable.

    Args:
        project_path: Absolute path to the project root.
        agent_session_id: Explicit session_id override (RAISE-9886 idiom),
            symmetric with the write path's ``raise_ledger_add`` override
            (AR F1, RAISE-13146) — closes the seam where a write under an
            explicit session could otherwise surface empty under a
            divergent env-resolved session.
    """
    from raise_cli._agent_session import discover_agent_session_id
    from raise_cli.session import ledger

    session_id = discover_agent_session_id(override=agent_session_id)
    if not session_id:
        return []
    return ledger.read_entries(session_id, project_path)


def _count_ledger(project_path: Path, agent_session_id: str | None = None) -> int:
    """Count ledger rows for the current session."""
    return len(_read_ledger_entries(project_path, agent_session_id))


def _count_code_context(project_path: Path, state: SessionState | None) -> int:
    """Count code context symbols from graph for active work."""
    from .bundle_data import get_code_symbols

    current_work = derive_current_work(project_path) if state is None else None
    work = current_work or (state.current_work if state else None)
    if work is None:
        return 0
    symbols = get_code_symbols(project_path, work)
    return len(symbols)


# Registry: section name → format function
# Format functions have heterogeneous signatures; the registry maps names
# for validation and dispatch. Actual calling happens in assemble_sections().
SECTION_REGISTRY: dict[str, Callable[..., str]] = {
    "governance": format_governance_primes,
    "behavioral": format_primes,
    "coaching": format_coaching,
    "deadlines": format_deadlines,
    "progress": format_progress,
    "code_context": format_code_context,
    "cli_reference": format_cli_reference,
    "ledger": format_ledger,
}


def count_section_items(
    section: str,
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
    agent_session_id: str | None = None,
) -> int:
    """Count items in a named section.

    Args:
        section: Section name from SECTION_REGISTRY.
        project_path: Absolute path to the project root.
        profile: Developer profile.
        state: Session state (may be None).
        agent_session_id: Explicit session_id override, consumed by the
            ``ledger`` section (RAISE-9886 idiom, AR F1 RAISE-13146).

    Returns:
        Number of items in the section.

    Raises:
        ValueError: If section name is not in SECTION_REGISTRY.
    """
    if section not in SECTION_REGISTRY:
        raise ConfigurationError(
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
    if section == "code_context":
        return _count_code_context(project_path, state)
    if section == "cli_reference":
        from .bundle_data import get_cli_commands

        return len(get_cli_commands())
    if section == "ledger":
        return _count_ledger(project_path, agent_session_id)

    return 0  # unreachable but satisfies pyright


def _format_governance_combined(project_path: Path) -> str:
    """Combine local graph governance + server-cached governance."""
    parts: list[str] = []
    local_gov = format_governance_primes(get_always_on_primes(project_path))
    if local_gov:
        parts.append(local_gov)
    try:
        from raise_cli.config.server import get_server_credentials

        if get_server_credentials() is not None:
            from raise_cli.session.bundle_governance import format_governance_cached
            from raise_cli.storage.connection import get_project_db, get_project_id

            gov_conn = get_project_db(project_path)
            server_gov = format_governance_cached(
                gov_conn, get_project_id(project_path)
            )
            if server_gov:
                parts.append(server_gov)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _logger.debug("Server governance read failed", exc_info=True)
    return "\n\n".join(parts)


def _format_section(
    name: str,
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
    agent_session_id: str | None = None,
) -> str:
    """Format a single section by name. Assumes name is valid.

    Args:
        name: Section name from SECTION_REGISTRY.
        project_path: Absolute path to the project root.
        profile: Developer profile.
        state: Session state (may be None).
        agent_session_id: Explicit session_id override, consumed by the
            ``ledger`` section (RAISE-9886 idiom, AR F1 RAISE-13146).
    """
    if name == "governance":
        return _format_governance_combined(project_path)
    if name == "behavioral":
        return format_primes(get_foundational_patterns(project_path))
    if name == "coaching":
        return format_coaching(profile)
    if name == "deadlines":
        return format_deadlines(profile)
    if name == "progress":
        return format_progress(state)
    if name == "code_context":
        from .bundle_data import get_code_symbols

        current_work = derive_current_work(project_path)
        work = current_work or (state.current_work if state else None)
        symbols = get_code_symbols(project_path, work)
        return format_code_context(symbols)
    if name == "cli_reference":
        from .bundle_data import get_cli_commands

        return format_cli_reference(get_cli_commands())
    if name == "ledger":
        from raise_cli._agent_session import discover_agent_session_id
        from raise_cli.session import ledger

        session_id = discover_agent_session_id(override=agent_session_id)
        if not session_id:
            return _LEDGER_UNAVAILABLE_MARKER
        return ledger.render_sections(ledger.read_entries(session_id, project_path))
    return ""


def assemble_sections(
    sections: list[str],
    project_path: Path,
    profile: DeveloperProfile,
    state: SessionState | None,
    agent_session_id: str | None = None,
) -> str:
    """Assemble formatted output for selected priming sections.

    Each section independently loads its data source (graph, profile, or state)
    and formats the output. Section names are validated against SECTION_REGISTRY.

    Args:
        sections: List of section names to load (e.g., ["governance", "behavioral"]).
        project_path: Absolute path to the project root.
        profile: Developer profile.
        state: Session state (may be None).
        agent_session_id: Explicit session_id override (RAISE-9886 idiom).
            Consumed by the ``ledger`` section — resolved in-process and
            threaded here from `raise_session_context` / `rai session
            context --session`, symmetric with the write path's
            `raise_ledger_add(agent_session_id=...)` override (AR F1,
            RAISE-13146). Ignored by sections that don't key on session_id.

    Returns:
        Formatted sections joined by blank lines, or empty string if no content.

    Raises:
        ValueError: If any section name is not in SECTION_REGISTRY.
    """
    if not sections:
        return ""

    for name in sections:
        if name not in SECTION_REGISTRY:
            raise ConfigurationError(
                f"Unknown section: '{name}'. Valid: {sorted(SECTION_REGISTRY.keys())}"
            )

    parts = [
        part
        for name in sections
        if (
            part := _format_section(
                name, project_path, profile, state, agent_session_id
            )
        )
    ]
    return "\n\n".join(parts)


def _build_provenance(
    *,
    donor_decision: ContinuityDonorDecision | None,
    worktree: Worktree | None,
    current_work_source: str,
) -> BundleProvenance:
    """Convert resolved bundle context into formatter-ready provenance."""
    return BundleProvenance(
        continuity_source=(
            donor_decision.source if donor_decision is not None else DonorSource.NONE
        ),
        continuity_session_id=(
            donor_decision.selected_session_id if donor_decision is not None else None
        ),
        mission_id=None,
        mission_source="none",
        worktree_id=worktree.worktree_id if worktree is not None else None,
        worktree_source="registered open" if worktree is not None else "none",
        current_work_source=current_work_source,
        mismatch=donor_decision.mismatch if donor_decision is not None else None,
    )


def assemble_orientation(  # noqa: C901
    profile: DeveloperProfile,
    state: SessionState | None,
    project_path: Path,
    session_id: str | None = None,
    worktree: Worktree | None = None,
    *,
    donor_decision: ContinuityDonorDecision | None = None,
) -> str:
    """Assemble orientation-only context (always-on sections).

    Orientation = "where are we?" — work state, continuity, pending.
    Does NOT include priming sections (governance, behavioral, coaching,
    deadlines, progress). Those are loaded separately via assemble_sections().

    Returns:
        Plain text orientation context.
    """
    # Derive current work from git (ADR-038); fallback to YAML state
    try:
        derived_work = derive_current_work(project_path)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _logger.debug("derive_current_work raised — using YAML fallback", exc_info=True)
        derived_work = None
    current_work_source = (
        "git branch"
        if derived_work is not None
        else "fallback state"
        if state
        else "none"
    )

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

    parts.append(
        format_provenance(
            _build_provenance(
                donor_decision=donor_decision,
                worktree=worktree,
                current_work_source=current_work_source,
            )
        )
    )

    # Fetch live backlog status (never blocks — degrades gracefully)
    live = fetch_live_status(state)

    parts.append(
        format_work_section(
            state, release_node=release_node, live=live, current_work=derived_work
        )
    )

    # Worktree context (injected when CWD is a registered worktree)
    if worktree is not None:
        parts.append(format_worktree_section(worktree))

    # Last session + recent sessions (scoped to the caller's worktree — E15456)
    parts.append(format_last_session(state))
    dev_prefix = profile.get_pattern_prefix()
    from raise_cli.session.scope import resolve_scope

    scope = resolve_scope(project_path)
    recent = format_recent_sessions(
        project_path, developer_prefix=dev_prefix, scope=scope
    )
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

    # Session ledger (RAISE-13341) — cross-project state, auto-surfaced at
    # orientation so a NEW session sees the prior one's ledger without a manual
    # --session. Full ledger inline (HITL decision A). The ledger is keyed by
    # the agent_session_id (CC uuid), a DIFFERENT id space than this function's
    # ``session_id`` param — so resolve it in-process, like the `ledger` section
    # in assemble_sections. resolve_surface_session applies the cross-session
    # fallback (current session if populated, else most recent previous session
    # attributable to the caller's worktree — E15456). Fail-open: never blocks
    # orientation.
    ledger_block = format_orientation_ledger(project_path)
    if ledger_block:
        parts.append(ledger_block)

    # Filter empty sections, join with blank lines
    return "\n\n".join(s for s in parts if s)


def format_orientation_ledger(project_path: Path) -> str:
    """Render the auto-surfaced session ledger block for orientation (RAISE-13341).

    Resolves the agent_session_id in-process, applies the cross-session
    fallback, and renders the full ledger. Marks the origin session when it
    comes from a previous session. Fail-open — returns "" on any error.

    Public (not `_`-prefixed): also called directly from
    `raise_cli.session.open_service` to surface the ledger through its own
    read-only channel on `OpenReport` when the mutating start bundle is
    skipped (RAISE-13382) — the ledger is cross-session continuity,
    independent of mission-selection/hygiene gating.
    """
    try:
        from raise_cli._agent_session import discover_agent_session_id
        from raise_cli.session import ledger as _ledger
        from raise_cli.session.scope import resolve_scope

        agent_sid = discover_agent_session_id()
        scope = resolve_scope(project_path, agent_sid)
        surfaced = _ledger.resolve_surface_session(project_path, agent_sid, scope=scope)
        if not surfaced:
            return ""
        body = _ledger.render_sections(_ledger.read_entries(surfaced, project_path))
        if not body:
            return ""
        header = (
            "## Session Ledger"
            if surfaced == agent_sid
            else f"## Session Ledger (sesión previa {surfaced})"
        )
        return f"{header}\n\n{body}"
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _logger.debug("orientation ledger surface failed — skipping", exc_info=True)
        return ""


def assemble_context_bundle(
    profile: DeveloperProfile,
    state: SessionState | None,
    project_path: Path,
    session_id: str | None = None,
    worktree: Worktree | None = None,
    *,
    donor_decision: ContinuityDonorDecision | None = None,
) -> str:
    """Assemble lean context bundle: orientation + manifest.

    Emits always-on orientation sections plus a manifest of available
    priming sections (with counts and token estimates). Priming sections
    are loaded separately via `rai session context --sections`.

    Returns:
        Plain text context bundle: orientation + manifest.
    """
    # Orientation (always-on sections)
    orientation = assemble_orientation(
        profile,
        state,
        project_path,
        session_id,
        worktree=worktree,
        donor_decision=donor_decision,
    )

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
