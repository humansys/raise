"""Shared WorkLifecycle emission for MCP handlers — S7884.6 (ADR-093 K3).

Single emission helper for every composite handler (pipeline advance,
story bookends). Populates the correlation fields the consumers query
by (skip-window S3008.5, flow analysis): branch, commit, session,
mission. Callers wrap in ``suppress(Exception)`` — emission must never
break a handler (ADR-039).
"""

from __future__ import annotations

import logging
import subprocess
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.telemetry.schemas import WorkLifecycle

logger = logging.getLogger(__name__)


def _git_value(cwd: str | None, *args: str) -> str | None:
    """Run git with the given args in cwd (None = process CWD, same as before)."""
    try:
        proc = subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() or None


def emit_work_lifecycle(
    work_type: str,
    work_id: str,
    event: str,
    phase_id: str,
    *,
    task: str | None = None,
    cwd: str | None = None,
    blocker: str | None = None,
) -> None:
    """Emit a WorkLifecycle signal with full correlation fields.

    ``phase_id`` is the raw pipeline phase — normalized via PHASE_MAP
    before storage so it always satisfies the schema literal.

    Args:
        work_type: Work type (e.g. "story", "epic", "task").
        work_id: Work identifier (e.g. "S8370.1").
        event: Lifecycle event (e.g. "start", "complete").
        phase_id: Raw pipeline phase — normalized via PHASE_MAP.
        task: Optional task identity within the phase (RAISE-2879 / S8370.1).
        cwd: Working directory for git resolution (None = process CWD, S8370.3/T1).
        blocker: Why work is blocked, for ``event="blocked"`` (RAISE-15986).
            The reason belongs here, not in ``phase_id`` — ``phase`` is a
            closed schema literal and an unmapped value raises before the
            signal is ever written.
    """
    from raise_cli._agent_session import discover_agent_session_id
    from raise_cli.telemetry import emitter as _emitter
    from raise_cli.telemetry.phase_map import normalize_phase
    from raise_cli.telemetry.schemas import WorkLifecycle

    lifecycle = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type,  # type: ignore[arg-type]
        work_id=work_id,
        event=event,  # type: ignore[arg-type]
        phase=normalize_phase(work_type, phase_id),  # type: ignore[arg-type]
        task=task,
        blocker=blocker,
        branch=_git_value(cwd, "branch", "--show-current"),
        commit=_git_value(cwd, "rev-parse", "HEAD"),
        agent_session_id=discover_agent_session_id(),
        mission_id=None,
    )
    _emitter.emit(lifecycle)
    _dispatch_work_hook(lifecycle, cwd)


def _dispatch_work_hook(lifecycle: WorkLifecycle, cwd: str | None) -> None:
    """Bridge the telemetry signal onto the hook bus — RAISE-15986.

    Two emission paths existed and only ``cli/commands/signal.py::emit_work``
    dispatched hooks. Every pipeline/MCP caller uses *this* module, so
    ``work:lifecycle`` subscribers never observed governed work — most
    visibly ``GraphAutoUpdateHook`` (ADR-085), whose complete+close trigger
    was satisfied in the data but never delivered. The knowledge graph
    therefore only ever rebuilt when someone ran ``rai graph build`` by hand.

    Dispatch is unconditional; filtering is each hook's own business. It is
    also strictly best-effort and runs *after* telemetry: the signal record
    is the durable artifact, hook side effects are not, and a rebuild must
    never fail a close (ADR-039).
    """
    try:
        from raise_cli.hooks.emitter import create_emitter
        from raise_cli.hooks.events import WorkLifecycleEvent

        emitter = create_emitter()
        emitter.emit(
            WorkLifecycleEvent(
                work_type=lifecycle.work_type,
                work_id=lifecycle.work_id,
                event=lifecycle.event,
                phase=lifecycle.phase,
                mission_id=lifecycle.mission_id or "",
                task=lifecycle.task or "",
                branch=lifecycle.branch or "",
                working_dir=cwd or "",
            )
        )
    except Exception:  # noqa: BLE001 — hook dispatch must never break a caller
        logger.warning("Hook dispatch failed for work:lifecycle event", exc_info=True)


def emit_cost_kpi(
    avg_cost: float | None,
    median_cost: float | None,
    p95_cost: float | None,
    stories_count: int,
    since: str | None,
    until: str | None,
    kpi_target: float = 18.0,
) -> None:
    """Emit a cost_kpi signal recording KPI validation result.

    Uses work_lifecycle with work_type='cost_kpi' so it is stored in SQLite
    and forwarded to raise-server when connected. The task field carries the
    key stats as a compact JSON blob for downstream querying.
    """
    import json

    from raise_cli._agent_session import discover_agent_session_id
    from raise_cli.telemetry import emitter as _emitter
    from raise_cli.telemetry.schemas import WorkLifecycle

    kpi_met = avg_cost is not None and avg_cost <= kpi_target
    payload_task = json.dumps(
        {
            "avg": round(avg_cost, 4) if avg_cost is not None else None,
            "median": round(median_cost, 4) if median_cost is not None else None,
            "p95": round(p95_cost, 4) if p95_cost is not None else None,
            "n": stories_count,
            "target": kpi_target,
            "met": kpi_met,
            "since": since,
            "until": until,
        },
        separators=(",", ":"),
    )
    lifecycle = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type="cost_kpi",
        work_id="cost-per-story",
        event="complete",
        phase="close",
        task=payload_task,
        agent_session_id=discover_agent_session_id(),
    )
    _emitter.emit(lifecycle)
