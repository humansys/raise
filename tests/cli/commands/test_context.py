"""Tests for context CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode

runner = CliRunner()


@pytest.fixture
def unified_graph() -> UnifiedGraph:
    """Create sample unified graph for testing."""
    graph = UnifiedGraph()

    graph.add_concept(
        ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Apply 0.5x multiplier to estimates when using kata cycle",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-02-01",
            metadata={"sub_type": "process"},
        )
    )
    graph.add_concept(
        ConceptNode(
            id="CAL-001",
            type="calibration",
            content="F2.1 Concept Extraction: Size S, Est 180m, Actual 52m",
            source_file=".raise/rai/memory/calibration.jsonl",
            created="2026-01-31",
            metadata={"feature": "F2.1"},
        )
    )
    graph.add_concept(
        ConceptNode(
            id="/feature-plan",
            type="skill",
            content="Decompose user stories into atomic executable tasks",
            source_file=".claude/skills/feature-plan/SKILL.md",
            created="2026-01-30",
            metadata={"needs_context": ["pattern", "calibration"]},
        )
    )
    graph.add_concept(
        ConceptNode(
            id="req-rf-05",
            type="requirement",
            content="The system MUST generate context from governance artifacts",
            source_file="governance/projects/raise-cli/prd.md",
            created="2026-01-29",
            metadata={"requirement_id": "RF-05"},
        )
    )

    return graph


class TestContextQueryCommand:
    """Tests for `raise context query` command."""

    def test_query_requires_graph(self, tmp_path: Path) -> None:
        """Test query command fails if graph not found."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["context", "query", "planning"])

            assert result.exit_code == 4  # ArtifactNotFoundError
            assert "not found" in result.output.lower() or "error" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_query_basic(self, unified_graph: UnifiedGraph, tmp_path: Path) -> None:
        """Test basic query command."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(app, ["context", "query", "multiplier"])

            assert result.exit_code == 0
            assert "Unified Context Results" in result.stdout
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_json_format(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query with JSON output."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app, ["context", "query", "multiplier", "--format", "json"]
            )

            assert result.exit_code == 0
            assert '"concepts"' in result.stdout
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_with_types_filter(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query with types filter."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                ["context", "query", "a", "--types", "calibration"],
            )

            assert result.exit_code == 0
            # Should only return calibration nodes
            assert "Calibration" in result.stdout or "calibration" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_concept_lookup(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query with concept_lookup strategy."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                ["context", "query", "PAT-001", "--strategy", "concept_lookup"],
            )

            assert result.exit_code == 0
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_invalid_strategy(self, tmp_path: Path) -> None:
        """Test query with invalid strategy."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            UnifiedGraph().save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                ["context", "query", "test", "--strategy", "invalid_strategy"],
            )

            assert result.exit_code == 7  # ValidationError
            assert "Invalid strategy" in result.output
        finally:
            os.chdir(original_cwd)

    def test_query_no_results(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query returns no results message."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(app, ["context", "query", "xyznonexistent"])

            assert result.exit_code == 0
            assert "No concepts found" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_with_output_file(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query saves to output file."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            output_file = tmp_path / "context.md"
            result = runner.invoke(
                app, ["context", "query", "multiplier", "--output", str(output_file)]
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "Unified Context Results" in content
        finally:
            os.chdir(original_cwd)

    def test_query_with_limit(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test query respects limit option."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                ["context", "query", "a", "--limit", "1"],
            )

            assert result.exit_code == 0
            # With limit 1, should only get one concept
            assert "Concepts: 1" in result.stdout or "Concepts:** 1" in result.stdout
        finally:
            os.chdir(original_cwd)
