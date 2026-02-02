"""Tests for context CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.models import Concept, ConceptType

runner = CliRunner()


@pytest.fixture
def sample_graph() -> ConceptGraph:
    """Create sample concept graph for testing."""
    concepts = [
        Concept(
            id="req-rf-05",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-05: Context Generation",
            lines=(1, 10),
            content="The system MUST generate context...",
            metadata={"requirement_id": "RF-05"},
        ),
        Concept(
            id="principle-governance",
            type=ConceptType.PRINCIPLE,
            file="constitution.md",
            section="§2. Governance",
            lines=(20, 30),
            content="Standards versioned in Git...",
            metadata={"principle_number": "2"},
        ),
    ]

    relationships = [
        Relationship(
            source="req-rf-05",
            target="principle-governance",
            type="governed_by",
            metadata={},
        ),
    ]

    return ConceptGraph(nodes={c.id: c for c in concepts}, edges=relationships)


class TestContextQueryCommand:
    """Tests for `raise context query` command."""

    def test_query_requires_graph(self, tmp_path: Path) -> None:
        """Test query command fails if graph not found."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["context", "query", "req-rf-05"])

            assert result.exit_code == 1
            assert "Graph file not found" in result.stdout or "Error" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_basic(self, sample_graph: ConceptGraph, tmp_path: Path) -> None:
        """Test basic query command."""
        # Create graph cache
        graph_file = tmp_path / "graph.json"
        graph_file.write_text(sample_graph.to_json())

        # Temporarily change working directory
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            result = runner.invoke(app, ["context", "query", "req-rf-05"])

            assert result.exit_code == 0
            assert "Minimum Viable Context" in result.stdout
            assert "req-rf-05" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_json_format(
        self, sample_graph: ConceptGraph, tmp_path: Path
    ) -> None:
        """Test query with JSON output."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            result = runner.invoke(app, ["context", "query", "req-rf-05", "--format", "json"])

            assert result.exit_code == 0
            assert '"concepts"' in result.stdout or "concepts" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_with_output_file(
        self, sample_graph: ConceptGraph, tmp_path: Path
    ) -> None:
        """Test query saves to output file."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            output_file = tmp_path / "context.md"
            result = runner.invoke(
                app, ["context", "query", "req-rf-05", "--output", str(output_file)]
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "Minimum Viable Context" in content
        finally:
            os.chdir(original_cwd)

    def test_query_with_strategy(
        self, sample_graph: ConceptGraph, tmp_path: Path
    ) -> None:
        """Test query with explicit strategy."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            result = runner.invoke(
                app, ["context", "query", "governance", "--strategy", "keyword_search"]
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_with_invalid_strategy(self) -> None:
        """Test query with invalid strategy."""
        result = runner.invoke(
            app, ["context", "query", "test", "--strategy", "invalid"]
        )

        # Should error before trying to load graph
        assert result.exit_code == 1

    def test_query_with_edge_types(
        self, sample_graph: ConceptGraph, tmp_path: Path
    ) -> None:
        """Test query with edge type filter."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            result = runner.invoke(
                app,
                ["context", "query", "req-rf-05", "--edge-types", "governed_by"],
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_with_type_filter(
        self, sample_graph: ConceptGraph, tmp_path: Path
    ) -> None:
        """Test query with concept type filter."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/cache").mkdir(parents=True, exist_ok=True)
            (tmp_path / ".raise/cache/graph.json").write_text(sample_graph.to_json())

            result = runner.invoke(
                app,
                [
                    "context",
                    "query",
                    "governance",
                    "--strategy",
                    "keyword_search",
                    "--type",
                    "principle",
                ],
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)
