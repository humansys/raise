"""DDD BC discovery engine — static-only, Python-first.

RAISE-16761: Proposes Bounded Contexts from Domain-classified symbols using
two static signals only:
  1. module_colocation — symbols sharing the same module → same BC candidate
  2. import_coupling   — CALLS/inherits_from edges between modules → merge BCs

No LLM, no co-change history. Designed as the baseline suggestion loop that
an architect reviews before ratifying into domain-model.yaml.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from raise_core.graph.engine import Graph
from raise_core.graph.models import SymbolNode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

# Two modules are merged when their cross-module call count exceeds this value.
# Exposed as a parameter in _cluster_modules for testability.
DEFAULT_MERGE_THRESHOLD: int = 3

# Coupling density ratio above which we downgrade confidence.
# ratio = total_inter_calls / max(1, total_possible_inter_calls)
_HIGH_CONFIDENCE_MAX_RATIO: float = 0.10  # ≤10% inter → high
_MEDIUM_CONFIDENCE_MAX_RATIO: float = 0.40  # ≤40% inter → medium; else low

_COUPLING_EDGE_TYPES: frozenset[str] = frozenset({"calls", "inherits_from"})

# ---------------------------------------------------------------------------
# Per-cluster confidence constants (RAISE-16789)
# ---------------------------------------------------------------------------

D_RATIO_WEIGHT: float = 0.6
COHESION_WEIGHT: float = 0.4
SPLIT_CANDIDATE_THRESHOLD: float = 0.15

# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class ClusterConfidence(BaseModel):
    """Decomposed per-cluster confidence components (RAISE-16789)."""

    confidence: float = Field(ge=0.0, le=1.0)
    d_ratio: float = Field(ge=0.0, le=1.0)
    cohesion: float = Field(ge=0.0, le=1.0)


NameSource = Literal["static", "llm_suggested", "ratified"]


class BCSuggestion(BaseModel):
    """A single Bounded Context proposal from the static discovery engine."""

    name: str
    symbols: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    d_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    cohesion: float = Field(default=0.0, ge=0.0, le=1.0)
    split_candidate: bool = False
    name_source: NameSource = "static"
    description: str | None = None


class BCDiscoveryResult(BaseModel):
    """Complete result of a BC discovery run."""

    bc_suggestions: list[BCSuggestion]
    confidence: Literal["high", "medium", "low"]
    signal_sources: list[str]
    run_artifact: Path
    overall_confidence: float = 0.0


class ThresholdSweepStep(BaseModel):
    """One step of a threshold sweep — captures BC count and stability at a given threshold."""

    threshold: int
    bc_count: int
    merges: list[str]  # module pair stems that merged at this threshold vs previous
    is_stable: bool
    is_recommended: bool


class ThresholdSweepResult(BaseModel):
    """Complete result of a threshold sweep advisory run."""

    steps: list[ThresholdSweepStep]
    recommended_threshold: int
    target_bcs: int


# Default sweep thresholds (ascending)
DEFAULT_SWEEP_STEPS: list[int] = [3, 6, 10, 14, 20, 30]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_domain_symbols(graph: Graph) -> list[SymbolNode]:
    """Return all SymbolNode instances in the graph classified as Domain ('D').

    A symbol is Domain-classified when its metadata contains ``ddd_layer == "D"``.
    Symbols with no ddd_layer (unclassified) are excluded.
    """
    result: list[SymbolNode] = []
    for node in graph.iter_concepts():
        if node.type != "symbol":
            continue
        meta = node.metadata or {}
        if meta.get("ddd_layer") == "D":
            # Reconstruct as SymbolNode
            if isinstance(node, SymbolNode):
                result.append(node)
            else:
                # Fallback: build SymbolNode from base GraphNode data
                result.append(
                    SymbolNode(
                        id=node.id,
                        content=node.content,
                        created=node.created,
                        source_file=node.source_file,
                        metadata=node.metadata,
                    )
                )
    return result


def _group_by_module(symbols: list[SymbolNode]) -> dict[str, list[SymbolNode]]:
    """Group symbols by their owning module id.

    Falls back to "unknown" when metadata["module"] is absent.
    """
    groups: dict[str, list[SymbolNode]] = defaultdict(list)
    for sym in symbols:
        module = (sym.metadata or {}).get("module") or "unknown"
        groups[str(module)].append(sym)
    return dict(groups)


def _compute_import_coupling(
    graph: Graph,
    groups: dict[str, list[SymbolNode]],
) -> dict[tuple[str, str], int]:
    """Count cross-module CALLS / inherits_from edges between module groups.

    Returns a dict mapping (module_a, module_b) → call_count for pairs where
    a != b. The key is always (source_module, target_module) — not symmetric.
    """
    # Build symbol → module lookup for fast edge resolution
    sym_to_module: dict[str, str] = {}
    for mod_id, syms in groups.items():
        for sym in syms:
            sym_to_module[sym.id] = mod_id

    coupling: dict[tuple[str, str], int] = defaultdict(int)
    for src, tgt, _key, data in graph.graph.edges(data=True, keys=True):
        edge_type = data.get("type", "")
        if edge_type not in _COUPLING_EDGE_TYPES:
            continue
        src_mod = sym_to_module.get(src)
        tgt_mod = sym_to_module.get(tgt)
        if src_mod is None or tgt_mod is None:
            continue
        if src_mod == tgt_mod:
            continue  # intra-module — not inter-coupling
        coupling[(src_mod, tgt_mod)] += 1

    return dict(coupling)


# ---------------------------------------------------------------------------
# Union-Find for greedy module merging
# ---------------------------------------------------------------------------


class _UnionFind:
    """Path-compressed union-find for merging module clusters."""

    def __init__(self, items: list[str]) -> None:
        self._parent: dict[str, str] = {x: x for x in items}

    def __contains__(self, item: str) -> bool:
        return item in self._parent

    def find(self, x: str) -> str:
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]  # path compression
            x = self._parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra


def _cluster_modules(
    groups: dict[str, list[SymbolNode]],
    coupling: dict[tuple[str, str], int],
    merge_threshold: int = DEFAULT_MERGE_THRESHOLD,
    n_bcs: int | None = None,
) -> list[list[SymbolNode]]:
    """Cluster modules into BC candidates using union-find on coupling edges.

    Two modules are merged when their cross-module call count meets or exceeds
    ``merge_threshold``. If ``n_bcs`` is given, the resulting clusters are
    sorted by size (descending) and truncated to ``n_bcs`` entries — smaller
    clusters are dropped (their symbols are covered by the symbol list of the
    trimmed clusters that remain).

    Returns a list of clusters, where each cluster is a list of SymbolNode.
    """
    module_ids = list(groups.keys())
    if not module_ids:
        return []

    uf = _UnionFind(module_ids)

    # Merge pairs exceeding the threshold
    for (mod_a, mod_b), count in coupling.items():
        if count >= merge_threshold and mod_a in uf and mod_b in uf:
            uf.union(mod_a, mod_b)

    # Build cluster → list[module_id] mapping
    cluster_modules: dict[str, list[str]] = defaultdict(list)
    for mod_id in module_ids:
        root = uf.find(mod_id)
        cluster_modules[root].append(mod_id)

    # Flatten into symbol lists
    clusters: list[list[SymbolNode]] = []
    for mods in cluster_modules.values():
        syms: list[SymbolNode] = []
        for mod in mods:
            syms.extend(groups.get(mod, []))
        clusters.append(syms)

    # Sort by size descending, then apply n_bcs limit
    clusters.sort(key=lambda c: len(c), reverse=True)
    if n_bcs is not None:
        clusters = clusters[:n_bcs]

    return clusters


def _compute_confidence_level(
    groups: dict[str, list[SymbolNode]],
    inter_coupling: dict[tuple[str, str], int],
) -> Literal["high", "medium", "low"]:
    """Derive overall confidence based on inter-module coupling density.

    Heuristic:
    - ratio = total_inter_calls / max(1, total_symbols * (n_modules - 1))
    - ratio ≤ _HIGH_CONFIDENCE_MAX_RATIO  → "high"
    - ratio ≤ _MEDIUM_CONFIDENCE_MAX_RATIO → "medium"
    - else                                  → "low"

    Rationale: well-separated modules produce sparse inter-coupling,
    meaning the BC boundaries are signal-backed. Dense coupling means the
    grouping is ambiguous and the architect should review carefully.
    """
    n_modules = len(groups)
    total_symbols = sum(len(s) for s in groups.values())
    total_inter = sum(inter_coupling.values())

    if n_modules <= 1 or total_symbols == 0:
        return "high"  # trivial case — single or empty cluster is unambiguous

    denominator = total_symbols * max(1, n_modules - 1)
    ratio = total_inter / denominator

    if ratio <= _HIGH_CONFIDENCE_MAX_RATIO:
        return "high"
    if ratio <= _MEDIUM_CONFIDENCE_MAX_RATIO:
        return "medium"
    return "low"


def _bc_name_from_modules(module_ids: list[str]) -> str:
    """Derive a human-readable BC name from module IDs.

    Single-module clusters → strip "mod-" prefix and use the remainder.
    Multi-module clusters → join the stems with "+".
    """
    stems = [mid.removeprefix("mod-") for mid in sorted(module_ids)]
    if len(stems) == 1:
        return stems[0]
    return "+".join(stems[:3]) + ("..." if len(stems) > 3 else "")


def _count_symbols_per_module(graph: Graph) -> dict[str, int]:
    """Count all symbol nodes per module (regardless of DDD layer).

    One pass over graph.iter_concepts().  Falls back to "unknown" when
    metadata["module"] is absent — same convention as _group_by_module.
    Used to compute d_ratio: what fraction of a module's symbols are in
    the D-classified cluster.
    """
    counts: dict[str, int] = defaultdict(int)
    for node in graph.iter_concepts():
        if node.type != "symbol":
            continue
        meta = node.metadata or {}
        module = meta.get("module") or "unknown"
        counts[str(module)] += 1
    return dict(counts)


def _per_cluster_confidence(
    cluster_syms: list[SymbolNode],
    coupling: dict[tuple[str, str], int],
    module_symbol_totals: dict[str, int],
) -> ClusterConfidence:
    """Per-cluster confidence using the RAISE-16789 formula.

    confidence = D_RATIO_WEIGHT * d_ratio + COHESION_WEIGHT * cohesion

    d_ratio:
        len(cluster_syms) / sum(module_symbol_totals[m] for m in cluster_modules)
        Capped at 1.0.  Falls back to 1.0 when total==0.

    cohesion:
        intra / (intra + extra + 1)
        where intra = coupling inside cluster_module_ids
              extra = coupling crossing the cluster boundary (exactly one endpoint inside)
        Special: if intra+extra==0, uses colocation prior (0.7 if >1 sym, else 0.5).
        Single-module floor: if len(cluster_module_ids)==1 and len(cluster_syms)>1,
            cohesion = max(cohesion, 0.5).
    """
    cluster_module_ids: set[str] = {
        str((sym.metadata or {}).get("module") or "unknown") for sym in cluster_syms
    }

    # d_ratio
    d_count = len(cluster_syms)
    total_module_syms = sum(module_symbol_totals.get(m, 0) for m in cluster_module_ids)
    d_ratio = 1.0 if total_module_syms == 0 else min(1.0, d_count / total_module_syms)

    # cohesion
    intra = sum(
        v
        for (a, b), v in coupling.items()
        if a in cluster_module_ids and b in cluster_module_ids
    )
    extra = sum(
        v
        for (a, b), v in coupling.items()
        if (a in cluster_module_ids) != (b in cluster_module_ids)
    )

    if intra + extra == 0:
        cohesion = 0.7 if len(cluster_syms) > 1 else 0.5
    else:
        cohesion = intra / (intra + extra + 1)
        if len(cluster_module_ids) == 1 and len(cluster_syms) > 1:
            cohesion = max(cohesion, 0.5)

    confidence = min(1.0, D_RATIO_WEIGHT * d_ratio + COHESION_WEIGHT * cohesion)

    return ClusterConfidence(
        confidence=confidence,
        d_ratio=d_ratio,
        cohesion=cohesion,
    )


# ---------------------------------------------------------------------------
# Public graph preparation helper (used by CLI for advisor pre-computation)
# ---------------------------------------------------------------------------


def prepare_discovery_inputs(
    graph: Graph,
) -> tuple[dict[str, list[SymbolNode]], dict[tuple[str, str], int]]:
    """Extract domain-symbol groups and inter-module coupling from the graph.

    Returns:
        (groups, coupling) where groups is module_id → [SymbolNode] and
        coupling is (mod_a, mod_b) → call_count.
    """
    domain_symbols = _extract_domain_symbols(graph)
    groups = _group_by_module(domain_symbols)
    coupling = _compute_import_coupling(graph, groups)
    return groups, coupling


# ---------------------------------------------------------------------------
# Threshold sweep advisor
# ---------------------------------------------------------------------------


def _modules_at_threshold(
    groups: dict[str, list[SymbolNode]],
    coupling: dict[tuple[str, str], int],
    threshold: int,
) -> set[frozenset[str]]:
    """Return the set of module clusters (as frozensets of module IDs) at a given threshold."""
    module_ids = list(groups.keys())
    if not module_ids:
        return set()
    uf = _UnionFind(module_ids)
    for (mod_a, mod_b), count in coupling.items():
        if count >= threshold and mod_a in uf and mod_b in uf:
            uf.union(mod_a, mod_b)
    clusters: dict[str, set[str]] = defaultdict(set)
    for mod_id in module_ids:
        root = uf.find(mod_id)
        clusters[root].add(mod_id)
    return {frozenset(c) for c in clusters.values()}


def _compute_merges_at_step(
    i: int,
    module_sets_per_step: list[set[frozenset[str]]],
    groups: dict[str, list[SymbolNode]],
) -> list[str]:
    """Return human-readable merge labels for step i vs step i-1."""
    baseline: set[frozenset[str]] = (
        {frozenset({mod}) for mod in groups} if i == 0 else module_sets_per_step[i - 1]
    )
    current = module_sets_per_step[i]
    merged: list[str] = []
    for cluster in current:
        if len(cluster) > 1 and any(c < cluster for c in baseline):
            stems = sorted(m.removeprefix("mod-") for m in cluster)
            merged.append("+".join(stems[:3]) + ("..." if len(stems) > 3 else ""))
    return merged


def _find_recommended_idx(
    bc_counts: list[int],
    is_stable: list[bool],
    ordered: list[int],
    target_bcs: int,
) -> int:
    """Return index of the recommended step (stable, closest to target, min threshold)."""
    best_idx = -1
    best_dist: int | None = None
    for i, stable in enumerate(is_stable):
        if not stable:
            continue
        dist = abs(bc_counts[i] - target_bcs)
        if (
            best_dist is None
            or dist < best_dist
            or (dist == best_dist and ordered[i] < ordered[best_idx])
        ):
            best_dist = dist
            best_idx = i
    return best_idx if best_idx >= 0 else len(ordered) - 1


def sweep_thresholds(
    groups: dict[str, list[SymbolNode]],
    coupling: dict[tuple[str, str], int],
    target_bcs: int,
    sweep_steps: list[int] = DEFAULT_SWEEP_STEPS,
) -> ThresholdSweepResult:
    """Sweep merge thresholds and advise the threshold closest to target_bcs BCs.

    For each threshold in ``sweep_steps`` (ascending):
    - Cluster modules using ``_cluster_modules(n_bcs=None)`` (untruncated).
    - Record bc_count and which module pairs merged vs the previous step.

    Stability:
    - Step i is stable when ``bc_count[i] == bc_count[i+1]``.
    - The last step is always stable.

    Recommended:
    - The stable step with minimum ``|bc_count - target_bcs|``.
    - Tie-broken by minimum threshold.

    Returns:
        ThresholdSweepResult with all steps annotated and the recommended threshold.
    """
    if not sweep_steps:
        raise ValueError("sweep_steps must be non-empty")

    ordered = sorted(sweep_steps)
    n = len(ordered)

    bc_counts = [
        len(_cluster_modules(groups, coupling, merge_threshold=t, n_bcs=None))
        for t in ordered
    ]
    module_sets_per_step = [_modules_at_threshold(groups, coupling, t) for t in ordered]
    merges_per_step = [
        _compute_merges_at_step(i, module_sets_per_step, groups) for i in range(n)
    ]
    is_stable = [
        True if i == n - 1 else bc_counts[i] == bc_counts[i + 1] for i in range(n)
    ]

    best_idx = _find_recommended_idx(bc_counts, is_stable, ordered, target_bcs)

    steps = [
        ThresholdSweepStep(
            threshold=ordered[i],
            bc_count=bc_counts[i],
            merges=merges_per_step[i],
            is_stable=is_stable[i],
            is_recommended=(i == best_idx),
        )
        for i in range(n)
    ]

    return ThresholdSweepResult(
        steps=steps,
        recommended_threshold=ordered[best_idx],
        target_bcs=target_bcs,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def discover_bcs(
    graph: Graph,
    *,
    n_bcs: int = 7,
    run_artifact: Path,
    merge_threshold: int = DEFAULT_MERGE_THRESHOLD,
) -> BCDiscoveryResult:
    """Discover Bounded Context suggestions from Domain-classified symbols.

    Algorithm:
    1. Extract D-classified symbols from the graph.
    2. Group by owning module (module_colocation signal).
    3. Compute inter-module CALLS/inherits_from coupling (import_coupling signal).
    4. Cluster modules using union-find; merge pairs with call count ≥ merge_threshold.
    5. Limit to n_bcs clusters (largest first).
    6. Derive confidence gradient from coupling density.
    7. Build BCSuggestion per cluster with name, symbols, and rationale.

    Args:
        graph: Loaded knowledge graph (from rai graph build output).
        n_bcs: Maximum number of BC suggestions to return.
        run_artifact: Path where the run artifact will be written by the caller.
        merge_threshold: Minimum cross-module calls to merge two modules.

    Returns:
        BCDiscoveryResult with suggestions, overall confidence, and signal sources.
    """
    domain_symbols = _extract_domain_symbols(graph)
    if not domain_symbols:
        return BCDiscoveryResult(
            bc_suggestions=[],
            confidence="high",
            signal_sources=["module_colocation", "import_coupling"],
            run_artifact=run_artifact,
        )

    groups = _group_by_module(domain_symbols)
    coupling = _compute_import_coupling(graph, groups)
    clusters = _cluster_modules(
        groups, coupling, merge_threshold=merge_threshold, n_bcs=n_bcs
    )

    confidence = _compute_confidence_level(groups, coupling)
    module_symbol_totals = _count_symbols_per_module(graph)

    # Build reverse: symbol_id → module for rationale generation
    sym_to_module: dict[str, str] = {
        sym.id: mod for mod, syms in groups.items() for sym in syms
    }

    suggestions: list[BCSuggestion] = []

    for cluster_syms in clusters:
        if not cluster_syms:
            continue
        module_ids = sorted(
            {sym_to_module[s.id] for s in cluster_syms if s.id in sym_to_module}
        )
        name = _bc_name_from_modules(module_ids)
        cc = _per_cluster_confidence(cluster_syms, coupling, module_symbol_totals)

        if len(module_ids) == 1:
            rationale = (
                f"All {len(cluster_syms)} symbols co-located in {module_ids[0]}."
            )
        else:
            total_calls = sum(
                v
                for (a, b), v in coupling.items()
                if a in module_ids and b in module_ids
            )
            rationale = (
                f"{len(cluster_syms)} symbols across {len(module_ids)} modules "
                f"({', '.join(module_ids[:3])}{'...' if len(module_ids) > 3 else ''}); "
                f"{total_calls} cross-module call(s) triggered merge."
            )

        suggestions.append(
            BCSuggestion(
                name=name,
                symbols=sorted(s.id for s in cluster_syms),
                confidence=cc.confidence,
                d_ratio=cc.d_ratio,
                cohesion=cc.cohesion,
                split_candidate=cc.confidence < SPLIT_CANDIDATE_THRESHOLD,
                rationale=rationale,
            )
        )

    # Symbol-count-weighted mean of per-cluster confidences
    total_sym_count = sum(len(s.symbols) for s in suggestions)
    overall_confidence = (
        sum(s.confidence * len(s.symbols) for s in suggestions) / total_sym_count
        if total_sym_count > 0
        else 0.0
    )

    return BCDiscoveryResult(
        bc_suggestions=suggestions,
        confidence=confidence,
        signal_sources=["module_colocation", "import_coupling"],
        run_artifact=run_artifact,
        overall_confidence=overall_confidence,
    )
