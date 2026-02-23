"""Tests for event wiring in CLI commands.

Verifies that CLI commands emit the correct lifecycle events
via create_emitter(). Uses monkeypatching to capture events
without triggering real hooks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from rai_cli.hooks.emitter import EventEmitter
from rai_cli.hooks.events import (
    AdapterFailedEvent,
    AdapterLoadedEvent,
    BeforeSessionCloseEvent,
    DiscoverScanEvent,
    EmitResult,
    GraphBuildEvent,
    HookEvent,
    InitCompleteEvent,
    PatternAddedEvent,
    SessionCloseEvent,
    SessionStartEvent,
)


@pytest.fixture()
def captured_events() -> list[HookEvent]:
    """List to capture emitted events."""
    return []


@pytest.fixture()
def mock_emitter(captured_events: list[HookEvent]) -> EventEmitter:
    """EventEmitter that captures events instead of dispatching."""
    emitter = EventEmitter()
    original_emit = emitter.emit

    def tracking_emit(event: HookEvent) -> EmitResult:
        captured_events.append(event)
        return EmitResult(aborted=False, abort_message="", handler_errors=())

    emitter.emit = tracking_emit  # type: ignore[assignment]
    return emitter


@pytest.fixture()
def patch_create_emitter(mock_emitter: EventEmitter):
    """Patch create_emitter in the command module being tested."""
    # Returns a context manager factory for patching specific modules
    def _patch(module_path: str):
        return patch(f"{module_path}.create_emitter", return_value=mock_emitter)

    return _patch


class TestSessionStartEvent:
    """session:start event wiring."""

    def test_session_start_emits_event(
        self, tmp_path: Path, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.session import session_app

        runner = CliRunner()

        with (
            patch("rai_cli.cli.commands.session.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("rai_cli.cli.commands.session.save_developer_profile"),
            patch("rai_cli.cli.commands.session.increment_session") as mock_inc,
        ):
            from rai_cli.onboarding.profile import DeveloperProfile

            profile = DeveloperProfile(name="Test")
            mock_load.return_value = profile
            mock_inc.return_value = profile

            result = runner.invoke(session_app, ["start"])

        assert result.exit_code == 0
        session_events = [e for e in captured_events if isinstance(e, SessionStartEvent)]
        assert len(session_events) == 1
        assert session_events[0].developer == "Test"

    def test_session_start_with_project_emits_session_id(
        self, tmp_path: Path, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.session import session_app

        runner = CliRunner()

        # Create minimal project structure
        personal_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        personal_dir.mkdir(parents=True)
        index = personal_dir / "index.jsonl"
        index.write_text("")

        with (
            patch("rai_cli.cli.commands.session.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("rai_cli.cli.commands.session.save_developer_profile"),
            patch("rai_cli.cli.commands.session.increment_session") as mock_inc,
            patch("rai_cli.cli.commands.session.get_next_id", return_value="SES-42"),
            patch("rai_cli.cli.commands.session.start_session") as mock_start,
            patch("rai_cli.cli.commands.session.migrate_flat_to_session"),
        ):
            from rai_cli.onboarding.profile import DeveloperProfile

            profile = DeveloperProfile(name="Alice")
            mock_load.return_value = profile
            mock_inc.return_value = profile
            mock_start.return_value = (profile, [])

            result = runner.invoke(session_app, ["start", "--project", str(tmp_path)])

        assert result.exit_code == 0
        session_events = [e for e in captured_events if isinstance(e, SessionStartEvent)]
        assert len(session_events) == 1
        assert session_events[0].session_id == "SES-42"


class TestSessionCloseEvents:
    """session:close and before:session:close event wiring."""

    def test_session_close_legacy_emits_both_events(
        self, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.session import session_app

        runner = CliRunner()

        with (
            patch("rai_cli.cli.commands.session.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("rai_cli.cli.commands.session.save_developer_profile"),
            patch("rai_cli.cli.commands.session.end_session") as mock_end,
        ):
            from rai_cli.onboarding.profile import ActiveSession, DeveloperProfile

            profile = DeveloperProfile(
                name="Test",
                active_sessions=[
                    ActiveSession(
                        session_id="SES-10",
                        project=str(Path.cwd()),
                        started_at="2026-02-23T00:00:00Z",
                    )
                ],
            )
            mock_load.return_value = profile
            mock_end.return_value = profile

            result = runner.invoke(session_app, ["close"])

        assert result.exit_code == 0
        before_events = [e for e in captured_events if isinstance(e, BeforeSessionCloseEvent)]
        after_events = [e for e in captured_events if isinstance(e, SessionCloseEvent)]
        assert len(before_events) == 1
        assert len(after_events) == 1
        assert before_events[0].session_id == "SES-10"

    def test_session_close_abort_stops_execution(
        self, captured_events: list[HookEvent],
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.session import session_app

        runner = CliRunner()

        # Create an emitter that aborts on before:session:close
        abort_emitter = EventEmitter()
        abort_calls: list[HookEvent] = []

        def abort_emit(event: HookEvent) -> EmitResult:
            abort_calls.append(event)
            if event.event_name == "before:session:close":
                return EmitResult(aborted=True, abort_message="Blocked by hook", handler_errors=())
            return EmitResult(aborted=False, abort_message="", handler_errors=())

        abort_emitter.emit = abort_emit  # type: ignore[assignment]

        with (
            patch("rai_cli.cli.commands.session.create_emitter", return_value=abort_emitter),
            patch("rai_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("rai_cli.cli.commands.session.end_session") as mock_end,
        ):
            from rai_cli.onboarding.profile import ActiveSession, DeveloperProfile

            profile = DeveloperProfile(
                name="Test",
                active_sessions=[
                    ActiveSession(
                        session_id="SES-10",
                        project=str(Path.cwd()),
                        started_at="2026-02-23T00:00:00Z",
                    )
                ],
            )
            mock_load.return_value = profile
            mock_end.return_value = profile

            result = runner.invoke(session_app, ["close"])

        # Should exit with error
        assert result.exit_code == 1
        # before: event was emitted, but session:close was NOT
        before_events = [e for e in abort_calls if isinstance(e, BeforeSessionCloseEvent)]
        after_events = [e for e in abort_calls if isinstance(e, SessionCloseEvent)]
        assert len(before_events) == 1
        assert len(after_events) == 0


class TestGraphBuildEvent:
    """graph:build event wiring."""

    def test_graph_build_emits_event(
        self, tmp_path: Path, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.graph import graph_app

        runner = CliRunner()

        # Create a mock graph with node_count and edge_count
        mock_graph = MagicMock()
        mock_graph.node_count = 42
        mock_graph.edge_count = 15
        mock_graph.iter_concepts.return_value = []
        mock_graph.iter_relationships.return_value = []

        mock_backend = MagicMock()
        mock_backend.load.return_value = None

        with (
            patch("rai_cli.cli.commands.graph.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.graph.get_active_backend", return_value=mock_backend),
            patch("rai_cli.cli.commands.graph.UnifiedGraphBuilder") as mock_builder_cls,
            patch("rai_cli.cli.commands.graph._get_default_index_path", return_value=tmp_path / "index.json"),
        ):
            mock_builder = MagicMock()
            mock_builder.build.return_value = mock_graph
            mock_builder_cls.return_value = mock_builder

            result = runner.invoke(graph_app, ["build", "--no-diff"])

        assert result.exit_code == 0
        graph_events = [e for e in captured_events if isinstance(e, GraphBuildEvent)]
        assert len(graph_events) == 1
        assert graph_events[0].node_count == 42
        assert graph_events[0].edge_count == 15


class TestPatternAddedEvent:
    """pattern:added event wiring."""

    def test_pattern_add_emits_event_on_success(
        self, tmp_path: Path, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.pattern import pattern_app

        runner = CliRunner()

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.id = "PAT-E-999"
        mock_result.message = "Pattern added"

        with (
            patch("rai_cli.cli.commands.pattern.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.pattern.get_memory_dir_for_scope", return_value=tmp_path),
            patch("rai_cli.cli.commands.pattern.append_pattern", return_value=mock_result),
            patch("rai_cli.cli.commands.pattern.load_developer_profile", return_value=None),
        ):
            result = runner.invoke(pattern_app, ["add", "Test pattern", "-c", "testing"])

        assert result.exit_code == 0
        pat_events = [e for e in captured_events if isinstance(e, PatternAddedEvent)]
        assert len(pat_events) == 1
        assert pat_events[0].pattern_id == "PAT-E-999"
        assert pat_events[0].content == "Test pattern"

    def test_pattern_add_no_event_on_failure(
        self, tmp_path: Path, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from rai_cli.cli.commands.pattern import pattern_app

        runner = CliRunner()

        mock_result = MagicMock()
        mock_result.success = False
        mock_result.message = "Failed"

        with (
            patch("rai_cli.cli.commands.pattern.create_emitter", return_value=mock_emitter),
            patch("rai_cli.cli.commands.pattern.get_memory_dir_for_scope", return_value=tmp_path),
            patch("rai_cli.cli.commands.pattern.append_pattern", return_value=mock_result),
            patch("rai_cli.cli.commands.pattern.load_developer_profile", return_value=None),
        ):
            result = runner.invoke(pattern_app, ["add", "Test pattern"])

        pat_events = [e for e in captured_events if isinstance(e, PatternAddedEvent)]
        assert len(pat_events) == 0
