"""PhaseFinishReport — per-phase telemetry DTO and compute function.

Consumes RawSessionWindow from AgentTelemetryAdapter (ADR-062).
Runtime-agnostic: same DTO regardless of which agent produced the data.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from raise_cli.work_events.schemas import AgentEventCreate

from raise_core.runtime.telemetry_adapter import (
    AgentTelemetryAdapter,
    ModelCostBreakdown,
    RawSessionWindow,
)


class PhaseFinishReport(BaseModel):
    """Telemetry report for a single pipeline phase completion."""

    phase: str
    pipeline_name: str
    run_id: str
    runtime: str
    issue: str | None = None
    duration_seconds: float | None = None
    cost_usd: float = 0.0
    boundary_source: str = "phase_timestamps"
    adapter_source: str = "session_data"
    by_model: list[ModelCostBreakdown] = []
    tool_fail_ratio: float | None = None
    edit_revert_files: int = 0
    max_gate_fail_streak: int = 0
    executed: bool = True
    """False only when the phase advanced with neither an agent-reported
    completion nor validated artifact proof — i.e. an impact=low HITL gate
    auto-approve (ADR-093 K2) on a phase with no `validates` configured at
    all, so nothing here can vouch that an agent ran.

    True in every other case: a dispatched agent reported completion on a
    non-gated phase, an explicit gate approval followed validated
    proof-of-work, OR an impact=low auto-approve on a phase that declares
    `validates` — artifact validation runs before the gate branch and
    applies on that path too, so reaching this point with `validates`
    non-empty already means the artifacts were checked and passed
    (RAISE-16031, RAISE-16237)."""


def phase_finish_report(
    project_path: Path,
    *,
    phase: str,
    pipeline_name: str,
    run_id: str,
    started_at: datetime | None,
    completed_at: datetime | None,
    adapter: AgentTelemetryAdapter | None = None,
    issue: str | None = None,
    session_data_override: Path | None = None,
    executed: bool = True,
) -> PhaseFinishReport:
    """Compute a PhaseFinishReport using the given telemetry adapter.

    Args:
        project_path: Project root for session data discovery.
        phase: Pipeline phase name.
        pipeline_name: Pipeline name (e.g. 'story', 'epic').
        run_id: Pipeline run identifier.
        started_at: Phase start timestamp (from run store).
        completed_at: Phase completion timestamp (from run store).
        adapter: Telemetry adapter to use. Auto-discovered if None.
        issue: Optional Jira issue key.
        session_data_override: Explicit session data path (skips find_session_data).
        executed: False only when the advance bypassed proof-of-work with
            nothing to vouch for it (an impact=low HITL auto-approve on a
            phase with no `validates`). An auto-approve backed by validated
            `validates` artifacts, or an approve-driven advance backed by
            validated artifacts, is still real execution — the caller is
            responsible for passing the correct value; see
            PhaseFinishReport.executed (RAISE-16031, RAISE-16237).
    """
    if adapter is None:
        from raise_cli.telemetry.adapter_registry import get_telemetry_adapter

        adapter = get_telemetry_adapter()

    has_timestamps = started_at is not None and completed_at is not None
    boundary_source = "phase_timestamps" if has_timestamps else "session_fallback"

    duration: float | None = None
    if started_at is not None and completed_at is not None:
        duration = (completed_at - started_at).total_seconds()

    source = session_data_override or adapter.find_session_data(project_path)
    window: RawSessionWindow
    adapter_source: str
    if source is not None:
        window = adapter.extract_window(
            source,
            since=started_at,
            until=completed_at,
        )
        adapter_source = "session_data"
    else:
        window = RawSessionWindow()
        # Do NOT overwrite boundary_source here — adapter absence is independent
        # of timestamp availability. Use adapter_source to signal no data. (RAISE-15790)
        adapter_source = "null"

    tool_fail_ratio: float | None = None
    if window.tool_calls > 0:
        tool_fail_ratio = window.tool_failures / window.tool_calls
    elif window.tool_failures > 0:
        tool_fail_ratio = 1.0

    return PhaseFinishReport(
        phase=phase,
        pipeline_name=pipeline_name,
        run_id=run_id,
        runtime=adapter.runtime_name,
        issue=issue,
        duration_seconds=duration,
        cost_usd=window.cost_usd,
        boundary_source=boundary_source,
        adapter_source=adapter_source,
        by_model=window.by_model,
        tool_fail_ratio=tool_fail_ratio,
        edit_revert_files=window.edit_reverts,
        max_gate_fail_streak=window.gate_fail_streak,
        executed=executed,
    )


def build_phase_finish_event(
    report: PhaseFinishReport,
    *,
    session_id: str | None = None,
) -> AgentEventCreate:
    """Build a server-bound phase_finish event from a PhaseFinishReport."""
    from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

    event_id = make_event_id(
        event_type="phase_finish",
        work_item_ref=report.issue,
        iso_timestamp=report.run_id,
        source_id=f"{report.pipeline_name}:{report.phase}",
    )

    payload: dict[str, object] = {
        "phase": report.phase,
        "pipeline_name": report.pipeline_name,
        "run_id": report.run_id,
        "runtime": report.runtime,
        "boundary_source": report.boundary_source,
        "adapter_source": report.adapter_source,
        "cost_usd": report.cost_usd,
        "duration_seconds": report.duration_seconds,
        "tool_fail_ratio": report.tool_fail_ratio,
        "edit_revert_files": report.edit_revert_files,
        "max_gate_fail_streak": report.max_gate_fail_streak,
        "executed": report.executed,
        "by_model": [m.model_dump() for m in report.by_model],
    }
    if report.issue:
        payload["issue"] = report.issue

    return AgentEventCreate(
        event_type="phase_finish",
        payload=payload,
        work_item_ref=report.issue,
        event_id=event_id,
        session_id=session_id,
    )


def format_phase_summary(report: PhaseFinishReport) -> str:
    """Compact one-line summary of a phase finish report for statusline."""
    parts: list[str] = [f"[{report.phase}]"]

    if report.duration_seconds is not None:
        mins = report.duration_seconds / 60
        parts.append(f"{mins:.0f}m" if mins >= 1 else f"{report.duration_seconds:.0f}s")

    parts.append(f"${report.cost_usd:.2f}")

    signals: list[str] = []
    if report.tool_fail_ratio is not None and report.tool_fail_ratio > 0:
        signals.append(f"tf:{report.tool_fail_ratio:.0%}")
    if report.edit_revert_files > 0:
        signals.append(f"er:{report.edit_revert_files}")
    if report.max_gate_fail_streak > 0:
        signals.append(f"gf:{report.max_gate_fail_streak}")

    if signals:
        parts.append(" ".join(signals))

    parts.append(f"@{report.runtime}")

    return " | ".join(parts)
