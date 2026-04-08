"""Tests for HookRegistry."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import MagicMock, patch

from raise_cli.hooks.events import HookEvent, HookResult
from raise_cli.hooks.protocol import LifecycleHook
from raise_cli.hooks.registry import HookRegistry

# --- Test hook classes ---


class _LowPriorityHook:
    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class _HighPriorityHook:
    events: ClassVar[list[str]] = ["session:start", "graph:build"]
    priority: ClassVar[int] = 100

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class _MediumPriorityHook:
    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 50

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class _NonCompliantClass:
    """Does not satisfy LifecycleHook Protocol."""

    pass


class TestHookRegistryDiscover:
    """Discovery via entry points."""

    def test_discover_returns_empty_when_no_entry_points(self) -> None:
        registry = HookRegistry()
        with patch("raise_cli.hooks.registry.entry_points", return_value=[]):
            registry.discover()
        assert registry.hooks == []

    def test_discover_loads_compliant_hooks(self) -> None:
        ep = MagicMock()
        ep.name = "telemetry"
        ep.load.return_value = _LowPriorityHook

        registry = HookRegistry()
        with patch("raise_cli.hooks.registry.entry_points", return_value=[ep]):
            registry.discover()

        assert len(registry.hooks) == 1
        assert isinstance(registry.hooks[0], LifecycleHook)

    def test_discover_skips_non_class_entry_points(self) -> None:
        ep = MagicMock()
        ep.name = "bad"
        ep.load.return_value = "not a class"
        ep.dist = MagicMock()
        ep.dist.name = "bad-pkg"

        registry = HookRegistry()
        with patch("raise_cli.hooks.registry.entry_points", return_value=[ep]):
            registry.discover()

        assert registry.hooks == []

    def test_discover_skips_non_compliant_classes(self) -> None:
        ep = MagicMock()
        ep.name = "broken"
        ep.load.return_value = _NonCompliantClass
        ep.dist = MagicMock()
        ep.dist.name = "broken-pkg"

        registry = HookRegistry()
        with patch("raise_cli.hooks.registry.entry_points", return_value=[ep]):
            registry.discover()

        assert registry.hooks == []

    def test_discover_skips_entry_point_that_raises(self) -> None:
        ep = MagicMock()
        ep.name = "crasher"
        ep.load.side_effect = ImportError("missing dep")
        ep.dist = MagicMock()
        ep.dist.name = "crash-pkg"

        registry = HookRegistry()
        with patch("raise_cli.hooks.registry.entry_points", return_value=[ep]):
            registry.discover()

        assert registry.hooks == []

    def test_discover_multiple_hooks(self) -> None:
        ep_low = MagicMock()
        ep_low.name = "low"
        ep_low.load.return_value = _LowPriorityHook

        ep_high = MagicMock()
        ep_high.name = "high"
        ep_high.load.return_value = _HighPriorityHook

        registry = HookRegistry()
        with patch(
            "raise_cli.hooks.registry.entry_points", return_value=[ep_low, ep_high]
        ):
            registry.discover()

        assert len(registry.hooks) == 2


class TestHookRegistryGetHooksForEvent:
    """Priority-sorted event lookup."""

    def test_get_hooks_for_event_returns_matching_hooks(self) -> None:
        registry = HookRegistry()
        registry._hooks = [_LowPriorityHook(), _HighPriorityHook()]

        hooks = registry.get_hooks_for_event("session:start")
        assert len(hooks) == 2

    def test_get_hooks_for_event_sorted_by_priority_highest_first(self) -> None:
        registry = HookRegistry()
        registry._hooks = [
            _LowPriorityHook(),
            _HighPriorityHook(),
            _MediumPriorityHook(),
        ]

        hooks = registry.get_hooks_for_event("session:start")
        priorities = [h.priority for h in hooks]
        assert priorities == [100, 50, 0]

    def test_get_hooks_for_event_excludes_non_matching(self) -> None:
        registry = HookRegistry()
        registry._hooks = [_LowPriorityHook()]

        hooks = registry.get_hooks_for_event("graph:build")
        assert hooks == []

    def test_get_hooks_for_event_empty_registry(self) -> None:
        registry = HookRegistry()
        hooks = registry.get_hooks_for_event("session:start")
        assert hooks == []

    def test_hooks_property_returns_copy(self) -> None:
        """Hooks list should not be mutated externally."""
        registry = HookRegistry()
        registry._hooks = [_LowPriorityHook()]

        hooks_a = registry.hooks
        hooks_b = registry.hooks
        assert hooks_a is not hooks_b
        assert hooks_a == hooks_b


class TestHookRegistryManualRegister:
    """Manual hook registration (for testing without entry points)."""

    def test_register_adds_compliant_hook(self) -> None:
        registry = HookRegistry()
        hook = _LowPriorityHook()
        registry.register(hook)
        assert len(registry.hooks) == 1

    def test_register_rejects_non_compliant(self) -> None:
        registry = HookRegistry()
        non_compliant = _NonCompliantClass()
        # Should not raise, just skip
        registry.register(non_compliant)  # type: ignore[arg-type]
        assert registry.hooks == []
