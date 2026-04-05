"""Tests for _resolve_env MCP env var resolution (RAISE-539)."""

from __future__ import annotations

from unittest.mock import patch

from raise_cli.cli.commands.mcp import _resolve_env
from raise_cli.mcp.schema import McpServerConfig, ServerConnection


def _config_with_env(env: list[str] | None) -> McpServerConfig:
    """Create a minimal McpServerConfig with given env list."""
    return McpServerConfig(
        name="test",
        server=ServerConnection(command="echo", args=[], env=env),
    )


class TestResolveEnv:
    """Tests for _resolve_env KEY=VALUE parsing (RAISE-539)."""

    def test_none_env_returns_none(self) -> None:
        """No env configured returns None."""
        config = _config_with_env(None)
        assert _resolve_env(config) is None

    def test_empty_env_returns_none(self) -> None:
        """Empty env list returns None."""
        config = _config_with_env([])
        assert _resolve_env(config) is None

    def test_key_value_inline(self) -> None:
        """KEY=VALUE in env list is parsed and used directly."""
        config = _config_with_env(["TOKEN=abc123"])
        result = _resolve_env(config)
        assert result is not None
        assert result["TOKEN"] == "abc123"

    def test_key_only_reads_from_environ(self) -> None:
        """Key-only entry reads from os.environ."""
        config = _config_with_env(["MY_VAR"])
        with patch.dict("os.environ", {"MY_VAR": "from_env"}, clear=False):
            result = _resolve_env(config)
        assert result is not None
        assert result["MY_VAR"] == "from_env"

    def test_key_only_missing_returns_empty(self) -> None:
        """Key-only entry missing from os.environ returns empty string."""
        config = _config_with_env(["NONEXISTENT_VAR_539"])
        with patch.dict("os.environ", {}, clear=False):
            result = _resolve_env(config)
        assert result is not None
        assert result["NONEXISTENT_VAR_539"] == ""

    def test_mixed_key_and_key_value(self) -> None:
        """Mixed entries: some KEY=VALUE, some KEY-only."""
        config = _config_with_env(["INLINE=secret", "FROM_ENV"])
        with patch.dict("os.environ", {"FROM_ENV": "envval"}, clear=False):
            result = _resolve_env(config)
        assert result is not None
        assert result["INLINE"] == "secret"
        assert result["FROM_ENV"] == "envval"

    def test_value_with_equals(self) -> None:
        """VALUE containing = is preserved (split on first = only)."""
        config = _config_with_env(["URL=https://host?a=1&b=2"])
        result = _resolve_env(config)
        assert result is not None
        assert result["URL"] == "https://host?a=1&b=2"
