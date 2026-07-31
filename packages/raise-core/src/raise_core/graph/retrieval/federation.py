"""Federated retrieval: fan-out, RRF merge, and orchestration across cartridges.

Provides cross_partition_search() for parallel fan-out, rrf_merge() for
Reciprocal Rank Fusion, and federated_retrieve() as the full orchestrator
integrating dedup (I.2), fan-out+RRF (I.3), and PIT normalization (I.4).

Design decisions: ADR-100 (Embedding Federation Architecture).
"""

# drift: ignore — orquestador que cita legítimamente los ADRs de federación
# (ADR-100/103) y su linaje de historias; densidad de story-tokens = diseño,
# no accretion. Exención pre-existente (drift-story-accretion CAND-05).

from __future__ import annotations

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt

    from raise_core.graph.engine import Graph
    from raise_core.graph.retrieval.dedup import (
        CanonicalizationMap,
        DeduplicationMetrics,
    )
    from raise_core.graph.retrieval.engine import SemanticScorer
    from raise_core.graph.retrieval.models import (
        DomainAdapter,
        RetrievalResult,
        SemanticResult,
    )
    from raise_core.graph.retrieval.normalization import CartridgeHistogram

logger = logging.getLogger(__name__)

__all__ = [
    "FederatedCandidate",
    "FederatedRetrievalResult",
    "combsum_merge",
    "cross_partition_search",
    "diversify_results",
    "federated_retrieve",
    "federated_retrieve_from_graph",
    "rrf_merge",
]


@dataclass(frozen=True, slots=True)
class FederatedCandidate:
    """A merged semantic candidate after RRF fusion across cartridges."""

    node_id: str
    rrf_score: float
    source_cartridge: str  # cartridge with highest cosine similarity
    source_type: str  # always "semantic" in S-RFCC.I.3
    similarity: float  # highest cosine similarity across cartridges


def rrf_merge(
    per_cartridge: dict[str, list[SemanticResult]],
    k: int = 60,
    limit: int = 20,
) -> list[FederatedCandidate]:
    """Merge per-cartridge semantic results using Reciprocal Rank Fusion.

    Formula: score(node) = sum over cartridges of 1 / (k + rank),
    where rank is 1-based within each cartridge's ordered list.

    Dedup rule: when the same node_id appears in multiple cartridges,
    accumulate the RRF score and keep source_cartridge = the one with
    highest cosine similarity.

    Args:
        per_cartridge: Mapping of cartridge_name → ordered list of SemanticResults.
        k: RRF constant (default 60). Lower values amplify rank differences.
        limit: Maximum number of results to return.

    Returns:
        List of FederatedCandidate sorted by rrf_score descending, capped at limit.
    """
    if not per_cartridge:
        return []

    # Accumulator: node_id → (rrf_score, source_cartridge, source_similarity)
    accumulated: dict[str, tuple[float, str, float]] = {}

    for cartridge_name, results in per_cartridge.items():
        for rank_0based, result in enumerate(results):
            rank = rank_0based + 1  # 1-based
            score_contribution = 1.0 / (k + rank)
            nid = result.node_id
            sim = result.similarity

            if nid not in accumulated:
                accumulated[nid] = (score_contribution, cartridge_name, sim)
            else:
                prev_score, prev_cartridge, prev_sim = accumulated[nid]
                new_score = prev_score + score_contribution
                # Keep source_cartridge with highest cosine similarity
                if sim > prev_sim:
                    accumulated[nid] = (new_score, cartridge_name, sim)
                else:
                    accumulated[nid] = (new_score, prev_cartridge, prev_sim)

    if not accumulated:
        return []

    candidates = [
        FederatedCandidate(
            node_id=nid,
            rrf_score=rrf_score,
            source_cartridge=src_cart,
            source_type="semantic",
            similarity=sim,
        )
        for nid, (rrf_score, src_cart, sim) in accumulated.items()
    ]

    candidates.sort(key=lambda c: c.rrf_score, reverse=True)
    return candidates[:limit]


