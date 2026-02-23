"""Tests for the EventEmitter."""

from __future__ import annotations

from pathlib import Path

from rai_cli.hooks.emitter import EventEmitter
from rai_cli.hooks.events import (
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
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


class TestBeforeEventAbortFlow:
    """Tests for before: event abort semantics."""

    def test_abort_on_before_event_sets_aborted(self) -> None:
        emitter = EventEmitter()

        def abort_handler(event: HookEvent) -> HookResult:
            return HookResult(status="abort", message="Compliance failed")

        emitter.register("before:release:publish", abort_handler)

        event = BeforeReleasePublishEvent(version="2.1.0", project_path=Path("/tmp"))
        result = emitter.emit(event)

        assert result.aborted
        assert result.abort_message == "Compliance failed"

    def test_all_ok_on_before_event_not_aborted(self) -> None:
        emitter = EventEmitter()

        emitter.register("before:session:close", _ok_handler)
        emitter.register("before:session:close", _ok_handler)

        event = BeforeSessionCloseEvent(session_id="SES-1", outcome="success")
        result = emitter.emit(event)

        assert not result.aborted

    def test_abort_on_after_event_is_ignored(self) -> None:
        """Abort status only meaningful for before: events."""
        emitter = EventEmitter()

        def abort_handler(event: HookEvent) -> HookResult:
            return HookResult(status="abort", message="should be ignored")

        emitter.register("session:start", abort_handler)

        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        result = emitter.emit(event)

        assert not result.aborted

    def test_first_abort_message_wins(self) -> None:
        """Multiple aborts — first message is captured."""
        emitter = EventEmitter()

        def abort_a(event: HookEvent) -> HookResult:
            return HookResult(status="abort", message="first")

        def abort_b(event: HookEvent) -> HookResult:
            return HookResult(status="abort", message="second")

        emitter.register("before:release:publish", abort_a)
        emitter.register("before:release:publish", abort_b)

        event = BeforeReleasePublishEvent(version="2.1.0", project_path=Path("/tmp"))
        result = emitter.emit(event)

        assert result.aborted
        assert result.abort_message == "first"

    def test_all_handlers_called_even_after_abort(self) -> None:
        """All handlers run even if one aborts (all-notify semantics)."""
        emitter = EventEmitter()
        calls: list[str] = []

        def abort_handler(event: HookEvent) -> HookResult:
            calls.append("abort")
            return HookResult(status="abort", message="blocked")

        def ok_handler(event: HookEvent) -> HookResult:
            calls.append("ok")
            return HookResult(status="ok")

        emitter.register("before:release:publish", abort_handler)
        emitter.register("before:release:publish", ok_handler)

        emitter.emit(BeforeReleasePublishEvent(version="2.1.0", project_path=Path(".")))

        assert calls == ["abort", "ok"]
