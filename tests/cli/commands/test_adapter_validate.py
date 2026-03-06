"""Tests for `rai adapter validate` CLI command and reference config."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import yaml
from typer.testing import CliRunner

from raise_cli.adapters.declarative.schema import DeclarativeAdapterConfig
from raise_cli.cli.main import app

runner = CliRunner()

# All 11 PM protocol methods from AsyncProjectManagementAdapter
PM_METHODS = {
    "create_issue",
    "get_issue",
    "update_issue",
    "transition_issue",
    "batch_transition",
    "link_to_parent",
    "link_issues",
    "add_comment",
    "get_comments",
    "search",
    "health",
}


class TestReferenceConfig:
    """Reference github.yaml validates and covers all PM methods."""

    def test_reference_yaml_validates(self) -> None:
        """Reference config parses into a valid DeclarativeAdapterConfig."""
        ref_dir = resources.files("raise_cli.adapters.declarative.reference")
        yaml_path = ref_dir / "github.yaml"
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
        config = DeclarativeAdapterConfig.model_validate(raw)
        assert config.adapter.name == "github"
        assert config.adapter.protocol == "pm"

    def test_reference_covers_all_pm_methods(self) -> None:
        """Reference config has entries for all 11 PM protocol methods."""
        ref_dir = resources.files("raise_cli.adapters.declarative.reference")
        yaml_path = ref_dir / "github.yaml"
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
        config = DeclarativeAdapterConfig.model_validate(raw)
        assert set(config.methods.keys()) == PM_METHODS


class TestValidateCommand:
    """Tests for `rai adapter validate <file>`."""

    def test_valid_config_exits_zero(self, tmp_path: Path) -> None:
        """Valid YAML config → exit 0, shows adapter name and protocol."""
        cfg = tmp_path / "good.yaml"
        cfg.write_text(
            "adapter:\n  name: test\n  protocol: pm\n"
            "server:\n  command: echo\n  args: [hi]\n"
            "methods:\n  search:\n    tool: t\n    args:\n      q: '{{ query }}'\n"
        )
        result = runner.invoke(app, ["adapter", "validate", str(cfg)])
        assert result.exit_code == 0
        assert "Valid" in result.output
        assert "test" in result.output
        assert "pm" in result.output

    def test_valid_config_shows_method_counts(self, tmp_path: Path) -> None:
        """Valid config output includes mapped and unsupported method counts."""
        cfg = tmp_path / "methods.yaml"
        cfg.write_text(
            "adapter:\n  name: x\n  protocol: pm\n"
            "server:\n  command: echo\n  args: []\n"
            "methods:\n"
            "  search:\n    tool: t\n    args:\n      q: '{{ query }}'\n"
            "  health: null\n"
        )
        result = runner.invoke(app, ["adapter", "validate", str(cfg)])
        assert result.exit_code == 0
        assert "1 mapped" in result.output
        assert "1 unsupported" in result.output

    def test_invalid_schema_exits_one(self, tmp_path: Path) -> None:
        """Missing required fields → exit 1, shows field errors."""
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("adapter:\n  protocol: pm\nserver:\n  command: echo\n")
        result = runner.invoke(app, ["adapter", "validate", str(cfg)])
        assert result.exit_code == 1
        assert "Invalid" in result.output
        assert "name" in result.output  # field error for missing name

    def test_missing_file_exits_one(self) -> None:
        """Nonexistent file → exit 1, file not found error."""
        result = runner.invoke(app, ["adapter", "validate", "/nonexistent.yaml"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_empty_file_exits_one(self, tmp_path: Path) -> None:
        """Empty YAML file → exit 1."""
        cfg = tmp_path / "empty.yaml"
        cfg.write_text("")
        result = runner.invoke(app, ["adapter", "validate", str(cfg)])
        assert result.exit_code == 1

    def test_non_yaml_exits_one(self, tmp_path: Path) -> None:
        """Non-YAML content → exit 1."""
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("<<<not yaml>>>: [[[")
        result = runner.invoke(app, ["adapter", "validate", str(cfg)])
        assert result.exit_code == 1


class TestValidateE2E:
    """End-to-end: validate shipped reference config via CLI."""

    def test_validate_reference_github_yaml(self) -> None:
        """Full path: shipped github.yaml → CLI validate → success output."""
        ref_dir = resources.files("raise_cli.adapters.declarative.reference")
        yaml_path = ref_dir / "github.yaml"
        result = runner.invoke(app, ["adapter", "validate", str(yaml_path)])
        assert result.exit_code == 0
        assert "Valid" in result.output
        assert "github" in result.output
        assert "pm" in result.output
        assert "GitHub Issues" in result.output  # description
        # All 11 methods: 7 mapped + 4 null (batch_transition, link_to_parent, link_issues, health)
        assert "7 mapped" in result.output
        assert "4 unsupported" in result.output
