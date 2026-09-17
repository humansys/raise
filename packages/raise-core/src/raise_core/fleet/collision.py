"""Fleet collision prevention primitives — ADR-106 §2, ADR-105 §1-§3.

Declares TaskClaimStore, ModuleScope, MergePreflight Protocols and
serialize_overlapping function. All interfaces are @runtime_checkable.
E-FLEET-3 declares; E-FLEET-2 implements the concrete SQLite/git versions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from raise_core.fleet.contracts import DispatchCandidate


@runtime_checkable
class TaskClaimStore(Protocol):
    """Atomic task claim with TTL, keyed by module_scope — ADR-105 §1.

    Follows the SqliteLeaseStore pattern: BEGIN IMMEDIATE + expiry +
    takeover by dead PID (ADR-094).
    """

    def claim(
        self,
        work_id: str,
        module_scope: str,
        *,
        pid: int,
        ttl_seconds: int = 1800,
    ) -> bool:
        """Atomically claim module_scope for work_id. Returns True if granted."""
        ...

    def release(self, work_id: str, module_scope: str, *, pid: int) -> None:
        """Release a previously granted claim identified by work_id + pid."""
        ...

    def holder(self, module_scope: str) -> str | None:
        """Return the work_id that currently holds the claim, or None."""
        ...


@runtime_checkable
class ModuleScope(Protocol):
    """Module ownership manifest: normalizes declared scope to comparable ids — ADR-105 §2."""

    def normalize(self, declared: Sequence[str]) -> frozenset[str]:
        """Normalize declared scope strings to a canonical frozenset."""
        ...

    def overlaps(self, a: Sequence[str], b: Sequence[str]) -> bool:
        """Return True if scope sets a and b have overlapping normalized ids."""
        ...


def serialize_overlapping(
    candidates: Sequence[DispatchCandidate],
    scope: ModuleScope,
) -> tuple[tuple[str, ...], ...]:
    """Group candidates with overlapping scope into groups to serialize — ADR-105 §2.

    Pure function. Signature declared by E-FLEET-3; body implemented by E-FLEET-2.
    """
    raise NotImplementedError(
        "serialize_overlapping implemented in E-FLEET-2 (RAISE-8396)"
    )


@dataclass(frozen=True)
class MergePreview:
    """Result of a merge-tree preflight check — ADR-105 §3.

    work_id: branch identifier checked
    has_conflict: True if a merge conflict was detected
    conflicted_paths: paths in conflict (empty when has_conflict is False)
    """

    work_id: str
    has_conflict: bool
    conflicted_paths: tuple[str, ...]


@runtime_checkable
class MergePreflight(Protocol):
    """git merge-tree preflight: previews conflict without modifying branches — ADR-105 §3."""

    def preview(self, branch: str, target: str) -> MergePreview:
        """Preview merging branch into target. Returns MergePreview without modifying refs."""
        ...