def combsum_merge(
    per_cartridge: dict[str, list[SemanticResult]],
    limit: int = 20,
) -> list[FederatedCandidate]:
    """Score-preserving fusion: sum per-cartridge similarities, keep best source.

    Formula: score(node) = sum over cartridges of similarity(node), with
    source_cartridge = the cartridge giving the highest cosine similarity.

    Unlike :func:`rrf_merge` (rank-based, discards magnitude — the proven regressor,
    RAISE-9415 P6: −18% NDCG/recall on a fair baseline), CombSUM preserves score
    magnitude. When partitions are **disjoint** and fan-out shares one scorer, each
    node hits exactly one cartridge, so the fused score equals the node's own
    similarity — i.e. the fused ranking is identical to ranking the whole corpus by
    similarity. This is why CombSUM recovers the global baseline exactly (P6: G == A).

    Args:
        per_cartridge: Mapping of cartridge_name → ordered SemanticResult list.
        limit: Maximum number of results to return.

    Returns:
        List of FederatedCandidate sorted by fused score descending, capped at
        limit. The ``rrf_score`` field carries the CombSUM score (name retained to
        avoid churning downstream consumers).
    """
    if not per_cartridge:
        return []

    score_sum: dict[str, float] = {}
    best: dict[str, tuple[str, float]] = {}  # node_id → (cartridge, similarity)
    for cartridge_name, results in per_cartridge.items():
        for result in results:
            nid = result.node_id
            score_sum[nid] = score_sum.get(nid, 0.0) + result.similarity
            if nid not in best or result.similarity > best[nid][1]:
                best[nid] = (cartridge_name, result.similarity)

    candidates = [
        FederatedCandidate(
            node_id=nid,
            rrf_score=score_sum[nid],
            source_cartridge=best[nid][0],
            source_type="semantic",
            similarity=best[nid][1],
        )
        for nid in score_sum
    ]
    candidates.sort(key=lambda c: c.rrf_score, reverse=True)
    return candidates[:limit]


def cross_partition_search(
    query_embedding: npt.NDArray[np.float32],
    cartridge_indexes: dict[str, Any],  # dict[str, NumpySemanticSearch]
    limit: int = 20,
    rrf_k: int = 60,
) -> list[FederatedCandidate]:
    """Fan-out semantic search across cartridges, then RRF-merge results.

    Executes search_by_vector() on each cartridge index in parallel using
    ThreadPoolExecutor. GIL is released during numpy operations, so threads
    provide genuine parallelism for CPU-bound cosine similarity.

    Args:
        query_embedding: Pre-computed query embedding vector.
        cartridge_indexes: Mapping of cartridge_name → NumpySemanticSearch instance.
        limit: Top-K results to return after merge.
        rrf_k: RRF constant (default 60).

    Returns:
        List of FederatedCandidate sorted by rrf_score descending, capped at limit.
    """
    if not cartridge_indexes:
        return []

    query_list = query_embedding.tolist()
    max_workers = min(len(cartridge_indexes), 8)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            name: pool.submit(index.search_by_vector, query_list, limit)
            for name, index in cartridge_indexes.items()
        }
        per_cartridge: dict[str, list[SemanticResult]] = {
            name: future.result() for name, future in futures.items()
        }

    return rrf_merge(per_cartridge, k=rrf_k, limit=limit)


@dataclass(frozen=True, slots=True)
class FederatedRetrievalResult:
    """Output of the federated retrieval orchestrator."""

    candidates: list[FederatedCandidate]
    dedup_metrics: DeduplicationMetrics
    canonicalization_map: CanonicalizationMap
    sa_normalized: bool
    diversification_applied: int
    processing_time_ms: float


def _round_robin_interleave(
    by_cart: dict[str, list[FederatedCandidate]],
    total: int,
) -> list[FederatedCandidate]:
    """Round-robin interleave candidates from multiple cartridge groups."""
    cart_order = sorted(by_cart, key=lambda k: by_cart[k][0].rrf_score, reverse=True)
    interleaved: list[FederatedCandidate] = []
    iterators = {k: iter(by_cart[k]) for k in cart_order}
    exhausted: set[str] = set()
    while len(interleaved) < total:
        if len(exhausted) == len(cart_order):
            break
        for cart in cart_order:
            if cart in exhausted:
                continue
            nxt = next(iterators[cart], None)
            if nxt is None:
                exhausted.add(cart)
                continue
            interleaved.append(nxt)
            if len(interleaved) >= total:
                break
    return interleaved


