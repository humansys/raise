"""Tests for rai adapter CLI commands."""

from __future__ import annotations

import json
from importlib.metadata import EntryPoint
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _make_entry_point(name: str, group: str, value: str) -> EntryPoint:
    """Create a synthetic EntryPoint for testing."""
    return EntryPoint(name=name, group=group, value=value)


class TestAdaptersList:
    """Tests for `rai adapter list`."""

    def test_list_shows_registered_parsers(self) -> None:
        result = runner.invoke(app, ["adapter", "list"])
        assert result.exit_code == 0
        # Built-in governance parsers from pyproject.toml
        assert "prd" in result.output
        assert "vision" in result.output
        assert "backlog" in result.output
        assert "GovernanceParser" in result.output

    def test_list_shows_graph_backends_group(self) -> None:
        result = runner.invoke(app, ["adapter", "list"])
        assert result.exit_code == 0
        assert "KnowledgeGraphBackend" in result.output

    def test_list_shows_empty_groups(self) -> None:
        result = runner.invoke(app, ["adapter", "list"])
        assert result.exit_code == 0
        # PM adapters group exists but has no registrations
        assert "ProjectManagementAdapter" in result.output
        assert "(none)" in result.output

    def test_list_shows_tier(self) -> None:
        result = runner.invoke(app, ["adapter", "list"])
        assert result.exit_code == 0
        assert "Tier:" in result.output

    def test_list_json_format(self) -> None:
        result = runner.invoke(app, ["adapter", "list", "--format", "json"])
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
        result = runner.invoke(app, ["adapter", "list", "--format", "json"])
        data = json.loads(result.output)
        parsers_group = next(
            g for g in data["groups"] if g["group"] == "rai.governance.parsers"
        )
        assert len(parsers_group["adapters"]) > 0
        adapter = parsers_group["adapters"][0]
        assert "name" in adapter
        assert "package" in adapter


class TestAdaptersCheck:
    """Tests for `rai adapter check`."""

    def test_check_builtins_pass(self) -> None:
        result = runner.invoke(app, ["adapter", "check"])
        assert result.exit_code == 0
        # All built-in adapters should be compliant
        assert "compliant" in result.output or "passed" in result.output

    def test_check_json_format(self) -> None:
        result = runner.invoke(app, ["adapter", "check", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "results" in data
        assert "all_passed" in data
        assert "total" in data
        assert isinstance(data["results"], list)

    def test_check_json_all_builtins_compliant(self) -> None:
        result = runner.invoke(app, ["adapter", "check", "--format", "json"])
        data = json.loads(result.output)
        for r in data["results"]:
            assert r["compliant"] is True, f"{r['name']} in {r['group']} not compliant"

    def test_check_broken_entry_point_shows_error(self) -> None:
        """Mock a broken entry point that fails to load."""
        broken_ep = _make_entry_point(
            name="broken",
            group="rai.adapters.pm",
            value="nonexistent.module:FakeClass",
        )

        original_entry_points = __import__(
            "importlib.metadata", fromlist=["entry_points"]
        ).entry_points

        def patched_entry_points(*, group: str) -> list[EntryPoint]:
            if group == "rai.adapters.pm":
                return [broken_ep]
            return list(original_entry_points(group=group))

        with patch(
            "raise_cli.cli.commands.adapters.entry_points",
            side_effect=patched_entry_points,
        ):
            result = runner.invoke(app, ["adapter", "check", "--format", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["all_passed"] is False
        broken_results = [r for r in data["results"] if r["name"] == "broken"]
        assert len(broken_results) == 1
        assert broken_results[0]["compliant"] is False
        assert "Failed to load" in broken_results[0]["error"]
