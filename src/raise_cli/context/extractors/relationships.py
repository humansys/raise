"""Relationship inference for the context graph.

Infers edges between concept nodes using explicit metadata
(learned_from, part_of, prerequisites) and heuristic keyword overlap.
"""

from __future__ import annotations

from typing import Any, cast

from raise_cli.core.text import STOPWORDS
from raise_core.graph.models import GraphEdge, GraphNode


def infer_relationships(nodes: list[GraphNode]) -> list[GraphEdge]:
    """Infer relationships between concepts.

    Creates explicit edges (weight=1.0) from known fields and
    inferred edges (weight<1.0) from heuristics.
    """
    if not nodes:
        return []

    edges: list[GraphEdge] = []
    node_by_id: dict[str, GraphNode] = {n.id: n for n in nodes}

    edges.extend(_infer_learned_from(nodes, node_by_id))
    edges.extend(_infer_part_of(nodes, node_by_id))
    edges.extend(_infer_skill_edges(nodes, node_by_id))
    edges.extend(_infer_depends_on(nodes, node_by_id))
    edges.extend(_infer_release_part_of(nodes, node_by_id))
    edges.extend(_infer_keyword_relationships(nodes))

    return edges


def _infer_learned_from(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],  # noqa: ARG001 — kept for consistent infer_* signature
) -> list[GraphEdge]:
    """Infer learned_from edges from pattern metadata."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "pattern":
            continue

        learned_from = node.metadata.get("learned_from")
        if not learned_from:
            continue

        for candidate in nodes:
            if candidate.type != "session":
                continue
            if str(learned_from) in candidate.content:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=candidate.id,
                        type="learned_from",
                        weight=1.0,
                    )
                )
                break

    return edges


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
    """Infer depends_on edges from module metadata."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "module":
            continue

        raw_deps: Any = node.metadata.get("depends_on", [])
        if not isinstance(raw_deps, list):
            continue
        deps = cast("list[str]", raw_deps)

        for dep_name in deps:
            target_id = f"mod-{dep_name}"
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


def _infer_keyword_relationships(
    nodes: list[GraphNode],
) -> list[GraphEdge]:
    """Infer related_to edges from shared keywords."""
    edges: list[GraphEdge] = []

    node_keywords: dict[str, set[str]] = {}
    for node in nodes:
        keywords = _extract_keywords(node)
        if keywords:
            node_keywords[node.id] = keywords

    node_ids = list(node_keywords.keys())
    for i, id1 in enumerate(node_ids):
        for id2 in node_ids[i + 1 :]:
            shared = node_keywords[id1] & node_keywords[id2]
            if len(shared) >= 2:
                edges.append(
                    GraphEdge(
                        source=id1,
                        target=id2,
                        type="related_to",
                        weight=0.5,
                        metadata={"shared_keywords": list(shared)},
                    )
                )

    return edges


def _extract_keywords(node: GraphNode) -> set[str]:
    """Extract keywords from a concept node."""
    keywords: set[str] = set()

    if node.content:
        words = node.content.lower().split()
        for word in words:
            clean = "".join(c for c in word if c.isalnum())
            if len(clean) >= 4 and clean not in STOPWORDS:
                keywords.add(clean)

    context_value: Any = node.metadata.get("context", [])
    if isinstance(context_value, list):
        context_list = cast("list[Any]", context_value)
        for ctx in context_list:
            if isinstance(ctx, str):
                keywords.add(ctx.lower())

    return keywords
