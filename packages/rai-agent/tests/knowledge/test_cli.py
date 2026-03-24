"""Tests for knowledge CLI app."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from rai_agent.knowledge.cli import app

runner = CliRunner()


def _create_domain(base: Path, name: str = "test") -> Path:
    """Create a minimal valid domain for CLI testing."""
    domain_dir = base / name
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "extracted").mkdir(exist_ok=True)
    (domain_dir / "curated").mkdir(exist_ok=True)

    manifest = {
        "name": name,
        "display_name": f"{name.title()} Domain",
        "schema": {
            "module": "tests.knowledge.conftest",
            "class_name": "SampleNode",
        },
    }
    (domain_dir / "domain.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False)
    )

    # Add a valid node
    node = {
        "id": "c1",
        "type": "concept",
        "name": "Concept One",
        "summary": "A test concept",
    }
    _write_yaml(domain_dir / "extracted" / "c1.yaml", node)

    return domain_dir


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False))


class TestCheckCommand:
    def test_check_all_gates(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "demo")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["check", "demo"])
        assert result.exit_code == 0
        assert "gates" in result.output.lower()

    def test_check_single_gate(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "demo")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["check", "demo", "--gate", "validate"])
        assert result.exit_code == 0
        assert "validate" in result.output.lower()

    def test_check_json_output(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "demo")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["check", "demo", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 4  # 4 gates
        assert all("gate" in item for item in data)

    def test_check_nonexistent_domain(self, tmp_path: Path) -> None:
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["check", "nonexistent"])
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_check_unknown_gate(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "demo")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["check", "demo", "--gate", "bogus"])
        assert result.exit_code == 1
        assert "unknown gate" in result.output.lower()


class TestStatusCommand:
    def test_status_with_domains(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "alpha")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "alpha" in result.output
        assert "1 registered" in result.output

    def test_status_empty(self, tmp_path: Path) -> None:
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "no" in result.output.lower()

    def test_status_json(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "alpha")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["status", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["name"] == "alpha"


class TestInitCommand:
    def test_init_creates_scaffold(self, tmp_path: Path) -> None:
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["init", "gtd"])
        assert result.exit_code == 0
        assert "created" in result.output.lower()
        assert (tmp_path / "gtd" / "domain.yaml").exists()
        assert (tmp_path / "gtd" / "extracted").is_dir()
        assert (tmp_path / "gtd" / "curated").is_dir()

    def test_init_with_corpus(self, tmp_path: Path) -> None:
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(
                app,
                ["init", "gtd", "--corpus", "~/Books/gtd.md"],
            )
        assert result.exit_code == 0
        manifest = yaml.safe_load((tmp_path / "gtd" / "domain.yaml").read_text())
        assert "~/Books/gtd.md" in manifest["corpus"]

    def test_init_duplicate(self, tmp_path: Path) -> None:
        _create_domain(tmp_path, "existing")
        with patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path):
            result = runner.invoke(app, ["init", "existing"])
        assert result.exit_code == 1
        assert "already exists" in result.output.lower()
