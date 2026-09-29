"""SQLite-backed port allocation store for cross-process collision avoidance.

Thin wrapper over the shared project DB (``~/.rai/raise.db``), following the
``SqliteWorktreeStore`` / ``SqliteMissionStore`` pattern: constructor takes a
project ``Path``, calls ``ensure_schema``, and transactional writes use
``with self._conn`` (RAISE-15605 lock-release pattern).

RAISE-16541, S16534.1 — Epic E-FLEET-8 (local dev stack isolation).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import ensure_schema


@runtime_checkable
class PortBlockLike(Protocol):
    """Structural type for objects with base and ports attributes."""

    @property
    def base(self) -> int:
        """Base port number."""
        ...

    @property
    def ports(self) -> Mapping[str, int]:
        """Mapping of service name to port number."""
        ...


logger = logging.getLogger(__name__)


class PortBlockClaimedError(Exception):
    """Raised when a port block's base_port is already claimed by another worktree path."""

    def __init__(self, base_port: int, existing_path: str) -> None:
        self.base_port = base_port
        self.existing_path = existing_path
        super().__init__(
            f"Port block base {base_port} already claimed by {existing_path}"
        )


@dataclass(frozen=True)
class PortAllocationClaim:
    """Read-only representation of a persisted port allocation claim."""

    project_id: str
    worktree_path: str
    base: int
    ports: MappingProxyType[str, int]
    allocated_at: str


class SqlitePortAllocationStore:
    """SQLite-backed port allocation store (V72 schema).

    API:
    - ``claim(worktree_path, block)`` — atomic INSERT/UPDATE; raises
      ``PortBlockClaimedError`` on UNIQUE violation by another path.
      Idempotent for same path.
    - ``get(worktree_path)`` — returns ``PortAllocationClaim | None``.
    - ``release(worktree_path)`` — DELETE; no-op if absent (idempotent teardown).
    - ``list_claims()`` — returns all claims for this project.

    Pattern: ``SqliteWorktreeStore`` — thin wrapper, no port logic.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        ensure_schema(self._conn)

    def claim(self, worktree_path: Path, block: PortBlockLike) -> None:
        """Persist a port block claim for a worktree path.

        If the same path already has a claim, it is updated (idempotent).
        If a different path holds the same ``base_port``, raises
        ``PortBlockClaimedError``.
        """
        path_str = str(worktree_path)
        base_port: int = block.base
        ports: dict[str, int] = dict(block.ports)
        ports_json = json.dumps(ports)

        with self._conn:
            try:
                self._conn.execute(
                    "INSERT INTO port_allocations "
                    "(project_id, worktree_path, base_port, ports_json) "
                    "VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(project_id, worktree_path) DO UPDATE SET "
                    "base_port = excluded.base_port, "
                    "ports_json = excluded.ports_json, "
                    "allocated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')",
                    (self._project_id, path_str, base_port, ports_json),
                )
            except sqlite3.IntegrityError:
                # base_port UNIQUE violation — another path owns it
                conflicting = self._conn.execute(
                    "SELECT worktree_path FROM port_allocations "
                    "WHERE base_port = ? AND worktree_path != ?",
                    (base_port, path_str),
                ).fetchone()
                conflicting_path = str(conflicting[0]) if conflicting else "<unknown>"
                raise PortBlockClaimedError(base_port, conflicting_path) from None

    def get(self, worktree_path: Path) -> PortAllocationClaim | None:
        """Retrieve the persisted claim for a worktree path, or None."""
        path_str = str(worktree_path)
        row = self._conn.execute(
            "SELECT project_id, worktree_path, base_port, ports_json, allocated_at "
            "FROM port_allocations WHERE project_id = ? AND worktree_path = ?",
            (self._project_id, path_str),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_claim(row)

    def release(self, worktree_path: Path) -> None:
        """Delete the claim for a worktree path. No-op if absent (idempotent)."""
        path_str = str(worktree_path)
        with self._conn:
            self._conn.execute(
                "DELETE FROM port_allocations "
                "WHERE project_id = ? AND worktree_path = ?",
                (self._project_id, path_str),
            )

    def release_by_path(self, worktree_path: Path) -> None:
        """Delete claim by worktree_path alone, ignoring project_id.

        Used by the orphan reaper where the working directory no longer
        exists and project_id resolution would produce a wrong value.
        """
        with self._conn:
            self._conn.execute(
                "DELETE FROM port_allocations WHERE worktree_path = ?",
                (str(worktree_path),),
            )

    def list_claims(self) -> list[PortAllocationClaim]:
        """Return all claims for this project."""
        rows = self._conn.execute(
            "SELECT project_id, worktree_path, base_port, ports_json, allocated_at "
            "FROM port_allocations WHERE project_id = ?",
            (self._project_id,),
        ).fetchall()
        return [self._row_to_claim(r) for r in rows]

    @staticmethod
    def _row_to_claim(row: sqlite3.Row) -> PortAllocationClaim:
        """Convert a sqlite3.Row to a PortAllocationClaim."""
        project_id = str(row["project_id"])
        worktree_path = str(row["worktree_path"])
        base_port = int(row["base_port"])
        ports_json = str(row["ports_json"])
        allocated_at = str(row["allocated_at"])
        try:
            ports_dict: dict[str, int] = json.loads(ports_json)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "Corrupt ports_json for %s — treating as empty", worktree_path
            )
            ports_dict = {}
        return PortAllocationClaim(
            project_id=project_id,
            worktree_path=worktree_path,
            base=base_port,
            ports=MappingProxyType(ports_dict),
            allocated_at=allocated_at,
        )
