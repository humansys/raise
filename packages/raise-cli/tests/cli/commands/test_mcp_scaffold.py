"""Tests for `rai mcp scaffold` command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import yaml
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.schema import McpServerConfig

runner = CliRunner()


def _mock_tool(name: str, description: str) -> MagicMock:
    t = MagicMock()
    t.name = name
    t.description = description
    return t


class TestScaffoldSuccess:
    """AC Scenario 1: Generates valid YAML from running server."""

    def test_generates_valid_yaml(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = [
            _mock_tool("resolve-library-id", "Resolve a library"),
            _mock_tool("query-docs", "Query documentation"),
        ]
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "context7",
                    "--command",
                    "npx",
                    "--args",
                    "-y @upstash/context7-mcp",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        yaml_path = mcp_dir / "context7.yaml"
        assert yaml_path.exists()

        # Verify parseable by McpServerConfig
        raw = yaml.safe_load(yaml_path.read_text())
        config = McpServerConfig.model_validate(raw)
        assert config.name == "context7"
        assert config.server.command == "npx"
        assert config.server.args == ["-y", "@upstash/context7-mcp"]

    def test_tool_names_in_comments(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = [
            _mock_tool("tool-a", "Tool A"),
            _mock_tool("tool-b", "Tool B"),
        ]
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "myserver",
                    "--command",
                    "echo",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0
        content = (mcp_dir / "myserver.yaml").read_text()
        assert "tool-a" in content
        assert "tool-b" in content


class TestScaffoldCreatesDirectory:
    """AC Scenario 3: Creates .raise/mcp/ if missing."""

    def test_creates_mcp_dir(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        assert not mcp_dir.exists()

        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = []
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "test-server",
                    "--command",
                    "echo",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0
        assert mcp_dir.is_dir()
        assert (mcp_dir / "test-server.yaml").exists()


class TestScaffoldOverwriteProtection:
    """AC Scenario 4: Refuses overwrite without --force."""

    def test_refuses_overwrite(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mcp_dir.mkdir(parents=True)
        original = "name: existing\n"
        (mcp_dir / "existing.yaml").write_text(original)

        result = runner.invoke(
            app,
            [
                "mcp",
                "scaffold",
                "existing",
                "--command",
                "echo",
                "--mcp-dir",
                str(mcp_dir),
            ],
        )
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()
        # File content preserved
        assert (mcp_dir / "existing.yaml").read_text() == original

    def test_force_overwrites(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mcp_dir.mkdir(parents=True)
        (mcp_dir / "existing.yaml").write_text("name: existing\n")

        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = []
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "existing",
                    "--command",
                    "echo",
                    "--force",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0
        raw = yaml.safe_load((mcp_dir / "existing.yaml").read_text())
        assert raw["server"]["command"] == "echo"


class TestScaffoldServerError:
    """AC Scenario 2: Unreachable server → exit 1."""

    def test_connection_error(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mock_bridge = AsyncMock()
        mock_bridge.list_tools.side_effect = Exception("Connection refused")
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "bad-server",
                    "--command",
                    "nonexistent",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code != 0
        assert "Connection refused" in result.output


class TestScaffoldWithEnv:
    """Env var names passed through to config."""

    def test_env_in_generated_yaml(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = []
        mock_bridge.aclose.return_value = None

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=mock_bridge,
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "scaffold",
                    "myserver",
                    "--command",
                    "uvx",
                    "--env",
                    "GITHUB_TOKEN,API_KEY",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0
        raw = yaml.safe_load((mcp_dir / "myserver.yaml").read_text())
        config = McpServerConfig.model_validate(raw)
        assert config.server.env == ["GITHUB_TOKEN", "API_KEY"]
