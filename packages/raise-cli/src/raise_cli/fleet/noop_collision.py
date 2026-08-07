"""No-op fleet collision stubs — intentionally inert for N<4 agents (ADR-106 §3).

These stubs satisfy the raise_core.fleet Protocols via structural subtyping.
They carry no state and perform no I/O. E-FLEET-2 replaces them with SQLite/git
implementations without touching the dispatcher (dependency injection).
"""

from __future__ import annotations

from collections.abc import Sequence

from raise_core.fleet import MergePreview


class NoopModuleScope:
    """No-op scope: never reports overlap. Intentional for N<4 (ADR-106 §3) — not a TODO."""

    def normalize(self, declared: Sequence[str]) -> frozenset[str]:
        """Return frozenset of declared without normalisation — all scopes distinct."""
        return frozenset(declared)

    def overlaps(self, a: Sequence[str], b: Sequence[str]) -> bool:
        """Always return False — no serialisation needed for N<4 agents."""
        return False


class NoopTaskClaimStore:
    """No-op claim store: always grants. Intentional for N<4 (ADR-106 §3) — not a TODO."""

    def claim(
        self,
        work_id: str,
        module_scope: str,
        *,
        pid: int,
        ttl_seconds: int = 1800,
    ) -> bool:
        """Always grant the claim — no contention possible with a single agent."""
        return True

    def release(self, work_id: str, module_scope: str, *, pid: int) -> None:
        """No-op release — nothing to release when claims are always granted."""
        return

    def holder(self, module_scope: str) -> str | None:
        """Always return None — no other agent holds any scope."""
        return None


class NoopMergePreflight:
    """No-op merge preflight: never conflicts. Intentional for N<4 (ADR-106 §3) — not a TODO."""

    def preview(self, branch: str, target: str) -> MergePreview:
        """Always report no conflict — single-agent dispatch never races on git refs."""
        return MergePreview(work_id=branch, has_conflict=False, conflicted_paths=())
