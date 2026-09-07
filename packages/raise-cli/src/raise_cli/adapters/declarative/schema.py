"""Pydantic models for declarative MCP adapter YAML config.

Validates the YAML structure used by DeclarativeMcpAdapter.
No ``model`` field in ResponseMapping — the adapter infers
the return type from the protocol method name (AR-R1).

Architecture: ADR-041, E337, E338 (AR-C2: shared ServerConnection)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AdapterMeta(BaseModel):
    """Top-level adapter identity and protocol selection."""

    name: str = Field(..., description="Adapter name (used in --adapter flag)")
    protocol: Literal["pm", "docs"] = Field(
        ..., description="Protocol: 'pm' (ProjectManagement) or 'docs' (Documentation)"
    )
    description: str | None = Field(
        default=None, description="Human-readable description"
    )


class ResponseMapping(BaseModel):
    """How to parse MCP tool response into adapter models.

    No ``model`` field — adapter infers return type from method name (AR-R1).
    """

    fields: dict[str, str] = Field(
        ..., description="Field name → expression template mapping"
    )
    items_path: str | None = Field(
        default=None,
        description="Dot-path to list in response (e.g. 'data.items')",
    )


class MethodMapping(BaseModel):
    """Maps a protocol method to an MCP tool call."""

    tool: str = Field(..., description="MCP tool name to call")
    args: dict[str, str] = Field(
        default_factory=dict,
        description="Argument name → expression template mapping",
    )
    response: ResponseMapping | None = Field(
        default=None, description="Response parsing config (None = raw result)"
    )


class ServerRef(BaseModel):
    """Server config: reference MCP registry OR inline connection.

    Either ``ref`` (name in ``.raise/mcp/`` registry) or ``command``
    (inline connection) must be provided. Both may be set but ref
    takes precedence at resolution time.

    Architecture: E338 S338.5 — Option B (separate from ServerConnection).
    """

    ref: str | None = Field(default=None, description="Name in .raise/mcp/ registry")
    command: str | None = Field(
        default=None, description="Server command (e.g. 'uvx', 'npx')"
    )
    args: list[str] = Field(
        default_factory=list, description="Server command arguments"
    )
    env: list[str] | None = Field(
        default=None,
        description="Env var names to pass to server subprocess",
    )

    @model_validator(mode="after")
    def _ref_or_command(self) -> ServerRef:
        if self.ref is None and self.command is None:
            msg = "Either 'ref' or 'command' must be provided"
            raise ValueError(msg)
        return self


class DeclarativeAdapterConfig(BaseModel):
    """Root config model for a declarative MCP adapter.

    Parsed from ``.raise/adapters/<name>.yaml``.
    """

    adapter: AdapterMeta
    server: ServerRef
    methods: dict[str, MethodMapping | None] = Field(
        default_factory=dict,
        description="Protocol method → MCP tool mapping. None = unsupported.",
    )
