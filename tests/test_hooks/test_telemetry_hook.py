"""Tests for TelemetryHook — built-in hook that writes CommandUsage signals."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from rai_cli.hooks.builtin.telemetry import TelemetryHook
from rai_cli.hooks.events import (
    AdapterFailedEvent,
    AdapterLoadedEvent,
    DiscoverScanEvent,
    GraphBuildEvent,
    HookResult,
    InitCompleteEvent,
    PatternAddedEvent,
    ReleasePublishEvent,
    SessionCloseEvent,
    SessionStartEvent,
)
from rai_cli.hooks.protocol import LifecycleHook
from rai_cli.hooks.registry import HookRegistry
from rai_cli.telemetry.writer import EmitResult


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """TelemetryHook must implement LifecycleHook Protocol."""

    def test_isinstance_check(self) -> None:
        hook = TelemetryHook()
        assert isinstance(hook, LifecycleHook)

    def test_has_events_classvar(self) -> None:
        assert isinstance(TelemetryHook.events, list)
        assert len(TelemetryHook.events) == 9

    def test_has_priority_classvar(self) -> None:
        assert TelemetryHook.priority == 0

    def test_has_handle_method(self) -> None:
        hook = TelemetryHook()
        assert callable(hook.handle)


# ---------------------------------------------------------------------------
# Event subscription
# ---------------------------------------------------------------------------


class TestEventSubscription:
    """TelemetryHook subscribes to all 9 after-events."""

    EXPECTED_EVENTS = [
        "session:start",
        "session:close",
        "graph:build",
        "pattern:added",
        "discover:scan",
        "init:complete",
        "adapter:loaded",
        "adapter:failed",
        "release:publish",
    ]

    def test_subscribes_to_all_after_events(self) -> None:
        assert sorted(TelemetryHook.events) == sorted(self.EXPECTED_EVENTS)

    def test_no_before_events(self) -> None:
        for event in TelemetryHook.events:
            assert not event.startswith("before:"), f"Should not subscribe to {event}"


# ---------------------------------------------------------------------------
# Event → Signal mapping
# ---------------------------------------------------------------------------


class TestEventMapping:
    """Each event maps to a CommandUsage signal via emit_command_usage."""

    @pytest.mark.parametrize(
        ("event", "expected_command", "expected_subcommand"),
        [
            (SessionStartEvent(session_id="SES-1"), "session", "start"),
            (SessionCloseEvent(session_id="SES-1"), "session", "close"),
            (GraphBuildEvent(node_count=10), "graph", "build"),
            (PatternAddedEvent(pattern_id="P-1"), "pattern", "added"),
            (DiscoverScanEvent(language="python"), "discover", "scan"),
            (InitCompleteEvent(project_name="test"), "init", "complete"),
            (AdapterLoadedEvent(adapter_name="a"), "adapter", "loaded"),
            (AdapterFailedEvent(adapter_name="a"), "adapter", "failed"),
            (ReleasePublishEvent(version="1.0"), "release", "publish"),
        ],
    )
    def test_event_maps_to_command_usage(
        self,
        event: SessionStartEvent
        | SessionCloseEvent
        | GraphBuildEvent
        | PatternAddedEvent
        | DiscoverScanEvent
        | InitCompleteEvent
        | AdapterLoadedEvent
        | AdapterFailedEvent
        | ReleasePublishEvent,
        expected_command: str,
        expected_subcommand: str,
    ) -> None:
        hook = TelemetryHook()
        with patch(
            "rai_cli.hooks.builtin.telemetry.emit_command_usage"
        ) as mock_emit:
            mock_emit.return_value = EmitResult(success=True)
            result = hook.handle(event)

        assert result.status == "ok"
        mock_emit.assert_called_once_with(expected_command, expected_subcommand)


# ---------------------------------------------------------------------------
# Error isolation
# ---------------------------------------------------------------------------


class TestErrorIsolation:
    """Hook never raises — returns HookResult(status='error') on failure."""

    def test_emit_failure_returns_error_status(self) -> None:
        hook = TelemetryHook()
        with patch(
            "rai_cli.hooks.builtin.telemetry.emit_command_usage"
        ) as mock_emit:
            mock_emit.return_value = EmitResult(
                success=False, error="Permission denied"
            )
            result = hook.handle(SessionStartEvent(session_id="SES-1"))

        assert result.status == "error"
        assert "Permission denied" in result.message

    def test_emit_exception_returns_error_status(self) -> None:
        hook = TelemetryHook()
        with patch(
            "rai_cli.hooks.builtin.telemetry.emit_command_usage"
        ) as mock_emit:
            mock_emit.side_effect = OSError("disk full")
            result = hook.handle(SessionStartEvent(session_id="SES-1"))

        assert result.status == "error"
        assert "disk full" in result.message

    def test_handle_never_raises(self) -> None:
        hook = TelemetryHook()
        with patch(
            "rai_cli.hooks.builtin.telemetry.emit_command_usage"
        ) as mock_emit:
            mock_emit.side_effect = RuntimeError("unexpected")
            result = hook.handle(SessionStartEvent(session_id="SES-1"))

        assert isinstance(result, HookResult)
        assert result.status == "error"


# ---------------------------------------------------------------------------
# Entry point discovery
# ---------------------------------------------------------------------------


class TestEntryPointDiscovery:
    """TelemetryHook is discoverable via rai.hooks entry point."""

    def test_registry_discovers_telemetry_hook(self) -> None:
        registry = HookRegistry()
        registry.discover()
        hook_types = [type(h).__name__ for h in registry.hooks]
        assert "TelemetryHook" in hook_types

    def test_discovered_hook_is_functional(self) -> None:
        registry = HookRegistry()
        registry.discover()
        telemetry_hooks = [h for h in registry.hooks if type(h).__name__ == "TelemetryHook"]
        assert len(telemetry_hooks) == 1
        hook = telemetry_hooks[0]
        assert hook.events == TelemetryHook.events
        assert hook.priority == 0
