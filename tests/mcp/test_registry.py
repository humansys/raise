"""Tests for MCP server registry discovery (T4).

Verifies discover_mcp_servers() scans .raise/mcp/*.yaml correctly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def mcp_dir(tmp_path: Path) -> Path:
    """Create a temporary .raise/mcp/ directory."""
    d = tmp_path / ".raise" / "mcp"
    d.mkdir(parents=True)
    return d


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.dump(data), encoding="utf-8")


class TestDiscoverMcpServers:
    def test_empty_when_dir_missing(self, tmp_path: Path) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        result = discover_mcp_servers(mcp_dir=tmp_path / "nonexistent")
        assert result == {}

    def test_discovers_valid_yaml(self, mcp_dir: Path) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        _write_yaml(
            mcp_dir / "context7.yaml",
            {
                "name": "context7",
                "description": "Library docs",
                "server": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]},
            },
        )
        _write_yaml(
            mcp_dir / "snyk.yaml",
            {
                "name": "snyk",
                "server": {"command": "uvx", "args": ["mcp-snyk"]},
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert len(result) == 2
        assert "context7" in result
        assert "snyk" in result
        assert result["context7"].server.command == "npx"
        assert result["snyk"].description is None

    def test_skips_invalid_yaml(
        self, mcp_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        (mcp_dir / "bad.yaml").write_text("{{invalid yaml", encoding="utf-8")
        _write_yaml(
            mcp_dir / "good.yaml",
            {
                "name": "good",
                "server": {"command": "echo"},
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert len(result) == 1
        assert "good" in result
        assert "bad.yaml" in caplog.text

    def test_skips_schema_validation_error(
        self, mcp_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        _write_yaml(
            mcp_dir / "broken.yaml",
            {
                "server": {"command": "echo"},
                # missing "name" field
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert result == {}
        assert "broken.yaml" in caplog.text

    def test_duplicate_names_first_wins(
        self, mcp_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        _write_yaml(
            mcp_dir / "a_first.yaml",
            {
                "name": "dupe",
                "server": {"command": "first"},
            },
        )
        _write_yaml(
            mcp_dir / "b_second.yaml",
            {
                "name": "dupe",
                "server": {"command": "second"},
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert len(result) == 1
        assert result["dupe"].server.command == "first"
        assert "already defined" in caplog.text

    def test_skips_catalog_yaml(self, mcp_dir: Path) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        _write_yaml(
            mcp_dir / "catalog.yaml",
            {
                "servers": {
                    "context7": {"package": "@upstash/context7-mcp", "type": "npx"},
                },
            },
        )
        _write_yaml(
            mcp_dir / "context7.yaml",
            {
                "name": "context7",
                "server": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]},
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert len(result) == 1
        assert "context7" in result

    def test_ignores_non_yaml_files(self, mcp_dir: Path) -> None:
        from raise_cli.mcp.registry import discover_mcp_servers

        (mcp_dir / "readme.md").write_text("# Not YAML", encoding="utf-8")
        _write_yaml(
            mcp_dir / "valid.yaml",
            {
                "name": "valid",
                "server": {"command": "echo"},
            },
        )

        result = discover_mcp_servers(mcp_dir=mcp_dir)
        assert len(result) == 1
