"""Tests for TelemetryHook — built-in hook that writes CommandUsage signals."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.hooks.builtin.telemetry import TelemetryHook
from raise_cli.hooks.emitter import EventEmitter
from raise_cli.hooks.events import (
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
from raise_cli.hooks.protocol import LifecycleHook
from raise_cli.hooks.registry import HookRegistry
from raise_cli.telemetry.writer import EmitResult

# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """TelemetryHook must implement LifecycleHook Protocol."""

    def test_isinstance_check(self) -> None:
        hook = TelemetryHook()
        assert isinstance(hook, LifecycleHook)


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
        with patch("raise_cli.hooks.builtin.telemetry.emit_command_usage") as mock_emit:
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
        with patch("raise_cli.hooks.builtin.telemetry.emit_command_usage") as mock_emit:
            mock_emit.return_value = EmitResult(
                success=False, error="Permission denied"
            )
            result = hook.handle(SessionStartEvent(session_id="SES-1"))

        assert result.status == "error"
        assert "Permission denied" in result.message

    def test_emit_exception_returns_error_status(self) -> None:
        hook = TelemetryHook()
        with patch("raise_cli.hooks.builtin.telemetry.emit_command_usage") as mock_emit:
            mock_emit.side_effect = OSError("disk full")
            result = hook.handle(SessionStartEvent(session_id="SES-1"))

        assert result.status == "error"
        assert "disk full" in result.message

    def test_handle_never_raises(self) -> None:
        hook = TelemetryHook()
        with patch("raise_cli.hooks.builtin.telemetry.emit_command_usage") as mock_emit:
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


# ---------------------------------------------------------------------------
# E2E integration: emitter → registry → hook → signals.jsonl
# ---------------------------------------------------------------------------


class TestE2EIntegration:
    """Full pipeline: emit event through registry, verify signal on disk."""

    def test_emit_event_writes_signal_to_disk(self, tmp_path: Path) -> None:
        """Emit a real event through the full pipeline and verify the signal file."""
        # Wire up: registry discovers TelemetryHook, emitter uses registry
        registry = HookRegistry()
        registry.discover()
        emitter = EventEmitter(registry=registry)

        # Emit a real event, pointing telemetry at tmp_path
        event = GraphBuildEvent(node_count=42, edge_count=10)
        with patch(
            "raise_cli.hooks.builtin.telemetry.emit_command_usage",
            wraps=_emit_to_tmpdir(tmp_path),
        ):
            result = emitter.emit(event)

        assert not result.aborted
        assert result.handler_errors == ()

        # Verify signal landed on disk
        signals_file = (
            tmp_path / ".raise" / "rai" / "personal" / "telemetry" / "signals.jsonl"
        )
        assert signals_file.exists()
        lines = signals_file.read_text().strip().splitlines()
        assert len(lines) == 1
        signal = json.loads(lines[0])
        assert signal["type"] == "command_usage"
        assert signal["command"] == "graph"
        assert signal["subcommand"] == "build"

    def test_multiple_events_append_signals(self, tmp_path: Path) -> None:
        """Multiple events produce multiple signal lines."""
        registry = HookRegistry()
        registry.discover()
        emitter = EventEmitter(registry=registry)

        events = [
            SessionStartEvent(session_id="SES-99"),
            GraphBuildEvent(node_count=10),
            PatternAddedEvent(pattern_id="P-1", content="test"),
        ]

        with patch(
            "raise_cli.hooks.builtin.telemetry.emit_command_usage",
            wraps=_emit_to_tmpdir(tmp_path),
        ):
            for event in events:
                emitter.emit(event)

        signals_file = (
            tmp_path / ".raise" / "rai" / "personal" / "telemetry" / "signals.jsonl"
        )
        lines = signals_file.read_text().strip().splitlines()
        assert len(lines) == 3
        commands = [
            (json.loads(line)["command"], json.loads(line)["subcommand"])
            for line in lines
        ]
        assert commands == [
            ("session", "start"),
            ("graph", "build"),
            ("pattern", "added"),
        ]


def _emit_to_tmpdir(tmp_path: Path):  # type: ignore[type-arg]
    """Create a wrapper that writes CommandUsage to tmp_path/signals.jsonl."""
    from datetime import UTC, datetime

    from raise_cli.telemetry.schemas import CommandUsage
    from raise_cli.telemetry.writer import emit

    def _wrapper(command: str, subcommand: str | None = None) -> EmitResult:
        signal = CommandUsage(
            timestamp=datetime.now(UTC),
            command=command,
            subcommand=subcommand,
        )
        return emit(signal, base_path=tmp_path)

    return _wrapper
