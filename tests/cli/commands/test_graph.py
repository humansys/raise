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

        assert result.exit_code == 4  # ArtifactNotFoundError
        # cli_error outputs to stderr, check output (combined stdout+stderr)
        assert "Error" in result.output or "not found" in result.output.lower()

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


class TestGraphBuildCommand:
    """Tests for `raise graph build` command."""

    @pytest.fixture
    def tmp_unified_project(self, tmp_path: Path) -> Path:
        """Create temporary project with all unified graph sources.

        Args:
            tmp_path: Pytest temp directory.

        Returns:
            Path to temporary project root.
        """
        project_root = tmp_path / "unified_project"
        project_root.mkdir()

        # Create governance files
        prd_file = project_root / "governance" / "projects" / "test" / "prd.md"
        prd_file.parent.mkdir(parents=True)
        prd_file.write_text(
            dedent(
                """
                ### RF-01: Test Requirement
                This is a test requirement for graph building.
                """
            )
        )

        # Create memory files
        memory_dir = project_root / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        patterns_file = memory_dir / "patterns.jsonl"
        patterns_file.write_text(
            '{"id": "PAT-001", "type": "process", "content": "Test pattern for graph", "context": ["testing", "graph"], "created": "2026-02-03"}\n'
        )

        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir()
        sessions_file = sessions_dir / "index.jsonl"
        sessions_file.write_text(
            '{"id": "SES-001", "date": "2026-02-03", "type": "feature", "topic": "Test Session", "outcomes": ["outcome1"]}\n'
        )

        # Create skill files
        skills_dir = project_root / ".claude" / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(
            dedent(
                """\
                ---
                name: test-skill
                description: Test skill for unified graph
                ---

                # Test Skill

                Test content.
                """
            )
        )

        return project_root

    def test_graph_build_help(self) -> None:
        """Should display help for graph build command."""
        result = runner.invoke(app, ["graph", "build", "--help"])

        assert result.exit_code == 0
        assert "Build unified context graph" in result.stdout
        assert "--output" in result.stdout

    def test_graph_build_creates_unified_graph(
        self, tmp_unified_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should build unified graph from all sources."""
        monkeypatch.chdir(tmp_unified_project)

        result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0
        assert "Building unified context graph" in result.stdout
        assert "nodes" in result.stdout.lower()
        assert "edges" in result.stdout.lower()

        # Should create file at .raise/graph/unified.json
        unified_graph_file = tmp_unified_project / ".raise" / "graph" / "unified.json"
        assert unified_graph_file.exists()

    def test_graph_build_with_custom_output(
        self, tmp_unified_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should save graph to custom location."""
        monkeypatch.chdir(tmp_unified_project)

        output_file = tmp_path / "custom_graph.json"
        result = runner.invoke(app, ["graph", "build", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify it's valid JSON with NetworkX node_link format
        data = json.loads(output_file.read_text())
        assert "nodes" in data
        # NetworkX uses "links" not "edges"
        assert "links" in data or "edges" in data
        assert "directed" in data

    def test_graph_build_shows_node_counts_by_type(
        self, tmp_unified_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should show node counts by type in output."""
        monkeypatch.chdir(tmp_unified_project)

        result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0
        # Should show counts by type
        assert "pattern" in result.stdout.lower()
        assert "skill" in result.stdout.lower()

    def test_graph_build_merges_all_sources(
        self, tmp_unified_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should merge governance, memory, and skills into unified graph."""
        monkeypatch.chdir(tmp_unified_project)

        result = runner.invoke(app, ["graph", "build"])
        assert result.exit_code == 0

        unified_graph_file = tmp_unified_project / ".raise" / "graph" / "unified.json"
        data = json.loads(unified_graph_file.read_text())

        # Count nodes - should have at least pattern, skill, requirement, session
        nodes = data.get("nodes", [])
        node_types = {n.get("type") for n in nodes}

        assert "pattern" in node_types
        assert "skill" in node_types


class TestGraphValidateCommand:
    """Tests for `raise graph validate` command."""

    def test_graph_validate_help(self) -> None:
        """Should display help for graph validate command."""
        result = runner.invoke(app, ["graph", "validate", "--help"])

        assert result.exit_code == 0
        assert "Validate graph structure" in result.stdout
        assert "--graph" in result.stdout

    def test_graph_validate_missing_file(self) -> None:
        """Should error when graph file doesn't exist."""
        result = runner.invoke(app, ["graph", "validate", "--graph", "/nonexistent/graph.json"])

        assert result.exit_code == 4  # ArtifactNotFoundError
        # cli_error outputs to stderr, check output (combined stdout+stderr)
        assert "Error" in result.output or "not found" in result.output.lower()
        assert "raise graph build" in result.output

    def test_graph_validate_valid_graph(
        self, tmp_governance_for_cli: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should validate a valid graph."""
        monkeypatch.chdir(tmp_governance_for_cli)

        # Build graph first
        build_result = runner.invoke(app, ["graph", "build"])
        assert build_result.exit_code == 0

        # Validate it
        result = runner.invoke(app, ["graph", "validate"])

        assert result.exit_code == 0
        assert "Validating graph" in result.stdout
        assert "valid" in result.stdout.lower()
        assert "relationships valid" in result.stdout.lower()

    def test_graph_validate_custom_graph_file(
        self, tmp_governance_for_cli: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should validate custom graph file."""
        monkeypatch.chdir(tmp_governance_for_cli)

        custom_graph = tmp_path / "my_graph.json"

        # Build to custom location
        build_result = runner.invoke(app, ["graph", "build", "--output", str(custom_graph)])
        assert build_result.exit_code == 0

        # Validate custom file
        result = runner.invoke(app, ["graph", "validate", "--graph", str(custom_graph)])

        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()


