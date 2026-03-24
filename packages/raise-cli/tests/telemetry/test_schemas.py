"""Tests for telemetry signal schemas.

Tests cover:
- Model instantiation and validation
- JSON serialization/deserialization
- Discriminated union parsing
- Edge cases and optional fields
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import TypeAdapter, ValidationError

from raise_cli.telemetry import (
    CalibrationEvent,
    CommandUsage,
    ErrorEvent,
    SessionEvent,
    Signal,
    SkillEvent,
    WorkLifecycle,
)

# --- Fixtures ---


@pytest.fixture
def now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(UTC)


# --- SkillEvent Tests ---


class TestSkillEvent:
    """Tests for SkillEvent schema."""

    def test_create_start_event(self, now: datetime) -> None:
        """Create a skill start event."""
        event = SkillEvent(timestamp=now, skill="rai-story-design", event="start")

        assert event.type == "skill_event"
        assert event.skill == "rai-story-design"
        assert event.event == "start"
        assert event.duration_sec is None

    def test_invalid_event_type(self, now: datetime) -> None:
        """Invalid event type raises ValidationError."""
        with pytest.raises(ValidationError):
            SkillEvent(timestamp=now, skill="test", event="invalid")  # type: ignore[arg-type]

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = SkillEvent(
            timestamp=now, skill="rai-story-design", event="complete", duration_sec=1200
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "skill_event"
        assert data["skill"] == "rai-story-design"
        assert data["event"] == "complete"
        assert data["duration_sec"] == 1200


# --- SessionEvent Tests ---


class TestSessionEvent:
    """Tests for SessionEvent schema."""

    def test_create_success_event(self, now: datetime) -> None:
        """Create a successful session event."""
        event = SessionEvent(
            timestamp=now,
            session_type="story",
            outcome="success",
            duration_min=90,
            stories=["F9.1", "F9.2"],
        )

        assert event.type == "session_event"
        assert event.session_type == "story"
        assert event.outcome == "success"
        assert event.duration_min == 90
        assert event.stories == ["F9.1", "F9.2"]

    def test_create_partial_event(self, now: datetime) -> None:
        """Create a partial session event."""
        event = SessionEvent(
            timestamp=now, session_type="research", outcome="partial", duration_min=45
        )

        assert event.outcome == "partial"
        assert event.stories == []  # Default empty list

    def test_invalid_outcome(self, now: datetime) -> None:
        """Invalid outcome raises ValidationError."""
        with pytest.raises(ValidationError):
            SessionEvent(
                timestamp=now,
                session_type="test",
                outcome="failed",  # type: ignore[arg-type]
                duration_min=30,
            )

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = SessionEvent(
            timestamp=now,
            session_type="story",
            outcome="success",
            duration_min=60,
            stories=["F9.1"],
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "session_event"
        assert data["stories"] == ["F9.1"]


# --- CalibrationEvent Tests ---


class TestCalibrationEvent:
    """Tests for CalibrationEvent schema."""

    def test_create_calibration_event(self, now: datetime) -> None:
        """Create a calibration event."""
        event = CalibrationEvent(
            timestamp=now,
            story_id="F9.1",
            story_size="XS",
            estimated_min=25,
            actual_min=20,
            velocity=1.25,
        )

        assert event.type == "calibration"
        assert event.story_id == "F9.1"
        assert event.story_size == "XS"
        assert event.estimated_min == 25
        assert event.actual_min == 20
        assert event.velocity == 1.25

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = CalibrationEvent(
            timestamp=now,
            story_id="F9.1",
            story_size="XS",
            estimated_min=25,
            actual_min=20,
            velocity=1.25,
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "calibration"
        assert data["velocity"] == 1.25


# --- ErrorEvent Tests ---


class TestErrorEvent:
    """Tests for ErrorEvent schema."""

    def test_create_recoverable_error(self, now: datetime) -> None:
        """Create a recoverable error event."""
        event = ErrorEvent(
            timestamp=now,
            tool="Bash",
            error_type="command_not_found",
            context="pytest",
            recoverable=True,
        )

        assert event.type == "error_event"
        assert event.tool == "Bash"
        assert event.error_type == "command_not_found"
        assert event.context == "pytest"
        assert event.recoverable is True

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = ErrorEvent(
            timestamp=now,
            tool="Bash",
            error_type="timeout",
            context="long_running_command",
            recoverable=True,
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "error_event"
        assert data["recoverable"] is True


# --- CommandUsage Tests ---


class TestCommandUsage:
    """Tests for CommandUsage schema."""

    def test_create_with_subcommand(self, now: datetime) -> None:
        """Create a command usage event with subcommand."""
        event = CommandUsage(timestamp=now, command="memory", subcommand="query")

        assert event.type == "command_usage"
        assert event.command == "memory"
        assert event.subcommand == "query"

    def test_create_without_subcommand(self, now: datetime) -> None:
        """Create a command usage event without subcommand."""
        event = CommandUsage(timestamp=now, command="version")

        assert event.subcommand is None

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = CommandUsage(timestamp=now, command="context", subcommand="query")
        data = json.loads(event.model_dump_json())

        assert data["type"] == "command_usage"
        assert data["subcommand"] == "query"


# --- WorkLifecycle Tests ---


class TestWorkLifecycle:
    """Tests for WorkLifecycle schema (unified Lean flow analysis)."""

    def test_create_story_start_event(self, now: datetime) -> None:
        """Create a story start event."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="story",
            work_id="F9.4",
            event="start",
            phase="design",
        )

        assert event.type == "work_lifecycle"
        assert event.work_type == "story"
        assert event.work_id == "F9.4"
        assert event.event == "start"
        assert event.phase == "design"
        assert event.blocker is None

    def test_invalid_work_type(self, now: datetime) -> None:
        """Invalid work type raises ValidationError."""
        with pytest.raises(ValidationError):
            WorkLifecycle(
                timestamp=now,
                work_type="sprint",  # type: ignore[arg-type]
                work_id="S1",
                event="start",
                phase="design",
            )

    def test_invalid_event_type(self, now: datetime) -> None:
        """Invalid event type raises ValidationError."""
        with pytest.raises(ValidationError):
            WorkLifecycle(
                timestamp=now,
                work_type="story",
                work_id="F9.4",
                event="invalid",  # type: ignore[arg-type]
                phase="design",
            )

    def test_invalid_phase(self, now: datetime) -> None:
        """Invalid phase raises ValidationError."""
        with pytest.raises(ValidationError):
            WorkLifecycle(
                timestamp=now,
                work_type="story",
                work_id="F9.4",
                event="start",
                phase="active",  # type: ignore[arg-type] - not valid with normalized phases
            )

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="story",
            work_id="F9.4",
            event="blocked",
            phase="plan",
            blocker="waiting for ADR",
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "work_lifecycle"
        assert data["work_type"] == "story"
        assert data["work_id"] == "F9.4"
        assert data["blocker"] == "waiting for ADR"

    def test_epic_review_phase(self, now: datetime) -> None:
        """Epic can use review phase (normalized from 'close')."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="epic",
            work_id="E9",
            event="complete",
            phase="review",
        )

        assert event.phase == "review"

    def test_epic_implement_phase(self, now: datetime) -> None:
        """Epic can use implement phase (normalized from 'active')."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="epic",
            work_id="E9",
            event="start",
            phase="implement",
        )

        assert event.phase == "implement"


