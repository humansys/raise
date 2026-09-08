"""Telemetry adapter registry — resolves runtime → AgentTelemetryAdapter.

Simple dict-based registry. Entry points deferred until 2+ adapters exist (YAGNI).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

log = logging.getLogger(__name__)

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
    if runtime not in adapters:
        log.warning(
            "Unknown agent runtime %r — telemetry disabled (NullTelemetryAdapter). "
            "Set RAISE_AGENT_RUNTIME to a known value (e.g. 'claude_code') to enable "
            "cost reporting. RAISE_AGENT_COMMAND is the cockpit launch var "
            "and must not be confused with RAISE_AGENT_RUNTIME. (RAISE-15790)",
            runtime,
        )
        return NullTelemetryAdapter()
    return adapters[runtime]
