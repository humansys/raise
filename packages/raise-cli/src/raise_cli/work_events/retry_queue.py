"""WorkEventRetryQueue — persistent retry queue for failed work event POSTs.

Composes two `PendingOpsLog` instances (canonical E1784 pending-ops pattern):
- ``work-events``              — live queue
- ``work-events-dead-letter``  — entries that exhausted the attempt cap

Design: work/epics/e1691-cli-events/stories/s2.3-design.md (S2.3, RAISE-1715)

Divergence from canonical (PAT-E-819): canonical has no attempt cap because
doc publishing is always-recoverable. Work events can fail deterministically
(schema drift → 422 every retry); a cap + dead-letter is the escape valve.

Crash semantics: on a failed drain, the queue appends the attempt-incremented
copy BEFORE removing the old one. A crash in between produces a duplicate
(safe — server dedup via deterministic ``event_id`` from S2.1), never a loss.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from raise_cli.adapters.pending_ops import PendingOpsLog

logger = logging.getLogger(__name__)

ATTEMPT_CAP = 4
DRAIN_BATCH_CAP = 10
_OP_NAME = "post_agent_event"


class WorkEventRetryQueue:
    """Retry queue for failed work event POSTs."""

    def __init__(self, project_root: Path) -> None:
        self._live = PendingOpsLog("work-events", project_root)
        self._dead_letter = PendingOpsLog("work-events-dead-letter", project_root)
        self._stats = {"queued": 0, "drained": 0, "dead_lettered": 0}

    @property
    def stats(self) -> dict[str, int]:
        """Return a copy of the counter dict (queued/drained/dead_lettered)."""
        return dict(self._stats)

    def enqueue(self, event_payload: dict[str, Any], work_item_ref: str | None) -> None:
        """Append a failed POST payload to the live queue for later replay."""
        self._live.append(
            op=_OP_NAME,
            key=work_item_ref or "",
            args={"event": event_payload, "attempts": 0},
        )
        self._stats["queued"] += 1

    def drain(self, post: Callable[[dict[str, Any]], bool]) -> None:
        """Best-effort FIFO drain. ``post(payload) -> success``. Never raises.

        Idempotency contract: on any I/O failure between a successful ``post``
        and ``mark_done``, the entry is re-posted on the next drain. Safe
        because ``event_id`` is deterministic (S2.1) — server-side dedup
        collapses duplicates. No silent loss.
        """
        try:
            # AC5: salvage corrupt entries to dead-letter BEFORE iter drops them.
            self._salvage_corrupt_to_dead_letter()

            drained = 0
            for op in list(self._live.iter()):
                if drained >= DRAIN_BATCH_CAP:
                    break
                event_payload = op.args.get("event") or {}
                attempts = int(op.args.get("attempts", 0))

                try:
                    success = post(event_payload)
                except Exception as exc:  # noqa: BLE001 — replay must not raise
                    logger.warning("retry_queue: post raised for %s — %s", op.id, exc)
                    success = False

                if success:
                    self._live.mark_done(op.id)
                    self._stats["drained"] += 1
                    drained += 1
                    continue

                new_attempts = attempts + 1
                if new_attempts >= ATTEMPT_CAP:
                    # Route to dead-letter: append first, then remove from live.
                    # Crash in between → entry is in BOTH queues on restart;
                    # next drain will re-route (same event_id → server dedup).
                    self._dead_letter.append(
                        op=op.op,
                        key=op.key,
                        args={"event": event_payload, "attempts": new_attempts},
                    )
                    self._live.mark_done(op.id)
                    self._stats["dead_lettered"] += 1
                    logger.warning(
                        "retry_queue: %s hit attempt cap (%d), moved to dead-letter",
                        op.id,
                        new_attempts,
                    )
                else:
                    # Rewrite live entry with incremented attempts.
                    # Append-then-mark_done preserves the entry under a crash.
                    self._live.append(
                        op=op.op,
                        key=op.key,
                        args={"event": event_payload, "attempts": new_attempts},
                    )
                    self._live.mark_done(op.id)
        except Exception:  # noqa: BLE001 — flush errors never block caller
            logger.exception("retry_queue: drain failed (non-fatal)")

    def _salvage_corrupt_to_dead_letter(self) -> None:
        """Route unparseable JSONL lines to dead-letter with a parse_error stamp.

        Without this pass, the next ``mark_done`` would rewrite the live
        file WITHOUT the corrupt lines — silent discard. Called at the top
        of every drain to honor the no-silent-discard contract (AC5 /
        scope MUST NOT).
        """
        corrupt_lines = self._live.salvage_corrupt_lines()
        for raw in corrupt_lines:
            self._dead_letter.append(
                op="corrupt",
                key="",
                args={
                    "event": None,
                    "attempts": ATTEMPT_CAP,
                    "parse_error": "unparseable JSONL",
                    "raw": raw[:500],
                },
            )
            self._stats["dead_lettered"] += 1
            logger.warning(
                "retry_queue: salvaged corrupt line to dead-letter: %.80s", raw
            )
