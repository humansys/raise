"""GenericCartridgeAdapter — zero-config DomainAdapter for any cartridge.

First production implementation of the DomainAdapter protocol (PAT-E-2128).
Receives graph + cartridge_name at construction to resolve the seeding gap
(the Protocol's advise_traversal signature has no graph access).
"""

from __future__ import annotations

import math

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode
from raise_core.graph.retrieval.models import (
    DomainHints,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.retrieval.text import STOP_WORDS as _STOP_WORDS
from raise_core.graph.retrieval.text import expand_keywords

# Seed cap. SA is quantized ({1.0, 0.5, 0.25} at decay 0.5 / depth 2), so a
# flat seed set floods the top bucket and kills W_SA discrimination. The fix
# for that is per-seed weighting (see seed_activations in advise_traversal),
# NOT cutting the seed count: full-metric E-BENCH-R (RAISE-10254) showed an
# aggressive cap (~5) lifts nDCG@10 but regresses precision@5 below gate floors
# on management-ontology and raise-dev-workflow, and the seed-count optimum is
# non-monotonic and per-cartridge. Tuning the count is therefore deferred to
# E-BENCH-G (RAISE-10230); the universal default keeps the original cap.
_MAX_SEEDS: int = 20
_FALLBACK_SEEDS: int = 10

# SA damping for membership edges — symbol→module hubs (degree ~200) flood
# spreading activation with uniform scores when traversed at full weight
DEFAULT_EDGE_WEIGHTS: dict[str, float] = {"belongs_to": 0.1}

# IDF threshold: keywords matching >15% of corpus nodes are near-stop-words
_HIGH_FREQ_THRESHOLD: float = 0.15
_HIGH_FREQ_IDF: float = 0.1


def _compute_idf(
    all_keywords: list[str],
    cartridge_nodes: list[GraphNode],
) -> dict[str, float]:
    """Compute IDF² weights for keywords against cartridge corpus."""
    n_docs = len(cartridge_nodes) or 1
    df: dict[str, int] = dict.fromkeys(all_keywords, 0)
    for node in cartridge_nodes:
        content = node.content.lower()
        for kw in all_keywords:
            if kw in content:
                df[kw] += 1

    idf: dict[str, float] = {}
    for kw, freq in df.items():
        if freq == 0:
            idf[kw] = 0.0
        elif freq / n_docs > _HIGH_FREQ_THRESHOLD:
            idf[kw] = _HIGH_FREQ_IDF
        else:
            raw = math.log((n_docs + 1) / (freq + 1))
            idf[kw] = raw * raw
    return idf


def _score_seeds(
    cartridge_nodes: list[GraphNode],
    all_keywords: list[str],
    original_set: set[str],
    idf: dict[str, float],
    expansion_weight: float,
    graph: Graph,
) -> tuple[list[tuple[float, int, str]], list[str]]:
    """Score each node by IDF-weighted keyword overlap, return matches + fallback."""
    matches: list[tuple[float, int, str]] = []
    fallback: list[str] = []

    for node in cartridge_nodes:
        if all_keywords:
            content = node.content.lower()
            score = 0.0
            for kw in all_keywords:
                if kw in content:
                    exp_w = 1.0 if kw in original_set else expansion_weight
                    score += exp_w * idf.get(kw, 1.0)
            if score > 0:
                connected = 1 if graph.graph.degree(node.id) > 0 else 0
                matches.append((score, connected, node.id))
                continue
        if len(fallback) < _FALLBACK_SEEDS:
            fallback.append(node.id)

    matches.sort(key=lambda m: (-m[0], -m[1], m[2]))
    return matches, fallback


class GenericCartridgeAdapter:
    """Zero-config adapter for any cartridge.

    Implements DomainAdapter protocol:
    - interpret_query → DomainHints with domain=cartridge_name
    - advise_traversal → keyword-ranked seeds from cartridge nodes
    - annotate_results → uniform 0.5 score (SA + attr do the real work)
    """

    _EXPANSION_WEIGHT: float = 0.5

    def __init__(
        self,
        graph: Graph,
        cartridge_name: str,
        synonyms: dict[str, frozenset[str]] | None = None,
    ) -> None:
        self._graph = graph
        self._cartridge_name = cartridge_name
        self.synonyms = synonyms

    def interpret_query(self, query: str) -> DomainHints:
        """Parse query into domain hints, storing query for advise_traversal."""
        hints = DomainHints(domain=self._cartridge_name)
        hints.query = query  # type: ignore[attr-defined]
        return hints

    def advise_traversal(
        self, hints: DomainHints, available_types: frozenset[str]
    ) -> TraversalAdvice:
        """Produce keyword-ranked seeds from cartridge-scoped nodes.

        Matches are ranked by IDF²-weighted keyword score; connected nodes
        (degree > 0) win ties so spreading activation has edges to propagate
        over (S-KC7.6 — insertion-order seeding left SA dead).

        Keywords are expanded with per-cartridge domain synonyms and basic
        stemming so that generic vocabulary bridges to domain terms.
        """
        query: str = getattr(hints, "query", "")
        raw_keywords = [
            kw.strip("?!.,;:\"'()") for kw in query.lower().split() if query
        ]
        raw_keywords = [kw for kw in raw_keywords if kw]
        keywords = [kw for kw in raw_keywords if kw not in _STOP_WORDS]
        if not keywords:
            keywords = raw_keywords

        all_keywords, _expanded = expand_keywords(keywords, synonyms=self.synonyms)
        original_set = set(keywords)

        cartridge_nodes = [
            n
            for n in self._graph.iter_concepts()
            if n.metadata.get("cartridge") == self._cartridge_name
        ]

        idf = _compute_idf(all_keywords, cartridge_nodes)
        matches, fallback = _score_seeds(
            cartridge_nodes,
            all_keywords,
            original_set,
            idf,
            self._EXPANSION_WEIGHT,
            self._graph,
        )

        top = matches[:_MAX_SEEDS]
        seeds = [node_id for _, _, node_id in top]
        denom = len(keywords) or 1
        seed_activations = {node_id: count / denom for count, _, node_id in top}
        if not seeds:
            seeds = fallback
            seed_activations = {}

        return TraversalAdvice(
            start_node_ids=seeds,
            max_depth=2,
            edge_weights=dict(DEFAULT_EDGE_WEIGHTS),
            seed_activations=seed_activations,
        )

    def annotate_results(
        self, nodes: list[GraphNode], hints: DomainHints
    ) -> list[ScoredNode]:
        """Uniform scoring — SA + attribute match do the real discrimination."""
        return [
            ScoredNode(node=n, score=0.5, explanation="generic-uniform") for n in nodes
        ]
