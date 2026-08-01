"""Lanza-Marinescu structural health metrics for a graph module (S2162.2).

Computes WMC, LCOM4, fan_in, fan_out, and cyclomatic_p95 deterministically
from SymbolNode + CALLS edges in the knowledge graph. No LLM required.

Architecture decisions: ADR-E2162-4 (LCOM4 variant, cyclomatic branch-node set,
fan coupling semantics).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode


class MetricsReport(BaseModel):
    """Structural health metrics for a module.

    Computed deterministically from SymbolNode + CALLS/INHERITS_FROM edges.
    No LLM required. Schema is additive-only (schema_version=1).

    Fields:
        schema_version: Report schema version (additive-only policy, always 1).
        module_id:      Module under analysis (e.g. "mod-discovery").
        symbol_count:   Total public symbols ingested for this module.
        wmc:            Weighted Methods per Class — count of method+function symbols.
        lcom:           LCOM4: max(0, connected_components - 1) via shared-callee
                        topology (any shared callee, not restricted to intra-class;
                        see ADR-E2162-4 §Q1).
        fan_in:         Distinct external modules with CALLS edges pointing INTO
                        this module (intra-module edges excluded per D4).
        fan_out:        Distinct external modules this module's symbols call OUT TO.
        cyclomatic_p95: 95th-percentile branch_count across method+function symbols.
        computed_at:    UTC timestamp of computation.
    """

    schema_version: int = Field(default=1)
    module_id: str
    symbol_count: int
    wmc: int
    lcom: int
    fan_in: int
    fan_out: int
    cyclomatic_p95: float
    computed_at: datetime


class MetricsComputer:
    """Compute Lanza-Marinescu metrics for a module from the knowledge graph.

    Args:
        graph:   The loaded knowledge Graph instance (post-build).
        now_fn:  Optional callable returning current UTC datetime. Used to
                 inject a fixed timestamp for deterministic tests (T11).
    """

    def __init__(
        self,
        graph: Graph,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._graph = graph
        self._now_fn: Callable[[], datetime] = now_fn or (lambda: datetime.now(tz=UTC))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(self, module_id: str) -> MetricsReport:
        """Compute metrics for the given module.

        Args:
            module_id: Module ID as stored in graph (e.g. "mod-discovery").

        Returns:
            MetricsReport with all structural health metrics.

        Raises:
            ModuleNotFoundError: If module_id has no SymbolNode records in the
                graph (no ModuleNode check — a module with zero public symbols
                is treated as not found; see ADR-E2162-4 §Q2).
        """
        all_symbols = [
            n
            for n in self._graph.get_concepts_by_type("symbol")
            if n.metadata.get("module") == module_id
        ]

        if not all_symbols:
            raise ModuleNotFoundError(module_id)

        # --- WMC: count of callable symbols (method or function) ---
        callables = [
            s for s in all_symbols if s.metadata.get("kind") in {"method", "function"}
        ]
        wmc = len(callables)

        # --- LCOM4: connected components via intra-class shared-callee graph ---
        lcom = _compute_lcom4(all_symbols, self._graph)

        # --- fan_in / fan_out: module-crossing CALLS edges only ---
        symbol_ids = {s.id for s in all_symbols}
        fan_in_modules: set[str] = set()
        fan_out_modules: set[str] = set()

        for edge in self._graph.iter_relationships():
            if edge.type != "calls":
                continue
            src_mod = _module_of(edge.source, self._graph)
            tgt_mod = _module_of(edge.target, self._graph)
            if src_mod == tgt_mod:
                continue  # intra-module — skip per D4
            if edge.target in symbol_ids and src_mod:
                fan_in_modules.add(src_mod)
            if edge.source in symbol_ids and tgt_mod:
                fan_out_modules.add(tgt_mod)

        fan_in = len(fan_in_modules)
        fan_out = len(fan_out_modules)

        # --- cyclomatic_p95: 95th-percentile branch_count ---
        branch_counts = [int(s.metadata.get("branch_count", 1)) for s in callables]
        cyclomatic_p95 = _p95(branch_counts)

        return MetricsReport(
            module_id=module_id,
            symbol_count=len(all_symbols),
            wmc=wmc,
            lcom=lcom,
            fan_in=fan_in,
            fan_out=fan_out,
            cyclomatic_p95=cyclomatic_p95,
            computed_at=self._now_fn(),
        )


# ---------------------------------------------------------------------------
# Private helpers (free functions for testability)
# ---------------------------------------------------------------------------


def _module_of(node_id: str, graph: Graph) -> str | None:
    """Return the module metadata of a graph node, or None if absent."""
    node: GraphNode | None = graph.get_concept(node_id)
    if node is None:
        return None
    mod = node.metadata.get("module")
    return str(mod) if mod else None


def _compute_lcom4(symbols: list[GraphNode], graph: Graph) -> int:  # noqa: C901
    """Compute LCOM4 = max(0, connected_components - 1) for the module.

    Algorithm (Hitz & Montazeri, extended Ratzinger):
    1. Group methods by their parent class.
    2. For each class, build an undirected graph where methods are nodes.
       Add an edge between M1 and M2 if they share at least one callee
       (any shared call target, not restricted to intra-class callees;
       see ADR-E2162-4 §Q1 — "any shared callee" variant chosen).
    3. Count connected components across all classes.
    4. Sum max(0, components - 1) per class and return the total.

    Aggregation per class (not per module) ensures two cohesive classes give
    lcom=0, not lcom=1. See ADR-E2162-4 §R2 for the rationale.

    Classes with a single method contribute 0 (cohesive by definition).
    Isolated methods (no shared callees) each form their own component.

    ADR-E2162-4 documents the variant choice.
    """
    # Group methods by (parent_class, module); ignore functions (no parent).
    # key: (parent, module) → list of method node_ids
    classes: dict[tuple[str, str], list[str]] = defaultdict(list)
    for sym in symbols:
        parent = sym.metadata.get("parent", "")
        kind = sym.metadata.get("kind", "")
        module = sym.metadata.get("module", "")
        if kind == "method" and parent:
            classes[(parent, module)].append(sym.id)

    if not classes:
        return 0

    total_components = 0

    for method_ids_list in classes.values():
        method_ids = set(method_ids_list)
        if len(method_ids) == 1:
            total_components += 1
            continue

        # Build set of callees per method within this class.
        # "Within this class" = callee has same parent as the calling method.
        # We use CALLS edges from the graph that land on nodes in method_ids.
        callees_of: dict[str, set[str]] = {m: set() for m in method_ids}
        for edge in graph.iter_relationships():
            if edge.type != "calls":
                continue
            if edge.source in method_ids:
                # Any callee — we connect methods sharing the same callee (shared
                # callable target within the class).
                callees_of[edge.source].add(edge.target)

        # Build adjacency: M1—M2 if they share ≥1 callee (intra-class graph).
        # NOTE: callee doesn't have to be in the class itself — the topology
        # only requires that two methods both call the same target.
        adjacency: dict[str, set[str]] = {m: set() for m in method_ids}
        method_list = list(method_ids)
        for i, m1 in enumerate(method_list):
            for m2 in method_list[i + 1 :]:
                if callees_of[m1] & callees_of[m2]:  # shared callee
                    adjacency[m1].add(m2)
                    adjacency[m2].add(m1)

        # Count connected components via BFS.
        visited: set[str] = set()
        components = 0
        for start in method_ids:
            if start in visited:
                continue
            components += 1
            queue = [start]
            while queue:
                node = queue.pop()
                if node in visited:
                    continue
                visited.add(node)
                queue.extend(adjacency[node] - visited)

        total_components += max(0, components - 1)

    return total_components


def _p95(values: list[int]) -> float:
    """Compute 95th-percentile using stdlib statistics only (no numpy).

    Policy (ADR-E2162-4):
    - len >= 20: use statistics.quantiles(data, n=20)[18] (index 18 = P95).
    - len in [2, 19]: use statistics.quantiles(data, n=20)[18] — statistics
      module interpolates; result capped at max(data) to prevent extrapolation
      beyond observed values on small samples (see ADR-E2162-4 §R4).
    - len == 1: return float(values[0]).
    - len == 0: return 1.0 (safe fallback; empty modules have no p95).

    Avoids numpy dependency to keep raise-core lightweight.
    """
    import statistics  # stdlib

    if not values:
        return 1.0
    if len(values) == 1:
        return float(values[0])
    # statistics.quantiles requires len >= 2; n=20 gives ventiles (P5, P10, ..., P95)
    # index 18 is the 95th percentile (19/20 = 0.95). Cap at max to prevent
    # extrapolation beyond observed values on small samples.
    raw = float(statistics.quantiles(values, n=20)[18])
    return min(raw, float(max(values)))
