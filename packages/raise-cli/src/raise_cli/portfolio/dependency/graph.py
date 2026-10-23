"""DSM view + topological sort for confirmed portfolio dependency edges (Layer 2).

Only confirmed edges (requires/enables) participate in toposort.
Advisory edges (impacted_by/sequence_with) are reported separately.

Kahn algorithm O(V+E) with deterministic tie-breaking (sorted node names).
Full transitive ordering is produced — every reachable predecessor appears
before every reachable successor, not just immediate dependencies.
(PAT-E-9232: docstring is explicit about this being full Kahn, not a
single-pass in-degree partition.)
"""

from __future__ import annotations

import heapq
from collections import defaultdict
from dataclasses import dataclass

from raise_cli.portfolio.derivation import AdvisoryEdge
from raise_cli.portfolio.storage import PortfolioDep


class CycleDetectedError(Exception):
    """Raised when a cycle is detected in confirmed dependency edges.

    Callers who need strict mode can raise this after inspecting
    ``TopoResult.has_cycle``; ``toposort()`` itself returns a partial
    order rather than raising.
    """

    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        super().__init__(f"Cycle detected: {' -> '.join(cycle)}")


@dataclass
class TopoResult:
    """Result of a topological sort over confirmed edges."""

    order: list[str]
    """Initiatives in dependency-first order (prerequisites before dependents)."""

    has_cycle: bool
    """True when a cycle was detected; ``order`` is partial in that case."""

    cycle: list[str]
    """Cycle path if detected (e.g. [A, B, A]), else empty."""

    advisory_edges: list[AdvisoryEdge]
    """Advisory edges passed to DependencyGraph, carried through for reporting."""


class DependencyGraph:
    """Builds and sorts the confirmed dependency graph from portfolio_deps.

    Only ordering-type edges (requires, enables) participate in the
    topological sort.  Advisory edges (impacted_by, sequence_with) are
    passed through to ``TopoResult.advisory_edges`` for reporting.

    Edge semantics in the ordering graph:
    - ``requires``:  source requires target  →  target precedes source
    - ``enables``:   source enables  target  →  source precedes target
    """

    ORDERING_TYPES: frozenset[str] = frozenset({"requires", "enables"})

    def __init__(
        self,
        deps: list[PortfolioDep],
        nodes: list[str] | None = None,
        advisory: list[AdvisoryEdge] | None = None,
    ) -> None:
        """Initialise the dependency graph.

        Args:
            deps:     All confirmed/declared portfolio dependency edges.
            nodes:    Additional initiative keys to include in the sort even
                      when they carry no confirmed ordering edge (e.g. isolated
                      nodes, or nodes known only from initiative profiles).
            advisory: Advisory edges from derivation; carried into TopoResult.
        """
        self._ordering_deps = [d for d in deps if d.type in self.ORDERING_TYPES]
        self._all_deps = deps
        self._extra_nodes: list[str] = list(nodes or [])
        self._advisory: list[AdvisoryEdge] = list(advisory or [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def toposort(self) -> TopoResult:
        """Kahn O(V+E) topological sort with deterministic alphabetical tie-breaking.

        Returns a partial order when a cycle is detected; ``has_cycle`` and
        ``cycle`` fields indicate what was found.  Advisory edges do not
        affect the ordering — they are reported in ``TopoResult.advisory_edges``.
        """
        all_nodes, adj, in_degree = self._build_ordering_graph()

        # Kahn: start with in-degree-0 nodes in alphabetical order (min-heap)
        heap: list[str] = [n for n in all_nodes if in_degree[n] == 0]
        heapq.heapify(heap)

        order: list[str] = []
        while heap:
            node = heapq.heappop(heap)
            order.append(node)
            for neighbor in sorted(adj.get(node, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    heapq.heappush(heap, neighbor)

        if len(order) < len(all_nodes):
            remaining = all_nodes - set(order)
            cycle = self._find_cycle(remaining, adj)
            return TopoResult(
                order=order,
                has_cycle=True,
                cycle=cycle,
                advisory_edges=self._advisory,
            )

        return TopoResult(
            order=order,
            has_cycle=False,
            cycle=[],
            advisory_edges=self._advisory,
        )

    def dsm_view(self) -> dict[str, list[str]]:
        """Return adjacency dict {source: [targets]} for confirmed ordering edges.

        Represents the raw dependency direction (e.g. RAISE-14052 → RAISE-15025
        for a ``requires`` edge), not the ordering direction used by Kahn.
        Non-ordering dep types (conflicts, supersedes) are excluded.
        """
        result: dict[str, list[str]] = {}
        for dep in self._ordering_deps:
            if dep.source not in result:
                result[dep.source] = []
            if dep.target not in result[dep.source]:
                result[dep.source].append(dep.target)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_ordering_graph(
        self,
    ) -> tuple[set[str], dict[str, list[str]], dict[str, int]]:
        """Build ordering graph (predecessor→successor adjacency) and in-degree map."""
        all_nodes: set[str] = set(self._extra_nodes)
        adj: dict[str, list[str]] = defaultdict(list)
        in_degree: dict[str, int] = {}
        added_edges: set[tuple[str, str]] = set()

        for dep in self._ordering_deps:
            all_nodes.add(dep.source)
            all_nodes.add(dep.target)

        for node in all_nodes:
            in_degree.setdefault(node, 0)

        for dep in self._ordering_deps:
            if dep.type == "requires":
                # target must precede source
                pred, succ = dep.target, dep.source
            else:
                # enables: source must precede target
                pred, succ = dep.source, dep.target

            edge = (pred, succ)
            if edge not in added_edges:
                added_edges.add(edge)
                adj[pred].append(succ)
                in_degree[succ] += 1

        return all_nodes, dict(adj), in_degree

    def _find_cycle(self, remaining: set[str], adj: dict[str, list[str]]) -> list[str]:
        """Find a cycle path in the subgraph of remaining nodes using DFS.

        Returns the cycle as a closed path (first node repeated at end), e.g.
        [A, B, A].  Returns an empty list if no cycle is found (shouldn't
        happen when called after Kahn detects residual nodes, but guards
        against edge-cases from degenerate input).
        """
        white, gray, black = 0, 1, 2
        color: dict[str, int] = dict.fromkeys(remaining, white)
        path: list[str] = []
        found: list[str] = []

        def dfs(node: str) -> bool:
            color[node] = gray
            path.append(node)
            for neighbor in sorted(adj.get(node, [])):
                if neighbor not in remaining:
                    continue
                if color[neighbor] == gray:
                    idx = path.index(neighbor)
                    found.extend(path[idx:])
                    found.append(neighbor)
                    return True
                if color[neighbor] == white and dfs(neighbor):
                    return True
            path.pop()
            color[node] = black
            return False

        for node in sorted(remaining):
            if color[node] == white and dfs(node):
                break

        return found
