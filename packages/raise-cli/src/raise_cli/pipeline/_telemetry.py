"""Pipeline telemetry — OTEL traces for phase transitions.

Emits one span per phase completion with pipeline.* attributes.
Uses ConsoleSpanExporter by default (zero-config).

opentelemetry is an optional dependency ([observability] extra).
When not installed, all emissions are silent no-ops.

Story: S1305.5 — Telemetry via Lifecycle Hooks (RAISE-1311)
Epic: E1305 — MCP Skill Runtime
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.hooks.emitter import EventEmitter

_log = logging.getLogger(__name__)

_TRACER_NAME = "rai-workspace"

_has_otel = False
_default_provider: object | None = None

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

    # Default provider: ConsoleSpanExporter MUST write to stderr, not stdout.
    # rai-workspace runs as an MCP subprocess using stdio transport, so stdout is
    # reserved for JSON-RPC. OTEL's ConsoleSpanExporter defaults to out=sys.stdout,
    # which corrupts the transport and disconnects Claude Code (RAISE-1999).
    _default_provider = TracerProvider()
    _default_provider.add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter(out=sys.stderr))
    )
    trace.set_tracer_provider(_default_provider)
    _has_otel = True
except ImportError:
    _log.debug("opentelemetry not installed — pipeline telemetry disabled")


def emit_phase_transition(
    *,
    pipeline_name: str,
    run_id: str,
    issue: str,
    phase_completed: str,
    phase_next: str | None,
    duration_seconds: float,
    gate_type: str | None,
    gate_result: str | None,
    context_nodes: int,
    mission_id: str = "",
    tracer_provider: object | None = None,
    event_emitter: EventEmitter | None = None,
) -> None:
    """Emit an OTEL span for a completed phase transition.

    Args:
        pipeline_name: Pipeline being executed (e.g. "story", "bugfix").
        run_id: Unique identifier of the pipeline run.
        issue: Jira issue key associated with the run.
        phase_completed: ID of the phase that just finished.
        phase_next: ID of the next phase, or None if this was the last.
        duration_seconds: Wall-clock time spent in the completed phase.
        gate_type: Type of gate on the completed phase (e.g. "hitl"), or None.
        gate_result: "passed"/"failed"/etc. for the gate, or None when no gate.
        context_nodes: Count of graph/pattern nodes surfaced as phase context.
        mission_id: Active mission ID (empty string when none).
        tracer_provider: Override for testing. Uses default if None.
        event_emitter: When provided, also emits a PipelinePhaseEvent via
            the hook system for HTTP delivery to raise-server (S1997.4 F3 fix).
    """
    if _has_otel:
        from opentelemetry.sdk.trace import TracerProvider as _TracerProvider

        provider: _TracerProvider
        if isinstance(tracer_provider, _TracerProvider):
            provider = tracer_provider
        else:
            assert isinstance(_default_provider, _TracerProvider)  # noqa: S101
            provider = _default_provider
        tracer = provider.get_tracer(_TRACER_NAME)

        with tracer.start_as_current_span(
            f"pipeline.phase.{phase_completed}",
        ) as span:
            span.set_attribute("pipeline.name", pipeline_name)
            span.set_attribute("pipeline.run_id", run_id)
            span.set_attribute("pipeline.issue", issue)
            span.set_attribute("pipeline.phase.name", phase_completed)
            span.set_attribute("pipeline.phase.next", phase_next or "")
            span.set_attribute("pipeline.phase.duration_seconds", duration_seconds)
            span.set_attribute("pipeline.phase.context_nodes", context_nodes)
            if mission_id:
                span.set_attribute("pipeline.mission_id", mission_id)
            if gate_type:
                span.set_attribute("pipeline.phase.gate_type", gate_type)
                span.set_attribute("pipeline.phase.gate_result", gate_result or "")

    # S1997.4: HTTP-emit alongside OTEL (F3 fix — pipeline:phase_entered)
    if event_emitter is not None:
        from raise_cli.hooks.events import PipelinePhaseEvent

        event_emitter.emit(
            PipelinePhaseEvent(
                pipeline_name=pipeline_name,
                run_id=run_id,
                phase=phase_completed,
                phase_next=phase_next,
                issue_id=issue,
                duration_seconds=duration_seconds,
                gate_type=gate_type,
                gate_result=gate_result,
                mission_id=mission_id,
            )
        )
