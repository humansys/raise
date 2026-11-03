"""Sync verification models for SyncVerifiable adapters.

Used by gate-sync to report local→remote parity verification results.

Architecture: S-AQG.4 — Sync gate real verification
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SyncEntry:
    """Result of verifying one ledger entry against the remote.

    Existence-only: the gate verifies that the remote artefact exists,
    not that its status matches local state (follow-up scope).
    """

    local_key: str
    remote_key: str
    exists: bool
    detail: str = ""


@dataclass(frozen=True)
class SyncReport:
    """Aggregated verification result for one adapter domain.

    pending_count / dead_letter_count semantics differ by domain:
    - backlog: scoped to the requested keys (op.key is a Jira key)
    - docs: always global (op.key is metadata title/type, not a path)

    entries=() means nothing was registered for this domain — passed=True.
    Phantom key detection (requested key not in any entry) is the gate's job.
    """

    domain: str
    entries: tuple[SyncEntry, ...] = field(default_factory=tuple)
    pending_count: int = 0
    dead_letter_count: int = 0

    @property
    def passed(self) -> bool:
        """True when all entries exist and no pending or dead-letter ops."""
        all_exist = all(e.exists for e in self.entries)
        no_pending = self.pending_count == 0 and self.dead_letter_count == 0
        return all_exist and no_pending
