"""Tests for BacklogHook and WorkLifecycleEvent (S325.4, S347.4)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.adapters.models import IssueRef, IssueSummary
from raise_cli.cli.main import app
from raise_cli.hooks.builtin.backlog import BacklogHook
from raise_cli.hooks.events import WorkLifecycleEvent

runner = CliRunner()


class TestWorkLifecycleEvent:
    """Tests for WorkLifecycleEvent dataclass."""

    def test_event_name(self) -> None:
        """Event name is work:lifecycle."""
        event = WorkLifecycleEvent(
            work_type="story", work_id="S325.4", event="start", phase="design"
        )
        assert event.event_name == "work:lifecycle"

    def test_fields(self) -> None:
        """Event carries work_type, work_id, event, phase."""
        event = WorkLifecycleEvent(
            work_type="epic", work_id="E325", event="complete", phase="close"
        )
        assert event.work_type == "epic"
        assert event.work_id == "E325"
        assert event.event == "complete"
        assert event.phase == "close"

    def test_frozen(self) -> None:
        """Event is immutable."""
        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="start", phase="design"
        )
        try:
            event.work_id = "S2"  # type: ignore[misc]
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass  # expected — frozen dataclass

    def test_has_timestamp(self) -> None:
        """Event has a timestamp from HookEvent base."""
        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="start", phase="design"
        )
        assert event.timestamp is not None


class TestEmitWorkBridge:
    """Tests for emit-work firing WorkLifecycleEvent to hook system."""

    def test_emit_work_fires_hook_event(self) -> None:
        """emit-work CLI command dispatches WorkLifecycleEvent after telemetry write."""
        mock_emitter = MagicMock()
        with (
            patch("raise_cli.hooks.emitter.create_emitter", return_value=mock_emitter),
            patch("raise_cli.telemetry.writer.emit") as mock_emit,
        ):
            mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-work",
                    "story",
                    "S325.4",
                    "--event",
                    "start",
                    "--phase",
                    "design",
                ],
            )

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
        with (
            patch("raise_cli.hooks.emitter.create_emitter", return_value=mock_emitter),
            patch("raise_cli.telemetry.writer.emit") as mock_emit,
        ):
            mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-work",
                    "epic",
                    "E325",
                    "--event",
                    "complete",
                    "--phase",
                    "close",
                ],
            )

        assert result.exit_code == 0
        fired_event = mock_emitter.emit.call_args[0][0]
        assert fired_event.work_type == "epic"
        assert fired_event.work_id == "E325"
        assert fired_event.event == "complete"

    def test_emit_work_hook_failure_does_not_crash(self) -> None:
        """If hook emit raises, CLI still succeeds (telemetry was written)."""
        mock_emitter = MagicMock()
        mock_emitter.emit.side_effect = RuntimeError("hook system exploded")
        with (
            patch("raise_cli.hooks.emitter.create_emitter", return_value=mock_emitter),
            patch("raise_cli.telemetry.writer.emit") as mock_emit,
        ):
            mock_emit.return_value = MagicMock(success=True, path="/tmp/test.jsonl")
            result = runner.invoke(
                app, ["signal", "emit-work", "story", "S1", "--event", "start"]
            )

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
        """Story start → search, create if missing, transition in-progress."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss
        adapter.create_issue.return_value = IssueRef(key="RAISE-99")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-99")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S325.4", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        assert adapter.search.call_count == 2  # label + summary fallback
        adapter.create_issue.assert_called_once()
        adapter.transition_issue.assert_called_once_with("RAISE-99", "in-progress")

    def test_story_start_create_includes_rai_label(self, tmp_path: Path) -> None:
        """RAISE-417 regression: created issue includes rai:{work_id} label."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss
        adapter.create_issue.return_value = IssueRef(key="RAISE-77")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-77")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S417.1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        spec = adapter.create_issue.call_args[0][1]
        assert "rai:S417.1" in spec.labels

    def test_epic_start_create_includes_rai_label(self, tmp_path: Path) -> None:
        """RAISE-417 regression: epic creation also includes rai:{work_id} label."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss
        adapter.create_issue.return_value = IssueRef(key="RAISE-78")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-78")

        event = WorkLifecycleEvent(
            work_type="epic", work_id="E417", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        spec = adapter.create_issue.call_args[0][1]
        assert "rai:E417" in spec.labels

    def test_story_start_existing_issue_transitions_only(self, tmp_path: Path) -> None:
        """Story start with existing issue → transition only, no create."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-333",
                summary="S325.4 — Backlog-Aware",
                status="Backlog",
                issue_type="Story",
            ),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-333")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S325.4", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.create_issue.assert_not_called()
        adapter.transition_issue.assert_called_once_with("RAISE-333", "in-progress")

    def test_story_complete_transitions_done(self, tmp_path: Path) -> None:
        """Story complete → transition to done."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [  # label search finds it
            IssueSummary(
                key="RAISE-333",
                summary="S325.4",
                status="In Progress",
                issue_type="Story",
            ),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-333")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S325.4", event="complete", phase="close"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.transition_issue.assert_called_once_with("RAISE-333", "done")

    def test_epic_start_creates_and_transitions(self, tmp_path: Path) -> None:
        """Epic start → search, create if missing, transition in-progress."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss
        adapter.create_issue.return_value = IssueRef(key="RAISE-50")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-50")

        event = WorkLifecycleEvent(
            work_type="epic", work_id="E325", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        assert adapter.search.call_count == 2  # label + summary fallback
        adapter.create_issue.assert_called_once()
        adapter.transition_issue.assert_called_once_with("RAISE-50", "in-progress")

    def test_epic_complete_transitions_done(self, tmp_path: Path) -> None:
        """Epic complete → transition to done."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-50", summary="E325", status="In Progress", issue_type="Epic"
            ),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-50")

        event = WorkLifecycleEvent(
            work_type="epic", work_id="E325", event="complete", phase="close"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        adapter.transition_issue.assert_called_once_with("RAISE-50", "done")

    def test_blocked_event_is_noop(self, tmp_path: Path) -> None:
        """Blocked event → no backlog action."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="blocked", phase="implement"
        )
        with patch("raise_cli.hooks.builtin.backlog.resolve_adapter") as mock_resolve:
            result = hook.handle(event)

        assert result.status == "ok"
        mock_resolve.assert_not_called()

    def test_unblocked_event_is_noop(self, tmp_path: Path) -> None:
        """Unblocked event → no backlog action."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="unblocked", phase="implement"
        )
        with patch("raise_cli.hooks.builtin.backlog.resolve_adapter") as mock_resolve:
            result = hook.handle(event)

        assert result.status == "ok"
        mock_resolve.assert_not_called()