def diversify_results(
    candidates: list[FederatedCandidate],
    top_k: int = 10,
) -> tuple[list[FederatedCandidate], int]:
    """Interleave candidates when one cartridge dominates the top-K.

    If >50% of the top-K candidates come from the same cartridge,
    round-robin interleave by source_cartridge to promote diversity.
    Preserves all candidates (moves, never removes).

    Args:
        candidates: Ranked candidates (descending score).
        top_k: Window size for dominance check.

    Returns:
        (reordered_candidates, number_of_moves)
    """
    if len(candidates) <= 1:
        return candidates, 0

    window = candidates[:top_k]
    cart_counts: dict[str, int] = {}
    for c in window:
        cart_counts[c.source_cartridge] = cart_counts.get(c.source_cartridge, 0) + 1

    if len(cart_counts) <= 1:
        return candidates, 0

    dominant_count = max(cart_counts.values())
    if dominant_count <= len(window) // 2:
        return candidates, 0

    by_cart: dict[str, list[FederatedCandidate]] = {}
    for c in window:
        by_cart.setdefault(c.source_cartridge, []).append(c)

    interleaved = _round_robin_interleave(by_cart, len(window))
    moves = sum(
        1
        for orig, new in zip(window, interleaved, strict=True)
        if orig.node_id != new.node_id
    )

    tail = candidates[top_k:]
    return interleaved + tail, moves


def federated_retrieve(
    per_cartridge_results: dict[str, list[SemanticResult]],
    node_texts: dict[str, str],
    embeddings: dict[str, npt.NDArray[np.float32]] | None = None,
    histograms: dict[str, CartridgeHistogram] | None = None,
    sa_scores: dict[str, dict[str, float]] | None = None,
    rrf_k: int = 60,
    cosine_threshold: float = 0.92,
    limit: int = 10,
    diversify: bool = False,
) -> FederatedRetrievalResult:
    """Orchestrate federated retrieval: RRF → dedup → PIT normalize → rank.

    Pipeline:
      1. RRF merge per-cartridge semantic results
      2. Cross-cartridge dedup (hash + optional cosine)
      3. PIT-normalize SA scores per cartridge (if provided)
      4. Re-sort by composite score (rrf + normalized SA)
      5. Apply limit (diversify first, only when explicitly requested)

    Args:
        per_cartridge_results: Cartridge name → ordered SemanticResult list.
        node_texts: Node ID → text content (for hash dedup).
        embeddings: Optional node ID → embedding vector (for cosine dedup).
        histograms: Optional cartridge name → CartridgeHistogram (for PIT).
        sa_scores: Optional cartridge name → {node_id: raw_sa_score}.
        rrf_k: RRF constant (default 60).
        cosine_threshold: Cosine similarity threshold for dedup (default 0.92).
        limit: Maximum results to return.
        diversify: When ``True``, forcibly interleave results when one
            cartridge dominates the top-K (see :func:`diversify_results`).
            Default ``False`` — relevance-pure ranking (RAISE-9757: forcing
            this unconditionally diluted legitimately-dominant results with
            lower-relevance cross-cartridge nodes on every federated query).

    Returns:
        FederatedRetrievalResult with candidates, metrics, and timing.
    """
    from raise_core.graph.retrieval.dedup import dedup_cross_cartridge
    from raise_core.graph.retrieval.normalization import pit_normalize

    start = time.perf_counter()

    # Step 1: score-preserving CombSUM fusion (RAISE-9415 P6 — replaces RRF, which
    # discarded magnitude and cost −18% NDCG/recall on a fair baseline). rrf_k is kept
    # in the signature for backward compatibility but is no longer used by the merge.
    _ = rrf_k
    merged = combsum_merge(per_cartridge_results, limit=limit * 5)

    # Step 2: cross-cartridge dedup
    deduped, canon_map, dedup_metrics = dedup_cross_cartridge(
        merged, node_texts, embeddings=embeddings, cosine_threshold=cosine_threshold
    )

    # Step 3: PIT-normalize SA and re-score
    sa_normalized = False
    if sa_scores and histograms:
        sa_normalized = True
        sa_weight = 0.3
        rescored: list[FederatedCandidate] = []
        for cand in deduped:
            cart_sa = sa_scores.get(cand.source_cartridge, {})
            raw_sa = cart_sa.get(cand.node_id, 0.0)
            hist = histograms.get(cand.source_cartridge)
            norm_sa = pit_normalize(raw_sa, hist)
            new_score = cand.rrf_score + sa_weight * norm_sa
            rescored.append(
                FederatedCandidate(
                    node_id=cand.node_id,
                    rrf_score=new_score,
                    source_cartridge=cand.source_cartridge,
                    source_type=cand.source_type,
                    similarity=cand.similarity,
                )
            )
        rescored.sort(key=lambda c: c.rrf_score, reverse=True)
        deduped = rescored

    # Step 4: diversify (opt-in only, RAISE-9757) + apply limit
    if diversify:
        diversified, div_count = diversify_results(deduped, top_k=limit)
    else:
        diversified, div_count = deduped, 0
    final = diversified[:limit]

    elapsed_ms = (time.perf_counter() - start) * 1000

    return FederatedRetrievalResult(
        candidates=final,
        dedup_metrics=dedup_metrics,
        canonicalization_map=canon_map,
        sa_normalized=sa_normalized,
        diversification_applied=div_count,
        processing_time_ms=elapsed_ms,
    )


