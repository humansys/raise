"""Domain-agnostic retrieval engine for knowledge graphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from raise_core.graph.retrieval.engine import (
    CandidateSearcher,
    SemanticScorer,
    attribute_match,
    composite_score,
    retrieve,
    spreading_activation,
)
from raise_core.graph.retrieval.models import (
    DomainAdapter,
    DomainHints,
    RetrievalResult,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.retrieval.text import STOP_WORDS, extract_keywords

if TYPE_CHECKING:
    from raise_core.graph.retrieval.dedup import (
        CanonicalEntry,
        CanonicalizationMap,
        DeduplicationMetrics,
        dedup_cross_cartridge,
    )
    from raise_core.graph.retrieval.federation import (
        FederatedCandidate,
        FederatedRetrievalResult,
        cross_partition_search,
        federated_retrieve,
        federated_retrieve_from_graph,
        rrf_merge,
    )
    from raise_core.graph.retrieval.normalization import (
        CartridgeHistogram,
        build_histogram,
        normalize_sa_scores,
        pit_normalize,
    )

__all__ = [
    "STOP_WORDS",
    "CanonicalEntry",
    "CandidateSearcher",
    "CanonicalizationMap",
    "CartridgeHistogram",
    "DeduplicationMetrics",
    "DomainAdapter",
    "DomainHints",
    "FederatedCandidate",
    "FederatedRetrievalResult",
    "RetrievalResult",
    "ScoredNode",
    "SemanticScorer",
    "TraversalAdvice",
    "attribute_match",
    "build_histogram",
    "composite_score",
    "cross_partition_search",
    "dedup_cross_cartridge",
    "extract_keywords",
    "federated_retrieve",
    "federated_retrieve_from_graph",
    "normalize_sa_scores",
    "pit_normalize",
    "retrieve",
    "rrf_merge",
    "spreading_activation",
]

_DEDUP_NAMES = frozenset(
    (
        "CanonicalEntry",
        "CanonicalizationMap",
        "DeduplicationMetrics",
        "dedup_cross_cartridge",
    )
)
_FEDERATION_NAMES = frozenset(
    (
        "FederatedCandidate",
        "FederatedRetrievalResult",
        "cross_partition_search",
        "federated_retrieve",
        "federated_retrieve_from_graph",
        "rrf_merge",
    )
)
_NORMALIZATION_NAMES = frozenset(
    ("CartridgeHistogram", "build_histogram", "normalize_sa_scores", "pit_normalize")
)


def __getattr__(name: str) -> object:
    if name in _DEDUP_NAMES:
        from raise_core.graph.retrieval import dedup

        globals()["CanonicalEntry"] = dedup.CanonicalEntry
        globals()["CanonicalizationMap"] = dedup.CanonicalizationMap
        globals()["DeduplicationMetrics"] = dedup.DeduplicationMetrics
        globals()["dedup_cross_cartridge"] = dedup.dedup_cross_cartridge
        return getattr(dedup, name)
    if name in _FEDERATION_NAMES:
        from raise_core.graph.retrieval import federation

        globals()["FederatedCandidate"] = federation.FederatedCandidate
        globals()["FederatedRetrievalResult"] = federation.FederatedRetrievalResult
        globals()["cross_partition_search"] = federation.cross_partition_search
        globals()["federated_retrieve"] = federation.federated_retrieve
        globals()["federated_retrieve_from_graph"] = (
            federation.federated_retrieve_from_graph
        )
        globals()["rrf_merge"] = federation.rrf_merge
        return getattr(federation, name)
    if name in _NORMALIZATION_NAMES:
        from raise_core.graph.retrieval import normalization

        globals()["CartridgeHistogram"] = normalization.CartridgeHistogram
        globals()["build_histogram"] = normalization.build_histogram
        globals()["normalize_sa_scores"] = normalization.normalize_sa_scores
        globals()["pit_normalize"] = normalization.pit_normalize
        return getattr(normalization, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
