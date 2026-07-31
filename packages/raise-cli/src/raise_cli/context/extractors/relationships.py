"""Relationship inference for the context graph.

Infers edges between concept nodes using explicit metadata
(learned_from, part_of, prerequisites) and deterministic pattern edges.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, cast

from raise_core.graph.models import GraphEdge, GraphNode


@dataclass
class EdgeResolutionReport:
    """Tracks resolution metrics for one edge type."""

    edge_type: str
    attempted: int
    resolved: int
    unresolved: int
    dangling: int

    @property
    def resolution_rate(self) -> float:
        """Fraction of attempted resolutions that succeeded."""
        return self.resolved / self.attempted if self.attempted > 0 else 0.0


@dataclass
class GraphHealthReport:
    """Aggregated health report from graph build."""

    total_nodes: int
    total_edges: int
    edge_resolutions: list[EdgeResolutionReport] = field(default_factory=list)
    dangling_edges: int = 0


def _normalize_learned_from_ref(ref: str) -> tuple[str, str]:
    """Normalize a learned_from ref to (canonical_id, target_type).

    Returns ("", "") for unresolvable freetext refs.
    """
    ref = ref.strip()
    if not ref:
        return ("", "")
    # S1962.7, s583.1 → story (graph ID: story-s1962-7)
    if re.match(r"^[Ss]\d+\.\d+$", ref):
        slug = ref.lower().replace(".", "-")
        return (f"story-{slug}", "story")
    # F1.5, F14.13 → story (graph ID: story-f1-5)
    if re.match(r"^F\d+\.\d+$", ref):
        slug = ref.lower().replace(".", "-")
        return (f"story-{slug}", "story")
    # SES-357 → session
    if ref.startswith("SES-"):
        return (ref, "session")
    # S-E-260414-0743, S-F-260415-0128-AB12 → session
    # (entropy suffix optional: added by RAISE-15482, old ids lack it)
    if re.match(r"^S-[A-Z]+-\d{6}-\d{4}(-[0-9A-F]{4})?$", ref):
        return (ref, "session")
    # RAISE-1276 → epic
    if ref.startswith("RAISE-"):
        num = ref.split("-", 1)[1]
        return (f"epic-e{num}", "epic")
    # UUID → session
    if re.match(r"^[0-9a-f]{8}-", ref):
        return (ref, "session")
    return ("", "")


def infer_relationships(
    nodes: list[GraphNode],
) -> tuple[list[GraphEdge], GraphHealthReport]:
    """Infer relationships between concepts using deterministic metadata.

    Returns edges and a health report with resolution metrics.
    """
    if not nodes:
        return [], GraphHealthReport(total_nodes=0, total_edges=0)

    edges: list[GraphEdge] = []
    node_by_id: dict[str, GraphNode] = {n.id: n for n in nodes}
    resolutions: list[EdgeResolutionReport] = []

    lf_edges, lf_report = _infer_pattern_learned_from(nodes, node_by_id)
    edges.extend(lf_edges)
    resolutions.append(lf_report)

    at_edges, at_report = _infer_pattern_applies_to(nodes, node_by_id)
    edges.extend(at_edges)
    resolutions.append(at_report)

    pm_edges, pm_report = _infer_pattern_mission(nodes, node_by_id)
    edges.extend(pm_edges)
    resolutions.append(pm_report)

    edges.extend(_infer_part_of(nodes, node_by_id))
    edges.extend(_infer_skill_edges(nodes, node_by_id))
    edges.extend(_infer_depends_on(nodes, node_by_id))
    edges.extend(_infer_release_part_of(nodes, node_by_id))

    dangling = sum(
        1 for e in edges if e.source not in node_by_id or e.target not in node_by_id
    )

    report = GraphHealthReport(
        total_nodes=len(nodes),
        total_edges=len(edges),
        edge_resolutions=resolutions,
        dangling_edges=dangling,
    )
    return edges, report


def _infer_pattern_learned_from(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → story/session/epic edges via learned_from metadata."""
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0

    for node in nodes:
        if node.type != "pattern":
            continue
        raw_lf = node.metadata.get("learned_from")
        if not raw_lf:
            continue

        attempted += 1
        refs = [r.strip() for r in str(raw_lf).replace(",", " ").split() if r.strip()]
        matched = False
        for ref in refs:
            canonical_id, _ = _normalize_learned_from_ref(ref)
            if canonical_id and canonical_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=canonical_id,
                        type="learned_from",
                        weight=1.0,
                    )
                )
                matched = True
        if matched:
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="learned_from",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=0,
    )


