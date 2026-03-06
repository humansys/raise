"""Built-in TelemetryHook — writes CommandUsage signals for lifecycle events.

First real LifecycleHook implementation. Subscribes to all 9 after-events
and maps each to a ``CommandUsage`` telemetry signal via ``emit_command_usage()``.

Error isolation: ``handle()`` never raises. Emit failures are logged and
returned as ``HookResult(status="error")``.

Architecture: ADR-039 §5 (Built-in hooks), S248.3
"""

from __future__ import annotations

import logging
from typing import ClassVar

from raise_cli.hooks.events import HookEvent, HookResult
from raise_cli.telemetry.writer import emit_command_usage

logger = logging.getLogger(__name__)


class TelemetryHook:
    """Writes CommandUsage signals for CLI lifecycle events.

    Maps event names to command/subcommand pairs::

        "session:start"  → command="session", subcommand="start"
        "graph:build"    → command="graph",   subcommand="build"

    Registered via ``rai.hooks`` entry point in pyproject.toml.
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
    ]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        """Map event to CommandUsage signal and emit.

        Never raises — returns ``HookResult(status="error")`` on failure.
        """
        command, subcommand = event.event_name.split(":", 1)

        try:
            result = emit_command_usage(command, subcommand)
        except Exception as exc:  # noqa: BLE001
            msg = f"{type(exc).__name__}: {exc}"
            logger.warning(
                "TelemetryHook emit failed for '%s': %s", event.event_name, msg
            )
            return HookResult(status="error", message=msg)

        if not result.success:
            logger.warning(
                "TelemetryHook emit failed for '%s': %s",
                event.event_name,
                result.error,
            )
            return HookResult(status="error", message=result.error or "unknown error")

        logger.debug("TelemetryHook emitted CommandUsage for '%s'", event.event_name)
        return HookResult(status="ok")
