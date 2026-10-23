"""Work events module — bridge between local telemetry and server event contract.

Implements ADR-048 (CLI -> Server Event Bridge). Translates a subset of
local lifecycle hook events (ADR-018 / ADR-039) to AgentEventCreate events
(ADR-046) and posts them to the raise-server.

Public API is populated as subsequent tasks land:
- T1 (S2.1): schemas
- T2 (S2.1): ref_resolver
- T3 (S2.1): translator
- T4 (S2.1): ServerEmitHook emitter
"""

from __future__ import annotations

from raise_cli.work_events.backfill import (
    BackfillStats,
    RunFile,
    RunPhase,
    iter_events,
    scan_runs,
)
from raise_cli.work_events.ref_resolver import resolve
from raise_cli.work_events.retry_queue import WorkEventRetryQueue
from raise_cli.work_events.schemas import (
    MAX_PAYLOAD_BYTES,
    SCHEMA_VERSION,
    AgentEventCreate,
    AgentEventResponse,
    WorkEventType,
    make_event_id,
)
from raise_cli.work_events.translator import translate

__all__ = [
    "MAX_PAYLOAD_BYTES",
    "SCHEMA_VERSION",
    "AgentEventCreate",
    "AgentEventResponse",
    "BackfillStats",
    "RunFile",
    "RunPhase",
    "WorkEventRetryQueue",
    "WorkEventType",
    "iter_events",
    "make_event_id",
    "resolve",
    "scan_runs",
    "translate",
]


def __getattr__(name: str) -> object:
    """Lazy backward compat alias — avoids circular import at package init."""
    if name == "ServerEmitHook":
        from raise_cli.telemetry.emitter import UnifiedEmitter

        return UnifiedEmitter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
