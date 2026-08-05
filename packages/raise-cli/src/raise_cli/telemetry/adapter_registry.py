"""Telemetry adapter registry — resolves runtime → AgentTelemetryAdapter.

Simple dict-based registry. Entry points deferred until 2+ adapters exist (YAGNI).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_core.runtime.telemetry_adapter import AgentTelemetryAdapter


def get_telemetry_adapter(
    *,
    override: AgentTelemetryAdapter | None = None,
) -> AgentTelemetryAdapter:
    """Resolve the active telemetry adapter based on the detected runtime.

    Args:
        override: Explicit adapter (skips runtime detection). Useful for testing.
    """
    if override is not None:
        return override

    from raise_cli._agent_session import discover_agent_runtime
    from raise_cli.telemetry.cc_adapter import (
        ClaudeCodeTelemetryAdapter,
        NullTelemetryAdapter,
    )

    runtime = discover_agent_runtime()
    adapters: dict[str, AgentTelemetryAdapter] = {
        "claude_code": ClaudeCodeTelemetryAdapter(),
    }
    return adapters.get(runtime, NullTelemetryAdapter())
