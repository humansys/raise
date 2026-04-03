"""Tests for rai learn CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from raise_cli.cli.error_handler import set_error_console
from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_error_console() -> Any:
    """Reset error console singleton so cli_error writes to CliRunner's stream."""
    set_error_console(None)
    yield
    set_error_console(None)


def _all_output(result: Any) -> str:
    """Get all output from CliRunner result (stdout + stderr if available)."""
    parts = [result.output or ""]
    if hasattr(result, "stderr") and result.stderr:
        parts.append(result.stderr)
    return "\n".join(parts).lower()


class TestLearnWrite:
    """Tests for rai learn write command."""

    def _valid_record_data(self) -> dict[str, object]:
        return {
            "skill": "rai-story-implement",
            "work_id": "S1136.2",
            "version": "1.0.0",
            "timestamp": "2026-04-01T10:00:00Z",
            "primed_patterns": ["PAT-E-589"],
            "tier1_queries": 3,
            "tier1_results": 5,
            "jit_queries": 1,
            "pattern_votes": {
                "PAT-E-589": {"vote": 1, "why": "Used seam pattern for config"},
            },
            "gaps": ["No pattern for CLI testing"],
            "artifacts": ["packages/raise-cli/src/raise_cli/cli/commands/learn.py"],
        }

    def test_happy_path_writes_record(self, tmp_path: Path) -> None:
        """Valid YAML file validates and writes to correct path."""
        yaml_file = tmp_path / "record.yaml"
        yaml_file.write_text(
            yaml.safe_dump(self._valid_record_data(), default_flow_style=False),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 0, f"Unexpected output: {result.output}"
        expected_path = (
            tmp_path
            / ".raise"
            / "rai"
            / "learnings"
            / "rai-story-implement"
            / "S1136.2"
            / "record.yaml"
        )
        assert expected_path.exists()
        assert "rai-story-implement" in result.output
        assert "S1136.2" in result.output

    def test_validation_error_exits_7(self, tmp_path: Path) -> None:
        """Invalid YAML (missing required field) exits with code 7."""
        bad_data = {"skill": "test"}  # missing work_id, version, timestamp
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text(
            yaml.safe_dump(bad_data, default_flow_style=False),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 7
        combined = _all_output(result)
        assert "validation" in combined or "error" in combined

    def test_missing_file_exits_1(self, tmp_path: Path) -> None:
        """Non-existent YAML file exits with code 1."""
        result = runner.invoke(
            app,
            ["learn", "write", str(tmp_path / "nope.yaml"), "--project", str(tmp_path)],
        )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "not found" in combined or "exist" in combined

    def test_malformed_yaml_exits_1(self, tmp_path: Path) -> None:
        """Malformed YAML (not valid YAML syntax) gives clear error."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("{{invalid yaml: [", encoding="utf-8")

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "yaml" in combined or "parse" in combined
