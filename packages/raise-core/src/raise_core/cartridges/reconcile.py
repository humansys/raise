"""Post-extraction reconciliation — detect phantoms, orphans, cross-category edges.

Generic version operating on GraphNode (ported from scaleupagent).
Pure logic, no LLM calls.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from raise_core.graph.models import GraphNode


class BrokenRelationship(BaseModel):
    """A relationship whose target does not resolve to any node."""

    source: str
    type: str
    target: str


class ReconciliationReport(BaseModel):
    """Result of reconciling extracted nodes."""

    phantom_targets: list[str] = Field(default_factory=list)
    orphan_nodes: list[str] = Field(default_factory=list)
    cross_category_edges: list[tuple[str, str]] = Field(default_factory=list)
    broken_relationships: list[BrokenRelationship] = Field(default_factory=list)


def reconcile_nodes(
    nodes: list[GraphNode], *, id_prefix: str | None = None
) -> ReconciliationReport:
    """Analyze nodes for structural issues.

    When *id_prefix* is given, a relationship target also resolves if
    ``{id_prefix}{target}`` is a node ID — the same rule ingest applies
    for cartridge slugs (see ingest.resolve_relationship_target).
    """
    if not nodes:
        return ReconciliationReport()

    node_map = {n.id: n for n in nodes}
    all_ids = set(node_map.keys())

    def resolves(target: str) -> bool:
        if target in all_ids:
            return True
        return id_prefix is not None and f"{id_prefix}{target}" in all_ids

    all_targets, broken = _collect_targets(nodes, resolves)
    phantoms = sorted(t for t in all_targets if not resolves(t))

    referenced_ids = all_targets & all_ids
    orphans = sorted(
        n.id for n in nodes if not _get_relationships(n) and n.id not in referenced_ids
    )

    cross_edges = _find_cross_category_edges(nodes, node_map)

    return ReconciliationReport(
        phantom_targets=phantoms,
        orphan_nodes=orphans,
        cross_category_edges=cross_edges,
        broken_relationships=broken,
    )


def _collect_targets(
    nodes: list[GraphNode], resolves: Callable[[str], bool]
) -> tuple[set[str], list[BrokenRelationship]]:
    """Gather all relationship targets and the relationships that don't resolve."""
    all_targets: set[str] = set()
    broken: list[BrokenRelationship] = []
    for node in nodes:
        for rel in _get_relationships(node):
            target = rel.get("target", "")
            if not target:
                continue
            all_targets.add(target)
            if not resolves(target):
                broken.append(
                    BrokenRelationship(
                        source=node.id, type=rel.get("type", ""), target=target
                    )
                )
    return all_targets, broken


def _find_cross_category_edges(
    nodes: list[GraphNode], node_map: dict[str, GraphNode]
) -> list[tuple[str, str]]:
    """Find edges connecting nodes of different categories."""
    cross_edges: list[tuple[str, str]] = []
    for node in nodes:
        node_cat = _get_category(node)
        if node_cat is None:
            continue
        for rel in _get_relationships(node):
            target_node = node_map.get(rel.get("target", ""))
            if target_node is None:
                continue
            target_cat = _get_category(target_node)
            if target_cat is not None and target_cat != node_cat:
                cross_edges.append((node.id, target_node.id))
    return cross_edges


def _get_relationships(node: GraphNode) -> list[dict[str, Any]]:
    rels = node.metadata.get("relationships", [])
    if isinstance(rels, list):
        return rels
    return []


def _get_category(node: GraphNode) -> str | None:
    cat = node.metadata.get("category")
    return str(cat) if cat is not None else None


__all__ = ["BrokenRelationship", "ReconciliationReport", "reconcile_nodes"]
