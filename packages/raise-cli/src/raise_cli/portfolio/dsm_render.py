"""Markdown (and JSON) renderer for the Portfolio DSM governance artifact.

Consumes confirmed dep edges and initiative profiles; delegates all graph
logic to DependencyGraph.toposort() / .dsm_view() and derive_advisory_edges()
— zero duplicate graph logic here (guarding against AG2 clone amplification).

Design: RAISE-15209 D1, D5 (e15198-portfolio-impact-model).
"""

from __future__ import annotations

from raise_cli.portfolio.dependency.graph import DependencyGraph, TopoResult
from raise_cli.portfolio.derivation import AdvisoryEdge, derive_advisory_edges
from raise_cli.portfolio.storage import InitiativeProfile, PortfolioDep

_ALL_DEP_TYPES: frozenset[str] = DependencyGraph.ORDERING_TYPES | frozenset(
    {"conflicts", "supersedes"}
)


def render_dsm_markdown(
    deps: list[PortfolioDep],
    profiles: list[InitiativeProfile],
    *,
    snapshot_at: str = "",
    gate_verdict: str | None = None,
    gate_initiative: str | None = None,
) -> str:
    """Render a Portfolio DSM governance artifact as Markdown.

    Args:
        deps:             Confirmed dependency edges from PortfolioStore.list_deps().
        profiles:         Initiative profiles from PortfolioStore.list_initiative_profiles().
        snapshot_at:      ISO-8601 timestamp string for the snapshot metadata line.
        gate_verdict:     Optional gate result string, e.g. "PASS" or "FAIL".
        gate_initiative:  The initiative key evaluated by the gate (for display).

    Returns:
        A deterministic Markdown string suitable for committing as a governance artifact.
    """
    advisory = derive_advisory_edges(profiles)
    graph = DependencyGraph(deps=deps, advisory=advisory)
    topo = graph.toposort()
    dsm = graph.dsm_view()
    mode_map = {p.initiative_key: p.change_mode for p in profiles}

    lines: list[str] = []
    _append_header(lines, snapshot_at)
    _append_toposort(lines, topo, mode_map)
    _append_confirmed_edges(lines, deps, dsm)
    _append_advisory_edges(lines, advisory)
    if gate_verdict is not None:
        _append_gate_verdict(lines, gate_verdict, gate_initiative)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section renderers (each < C901 threshold)
# ---------------------------------------------------------------------------


def _append_header(lines: list[str], snapshot_at: str) -> None:
    lines.append("# Portfolio DSM — Dependency Structure Matrix")
    lines.append("")
    if snapshot_at:
        lines.append(f"**Snapshot**: {snapshot_at}")
        lines.append("")


def _append_toposort(
    lines: list[str],
    topo: TopoResult,
    mode_map: dict[str, str],
) -> None:
    lines.append("## Toposort Order")
    lines.append("")
    if topo.order:
        for i, key in enumerate(topo.order, start=1):
            mode = mode_map.get(key, "")
            mode_str = f" ({mode})" if mode else ""
            lines.append(f"{i}. {key}{mode_str}")
    else:
        lines.append("_No confirmed ordering edges — all initiatives are independent._")
    if topo.has_cycle:
        lines.append("")
        lines.append(
            f"> ⚠ **CYCLE DETECTED**: {' → '.join(topo.cycle)} — manual resolution required."
        )
    lines.append("")


def _append_confirmed_edges(
    lines: list[str],
    deps: list[PortfolioDep],
    dsm: dict[str, list[str]],
) -> None:
    lines.append("## Confirmed Edges")
    lines.append("")
    if dsm:
        lines.append("| Source | Type | Target | Rationale |")
        lines.append("|--------|------|--------|-----------|")
        for dep in sorted(deps, key=lambda d: (d.source, d.target)):
            if dep.type in _ALL_DEP_TYPES:
                lines.append(
                    f"| {dep.source} | {dep.type} | {dep.target} | {dep.rationale} |"
                )
    else:
        lines.append("_No confirmed edges._")
    lines.append("")


def _append_advisory_edges(lines: list[str], advisory: list[AdvisoryEdge]) -> None:
    lines.append("## Advisory Edges")
    lines.append("")
    ordering = [e for e in advisory if e.type == "sequence_with"]
    impacted = [e for e in advisory if e.type == "impacted_by"]
    if ordering:
        _append_sequence_with(lines, ordering)
    if impacted:
        _append_impacted_by(lines, impacted)
    if not ordering and not impacted:
        lines.append("_No advisory edges derived from current profiles._")
        lines.append("")


def _append_sequence_with(lines: list[str], edges: list[AdvisoryEdge]) -> None:
    lines.append("### Sequence suggestions (breaking → non-breaking)")
    lines.append("")
    lines.append("| Non-breaking | sequence_with | Breaking | Rationale |")
    lines.append("|-------------|---------------|----------|-----------|")
    for edge in _sorted_advisory(edges):
        lines.append(
            f"| {edge.source} | sequence_with | {edge.target} | {edge.rationale} |"
        )
    lines.append("")


def _append_impacted_by(lines: list[str], edges: list[AdvisoryEdge]) -> None:
    lines.append("### Component impacts (impacted_by)")
    lines.append("")
    lines.append("| Initiative | impacted_by | Component |")
    lines.append("|------------|-------------|-----------|")
    for edge in _sorted_advisory(edges):
        lines.append(f"| {edge.source} | impacted_by | {edge.target} |")
    lines.append("")


def _append_gate_verdict(
    lines: list[str],
    gate_verdict: str,
    gate_initiative: str | None,
) -> None:
    lines.append("## Gate Verdict")
    lines.append("")
    icon = "✅" if gate_verdict.upper() == "PASS" else "❌"
    init_str = f" on {gate_initiative}" if gate_initiative else ""
    lines.append(f"{icon} **gate-before-ready{init_str}**: {gate_verdict.upper()}")
    lines.append("")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sorted_advisory(edges: list[AdvisoryEdge]) -> list[AdvisoryEdge]:
    return sorted(edges, key=lambda e: (e.source, e.target))