def _infer_pattern_applies_to(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → module edges via context keywords → mod-{keyword} exact match."""
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0

    for node in nodes:
        if node.type != "pattern":
            continue
        context: Any = node.metadata.get("context", [])
        if not isinstance(context, list) or not context:
            continue

        attempted += 1
        matched = False
        for keyword in context:
            if not isinstance(keyword, str):
                continue
            mod_id = f"mod-{keyword}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=mod_id,
                        type="applies_to",
                        weight=0.8,
                    )
                )
                matched = True
        if matched:
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="applies_to",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=0,
    )


def _infer_pattern_mission(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → mission edges via mission_id metadata."""
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0

    for node in nodes:
        if node.type != "pattern":
            continue
        mission_id = node.metadata.get("mission_id")
        if not mission_id:
            continue

        attempted += 1
        target_id = f"mission-{mission_id}"
        if target_id in node_by_id:
            edges.append(
                GraphEdge(
                    source=node.id,
                    target=target_id,
                    type="part_of_mission",
                    weight=1.0,
                )
            )
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="part_of_mission",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=0,
    )


def _infer_part_of(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer part_of edges from story to epic."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "story":
            continue

        story_id = node.id
        if story_id.startswith("F"):
            parts = story_id[1:].split(".")
            if parts:
                epic_id = f"E{parts[0]}"
                if epic_id in node_by_id:
                    edges.append(
                        GraphEdge(
                            source=node.id,
                            target=epic_id,
                            type="part_of",
                            weight=1.0,
                        )
                    )

    return edges


def _infer_skill_edges(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer edges from skill metadata (prerequisites, next)."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "skill":
            continue

        prereq = node.metadata.get("raise.prerequisites")
        if prereq:
            prereq_id = f"/{prereq}" if not str(prereq).startswith("/") else prereq
            if prereq_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=prereq_id,
                        type="needs_context",
                        weight=1.0,
                    )
                )

        next_skill = node.metadata.get("raise.next")
        if next_skill:
            next_id = (
                f"/{next_skill}" if not str(next_skill).startswith("/") else next_skill
            )
            if next_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=next_id,
                        type="related_to",
                        weight=1.0,
                    )
                )

    return edges


def _infer_depends_on(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer depends_on edges from module and component metadata (RAISE-573)."""
    edges: list[GraphEdge] = []

    # Build name→id index for component nodes (class name → node ID)
    comp_name_index: dict[str, str] = {}
    for node in nodes:
        if node.type == "component":
            name = node.metadata.get("name", "")
            if name:
                comp_name_index[name] = node.id

    for node in nodes:
        if node.type not in ("module", "component"):
            continue

        raw_deps: Any = node.metadata.get("depends_on", [])
        if not isinstance(raw_deps, list):
            continue
        deps = cast("list[str]", raw_deps)

        for dep_name in deps:
            # Resolution order: component name → module name
            target_id = comp_name_index.get(dep_name) or f"mod-{dep_name}"
            if target_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=target_id,
                        type="depends_on",
                        weight=1.0,
                    )
                )

    return edges


def _infer_release_part_of(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer part_of edges from epics to releases."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "release":
            continue

        epic_refs: Any = node.metadata.get("epics", [])
        if not isinstance(epic_refs, list):
            continue

        for epic_ref in cast("list[str]", epic_refs):
            epic_id = f"epic-{epic_ref.lower()}"
            if epic_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=epic_id,
                        target=node.id,
                        type="part_of",
                        weight=1.0,
                    )
                )

    return edges
