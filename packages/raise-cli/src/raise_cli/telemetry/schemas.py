"""Pydantic models for telemetry signals.

This module defines the signal schemas for local telemetry collection
as specified in ADR-018. Signals follow OpenTelemetry semantic conventions
for future OTLP export compatibility.

Signal types:
- SkillEvent: Tracks skill invocations (start/complete/abandon)
- SessionEvent: Tracks session outcomes
- CalibrationEvent: Tracks estimate vs actual for velocity calibration
- ErrorEvent: Tracks tool failures
- CommandUsage: Tracks CLI command usage
- WorkLifecycle: Tracks work items (epic/story) through phases (Lean flow analysis)
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AliasChoices, BaseModel, Field

_TIMESTAMP_DESC = "When the event occurred (UTC)"

# Signal vocabulary version (RAISE-16691, S16430.3, D1). Versions the *set* of
# Signal models as a whole, not per-field. History:
#   1.0.0 — S16430.1 baseline: 8 models (SkillEvent, SessionEvent,
#           CalibrationEvent, ErrorEvent, CommandUsage, SessionTopic,
#           WorkLifecycle, TokenUsage) + signal_schema_version infra +
#           WorkLifecycle.caused_by_work_id. Field exists on all 8 models
#           but nothing stamps it by default (nullable, opt-in).
#   1.1.0 — S16430.3: adds GovernanceAuditEvent. Stamped by default only on
#           the new model — re-stamping the other 8 legacy models is a
#           separate follow-up, out of scope here.
SIGNAL_SCHEMA_VERSION = "1.1.0"


class SkillEvent(BaseModel):
    """A skill invocation event.

    Emitted when a skill starts, completes, or is abandoned.

    Attributes:
        type: Discriminator field, always "skill_event".
        timestamp: When the event occurred (UTC).
        skill: Name of the skill (e.g., "story-design").
        event: Event type (start, complete, abandon).
        duration_sec: Duration in seconds (only for complete/abandon).

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = SkillEvent(
        ...     timestamp=datetime.now(timezone.utc),
        ...     skill="story-design",
        ...     event="complete",
        ...     duration_sec=1800
        ... )
        >>> event.type
        'skill_event'
    """

    type: Literal["skill_event"] = "skill_event"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    skill: str = Field(..., description="Name of the skill (e.g., 'story-design')")
    event: Literal["start", "complete", "abandon"] = Field(
        ..., description="Event type"
    )
    duration_sec: int | None = Field(
        default=None, description="Duration in seconds (for complete/abandon)"
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class SessionEvent(BaseModel):
    """A session lifecycle event.

    Emitted when a session closes, capturing its outcome.

    Attributes:
        type: Discriminator field, always "session_event".
        timestamp: When the event occurred (UTC).
        session_type: Type of session (e.g., "story", "research").
        outcome: How the session ended.
        duration_min: Duration in minutes.
        stories: Story IDs worked on during the session.

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = SessionEvent(
        ...     timestamp=datetime.now(timezone.utc),
        ...     session_type="story",
        ...     outcome="success",
        ...     duration_min=90,
        ...     stories=["F9.1", "F9.2"]
        ... )
        >>> event.type
        'session_event'
    """

    type: Literal["session_event"] = "session_event"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    session_type: str = Field(
        ..., description="Type of session (e.g., 'story', 'research')"
    )
    outcome: Literal["success", "partial", "abandoned"] = Field(
        ..., description="How the session ended"
    )
    duration_min: int = Field(..., description="Duration in minutes")
    stories: list[str] = Field(default_factory=list, description="Story IDs worked on")
    agent_session_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("agent_session_id", "cc_session_id"),
        description="Agent session UUID; null when not discoverable",
    )
    source: str | None = Field(
        default=None, description="Agent runtime source (e.g. 'claude_code', 'hermes')"
    )
    mission_id: str | None = Field(
        default=None,
        description="Active mission ID (S2491.11); null when no mission active",
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class CalibrationEvent(BaseModel):
    """A calibration data point for velocity tracking.

    Emitted when a story is completed, comparing estimate to actual.

    Attributes:
        type: Discriminator field, always "calibration".
        timestamp: When the event occurred (UTC).
        story_id: Story identifier (e.g., "F9.1").
        story_size: T-shirt size (XS, S, M, L).
        estimated_min: Estimated duration in minutes.
        actual_min: Actual duration in minutes.
        velocity: Ratio of estimated to actual (>1 means faster than expected).

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = CalibrationEvent(
        ...     timestamp=datetime.now(timezone.utc),
        ...     story_id="F9.1",
        ...     story_size="XS",
        ...     estimated_min=25,
        ...     actual_min=20,
        ...     velocity=1.25
        ... )
        >>> event.velocity
        1.25
    """

    type: Literal["calibration"] = "calibration"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    story_id: str = Field(..., description="Story identifier (e.g., 'F9.1')")
    story_size: str = Field(..., description="T-shirt size (XS, S, M, L)")
    estimated_min: int = Field(..., description="Estimated duration in minutes")
    actual_min: int = Field(..., description="Actual duration in minutes")
    velocity: float = Field(
        ..., description="Ratio of estimated to actual (>1 = faster)"
    )
    agent_session_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("agent_session_id", "cc_session_id"),
        description="Agent session UUID; null when not discoverable",
    )
    source: str | None = Field(
        default=None, description="Agent runtime source (e.g. 'claude_code', 'hermes')"
    )
    mission_id: str | None = Field(
        default=None,
        description="Active mission ID (S2491.11); null when no mission active",
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class ErrorEvent(BaseModel):
    """A tool error event.

    Emitted when a tool fails, for pattern detection.

    Attributes:
        type: Discriminator field, always "error_event".
        timestamp: When the event occurred (UTC).
        tool: Name of the tool that failed (e.g., "Bash", "Read").
        error_type: Type of error (e.g., "command_not_found").
        context: Brief context (no sensitive data).
        recoverable: Whether the error was recoverable.

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = ErrorEvent(
        ...     timestamp=datetime.now(timezone.utc),
        ...     tool="Bash",
        ...     error_type="command_not_found",
        ...     context="pytest",
        ...     recoverable=True
        ... )
        >>> event.recoverable
        True
    """

    type: Literal["error_event"] = "error_event"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    tool: str = Field(..., description="Name of the tool that failed")
    error_type: str = Field(..., description="Type of error")
    context: str = Field(..., description="Brief context (no sensitive data)")
    recoverable: bool = Field(..., description="Whether the error was recoverable")
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class CommandUsage(BaseModel):
    """A CLI command usage event.

    Emitted when a raise CLI command is invoked.

    Attributes:
        type: Discriminator field, always "command_usage".
        timestamp: When the event occurred (UTC).
        command: Main command name (e.g., "memory").
        subcommand: Subcommand name if any (e.g., "query").

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = CommandUsage(
        ...     timestamp=datetime.now(timezone.utc),
        ...     command="memory",
        ...     subcommand="query"
        ... )
        >>> event.command
        'memory'
    """

    type: Literal["command_usage"] = "command_usage"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    command: str = Field(..., description="Main command name (e.g., 'memory')")
    subcommand: str | None = Field(default=None, description="Subcommand name if any")
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class SessionTopic(BaseModel):
    """A session topic marker for HUD timeline.

    Emitted by the raise_session_topic MCP tool to mark what the agent
    is working on during a session.
    """

    type: Literal["session_topic"] = "session_topic"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    kind: str = Field(
        ..., description="Topic kind (e.g., 'implement', 'decide', 'research')"
    )
    topic: str = Field(..., description="Short topic description for HUD timeline")
    agent_session_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("agent_session_id", "cc_session_id"),
        description="Agent session UUID; null when not discoverable",
    )
    source: str | None = Field(
        default=None, description="Agent runtime source (e.g. 'claude_code', 'hermes')"
    )
    mission_id: str | None = Field(
        default=None,
        description="Active mission ID; null when no mission active",
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class WorkLifecycle(BaseModel):
    """A unified work lifecycle event for Lean flow analysis.

    Tracks work items (epics, stories, etc.) through normalized phases to enable:
    - Lead time calculation (start to complete)
    - Wait time detection (gaps between phases)
    - WIP tracking (started but not completed)
    - Bottleneck identification (longest phase)
    - Flow efficiency (active time / lead time)
    - Cross-level analysis (compare epic vs story flow)

    Phases (normalized across all work types):
    - design: Scope definition and specification
    - plan: Task/story decomposition and sequencing
    - implement: Active development work
    - architecture-review / quality-review: Review phases (identity preserved, RAISE-8347)
    - review: Retrospective and learnings

    Attributes:
        type: Discriminator field, always "work_lifecycle".
        timestamp: When the event occurred (UTC).
        work_type: Type of work item (epic, story, etc.).
        work_id: Work item identifier (e.g., "E9", "F9.4").
        event: Lifecycle event type.
        phase: Current phase in the workflow.
        blocker: Description of blocker (only for blocked event).

    Examples:
        >>> from datetime import datetime, timezone
        >>> event = WorkLifecycle(
        ...     timestamp=datetime.now(timezone.utc),
        ...     work_type="story",
        ...     work_id="F9.4",
        ...     event="start",
        ...     phase="design"
        ... )
        >>> event.type
        'work_lifecycle'

        >>> epic = WorkLifecycle(
        ...     timestamp=datetime.now(timezone.utc),
        ...     work_type="epic",
        ...     work_id="E9",
        ...     event="complete",
        ...     phase="review"
        ... )
        >>> epic.work_type
        'epic'

        >>> blocked = WorkLifecycle(
        ...     timestamp=datetime.now(timezone.utc),
        ...     work_type="story",
        ...     work_id="F9.4",
        ...     event="blocked",
        ...     phase="plan",
        ...     blocker="unclear requirements"
        ... )
        >>> blocked.blocker
        'unclear requirements'
    """

    type: Literal["work_lifecycle"] = "work_lifecycle"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    work_type: str = Field(
        ..., description="Type of work item (e.g. 'epic', 'story', 'bugfix')"
    )
    work_id: str = Field(..., description="Work item identifier (e.g., 'E9', 'F9.4')")
    event: Literal[
        "start", "complete", "blocked", "unblocked", "abandoned", "ar-skip"
    ] = Field(..., description="Lifecycle event type")
    phase: Literal[
        "init",
        "design",
        "plan",
        "implement",
        "architecture-review",
        "quality-review",
        "review",
        "close",
    ] = Field(..., description="Current phase in the workflow")
    blocker: str | None = Field(
        default=None, description="Description of blocker (for blocked event)"
    )
    task: str | None = Field(
        default=None,
        description="Task identity within a phase (RAISE-2879); null when not provided",
    )
    branch: str | None = Field(
        default=None,
        description="Git branch name (RAISE-2879); null when not resolvable",
    )
    agent_session_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("agent_session_id", "cc_session_id"),
        description="Agent session UUID; null when not discoverable",
    )
    source: str | None = Field(
        default=None, description="Agent runtime source (e.g. 'claude_code', 'hermes')"
    )
    mission_id: str | None = Field(
        default=None,
        description="Active mission ID (S2491.11); null when no mission active",
    )
    commit: str | None = Field(
        default=None,
        description="Git HEAD commit hash at time of event (S3008.5); null when not resolvable",
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )
    caused_by_work_id: str | None = Field(
        default=None,
        description="Reference to causative work item (bugfix->story linkage)",
    )


class TokenUsage(BaseModel):
    """Token usage record for cost tracking.

    Emitted when a CLI command reports token consumption.
    Always written to SQLite; server replication via standard emit() path.
    """

    type: Literal["token_usage"] = "token_usage"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    story_id: str | None = Field(default=None, description="Story being worked on")
    phase: str | None = Field(default=None, description="Workflow phase")
    output_tokens: int | None = Field(
        default=None, description="Output tokens consumed"
    )
    input_tokens: int | None = Field(default=None, description="Input tokens consumed")
    cache_read_tokens: int | None = Field(default=None, description="Cache read tokens")
    cache_write_tokens: int | None = Field(
        default=None, description="Cache write tokens"
    )
    source: str | None = Field(default=None, description="Agent runtime source")
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    signal_schema_version: str | None = Field(
        default=None,
        description="Signal schema version (semver, e.g. '1.0.0'); None for legacy",
    )


class GovernanceAuditEvent(BaseModel):
    """An immutable governance audit event (RAISE-16691, S16430.3).

    Records a single governance decision — a gate check outcome or an HITL
    resolution — with cryptographic integrity (payload_sha256) so it can be
    forwarded to the server-side append-only audit trail
    (``governance_audit_events``). CLI emits only ``gate_decision`` and
    ``hitl_decision``; ``phase_transition`` and ``artifact_created`` are
    server-side projections, never emitted from here.

    ``detail`` (raw gate output/message) is stored in local SQLite only —
    the server payload excludes it (translator). ``payload_sha256`` proves
    the local record wasn't rewritten without ever transmitting its content.

    Attributes:
        type: Discriminator field, always "governance_audit".
        timestamp: When the event occurred (UTC).
        event_kind: gate_decision | hitl_decision.
        decision: Outcome — pass/fail/skip/crash for gates,
            approve/reject/revise/auto_approve for HITL. None when the caller
            could not normalize a free-text decision (fail-open — no
            emission is ever blocked on vocabulary mismatch).
        subject_id: gate_id | "{pipeline}:{phase_id}" | phase_id.
        run_id: Pipeline run correlation id; None for manual `rai gate check`.
        pipeline_name: Pipeline name, when known.
        workflow_point: e.g. 'before:story:close' (gate_decision only).
        work_item_ref: Jira key of the work item, when resolvable.
        branch: Git branch, best-effort.
        commit: Git commit sha, best-effort.
        actor_kind: Correlation only, never authorization
            (terminal|auto|agent|gate|resume).
        detail: Gate output/message — local SQLite only.
        payload_sha256: sha256 hex digest (64 chars) over the canonical JSON
            of every other field (including `detail`).
        idempotency_key: f"ga:{payload_sha256[:24]}" — deterministic for
            identical (fields+timestamp) tuples, enabling retry-queue replay
            dedup while staying distinct across logically repeated decisions.
        signal_schema_version: Stamped "1.1.0" by default (see module
            SIGNAL_SCHEMA_VERSION history block).

    Examples:
        >>> from raise_cli.telemetry.audit import build_governance_audit_event
        >>> event = build_governance_audit_event(
        ...     event_kind="gate_decision",
        ...     decision="pass",
        ...     subject_id="gate-tests",
        ... )
        >>> event.type
        'governance_audit'
    """

    type: Literal["governance_audit"] = "governance_audit"
    timestamp: datetime = Field(..., description=_TIMESTAMP_DESC)
    event_kind: Literal["gate_decision", "hitl_decision"] = Field(
        ..., description="Kind of governance decision recorded"
    )
    decision: str | None = Field(
        default=None,
        description=(
            "pass|fail|skip|crash (gate_decision) or "
            "approve|reject|revise|auto_approve (hitl_decision)"
        ),
    )
    subject_id: str = Field(
        ..., description="gate_id | '{pipeline}:{phase_id}' | phase_id"
    )
    run_id: str | None = Field(default=None, description="Pipeline run correlation id")
    pipeline_name: str | None = Field(default=None, description="Pipeline name")
    workflow_point: str | None = Field(
        default=None, description="e.g. 'before:story:close' (gate_decision only)"
    )
    work_item_ref: str | None = Field(
        default=None, description="Jira key of the work item, when resolvable"
    )
    branch: str | None = Field(default=None, description="Git branch, best-effort")
    commit: str | None = Field(default=None, description="Git commit sha, best-effort")
    actor_kind: Literal["terminal", "auto", "agent", "gate", "resume"] | None = Field(
        default=None, description="Correlation only, never authorization"
    )
    detail: str | None = Field(
        default=None,
        description="Gate output/message — local SQLite only, never sent to server",
    )
    agent_session_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("agent_session_id", "cc_session_id"),
        description="Agent session UUID; null when not discoverable",
    )
    source: str | None = Field(
        default=None, description="Agent runtime source (e.g. 'claude_code', 'hermes')"
    )
    trace_id: str | None = Field(default=None, description="Trace ID (session scope)")
    span_id: str | None = Field(default=None, description="Span ID (skill scope)")
    payload_sha256: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="sha256 hex digest over canonical JSON of every other field",
    )
    idempotency_key: str = Field(
        ..., description="f'ga:{payload_sha256[:24]}' — deterministic replay key"
    )
    signal_schema_version: str = Field(
        default=SIGNAL_SCHEMA_VERSION,
        description="Signal schema version (semver); stamped by default on this signal",
    )


# Union type for type-safe signal handling
Signal = Annotated[
    SkillEvent
    | SessionEvent
    | CalibrationEvent
    | ErrorEvent
    | CommandUsage
    | SessionTopic
    | WorkLifecycle
    | TokenUsage
    | GovernanceAuditEvent,
    Field(discriminator="type"),
]
"""Union of all signal types with discriminator for type-safe parsing."""
