"""Tests for artifact CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def valid_artifact_yaml() -> dict:
    """A valid story-design artifact as a dict."""
    return {
        "artifact_type": "story-design",
        "version": 1,
        "skill": "rai-story-design",
        "created": "2026-03-03T10:00:00+00:00",
        "story": "S354.1",
        "epic": "E354",
        "content": {
            "summary": "Base artifact model and storage",
            "complexity": "simple",
            "acceptance_criteria": [
                {"id": "AC1", "description": "Model exists", "verifiable": True},
            ],
            "integration_points": [],
            "decisions": [],
        },
        "refs": {"backlog_item": "RAISE-418"},
        "metadata": {},
    }


@pytest.fixture
def project_with_artifact(tmp_path: Path, valid_artifact_yaml: dict) -> Path:
    """Create a temp project with one valid artifact."""
    artifacts_dir = tmp_path / ".raise" / "artifacts"
    artifacts_dir.mkdir(parents=True)
    path = artifacts_dir / "s354.1-design.yaml"
    path.write_text(yaml.dump(valid_artifact_yaml, default_flow_style=False))
    return tmp_path


class TestArtifactValidate:
    """Tests for rai artifact validate."""

    def test_validate_all_pass(self, project_with_artifact: Path) -> None:
        """All valid artifacts → exit 0."""
        result = runner.invoke(
            app,
            ["artifact", "validate"],
            env={"RAI_PROJECT_ROOT": str(project_with_artifact)},
        )
        assert result.exit_code == 0
        assert "s354.1-design.yaml" in result.stdout

    def test_validate_no_artifacts_dir(self, tmp_path: Path) -> None:
        """No .raise/artifacts/ → exit 0 with message."""
        result = runner.invoke(
            app, ["artifact", "validate"], env={"RAI_PROJECT_ROOT": str(tmp_path)}
        )
        assert result.exit_code == 0
        assert "No artifacts found" in result.stdout

    def test_validate_invalid_artifact(self, tmp_path: Path) -> None:
        """Invalid YAML schema → exit 1."""
        artifacts_dir = tmp_path / ".raise" / "artifacts"
        artifacts_dir.mkdir(parents=True)
        bad = artifacts_dir / "bad.yaml"
        bad.write_text(yaml.dump({"artifact_type": "story-design", "version": 1}))
        result = runner.invoke(
            app, ["artifact", "validate"], env={"RAI_PROJECT_ROOT": str(tmp_path)}
        )
        assert result.exit_code == 1
        assert "bad.yaml" in result.stdout

    def test_validate_single_file(self, project_with_artifact: Path) -> None:
        """--file flag validates a single artifact."""
        artifact_path = (
            project_with_artifact / ".raise" / "artifacts" / "s354.1-design.yaml"
        )
        result = runner.invoke(
            app,
            ["artifact", "validate", "--file", str(artifact_path)],
            env={"RAI_PROJECT_ROOT": str(project_with_artifact)},
        )
        assert result.exit_code == 0
        assert "s354.1-design.yaml" in result.stdout

    def test_validate_single_file_not_found(self, tmp_path: Path) -> None:
        """--file with nonexistent file → exit 1."""
        result = runner.invoke(
            app,
            ["artifact", "validate", "--file", str(tmp_path / "nope.yaml")],
            env={"RAI_PROJECT_ROOT": str(tmp_path)},
        )
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_validate_json_output(self, project_with_artifact: Path) -> None:
        """--format json outputs structured results."""
        result = runner.invoke(
            app,
            ["artifact", "validate", "--format", "json"],
            env={"RAI_PROJECT_ROOT": str(project_with_artifact)},
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["all_passed"] is True
        assert len(data["results"]) == 1
        assert data["results"][0]["file"] == "s354.1-design.yaml"

    def test_validate_mixed_pass_fail(self, project_with_artifact: Path) -> None:
        """Mix of valid and invalid → exit 1, both reported."""
        bad = project_with_artifact / ".raise" / "artifacts" / "bad.yaml"
        bad.write_text(yaml.dump({"artifact_type": "story-design", "version": 1}))
        result = runner.invoke(
            app,
            ["artifact", "validate"],
            env={"RAI_PROJECT_ROOT": str(project_with_artifact)},
        )
        assert result.exit_code == 1
        # Both files mentioned
        assert "s354.1-design.yaml" in result.stdout
        assert "bad.yaml" in result.stdout
