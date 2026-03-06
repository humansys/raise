"""Tests for ServerRef resolution in DeclarativeMcpAdapter.

S338.5 AC scenarios 1 (ref resolves), 2 (inline compat), 4 (missing ref error).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from raise_cli.adapters.declarative.adapter import DeclarativeMcpAdapter
from raise_cli.adapters.declarative.schema import (
    AdapterMeta,
    DeclarativeAdapterConfig,
    ServerRef,
)
from raise_cli.mcp.bridge import McpBridgeError
from raise_cli.mcp.schema import McpServerConfig, ServerConnection


def _make_config(
    *, ref: str | None = None, command: str | None = None
) -> DeclarativeAdapterConfig:
    """Build a minimal DeclarativeAdapterConfig for testing."""
    return DeclarativeAdapterConfig(
        adapter=AdapterMeta(name="test-adapter", protocol="pm"),
        server=ServerRef(ref=ref, command=command, args=["test"]),
        methods={},
    )


_REGISTRY_SERVER = McpServerConfig(
    name="context7",
    description="Context7 docs server",
    server=ServerConnection(
        command="npx", args=["-y", "@upstash/context7-mcp"], env=["C7_TOKEN"]
    ),
)


class TestRefResolution:
    """AC Scenario 1: server.ref resolves from MCP registry."""

    def test_ref_resolves_to_registry_server(self) -> None:
        config = _make_config(ref="context7")
        with patch(
            "raise_cli.adapters.declarative.adapter.discover_mcp_servers",
            return_value={"context7": _REGISTRY_SERVER},
        ):
            adapter = DeclarativeMcpAdapter(config)
        # Bridge should use registry server's command and args
        assert adapter._bridge._server_command == "npx"
        assert adapter._bridge._server_args == ["-y", "@upstash/context7-mcp"]

    def test_ref_resolves_env_from_registry(self) -> None:
        config = _make_config(ref="context7")
        with patch(
            "raise_cli.adapters.declarative.adapter.discover_mcp_servers",
            return_value={"context7": _REGISTRY_SERVER},
        ):
            adapter = DeclarativeMcpAdapter(config)
        # Bridge env should include the registry server's env vars
        assert adapter._bridge._env is not None
        assert "C7_TOKEN" in adapter._bridge._env


class TestRefNotFound:
    """AC Scenario 4: ref to nonexistent server raises McpBridgeError."""

    def test_missing_ref_raises(self) -> None:
        config = _make_config(ref="nonexistent")
        with (
            patch(
                "raise_cli.adapters.declarative.adapter.discover_mcp_servers",
                return_value={},
            ),
            pytest.raises(McpBridgeError, match="nonexistent"),
        ):
            DeclarativeMcpAdapter(config)


class TestInlineCompat:
    """AC Scenario 2: inline server.command still works."""

    def test_inline_creates_bridge(self) -> None:
        config = _make_config(command="echo")
        adapter = DeclarativeMcpAdapter(config)
        assert adapter._bridge._server_command == "echo"
        assert adapter._bridge._server_args == ["test"]
