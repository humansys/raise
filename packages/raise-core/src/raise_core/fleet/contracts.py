"""Fleet dispatcher contract — ADR-106 §1.

Declares DispatchCandidate, DispatchPlan, and DependencyResolver Protocol.
All interfaces are @runtime_checkable; no concrete implementation lives here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class DispatchCandidate:
    """A work item that may be dispatched.

    work_id: backlog key, e.g. "RAISE-8401"
    blocked_by: keys that block this candidate (empty = unblocked)
    declared_scope: declared module scopes (may be empty)
    """

    work_id: str
    blocked_by: tuple[str, ...]
    declared_scope: tuple[str, ...]


@dataclass(frozen=True)
class DispatchPlan:
    """Result of DependencyResolver.resolve — ADR-106 §1.

    dispatchable: work_ids ready for parallel dispatch
    blocked: blocked by unresolved dependency
    serialized: groups to execute serially due to scope overlap
    rejected: excluded (e.g. terminal mission state)
    rejection_reasons: (work_id, reason) pairs carrying WHY a key landed in
        `rejected` — e.g. ("RAISE-1", "terminal_status"). Added RAISE-15764
        (D2.b): `rejected` was a bare tuple of keys with nowhere to carry a
        machine-readable reason (ProvisioningCheck.detail, terminal-mission
        status, etc.). Defaulted so existing construction sites
        (DagDependencyResolver, FleetDispatchService) keep compiling
        unchanged — frozen + tuple-of-pairs (not a dict) to preserve
        hashability and the module's frozen-dataclass convention.
    """

    dispatchable: tuple[str, ...]
    blocked: tuple[str, ...]
    serialized: tuple[tuple[str, ...], ...]
    rejected: tuple[str, ...]
    rejection_reasons: tuple[tuple[str, str], ...] = ()


@runtime_checkable
class DependencyResolver(Protocol):
    """Resolves the backlog dependency DAG — ADR-106 §1.

    resolve is pure and deterministic: given candidates with blocked_by
    and declared_scope, produces the plan. No I/O — sub-ms for ≥100 edges.
    """

    def resolve(self, candidates: Sequence[DispatchCandidate]) -> DispatchPlan:
        """Resolve the dependency DAG and return a DispatchPlan."""
        ...
