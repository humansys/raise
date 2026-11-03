"""PendingOpsLog — JSONL append-only queue for failed remote operations.

Each entry is a JSON line with: id, op, key, args, ts.
Used by composite adapters to queue operations when remotes fail.
Replay via per-adapter sync commands.

File: .raise/sync/{domain}-pending-ops.jsonl (gitignored, per-dev).

Story: S1700.2 | Epic: E1700 Adapter Migration Path
ADR: adr-047-filesystem-canonical-adapter-pattern
AR-Q1: skip unparseable entries, never lose data.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PendingOp(BaseModel):
    """A single pending operation queued for replay."""

    id: str
    op: str
    key: str
    args: dict[str, Any]
    ts: str
    completed_remotes: list[int] = []
    attempt_count: int = 0
    last_error: str | None = None


class PendingOpsLog:
    """Append-only JSONL log of failed remote operations.

    Append on failure, iterate for replay, mark_done to remove replayed entries.
    Unparseable lines are skipped gracefully (AR-Q1).
    """

    def __init__(self, domain: str, project_root: Path) -> None:
        self._path = project_root / ".raise" / "sync" / f"{domain}-pending-ops.jsonl"

    def append(
        self,
        op: str,
        key: str,
        args: dict[str, Any],
        completed_remotes: list[int] | None = None,
    ) -> None:
        """Append a pending operation to the log."""
        entry = PendingOp(
            id=uuid.uuid4().hex[:12],
            op=op,
            key=key,
            args=args,
            ts=datetime.now(UTC).isoformat(),
            completed_remotes=completed_remotes or [],
        )
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def iter(self) -> Iterator[PendingOp]:
        """Iterate pending ops in order. Skips unparseable lines (AR-Q1)."""
        if not self._path.exists():
            return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data: dict[str, Any] = json.loads(line)
                yield PendingOp.model_validate(data)
            except (json.JSONDecodeError, Exception):  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("Skipping unparseable pending op: %.80s", line)

    def mark_done(self, op_id: str) -> None:
        """Remove a completed operation. Rewrites file without the entry."""
        remaining = [op for op in self.iter() if op.id != op_id]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for op in remaining:
                f.write(op.model_dump_json() + "\n")

    def update_completed(self, op_id: str, completed_remotes: list[int]) -> None:
        """Update completed_remotes for an op. Rewrites file with the change."""
        ops = list(self.iter())
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for op in ops:
                if op.id == op_id:
                    op.completed_remotes = completed_remotes
                f.write(op.model_dump_json() + "\n")

    def pending_count(self) -> int:
        """Count pending operations without full deserialization."""
        if not self._path.exists():
            return 0
        count = 0
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                count += 1
            except json.JSONDecodeError:
                pass
        return count

    @property
    def dead_letter_path(self) -> Path:
        """Path to the dead-letter file for permanently failed ops."""
        return self._path.with_name(
            self._path.name.replace("-pending-ops.jsonl", "-dead-letter.jsonl")
        )

    def update_last_error(self, op_id: str, error: str) -> None:
        """Persist a truncated error message on a pending op."""
        truncated = error[:200]
        ops = list(self.iter())
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for op in ops:
                if op.id == op_id:
                    op.last_error = truncated
                f.write(op.model_dump_json() + "\n")

    def increment_attempt(self, op_id: str) -> int:
        """Increment attempt_count for an op. Returns the new count (0 if not found)."""
        ops = list(self.iter())
        new_count = 0
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for op in ops:
                if op.id == op_id:
                    op.attempt_count += 1
                    new_count = op.attempt_count
                f.write(op.model_dump_json() + "\n")
        return new_count

    def move_to_dead_letter(self, op_id: str) -> None:
        """Move op to dead-letter file; remove from active queue."""
        ops = list(self.iter())
        target = next((op for op in ops if op.id == op_id), None)
        if target is None:
            return
        self.dead_letter_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dead_letter_path.open("a", encoding="utf-8") as f:
            f.write(target.model_dump_json() + "\n")
        remaining = [op for op in ops if op.id != op_id]
        with self._path.open("w", encoding="utf-8") as f:
            for op in remaining:
                f.write(op.model_dump_json() + "\n")

    def iter_dead_letter(self) -> Iterator[PendingOp]:
        """Iterate dead-letter ops in order. Skips unparseable lines (AR-Q1)."""
        if not self.dead_letter_path.exists():
            return
        for line in self.dead_letter_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data: dict[str, Any] = json.loads(line)
                yield PendingOp.model_validate(data)
            except (json.JSONDecodeError, Exception):  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("Skipping unparseable dead-letter op: %.80s", line)

    def clear_dead_letter(self) -> int:
        """Remove all dead-letter ops. Returns the count removed."""
        if not self.dead_letter_path.exists():
            return 0
        count = sum(
            1
            for line in self.dead_letter_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        self.dead_letter_path.write_text("", encoding="utf-8")
        return count

    def clear(self) -> int:
        """Remove all pending ops. Returns the count of ops removed."""
        count = self.pending_count()
        if self._path.exists():
            self._path.write_text("", encoding="utf-8")
        return count

    def salvage_corrupt_lines(self) -> list[str]:
        """Remove unparseable lines from the file and return their raw text.

        Complements :meth:`iter` (which silently skips corrupt lines under
        AR-Q1). This method lets callers route raw corrupt bytes to a
        dead-letter destination instead of losing them on the next rewrite.

        Returns a list of stripped raw line strings that failed to parse as
        ``PendingOp``. If any corrupt lines are found, the file is rewritten
        with only the valid entries. No-op when the file does not exist or
        contains no corrupt lines.
        """
        if not self._path.exists():
            return []
        corrupt: list[str] = []
        valid: list[PendingOp] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data: dict[str, Any] = json.loads(stripped)
                valid.append(PendingOp.model_validate(data))
            except (json.JSONDecodeError, Exception):  # noqa: BLE001
                corrupt.append(stripped)
        if not corrupt:
            return []
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for op in valid:
                f.write(op.model_dump_json() + "\n")
        return corrupt