# ---------------------------------------------------------------------------
# Production orchestration layer — ADR-103
# ---------------------------------------------------------------------------

_DEFAULT_CARTRIDGE = "default"

# Default-OFF gate (S-RFCC.W.4, decision per ADR-103 measurement gate):
# E-RFCC.R/synthesis.md DD-2 prescribed PIT-global + CombMNZ for terminal fusion and
# flagged pure RRF as a known regressor (−51% NDCG, S-KC7.11). The .4 A/B confirmed RRF
# fusion regresses retrieval on the federated fixtures. CombSUM with a shared scorer
# passes the QAS gate (BEIR tier-1, RAISE-9416 NDCG@10 Δ≈0), so federation is now ON
# by default (ADR-100). Set RAISE_FEDERATION_ENABLED=0 to opt out.
_FEDERATION_ENV = "RAISE_FEDERATION_ENABLED"
_TRUTHY = frozenset({"1", "true", "yes", "on"})
_FALSY = frozenset({"0", "false", "no", "off"})


def _federation_enabled() -> bool:
    """Return True unless ``RAISE_FEDERATION_ENABLED`` is explicitly falsy (default ON)."""
    val = os.environ.get(_FEDERATION_ENV, "").strip().lower()
    return val not in _FALSY


# Overfetch per cartridge before RRF fusion (ADR-103 A1 starvation mitigation):
# pull more than top_k from each cartridge so small cartridges still contribute
# candidates that a shared scorer's global top-N would otherwise crowd out.
# .4's eval gate may tune these against the per-cartridge-scorer baseline.
_OVERFETCH_FACTOR = 2
_MIN_OVERFETCH = 20


def _group_by_cartridge(graph: Graph) -> dict[str, list[str]]:
    """Group graph concept IDs by their ``metadata.cartridge`` tag.

    Nodes without a cartridge tag collapse into a single ``_DEFAULT_CARTRIDGE``
    group, matching the harness ``_partition_by_cartridge`` convention.
    """
    groups: dict[str, list[str]] = {}
    for node in graph.iter_concepts():
        cartridge = (node.metadata or {}).get("cartridge", _DEFAULT_CARTRIDGE)
        groups.setdefault(cartridge, []).append(node.id)
    return groups


def _cartridge_subgraph(graph: Graph, node_ids: list[str]) -> Graph:
    """Build a Graph restricted to ``node_ids`` (induced subgraph, edges kept)."""
    from raise_core.graph.engine import Graph as _Graph

    sub = _Graph()
    sub.graph = cast("Any", graph.graph.subgraph(node_ids).copy())
    return sub


