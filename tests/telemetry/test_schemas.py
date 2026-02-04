"""Tests for telemetry signal schemas.

Tests cover:
- Model instantiation and validation
- JSON serialization/deserialization
- Discriminated union parsing
- Edge cases and optional fields
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

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
    return datetime.now(timezone.utc)


# --- SkillEvent Tests ---


class TestSkillEvent:
    """Tests for SkillEvent schema."""

    def test_create_start_event(self, now: datetime) -> None:
        """Create a skill start event."""
        event = SkillEvent(timestamp=now, skill="feature-design", event="start")

        assert event.type == "skill_event"
        assert event.skill == "feature-design"
        assert event.event == "start"
        assert event.duration_sec is None

    def test_create_complete_event_with_duration(self, now: datetime) -> None:
        """Create a skill complete event with duration."""
        event = SkillEvent(
            timestamp=now, skill="feature-implement", event="complete", duration_sec=1800
        )

        assert event.event == "complete"
        assert event.duration_sec == 1800

    def test_create_abandon_event(self, now: datetime) -> None:
        """Create a skill abandon event."""
        event = SkillEvent(
            timestamp=now, skill="research", event="abandon", duration_sec=600
        )

        assert event.event == "abandon"
        assert event.duration_sec == 600

    def test_invalid_event_type(self, now: datetime) -> None:
        """Invalid event type raises ValidationError."""
        with pytest.raises(ValidationError):
            SkillEvent(timestamp=now, skill="test", event="invalid")  # type: ignore[arg-type]

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = SkillEvent(
            timestamp=now, skill="feature-design", event="complete", duration_sec=1200
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "skill_event"
        assert data["skill"] == "feature-design"
        assert data["event"] == "complete"
        assert data["duration_sec"] == 1200


# --- SessionEvent Tests ---


class TestSessionEvent:
    """Tests for SessionEvent schema."""

    def test_create_success_event(self, now: datetime) -> None:
        """Create a successful session event."""
        event = SessionEvent(
            timestamp=now,
            session_type="feature",
            outcome="success",
            duration_min=90,
            features=["F9.1", "F9.2"],
        )

        assert event.type == "session_event"
        assert event.session_type == "feature"
        assert event.outcome == "success"
        assert event.duration_min == 90
        assert event.features == ["F9.1", "F9.2"]

    def test_create_partial_event(self, now: datetime) -> None:
        """Create a partial session event."""
        event = SessionEvent(
            timestamp=now, session_type="research", outcome="partial", duration_min=45
        )

        assert event.outcome == "partial"
        assert event.features == []  # Default empty list

    def test_create_abandoned_event(self, now: datetime) -> None:
        """Create an abandoned session event."""
        event = SessionEvent(
            timestamp=now, session_type="ideation", outcome="abandoned", duration_min=15
        )

        assert event.outcome == "abandoned"

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
            session_type="feature",
            outcome="success",
            duration_min=60,
            features=["F9.1"],
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "session_event"
        assert data["features"] == ["F9.1"]


# --- CalibrationEvent Tests ---


class TestCalibrationEvent:
    """Tests for CalibrationEvent schema."""

    def test_create_calibration_event(self, now: datetime) -> None:
        """Create a calibration event."""
        event = CalibrationEvent(
            timestamp=now,
            feature_id="F9.1",
            feature_size="XS",
            estimated_min=25,
            actual_min=20,
            velocity=1.25,
        )

        assert event.type == "calibration"
        assert event.feature_id == "F9.1"
        assert event.feature_size == "XS"
        assert event.estimated_min == 25
        assert event.actual_min == 20
        assert event.velocity == 1.25

    def test_velocity_less_than_one(self, now: datetime) -> None:
        """Velocity < 1 means slower than expected."""
        event = CalibrationEvent(
            timestamp=now,
            feature_id="F9.2",
            feature_size="S",
            estimated_min=30,
            actual_min=45,
            velocity=0.67,
        )

        assert event.velocity < 1.0

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = CalibrationEvent(
            timestamp=now,
            feature_id="F9.1",
            feature_size="XS",
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

    def test_create_non_recoverable_error(self, now: datetime) -> None:
        """Create a non-recoverable error event."""
        event = ErrorEvent(
            timestamp=now,
            tool="Read",
            error_type="file_not_found",
            context="config.yaml",
            recoverable=False,
        )

        assert event.recoverable is False

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

    def test_create_feature_start_event(self, now: datetime) -> None:
        """Create a feature start event."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="feature",
            work_id="F9.4",
            event="start",
            phase="design",
        )

        assert event.type == "work_lifecycle"
        assert event.work_type == "feature"
        assert event.work_id == "F9.4"
        assert event.event == "start"
        assert event.phase == "design"
        assert event.blocker is None

    def test_create_epic_start_event(self, now: datetime) -> None:
        """Create an epic start event."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="epic",
            work_id="E9",
            event="start",
            phase="design",
        )

        assert event.type == "work_lifecycle"
        assert event.work_type == "epic"
        assert event.work_id == "E9"

    def test_create_complete_event(self, now: datetime) -> None:
        """Create a complete event."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="feature",
            work_id="F9.4",
            event="complete",
            phase="review",
        )

        assert event.event == "complete"
        assert event.phase == "review"

    def test_create_blocked_event_with_blocker(self, now: datetime) -> None:
        """Create a blocked event with blocker description."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="feature",
            work_id="F9.4",
            event="blocked",
            phase="plan",
            blocker="unclear requirements",
        )

        assert event.event == "blocked"
        assert event.blocker == "unclear requirements"

    def test_create_abandoned_event(self, now: datetime) -> None:
        """Create an abandoned event."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="epic",
            work_id="E9",
            event="abandoned",
            phase="implement",
        )

        assert event.event == "abandoned"

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
                work_type="feature",
                work_id="F9.4",
                event="invalid",  # type: ignore[arg-type]
                phase="design",
            )

    def test_invalid_phase(self, now: datetime) -> None:
        """Invalid phase raises ValidationError."""
        with pytest.raises(ValidationError):
            WorkLifecycle(
                timestamp=now,
                work_type="feature",
                work_id="F9.4",
                event="start",
                phase="active",  # type: ignore[arg-type] - not valid with normalized phases
            )

    def test_serialization(self, now: datetime) -> None:
        """Event serializes to JSON correctly."""
        event = WorkLifecycle(
            timestamp=now,
            work_type="feature",
            work_id="F9.4",
            event="blocked",
            phase="plan",
            blocker="waiting for ADR",
        )
        data = json.loads(event.model_dump_json())

        assert data["type"] == "work_lifecycle"
        assert data["work_type"] == "feature"
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
            "skill": "feature-design",
            "event": "complete",
            "duration_sec": 1800,
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, SkillEvent)
        assert signal.skill == "feature-design"

    def test_parse_session_event(self, now: datetime) -> None:
        """Parse SessionEvent from JSON via discriminated union."""
        data = {
            "type": "session_event",
            "timestamp": now.isoformat(),
            "session_type": "feature",
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
            "feature_id": "F9.1",
            "feature_size": "XS",
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

    def test_parse_work_lifecycle_feature(self, now: datetime) -> None:
        """Parse WorkLifecycle for feature from JSON via discriminated union."""
        data = {
            "type": "work_lifecycle",
            "timestamp": now.isoformat(),
            "work_type": "feature",
            "work_id": "F9.4",
            "event": "blocked",
            "phase": "plan",
            "blocker": "waiting for ADR",
        }
        adapter = TypeAdapter(Signal)
        signal = adapter.validate_python(data)

        assert isinstance(signal, WorkLifecycle)
        assert signal.work_type == "feature"
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
