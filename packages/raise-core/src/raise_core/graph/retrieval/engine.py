"""Retrieval engine: scoring functions and retrieve() orchestrator.

All scoring logic lives here. Domain adapters advise; the engine decides.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any, Protocol, runtime_checkable

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode
from raise_core.graph.retrieval.models import (
    DomainAdapter,
    DomainHints,
    RetrievalResult,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.retrieval.text import (
    STOP_WORDS,
    expand_keywords,
    extract_keywords,
)

logger = logging.getLogger(__name__)

# Composite scoring weights (AR-Q3: named constants)
# SA = structural proximity, ATTR = keyword overlap, DOMAIN = adapter annotation, SEM = semantic similarity
# Tuned on the raise-methodology corpus (2179 nodes, 31 CQs) — S-KC7.9.
# The neutral-adapter eval can only observe ATTR and SEM; SA/DOMAIN weights
# are preserved for production adapters, which this suite cannot measure.
W_SA: float = 0.4
W_ATTR: float = 0.3
W_DOMAIN: float = 0.2
W_SEM: float = 0.1


@runtime_checkable
class SemanticScorer(Protocol):
    """Protocol for semantic similarity scoring of graph nodes."""

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:
        """Return semantic similarity scores for the given node IDs."""
        ...


class CandidateSearcher(Protocol):
    """Optional extension: generate independent semantic candidates."""

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by semantic similarity.

        Each dict has at least 'node_id' and 'similarity' keys.
        """
        ...


# --- Scoring functions (pure, no side effects) ---


def spreading_activation(  # noqa: C901
    graph: Graph,
    seed_ids: list[str],
    decay: float = 0.5,
    max_depth: int = 2,
    edge_weights: dict[str, float] | None = None,
    edge_type_filter: list[str] | None = None,
    initial_activations: dict[str, float] | None = None,
) -> dict[str, float]:
    """BFS-based spreading activation from seed nodes.

    Each hop multiplies activation by decay * edge_weight.
    Multiple paths: keeps the max activation seen for each node.

    Args:
        graph: The knowledge graph to traverse.
        seed_ids: Starting node IDs (activation = 1.0 unless overridden).
        decay: Activation multiplier per hop.
        max_depth: Maximum BFS depth.
        edge_weights: Per-edge-type weight multiplier.
        edge_type_filter: When not None, only edges whose type is in this list
            are traversed. None = all edges (backward-compatible default).
            Empty list = no edges traversed (only seeds get activation).
        initial_activations: Per-seed starting activation. A seed present in
            this mapping starts at its value instead of 1.0; seeds absent from
            it (or None = whole arg omitted) default to 1.0. This lets the
            caller weight seeds by their real relevance so the highest-weight
            SA signal discriminates within the top bucket instead of flooding
            it with ties (RAISE-10243 / V5). Lower seed activation also
            propagates proportionally less to neighbors.

    Returns:
        Mapping of node_id → activation score.
    """
    if not seed_ids:
        return {}

    # Convert to set once for O(1) membership checks
    allowed_types: frozenset[str] | None = (
        frozenset(edge_type_filter) if edge_type_filter is not None else None
    )

    scores: dict[str, float] = {}
    # Queue entries: (node_id, current_activation, current_depth)
    queue: deque[tuple[str, float, int]] = deque()

    init_map = initial_activations or {}
    for sid in seed_ids:
        if sid in graph.graph.nodes:
            init = init_map.get(sid, 1.0)
            scores[sid] = init
            queue.append((sid, init, 0))

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
            if allowed_types is not None and edge_type not in allowed_types:
                continue
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
            if allowed_types is not None and edge_type not in allowed_types:
                continue
            w = (edge_weights or {}).get(edge_type, 1.0) if edge_weights else 1.0
            new_activation = activation * decay * w
            if new_activation > scores.get(source, 0.0):
                scores[source] = new_activation
                queue.append((source, new_activation, depth + 1))

    return scores


_ATTR_EXPANSION_WEIGHT: float = 0.5


def attribute_match(
    node: GraphNode,
    keywords: list[str],
    synonyms: dict[str, frozenset[str]] | None = None,
) -> float:
    """Keyword overlap ratio between node content and query keywords.

    When synonyms is provided, expands keywords with domain synonyms
    and stemming. Expanded terms contribute at 0.5x weight; denominator
    uses original keyword count to preserve scale.

    Returns:
        Float in [0.0, ...]. 0.0 if no keywords or all are stop words.
    """
    if not keywords:
        return 0.0
    content_kws = [kw for kw in keywords if kw.lower() not in STOP_WORDS]
    if not content_kws:
        return 0.0

    all_kws, _expanded = expand_keywords(content_kws, synonyms=synonyms)
    original_set = set(content_kws)
    content_lower = node.content.lower()

    score = 0.0
    for kw in all_kws:
        if kw.lower() in content_lower:
            score += 1.0 if kw in original_set else _ATTR_EXPANSION_WEIGHT
    return score / len(content_kws)


