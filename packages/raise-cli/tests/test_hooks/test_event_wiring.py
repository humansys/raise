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

from raise_cli.hooks.emitter import EventEmitter
from raise_cli.hooks.events import (
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


@pytest.fixture
def captured_events() -> list[HookEvent]:
    """List to capture emitted events."""
    return []


@pytest.fixture
def mock_emitter(captured_events: list[HookEvent]) -> EventEmitter:
    """EventEmitter that captures events instead of dispatching."""
    emitter = EventEmitter()

    def tracking_emit(event: HookEvent) -> EmitResult:
        captured_events.append(event)
        return EmitResult(aborted=False, abort_message="", handler_errors=())

    emitter.emit = tracking_emit  # type: ignore[assignment]
    return emitter


class TestSessionStartEvent:
    """session:start event wiring."""

    def test_session_start_emits_event(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.session import session_app

        runner = CliRunner()

        with (
            patch(
                "raise_cli.cli.commands.session.create_emitter",
                return_value=mock_emitter,
            ),
            patch("raise_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.increment_session") as mock_inc,
        ):
            from raise_cli.onboarding.profile import DeveloperProfile

            profile = DeveloperProfile(name="Test")
            mock_load.return_value = profile
            mock_inc.return_value = profile

            result = runner.invoke(session_app, ["start"])

        assert result.exit_code == 0
        session_events = [
            e for e in captured_events if isinstance(e, SessionStartEvent)
        ]
        assert len(session_events) == 1
        assert session_events[0].developer == "Test"

    def test_session_start_with_project_emits_session_id(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.session import session_app

        runner = CliRunner()

        # Create minimal project structure
        personal_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        personal_dir.mkdir(parents=True)
        index = personal_dir / "index.jsonl"
        index.write_text("")

        with (
            patch(
                "raise_cli.cli.commands.session.create_emitter",
                return_value=mock_emitter,
            ),
            patch("raise_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.increment_session") as mock_inc,
            patch(
                "raise_cli.cli.commands.session.generate_session_id",
                return_value="S-A-260322-1430",
            ),
            patch("raise_cli.cli.commands.session.start_session") as mock_start,
            patch("raise_cli.cli.commands.session.migrate_flat_to_session"),
            patch("raise_cli.cli.commands.session.write_active_session"),
            patch("raise_cli.cli.commands.session.PrefixRegistry") as mock_registry,
        ):
            from raise_cli.onboarding.profile import DeveloperProfile

            mock_reg_instance = mock_registry.load.return_value
            mock_reg_instance.register.return_value = "A"

            profile = DeveloperProfile(name="Alice")
            mock_load.return_value = profile
            mock_inc.return_value = profile
            mock_start.return_value = (profile, [])

            result = runner.invoke(session_app, ["start", "--project", str(tmp_path)])

        assert result.exit_code == 0
        session_events = [
            e for e in captured_events if isinstance(e, SessionStartEvent)
        ]
        assert len(session_events) == 1
        assert session_events[0].session_id == "S-A-260322-1430"


class TestSessionCloseEvents:
    """session:close and before:session:close event wiring."""

    def test_session_close_legacy_emits_both_events(
        self, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.session import session_app

        runner = CliRunner()

        with (
            patch(
                "raise_cli.cli.commands.session.create_emitter",
                return_value=mock_emitter,
            ),
            patch("raise_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.end_session") as mock_end,
        ):
            from raise_cli.onboarding.profile import ActiveSession, DeveloperProfile

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
        before_events = [
            e for e in captured_events if isinstance(e, BeforeSessionCloseEvent)
        ]
        after_events = [e for e in captured_events if isinstance(e, SessionCloseEvent)]
        assert len(before_events) == 1
        assert len(after_events) == 1
        assert before_events[0].session_id == "SES-10"

    def test_session_close_abort_stops_execution(
        self,
        captured_events: list[HookEvent],
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.session import session_app

        runner = CliRunner()

        # Create an emitter that aborts on before:session:close
        abort_emitter = EventEmitter()
        abort_calls: list[HookEvent] = []

        def abort_emit(event: HookEvent) -> EmitResult:
            abort_calls.append(event)
            if event.event_name == "before:session:close":
                return EmitResult(
                    aborted=True, abort_message="Blocked by hook", handler_errors=()
                )
            return EmitResult(aborted=False, abort_message="", handler_errors=())

        abort_emitter.emit = abort_emit  # type: ignore[assignment]

        with (
            patch(
                "raise_cli.cli.commands.session.create_emitter",
                return_value=abort_emitter,
            ),
            patch("raise_cli.cli.commands.session.load_developer_profile") as mock_load,
            patch("raise_cli.cli.commands.session.end_session") as mock_end,
        ):
            from raise_cli.onboarding.profile import ActiveSession, DeveloperProfile

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
        before_events = [
            e for e in abort_calls if isinstance(e, BeforeSessionCloseEvent)
        ]
        after_events = [e for e in abort_calls if isinstance(e, SessionCloseEvent)]
        assert len(before_events) == 1
        assert len(after_events) == 0


class TestGraphBuildEvent:
    """graph:build event wiring."""

    def test_graph_build_emits_event(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.graph import graph_app

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
            patch(
                "raise_cli.cli.commands.graph.create_emitter", return_value=mock_emitter
            ),
            patch(
                "raise_cli.cli.commands.graph.get_active_backend",
                return_value=mock_backend,
            ),
            patch("raise_cli.cli.commands.graph.GraphBuilder") as mock_builder_cls,
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=tmp_path / "index.json",
            ),
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
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.pattern import pattern_app

        runner = CliRunner()

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.id = "PAT-E-999"
        mock_result.message = "Pattern added"

        with (
            patch(
                "raise_cli.cli.commands.pattern.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.pattern.get_memory_dir_for_scope",
                return_value=tmp_path,
            ),
            patch(
                "raise_cli.cli.commands.pattern.append_pattern",
                return_value=mock_result,
            ),
            patch(
                "raise_cli.cli.commands.pattern.load_developer_profile",
                return_value=None,
            ),
        ):
            result = runner.invoke(
                pattern_app, ["add", "Test pattern", "-c", "testing"]
            )

        assert result.exit_code == 0
        pat_events = [e for e in captured_events if isinstance(e, PatternAddedEvent)]
        assert len(pat_events) == 1
        assert pat_events[0].pattern_id == "PAT-E-999"
        assert pat_events[0].content == "Test pattern"

    def test_pattern_add_no_event_on_failure(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.pattern import pattern_app

        runner = CliRunner()

        mock_result = MagicMock()
        mock_result.success = False
        mock_result.message = "Failed"

        with (
            patch(
                "raise_cli.cli.commands.pattern.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.pattern.get_memory_dir_for_scope",
                return_value=tmp_path,
            ),
            patch(
                "raise_cli.cli.commands.pattern.append_pattern",
                return_value=mock_result,
            ),
            patch(
                "raise_cli.cli.commands.pattern.load_developer_profile",
                return_value=None,
            ),
        ):
            runner.invoke(pattern_app, ["add", "Test pattern"])

        pat_events = [e for e in captured_events if isinstance(e, PatternAddedEvent)]
        assert len(pat_events) == 0


class TestDiscoverScanEvent:
    """discover:scan event wiring."""

    def test_discover_scan_emits_event(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.discover import discover_app

        runner = CliRunner()

        mock_result = MagicMock()
        mock_result.symbols = [MagicMock(), MagicMock(), MagicMock()]
        mock_result.files_scanned = 5
        mock_result.errors = []

        with (
            patch(
                "raise_cli.cli.commands.discover.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.discover.scan_directory",
                return_value=mock_result,
            ),
            patch("raise_cli.cli.commands.discover.format_scan_result"),
        ):
            result = runner.invoke(discover_app, ["scan", str(tmp_path)])

        assert result.exit_code == 0
        scan_events = [e for e in captured_events if isinstance(e, DiscoverScanEvent)]
        assert len(scan_events) == 1
        assert scan_events[0].component_count == 3
        assert scan_events[0].language == "auto"


class TestInitCompleteEvent:
    """init:complete event wiring."""

    def test_init_emits_event(
        self,
        tmp_path: Path,
        captured_events: list[HookEvent],
        mock_emitter: EventEmitter,
    ) -> None:
        # Create a Typer app just for testing
        import typer
        from typer.testing import CliRunner

        from raise_cli.cli.commands.init import init_command

        app = typer.Typer()
        app.command()(init_command)

        runner = CliRunner()

        mock_profile = MagicMock()
        mock_profile.name = "Test"
        mock_profile.experience_level = MagicMock()
        mock_profile.experience_level.value = "ha"
        mock_profile.projects = []
        mock_profile.get_pattern_prefix.return_value = "E"

        from raise_cli.onboarding.detection import ProjectType

        mock_detection = MagicMock()
        mock_detection.project_type = ProjectType.GREENFIELD
        mock_detection.code_file_count = 0
        mock_detection.language = None
        mock_detection.toolchain = None

        mock_config = MagicMock()
        mock_config.agent_type = "claude"
        mock_config.skills_dir = ".claude/skills"
        mock_config.instructions_file = "CLAUDE.md"

        mock_registry = MagicMock()
        mock_registry.get_config.return_value = mock_config
        mock_registry.get_plugin.return_value = MagicMock()

        mock_skills_result = MagicMock()
        mock_skills_result.already_existed = True
        mock_skills_result.skills_copied = 0
        mock_skills_result.skills_installed = []
        mock_skills_result.skills_updated = []
        mock_skills_result.skills_conflicted = []
        mock_skills_result.skills_kept = []
        mock_skills_result.skills_overwritten = []
        mock_skills_result.skills_current = []

        mock_gov_result = MagicMock()
        mock_gov_result.already_existed = True
        mock_gov_result.files_created = 0

        mock_bootstrap = MagicMock()
        mock_bootstrap.already_existed = True
        mock_bootstrap.patterns_added = 0
        mock_bootstrap.patterns_updated = 0

        with (
            patch(
                "raise_cli.cli.commands.init.create_emitter", return_value=mock_emitter
            ),
            patch(
                "raise_cli.cli.commands.init.load_developer_profile",
                return_value=mock_profile,
            ),
            patch("raise_cli.cli.commands.init.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.init.detect_project_type",
                return_value=mock_detection,
            ),
            patch(
                "raise_cli.cli.commands.init.load_registry", return_value=mock_registry
            ),
            patch("raise_cli.cli.commands.init.save_manifest"),
            patch(
                "raise_cli.onboarding.bootstrap.bootstrap_rai_base",
                return_value=mock_bootstrap,
            ),
            patch(
                "raise_cli.onboarding.governance.scaffold_governance",
                return_value=mock_gov_result,
            ),
            patch(
                "raise_cli.onboarding.memory_md.generate_memory_md",
                return_value="# Memory",
            ),
            patch(
                "raise_cli.config.paths.get_memory_dir",
                return_value=tmp_path / "memory",
            ),
            patch(
                "raise_cli.config.paths.get_framework_dir",
                return_value=tmp_path / "framework",
            ),
            patch(
                "raise_cli.config.paths.get_claude_memory_path",
                return_value=tmp_path / "claude" / "MEMORY.md",
            ),
            patch(
                "raise_cli.onboarding.skills.scaffold_skills",
                return_value=mock_skills_result,
            ),
            patch("raise_cli.onboarding.workflows.scaffold_workflows"),
            patch(
                "raise_cli.cli.commands.init.generate_instructions",
                return_value="# Test CLAUDE.md",
            ),
        ):
            # Create necessary dirs
            (tmp_path / "memory").mkdir(parents=True, exist_ok=True)
            (tmp_path / "claude").mkdir(parents=True, exist_ok=True)
            (tmp_path / "framework").mkdir(parents=True, exist_ok=True)
            (tmp_path / "framework" / "methodology.yaml").write_text("")
            (tmp_path / ".raise").mkdir(parents=True, exist_ok=True)

            result = runner.invoke(app, ["--path", str(tmp_path), "--force"])

        assert result.exit_code == 0, result.output
        init_events = [e for e in captured_events if isinstance(e, InitCompleteEvent)]
        assert len(init_events) == 1
        assert init_events[0].project_name == tmp_path.name


class TestAdapterEvents:
    """adapter:loaded and adapter:failed event wiring."""

    def test_adapter_check_emits_loaded_for_compliant(
        self, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.adapters import adapters_app

        runner = CliRunner()

        # Create a compliant adapter (subclass of GovernanceParser)
        from raise_cli.adapters.protocols import GovernanceParser

        compliant_cls = type("FakeParser", (GovernanceParser,), {})
        mock_ep = MagicMock()
        mock_ep.name = "test-adapter"
        mock_ep.load.return_value = compliant_cls
        mock_ep.dist = MagicMock()
        mock_ep.dist.name = "test-pkg"

        # Only return entries for the governance_parsers group
        from raise_cli.adapters.registry import EP_GOVERNANCE_PARSERS

        def selective_entry_points(group: str) -> list[Any]:
            if group == EP_GOVERNANCE_PARSERS:
                return [mock_ep]
            return []

        with (
            patch(
                "raise_cli.cli.commands.adapters.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.adapters.entry_points",
                side_effect=selective_entry_points,
            ),
            patch(
                "raise_cli.cli.commands.adapters._get_tier", return_value="community"
            ),
            patch("raise_cli.cli.commands.adapters.format_check_human"),
        ):
            result = runner.invoke(adapters_app, ["check"])

        assert result.exit_code == 0
        loaded_events = [
            e for e in captured_events if isinstance(e, AdapterLoadedEvent)
        ]
        assert len(loaded_events) == 1
        assert loaded_events[0].adapter_name == "test-adapter"
        # Non-compliant should NOT emit loaded
        failed_events = [
            e for e in captured_events if isinstance(e, AdapterFailedEvent)
        ]
        assert len(failed_events) == 0

    def test_adapter_check_emits_failed_for_non_compliant(
        self, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.adapters import adapters_app

        runner = CliRunner()

        # Non-compliant: loads a class but not a Protocol subclass
        mock_ep = MagicMock()
        mock_ep.name = "bad-adapter"
        mock_ep.load.return_value = type("NotAParser", (), {})
        mock_ep.dist = MagicMock()
        mock_ep.dist.name = "bad-pkg"

        from raise_cli.adapters.registry import EP_GOVERNANCE_PARSERS

        def selective_entry_points(group: str) -> list[Any]:
            if group == EP_GOVERNANCE_PARSERS:
                return [mock_ep]
            return []

        with (
            patch(
                "raise_cli.cli.commands.adapters.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.adapters.entry_points",
                side_effect=selective_entry_points,
            ),
            patch(
                "raise_cli.cli.commands.adapters._get_tier", return_value="community"
            ),
            patch("raise_cli.cli.commands.adapters.format_check_human"),
        ):
            result = runner.invoke(adapters_app, ["check"])

        assert result.exit_code == 0
        # Non-compliant adapters emit failed, not loaded
        failed_events = [
            e for e in captured_events if isinstance(e, AdapterFailedEvent)
        ]
        assert len(failed_events) == 1
        assert failed_events[0].adapter_name == "bad-adapter"
        loaded_events = [
            e for e in captured_events if isinstance(e, AdapterLoadedEvent)
        ]
        assert len(loaded_events) == 0

    def test_adapter_check_emits_failed_on_load_error(
        self, captured_events: list[HookEvent], mock_emitter: EventEmitter
    ) -> None:
        from typer.testing import CliRunner

        from raise_cli.cli.commands.adapters import adapters_app

        runner = CliRunner()

        mock_ep = MagicMock()
        mock_ep.name = "broken-adapter"
        mock_ep.load.side_effect = ImportError("missing dep")
        mock_ep.dist = MagicMock()
        mock_ep.dist.name = "broken-pkg"

        with (
            patch(
                "raise_cli.cli.commands.adapters.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.adapters.entry_points", return_value=[mock_ep]
            ),
            patch(
                "raise_cli.cli.commands.adapters._get_tier", return_value="community"
            ),
            patch("raise_cli.cli.commands.adapters.format_check_human"),
        ):
            result = runner.invoke(adapters_app, ["check"])

        assert result.exit_code == 0
        failed_events = [
            e for e in captured_events if isinstance(e, AdapterFailedEvent)
        ]
        assert len(failed_events) >= 1
        assert failed_events[0].adapter_name == "broken-adapter"
        assert "missing dep" in failed_events[0].error
