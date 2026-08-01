"""Evaluation harness runner — E2E pipeline from fixtures to EvalResult."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from raise_cli.eval._models import EvalResult
from raise_cli.eval.metrics import evaluate_run, evaluate_run_per_query
from raise_core.cartridges.ingest import (
    materialize_edges,
    materialize_reference_edges,
    materialize_structural_edges,
)
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode
from raise_core.graph.retrieval.engine import SemanticScorer, retrieve
from raise_core.graph.retrieval.models import (
    DomainHints,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.scorers import (
    SEM_ALPHA,
    HybridSemanticScorer,
    InMemorySemanticScorer,
)


class _EvalDomainAdapter:
    """Minimal domain adapter for evaluation — no domain-specific scoring."""

    def interpret_query(self, query: str) -> DomainHints:
        return DomainHints(domain="eval")

    def advise_traversal(
        self, hints: DomainHints, available_types: frozenset[str]
    ) -> TraversalAdvice:
        # Return None to trigger keyword_search_fallback in engine.py
        return None  # type: ignore[return-value]

    def annotate_results(
        self, nodes: list[GraphNode], hints: DomainHints
    ) -> list[ScoredNode]:
        return [
            ScoredNode(node=n, score=0.0, explanation="eval-adapter: no domain score")
            for n in nodes
        ]


class EvalSemanticScorer:
    """Dense-embedding scorer for eval — uses SentenceTransformerProvider.

    Pre-embeds the entire corpus at construction time so that score_nodes
    and search_candidates only compute query embedding + cosine similarity.
    """

    def __init__(self, corpus: list[dict[str, Any]]) -> None:
        from raise_core.cartridges.embedding import SentenceTransformerProvider

        self._provider = SentenceTransformerProvider()
        texts = [n.get("content", "") for n in corpus]
        ids = [n["id"] for n in corpus]
        vectors = self._provider.embed(texts)
        self._ids = ids
        self._vectors = vectors  # list[list[float]]
        self._id_to_idx: dict[str, int] = {nid: i for i, nid in enumerate(ids)}

    @staticmethod
    def _cosine_dense(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0
        return dot / (mag_a * mag_b)

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        qvec = self._provider.embed_query([query])[0]
        result: dict[str, float] = {}
        for nid in node_ids:
            idx = self._id_to_idx.get(nid)
            if idx is not None:
                result[nid] = self._cosine_dense(qvec, self._vectors[idx])
            else:
                result[nid] = 0.0
        return result

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by dense embedding cosine similarity."""
        qvec = self._provider.embed_query([query])[0]
        scored = [
            (nid, self._cosine_dense(qvec, self._vectors[idx]))
            for nid, idx in self._id_to_idx.items()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {"node_id": nid, "similarity": sim}
            for nid, sim in scored[:limit]
            if sim > 0.0
        ]


def _resolve_eval_scorer(
    corpus: list[dict[str, Any]],
    *,
    alpha: float | None = None,
) -> SemanticScorer:
    """Resolve evaluation scorer: TF-IDF always; Hybrid(tfidf, dense) when model available.

    Builds an ``InMemorySemanticScorer`` (TF-IDF, model-free, CI-safe) unconditionally.
    When ``sentence-transformers`` is available, wraps with ``EvalSemanticScorer`` (dense)
    in a ``HybridSemanticScorer``.  Falls back to TF-IDF-only on ``ImportError``.

    Args:
        corpus: List of node dicts with ``id`` and ``content`` fields.
        alpha: Hybrid weight for the TF-IDF component.  ``None`` → ``SEM_ALPHA``.

    Returns:
        A ``SemanticScorer`` instance — never ``None``.
    """
    effective_alpha = alpha if alpha is not None else SEM_ALPHA
    tfidf = InMemorySemanticScorer(corpus)
    try:
        dense = EvalSemanticScorer(corpus)
        return HybridSemanticScorer(tfidf, dense, alpha=effective_alpha)
    except ImportError:
        return tfidf


def _build_graph(
    corpus: list[dict[str, Any]],
    edges: list[dict[str, Any]] | None = None,
) -> Graph:
    """Build an in-memory Graph from corpus fixture nodes and optional edges."""
    graph = Graph()
    cartridges: set[str] = set()
    for node_data in corpus:
        node = GraphNode(
            id=node_data["id"],
            type=node_data.get("type", "concept"),
            content=node_data.get("content", ""),
            source_file=node_data.get("source_file"),
            created=node_data.get("created", "2026-01-01"),
            metadata=node_data.get("metadata", {}),
        )
        graph.add_concept(node)
        if cartridge := node_data.get("metadata", {}).get("cartridge"):
            cartridges.add(cartridge)

    node_ids = frozenset(graph.graph.nodes)
    for edge_data in edges or []:
        if edge_data["source"] in node_ids and edge_data["target"] in node_ids:
            graph.add_relationship(
                GraphEdge(
                    source=edge_data["source"],
                    target=edge_data["target"],
                    type=edge_data.get("type", "related_to"),
                    weight=edge_data.get("weight", 1.0),
                )
            )
    for cartridge_name in cartridges:
        materialize_edges(graph, cartridge_name)
        materialize_structural_edges(graph, cartridge_name)
        materialize_reference_edges(graph, cartridge_name)
    return graph


