"""Tests for telemetry signal writer.

Tests cover:
- Basic emit functionality
- Directory creation
- File locking behavior
- Error handling
- Convenience functions
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from raise_cli.telemetry import (
    CalibrationEvent,
    CommandUsage,
    ErrorEvent,
    SessionEvent,
    SkillEvent,
    emit,
    emit_command_usage,
    emit_error_event,
    emit_skill_event,
)
from raise_cli.telemetry.writer import EmitResult, _get_telemetry_path

# --- Fixtures ---


@pytest.fixture
def temp_telemetry_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for telemetry tests."""
    return tmp_path


@pytest.fixture
def now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(UTC)


# --- Path Helper Tests ---


class TestGetTelemetryPath:
    """Tests for _get_telemetry_path helper."""

    def test_default_path(self, tmp_path: Path) -> None:
        """Returns path under .raise/rai/personal/telemetry/signals.jsonl."""
        path = _get_telemetry_path(tmp_path)

        # Telemetry is personal data per F14.15
        assert path == tmp_path / ".raise/rai/personal/telemetry/signals.jsonl"

    def test_none_uses_cwd(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """None base_path uses current working directory."""
        monkeypatch.chdir(tmp_path)
        path = _get_telemetry_path(None)

        assert path == tmp_path / ".raise/rai/personal/telemetry/signals.jsonl"


# --- Emit Function Tests ---


class TestEmit:
    """Tests for emit() function."""

    def test_emit_skill_event(self, temp_telemetry_dir: Path, now: datetime) -> None:
        """Emit a skill event to signals.jsonl."""
        event = SkillEvent(timestamp=now, skill="rai-story-design", event="start")

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True
        assert result.path is not None
        assert result.path.exists()
        assert result.error is None

        # Verify file contents
        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "skill_event"
        assert data["skill"] == "rai-story-design"
        assert data["event"] == "start"

    def test_emit_session_event(self, temp_telemetry_dir: Path, now: datetime) -> None:
        """Emit a session event."""
        event = SessionEvent(
            timestamp=now,
            session_type="story",
            outcome="success",
            duration_min=90,
            features=["F9.1"],
        )

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "session_event"
        assert data["outcome"] == "success"

    def test_emit_calibration_event(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Emit a calibration event."""
        event = CalibrationEvent(
            timestamp=now,
            story_id="F9.1",
            story_size="XS",
            estimated_min=25,
            actual_min=18,
            velocity=1.4,
        )

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "calibration"
        assert data["velocity"] == 1.4

    def test_emit_error_event(self, temp_telemetry_dir: Path, now: datetime) -> None:
        """Emit an error event."""
        event = ErrorEvent(
            timestamp=now,
            tool="Bash",
            error_type="command_not_found",
            context="pytest",
            recoverable=True,
        )

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "error_event"
        assert data["recoverable"] is True

    def test_emit_command_usage_event(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Emit a command usage event."""
        event = CommandUsage(timestamp=now, command="memory", subcommand="query")

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "command_usage"
        assert data["command"] == "memory"

    def test_creates_directory_if_missing(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Creates .raise/rai/personal/telemetry/ directory if it doesn't exist."""
        event = SkillEvent(timestamp=now, skill="test", event="start")

        # Directory doesn't exist yet (personal telemetry path per F14.15)
        telemetry_dir = temp_telemetry_dir / ".raise/rai/personal/telemetry"
        assert not telemetry_dir.exists()

        result = emit(event, base_path=temp_telemetry_dir)

        assert result.success is True
        assert telemetry_dir.exists()

    def test_appends_multiple_signals(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Multiple emits append to the same file."""
        event1 = SkillEvent(timestamp=now, skill="skill1", event="start")
        event2 = SkillEvent(
            timestamp=now, skill="skill2", event="complete", duration_sec=60
        )
        event3 = CommandUsage(timestamp=now, command="memory")

        emit(event1, base_path=temp_telemetry_dir)
        emit(event2, base_path=temp_telemetry_dir)
        result = emit(event3, base_path=temp_telemetry_dir)

        # Read all lines
        lines = result.path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3

        # Verify each line is valid JSON
        data1 = json.loads(lines[0])
        data2 = json.loads(lines[1])
        data3 = json.loads(lines[2])

        assert data1["skill"] == "skill1"
        assert data2["skill"] == "skill2"
        assert data3["command"] == "memory"


class TestEmitPathTraversal:
    """CWE-23 regression: emit must reject traversal session IDs."""

    def test_emit_rejects_traversal_session_id(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """emit() rejects session_id with path traversal via get_session_dir."""
        event = SkillEvent(timestamp=now, skill="test", event="start")

        with pytest.raises(ValueError, match="path traversal"):
            emit(
                event,
                base_path=temp_telemetry_dir,
                session_id="../../etc",
            )

    def test_emit_rejects_slash_session_id(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """emit() rejects session_id containing forward slashes."""
        event = SkillEvent(timestamp=now, skill="test", event="start")

        with pytest.raises(ValueError, match="path traversal"):
            emit(
                event,
                base_path=temp_telemetry_dir,
                session_id="SES-1/../../tmp/pwned",
            )


class TestEmitPerSession:
    """Tests for per-session telemetry writes."""

    def test_emit_to_per_session_dir(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Emit to sessions/{session_id}/signals.jsonl when session_id provided."""
        event = SkillEvent(timestamp=now, skill="test", event="start")

        result = emit(event, base_path=temp_telemetry_dir, session_id="SES-177")

        assert result.success is True
        expected_path = (
            temp_telemetry_dir
            / ".raise"
            / "rai"
            / "personal"
            / "sessions"
            / "SES-177"
            / "signals.jsonl"
        )
        assert result.path == expected_path
        assert expected_path.exists()

        data = json.loads(expected_path.read_text(encoding="utf-8").strip())
        assert data["skill"] == "test"

    def test_per_session_does_not_write_to_shared(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Per-session emit should NOT write to shared telemetry dir."""
        event = SkillEvent(timestamp=now, skill="test", event="start")

        emit(event, base_path=temp_telemetry_dir, session_id="SES-177")

        shared_path = (
            temp_telemetry_dir
            / ".raise"
            / "rai"
            / "personal"
            / "telemetry"
            / "signals.jsonl"
        )
        assert not shared_path.exists()

    def test_two_sessions_write_independently(
        self, temp_telemetry_dir: Path, now: datetime
    ) -> None:
        """Two sessions write to separate files without interference."""
        event1 = SkillEvent(timestamp=now, skill="session1", event="start")
        event2 = SkillEvent(timestamp=now, skill="session2", event="start")

        emit(event1, base_path=temp_telemetry_dir, session_id="SES-177")
        emit(event2, base_path=temp_telemetry_dir, session_id="SES-178")

        path1 = (
            temp_telemetry_dir
            / ".raise"
            / "rai"
            / "personal"
            / "sessions"
            / "SES-177"
            / "signals.jsonl"
        )
        path2 = (
            temp_telemetry_dir
            / ".raise"
            / "rai"
            / "personal"
            / "sessions"
            / "SES-178"
            / "signals.jsonl"
        )

        data1 = json.loads(path1.read_text(encoding="utf-8").strip())
        data2 = json.loads(path2.read_text(encoding="utf-8").strip())

        assert data1["skill"] == "session1"
        assert data2["skill"] == "session2"


class TestEmitResult:
    """Tests for EmitResult dataclass."""

    def test_success_result(self, tmp_path: Path) -> None:
        """Success result has path and no error."""
        result = EmitResult(success=True, path=tmp_path / "test.jsonl")

        assert result.success is True
        assert result.path is not None
        assert result.error is None

    def test_failure_result(self) -> None:
        """Failure result has error and no path."""
        result = EmitResult(success=False, error="Permission denied")

        assert result.success is False
        assert result.path is None
        assert result.error == "Permission denied"


# --- Convenience Function Tests ---


class TestEmitSkillEvent:
    """Tests for emit_skill_event convenience function."""

    def test_emit_start_event(self, temp_telemetry_dir: Path) -> None:
        """Emit a skill start event."""
        result = emit_skill_event(
            skill="rai-story-design",
            event="start",
            base_path=temp_telemetry_dir,
        )

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["type"] == "skill_event"
        assert data["skill"] == "rai-story-design"
        assert data["event"] == "start"
        assert data["duration_sec"] is None

    def test_emit_complete_event_with_duration(self, temp_telemetry_dir: Path) -> None:
        """Emit a skill complete event with duration."""
        result = emit_skill_event(
            skill="rai-story-implement",
            event="complete",
            duration_sec=1800,
            base_path=temp_telemetry_dir,
        )

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["event"] == "complete"
        assert data["duration_sec"] == 1800


class TestEmitCommandUsage:
    """Tests for emit_command_usage convenience function."""

    def test_emit_with_subcommand(self, temp_telemetry_dir: Path) -> None:
        """Emit command usage with subcommand."""
        result = emit_command_usage(
            command="memory",
            subcommand="query",
            base_path=temp_telemetry_dir,
        )

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["command"] == "memory"
        assert data["subcommand"] == "query"

    def test_emit_without_subcommand(self, temp_telemetry_dir: Path) -> None:
        """Emit command usage without subcommand."""
        result = emit_command_usage(
            command="version",
            base_path=temp_telemetry_dir,
        )

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["command"] == "version"
        assert data["subcommand"] is None


class TestEmitErrorEvent:
    """Tests for emit_error_event convenience function."""

    def test_emit_recoverable_error(self, temp_telemetry_dir: Path) -> None:
        """Emit a recoverable error event."""
        result = emit_error_event(
            tool="Bash",
            error_type="command_not_found",
            context="pytest",
            recoverable=True,
            base_path=temp_telemetry_dir,
        )

        assert result.success is True

        content = result.path.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["tool"] == "Bash"
        assert data["error_type"] == "command_not_found"
        assert data["context"] == "pytest"
        assert data["recoverable"] is True
