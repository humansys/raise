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

from pydantic import BaseModel, Field

_TIMESTAMP_DESC = "When the event occurred (UTC)"


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
    work_type: Literal["epic", "story"] = Field(
        ..., description="Type of work item (epic, story)"
    )
    work_id: str = Field(..., description="Work item identifier (e.g., 'E9', 'F9.4')")
    event: Literal["start", "complete", "blocked", "unblocked", "abandoned"] = Field(
        ..., description="Lifecycle event type"
    )
    phase: Literal["init", "design", "plan", "implement", "review", "close"] = Field(
        ..., description="Current phase in the workflow"
    )
    blocker: str | None = Field(
        default=None, description="Description of blocker (for blocked event)"
    )


# Union type for type-safe signal handling
Signal = Annotated[
    SkillEvent
    | SessionEvent
    | CalibrationEvent
    | ErrorEvent
    | CommandUsage
    | WorkLifecycle,
    Field(discriminator="type"),
]
"""Union of all signal types with discriminator for type-safe parsing."""
