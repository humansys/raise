"""Typed lifecycle event definitions.

Each event is a frozen dataclass with a specific payload type.
Events use frozen dataclasses (not Pydantic) because they are internal
infrastructure, not boundary objects.

Architecture: ADR-039 §2 (Typed events as frozen dataclasses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class HookEvent:
    """Base class for all lifecycle events.

    Subclasses set ``event_name`` via a class-level default with ``init=False``.
    ``timestamp`` defaults to now(UTC) but can be overridden for testing.
    """

    event_name: str = field(init=False, default="")
    timestamp: datetime = field(default_factory=_now_utc)


@dataclass(frozen=True)
class HookResult:
    """Result returned by a hook handler.

    Attributes:
        status: ``ok`` (success), ``abort`` (request operation abort,
                only valid for ``before:`` events), or ``error`` (handler failed).
        message: Human-readable detail (required for abort/error).
    """

    status: Literal["ok", "abort", "error"] = "ok"
    message: str = ""


@dataclass(frozen=True)
class EmitResult:
    """Aggregate result from dispatching an event to all handlers.

    Attributes:
        aborted: True if a handler requested abort on a ``before:`` event.
        abort_message: Reason for abort.
        handler_errors: Error messages from handlers that raised exceptions.
    """

    aborted: bool = False
    abort_message: str = ""
    handler_errors: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Concrete events — S248.1 initial set (2 of 9 after-events)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SessionStartEvent(HookEvent):
    """Emitted after a session starts."""

    event_name: Literal["session:start"] = field(  # type: ignore[assignment]
        default="session:start", init=False
    )
    session_id: str = ""
    developer: str = ""


@dataclass(frozen=True)
class GraphBuildEvent(HookEvent):
    """Emitted after a graph build completes."""

    event_name: Literal["graph:build"] = field(  # type: ignore[assignment]
        default="graph:build", init=False
    )
    project_path: Path = field(default_factory=lambda: Path("."))
    node_count: int = 0
    edge_count: int = 0
