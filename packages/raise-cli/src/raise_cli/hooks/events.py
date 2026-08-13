"""Typed lifecycle event definitions.

Each event is a frozen dataclass with a specific payload type.
Events use frozen dataclasses (not Pydantic) because they are internal
infrastructure, not boundary objects.

Architecture: ADR-039 §2 (Typed events as frozen dataclasses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


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
# Concrete events
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SessionStartEvent(HookEvent):
    """Emitted after a session starts."""

    event_name: Literal["session:start"] = field(  # type: ignore[assignment]
        default="session:start", init=False
    )
    session_id: str = ""
    developer: str = ""
    agent_name: str = ""
    model: str = ""
    branch: str = ""
    worktree_path: str = ""
    parent_session_id: str = ""


@dataclass(frozen=True)
class SessionCloseEvent(HookEvent):
    """Emitted after a session closes."""

    event_name: Literal["session:close"] = field(  # type: ignore[assignment]
        default="session:close", init=False
    )
    session_id: str = ""
    outcome: str = ""
    patterns_reinforced: int = 0
    session_satisfaction: int = 0


@dataclass(frozen=True)
class PipelinePhaseEvent(HookEvent):
    """Emitted when a pipeline phase completes and transitions to the next."""

    event_name: Literal["pipeline:phase_entered"] = field(  # type: ignore[assignment]
        default="pipeline:phase_entered", init=False
    )
    pipeline_name: str = ""
    run_id: str = ""
    phase: str = ""
    phase_next: str | None = None
    issue_id: str = ""
    duration_seconds: float = 0.0
    gate_type: str | None = None
    gate_result: str | None = None
    mission_id: str = ""


@dataclass(frozen=True)
class GraphBuildEvent(HookEvent):
    """Emitted after a graph build completes."""

    event_name: Literal["graph:build"] = field(  # type: ignore[assignment]
        default="graph:build", init=False
    )
    project_path: Path = field(default_factory=lambda: Path("."))
    node_count: int = 0
    edge_count: int = 0


@dataclass(frozen=True)
class PatternAddedEvent(HookEvent):
    """Emitted after a pattern is added to memory."""

    event_name: Literal["pattern:added"] = field(  # type: ignore[assignment]
        default="pattern:added", init=False
    )
    pattern_id: str = ""
    content: str = ""
    context: str = ""


@dataclass(frozen=True)
class DiscoverScanEvent(HookEvent):
    """Emitted after a discovery scan completes."""

    event_name: Literal["discover:scan"] = field(  # type: ignore[assignment]
        default="discover:scan", init=False
    )
    project_path: Path = field(default_factory=lambda: Path("."))
    language: str = ""
    component_count: int = 0


@dataclass(frozen=True)
class InitCompleteEvent(HookEvent):
    """Emitted after project initialization completes."""

    event_name: Literal["init:complete"] = field(  # type: ignore[assignment]
        default="init:complete", init=False
    )
    project_path: Path = field(default_factory=lambda: Path("."))
    project_name: str = ""


@dataclass(frozen=True)
class AdapterLoadedEvent(HookEvent):
    """Emitted after an adapter is successfully loaded from entry points."""

    event_name: Literal["adapter:loaded"] = field(  # type: ignore[assignment]
        default="adapter:loaded", init=False
    )
    adapter_name: str = ""
    group: str = ""
    adapter_type: str = ""


@dataclass(frozen=True)
class AdapterFailedEvent(HookEvent):
    """Emitted when an adapter fails to load from entry points."""

    event_name: Literal["adapter:failed"] = field(  # type: ignore[assignment]
        default="adapter:failed", init=False
    )
    adapter_name: str = ""
    group: str = ""
    error: str = ""


@dataclass(frozen=True)
class ReleasePublishEvent(HookEvent):
    """Emitted after a release is published."""

    event_name: Literal["release:publish"] = field(  # type: ignore[assignment]
        default="release:publish", init=False
    )
    version: str = ""
    project_path: Path = field(default_factory=lambda: Path("."))


@dataclass(frozen=True)
class WorkLifecycleEvent(HookEvent):
    """Emitted when a work lifecycle signal is recorded.

    Bridges ``rai signal emit-work`` and ``emit_work_lifecycle`` (the
    pipeline/MCP path) to the hook system so hooks can react to
    story/epic lifecycle transitions.
    """

    event_name: Literal["work:lifecycle"] = field(  # type: ignore[assignment]
        default="work:lifecycle", init=False
    )
    work_type: str = ""  # "story" or "epic"
    work_id: str = ""  # e.g. "S325.4", "E325"
    event: str = ""  # "start", "complete", "blocked", etc.
    phase: str = ""  # "design", "plan", "implement", "review", "close"
    mission_id: str = ""
    task: str = ""
    branch: str = ""
    # RAISE-15986: the caller's checkout. In-process (MCP) emitters MUST
    # populate this — the server process CWD is not the agent's worktree,
    # and checkout-scoped hooks (GraphAutoUpdateHook) would otherwise key
    # their work to the wrong partition. Same convention as the
    # ``before:*`` events. Empty means "resolve from process CWD" (CLI).
    working_dir: str = ""


# ---------------------------------------------------------------------------
# Work lifecycle events (S301.6: auto-sync hooks)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkStartEvent(HookEvent):
    """Emitted when a work item (story/epic) starts."""

    event_name: Literal["work:start"] = field(  # type: ignore[assignment]
        default="work:start", init=False
    )
    work_type: str = ""
    work_id: str = ""
    issue_key: str = ""


@dataclass(frozen=True)
class WorkCloseEvent(HookEvent):
    """Emitted when a work item (story/epic) closes."""

    event_name: Literal["work:close"] = field(  # type: ignore[assignment]
        default="work:close", init=False
    )
    work_type: str = ""
    work_id: str = ""
    issue_key: str = ""


# ---------------------------------------------------------------------------
# Before-variant events (AD-6: only release:publish and session:close)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BeforeSessionCloseEvent(HookEvent):
    """Emitted before a session closes. Handlers can abort."""

    event_name: Literal["before:session:close"] = field(  # type: ignore[assignment]
        default="before:session:close", init=False
    )
    session_id: str = ""
    outcome: str = ""
    working_dir: str = ""


@dataclass(frozen=True)
class BeforeBugCloseEvent(HookEvent):
    """Emitted before a bug is closed. Handlers can abort.

    RAISE-12207: engine emits this at the bugfix `close` phase exit so the
    architecture-review gate is engine-forced rather than skill-prose-forced.
    The close-sync postcondition runs separately after the backlog transition.
    ``working_dir`` MUST be populated by the in-process (MCP) emitter — see
    gate_bridge.py.
    """

    event_name: Literal["before:bug:close"] = field(  # type: ignore[assignment]
        default="before:bug:close", init=False
    )
    issue_id: str = ""
    working_dir: str = ""
    # RAISE-12207 (Option B): the agent session id resolved from the run, so the
    # engine-side gate re-check (running in the MCP-server process, where ambient
    # `discover_agent_session_id()` sees the *server's* env, not the agent's)
    # resolves the SAME session-scoped `ar-reviewed` marker the close skill wrote.
    session_id: str | None = None


@dataclass(frozen=True)
class BeforeStoryCloseEvent(HookEvent):
    """Emitted before a story is closed. Handlers run advisory gates only.

    S14263.6 (RAISE-14712): engine emits this at the story pipeline `close`
    phase so ``capability-overlap`` and other ``before:story:close`` gates run
    inside the governed flow — defence in depth before CI. Advisory-only: the
    engine never aborts story close on gate failure (mirrors CI
    ``allow_failure: true``, ADR-130 D2). ``working_dir`` MUST be populated
    by the in-process (MCP) emitter — see gate_bridge.py.
    """

    event_name: Literal["before:story:close"] = field(  # type: ignore[assignment]
        default="before:story:close", init=False
    )
    issue_id: str = ""
    working_dir: str = ""
    session_id: str | None = None


@dataclass(frozen=True)
class BeforeInitiativeValidatedEvent(HookEvent):
    """Emitted before an Initiative advances into Validated. Handlers can abort.

    S14559.1 (RAISE-14588): engine emits this at the initiative pipeline's
    `validated` phase exit so `gate-strategic-fit` is engine-forced rather
    than skill-prose-forced — same mechanism as `before:bug:close`
    (RAISE-12207). `working_dir` MUST be populated by the in-process (MCP)
    emitter — see gate_bridge.py.
    """

    event_name: Literal["before:initiative:validated"] = field(  # type: ignore[assignment]
        default="before:initiative:validated", init=False
    )
    issue_id: str = ""
    working_dir: str = ""
    session_id: str | None = None


@dataclass(frozen=True)
class BeforeInitiativeConcludedEvent(HookEvent):
    """Emitted before an Initiative advances into Concluded. Handlers can abort.

    S14559.1 (RAISE-14588): engine emits this at the initiative pipeline's
    `concluded` phase exit so `gate-child-epics-complete` is engine-forced.
    Same shape/rationale as `BeforeInitiativeValidatedEvent`.
    """

    event_name: Literal["before:initiative:concluded"] = field(  # type: ignore[assignment]
        default="before:initiative:concluded", init=False
    )
    issue_id: str = ""
    working_dir: str = ""
    session_id: str | None = None


@dataclass(frozen=True)
class BeforeReleasePublishEvent(HookEvent):
    """Emitted before a release is published. Handlers can abort."""

    event_name: Literal["before:release:publish"] = field(  # type: ignore[assignment]
        default="before:release:publish", init=False
    )
    version: str = ""
    project_path: Path = field(default_factory=lambda: Path("."))
    working_dir: str = ""


# ---------------------------------------------------------------------------
# Pipeline backlog transition events (RAISE-15267)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BacklogTransitionEvent(HookEvent):
    """Emitted when a pipeline phase successfully applies a backlog transition.

    Only emitted when ``TransitionRecord.outcome == "applied"``.
    Fail-open: emission is wrapped in ``contextlib.suppress(Exception)``.
    """

    event_name: Literal["pipeline:backlog_transition"] = field(  # type: ignore[assignment]
        default="pipeline:backlog_transition", init=False
    )
    run_id: str = ""
    phase_id: str = ""
    issue_key: str = ""
    from_status: str = ""
    to_slug: str = ""


# ---------------------------------------------------------------------------
# MCP events (E338: MCP Platform)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class McpCallEvent(HookEvent):
    """Emitted after an MCP tool call completes (success or failure)."""

    event_name: Literal["mcp:call"] = field(  # type: ignore[assignment]
        default="mcp:call", init=False
    )
    server: str = ""
    tool: str = ""
    success: bool = True
    latency_ms: int = 0
    error: str = ""
    mission_id: str = ""
