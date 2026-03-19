"""Tests for JiraSyncHook — auto-sync lifecycle events to Jira transitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml
from rai_pro.hooks.jira_sync import (
    JiraSyncHook,
    _load_lifecycle_mapping,
    _resolve_status_name,
)

from raise_cli.hooks.events import WorkCloseEvent, WorkStartEvent
from raise_cli.hooks.protocol import LifecycleHook

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

JIRA_YAML_CONTENT: dict[str, Any] = {
    "workflow": {
        "status_mapping": {
            "backlog": 11,
            "selected": 21,
            "in-progress": 31,
            "done": 41,
        },
        "lifecycle_mapping": {
            "story_start": 31,
            "story_close": 41,
            "epic_start": 31,
            "epic_close": 41,
        },
    }
}


@pytest.fixture
def jira_yaml(tmp_path: Path) -> Path:
    """Create a .raise/jira.yaml in tmp_path."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    yaml_path = raise_dir / "jira.yaml"
    yaml_path.write_text(yaml.dump(JIRA_YAML_CONTENT))
    return yaml_path


@pytest.fixture
def jira_yaml_no_lifecycle(tmp_path: Path) -> Path:
    """Create a .raise/jira.yaml without lifecycle_mapping."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    yaml_path = raise_dir / "jira.yaml"
    content = {"workflow": {"status_mapping": {"done": 41}}}
    yaml_path.write_text(yaml.dump(content))
    return yaml_path


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocol:
    """JiraSyncHook must satisfy LifecycleHook Protocol."""

    def test_isinstance_lifecycle_hook(self) -> None:
        hook = JiraSyncHook()
        assert isinstance(hook, LifecycleHook)

    def test_events_attribute(self) -> None:
        assert JiraSyncHook.events == ["work:start", "work:close"]

    def test_priority_attribute(self) -> None:
        assert JiraSyncHook.priority == -10


# ---------------------------------------------------------------------------
# Happy path transitions
# ---------------------------------------------------------------------------


class TestTransitions:
    """Hook calls adapter.transition_issue with correct args."""

    def test_story_start_transitions_to_in_progress(
        self, jira_yaml: Path, tmp_path: Path
    ) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        mock_adapter = MagicMock()
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value=JIRA_YAML_CONTENT["workflow"]["lifecycle_mapping"],
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                return_value=mock_adapter,
            ),
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        mock_adapter.transition_issue.assert_called_once_with(
            "RAISE-301", "in-progress"
        )

    def test_story_close_transitions_to_done(self) -> None:
        hook = JiraSyncHook()
        event = WorkCloseEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        mock_adapter = MagicMock()
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"story_close": 41},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="done",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                return_value=mock_adapter,
            ),
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        mock_adapter.transition_issue.assert_called_once_with("RAISE-301", "done")

    def test_epic_start_transitions(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(work_type="epic", work_id="E301", issue_key="RAISE-301")
        mock_adapter = MagicMock()
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"epic_start": 31},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                return_value=mock_adapter,
            ),
        ):
            result = hook.handle(event)

        assert result.status == "ok"
        mock_adapter.transition_issue.assert_called_once_with(
            "RAISE-301", "in-progress"
        )


# ---------------------------------------------------------------------------
# Graceful skip paths
# ---------------------------------------------------------------------------


class TestGracefulSkips:
    """Hook returns ok without calling adapter on skip conditions."""

    def test_no_issue_key_skips(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(work_type="story", work_id="S301.6", issue_key="")
        result = hook.handle(event)
        assert result.status == "ok"

    def test_no_lifecycle_mapping_skips(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        with patch(
            "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
            return_value=None,
        ):
            result = hook.handle(event)
        assert result.status == "ok"

    def test_no_mapping_for_key_skips(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        # lifecycle_mapping exists but has no story_start entry
        with patch(
            "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
            return_value={"epic_start": 31},
        ):
            result = hook.handle(event)
        assert result.status == "ok"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Hook returns error on adapter failure, never raises."""

    def test_adapter_failure_returns_error(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        mock_adapter = MagicMock()
        mock_adapter.transition_issue.side_effect = RuntimeError("MCP server not found")
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"story_start": 31},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                return_value=mock_adapter,
            ),
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert "MCP server not found" in result.message

    def test_resolve_adapter_failure_returns_error(self) -> None:
        hook = JiraSyncHook()
        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"story_start": 31},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                side_effect=RuntimeError("No adapter installed"),
            ),
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert "No adapter installed" in result.message


