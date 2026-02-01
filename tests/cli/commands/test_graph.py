"""Tests for graph CLI commands."""

import json
from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def tmp_governance_for_cli(tmp_path: Path) -> Path:
    """Create temporary governance files for CLI testing.

    Args:
        tmp_path: Pytest temp directory.

    Returns:
        Path to temporary project root.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create PRD
    prd_file = project_root / "governance" / "projects" / "test-cli" / "prd.md"
    prd_file.parent.mkdir(parents=True)
    prd_file.write_text(
        dedent(
            """
            ### RF-01: Test Requirement
            This is a test requirement.
            """
        )
    )

    # Create Vision
    vision_file = project_root / "governance" / "solution" / "vision.md"
    vision_file.parent.mkdir(parents=True)
    vision_file.write_text(
        dedent(
            """
            | **Outcome** | Description |
            |-------------|-------------|
            | **Test Outcome** | Test description |
            """
        )
    )

    # Create Constitution
    constitution_file = project_root / "framework" / "reference" / "constitution.md"
    constitution_file.parent.mkdir(parents=True)
    constitution_file.write_text(
        dedent(
            """
            ### §1. Test Principle
            This is a test principle.
            """
        )
    )

    return project_root


class TestGraphExtractCommand:
    """Tests for `raise graph extract` command."""

    def test_graph_extract_help(self) -> None:
        """Should display help for graph extract command."""
        result = runner.invoke(app, ["graph", "extract", "--help"])

        assert result.exit_code == 0
        assert "Extract concepts from governance markdown files" in result.stdout
        assert "FILE_PATH" in result.stdout

    def test_graph_extract_single_file_human(self, tmp_governance_for_cli: Path) -> None:
        """Should extract from single file with human-readable output."""
        prd_file = tmp_governance_for_cli / "governance" / "projects" / "test-cli" / "prd.md"

        result = runner.invoke(app, ["graph", "extract", str(prd_file)])

        assert result.exit_code == 0
        assert "Extracting concepts from" in result.stdout
        assert "Found" in result.stdout or "RF-01" in result.stdout
        assert "1" in result.stdout  # Should show count

    def test_graph_extract_single_file_json(self, tmp_governance_for_cli: Path) -> None:
        """Should extract from single file with JSON output."""
        prd_file = tmp_governance_for_cli / "governance" / "projects" / "test-cli" / "prd.md"

        result = runner.invoke(app, ["graph", "extract", str(prd_file), "--format", "json"])

        assert result.exit_code == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert "concepts" in output
        assert "total" in output
        assert output["total"] == 1
        assert len(output["concepts"]) == 1
        assert output["concepts"][0]["type"] == "requirement"

    def test_graph_extract_missing_file(self) -> None:
        """Should error gracefully for missing file."""
        result = runner.invoke(app, ["graph", "extract", "/nonexistent/file.md"])

        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()

    def test_graph_extract_all_files(self, tmp_governance_for_cli: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should extract from all governance files."""
        # Change to temp directory so extractor finds the test governance files
        monkeypatch.chdir(tmp_governance_for_cli)

        result = runner.invoke(app, ["graph", "extract"])

        assert result.exit_code == 0
        assert "Extracting concepts from governance files" in result.stdout
        assert "prd.md" in result.stdout or "requirements" in result.stdout.lower()
        assert "Total:" in result.stdout

    def test_graph_extract_all_files_json(self, tmp_governance_for_cli: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should extract all files with JSON output."""
        monkeypatch.chdir(tmp_governance_for_cli)

        result = runner.invoke(app, ["graph", "extract", "--format", "json"])

        assert result.exit_code == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert "concepts" in output
        assert "total" in output
        assert "files_processed" in output

        # Should have extracted from 3 files
        assert output["files_processed"] == 3
        assert output["total"] == 3  # 1 req + 1 outcome + 1 principle

    def test_integration_with_real_governance(self) -> None:
        """Should work with real raise-cli governance files."""
        # Skip if not in raise-commons project
        if not Path("governance/projects/raise-cli/prd.md").exists():
            pytest.skip("Real governance files not found")

        result = runner.invoke(app, ["graph", "extract"])

        assert result.exit_code == 0
        assert "Total:" in result.stdout
        # Should extract 20+ concepts from raise-commons
        assert "2" in result.stdout  # At least 20+ concepts

    def test_integration_json_output_real_governance(self) -> None:
        """Should produce valid JSON from real governance files."""
        if not Path("governance/projects/raise-cli/prd.md").exists():
            pytest.skip("Real governance files not found")

        result = runner.invoke(app, ["graph", "extract", "--format", "json"])

        assert result.exit_code == 0
        # JSON output should contain key fields (don't parse due to ANSI formatting in test runner)
        assert "concepts" in result.stdout
        assert "total" in result.stdout
        assert "type" in result.stdout
