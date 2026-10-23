"""Session ledger schema — cross-project self-surfacing store (RAISE-13146).

Stored in the ``session_ledger_entries`` table of the global ``~/.rai/raise.db``
(see ``raise_cli.storage.connection.get_project_db``). Rows are keyed by
``(session_id, natural_key)`` and upserted (latest-wins, transactional) — no
append+fold reconstruction at read time.

Eight sections of the session-ledger specimen plus ``friction`` (a typed
quality signal, dual-use with RAISE-11125) are modeled as one discriminated
row shape: ``LedgerEntry`` with a ``kind`` discriminator and a free-form
``fields`` dict holding the per-kind columns.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LedgerKind(str, Enum):
    """Discriminator for the 8 specimen sections + friction."""

    meta = "meta"
    project = "project"
    cartridge = "cartridge"
    issue = "issue"
    branch = "branch"
    artifact = "artifact"
    mission = "mission"
    open_thread = "open_thread"
    friction = "friction"


class LedgerEntry(BaseModel):
    """One row of the session ledger.

    Attributes:
        session_id: Partition key — ``discover_agent_session_id()``.
        kind: Section discriminator.
        natural_key: Upsert key within the session (e.g. "RAISE-13146").
        timestamp: When the entry was written (or last upserted).
        project_id: Stable project slug (``get_project_id(cwd)``), if known.
        fields: Per-kind columns (e.g. friction: phase/seam/severity/...).
    """

    session_id: str
    kind: LedgerKind
    natural_key: str
    timestamp: datetime
    project_id: str | None = None
    fields: dict[str, str] = Field(default_factory=dict)
