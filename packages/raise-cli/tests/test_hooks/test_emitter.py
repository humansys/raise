"""Tests for the EventEmitter."""

from __future__ import annotations

import time
from pathlib import Path
from typing import ClassVar

from raise_cli.hooks.emitter import EventEmitter
from raise_cli.hooks.events import (
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
    GraphBuildEvent,
    HookEvent,
    HookResult,
    SessionStartEvent,
)
from raise_cli.hooks.registry import HookRegistry


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

        result = emitter.emit(SessionStartEvent(session_id="SES-1", developer="emilio"))
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


# --- Test hook classes for registry integration ---


class _TrackingHook:
    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 0

    def __init__(self) -> None:
        self.calls: list[HookEvent] = []

    def handle(self, event: HookEvent) -> HookResult:
        self.calls.append(event)
        return HookResult(status="ok")


class _SlowHook:
    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 0
    timeout: ClassVar[float] = 0.1  # 100ms for test speed

    def handle(self, event: HookEvent) -> HookResult:
        time.sleep(1.0)  # exceeds 100ms timeout
        return HookResult(status="ok")


class _FastHookAfterSlow:
    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = -1  # lower priority, runs after slow

    def __init__(self) -> None:
        self.called = False

    def handle(self, event: HookEvent) -> HookResult:
        self.called = True
        return HookResult(status="ok")


class TestEmitterWithRegistry:
    """EventEmitter + HookRegistry integration."""

    def test_emitter_without_registry_still_works(self) -> None:
        """Backward compat: no registry, bare handlers."""
        emitter = EventEmitter()
        emitter.register("session:start", _ok_handler)
        result = emitter.emit(SessionStartEvent(session_id="SES-1", developer="e"))
        assert not result.aborted

    def test_emitter_with_registry_dispatches_hooks(self) -> None:
        registry = HookRegistry()
        hook = _TrackingHook()
        registry.register(hook)

        emitter = EventEmitter(registry=registry)
        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        emitter.emit(event)

        assert len(hook.calls) == 1
        assert hook.calls[0] is event

    def test_emitter_with_registry_priority_order(self) -> None:
        """Hooks dispatch in priority order (highest first)."""
        call_order: list[str] = []

        class HighHook:
            events: ClassVar[list[str]] = ["session:start"]
            priority: ClassVar[int] = 100

            def handle(self, event: HookEvent) -> HookResult:
                call_order.append("high")
                return HookResult(status="ok")

        class LowHook:
            events: ClassVar[list[str]] = ["session:start"]
            priority: ClassVar[int] = 0

            def handle(self, event: HookEvent) -> HookResult:
                call_order.append("low")
                return HookResult(status="ok")

        registry = HookRegistry()
        # Register low first, high second — priority should override
        registry.register(LowHook())
        registry.register(HighHook())

        emitter = EventEmitter(registry=registry)
        emitter.emit(SessionStartEvent(session_id="SES-1", developer="emilio"))

        assert call_order == ["high", "low"]

    def test_emitter_with_registry_and_manual_handlers(self) -> None:
        """Registry hooks + manual handlers coexist."""
        registry = HookRegistry()
        hook = _TrackingHook()
        registry.register(hook)

        emitter = EventEmitter(registry=registry)

        manual_calls: list[HookEvent] = []

        def manual_handler(event: HookEvent) -> HookResult:
            manual_calls.append(event)
            return HookResult(status="ok")

        emitter.register("session:start", manual_handler)

        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        emitter.emit(event)

        # Both fired
        assert len(hook.calls) == 1
        assert len(manual_calls) == 1

    def test_emitter_with_empty_registry(self) -> None:
        registry = HookRegistry()
        emitter = EventEmitter(registry=registry)
        result = emitter.emit(SessionStartEvent(session_id="SES-1", developer="e"))
        assert not result.aborted
        assert result.handler_errors == ()


