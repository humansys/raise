"""Tests for context CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode
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


@pytest.fixture
def unified_graph() -> UnifiedGraph:
    """Create sample unified graph for testing."""
    graph = UnifiedGraph()

    graph.add_concept(
        ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Apply 0.5x multiplier to estimates when using kata cycle",
            source_file=".rai/memory/patterns.jsonl",
            created="2026-02-01",
            metadata={"sub_type": "process"},
        )
    )
    graph.add_concept(
        ConceptNode(
            id="CAL-001",
            type="calibration",
            content="F2.1 Concept Extraction: Size S, Est 180m, Actual 52m",
            source_file=".rai/memory/calibration.jsonl",
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

    return graph


class TestUnifiedContextQuery:
    """Tests for `raise context query --unified` command."""

    def test_unified_query_requires_graph(self, tmp_path: Path) -> None:
        """Test unified query fails if graph not found."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app, ["context", "query", "planning", "--unified"]
            )

            assert result.exit_code == 1
            assert "Graph file not found" in result.stdout or "Error" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_basic(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test basic unified query command."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app, ["context", "query", "multiplier", "--unified"]
            )

            assert result.exit_code == 0
            assert "Unified Context Results" in result.stdout
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_json_format(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test unified query with JSON output."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app, ["context", "query", "multiplier", "--unified", "--format", "json"]
            )

            assert result.exit_code == 0
            assert '"concepts"' in result.stdout
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_with_types_filter(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test unified query with types filter."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                ["context", "query", "a", "--unified", "--types", "calibration"],
            )

            assert result.exit_code == 0
            # Should only return calibration nodes
            assert "Calibration" in result.stdout or "calibration" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_concept_lookup(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test unified query with concept_lookup strategy."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                [
                    "context",
                    "query",
                    "PAT-001",
                    "--unified",
                    "--strategy",
                    "concept_lookup",
                ],
            )

            assert result.exit_code == 0
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_invalid_strategy(self, tmp_path: Path) -> None:
        """Test unified query with invalid strategy."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            # Create empty graph file
            UnifiedGraph().save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app,
                [
                    "context",
                    "query",
                    "test",
                    "--unified",
                    "--strategy",
                    "invalid_strategy",
                ],
            )

            assert result.exit_code == 1
            assert "Invalid strategy" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_unified_query_no_results(
        self, unified_graph: UnifiedGraph, tmp_path: Path
    ) -> None:
        """Test unified query returns no results message."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".raise/graph").mkdir(parents=True, exist_ok=True)
            unified_graph.save(tmp_path / ".raise/graph/unified.json")

            result = runner.invoke(
                app, ["context", "query", "xyznonexistent", "--unified"]
            )

            assert result.exit_code == 0
            assert "No concepts found" in result.stdout
        finally:
            os.chdir(original_cwd)
