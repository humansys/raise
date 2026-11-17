"""DagDependencyResolver — Kahn topsort over DispatchCandidate DAG.

Pure, no I/O. Implements DependencyResolver Protocol (ADR-106 §1).

serialized is always () — scope-overlap grouping is FLEET-2 (RAISE-8396).
rejected is always () — terminal-mission filtering is FleetDispatchService's job.
"""

from __future__ import annotations

from collections.abc import Sequence

from raise_core.fleet.contracts import DispatchCandidate, DispatchPlan


class DagDependencyResolver:
    """Kahn topological sort resolver.

    Partition semantics:
    - dispatchable: in-degree == 0 after resolving all known edges
    - blocked: in-degree > 0 (cycle members or unresolved dependencies)
    - serialized: always () — FLEET-2 out of scope
    - rejected: always () — caller (FleetDispatchService) populates this
    """

    def resolve(self, candidates: Sequence[DispatchCandidate]) -> DispatchPlan:
        """Resolve the dependency DAG and return a DispatchPlan.

        Unknown blocker keys (keys not present in the candidate set) are treated
        as unresolved — the candidate remains blocked (D5, AC10).
        """
        if not candidates:
            return DispatchPlan(
                dispatchable=(),
                blocked=(),
                serialized=(),
                rejected=(),
            )

        # in_degree tracks effective dependency count per work_id.
        # Unknown blockers are counted the same as known ones — they cannot
        # be resolved (no one will "complete" them), so the candidate stays blocked.
        in_degree: dict[str, int] = {c.work_id: 0 for c in candidates}

        for c in candidates:
            # Each entry in blocked_by increments in_degree regardless of whether
            # the blocker is in the candidate set. Known blockers would eventually
            # be resolved in a full Kahn pass; unknown ones never are (D5, AC10).
            in_degree[c.work_id] += len(c.blocked_by)

        # dispatchable = nodes with in_degree 0 in the INPUT graph
        # (what can be dispatched RIGHT NOW, not after iterating)
        dispatchable: list[str] = [wid for wid, deg in in_degree.items() if deg == 0]
        # blocked = everything else (has unsatisfied dependencies or is in a cycle)
        dispatchable_set = set(dispatchable)
        blocked = tuple(wid for wid in in_degree if wid not in dispatchable_set)
        return DispatchPlan(
            dispatchable=tuple(dispatchable),
            blocked=blocked,
            serialized=(),
            rejected=(),
        )