def _corpus_hash(corpus: list[dict[str, Any]]) -> str:
    """SHA256 hash of the corpus for versioning."""
    content = json.dumps(corpus, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def run_eval_impl(
    *,
    qrels: dict[str, dict[str, int]],
    corpus: list[dict[str, Any]],
    queries: dict[str, dict[str, Any]],
    suite: str = "cartridge",
    thresholds: dict[str, float] | None = None,
    weights: tuple[float, ...] | None = None,
    semantic_scorer: SemanticScorer | None = None,
    edges: list[dict[str, Any]] | None = None,
    use_cartridge_adapter: bool = False,
    metrics: list[str] | None = None,
) -> EvalResult:
    """Core evaluation runner.

    For each query in qrels, runs retrieve() against the corpus graph
    and builds a ranx.Run for scoring.

    With ``use_cartridge_adapter``, each query gets a GenericCartridgeAdapter
    scoped to its ``source_cartridge`` — this activates seeds, SA, and the
    domain signal, unlike the neutral eval adapter (SA=0, domain=0).
    """
    if semantic_scorer is None:
        semantic_scorer = _resolve_eval_scorer(corpus)
    graph = _build_graph(corpus, edges=edges)
    neutral_adapter = _EvalDomainAdapter()

    cartridges = sorted(
        {c for n in corpus if (c := n.get("metadata", {}).get("cartridge"))}
    )

    def _adapter_for(query_id: str) -> Any:
        if not use_cartridge_adapter or not cartridges:
            return neutral_adapter
        from raise_core.cartridges.adapter import GenericCartridgeAdapter
        from raise_core.cartridges.synonyms import load_synonyms

        src = queries.get(query_id, {}).get("source_cartridge", "")
        cart = src.split("+")[0] if src else cartridges[0]
        if cart not in cartridges:
            cart = cartridges[0]
        instances_dir = Path(".raise/cartridges") / cart / "instances"
        syns = load_synonyms(instances_dir) or None
        return GenericCartridgeAdapter(graph, cart, synonyms=syns)

    run: dict[str, dict[str, float]] = {}
    for query_id in qrels:
        query_text = queries.get(query_id, {}).get("text", query_id)
        result = retrieve(
            graph,
            query_text,
            _adapter_for(query_id),
            top_k=20,
            weights=weights,
            semantic_scorer=semantic_scorer,
        )
        scores = {sn.node.id: float(sn.score) for sn in result.nodes}
        if not scores:
            # ranx requires at least one doc per query — use a dummy with score 0
            scores = {"__no_result__": 0.0}
        run[query_id] = scores

    agg_metrics = evaluate_run(qrels, run, metrics=metrics)
    per_query = evaluate_run_per_query(qrels, run, metrics=metrics)

    return EvalResult(
        suite=suite,
        metrics=agg_metrics,
        per_query=per_query,
        num_queries=len(queries),
        corpus_hash=_corpus_hash(corpus),
        thresholds=thresholds,
    )


def run_federated_eval_impl(
    *,
    qrels: dict[str, dict[str, int]],
    corpus: list[dict[str, Any]],
    queries: dict[str, dict[str, Any]],
    suite: str = "federated",
    thresholds: dict[str, float] | None = None,
    metrics: list[str] | None = None,
) -> EvalResult:
    """Federated evaluation — faithful to the production orchestrator (RAISE-9415).

    Mirrors ``federated_retrieve_from_graph`` exactly: builds the corpus graph, uses
    ONE global semantic scorer, and runs the production path per query (per-cartridge
    ``retrieve()`` full pipeline → CombSUM score-preserving fusion → dedup → diversify).

    The previous implementation scored candidates with raw ``search_candidates`` cosine
    while the baseline ran the full ``retrieve()`` pipeline — an unfair comparison that
    manufactured a ~45% NDCG gap and a spurious −53% "federation regression" (RAISE-9415
    P5/P6). Scored like production, federation matches the global baseline (P6: G == A).
    """
    from raise_core.graph.retrieval.federation import federated_retrieve_from_graph

    graph = _build_graph(corpus)
    cartridges = sorted(
        {c for n in corpus if (c := n.get("metadata", {}).get("cartridge"))}
    )
    if cartridges:
        from raise_core.cartridges.adapter import GenericCartridgeAdapter
        from raise_core.cartridges.synonyms import load_synonyms

        instances_dir = Path(".raise/cartridges") / cartridges[0] / "instances"
        syns = load_synonyms(instances_dir) or None
        adapter: Any = GenericCartridgeAdapter(graph, cartridges[0], synonyms=syns)
    else:
        adapter = _EvalDomainAdapter()
    scorer: SemanticScorer = _resolve_eval_scorer(corpus)

    # Force federation on for the eval (the production default-OFF gate is a rollout
    # decision, not a measurement one). Restore the prior value afterwards.
    prev_flag = os.environ.get("RAISE_FEDERATION_ENABLED")
    os.environ["RAISE_FEDERATION_ENABLED"] = "1"
    try:
        run: dict[str, dict[str, float]] = {}
        for query_id in qrels:
            query_text = queries.get(query_id, {}).get("text", query_id)
            result = federated_retrieve_from_graph(
                graph, query_text, adapter, top_k=20, semantic_scorer=scorer
            )
            scores = {sn.node.id: float(sn.score) for sn in result.nodes}
            run[query_id] = scores or {"__no_result__": 0.0}
    finally:
        if prev_flag is None:
            os.environ.pop("RAISE_FEDERATION_ENABLED", None)
        else:
            os.environ["RAISE_FEDERATION_ENABLED"] = prev_flag

    agg_metrics = evaluate_run(qrels, run, metrics=metrics)
    per_query = evaluate_run_per_query(qrels, run, metrics=metrics)

    return EvalResult(
        suite=suite,
        metrics=agg_metrics,
        per_query=per_query,
        num_queries=len(queries),
        corpus_hash=_corpus_hash(corpus),
        thresholds=thresholds,
    )
