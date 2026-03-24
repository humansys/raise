"""Tests for McpCallEvent telemetry event."""

from __future__ import annotations

import dataclasses

from raise_cli.hooks.events import HookEvent, McpCallEvent


class TestMcpCallEvent:
    """McpCallEvent structure and behavior."""

    def test_is_frozen_dataclass(self) -> None:
        event = McpCallEvent(server="ctx7", tool="query-docs")
        assert dataclasses.is_dataclass(event)
        assert event.__dataclass_params__.frozen  # type: ignore[attr-defined]

    def test_event_name(self) -> None:
        event = McpCallEvent()
        assert event.event_name == "mcp:call"

    def test_extends_hook_event(self) -> None:
        assert issubclass(McpCallEvent, HookEvent)

    def test_fields_with_defaults(self) -> None:
        event = McpCallEvent()
        assert event.server == ""
        assert event.tool == ""
        assert event.success is True
        assert event.latency_ms == 0
        assert event.error == ""

    def test_fields_with_values(self) -> None:
        event = McpCallEvent(
            server="context7",
            tool="resolve-library-id",
            success=False,
            latency_ms=245,
            error="Connection refused",
        )
        assert event.server == "context7"
        assert event.tool == "resolve-library-id"
        assert event.success is False
        assert event.latency_ms == 245
        assert event.error == "Connection refused"

    def test_has_timestamp(self) -> None:
        event = McpCallEvent()
        assert event.timestamp is not None
