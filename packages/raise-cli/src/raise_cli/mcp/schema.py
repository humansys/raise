"""MCP server configuration schema.

Defines the YAML config format for ``.raise/mcp/*.yaml`` and the shared
``ServerConnection`` model used by both MCP registry and declarative adapters.

Architecture: ADR-042, E338 (AR-C2)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ServerConnection(BaseModel):
    """MCP server connection configuration.

    Shared between MCP registry (``McpServerConfig``) and declarative
    adapters (``DeclarativeAdapterConfig``). Eliminates duplication (AR-C2).
    """

    command: str = Field(..., description="Server command (e.g. 'uvx', 'npx')")
    args: list[str] = Field(
        default_factory=list, description="Server command arguments"
    )
    env: list[str] | None = Field(
        default=None,
        description="Env var names to pass to server subprocess",
    )


class McpServerConfig(BaseModel):
    """Root config model for a generic MCP server.

    Parsed from ``.raise/mcp/<name>.yaml``. Not tied to any domain protocol.
    """

    name: str = Field(..., description="Server name (used in rai mcp commands)")
    description: str | None = Field(
        default=None, description="Human-readable description"
    )
    server: ServerConnection
