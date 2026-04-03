"""LifecycleHook Protocol — contract for hook implementations.

Hooks react to CLI lifecycle events (telemetry, notifications, compliance).
A hook failure is logged and skipped — hooks never crash the CLI.

Architecture: ADR-039 §1 (LifecycleHook Protocol)
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from raise_cli.hooks.events import HookEvent, HookResult


@runtime_checkable
class LifecycleHook(Protocol):
    """Contract for lifecycle hook implementations.

    Attributes:
        events: Event names this hook subscribes to (e.g. ``["session:start"]``).
        priority: Dispatch order — higher runs first. Default ``0``.

    Example::

        class TelemetryHook:
            events = ["session:start", "graph:build"]
            priority = 0

            def handle(self, event: HookEvent) -> HookResult:
                # write to signals.jsonl...
                return HookResult(status="ok")
    """

    events: ClassVar[list[str]]
    priority: ClassVar[int]

    def handle(self, event: HookEvent) -> HookResult: ...
