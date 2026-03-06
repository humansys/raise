"""MCP infrastructure layer — independent of domain adapters.

Provides generic MCP server management: bridge, models, schema, registry.
Domain adapters (PM, Docs) live in ``raise_cli.adapters`` and consume this layer.

Architecture: ADR-042, E338

Note: Bridge imports are lazy because the ``mcp`` SDK and ``logfire-api``
are optional dependencies. Eager import would crash CLI startup when
these packages are not installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from raise_cli.mcp.models import McpHealthResult, McpToolInfo, McpToolResult
from raise_cli.mcp.registry import discover_mcp_servers
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

if TYPE_CHECKING:
    from raise_cli.mcp.bridge import McpBridge, McpBridgeError

__all__ = [
    "McpBridge",
    "McpBridgeError",
    "McpHealthResult",
    "McpServerConfig",
    "McpToolInfo",
    "McpToolResult",
    "ServerConnection",
    "discover_mcp_servers",
]
