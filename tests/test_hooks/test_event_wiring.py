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
    BeforeSessionCloseEvent,
    EmitResult,
    HookEvent,
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
