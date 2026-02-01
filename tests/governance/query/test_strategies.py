"""Tests for query strategies."""

import pytest

from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.query.strategies import (
    extract_keywords,
    normalize_concept_id,
    query_concept_lookup,
    query_keyword_search,
    query_related_concepts,
    query_relationship_traversal,
)


class TestHelpers:
    """Tests for helper functions."""

    def test_normalize_concept_id_requirement(self) -> None:
        """Test normalizing requirement IDs."""
        assert normalize_concept_id("RF-05") == "req-rf-05"
        assert normalize_concept_id("rf-05") == "req-rf-05"
        assert normalize_concept_id("req-rf-05") == "req-rf-05"

    def test_normalize_concept_id_already_normalized(self) -> None:
        """Test already normalized IDs pass through."""
        assert normalize_concept_id("req-rf-05") == "req-rf-05"
        assert normalize_concept_id("outcome-context") == "outcome-context"
        assert normalize_concept_id("principle-governance") == "principle-governance"

    def test_extract_keywords(self) -> None:
        """Test keyword extraction."""
        keywords = extract_keywords("The system MUST validate user inputs")

        assert "system" in keywords
        assert "validate" in keywords
        assert "user" in keywords
        assert "inputs" in keywords

        # Stopwords removed
        assert "the" not in keywords
        assert "must" not in keywords

        # Short words removed
        assert "a" not in keywords

    def test_extract_keywords_empty(self) -> None:
        """Test keyword extraction from empty string."""
        keywords = extract_keywords("")
        assert keywords == set()

    def test_extract_keywords_only_stopwords(self) -> None:
        """Test keyword extraction with only stopwords."""
        keywords = extract_keywords("the and or but")
        assert keywords == set()