def federated_retrieve_from_graph(
    graph: Graph,
    query: str,
    adapter: DomainAdapter,
    top_k: int = 10,
    semantic_scorer: SemanticScorer | None = None,
    rrf_k: int = 60,
    diversify: bool = False,
) -> RetrievalResult:
    """Cartridge-aware retrieval orchestrator (ADR-103, ADR-100) — drop-in for retrieve().

    Federation is **default-ON** (CombSUM passed QAS gate — RAISE-9416, ADR-100). Set
    ``RAISE_FEDERATION_ENABLED=0`` to disable. When enabled, it enumerates cartridges
    in the graph by ``metadata.cartridge``:

    - **≤1 cartridge** → delegates to :func:`retrieve` unchanged (clean fallback,
      no behavior change for single-cartridge repos).
    - **>1 cartridge** → runs :func:`retrieve` per cartridge over an induced
      subgraph (shared ``semantic_scorer`` with overfetch — ADR-103 A1), fuses the
      per-cartridge rankings via :func:`federated_retrieve` (CombSUM → dedup →
      diversify, when opted in), and maps the surviving candidates back to
      ``ScoredNode``.

    Args:
        graph: Loaded knowledge graph (nodes tagged with ``metadata.cartridge``).
        query: Natural-language query.
        adapter: Domain adapter (neutral in production callers).
        top_k: Number of results to return.
        semantic_scorer: Optional shared semantic scorer.
        rrf_k: RRF constant forwarded to :func:`federated_retrieve` (default 60).
        diversify: Forwarded to :func:`federated_retrieve`. Default ``False`` —
            relevance-pure ranking is the production default (RAISE-9757); this
            is the PRIME hot path (``query_backend.query`` → ``hint_oracle``),
            so the change is default-off, opt-in only.

    Returns:
        A ``RetrievalResult`` — identical shape to :func:`retrieve`.
    """
    from raise_core.graph.retrieval.engine import retrieve
    from raise_core.graph.retrieval.models import (
        RetrievalResult,
        ScoredNode,
        SemanticResult,
    )

    # RAISE-11749: reset any reachability latch the scorer holds ONCE per
    # query, before any early return. This scopes the ServerSemanticScorer
    # ``_unreachable`` memo to exactly one query and — critically — keeps the
    # single-cartridge and RAISE_FEDERATION_ENABLED=0 fallback paths
    # self-healing: those route through retrieve() without the per-cartridge
    # loop, so a reset placed only before the loop would leave a long-lived
    # singleton (hint_oracle._backend) latched forever after one transient
    # failure. Safe no-op for scorers that don't implement reset().
    scorer_reset = getattr(semantic_scorer, "reset", None)
    if callable(scorer_reset):
        scorer_reset()

    # Default-ON gate (ADR-100): disable via RAISE_FEDERATION_ENABLED=0.
    if not _federation_enabled():
        return retrieve(
            graph, query, adapter, top_k=top_k, semantic_scorer=semantic_scorer
        )

    groups = _group_by_cartridge(graph)

    # Fallback: 0 or 1 cartridge → federation does not apply.
    if len(groups) <= 1:
        return retrieve(
            graph, query, adapter, top_k=top_k, semantic_scorer=semantic_scorer
        )

    # Per-cartridge retrieval over induced subgraphs (deterministic order).
    overfetch = max(top_k * _OVERFETCH_FACTOR, _MIN_OVERFETCH)
    per_cartridge: dict[str, list[SemanticResult]] = {}
    node_texts: dict[str, str] = {}
    for cartridge in sorted(groups):
        subgraph = _cartridge_subgraph(graph, groups[cartridge])
        sub_result = retrieve(
            subgraph,
            query,
            adapter,
            top_k=overfetch,
            semantic_scorer=semantic_scorer,
        )
        per_cartridge[cartridge] = [
            SemanticResult(node_id=sn.node.id, similarity=sn.score)
            for sn in sub_result.nodes
        ]
        for sn in sub_result.nodes:
            node_texts[sn.node.id] = sn.node.content

    fused = federated_retrieve(
        per_cartridge_results=per_cartridge,
        node_texts=node_texts,
        rrf_k=rrf_k,
        limit=top_k,
        diversify=diversify,
    )

    # Map FederatedCandidate → ScoredNode; drop candidates absent from the graph.
    scored: list[ScoredNode] = []
    for cand in fused.candidates:
        node = graph.get_concept(cand.node_id)
        if node is None:
            logger.debug("federated candidate %s not in graph — dropping", cand.node_id)
            continue
        scored.append(
            ScoredNode(
                node=node,
                score=cand.rrf_score,
                explanation=(
                    f"federated combsum={cand.rrf_score:.4f} "
                    f"cartridge={cand.source_cartridge}"
                ),
                source_cartridge=cand.source_cartridge,
            )
        )

    return RetrievalResult(nodes=scored, query=query)
