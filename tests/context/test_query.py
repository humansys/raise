"""Tests for unified context query module."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode
from raise_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryMetadata,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)

# --- Fixtures ---


@pytest.fixture
def sample_graph() -> UnifiedGraph:
    """Create a sample graph for testing."""
    graph = UnifiedGraph()

    # Add pattern nodes
    graph.add_concept(
        ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Apply 0.5x multiplier to estimates when using full kata cycle",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-02-01",
            metadata={"sub_type": "process"},
        )
    )
    graph.add_concept(
        ConceptNode(
            id="PAT-002",
            type="pattern",
            content="Use singleton pattern with get/set/configure methods",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-15",
            metadata={"sub_type": "codebase"},
        )
    )

    # Add calibration nodes
    graph.add_concept(
        ConceptNode(
            id="CAL-001",
            type="calibration",
            content="F2.1 Concept Extraction: Size S, Est 180m, Actual 52m, Velocity 3.5x",
            source_file=".raise/rai/memory/calibration.jsonl",
            created="2026-01-31",
            metadata={"story": "F2.1", "velocity": 3.5},
        )
    )

    # Add skill nodes
    graph.add_concept(
        ConceptNode(
            id="/story-plan",
            type="skill",
            content="Decompose user stories into atomic executable tasks",
            source_file=".claude/skills/story-plan/SKILL.md",
            created="2026-01-30",
            metadata={"needs_context": ["pattern", "calibration"]},
        )
    )

    # Add session node
    graph.add_concept(
        ConceptNode(
            id="SES-001",
            type="session",
            content="E3 Implementation Plan session with epic-plan skill",
            source_file=".raise/rai/memory/sessions/index.jsonl",
            created="2026-02-01",
        )
    )

    return graph


@pytest.fixture
def engine(sample_graph: UnifiedGraph) -> UnifiedQueryEngine:
    """Create query engine with sample graph."""
    return UnifiedQueryEngine(sample_graph)


# --- Model Tests ---


class TestUnifiedQuery:
    """Tests for UnifiedQuery model."""

    def test_default_strategy(self) -> None:
        """Default strategy is keyword_search."""
        query = UnifiedQuery(query="planning")
        assert query.strategy == UnifiedQueryStrategy.KEYWORD_SEARCH

    def test_default_max_depth(self) -> None:
        """Default max_depth is 1."""
        query = UnifiedQuery(query="planning")
        assert query.max_depth == 1

    def test_types_filter(self) -> None:
        """Types filter is optional list."""
        query = UnifiedQuery(query="planning", types=["pattern", "calibration"])
        assert query.types == ["pattern", "calibration"]

    def test_max_depth_validation(self) -> None:
        """Max depth must be between 0 and 5."""
        with pytest.raises(ValueError):
            UnifiedQuery(query="test", max_depth=6)

    def test_limit_default(self) -> None:
        """Default limit is 10."""
        query = UnifiedQuery(query="test")
        assert query.limit == 10


class TestUnifiedQueryMetadata:
    """Tests for UnifiedQueryMetadata model."""

    def test_types_found_dict(self) -> None:
        """Types found is a dict of type -> count."""
        metadata = UnifiedQueryMetadata(
            query="test",
            strategy=UnifiedQueryStrategy.KEYWORD_SEARCH,
            total_concepts=5,
            token_estimate=320,
            execution_time_ms=8.5,
            types_found={"pattern": 2, "calibration": 2, "skill": 1},
        )
        assert metadata.types_found["pattern"] == 2


class TestUnifiedQueryResult:
    """Tests for UnifiedQueryResult model."""

    def test_to_json(self, sample_graph: UnifiedGraph) -> None:
        """Result can be serialized to JSON."""
        concept = sample_graph.get_concept("PAT-001")
        assert concept is not None

        result = UnifiedQueryResult(
            concepts=[concept],
            metadata=UnifiedQueryMetadata(
                query="test",
                strategy=UnifiedQueryStrategy.KEYWORD_SEARCH,
                total_concepts=1,
                token_estimate=50,
                execution_time_ms=5.0,
                types_found={"pattern": 1},
            ),
        )
        json_str = result.to_json()
        assert "PAT-001" in json_str
        assert "pattern" in json_str


# --- Engine Tests ---


class TestUnifiedQueryEngineKeywordSearch:
    """Tests for keyword search strategy."""

    def test_single_keyword_match(self, engine: UnifiedQueryEngine) -> None:
        """Single keyword matches content."""
        result = engine.query(UnifiedQuery(query="multiplier"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_multiple_keywords_match(self, engine: UnifiedQueryEngine) -> None:
        """Multiple keywords all match."""
        result = engine.query(UnifiedQuery(query="kata cycle"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_case_insensitive(self, engine: UnifiedQueryEngine) -> None:
        """Search is case-insensitive."""
        result = engine.query(UnifiedQuery(query="MULTIPLIER"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_no_match_returns_empty(self, engine: UnifiedQueryEngine) -> None:
        """No matches returns empty list."""
        result = engine.query(UnifiedQuery(query="xyznonexistent"))
        assert len(result.concepts) == 0

    def test_type_filter(self, engine: UnifiedQueryEngine) -> None:
        """Type filter limits results."""
        result = engine.query(
            UnifiedQuery(query="pattern", types=["calibration"])
        )
        # Should only return calibration nodes, not pattern nodes
        for concept in result.concepts:
            assert concept.type == "calibration"

    def test_limit_results(self, engine: UnifiedQueryEngine) -> None:
        """Limit caps result count."""
        result = engine.query(UnifiedQuery(query="a", limit=2))
        assert len(result.concepts) <= 2

    def test_relevance_scoring(self, engine: UnifiedQueryEngine) -> None:
        """More keyword hits rank higher."""
        result = engine.query(UnifiedQuery(query="kata cycle multiplier"))
        if len(result.concepts) > 0:
            # PAT-001 has all three keywords, should be first
            assert result.concepts[0].id == "PAT-001"


class TestUnifiedQueryEngineConceptLookup:
    """Tests for concept lookup strategy."""

    def test_direct_lookup(self, engine: UnifiedQueryEngine) -> None:
        """Direct ID lookup returns concept."""
        result = engine.query(
            UnifiedQuery(
                query="PAT-001",
                strategy=UnifiedQueryStrategy.CONCEPT_LOOKUP,
            )
        )
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_lookup_not_found(self, engine: UnifiedQueryEngine) -> None:
        """Non-existent ID returns empty."""
        result = engine.query(
            UnifiedQuery(
                query="NONEXISTENT-999",
                strategy=UnifiedQueryStrategy.CONCEPT_LOOKUP,
            )
        )
        assert len(result.concepts) == 0

    def test_lookup_with_neighbors(
        self, sample_graph: UnifiedGraph
    ) -> None:
        """Lookup with depth > 0 includes neighbors."""
        from raise_cli.context.models import ConceptEdge

        # Add relationship
        sample_graph.add_relationship(
            ConceptEdge(
                source="PAT-001",
                target="SES-001",
                type="learned_from",
            )
        )

        engine = UnifiedQueryEngine(sample_graph)
        result = engine.query(
            UnifiedQuery(
                query="PAT-001",
                strategy=UnifiedQueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
            )
        )
        # Should include PAT-001 and its neighbor SES-001
        ids = [c.id for c in result.concepts]
        assert "PAT-001" in ids
        assert "SES-001" in ids


class TestUnifiedQueryEngineMetadata:
    """Tests for query metadata."""

    def test_token_estimate(self, engine: UnifiedQueryEngine) -> None:
        """Token estimate is calculated."""
        result = engine.query(UnifiedQuery(query="multiplier"))
        assert result.metadata.token_estimate > 0

    def test_execution_time(self, engine: UnifiedQueryEngine) -> None:
        """Execution time is recorded."""
        result = engine.query(UnifiedQuery(query="multiplier"))
        assert result.metadata.execution_time_ms >= 0

    def test_types_found(self, engine: UnifiedQueryEngine) -> None:
        """Types found is populated."""
        result = engine.query(UnifiedQuery(query="pattern singleton"))
        if len(result.concepts) > 0:
            assert len(result.metadata.types_found) > 0


class TestUnifiedQueryEngineFromFile:
    """Tests for loading engine from file."""

    def test_from_file(self, sample_graph: UnifiedGraph, tmp_path: Path) -> None:
        """Engine can be loaded from file."""
        graph_path = tmp_path / "unified.json"
        sample_graph.save(graph_path)

        engine = UnifiedQueryEngine.from_file(graph_path)
        assert engine.graph.node_count == sample_graph.node_count

    def test_from_file_not_found(self, tmp_path: Path) -> None:
        """FileNotFoundError if file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            UnifiedQueryEngine.from_file(tmp_path / "nonexistent.json")
