"""Tests for MCP schema models (T3).

Verifies ServerConnection, McpServerConfig, and declarative adapter compat.
"""

from __future__ import annotations

import pytest


class TestServerConnection:
    def test_valid_connection(self) -> None:
        from raise_cli.mcp.schema import ServerConnection

        conn = ServerConnection(command="npx", args=["-y", "mcp-server"], env=["TOKEN"])
        assert conn.command == "npx"
        assert conn.args == ["-y", "mcp-server"]
        assert conn.env == ["TOKEN"]

    def test_defaults(self) -> None:
        from raise_cli.mcp.schema import ServerConnection

        conn = ServerConnection(command="uvx")
        assert conn.args == []
        assert conn.env is None

    def test_missing_command_fails(self) -> None:
        from pydantic import ValidationError

        from raise_cli.mcp.schema import ServerConnection

        with pytest.raises(ValidationError):
            ServerConnection()  # type: ignore[call-arg]


class TestMcpServerConfig:
    def test_valid_config(self) -> None:
        from raise_cli.mcp.schema import McpServerConfig, ServerConnection

        config = McpServerConfig(
            name="context7",
            description="Library docs via Context7",
            server=ServerConnection(
                command="npx", args=["-y", "@upstash/context7-mcp"]
            ),
        )
        assert config.name == "context7"
        assert config.description == "Library docs via Context7"
        assert config.server.command == "npx"

    def test_missing_name_fails(self) -> None:
        from pydantic import ValidationError

        from raise_cli.mcp.schema import McpServerConfig, ServerConnection

        with pytest.raises(ValidationError):
            McpServerConfig(
                server=ServerConnection(command="npx"),
            )  # type: ignore[call-arg]

    def test_description_optional(self) -> None:
        from raise_cli.mcp.schema import McpServerConfig, ServerConnection

        config = McpServerConfig(
            name="test",
            server=ServerConnection(command="echo"),
        )
        assert config.description is None


class TestDeclarativeBackwardsCompat:
    def test_declarative_config_with_server_connection(self) -> None:
        """DeclarativeAdapterConfig still works after ServerConfig → ServerConnection."""
        from raise_cli.adapters.declarative.schema import DeclarativeAdapterConfig

        raw = {
            "adapter": {"name": "github", "protocol": "pm"},
            "server": {
                "command": "uvx",
                "args": ["mcp-github"],
                "env": ["GITHUB_TOKEN"],
            },
            "methods": {},
        }
        config = DeclarativeAdapterConfig.model_validate(raw)
        assert config.server.command == "uvx"
        assert config.server.args == ["mcp-github"]
        assert config.server.env == ["GITHUB_TOKEN"]
        assert config.adapter.protocol == "pm"
