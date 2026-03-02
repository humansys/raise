"""Tests for BacklogHook and WorkLifecycleEvent (S325.4)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.hooks.events import WorkLifecycleEvent

runner = CliRunner()


class TestWorkLifecycleEvent:
    """Tests for WorkLifecycleEvent dataclass."""

    def test_event_name(self) -> None:
        """Event name is work:lifecycle."""
        event = WorkLifecycleEvent(work_type="story", work_id="S325.4", event="start", phase="design")
        assert event.event_name == "work:lifecycle"

    def test_fields(self) -> None:
        """Event carries work_type, work_id, event, phase."""
        event = WorkLifecycleEvent(work_type="epic", work_id="E325", event="complete", phase="close")
        assert event.work_type == "epic"
        assert event.work_id == "E325"
        assert event.event == "complete"
        assert event.phase == "close"

    def test_frozen(self) -> None:
        """Event is immutable."""
        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="start", phase="design")
        try:
            event.work_id = "S2"  # type: ignore[misc]
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass  # expected — frozen dataclass

    def test_has_timestamp(self) -> None:
        """Event has a timestamp from HookEvent base."""
        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="start", phase="design")
        assert event.timestamp is not None


class TestEmitWorkBridge:
    """Tests for emit-work firing WorkLifecycleEvent to hook system."""

    def test_emit_work_fires_hook_event(self) -> None:
        """emit-work CLI command dispatches WorkLifecycleEvent after telemetry write."""
        mock_emitter = MagicMock()
        with patch("rai_cli.hooks.emitter.create_emitter", return_value=mock_emitter):
            with patch("rai_cli.telemetry.writer.emit") as mock_emit:
                mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
                result = runner.invoke(app, ["signal", "emit-work", "story", "S325.4", "--event", "start", "--phase", "design"])

        assert result.exit_code == 0
        # Verify hook event was fired
        mock_emitter.emit.assert_called_once()
        fired_event = mock_emitter.emit.call_args[0][0]
        assert isinstance(fired_event, WorkLifecycleEvent)
        assert fired_event.work_type == "story"
        assert fired_event.work_id == "S325.4"
        assert fired_event.event == "start"
        assert fired_event.phase == "design"

    def test_emit_work_fires_for_epic(self) -> None:
        """emit-work fires WorkLifecycleEvent for epic work type."""
        mock_emitter = MagicMock()
        with patch("rai_cli.hooks.emitter.create_emitter", return_value=mock_emitter):
            with patch("rai_cli.telemetry.writer.emit") as mock_emit:
                mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
                result = runner.invoke(app, ["signal", "emit-work", "epic", "E325", "--event", "complete", "--phase", "close"])

        assert result.exit_code == 0
        fired_event = mock_emitter.emit.call_args[0][0]
        assert fired_event.work_type == "epic"
        assert fired_event.work_id == "E325"
        assert fired_event.event == "complete"

    def test_emit_work_hook_failure_does_not_crash(self) -> None:
        """If hook emit raises, CLI still succeeds (telemetry was written)."""
        mock_emitter = MagicMock()
        mock_emitter.emit.side_effect = RuntimeError("hook system exploded")
        with patch("rai_cli.hooks.emitter.create_emitter", return_value=mock_emitter):
            with patch("rai_cli.telemetry.writer.emit") as mock_emit:
                mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
                result = runner.invoke(app, ["signal", "emit-work", "story", "S1", "--event", "start"])

        # CLI should still succeed — hook failure is non-fatal
        assert result.exit_code == 0
