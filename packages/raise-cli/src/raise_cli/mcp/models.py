"""MCP infrastructure models — independent of domain adapters.

These models belong to the MCP infrastructure layer. Domain adapters
(PM, Docs) have their own models in ``raise_cli.adapters.models``.

Architecture: ADR-042, E338 (AR-C1)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class McpToolResult(BaseModel):
    """Parsed result from an MCP tool call."""

    text: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    is_error: bool = False
    error_message: str = ""


class McpToolInfo(BaseModel):
    """Tool metadata from server discovery."""

    name: str
    description: str = ""


class McpHealthResult(BaseModel):
    """Health check result for an MCP server.

    Independent of AdapterHealth (domain layer). Adapters convert
    McpHealthResult → AdapterHealth when needed.
    """

    server_name: str = Field(..., description="MCP server identifier")
    healthy: bool = Field(..., description="Whether server responded")
    message: str = Field(default="", description="Status or error message")
    latency_ms: int | None = Field(default=None, description="Response latency in ms")
    tool_count: int = Field(default=0, description="Number of tools discovered")
