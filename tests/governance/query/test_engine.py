"""Tests for MVC query engine."""

from pathlib import Path

import pytest

from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.query.engine import ContextQueryEngine
from raise_cli.governance.query.models import ContextQuery, QueryStrategy


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
            content="The system MUST generate governance context for AI agents to reduce hallucination...",
            metadata={"requirement_id": "RF-05"},
        ),
        Concept(
            id="req-rf-07",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-07: Validation Gates",
            lines=(20, 30),
            content="The system MUST validate code against quality gates...",
            metadata={"requirement_id": "RF-07"},
        ),
        Concept(
            id="principle-governance-as-code",
            type=ConceptType.PRINCIPLE,
            file="constitution.md",
            section="§2. Governance as Code",
            lines=(50, 70),
            content="Standards versioned in Git; what's not in repo doesn't exist...",
            metadata={"principle_number": "2"},
        ),
        Concept(
            id="outcome-context-generation",
            type=ConceptType.OUTCOME,
            file="vision.md",
            section="Context Generation Outcome",
            lines=(100, 110),
            content="Reduce AI hallucination by 80% through governed context generation...",
            metadata={"outcome_id": "O1"},
        ),
    ]

    relationships = [
        Relationship(
            source="req-rf-05",
            target="principle-governance-as-code",
            type="governed_by",
            metadata={"confidence": 1.0},
        ),
        Relationship(
            source="req-rf-05",
            target="outcome-context-generation",
            type="implements",
            metadata={"confidence": 0.9},
        ),
    ]

    return ConceptGraph(
        nodes={c.id: c for c in concepts},
        edges=relationships,
        metadata={"build_time": "2026-01-31"},
    )


@pytest.fixture
def engine(sample_graph: ConceptGraph) -> ContextQueryEngine:
    """Create query engine with sample graph."""
    return ContextQueryEngine(sample_graph)


class TestContextQueryEngine:
    """Tests for ContextQueryEngine class."""

    def test_engine_initialization(self, sample_graph: ConceptGraph) -> None:
        """Test creating query engine."""
        engine = ContextQueryEngine(sample_graph)

        assert engine.graph == sample_graph

    def test_from_cache_not_found(self) -> None:
        """Test loading from non-existent cache file."""
        with pytest.raises(FileNotFoundError):
            ContextQueryEngine.from_cache(Path("nonexistent.json"))

    def test_from_cache_success(self, sample_graph: ConceptGraph, tmp_path: Path) -> None:
        """Test loading from cached graph file."""
        cache_file = tmp_path / "graph.json"
        cache_file.write_text(sample_graph.to_json())

        engine = ContextQueryEngine.from_cache(cache_file)

        assert len(engine.graph.nodes) == len(sample_graph.nodes)


