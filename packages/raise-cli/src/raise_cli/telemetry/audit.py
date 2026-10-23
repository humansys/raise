"""Governance audit event emission (RAISE-16691, S16430.3).

Emits ``GovernanceAuditEvent`` signals for gate decisions and HITL
resolutions via the existing ``UnifiedEmitter`` path (SD1 — no parallel
POST endpoint). Every emission helper is fail-open: audit emission can
NEVER alter a gate outcome, block a pipeline, or reject a telemetry POST.
Every helper is wrapped in ``try/except Exception: logger.debug`` for
exactly that reason.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

from raise_cli.telemetry.emitter import EmitResult, UnifiedEmitter, default_emitter
from raise_cli.telemetry.schemas import SIGNAL_SCHEMA_VERSION, GovernanceAuditEvent


class _GateResultLike(Protocol):
    """Structural type for ``gates.models.GateResult`` (RAISE-16340 layering).

    ``telemetry`` may not import ``gates`` (5-layer model) — this Protocol
    avoids that dependency while staying precisely typed against the real
    shape ``emit_gate_report`` receives. Declared via read-only properties
    (not plain attributes) so frozen dataclasses — ``GateResult`` included —
    satisfy it structurally; a plain-attribute Protocol requires read+write
    access, which pyright treats frozen dataclass fields as failing.
    """

    @property
    def gate_id(self) -> str: ...
    @property
    def passed(self) -> bool: ...
    @property
    def skipped(self) -> bool: ...
    @property
    def message(self) -> str: ...


class _GateSkipLike(Protocol):
    """Structural type for ``gates.execution.GateSkip``."""

    @property
    def gate_id(self) -> str: ...
    @property
    def reason(self) -> str: ...


class _GatePointReportLike(Protocol):
    """Structural type for ``gates.execution.GatePointReport``."""

    @property
    def workflow_point(self) -> str | None: ...
    @property
    def results(self) -> Sequence[_GateResultLike]: ...
    @property
    def skips(self) -> Sequence[_GateSkipLike]: ...


logger = logging.getLogger(__name__)

GateDecision = Literal["pass", "fail", "skip", "crash"]
HitlDecisionValue = Literal["approve", "reject", "revise", "auto_approve"]

_HITL_DECISION_VOCAB: frozenset[str] = frozenset(
    {"approve", "reject", "revise", "auto_approve"}
)


def _canonical_json(data: dict[str, Any]) -> str:
    """Deterministic JSON — stable across key order, always the same bytes."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def normalize_hitl_decision(raw: str) -> str | None:
    """Best-effort normalize a free-text HITL decision to the audit vocabulary.

    Journal-only directional decisions (``_decide_once`` / ``pipeline_decision``,
    RAISE-15048) carry arbitrary free text, not the closed HitlDecision literal.
    Returns None when no match is found — ``decision`` is nullable on the audit
    row precisely for this case (fail-open: an unrecognized string never blocks
    emission, it just carries no decision).
    """
    lowered = raw.strip().lower().replace("-", "_")
    if lowered in _HITL_DECISION_VOCAB:
        return lowered
    if "auto" in lowered and "approv" in lowered:
        return "auto_approve"
    if "approv" in lowered:
        return "approve"
    if "reject" in lowered:
        return "reject"
    if "revis" in lowered:
        return "revise"
    return None


def build_governance_audit_event(
    *,
    event_kind: Literal["gate_decision", "hitl_decision"],
    decision: str | None,
    subject_id: str,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    workflow_point: str | None = None,
    work_item_ref: str | None = None,
    branch: str | None = None,
    commit: str | None = None,
    actor_kind: Literal["terminal", "auto", "agent", "gate", "resume"] | None = None,
    detail: str | None = None,
    agent_session_id: str | None = None,
    source: str | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
    timestamp: datetime | None = None,
) -> GovernanceAuditEvent:
    """Construct a ``GovernanceAuditEvent`` with integrity fields computed.

    ``payload_sha256`` is a sha256 hex digest over the canonical JSON of every
    field EXCEPT the two integrity fields themselves (they don't exist yet at
    hash time). ``idempotency_key`` is deterministic from that hash, so retry
    replays of the same object dedup, while two logically identical decisions
    at different times (distinct ``timestamp`` in the hash input) get distinct
    keys.
    """
    ts = timestamp or datetime.now(UTC)
    base: dict[str, Any] = {
        "type": "governance_audit",
        "timestamp": ts.isoformat(),
        "event_kind": event_kind,
        "decision": decision,
        "subject_id": subject_id,
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "workflow_point": workflow_point,
        "work_item_ref": work_item_ref,
        "branch": branch,
        "commit": commit,
        "actor_kind": actor_kind,
        "detail": detail,
        "agent_session_id": agent_session_id,
        "source": source,
        "trace_id": trace_id,
        "span_id": span_id,
        "signal_schema_version": SIGNAL_SCHEMA_VERSION,
    }
    payload_sha256 = hashlib.sha256(_canonical_json(base).encode("utf-8")).hexdigest()
    idempotency_key = f"ga:{payload_sha256[:24]}"

    return GovernanceAuditEvent(
        timestamp=ts,
        event_kind=event_kind,
        decision=decision,
        subject_id=subject_id,
        run_id=run_id,
        pipeline_name=pipeline_name,
        workflow_point=workflow_point,
        work_item_ref=work_item_ref,
        branch=branch,
        commit=commit,
        actor_kind=actor_kind,
        detail=detail,
        agent_session_id=agent_session_id,
        source=source,
        trace_id=trace_id,
        span_id=span_id,
        payload_sha256=payload_sha256,
        idempotency_key=idempotency_key,
    )


