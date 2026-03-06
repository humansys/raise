"""Tests for GateBridgeHook — bridges gate system into before: events."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import patch

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.hooks.events import (
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
)
from raise_cli.hooks.protocol import LifecycleHook

# ---------------------------------------------------------------------------
# Test gates for bridge tests
# ---------------------------------------------------------------------------


class _PassGate:
    gate_id: ClassVar[str] = "gate-pass"
    description: ClassVar[str] = "Always passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id, message="OK")


class _FailGate:
    gate_id: ClassVar[str] = "gate-fail"
    description: ClassVar[str] = "Always fails"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=False, gate_id=self.gate_id, message="Nope")


class _ExplodingGate:
    gate_id: ClassVar[str] = "gate-explode"
    description: ClassVar[str] = "Raises exception"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        msg = "kaboom"
        raise RuntimeError(msg)


class _SessionGate:
    gate_id: ClassVar[str] = "gate-session"
    description: ClassVar[str] = "Session gate"
    workflow_point: ClassVar[str] = "before:session:close"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id, message="OK")


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """GateBridgeHook must implement LifecycleHook Protocol."""

    def test_isinstance_check(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        assert isinstance(hook, LifecycleHook)

    def test_subscribes_to_before_events(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        assert "before:release:publish" in GateBridgeHook.events
        assert "before:session:close" in GateBridgeHook.events


# ---------------------------------------------------------------------------
# Gate execution
# ---------------------------------------------------------------------------


class TestGateExecution:
    """Bridge runs matching gates and returns abort/ok."""

    def test_all_pass_returns_ok(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        event = BeforeReleasePublishEvent(version="1.0")

        with patch("raise_cli.hooks.builtin.gate_bridge.GateRegistry") as mock_reg:
            instance = mock_reg.return_value
            instance.discover.return_value = None
            instance.get_gates_for_point.return_value = [_PassGate()]
            result = hook.handle(event)

        assert result.status == "ok"

    def test_one_fail_returns_abort(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        event = BeforeReleasePublishEvent(version="1.0")

        with patch("raise_cli.hooks.builtin.gate_bridge.GateRegistry") as mock_reg:
            instance = mock_reg.return_value
            instance.discover.return_value = None
            instance.get_gates_for_point.return_value = [_PassGate(), _FailGate()]
            result = hook.handle(event)

        assert result.status == "abort"
        assert "gate-fail" in result.message

    def test_no_matching_gates_returns_ok(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        event = BeforeReleasePublishEvent(version="1.0")

        with patch("raise_cli.hooks.builtin.gate_bridge.GateRegistry") as mock_reg:
            instance = mock_reg.return_value
            instance.discover.return_value = None
            instance.get_gates_for_point.return_value = []
            result = hook.handle(event)

        assert result.status == "ok"

    def test_gate_exception_treated_as_failure(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        event = BeforeReleasePublishEvent(version="1.0")

        with patch("raise_cli.hooks.builtin.gate_bridge.GateRegistry") as mock_reg:
            instance = mock_reg.return_value
            instance.discover.return_value = None
            instance.get_gates_for_point.return_value = [_ExplodingGate()]
            result = hook.handle(event)

        assert result.status == "abort"
        assert "gate-explode" in result.message

    def test_maps_event_name_to_workflow_point(self) -> None:
        from raise_cli.hooks.builtin.gate_bridge import GateBridgeHook

        hook = GateBridgeHook()
        event = BeforeSessionCloseEvent(session_id="SES-1")

        with patch("raise_cli.hooks.builtin.gate_bridge.GateRegistry") as mock_reg:
            instance = mock_reg.return_value
            instance.discover.return_value = None
            instance.get_gates_for_point.return_value = [_SessionGate()]
            result = hook.handle(event)

        instance.get_gates_for_point.assert_called_once_with("before:session:close")
        assert result.status == "ok"


# ---------------------------------------------------------------------------
# Entry point discovery
# ---------------------------------------------------------------------------


class TestEntryPointDiscovery:
    """GateBridgeHook is discoverable via rai.hooks entry point."""

    def test_registry_discovers_bridge(self) -> None:
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.discover()
        hook_types = [type(h).__name__ for h in registry.hooks]
        assert "GateBridgeHook" in hook_types

    def test_bridge_has_higher_priority_than_telemetry(self) -> None:
        from raise_cli.hooks.registry import HookRegistry

        registry = HookRegistry()
        registry.discover()
        bridge = next(h for h in registry.hooks if type(h).__name__ == "GateBridgeHook")
        telemetry = next(
            h for h in registry.hooks if type(h).__name__ == "TelemetryHook"
        )
        assert bridge.priority > telemetry.priority