class TestQueryConceptLookup:
    """Tests for CONCEPT_LOOKUP strategy."""

    def test_query_concept_lookup(self, engine: ContextQueryEngine) -> None:
        """Test concept lookup query."""
        query = ContextQuery(query="req-rf-05", strategy=QueryStrategy.CONCEPT_LOOKUP)
        result = engine.query(query)

        # Should find RF-05 + dependencies
        assert len(result.concepts) >= 1
        concept_ids = {c.id for c in result.concepts}
        assert "req-rf-05" in concept_ids

    def test_query_concept_lookup_includes_dependencies(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test concept lookup includes dependencies."""
        query = ContextQuery(query="req-rf-05")
        result = engine.query(query)

        concept_ids = {c.id for c in result.concepts}
        assert "principle-governance-as-code" in concept_ids
        assert "outcome-context-generation" in concept_ids

    def test_query_concept_lookup_metadata(self, engine: ContextQueryEngine) -> None:
        """Test concept lookup returns correct metadata."""
        query = ContextQuery(query="req-rf-05")
        result = engine.query(query)

        assert result.metadata.query == "req-rf-05"
        assert result.metadata.strategy == QueryStrategy.CONCEPT_LOOKUP
        assert result.metadata.total_concepts == len(result.concepts)
        assert result.metadata.token_estimate > 0
        assert result.metadata.execution_time_ms > 0

    def test_query_concept_lookup_with_edge_filter(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test concept lookup with edge type filter."""
        query = ContextQuery(
            query="req-rf-05",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            filters={"edge_types": ["governed_by"]},
        )
        result = engine.query(query)

        concept_ids = {c.id for c in result.concepts}
        assert "principle-governance-as-code" in concept_ids
        # Should NOT include outcome (implements edge)
        assert "outcome-context-generation" not in concept_ids


class TestQueryKeywordSearch:
    """Tests for KEYWORD_SEARCH strategy."""

    def test_query_keyword_search(self, engine: ContextQueryEngine) -> None:
        """Test keyword search query."""
        query = ContextQuery(query="validation", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        # Should find RF-07 which mentions validation
        concept_ids = {c.id for c in result.concepts}
        assert "req-rf-07" in concept_ids

    def test_query_keyword_search_with_type_filter(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test keyword search with type filter."""
        query = ContextQuery(
            query="governance",
            strategy=QueryStrategy.KEYWORD_SEARCH,
            filters={"type": "principle"},
        )
        result = engine.query(query)

        # Should only return principles
        assert all(c.type == ConceptType.PRINCIPLE for c in result.concepts)

    def test_query_keyword_search_metadata(self, engine: ContextQueryEngine) -> None:
        """Test keyword search metadata."""
        query = ContextQuery(query="context", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        assert result.metadata.strategy == QueryStrategy.KEYWORD_SEARCH
        assert result.metadata.token_estimate > 0


class TestQueryRelationshipTraversal:
    """Tests for RELATIONSHIP_TRAVERSAL strategy."""

    def test_query_relationship_traversal(self, engine: ContextQueryEngine) -> None:
        """Test relationship traversal query."""
        query = ContextQuery(
            query="req-rf-05",
            strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
            filters={"edge_types": ["governed_by"]},
        )
        result = engine.query(query)

        concept_ids = {c.id for c in result.concepts}
        assert "req-rf-05" in concept_ids
        assert "principle-governance-as-code" in concept_ids

    def test_query_relationship_traversal_paths(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test relationship traversal traces paths."""
        query = ContextQuery(
            query="req-rf-05",
            strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
            filters={"edge_types": ["governed_by"]},
        )
        result = engine.query(query)

        # Should include relationship paths
        assert len(result.metadata.paths) > 0
        # Should have path from req-rf-05 to principle
        paths_flat = [node for path in result.metadata.paths for node in path]
        assert "req-rf-05" in paths_flat


class TestQueryRelatedConcepts:
    """Tests for RELATED_CONCEPTS strategy."""

    def test_query_related_concepts(self, engine: ContextQueryEngine) -> None:
        """Test related concepts query."""
        query = ContextQuery(
            query="context generation", strategy=QueryStrategy.RELATED_CONCEPTS
        )
        result = engine.query(query)

        # Should find concepts with shared keywords
        assert len(result.concepts) >= 1

    def test_query_related_concepts_metadata(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test related concepts metadata."""
        query = ContextQuery(query="context", strategy=QueryStrategy.RELATED_CONCEPTS)
        result = engine.query(query)

        assert result.metadata.strategy == QueryStrategy.RELATED_CONCEPTS


class TestQueryMetadata:
    """Tests for metadata calculation."""

    def test_token_estimation(self, engine: ContextQueryEngine) -> None:
        """Test token estimation in results."""
        query = ContextQuery(query="req-rf-05")
        result = engine.query(query)

        # Token estimate should be reasonable
        assert result.metadata.token_estimate > 0
        # Should be much less than manual file loading (~6000 tokens)
        assert result.metadata.token_estimate < 2000

    def test_execution_time_tracked(self, engine: ContextQueryEngine) -> None:
        """Test execution time is tracked."""
        query = ContextQuery(query="req-rf-05")
        result = engine.query(query)

        assert result.metadata.execution_time_ms > 0
        # Should be fast (<100ms for small graph)
        assert result.metadata.execution_time_ms < 1000

    def test_traversal_depth_calculated(self, engine: ContextQueryEngine) -> None:
        """Test traversal depth is calculated."""
        query = ContextQuery(query="req-rf-05", max_depth=1)
        result = engine.query(query)

        # Should report actual depth
        assert result.metadata.traversal_depth >= 0
        assert result.metadata.traversal_depth <= query.max_depth

    def test_paths_traced_for_lookup(self, engine: ContextQueryEngine) -> None:
        """Test paths are traced for concept lookup."""
        query = ContextQuery(query="req-rf-05", strategy=QueryStrategy.CONCEPT_LOOKUP)
        result = engine.query(query)

        # Should have relationship paths
        assert len(result.metadata.paths) > 0

    def test_paths_not_traced_for_keyword_search(
        self, engine: ContextQueryEngine
    ) -> None:
        """Test paths are not traced for keyword search."""
        query = ContextQuery(query="validation", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        # Should not trace paths for keyword search
        assert len(result.metadata.paths) == 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_query_nonexistent_concept(self, engine: ContextQueryEngine) -> None:
        """Test querying non-existent concept."""
        query = ContextQuery(query="req-rf-99")
        result = engine.query(query)

        assert len(result.concepts) == 0
        assert result.metadata.total_concepts == 0

    def test_query_empty_string(self, engine: ContextQueryEngine) -> None:
        """Test querying with empty string."""
        query = ContextQuery(query="", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        # Should return no results
        assert len(result.concepts) == 0

    def test_query_with_max_depth_zero(self, engine: ContextQueryEngine) -> None:
        """Test query with max_depth=0."""
        query = ContextQuery(query="req-rf-05", max_depth=0)
        result = engine.query(query)

        # Should only return the query concept
        assert len(result.concepts) == 1
        assert result.concepts[0].id == "req-rf-05"
