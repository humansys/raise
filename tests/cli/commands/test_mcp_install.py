"""Tests for `rai mcp install` command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import yaml
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.schema import McpServerConfig

runner = CliRunner()


def _mock_tool(name: str) -> MagicMock:
    t = MagicMock()
    t.name = name
    t.description = f"Tool {name}"
    return t


def _healthy_bridge() -> AsyncMock:
    bridge = AsyncMock()
    bridge.list_tools.return_value = [_mock_tool("tool-a")]
    bridge.aclose.return_value = None
    return bridge


class TestInstallNpx:
    """AC Scenario 1: Install via npx."""

    def test_npx_generates_config(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=_healthy_bridge(),
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "install",
                    "@upstash/context7-mcp",
                    "--type",
                    "npx",
                    "--name",
                    "context7",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        raw = yaml.safe_load((mcp_dir / "context7.yaml").read_text())
        config = McpServerConfig.model_validate(raw)
        assert config.name == "context7"
        assert config.server.command == "npx"
        assert config.server.args == ["-y", "@upstash/context7-mcp"]


class TestInstallUvx:
    """AC Scenario 2: Install via uvx."""

    def test_uvx_generates_config(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=_healthy_bridge(),
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "install",
                    "mcp-github",
                    "--type",
                    "uvx",
                    "--name",
                    "github",
                    "--env",
                    "GITHUB_TOKEN",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        raw = yaml.safe_load((mcp_dir / "github.yaml").read_text())
        config = McpServerConfig.model_validate(raw)
        assert config.server.command == "uvx"
        assert config.server.args == ["mcp-github"]
        assert config.server.env == ["GITHUB_TOKEN"]


class TestInstallPip:
    """AC Scenario 3: Install via pip."""

    def test_pip_generates_config(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"

        with (
            patch(
                "raise_cli.cli.commands.mcp.subprocess.run",
            ) as mock_pip,
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=_healthy_bridge(),
            ),
        ):
            mock_pip.return_value = MagicMock(returncode=0)
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "install",
                    "mcp-server-fetch",
                    "--type",
                    "pip",
                    "--name",
                    "fetch",
                    "--module",
                    "mcp_server_fetch",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        raw = yaml.safe_load((mcp_dir / "fetch.yaml").read_text())
        config = McpServerConfig.model_validate(raw)
        assert config.server.command == "python"
        assert config.server.args == ["-m", "mcp_server_fetch"]
        # pip install was called
        mock_pip.assert_called_once()

    def test_pip_without_module_fails(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        result = runner.invoke(
            app,
            [
                "mcp",
                "install",
                "mcp-server-fetch",
                "--type",
                "pip",
                "--name",
                "fetch",
                "--mcp-dir",
                str(mcp_dir),
            ],
        )
        assert result.exit_code != 0
        assert "module" in result.output.lower()

    def test_pip_install_failure(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"

        with patch(
            "raise_cli.cli.commands.mcp.subprocess.run",
        ) as mock_pip:
            mock_pip.return_value = MagicMock(returncode=1, stderr="Package not found")
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "install",
                    "bad-pkg",
                    "--type",
                    "pip",
                    "--name",
                    "bad",
                    "--module",
                    "bad_pkg",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code != 0
        assert not (mcp_dir / "bad.yaml").exists()


class TestInstallHealthFailure:
    """AC Scenario 4: Health check fails — warn but still write config."""

    def test_health_failure_still_writes_config(self, tmp_path: Path) -> None:
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
                    "install",
                    "flaky-server",
                    "--type",
                    "uvx",
                    "--name",
                    "flaky",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        # Exit 0 — install succeeded even though health failed
        assert result.exit_code == 0
        assert (mcp_dir / "flaky.yaml").exists()
        # Warning present in output
        assert "warning" in result.output.lower() or "health" in result.output.lower()


class TestInstallOverwrite:
    """Overwrite protection."""

    def test_refuses_overwrite(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mcp_dir.mkdir(parents=True)
        original = "name: existing\n"
        (mcp_dir / "existing.yaml").write_text(original)

        result = runner.invoke(
            app,
            [
                "mcp",
                "install",
                "pkg",
                "--type",
                "uvx",
                "--name",
                "existing",
                "--mcp-dir",
                str(mcp_dir),
            ],
        )
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()
        assert (mcp_dir / "existing.yaml").read_text() == original

    def test_force_overwrites(self, tmp_path: Path) -> None:
        mcp_dir = tmp_path / ".raise" / "mcp"
        mcp_dir.mkdir(parents=True)
        (mcp_dir / "existing.yaml").write_text("name: existing\n")

        with patch(
            "raise_cli.mcp.bridge.McpBridge",
            return_value=_healthy_bridge(),
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "install",
                    "new-pkg",
                    "--type",
                    "uvx",
                    "--name",
                    "existing",
                    "--force",
                    "--mcp-dir",
                    str(mcp_dir),
                ],
            )
        assert result.exit_code == 0
        raw = yaml.safe_load((mcp_dir / "existing.yaml").read_text())
        assert raw["server"]["command"] == "uvx"
