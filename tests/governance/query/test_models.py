"""Tests for query models."""

from pathlib import Path

import pytest

from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.query.models import (
    ContextMetadata,
    ContextQuery,
    ContextResult,
    QueryStrategy,
)


class TestQueryStrategy:
    """Tests for QueryStrategy enum."""

    def test_query_strategy_values(self) -> None:
        """Test QueryStrategy enum values."""
        assert QueryStrategy.CONCEPT_LOOKUP == "concept_lookup"
        assert QueryStrategy.KEYWORD_SEARCH == "keyword_search"
        assert QueryStrategy.RELATIONSHIP_TRAVERSAL == "relationship_traversal"
        assert QueryStrategy.RELATED_CONCEPTS == "related_concepts"


class TestContextQuery:
    """Tests for ContextQuery model."""

    def test_mvc_query_creation(self) -> None:
        """Test creating ContextQuery with required fields."""
        query = ContextQuery(query="req-rf-05")

        assert query.query == "req-rf-05"
        assert query.strategy == QueryStrategy.CONCEPT_LOOKUP
        assert query.max_depth == 1
        assert query.filters == {}

    def test_mvc_query_with_strategy(self) -> None:
        """Test ContextQuery with explicit strategy."""
        query = ContextQuery(
            query="validation", strategy=QueryStrategy.KEYWORD_SEARCH
        )

        assert query.query == "validation"
        assert query.strategy == QueryStrategy.KEYWORD_SEARCH

    def test_mvc_query_with_filters(self) -> None:
        """Test ContextQuery with filters."""
        query = ContextQuery(
            query="req-rf-05",
            strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
            filters={"edge_types": ["governed_by"]},
            max_depth=2,
        )

        assert query.filters == {"edge_types": ["governed_by"]}
        assert query.max_depth == 2

    def test_mvc_query_validates_max_depth(self) -> None:
        """Test ContextQuery validates max_depth range."""
        # Valid depth
        query = ContextQuery(query="test", max_depth=3)
        assert query.max_depth == 3

        # Invalid depth (too high)
        with pytest.raises(ValueError):
            ContextQuery(query="test", max_depth=10)

        # Invalid depth (negative)
        with pytest.raises(ValueError):
            ContextQuery(query="test", max_depth=-1)

    def test_mvc_query_serialization(self) -> None:
        """Test ContextQuery JSON serialization."""
        query = ContextQuery(
            query="req-rf-05",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            max_depth=2,
            filters={"type": "requirement"},
        )

        # Serialize
        json_str = query.model_dump_json()
        assert "req-rf-05" in json_str
        assert "concept_lookup" in json_str

        # Deserialize
        loaded = ContextQuery.model_validate_json(json_str)
        assert loaded.query == query.query
        assert loaded.strategy == query.strategy
        assert loaded.max_depth == query.max_depth
        assert loaded.filters == query.filters


class TestContextMetadata:
    """Tests for ContextMetadata model."""

    def test_mvc_metadata_creation(self) -> None:
        """Test creating ContextMetadata."""
        metadata = ContextMetadata(
            query="req-rf-05",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            total_concepts=3,
            token_estimate=350,
            traversal_depth=1,
            paths=[["req-rf-05", "principle-governance-as-code"]],
            execution_time_ms=12.5,
        )

        assert metadata.query == "req-rf-05"
        assert metadata.strategy == QueryStrategy.CONCEPT_LOOKUP
        assert metadata.total_concepts == 3
        assert metadata.token_estimate == 350
        assert metadata.traversal_depth == 1
        assert len(metadata.paths) == 1
        assert metadata.execution_time_ms == 12.5

    def test_mvc_metadata_empty_paths(self) -> None:
        """Test ContextMetadata with empty paths."""
        metadata = ContextMetadata(
            query="req-rf-05",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            total_concepts=1,
            token_estimate=100,
            traversal_depth=0,
            execution_time_ms=5.0,
        )

        assert metadata.paths == []


class TestContextResult:
    """Tests for ContextResult model."""

    @pytest.fixture
    def sample_concept(self) -> Concept:
        """Create sample concept for testing."""
        return Concept(
            id="req-rf-05",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-05: Golden Context",
            lines=(1, 10),
            content="The system MUST generate context...",
            metadata={"requirement_id": "RF-05"},
        )

    @pytest.fixture
    def sample_metadata(self) -> ContextMetadata:
        """Create sample metadata for testing."""
        return ContextMetadata(
            query="req-rf-05",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            total_concepts=1,
            token_estimate=100,
            traversal_depth=0,
            paths=[],
            execution_time_ms=5.0,
        )

    def test_mvc_result_creation(
        self, sample_concept: Concept, sample_metadata: ContextMetadata
    ) -> None:
        """Test creating ContextResult."""
        result = ContextResult(concepts=[sample_concept], metadata=sample_metadata)

        assert len(result.concepts) == 1
        assert result.concepts[0].id == "req-rf-05"
        assert result.metadata.query == "req-rf-05"

    def test_mvc_result_empty_concepts(self, sample_metadata: ContextMetadata) -> None:
        """Test ContextResult with no concepts."""
        result = ContextResult(concepts=[], metadata=sample_metadata)

        assert len(result.concepts) == 0
        assert result.metadata.total_concepts == 1  # metadata can differ

    def test_mvc_result_to_json(
        self, sample_concept: Concept, sample_metadata: ContextMetadata
    ) -> None:
        """Test ContextResult JSON serialization."""
        result = ContextResult(concepts=[sample_concept], metadata=sample_metadata)

        json_str = result.to_json()

        assert "concepts" in json_str
        assert "metadata" in json_str
        assert "req-rf-05" in json_str
        assert "concept_lookup" in json_str

    def test_mvc_result_from_json(
        self, sample_concept: Concept, sample_metadata: ContextMetadata
    ) -> None:
        """Test ContextResult JSON deserialization."""
        result = ContextResult(concepts=[sample_concept], metadata=sample_metadata)

        # Serialize and deserialize
        json_str = result.to_json()
        loaded = ContextResult.from_json(json_str)

        assert len(loaded.concepts) == len(result.concepts)
        assert loaded.concepts[0].id == result.concepts[0].id
        assert loaded.metadata.query == result.metadata.query
        assert loaded.metadata.strategy == result.metadata.strategy

    def test_mvc_result_to_file_json(
        self, sample_concept: Concept, sample_metadata: ContextMetadata, tmp_path: Path
    ) -> None:
        """Test saving ContextResult to JSON file."""
        result = ContextResult(concepts=[sample_concept], metadata=sample_metadata)
        output_file = tmp_path / "result.json"

        result.to_file(output_file, format="json")

        assert output_file.exists()
        content = output_file.read_text()
        assert "concepts" in content
        assert "req-rf-05" in content

    def test_mvc_result_to_file_markdown(
        self, sample_concept: Concept, sample_metadata: ContextMetadata, tmp_path: Path
    ) -> None:
        """Test saving ContextResult to markdown file."""
        result = ContextResult(concepts=[sample_concept], metadata=sample_metadata)
        output_file = tmp_path / "result.md"

        result.to_file(output_file, format="markdown")

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Minimum Viable Context" in content
        assert "req-rf-05" in content