# ---------------------------------------------------------------------------
# Config readers
# ---------------------------------------------------------------------------


class TestConfigReaders:
    """Unit tests for _load_lifecycle_mapping and _resolve_status_name."""

    def test_load_lifecycle_mapping(self, jira_yaml: Path, tmp_path: Path) -> None:
        with patch(
            "rai_pro.hooks.jira_sync._JIRA_YAML_PATH",
            jira_yaml,
        ):
            mapping = _load_lifecycle_mapping()
        assert mapping == {
            "story_start": 31,
            "story_close": 41,
            "epic_start": 31,
            "epic_close": 41,
        }

    def test_load_lifecycle_mapping_missing_file(self, tmp_path: Path) -> None:
        with patch(
            "rai_pro.hooks.jira_sync._JIRA_YAML_PATH",
            tmp_path / ".raise" / "jira.yaml",
        ):
            mapping = _load_lifecycle_mapping()
        assert mapping is None

    def test_load_lifecycle_mapping_no_section(
        self, jira_yaml_no_lifecycle: Path
    ) -> None:
        with patch(
            "rai_pro.hooks.jira_sync._JIRA_YAML_PATH",
            jira_yaml_no_lifecycle,
        ):
            mapping = _load_lifecycle_mapping()
        assert mapping is None

    def test_resolve_status_name_found(self, jira_yaml: Path) -> None:
        with patch(
            "rai_pro.hooks.jira_sync._JIRA_YAML_PATH",
            jira_yaml,
        ):
            name = _resolve_status_name(31)
        assert name == "in-progress"

    def test_resolve_status_name_not_found_fallback(self, jira_yaml: Path) -> None:
        with patch(
            "rai_pro.hooks.jira_sync._JIRA_YAML_PATH",
            jira_yaml,
        ):
            name = _resolve_status_name(999)
        assert name == "999"


# ---------------------------------------------------------------------------
# Integration: EventEmitter + JiraSyncHook
# ---------------------------------------------------------------------------


class TestEmitterIntegration:
    """Test JiraSyncHook dispatched through EventEmitter."""

    def test_emitter_dispatches_to_jira_sync_hook(self) -> None:
        """Full path: emitter → hook → adapter.transition_issue()."""
        from raise_cli.hooks.emitter import EventEmitter
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.register(JiraSyncHook())
        emitter = EventEmitter(registry=registry)

        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        mock_adapter = MagicMock()
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"story_start": 31},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                return_value=mock_adapter,
            ),
        ):
            result = emitter.emit(event)

        assert not result.aborted
        assert result.handler_errors == ()
        mock_adapter.transition_issue.assert_called_once_with(
            "RAISE-301", "in-progress"
        )

    def test_emitter_error_isolation(self) -> None:
        """Adapter failure is caught by hook, emitter sees no handler_errors."""
        from raise_cli.hooks.emitter import EventEmitter
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.register(JiraSyncHook())
        emitter = EventEmitter(registry=registry)

        event = WorkStartEvent(
            work_type="story", work_id="S301.6", issue_key="RAISE-301"
        )
        with (
            patch(
                "rai_pro.hooks.jira_sync._load_lifecycle_mapping",
                return_value={"story_start": 31},
            ),
            patch(
                "rai_pro.hooks.jira_sync._resolve_status_name",
                return_value="in-progress",
            ),
            patch(
                "raise_cli.cli.commands._resolve.resolve_adapter",
                side_effect=RuntimeError("No adapter"),
            ),
        ):
            result = emitter.emit(event)

        # Hook catches internally → returns HookResult(error), doesn't raise
        # Emitter sees no handler_errors because the hook didn't raise
        assert not result.aborted
        assert result.handler_errors == ()
