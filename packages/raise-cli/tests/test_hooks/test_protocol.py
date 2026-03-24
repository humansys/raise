"""Tests for LifecycleHook Protocol."""

from __future__ import annotations

from typing import ClassVar

from raise_cli.hooks.events import HookEvent, HookResult
from raise_cli.hooks.protocol import LifecycleHook


class _CompliantHook:
    """Hook that satisfies the LifecycleHook Protocol."""

    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class _CompliantHighPriority:
    """Hook with non-default priority."""

    events: ClassVar[list[str]] = ["session:start", "graph:build"]
    priority: ClassVar[int] = 100

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok", message="high priority")


class _MissingHandle:
    """Missing handle method — not compliant."""

    events: ClassVar[list[str]] = ["session:start"]
    priority: ClassVar[int] = 0


class _MissingEvents:
    """Missing events — not compliant."""

    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class _MissingPriority:
    """Missing priority — not compliant."""

    events: ClassVar[list[str]] = ["session:start"]

    def handle(self, event: HookEvent) -> HookResult:
        return HookResult(status="ok")


class TestLifecycleHookProtocol:
    """Protocol conformance tests."""

    def test_compliant_hook_is_instance(self) -> None:
        assert isinstance(_CompliantHook(), LifecycleHook)

    def test_compliant_high_priority_is_instance(self) -> None:
        assert isinstance(_CompliantHighPriority(), LifecycleHook)

    def test_missing_handle_is_not_instance(self) -> None:
        assert not isinstance(_MissingHandle(), LifecycleHook)

    def test_missing_events_is_not_instance(self) -> None:
        assert not isinstance(_MissingEvents(), LifecycleHook)

    def test_missing_priority_is_not_instance(self) -> None:
        assert not isinstance(_MissingPriority(), LifecycleHook)
