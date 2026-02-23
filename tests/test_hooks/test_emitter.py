"""Tests for the EventEmitter."""

from __future__ import annotations

from pathlib import Path

from rai_cli.hooks.emitter import EventEmitter
from rai_cli.hooks.events import (
    GraphBuildEvent,
    HookEvent,
    HookResult,
    SessionStartEvent,
)


def _ok_handler(event: HookEvent) -> HookResult:
    """Handler that always returns ok."""
    return HookResult(status="ok")


class TestEmitterRegisterAndDispatch:
    """Basic register + emit tests."""

    def test_emit_dispatches_to_registered_handler(self) -> None:
        emitter = EventEmitter()
        calls: list[HookEvent] = []

        def tracking_handler(event: HookEvent) -> HookResult:
            calls.append(event)
            return HookResult(status="ok")

        emitter.register("session:start", tracking_handler)

        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        emitter.emit(event)

        assert len(calls) == 1
        assert calls[0] is event

    def test_handler_for_different_event_not_called(self) -> None:
        emitter = EventEmitter()
        calls: list[HookEvent] = []

        def tracking_handler(event: HookEvent) -> HookResult:
            calls.append(event)
            return HookResult(status="ok")

        emitter.register("graph:build", tracking_handler)

        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        emitter.emit(event)

        assert len(calls) == 0

    def test_multiple_handlers_for_same_event(self) -> None:
        emitter = EventEmitter()
        call_order: list[str] = []

        def handler_a(event: HookEvent) -> HookResult:
            call_order.append("a")
            return HookResult(status="ok")

        def handler_b(event: HookEvent) -> HookResult:
            call_order.append("b")
            return HookResult(status="ok")

        emitter.register("session:start", handler_a)
        emitter.register("session:start", handler_b)

        emitter.emit(SessionStartEvent(session_id="SES-1", developer="emilio"))

        assert call_order == ["a", "b"]

    def test_emit_with_no_handlers_returns_ok(self) -> None:
        emitter = EventEmitter()
        result = emitter.emit(
            GraphBuildEvent(project_path=Path("/tmp"), node_count=1, edge_count=0)
        )
        assert not result.aborted
        assert result.handler_errors == ()


class TestEmitterErrorIsolation:
    """Handler error isolation tests."""

    def test_broken_handler_is_caught_and_skipped(self) -> None:
        emitter = EventEmitter()
        good_calls: list[HookEvent] = []

        def broken_handler(event: HookEvent) -> HookResult:
            msg = "oops"
            raise RuntimeError(msg)

        def good_handler(event: HookEvent) -> HookResult:
            good_calls.append(event)
            return HookResult(status="ok")

        emitter.register("session:start", broken_handler)
        emitter.register("session:start", good_handler)

        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        result = emitter.emit(event)

        # Good handler still ran
        assert len(good_calls) == 1
        # Error was captured
        assert len(result.handler_errors) == 1
        assert "oops" in result.handler_errors[0]

    def test_multiple_broken_handlers_all_reported(self) -> None:
        emitter = EventEmitter()

        def broken_a(event: HookEvent) -> HookResult:
            msg = "error a"
            raise ValueError(msg)

        def broken_b(event: HookEvent) -> HookResult:
            msg = "error b"
            raise TypeError(msg)

        emitter.register("session:start", broken_a)
        emitter.register("session:start", broken_b)

        result = emitter.emit(
            SessionStartEvent(session_id="SES-1", developer="emilio")
        )
        assert len(result.handler_errors) == 2