class TestBacklogHookGracefulDegradation:
    """Tests for BacklogHook error isolation."""

    def test_adapter_unavailable(self, tmp_path: Path) -> None:
        """Adapter resolution failure → error result, no crash."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter",
            side_effect=RuntimeError("no adapter"),
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert "adapter" in result.message.lower()

    def test_no_jira_yaml(self, tmp_path: Path) -> None:
        """Missing jira.yaml → error result, no crash."""
        hook = _make_hook(tmp_path)  # no jira.yaml created

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="start", phase="design"
        )
        result = hook.handle(event)

        assert result.status == "error"
        assert "jira" in result.message.lower()

    def test_search_failure(self, tmp_path: Path) -> None:
        """Search failure → error result, no crash."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = RuntimeError("search exploded")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "error"

    def test_complete_without_existing_issue_warns(self, tmp_path: Path) -> None:
        """Complete event but no issue found → error (can't transition nothing)."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss

        event = WorkLifecycleEvent(
            work_type="story", work_id="S1", event="complete", phase="close"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "error"
        adapter.transition_issue.assert_not_called()


class TestAdapterAgnosticRenames:
    """T1: Verify adapter-agnostic renames (S347.4)."""

    def test_resolve_jira_key_no_longer_exists(self) -> None:
        """Old _resolve_jira_key function is removed."""
        import raise_cli.hooks.builtin.backlog as mod

        assert not hasattr(mod, "_resolve_jira_key"), (
            "_resolve_jira_key should be renamed to _resolve_issue_key"
        )

    def test_resolve_issue_key_exists(self) -> None:
        """New _resolve_issue_key function exists."""
        import raise_cli.hooks.builtin.backlog as mod

        assert hasattr(mod, "_resolve_issue_key"), "_resolve_issue_key should exist"

    def test_resolve_adapter_called_with_none(self, tmp_path: Path) -> None:
        """resolve_adapter uses None (manifest-aware) instead of hardcoded 'jira'."""
        with patch("raise_cli.cli.commands._resolve.resolve_adapter") as mock_resolve:
            mock_resolve.return_value = MagicMock()
            from raise_cli.hooks.builtin.backlog import resolve_adapter

            resolve_adapter()
        mock_resolve.assert_called_once_with(None)

    def test_module_docstring_adapter_agnostic(self) -> None:
        """Module docstring says 'backlog state', not 'Jira state'."""
        import raise_cli.hooks.builtin.backlog as mod

        assert "backlog state" in (mod.__doc__ or "").lower()

    def test_class_docstring_adapter_agnostic(self) -> None:
        """BacklogHook class docstring says 'backlog state', not 'Jira state'."""
        assert "backlog state" in (BacklogHook.__doc__ or "").lower()


class TestJiraLabelFirstSearch:
    """T2: Jira label-first search with summary fallback (S347.4)."""

    def test_jira_label_search_finds_issue(self, tmp_path: Path) -> None:
        """Label-first search finds issue on first try — no summary fallback."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-100", summary="S99.1", status="Backlog", issue_type="Story"
            ),
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-100")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S99.1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        # Only ONE search call (label query), not two
        assert adapter.search.call_count == 1
        label_query = adapter.search.call_args_list[0][0][0]
        assert 'labels = "rai:S99.1"' in label_query
        adapter.transition_issue.assert_called_once_with("RAISE-100", "in-progress")

    def test_jira_label_miss_falls_back_to_summary(self, tmp_path: Path) -> None:
        """Label search returns nothing, summary fallback finds issue + warning logged."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        # First call (label) returns nothing, second call (summary) returns match
        adapter.search.side_effect = [
            [],
            [
                IssueSummary(
                    key="RAISE-200",
                    summary="S99.1",
                    status="Backlog",
                    issue_type="Story",
                )
            ],
        ]
        adapter.transition_issue.return_value = IssueRef(key="RAISE-200")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S99.1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        assert adapter.search.call_count == 2
        # First call: label query
        label_q = adapter.search.call_args_list[0][0][0]
        assert 'labels = "rai:S99.1"' in label_q
        # Second call: summary query
        summary_q = adapter.search.call_args_list[1][0][0]
        assert 'summary ~ "S99.1"' in summary_q
        adapter.transition_issue.assert_called_once_with("RAISE-200", "in-progress")

    def test_jira_both_searches_miss_returns_none(self, tmp_path: Path) -> None:
        """Both label and summary searches miss — no issue created on complete."""
        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss

        event = WorkLifecycleEvent(
            work_type="story", work_id="S99.1", event="complete", phase="close"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert adapter.search.call_count == 2
        adapter.transition_issue.assert_not_called()


class TestFilesystemAdapterDirectSearch:
    """T3: FileAdapter uses direct key search, no JQL (S347.4)."""

    def test_filesystem_adapter_uses_direct_search(self, tmp_path: Path) -> None:
        """FilesystemPMAdapter search is called with plain work_id, not JQL."""
        from raise_cli.adapters.filesystem import FilesystemPMAdapter

        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        # Create a mock that passes isinstance check
        adapter = MagicMock(spec=FilesystemPMAdapter)
        adapter.search.return_value = [
            IssueSummary(
                key="S99.1",
                summary="S99.1 — Test",
                status="pending",
                issue_type="Story",
            ),
        ]
        adapter.transition_issue.return_value = IssueRef(key="S99.1")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S99.1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        # Direct search: called with plain work_id, not JQL
        adapter.search.assert_called_once_with("S99.1", limit=1)
        adapter.transition_issue.assert_called_once_with("S99.1", "in-progress")

    def test_filesystem_adapter_no_match_returns_none(self, tmp_path: Path) -> None:
        """FilesystemPMAdapter search returns empty → create is attempted."""
        from raise_cli.adapters.filesystem import FilesystemPMAdapter

        root = _jira_yaml(tmp_path)
        hook = _make_hook(root)

        adapter = MagicMock(spec=FilesystemPMAdapter)
        adapter.search.return_value = []
        adapter.create_issue.return_value = IssueRef(key="S99.1")
        adapter.transition_issue.return_value = IssueRef(key="S99.1")

        event = WorkLifecycleEvent(
            work_type="story", work_id="S99.1", event="start", phase="design"
        )
        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        # Only ONE search call (direct), no label/summary fallback
        adapter.search.assert_called_once_with("S99.1", limit=1)
        adapter.create_issue.assert_called_once()


class TestBacklogHookDiscovery:
    """Tests for entry point discovery."""

    def test_backlog_hook_discovered_via_registry(self) -> None:
        """BacklogHook is found by HookRegistry.discover()."""
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.discover()
        hook_types = [type(h).__name__ for h in registry.hooks]
        assert "BacklogHook" in hook_types

    def test_backlog_hook_subscribes_to_work_lifecycle(self) -> None:
        """BacklogHook subscribes to work:lifecycle event."""
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.discover()
        handlers = registry.get_hooks_for_event("work:lifecycle")
        handler_types = [type(h).__name__ for h in handlers]
        assert "BacklogHook" in handler_types


class TestBacklogHookEndToEnd:
    """End-to-end: emit-work → hook system → adapter calls."""

    def test_emit_work_start_triggers_create_and_transition(
        self, tmp_path: Path
    ) -> None:
        """Full flow: emit-work story start → BacklogHook → create + transition."""
        root = _jira_yaml(tmp_path)
        adapter = MagicMock()
        adapter.search.side_effect = [[], []]  # label miss, summary miss
        adapter.create_issue.return_value = IssueRef(key="RAISE-99")
        adapter.transition_issue.return_value = IssueRef(key="RAISE-99")

        # Patch BacklogHook to use our test root and mock adapter
        with (
            patch(
                "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
            ),
            patch.object(
                BacklogHook,
                "__init__",
                lambda self, **kw: setattr(self, "_project_root", root),
            ),
            patch("raise_cli.telemetry.writer.emit") as mock_telemetry,
        ):
            mock_telemetry.return_value = MagicMock(
                success=True, path="/tmp/test.jsonl"
            )
            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-work",
                    "story",
                    "S99.1",
                    "--event",
                    "start",
                    "--phase",
                    "design",
                ],
            )

        assert result.exit_code == 0
        # Adapter was called by BacklogHook via hook system
        assert adapter.search.call_count == 2  # label + summary fallback
        adapter.create_issue.assert_called_once()
        adapter.transition_issue.assert_called_once_with("RAISE-99", "in-progress")
