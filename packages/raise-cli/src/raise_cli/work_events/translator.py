"""Translate local hook events (ADR-039) to server AgentEventCreate (ADR-046).

Covers the S2.1 subset: story_started, story_closed, session_closed.
Other event families (pipeline/gate/artifact) wire in subsequent stories.

Unsupported or unmappable events return None — the caller logs and drops.

translate_signal() (S3672.1): Signal Pydantic models → AgentEventCreate.
Only WorkLifecycle and SessionEvent have server mappings; others return None.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.hook_bus.events import (
    HookEvent,
    PipelinePhaseEvent,
    SessionCloseEvent,
    SessionStartEvent,
    WorkCloseEvent,
    WorkLifecycleEvent,
    WorkStartEvent,
)
from raise_cli.work_events.ref_resolver import resolve
from raise_cli.work_events.schemas import (
    AgentEventCreate,
    WorkEventType,
    make_event_id,
)

# Jira/backlog issue key shape: PROJECT-NUMBER (e.g. RAISE-1714, ACV2-642,
# MY_PROJ-7). Matches Atlassian MCP schema pattern (allows `_` in prefix).
# Kept local per rule-of-three. Centralize when S2.7 contract test or a third
# consumer needs it — see dev/parking-lot.md § "Centralize issue-key regex".
_WORK_ITEM_REF_RE = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")


def _current_repo_slug() -> str | None:
    """Return the repo slug for the current working directory."""
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_server_slug

    # The local project id is intentionally stable across a server rename and
    # must never be used as the wire/project identity.  Telemetry is routed by
    # the server slug bound in the manifest (with the local slug as a legacy
    # fallback when no binding exists).
    return get_server_slug(resolve_checkout_root())


def translate(
    event: HookEvent, *, db_path: Path | None = None
) -> AgentEventCreate | None:
    """Translate a hook event to a server-bound event. None = skip this event."""
    iso = event.timestamp.isoformat()

    if isinstance(event, WorkStartEvent):
        return _translate_work_start(event, iso, db_path)
    if isinstance(event, WorkCloseEvent):
        return _translate_work_close(event, iso, db_path)
    if isinstance(event, WorkLifecycleEvent):
        return _translate_work_lifecycle(event, iso, db_path)
    if isinstance(event, PipelinePhaseEvent):
        return _translate_pipeline_phase(event, iso)
    if isinstance(event, SessionStartEvent):
        return _translate_session_start(event, iso)
    if isinstance(event, SessionCloseEvent):
        return _translate_session_close(event, iso)
    return None


def _translate_work_start(
    event: WorkStartEvent, iso: str, db_path: Path | None
) -> AgentEventCreate | None:
    if event.work_type != "story":
        return None
    ref = event.issue_key or resolve(event.work_id, db_path=db_path)
    if not ref:
        return None
    payload: dict[str, Any] = {"work_id": event.work_id}
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build("story_started", ref, iso, event.work_id, payload)


def _translate_work_close(
    event: WorkCloseEvent, iso: str, db_path: Path | None
) -> AgentEventCreate | None:
    if event.work_type != "story":
        return None
    ref = event.issue_key or resolve(event.work_id, db_path=db_path)
    if not ref:
        return None
    payload: dict[str, Any] = {"work_id": event.work_id}
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build("story_closed", ref, iso, event.work_id, payload)


def _translate_work_lifecycle(
    event: WorkLifecycleEvent, iso: str, db_path: Path | None
) -> AgentEventCreate | None:
    ref = resolve(event.work_id, db_path=db_path)
    if not ref:
        return None
    payload: dict[str, Any] = {
        "work_type": event.work_type,
        "work_id": event.work_id,
        "event": event.event,
        "phase": event.phase,
        "task": event.task,
        "branch": event.branch,
    }
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build("work_lifecycle", ref, iso, event.work_id, payload)


def _translate_pipeline_phase(
    event: PipelinePhaseEvent,
    iso: str,
) -> AgentEventCreate | None:
    payload: dict[str, Any] = {
        "pipeline_name": event.pipeline_name,
        "run_id": event.run_id,
        "phase": event.phase,
        "phase_next": event.phase_next,
        "duration_seconds": event.duration_seconds,
        "gate_type": event.gate_type,
        "gate_result": event.gate_result,
    }
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build(
        "pipeline_phase_completed",
        event.issue_id or None,
        iso,
        event.run_id,
        payload,
    )


def _translate_session_start(
    event: SessionStartEvent,
    iso: str,
) -> AgentEventCreate | None:
    payload: dict[str, Any] = {
        "session_id": event.session_id,
        "developer": event.developer,
        "agent_name": event.agent_name,
        "model": event.model,
        "branch": event.branch,
        "worktree_path": event.worktree_path,
        "parent_session_id": event.parent_session_id,
        "status": "running",
    }
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build(
        "session_started",
        None,
        iso,
        event.session_id,
        payload,
        session_id=event.session_id,
    )


def _translate_session_close(
    event: SessionCloseEvent, iso: str
) -> AgentEventCreate | None:
    payload: dict[str, Any] = {
        "session_id": event.session_id,
        "outcome": event.outcome,
        "patterns_reinforced": event.patterns_reinforced,
        "session_satisfaction": event.session_satisfaction,
    }
    repo_slug = _current_repo_slug()
    if repo_slug:
        payload["repo_slug"] = repo_slug
    return _build(
        "session_closed",
        None,
        iso,
        event.session_id,
        payload,
        session_id=event.session_id,
    )


def _resolve_session_id() -> str | None:
    """Resolve agent session_id via runtime priority chain."""
    return discover_agent_session_id()


def _build(
    event_type: WorkEventType,
    ref: str | None,
    iso: str,
    source: str,
    payload: dict[str, Any],
    *,
    session_id: str | None = None,
) -> AgentEventCreate | None:
    if ref is not None and not _WORK_ITEM_REF_RE.match(ref):
        return None
    sid = session_id or _resolve_session_id()
    return AgentEventCreate(
        event_type=event_type,
        payload=payload,
        work_item_ref=ref,
        event_id=make_event_id(
            event_type=event_type,
            work_item_ref=ref,
            iso_timestamp=iso,
            source_id=source,
        ),
        session_id=sid,
    )


# ---------------------------------------------------------------------------
# Signal → AgentEventCreate (S3672.1 — UnifiedEmitter server path)
# ---------------------------------------------------------------------------


def translate_signal(
    signal: Any, *, session_id: str | None = None
) -> AgentEventCreate | None:
    """Translate a Pydantic Signal to AgentEventCreate for server POST.

    WorkLifecycle and SessionEvent have server mappings.
    All other Signal types return None (SQLite-only).
    """
    from raise_cli.telemetry.schemas import (
        GovernanceAuditEvent,
        SessionEvent,
        TokenUsage,
        WorkLifecycle,
    )

    iso = signal.timestamp.isoformat()
    sid = session_id or _resolve_session_id()

    if isinstance(signal, WorkLifecycle):
        payload: dict[str, Any] = {
            "work_type": signal.work_type,
            "work_id": signal.work_id,
            "event": signal.event,
            "phase": signal.phase,
            "task": signal.task,
            "branch": signal.branch,
            "agent_session_id": signal.agent_session_id,
            "source": signal.source,
            "mission_id": signal.mission_id,
        }
        repo_slug = _current_repo_slug()
        if repo_slug:
            payload["repo_slug"] = repo_slug
        return _build(
            "work_lifecycle",
            resolve(signal.work_id),
            iso,
            signal.work_id,
            payload,
            session_id=sid,
        )

    if isinstance(signal, SessionEvent):
        payload = {
            "session_type": signal.session_type,
            "outcome": signal.outcome,
            "duration_min": signal.duration_min,
            "stories": signal.stories,
            "agent_session_id": signal.agent_session_id,
            "source": signal.source,
            "mission_id": signal.mission_id,
        }
        repo_slug = _current_repo_slug()
        if repo_slug:
            payload["repo_slug"] = repo_slug
        return _build(
            "session_closed",
            None,
            iso,
            signal.agent_session_id or "unknown",
            payload,
            session_id=sid,
        )

    if isinstance(signal, GovernanceAuditEvent):
        payload = {
            "occurred_at": iso,
            "event_kind": signal.event_kind,
            "decision": signal.decision,
            "subject_id": signal.subject_id,
            "run_id": signal.run_id,
            "pipeline_name": signal.pipeline_name,
            "workflow_point": signal.workflow_point,
            "branch": signal.branch,
            "commit": signal.commit,
            "actor_kind": signal.actor_kind,
            "agent_session_id": signal.agent_session_id,
            "source": signal.source,
            "signal_schema_version": signal.signal_schema_version,
            # Integrity fields — server-side projection (SD5) persists these
            # onto governance_audit_events.{payload_sha256,idempotency_key}.
            "payload_sha256": signal.payload_sha256,
            "idempotency_key": signal.idempotency_key,
            # No `detail` — raw gate output/message stays local-only (D2).
        }
        repo_slug = _current_repo_slug()
        if repo_slug:
            payload["repo_slug"] = repo_slug
        ref = resolve(signal.work_item_ref) if signal.work_item_ref else None
        return AgentEventCreate(
            event_type="governance_audit",
            payload=payload,
            work_item_ref=ref,
            event_id=signal.payload_sha256[:16],
            session_id=sid,
        )

    if isinstance(signal, TokenUsage):
        payload = {
            "story_id": signal.story_id,
            "phase": signal.phase,
            "input_tokens": signal.input_tokens,
            "output_tokens": signal.output_tokens,
            "cache_read_tokens": signal.cache_read_tokens,
            "cache_write_tokens": signal.cache_write_tokens,
            "source": signal.source,
            "trace_id": signal.trace_id,
            "span_id": signal.span_id,
        }
        repo_slug = _current_repo_slug()
        if repo_slug:
            payload["repo_slug"] = repo_slug
        return _build(
            "token_usage",
            resolve(signal.story_id) if signal.story_id else None,
            iso,
            signal.source or "unknown",
            payload,
            session_id=sid,
        )

    return None