def emit_gate_decision(
    *,
    gate_id: str,
    decision: GateDecision,
    work_item_ref: str | None = None,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    workflow_point: str | None = None,
    branch: str | None = None,
    commit: str | None = None,
    detail: str | None = None,
    session_id: str | None = None,
    emitter: UnifiedEmitter | None = None,
) -> EmitResult | None:
    """Emit a ``gate_decision`` governance audit event. Fail-open — never raises.

    Returns None (instead of propagating) on any failure — callers must never
    branch on this beyond "best effort" (constraint: audit emission can never
    alter a gate outcome or block a pipeline).
    """
    try:
        event = build_governance_audit_event(
            event_kind="gate_decision",
            decision=decision,
            subject_id=gate_id,
            work_item_ref=work_item_ref,
            run_id=run_id,
            pipeline_name=pipeline_name,
            workflow_point=workflow_point,
            branch=branch,
            commit=commit,
            detail=detail,
        )
        return (emitter or default_emitter).emit(event, session_id=session_id)
    except Exception:  # noqa: BLE001 — fail-open by design (SD3)
        logger.debug("governance audit emission failed (gate_decision)", exc_info=True)
        return None


def emit_gate_report(
    report: _GatePointReportLike,
    *,
    issue_id: str | None,
    session_id: str | None = None,
    emitter: UnifiedEmitter | None = None,
) -> None:
    """Emit one ``gate_decision`` event per result/skip in a ``GatePointReport``.

    Choke point (SD3a): called at the end of ``run_gates_for_point``,
    ``run_gates_by_id``, ``run_all_gates``. Skip semantics:
    ``GateResult.skipped`` -> "skip"; the synthetic
    ``(point:...)`` "no-gates-for-point" marker is noise, never emitted.
    Fail-open — any exception here is swallowed; the caller's report is
    never touched (this function has no return value and runs strictly
    after the report is built).
    """
    try:
        for result in report.results:
            decision: GateDecision = (
                "skip" if result.skipped else ("pass" if result.passed else "fail")
            )
            emit_gate_decision(
                gate_id=result.gate_id,
                decision=decision,
                work_item_ref=issue_id,
                workflow_point=report.workflow_point,
                detail=result.message or None,
                session_id=session_id,
                emitter=emitter,
            )
        for skip in report.skips:
            if skip.reason == "no-gates-for-point":
                continue
            emit_gate_decision(
                gate_id=skip.gate_id,
                decision="skip",
                work_item_ref=issue_id,
                workflow_point=report.workflow_point,
                detail=skip.reason,
                session_id=session_id,
                emitter=emitter,
            )
    except Exception:  # noqa: BLE001 — fail-open by design (SD3)
        logger.debug("governance audit emission failed (gate_report)", exc_info=True)


def emit_hitl_decision(
    *,
    phase_id: str,
    decision: str,
    actor_kind: Literal["terminal", "auto", "agent", "gate", "resume"] | None = None,
    work_item_ref: str | None = None,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    branch: str | None = None,
    commit: str | None = None,
    detail: str | None = None,
    session_id: str | None = None,
    emitter: UnifiedEmitter | None = None,
) -> EmitResult | None:
    """Emit a ``hitl_decision`` governance audit event. Fail-open — never raises.

    ``decision`` is normalized via ``normalize_hitl_decision`` — callers may
    pass either a clean vocabulary value (engine sync/resume sites) or
    arbitrary free text (MCP journal-only decisions); an unmatched string
    yields ``decision=None`` on the emitted event rather than blocking.
    """
    try:
        normalized = normalize_hitl_decision(decision)
        event = build_governance_audit_event(
            event_kind="hitl_decision",
            decision=normalized,
            subject_id=phase_id,
            work_item_ref=work_item_ref,
            run_id=run_id,
            pipeline_name=pipeline_name,
            branch=branch,
            commit=commit,
            actor_kind=actor_kind,
            detail=detail,
        )
        return (emitter or default_emitter).emit(event, session_id=session_id)
    except Exception:  # noqa: BLE001 — fail-open by design (SD3)
        logger.debug("governance audit emission failed (hitl_decision)", exc_info=True)
        return None
