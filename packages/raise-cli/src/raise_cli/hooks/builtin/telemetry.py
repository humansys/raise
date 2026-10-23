"""Built-in TelemetryHook — thin wrapper delegating to UnifiedEmitter (S3672.1).

All emission logic lives in UnifiedEmitter. TelemetryHook remains as the
registered hook entry point so pyproject.toml and tests don't need changes.

Architecture: ADR-039 §5 (Built-in hooks), ADR-018 (local telemetry)
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.hooks.events import HookEvent, HookResult
from raise_cli.telemetry.emitter import default_emitter as _default_emitter


class TelemetryHook:
    """Delegates all hook emission to UnifiedEmitter._default_emitter.

    Events list expanded to include work lifecycle events (absorbed from
    ServerEmitHook in S3672.1).
    """

    events: ClassVar[list[str]] = [
        "session:start",
        "session:close",
        "graph:build",
        "pattern:added",
        "discover:scan",
        "init:complete",
        "adapter:loaded",
        "adapter:failed",
        "release:publish",
        "work:start",
        "work:close",
        "work:lifecycle",
    ]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        """Delegate to UnifiedEmitter. Never raises."""
        return _default_emitter.handle(event)