def composite_score(
    sa: float,
    attr: float,
    domain: float,
    sem: float = 0.0,
    weights: tuple[float, ...] = (W_SA, W_ATTR, W_DOMAIN, W_SEM),
) -> float:
    """Weighted sum of scoring signals (3 or 4).

    Accepts 3-tuple weights (backward compat) or 4-tuple weights.
    When 3-tuple, W_SEM defaults to 0.0 (sem signal ignored).
    """
    w_sa = weights[0]
    w_attr = weights[1]
    w_domain = weights[2]
    w_sem = weights[3] if len(weights) >= 4 else 0.0
    return w_sa * sa + w_attr * attr + w_domain * domain + w_sem * sem


# --- Orchestrator ---


def _keyword_search_fallback(graph: Graph, query: str) -> list[GraphNode]:
    """Fallback: scan all nodes for keyword matches.

    Uses extract_keywords() to drop stop words; falls back to raw tokens
    when the query is all stop words (degraded match beats no match).
    """
    keywords = extract_keywords(query) or query.lower().split()
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


def _candidate_union(
    graph: Graph,
    traversed: list[GraphNode],
    semantic_scorer: SemanticScorer,
    query: str,
    limit: int,
) -> list[GraphNode]:
    """Merge semantic candidates into the symbolic candidate list (no duplicates)."""
    searcher = getattr(semantic_scorer, "search_candidates", None)
    if searcher is None:
        return traversed
    try:
        sem_candidates: list[dict[str, Any]] = searcher(query, limit)
    except Exception:
        logger.warning("search_candidates failed, skipping candidate union")
        return traversed

    sym_ids = {n.id for n in traversed}
    for candidate in sem_candidates:
        nid = candidate["node_id"]
        if nid not in sym_ids:
            node = graph.get_concept(nid)
            if node is not None:
                traversed.append(node)
                sym_ids.add(nid)
    return traversed


def _score_candidates(
    annotated: list[ScoredNode],
    sa_scores: dict[str, float],
    keywords: list[str],
    sem_scores: dict[str, float],
    effective_weights: tuple[float, ...],
    has_scorer: bool,
    synonyms: dict[str, frozenset[str]] | None = None,
) -> list[ScoredNode]:
    """Compute composite scores for annotated candidates."""
    scored: list[ScoredNode] = []
    for sn in annotated:
        sa_val = sa_scores.get(sn.node.id, 0.0)
        attr_val = attribute_match(sn.node, keywords, synonyms=synonyms)
        domain_val = sn.score
        sem_val = sem_scores.get(sn.node.id, 0.0)
        final = composite_score(
            sa=sa_val,
            attr=attr_val,
            domain=domain_val,
            sem=sem_val,
            weights=effective_weights,
        )
        explanation = f"SA={sa_val:.2f}, attr={attr_val:.2f}, domain={domain_val:.2f}"
        if has_scorer:
            explanation += f", sem={sem_val:.2f}"
        scored.append(ScoredNode(node=sn.node, score=final, explanation=explanation))
    scored.sort(reverse=True)
    return scored


def retrieve(
    graph: Graph,
    query: str,
    adapter: DomainAdapter,
    top_k: int = 10,
    weights: tuple[float, ...] | None = None,
    semantic_scorer: SemanticScorer | None = None,
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

    # Step 3: traverse graph (symbolic candidates)
    if advice is not None:
        traversed = _traverse(graph, advice)
    else:
        traversed = _keyword_search_fallback(graph, query)

    # Step 3b: candidate union — add semantic candidates not found by symbolic path
    if semantic_scorer is not None:
        traversed = _candidate_union(
            graph, traversed, semantic_scorer, query, top_k * 2
        )

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

    # Step 5: composite scoring — SA + attr + domain + sem (when available)
    sa_scores = spreading_activation(
        graph,
        seed_ids=advice.start_node_ids if advice else [],
        max_depth=advice.max_depth if advice else 2,
        edge_weights=advice.edge_weights if advice and advice.edge_weights else None,
        edge_type_filter=(
            list(advice.edge_type_filter)
            if advice and advice.edge_type_filter is not None
            else None
        ),
        initial_activations=(
            advice.seed_activations if advice and advice.seed_activations else None
        ),
    )

    sem_scores: dict[str, float] = {}
    if semantic_scorer is not None:
        try:
            node_ids = [sn.node.id for sn in annotated]
            sem_scores = semantic_scorer.score_nodes(query, node_ids)
        except Exception:
            logger.warning("semantic_scorer.score_nodes failed, using zero scores")

    adapter_synonyms: dict[str, frozenset[str]] | None = getattr(
        adapter, "synonyms", None
    )
    scored = _score_candidates(
        annotated=annotated,
        sa_scores=sa_scores,
        keywords=extract_keywords(query),
        sem_scores=sem_scores,
        effective_weights=weights or (W_SA, W_ATTR, W_DOMAIN, W_SEM),
        has_scorer=semantic_scorer is not None,
        synonyms=adapter_synonyms,
    )
    return RetrievalResult(nodes=scored[:top_k], query=query, hints=hints)
