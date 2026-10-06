"""MCP infrastructure layer — independent of domain adapters.

Provides generic MCP server management: bridge, models, schema, registry.
Domain adapters (PM, Docs) live in ``raise_cli.adapters`` and consume this layer.

Architecture: ADR-042, E338
"""

from __future__ import annotations

from raise_cli.mcp.bridge import McpBridge, McpBridgeError
from raise_cli.mcp.models import McpHealthResult, McpToolInfo, McpToolResult
from raise_cli.mcp.registry import discover_mcp_servers
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

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
