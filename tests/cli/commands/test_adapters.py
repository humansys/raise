"""Tests for rai adapters CLI commands."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from rai_cli.cli.main import app

runner = CliRunner()


class TestAdaptersList:
    """Tests for `rai adapters list`."""

    def test_list_shows_registered_parsers(self) -> None:
        result = runner.invoke(app, ["adapters", "list"])
        assert result.exit_code == 0
        # Built-in governance parsers from pyproject.toml
        assert "prd" in result.output
        assert "vision" in result.output
        assert "backlog" in result.output
        assert "GovernanceParser" in result.output

    def test_list_shows_graph_backends_group(self) -> None:
        result = runner.invoke(app, ["adapters", "list"])
        assert result.exit_code == 0
        assert "KnowledgeGraphBackend" in result.output

    def test_list_shows_empty_groups(self) -> None:
        result = runner.invoke(app, ["adapters", "list"])
        assert result.exit_code == 0
        # PM adapters group exists but has no registrations
        assert "ProjectManagementAdapter" in result.output
        assert "(none)" in result.output

    def test_list_shows_tier(self) -> None:
        result = runner.invoke(app, ["adapters", "list"])
        assert result.exit_code == 0
        assert "Tier:" in result.output

    def test_list_json_format(self) -> None:
        result = runner.invoke(app, ["adapters", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tier" in data
        assert "groups" in data
        assert isinstance(data["groups"], list)
        # At least governance parsers and graph backends
        group_names = [g["group"] for g in data["groups"]]
        assert "rai.governance.parsers" in group_names
        assert "rai.graph.backends" in group_names

    def test_list_json_contains_adapter_details(self) -> None:
        result = runner.invoke(app, ["adapters", "list", "--format", "json"])
        data = json.loads(result.output)
        parsers_group = next(
            g for g in data["groups"] if g["group"] == "rai.governance.parsers"
        )
        assert len(parsers_group["adapters"]) > 0
        adapter = parsers_group["adapters"][0]
        assert "name" in adapter
        assert "package" in adapter
