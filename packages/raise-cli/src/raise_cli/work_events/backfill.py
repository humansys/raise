"""Backfill historical pipeline runs as pipeline_phase_completed events.

S2.6 (RAISE-1851). Scans `.rai-state/pipeline/runs/*.json`, builds an
AgentEventCreate for each completed phase that has a resolvable
work_item_ref, and returns them for emission by the caller.

Idempotency: each event's id is derived deterministically from
(event_type, work_item_ref, completed_at, f"{run_id}:{phase_id}") via
`make_event_id`. Re-scanning the same runs produces identical event_ids,
which the server dedups via the partial unique index on
(org_id, event_id) (S2.6/T1, migration 005).

This module is deliberately transport-free — it returns events; the CLI
layer wires them to `ServerEmitHook` / `WorkEventRetryQueue`.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

# Mirror the translator's check (kept local per rule-of-three — see
# translator.py notes). Prevents emitting events whose work_item_ref would
# not satisfy the server's 1..255 length bounds or look like a valid key.
_WORK_ITEM_REF_RE = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")


class RunPhase(BaseModel):
    """One phase inside a `.rai-state/pipeline/runs/*.json` ledger file.

    Older runs may omit fields that newer ones include — `extra='ignore'`
    tolerates schema drift. The minimum viable phase has an `id` and a
    `status`; everything else is optional.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    status: str
    skill: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class RunFile(BaseModel):
    """Shape of `.rai-state/pipeline/runs/*.json` the backfill reads."""

    model_config = ConfigDict(extra="ignore")

    run_id: str
    pipeline_name: str | None = None
    issue_id: str | None = None
    phases: list[RunPhase] = Field(default_factory=list)


@dataclass
class BackfillStats:
    """Running counters for a backfill pass.

    scanned: total run JSON files encountered.
    eligible: completed phases with a valid issue_id (ready for emission).
    emitted: POSTs that inserted a new row (server status='ok').
    queued: POSTs that failed transport and landed in the retry queue.
    already_present: POSTs where the event_id already existed on the server.
    skipped: run files that were corrupt or structurally invalid.
    skipped_no_ref: run files missing (or with an invalid) issue_id.
    """

    scanned: int = 0
    eligible: int = 0
    emitted: int = 0
    queued: int = 0
    already_present: int = 0
    skipped: int = 0
    skipped_no_ref: int = 0


def _build_phase_event(run: RunFile, phase: RunPhase) -> AgentEventCreate:
    iso_timestamp = phase.completed_at or ""
    payload: dict[str, object] = {
        "run_id": run.run_id,
        "pipeline_name": run.pipeline_name,
        "phase_id": phase.id,
        "status": phase.status,
    }
    if phase.skill is not None:
        payload["skill"] = phase.skill
    if phase.started_at is not None:
        payload["started_at"] = phase.started_at
    if phase.completed_at is not None:
        payload["completed_at"] = phase.completed_at

    return AgentEventCreate(
        event_type="pipeline_phase_completed",
        work_item_ref=run.issue_id,
        payload=payload,
        event_id=make_event_id(
            event_type="pipeline_phase_completed",
            work_item_ref=run.issue_id,
            iso_timestamp=iso_timestamp,
            source_id=f"{run.run_id}:{phase.id}",
        ),
    )


def iter_events(runs_dir: Path, *, stats: BackfillStats) -> Iterator[AgentEventCreate]:
    """Yield one AgentEventCreate per completed phase with a valid ref.

    Invalid run files (corrupt JSON, Pydantic validation errors, missing
    `phases`) increment `stats.skipped` and are otherwise silent — the CLI
    layer logs and continues. Runs missing `issue_id` (or with a ref that
    does not match `PROJECT-NUMBER`) increment `stats.skipped_no_ref`.
    """
    if not runs_dir.is_dir():
        return
    for path in sorted(runs_dir.glob("*.json")):
        stats.scanned += 1
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            run = RunFile.model_validate(data)
        except (OSError, json.JSONDecodeError, ValidationError):
            stats.skipped += 1
            continue

        if not run.issue_id or not _WORK_ITEM_REF_RE.match(run.issue_id):
            stats.skipped_no_ref += 1
            continue

        for phase in run.phases:
            if phase.status != "done" or not phase.completed_at:
                continue
            yield _build_phase_event(run, phase)


def scan_runs(runs_dir: Path, *, stats: BackfillStats) -> list[AgentEventCreate]:
    """Scan `runs_dir` and return every eligible event, updating `stats`.

    Thin wrapper over `iter_events` that also populates `stats.eligible`.
    Useful when the caller wants a full list upfront (e.g. to apply --limit
    or print a dry-run summary without emitting).
    """
    events = list(iter_events(runs_dir, stats=stats))
    stats.eligible = len(events)
    return events
