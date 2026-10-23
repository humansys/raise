"""Federated query over cartridges with signal-weighted merge (soft routing).

Per-cartridge retrieval over the unified graph; each cartridge's composite
scores are damped by the cartridge's query signal before the global merge.
Keeps engine.py untouched — all federation logic lives here.

S-KC7.11: replaced rank-only RRF, which guaranteed every cartridge's rank-1
the same merged score regardless of relevance — on the union eval corpus it
degraded NDCG@10 by 51% vs flat retrieval (0.1572 vs 0.3235); soft routing
restores parity (0.3230) with MAP/P@5 above flat.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from raise_core.cartridges.adapter import GenericCartridgeAdapter
from raise_core.cartridges.loader import load_cartridge
from raise_core.cartridges.synonyms import load_synonyms
from raise_core.graph.engine import Graph
from raise_core.graph.retrieval.engine import attribute_match, retrieve
from raise_core.graph.retrieval.text import extract_keywords

if TYPE_CHECKING:
    # Structural Protocol — the canonical scorer contract that retrieve()
    # consumes and resolve_semantic_scorer() returns. Avoids a closed Union
    # of concrete classes that diverged from the downstream contract and
    # broke gate-types at the call site (RAISE-10268).
    from raise_core.graph.retrieval.engine import SemanticScorer

# Base directory for cartridge manifests (relative to CWD at runtime).
_CARTRIDGES_DIR: Path = Path(".raise/cartridges")

# Top-N attribute_match scores summed into a cartridge's query signal
_SIGNAL_TOP_N: int = 3


def _cartridge_dir(cartridge_name: str) -> Path:
    """Resolve the cartridge directory path from CWD (mirrors CLI convention)."""
    return _CARTRIDGES_DIR / cartridge_name


def _cartridge_synonyms(cartridge_name: str) -> dict[str, frozenset[str]] | None:
    """Load per-cartridge synonyms from instances/synonyms.json.

    Returns None (not {}) when missing — the adapter treats None as
    "no synonyms provided" which is semantically different from
    "synonyms provided but empty".
    """
    instances_dir = _cartridge_dir(cartridge_name) / "instances"
    result = load_synonyms(instances_dir)
    return result or None


def _profile_weights(cartridge_name: str) -> tuple[float, ...] | None:
    """Return per-cartridge weights tuple from the manifest retrieval_profile.

    Returns:
        4-tuple (w_sa, w_attr, w_domain, w_sem) if the manifest declares a
        retrieval_profile; None otherwise (engine uses global defaults).
        Silently returns None on any manifest load failure or missing profile —
        a corrupt on-disk CARTRIDGE.yaml degrades to global weights in
        production rather than crashing the query (D3 graceful degradation).
    """
    try:
        manifest, _ = load_cartridge(_cartridge_dir(cartridge_name))
    except Exception:
        return None
    p = manifest.retrieval_profile
    if p is None:
        return None
    return p.to_weights()


class FederatedResult(BaseModel):
    """A single result from federated query with source attribution."""

    node_id: str = Field(..., description="Graph node ID")
    cartridge: str = Field(..., description="Source cartridge name")
    score: float = Field(..., description="Signal-weighted composite score")
    content: str = Field(..., description="Node content")
    node_type: str = Field(default="", description="Node type")


def _cartridge_signal(graph: Graph, cartridge: str, keywords: list[str]) -> float:
    """Query signal for a cartridge: sum of its top-N attribute_match scores."""
    top = sorted(
        (
            attribute_match(node, keywords)
            for node in graph.iter_concepts()
            if node.metadata.get("cartridge") == cartridge
        ),
        reverse=True,
    )[:_SIGNAL_TOP_N]
    return sum(top)


def _cartridge_matches_org(cartridge: str, org_ids: list[str]) -> bool:
    """True if the cartridge name starts with backlog-{org_id}- for any org in org_ids."""
    return any(cartridge.startswith(f"backlog-{org_id}-") for org_id in org_ids)


def federated_query(
    graph: Graph,
    query: str,
    limit: int = 10,
    per_cartridge_limit: int = 10,
    org_ids: list[str] | None = None,
    cartridge_types: list[str] | None = None,
    semantic_scorer: SemanticScorer | None = None,
) -> list[FederatedResult]:
    """Per-cartridge query + signal-weighted merge (soft routing).

    Partitions graph by metadata.cartridge, runs retrieve() per-cartridge
    with GenericCartridgeAdapter, scales each cartridge's composite scores
    by signal/max_signal, then merges globally. Zero-signal cartridges are
    skipped — unless no cartridge has signal, where federation degrades to
    an unweighted score merge (fallback-seed results stay reachable).

    Args:
        graph: Unified knowledge graph to query.
        query: Natural language query string.
        limit: Max total results across all cartridges.
        per_cartridge_limit: Max results per cartridge before merge.
        org_ids: If set, restrict to backlog cartridges from these org IDs.
            Convention: cartridge name ``backlog-{org_id}-{project_key}``.
            Empty list returns no results. None = no filter (all orgs).
        cartridge_types: If set, restrict final results to nodes with these
            node types. Applied after federation merge (post-filter).
        semantic_scorer: Optional scorer propagated to each per-cartridge
            retrieve() call. None (default) = keyword-only fallback (AC1).
    """
    if org_ids is not None and len(org_ids) == 0:
        return []

    cartridge_names: set[str] = set()
    for node in graph.iter_concepts():
        cartridge = node.metadata.get("cartridge")
        if cartridge:
            cartridge_names.add(cartridge)

    # ADR-113: org_ids boundary — filter to cartridges matching allowed orgs
    if org_ids is not None:
        cartridge_names = {
            name for name in cartridge_names if _cartridge_matches_org(name, org_ids)
        }

    if not cartridge_names:
        return []

    keywords = extract_keywords(query) or query.lower().split()
    signals = {
        name: _cartridge_signal(graph, name, keywords)
        for name in sorted(cartridge_names)
    }
    max_signal = max(signals.values())

    all_results: list[FederatedResult] = []
    for name in sorted(cartridge_names):
        weight = signals[name] / max_signal if max_signal > 0 else 1.0
        if weight <= 0.0:
            continue
        adapter = GenericCartridgeAdapter(
            graph, cartridge_name=name, synonyms=_cartridge_synonyms(name)
        )
        result = retrieve(
            graph=graph,
            query=query,
            adapter=adapter,
            top_k=per_cartridge_limit,
            weights=_profile_weights(name),
            semantic_scorer=semantic_scorer,
        )
        for scored_node in result.nodes:
            all_results.append(
                FederatedResult(
                    node_id=scored_node.node.id,
                    cartridge=name,
                    score=scored_node.score * weight,
                    content=scored_node.node.content,
                    node_type=scored_node.node.type,
                )
            )

    all_results.sort(key=lambda r: r.score, reverse=True)

    # ADR-113: cartridge_types post-filter — restrict to specific node types
    if cartridge_types is not None:
        all_results = [r for r in all_results if r.node_type in cartridge_types]

    return all_results[:limit]