class TestEmitterTimeout:
    """Per-hook timeout enforcement."""

    def test_slow_hook_times_out(self) -> None:
        registry = HookRegistry()
        registry.register(_SlowHook())

        emitter = EventEmitter(registry=registry)
        result = emitter.emit(SessionStartEvent(session_id="SES-1", developer="e"))

        assert len(result.handler_errors) == 1
        assert "timeout" in result.handler_errors[0].lower()

    def test_fast_hook_runs_after_slow_hook_timeout(self) -> None:
        """Error isolation: slow hook times out, fast hook still runs."""
        registry = HookRegistry()
        registry.register(_SlowHook())
        fast_hook = _FastHookAfterSlow()
        registry.register(fast_hook)

        emitter = EventEmitter(registry=registry)
        emitter.emit(SessionStartEvent(session_id="SES-1", developer="e"))

        assert fast_hook.called


class TestE2EPipeline:
    """End-to-end integration: Protocol → Registry → Emitter → Hook execution."""

    def test_full_pipeline_priority_dispatch_and_error_isolation(self) -> None:
        """Multi-hook pipeline with priority ordering, timeout, and error isolation."""
        call_log: list[str] = []

        class HighPriorityHook:
            events: ClassVar[list[str]] = ["session:start", "graph:build"]
            priority: ClassVar[int] = 100

            def handle(self, event: HookEvent) -> HookResult:
                call_log.append(f"high:{event.event_name}")
                return HookResult(status="ok")

        class MediumBrokenHook:
            events: ClassVar[list[str]] = ["session:start"]
            priority: ClassVar[int] = 50

            def handle(self, event: HookEvent) -> HookResult:
                call_log.append("medium:broken")
                msg = "intentional failure"
                raise RuntimeError(msg)

        class LowPriorityHook:
            events: ClassVar[list[str]] = ["session:start"]
            priority: ClassVar[int] = 0

            def handle(self, event: HookEvent) -> HookResult:
                call_log.append(f"low:{event.event_name}")
                return HookResult(status="ok")

        # Protocol conformance
        from raise_cli.hooks.protocol import LifecycleHook

        assert isinstance(HighPriorityHook(), LifecycleHook)
        assert isinstance(MediumBrokenHook(), LifecycleHook)
        assert isinstance(LowPriorityHook(), LifecycleHook)

        # Registry
        registry = HookRegistry()
        registry.register(LowPriorityHook())
        registry.register(HighPriorityHook())
        registry.register(MediumBrokenHook())

        # Verify priority sorting
        hooks = registry.get_hooks_for_event("session:start")
        priorities = [h.priority for h in hooks]
        assert priorities == [100, 50, 0]

        # Emitter with registry
        emitter = EventEmitter(registry=registry)

        # Emit session:start — all 3 hooks fire
        result = emitter.emit(SessionStartEvent(session_id="SES-99", developer="test"))

        # Priority order: high (100) → medium broken (50) → low (0)
        assert call_log == ["high:session:start", "medium:broken", "low:session:start"]
        # Error from broken hook captured
        assert len(result.handler_errors) == 1
        assert "intentional failure" in result.handler_errors[0]
        # Not aborted (after: event)
        assert not result.aborted

        # Emit graph:build — only high hook subscribes
        call_log.clear()
        result = emitter.emit(
            GraphBuildEvent(project_path=Path("/tmp"), node_count=10, edge_count=5)
        )
        assert call_log == ["high:graph:build"]
        assert result.handler_errors == ()

    def test_full_pipeline_before_event_with_abort(self) -> None:
        """Before: event with abort + registry hooks."""

        class ComplianceHook:
            events: ClassVar[list[str]] = ["before:release:publish"]
            priority: ClassVar[int] = 100

            def handle(self, event: HookEvent) -> HookResult:
                return HookResult(status="abort", message="Not compliant")

        class AuditHook:
            events: ClassVar[list[str]] = ["before:release:publish"]
            priority: ClassVar[int] = 0

            def __init__(self) -> None:
                self.called = False

            def handle(self, event: HookEvent) -> HookResult:
                self.called = True
                return HookResult(status="ok")

        registry = HookRegistry()
        registry.register(ComplianceHook())
        audit = AuditHook()
        registry.register(audit)

        emitter = EventEmitter(registry=registry)
        result = emitter.emit(
            BeforeReleasePublishEvent(version="3.0.0", project_path=Path("."))
        )

        # Aborted by compliance hook
        assert result.aborted
        assert result.abort_message == "Not compliant"
        # Audit hook still ran (all-notify semantics)
        assert audit.called
