"""Retrieval engine: scoring functions and retrieve() orchestrator.

All scoring logic lives here. Domain adapters advise; the engine decides.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from rai_agent.knowledge.retrieval.models import (
    DomainAdapter,
    DomainHints,
    RetrievalResult,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

# Composite scoring weights (AR-Q3: named constants)
# SA = structural proximity, ATTR = keyword overlap, DOMAIN = adapter annotation
W_SA: float = 0.5
W_ATTR: float = 0.3
W_DOMAIN: float = 0.2


# --- Scoring functions (pure, no side effects) ---


def spreading_activation(
    graph: Graph,
    seed_ids: list[str],
    decay: float = 0.5,
    max_depth: int = 2,
    edge_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """BFS-based spreading activation from seed nodes.

    Each hop multiplies activation by decay * edge_weight.
    Multiple paths: keeps the max activation seen for each node.

    Returns:
        Mapping of node_id → activation score.
    """
    if not seed_ids:
        return {}

    scores: dict[str, float] = {}
    # Queue entries: (node_id, current_activation, current_depth)
    queue: deque[tuple[str, float, int]] = deque()

    for sid in seed_ids:
        if sid in graph.graph.nodes:
            scores[sid] = 1.0
            queue.append((sid, 1.0, 0))

    if not scores:
        return {}

    while queue:
        node_id, activation, depth = queue.popleft()
        if depth >= max_depth:
            continue

        # Outgoing edges
        out_edge: tuple[str, str, dict[str, Any]]
        for out_edge in graph.graph.out_edges(node_id, data=True):
            target: str = out_edge[1]
            edge_data: dict[str, Any] = out_edge[2]
            edge_type: str = edge_data.get("type", "")
            w = (edge_weights or {}).get(edge_type, 1.0) if edge_weights else 1.0
            new_activation = activation * decay * w
            if new_activation > scores.get(target, 0.0):
                scores[target] = new_activation
                queue.append((target, new_activation, depth + 1))

        # Incoming edges (undirected traversal)
        in_edge: tuple[str, str, dict[str, Any]]
        for in_edge in graph.graph.in_edges(node_id, data=True):
            source: str = in_edge[0]
            edge_data = in_edge[2]
            edge_type = edge_data.get("type", "")
            w = (edge_weights or {}).get(edge_type, 1.0) if edge_weights else 1.0
            new_activation = activation * decay * w
            if new_activation > scores.get(source, 0.0):
                scores[source] = new_activation
                queue.append((source, new_activation, depth + 1))

    return scores


def attribute_match(node: GraphNode, keywords: list[str]) -> float:
    """Keyword overlap ratio between node content and query keywords.

    Returns:
        Float in [0.0, 1.0]. 0.0 if no keywords provided.
    """
    if not keywords:
        return 0.0
    content_lower = node.content.lower()
    matches = sum(1 for kw in keywords if kw.lower() in content_lower)
    return matches / len(keywords)


def composite_score(
    sa: float,
    attr: float,
    domain: float,
    weights: tuple[float, float, float] = (W_SA, W_ATTR, W_DOMAIN),
) -> float:
    """Weighted sum of three scoring signals.

    Args:
        sa: Spreading activation score (structural proximity).
        attr: Attribute match score (keyword overlap).
        domain: Domain adapter annotation score (type boost + domain-specific signals).
        weights: (w_sa, w_attr, w_domain) tuple, defaults to module constants.
    """
    return weights[0] * sa + weights[1] * attr + weights[2] * domain


# --- Orchestrator ---


def _keyword_search_fallback(graph: Graph, query: str) -> list[GraphNode]:
    """Fallback: scan all nodes for keyword matches."""
    keywords = query.lower().split()
    results: list[GraphNode] = []
    for node in graph.iter_concepts():
        if any(kw in node.content.lower() for kw in keywords):
            results.append(node)
    return results


def _traverse(graph: Graph, advice: TraversalAdvice) -> list[GraphNode]:
    """Execute BFS traversal following adapter's advice."""
    if not advice.start_node_ids:
        return []

    visited: set[str] = set()
    nodes: list[GraphNode] = []

    edge_types_list: list[str] | None = (
        list(advice.edge_type_filter) if advice.edge_type_filter else None
    )

    for seed_id in advice.start_node_ids:
        seed = graph.get_concept(seed_id)
        if seed is None:
            continue
        if seed_id not in visited:
            visited.add(seed_id)
            nodes.append(seed)

        neighbors = graph.get_neighbors(
            seed_id, depth=advice.max_depth, edge_types=edge_types_list
        )
        for neighbor in neighbors:
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                if (
                    advice.node_type_filter is None
                    or neighbor.type in advice.node_type_filter
                ):
                    nodes.append(neighbor)

    return nodes


def retrieve(
    graph: Graph,
    query: str,
    adapter: DomainAdapter,
    top_k: int = 10,
) -> RetrievalResult:
    """Domain-agnostic retrieval: interpret → advise → traverse → annotate → score.

    Each adapter step has a graceful fallback on failure.
    """
    # Step 1: interpret query
    try:
        hints = adapter.interpret_query(query)
    except Exception:
        logger.warning("adapter.interpret_query failed, using fallback hints")
        hints = DomainHints(domain="unknown")

    # Step 2: get traversal advice
    try:
        available_types = frozenset(n.type for n in graph.iter_concepts() if n.type)
        advice = adapter.advise_traversal(hints, available_types)
    except Exception:
        logger.warning("adapter.advise_traversal failed, using keyword fallback")
        advice = None

    # Step 3: traverse graph
    if advice is not None:
        traversed = _traverse(graph, advice)
    else:
        traversed = _keyword_search_fallback(graph, query)

    if not traversed:
        return RetrievalResult(query=query, hints=hints)

    # Step 4: adapter annotates results
    try:
        annotated = adapter.annotate_results(traversed, hints)
    except Exception:
        logger.warning("adapter.annotate_results failed, using zero scores")
        annotated = [
            ScoredNode(node=n, score=0.0, explanation="annotation failed")
            for n in traversed
        ]

    # Step 5: composite scoring — SA (with adapter edge weights) + attr + domain annotation
    sa_scores = spreading_activation(
        graph,
        seed_ids=advice.start_node_ids if advice else [],
        max_depth=advice.max_depth if advice else 2,
        edge_weights=advice.edge_weights if advice and advice.edge_weights else None,
    )
    keywords = query.lower().split()

    scored: list[ScoredNode] = []
    for sn in annotated:
        sa_val = sa_scores.get(sn.node.id, 0.0)
        attr_val = attribute_match(sn.node, keywords)
        domain_val = sn.score
        final = composite_score(sa=sa_val, attr=attr_val, domain=domain_val)
        scored.append(
            ScoredNode(
                node=sn.node,
                score=final,
                explanation=f"SA={sa_val:.2f}, attr={attr_val:.2f}, domain={domain_val:.2f}",
            )
        )

    scored.sort(reverse=True)
    return RetrievalResult(
        nodes=scored[:top_k],
        query=query,
        hints=hints,
    )