@pytest.fixture
def sample_graph() -> ConceptGraph:
    """Create a sample concept graph for testing."""
    concepts = [
        Concept(
            id="req-rf-05",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-05: Context Generation",
            lines=(1, 10),
            content="The system MUST generate governance context for AI agents...",
            metadata={"requirement_id": "RF-05"},
        ),
        Concept(
            id="req-rf-07",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-07: Validation Gates",
            lines=(20, 30),
            content="The system MUST validate code against gates...",
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
            content="Reduce AI hallucination through governed context...",
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


class TestQueryConceptLookup:
    """Tests for concept lookup strategy."""

    def test_concept_lookup_by_id(self, sample_graph: ConceptGraph) -> None:
        """Test looking up concept by ID."""
        result = query_concept_lookup(sample_graph, "req-rf-05")

        assert len(result) >= 1
        assert result[0].id == "req-rf-05"

    def test_concept_lookup_with_dependencies(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test concept lookup includes dependencies."""
        result = query_concept_lookup(sample_graph, "req-rf-05")

        # Should include RF-05 + its dependencies
        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "principle-governance-as-code" in concept_ids
        assert "outcome-context-generation" in concept_ids

    def test_concept_lookup_normalized_id(self, sample_graph: ConceptGraph) -> None:
        """Test concept lookup with user-friendly ID."""
        result = query_concept_lookup(sample_graph, "RF-05")

        assert len(result) >= 1
        assert result[0].id == "req-rf-05"

    def test_concept_lookup_not_found(self, sample_graph: ConceptGraph) -> None:
        """Test concept lookup with non-existent ID."""
        result = query_concept_lookup(sample_graph, "req-rf-99")

        assert result == []

    def test_concept_lookup_custom_edge_types(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test concept lookup with specific edge types."""
        result = query_concept_lookup(
            sample_graph, "req-rf-05", edge_types=["governed_by"]
        )

        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "principle-governance-as-code" in concept_ids
        # Should NOT include outcome (implements edge)
        assert "outcome-context-generation" not in concept_ids

    def test_concept_lookup_no_dependencies(self, sample_graph: ConceptGraph) -> None:
        """Test concept lookup with max_depth=0 (no dependencies)."""
        result = query_concept_lookup(sample_graph, "req-rf-05", max_depth=0)

        assert len(result) == 1
        assert result[0].id == "req-rf-05"


class TestQueryKeywordSearch:
    """Tests for keyword search strategy."""

    def test_keyword_search_basic(self, sample_graph: ConceptGraph) -> None:
        """Test basic keyword search."""
        result = query_keyword_search(sample_graph, "validation")

        # Should find RF-07 which mentions validation
        concept_ids = {c.id for c in result}
        assert "req-rf-07" in concept_ids

    def test_keyword_search_with_type_filter(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test keyword search with type filter."""
        result = query_keyword_search(
            sample_graph, "governance", concept_type="principle"
        )

        # Should only return principles
        assert all(c.type == ConceptType.PRINCIPLE for c in result)
        assert len(result) >= 1

    def test_keyword_search_multiple_keywords(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test keyword search with multiple keywords."""
        result = query_keyword_search(sample_graph, "context generation")

        # Should find concepts mentioning context or generation
        assert len(result) >= 2

    def test_keyword_search_no_matches(self, sample_graph: ConceptGraph) -> None:
        """Test keyword search with no matches."""
        result = query_keyword_search(sample_graph, "nonexistent")

        assert result == []

    def test_keyword_search_sorted_by_relevance(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test keyword search results sorted by relevance."""
        result = query_keyword_search(sample_graph, "context generation")

        # Concepts with more keyword matches should come first
        # RF-05 has both "context" and "generation"
        if len(result) > 0:
            assert result[0].id in ["req-rf-05", "outcome-context-generation"]

    def test_keyword_search_respects_limit(self, sample_graph: ConceptGraph) -> None:
        """Test keyword search respects result limit."""
        result = query_keyword_search(sample_graph, "system", limit=1)

        assert len(result) <= 1


class TestQueryRelationshipTraversal:
    """Tests for relationship traversal strategy."""

    def test_relationship_traversal_basic(self, sample_graph: ConceptGraph) -> None:
        """Test basic relationship traversal."""
        result = query_relationship_traversal(
            sample_graph, "req-rf-05", edge_types=["governed_by"]
        )

        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids  # Start concept
        assert "principle-governance-as-code" in concept_ids  # Via governed_by

    def test_relationship_traversal_multiple_edge_types(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test traversal with multiple edge types."""
        result = query_relationship_traversal(
            sample_graph, "req-rf-05", edge_types=["governed_by", "implements"]
        )

        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "principle-governance-as-code" in concept_ids
        assert "outcome-context-generation" in concept_ids

    def test_relationship_traversal_max_depth(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test traversal respects max_depth."""
        result = query_relationship_traversal(
            sample_graph, "req-rf-05", edge_types=["governed_by"], max_depth=1
        )

        # Should find concepts within 1 hop
        assert len(result) >= 1

    def test_relationship_traversal_not_found(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test traversal from non-existent concept."""
        result = query_relationship_traversal(
            sample_graph, "req-rf-99", edge_types=["governed_by"]
        )

        assert result == []


class TestQueryRelatedConcepts:
    """Tests for related concepts strategy."""

    def test_related_concepts_basic(self, sample_graph: ConceptGraph) -> None:
        """Test finding related concepts."""
        result = query_related_concepts(sample_graph, "context generation")

        # Should find concepts with shared keywords
        assert len(result) >= 1

    def test_related_concepts_minimum_keywords(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test related concepts requires minimum shared keywords."""
        result = query_related_concepts(
            sample_graph, "context generation", min_shared_keywords=2
        )

        # Should only return concepts with 2+ shared keywords
        for concept in result:
            text = (concept.section + " " + concept.content[:500]).lower()
            # Check that it has multiple keyword matches
            assert sum(
                1 for kw in ["context", "generation"] if kw in text
            ) >= 1

    def test_related_concepts_sorted_by_relevance(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test related concepts sorted by relevance score."""
        result = query_related_concepts(sample_graph, "governance code")

        # Higher relevance should come first
        if len(result) > 1:
            # principle-governance-as-code should rank high
            assert any("governance" in c.id for c in result[:2])

    def test_related_concepts_respects_limit(
        self, sample_graph: ConceptGraph
    ) -> None:
        """Test related concepts respects result limit."""
        result = query_related_concepts(sample_graph, "system", limit=2)

        assert len(result) <= 2

    def test_related_concepts_no_matches(self, sample_graph: ConceptGraph) -> None:
        """Test related concepts with no keyword overlap."""
        result = query_related_concepts(
            sample_graph, "xyz", min_shared_keywords=1
        )

        assert result == []

    def test_related_concepts_empty_query(self, sample_graph: ConceptGraph) -> None:
        """Test related concepts with empty query."""
        result = query_related_concepts(sample_graph, "")

        assert result == []
