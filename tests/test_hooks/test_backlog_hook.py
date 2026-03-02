"""Tests for BacklogHook and WorkLifecycleEvent (S325.4)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rai_cli.adapters.models import IssueRef, IssueSummary
from rai_cli.cli.main import app
from rai_cli.hooks.builtin.backlog import BacklogHook
from rai_cli.hooks.events import HookResult, WorkLifecycleEvent

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


def _jira_yaml(tmp_path: Path) -> Path:
    """Create a minimal jira.yaml with lifecycle_mapping."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    config = raise_dir / "jira.yaml"
    config.write_text(
        "projects:\n"
        "  RAISE:\n"
        "    name: RAISE\n"
        "workflow:\n"
        "  lifecycle_mapping:\n"
        "    story_start: 31\n"
        "    story_close: 41\n"
        "    epic_start: 31\n"
        "    epic_close: 41\n"
    )
    return tmp_path


def _make_hook(project_root: Path) -> BacklogHook:
    """Create a BacklogHook pointing at a test project root."""
    return BacklogHook(project_root=project_root)


class TestBacklogHookMapping:
    """Tests for BacklogHook event-to-backlog mapping."""

    def test_story_start_creates_and_transitions(self, tmp_path: Path) -> None:
        """story start → search, create if missing, transition in-progress."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = []  # no existing issue
        adapter.create_issue.return_value = IssueRef(key="RAISE-99")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-99")

        event = WorkLifecycleEvent(work_type="story", work_id="S325.4", event="start", phase="design")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.search.assert_called_once()
        adapter.create_issue.assert_called_once()
        adapter.transition_issue.assert_called_once_with("RAISE-99", "in-progress")

    def test_story_start_existing_issue_transitions_only(self, tmp_path: Path) -> None:
        """story start with existing issue → transition only, no create."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(key="RAISE-333", summary="S325.4 — Backlog-Aware", status="Backlog", issue_type="Story"),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-333")

        event = WorkLifecycleEvent(work_type="story", work_id="S325.4", event="start", phase="design")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.create_issue.assert_not_called()
        adapter.transition_issue.assert_called_once_with("RAISE-333", "in-progress")

    def test_story_complete_transitions_done(self, tmp_path: Path) -> None:
        """story complete → transition to done."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(key="RAISE-333", summary="S325.4", status="In Progress", issue_type="Story"),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-333")

        event = WorkLifecycleEvent(work_type="story", work_id="S325.4", event="complete", phase="close")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.transition_issue.assert_called_once_with("RAISE-333", "done")

    def test_epic_start_creates_and_transitions(self, tmp_path: Path) -> None:
        """epic start → search, create if missing, transition in-progress."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = []
        adapter.create_issue.return_value = IssueRef(key="RAISE-50")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-50")

        event = WorkLifecycleEvent(work_type="epic", work_id="E325", event="start", phase="design")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.create_issue.assert_called_once()
        adapter.transition_issue.assert_called_once_with("RAISE-50", "in-progress")

    def test_epic_complete_transitions_done(self, tmp_path: Path) -> None:
        """epic complete → transition to done."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(key="RAISE-50", summary="E325", status="In Progress", issue_type="Epic"),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-50")

        event = WorkLifecycleEvent(work_type="epic", work_id="E325", event="complete", phase="close")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.transition_issue.assert_called_once_with("RAISE-50", "done")

    def test_blocked_event_is_noop(self, tmp_path: Path) -> None:
        """blocked event → no backlog action."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="blocked", phase="implement")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter") as mock_resolve:
            result = hook.handle(event)

        assert result.status == "ok"
        mock_resolve.assert_not_called()

    def test_unblocked_event_is_noop(self, tmp_path: Path) -> None:
        """unblocked event → no backlog action."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="unblocked", phase="implement")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter") as mock_resolve:
            result = hook.handle(event)

        assert result.status == "ok"
        mock_resolve.assert_not_called()


class TestBacklogHookGracefulDegradation:
    """Tests for BacklogHook error isolation."""

    def test_adapter_unavailable(self, tmp_path: Path) -> None:
        """Adapter resolution failure → error result, no crash."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="start", phase="design")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", side_effect=RuntimeError("no adapter")):
            result = hook.handle(event)

        assert result.status == "error"
        assert "adapter" in result.message.lower()

    def test_no_jira_yaml(self, tmp_path: Path) -> None:
        """Missing jira.yaml → error result, no crash."""
        hook = _make_hook(tmp_path)  # no jira.yaml created

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="start", phase="design")
        result = hook.handle(event)

        assert result.status == "error"
        assert "jira" in result.message.lower()

    def test_search_failure(self, tmp_path: Path) -> None:
        """Search failure → error result, no crash."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = RuntimeError("search exploded")

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="start", phase="design")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "error"

    def test_complete_without_existing_issue_warns(self, tmp_path: Path) -> None:
        """complete event but no Jira issue found → error (can't transition nothing)."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = []

        event = WorkLifecycleEvent(work_type="story", work_id="S1", event="complete", phase="close")
        with patch("rai_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter):
            result = hook.handle(event)

        assert result.status == "error"
        adapter.transition_issue.assert_not_called()