# --- Signal Union Tests ---


class TestSignalUnion:
    """Tests for Signal discriminated union."""

    def test_parse_skill_event(self, now: datetime) -> None:
        """Parse SkillEvent from JSON via discriminated union."""
        data = {
            "type": "skill_event",
            "timestamp": now.isoformat(),
            "skill": "rai-story-design",
            "event": "complete",
            "duration_sec": 1800,
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, SkillEvent)
        assert signal.skill == "rai-story-design"

    def test_parse_session_event(self, now: datetime) -> None:
        """Parse SessionEvent from JSON via discriminated union."""
        data = {
            "type": "session_event",
            "timestamp": now.isoformat(),
            "session_type": "story",
            "outcome": "success",
            "duration_min": 90,
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, SessionEvent)
        assert signal.outcome == "success"

    def test_parse_calibration_event(self, now: datetime) -> None:
        """Parse CalibrationEvent from JSON via discriminated union."""
        data = {
            "type": "calibration",
            "timestamp": now.isoformat(),
            "story_id": "F9.1",
            "story_size": "XS",
            "estimated_min": 25,
            "actual_min": 20,
            "velocity": 1.25,
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, CalibrationEvent)
        assert signal.velocity == 1.25

    def test_parse_error_event(self, now: datetime) -> None:
        """Parse ErrorEvent from JSON via discriminated union."""
        data = {
            "type": "error_event",
            "timestamp": now.isoformat(),
            "tool": "Bash",
            "error_type": "command_not_found",
            "context": "pytest",
            "recoverable": True,
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, ErrorEvent)
        assert signal.tool == "Bash"

    def test_parse_command_usage(self, now: datetime) -> None:
        """Parse CommandUsage from JSON via discriminated union."""
        data = {
            "type": "command_usage",
            "timestamp": now.isoformat(),
            "command": "memory",
            "subcommand": "query",
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, CommandUsage)
        assert signal.command == "memory"

    def test_parse_work_lifecycle_story(self, now: datetime) -> None:
        """Parse WorkLifecycle for story from JSON via discriminated union."""
        data = {
            "type": "work_lifecycle",
            "timestamp": now.isoformat(),
            "work_type": "story",
            "work_id": "F9.4",
            "event": "blocked",
            "phase": "plan",
            "blocker": "waiting for ADR",
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, WorkLifecycle)
        assert signal.work_type == "story"
        assert signal.work_id == "F9.4"
        assert signal.blocker == "waiting for ADR"

    def test_parse_work_lifecycle_epic(self, now: datetime) -> None:
        """Parse WorkLifecycle for epic from JSON via discriminated union."""
        data = {
            "type": "work_lifecycle",
            "timestamp": now.isoformat(),
            "work_type": "epic",
            "work_id": "E9",
            "event": "complete",
            "phase": "review",
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, WorkLifecycle)
        assert signal.work_type == "epic"
        assert signal.work_id == "E9"
        assert signal.phase == "review"

    def test_invalid_type_discriminator(self, now: datetime) -> None:
        """Invalid type discriminator raises ValidationError."""
        data = {
            "type": "unknown_event",
            "timestamp": now.isoformat(),
        }
        adapter = TypeAdapter(Signal)

        with pytest.raises(ValidationError):
            adapter.validate_python(data)
