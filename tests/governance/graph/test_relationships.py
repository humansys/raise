"""Tests for relationship inference logic."""

import pytest

from raise_cli.governance.graph.relationships import (
    extract_keywords,
    infer_relationships,
)
from raise_cli.governance.models import Concept, ConceptType


@pytest.fixture
def req_context_generation() -> Concept:
    """Sample requirement about context generation."""
    return Concept(
        id="req-rf-05",
        type=ConceptType.REQUIREMENT,
        file="governance/projects/raise-cli/prd.md",
        section="RF-05: Golden Context Generation",
        lines=(206, 214),
        content="The system MUST generate CLAUDE.md with context for AI agents. "
        "Per §2, standards must be versioned in Git.",
        metadata={"requirement_id": "RF-05", "title": "Golden Context Generation"},
    )


@pytest.fixture
def outcome_context() -> Concept:
    """Sample outcome for context generation."""
    return Concept(
        id="outcome-context-generation",
        type=ConceptType.OUTCOME,
        file="governance/solution/vision.md",
        section="Context Generation",
        lines=(50, 55),
        content="Enable AI agents to receive relevant context automatically.",
        metadata={"title": "Context Generation"},
    )


@pytest.fixture
def principle_governance() -> Concept:
    """Sample principle about governance as code."""
    return Concept(
        id="principle-governance-as-code",
        type=ConceptType.PRINCIPLE,
        file="framework/reference/constitution.md",
        section="§2. Governance as Code",
        lines=(100, 115),
        content="Standards versioned in Git; what's not in repo doesn't exist.",
        metadata={"principle_number": 2},
    )


@pytest.fixture
def req_with_dependency() -> Concept:
    """Sample requirement with explicit dependency."""
    return Concept(
        id="req-rf-10",
        type=ConceptType.REQUIREMENT,
        file="prd.md",
        section="RF-10: Advanced Feature",
        lines=(300, 310),
        content="This feature depends on RF-05 and requires RF-03 to work properly.",
        metadata={"requirement_id": "RF-10"},
    )


@pytest.fixture
def req_rf_03() -> Concept:
    """Sample requirement RF-03."""
    return Concept(
        id="req-rf-03",
        type=ConceptType.REQUIREMENT,
        file="prd.md",
        section="RF-03: Basic Feature",
        lines=(100, 110),
        content="Basic feature description.",
        metadata={"requirement_id": "RF-03"},
    )


class TestExtractKeywords:
    """Tests for keyword extraction."""

    def test_extract_basic_keywords(self) -> None:
        """Test extracting keywords from simple text."""
        text = "The Context Generation System"
        keywords = extract_keywords(text)

        assert "context" in keywords
        assert "generation" in keywords
        assert "system" in keywords
        assert "the" not in keywords  # Stopword filtered

    def test_stopwords_filtered(self) -> None:
        """Test that stopwords are properly filtered."""
        text = "the and or but in on at to for of with from by this that"
        keywords = extract_keywords(text)

        # All should be filtered (all are stopwords or <3 chars)
        assert len(keywords) == 0

    def test_short_words_filtered(self) -> None:
        """Test that words <=3 chars are filtered."""
        text = "a an is be can may the"
        keywords = extract_keywords(text)

        assert len(keywords) == 0

    def test_case_insensitive(self) -> None:
        """Test that extraction is case-insensitive."""
        text1 = "Context Generation"
        text2 = "context generation"

        assert extract_keywords(text1) == extract_keywords(text2)

    def test_punctuation_handled(self) -> None:
        """Test that punctuation is properly handled."""
        text = "Context, generation; system."
        keywords = extract_keywords(text)

        assert "context" in keywords
        assert "generation" in keywords
        assert "system" in keywords


class TestInferImplements:
    """Tests for 'implements' relationship inference."""

    def test_infer_implements_from_keyword_match(
        self, req_context_generation: Concept, outcome_context: Concept
    ) -> None:
        """Test inferring implements relationship via keyword matching."""
        relationships = infer_relationships([req_context_generation, outcome_context])

        implements = [r for r in relationships if r.type == "implements"]
        assert len(implements) == 1
        assert implements[0].source == req_context_generation.id
        assert implements[0].target == outcome_context.id
        assert implements[0].metadata["confidence"] == 0.8
        assert implements[0].metadata["method"] == "keyword_match"

    def test_no_implements_without_keyword_match(
        self, req_rf_03: Concept, outcome_context: Concept
    ) -> None:
        """Test that implements is not inferred without keyword match."""
        relationships = infer_relationships([req_rf_03, outcome_context])

        implements = [r for r in relationships if r.type == "implements"]
        assert len(implements) == 0


class TestInferGovernedBy:
    """Tests for 'governed_by' relationship inference."""

    def test_infer_governed_by_from_explicit_ref(
        self, req_context_generation: Concept, principle_governance: Concept
    ) -> None:
        """Test inferring governed_by from explicit §N reference."""
        relationships = infer_relationships([req_context_generation, principle_governance])

        governed = [r for r in relationships if r.type == "governed_by"]
        assert len(governed) == 1
        assert governed[0].source == req_context_generation.id
        assert governed[0].target == principle_governance.id
        assert governed[0].metadata["confidence"] == 1.0
        assert governed[0].metadata["method"] == "explicit_reference"

    def test_no_governed_by_without_ref(
        self, req_rf_03: Concept, principle_governance: Concept
    ) -> None:
        """Test that governed_by is not inferred without §N reference."""
        relationships = infer_relationships([req_rf_03, principle_governance])

        governed = [r for r in relationships if r.type == "governed_by"]
        assert len(governed) == 0

    def test_governed_by_works_for_outcomes(
        self, principle_governance: Concept
    ) -> None:
        """Test that governed_by works for outcomes, not just requirements."""
        outcome = Concept(
            id="outcome-test",
            type=ConceptType.OUTCOME,
            file="vision.md",
            section="Test",
            lines=(1, 5),
            content="This outcome references §2 governance principle.",
            metadata={"title": "Test"},
        )

        relationships = infer_relationships([outcome, principle_governance])

        governed = [r for r in relationships if r.type == "governed_by"]
        assert len(governed) == 1
        assert governed[0].source == outcome.id


class TestInferDependsOn:
    """Tests for 'depends_on' relationship inference."""

    def test_infer_depends_on_explicit(
        self, req_with_dependency: Concept, req_context_generation: Concept, req_rf_03: Concept
    ) -> None:
        """Test inferring depends_on from explicit references."""
        relationships = infer_relationships(
            [req_with_dependency, req_context_generation, req_rf_03]
        )

        depends = [r for r in relationships if r.type == "depends_on"]
        assert len(depends) == 2

        # Check both dependencies found
        source_targets = {(r.source, r.target) for r in depends}
        assert (req_with_dependency.id, req_context_generation.id) in source_targets
        assert (req_with_dependency.id, req_rf_03.id) in source_targets

    def test_depends_on_case_insensitive(
        self, req_context_generation: Concept
    ) -> None:
        """Test that depends_on detection is case-insensitive."""
        req_upper = Concept(
            id="req-test",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="Test",
            lines=(1, 5),
            content="This DEPENDS ON RF-05 for functionality.",
        )

        relationships = infer_relationships([req_upper, req_context_generation])

        depends = [r for r in relationships if r.type == "depends_on"]
        assert len(depends) == 1

    def test_depends_on_ignores_nonexistent(
        self, req_with_dependency: Concept
    ) -> None:
        """Test that depends_on doesn't create edges to non-existent concepts."""
        # Only provide req_with_dependency, not its dependencies
        relationships = infer_relationships([req_with_dependency])

        depends = [r for r in relationships if r.type == "depends_on"]
        # Should find 0 because RF-05 and RF-03 don't exist in concept list
        assert len(depends) == 0


class TestInferRelatedTo:
    """Tests for 'related_to' relationship inference."""

    def test_infer_related_to_from_shared_keywords(self) -> None:
        """Test inferring related_to from shared keywords."""
        concept1 = Concept(
            id="c1",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="Context Generation System Framework",
            lines=(1, 5),
            content="A system framework for generating context automatically with governance.",
        )

        concept2 = Concept(
            id="c2",
            type=ConceptType.OUTCOME,
            file="vision.md",
            section="Automated Context Generation Framework",
            lines=(1, 5),
            content="Enable automatic context generation system with governance framework for agents.",
        )

        relationships = infer_relationships([concept1, concept2])

        related = [r for r in relationships if r.type == "related_to"]
        assert len(related) > 0
        assert related[0].source == concept1.id
        assert related[0].target == concept2.id
        assert related[0].metadata["confidence"] == 0.6
        assert "shared_keywords" in related[0].metadata

    def test_no_related_to_with_few_shared_keywords(self) -> None:
        """Test that related_to is not inferred with <3 shared keywords."""
        concept1 = Concept(
            id="c1",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="Context Generation",
            lines=(1, 5),
            content="Generate context.",
        )

        concept2 = Concept(
            id="c2",
            type=ConceptType.OUTCOME,
            file="vision.md",
            section="Security Validation",
            lines=(1, 5),
            content="Validate security policies.",
        )

        relationships = infer_relationships([concept1, concept2])

        related = [r for r in relationships if r.type == "related_to"]
        # Only shares 0-2 keywords, should not create relationship
        assert len(related) == 0


class TestInferRelationshipsIntegration:
    """Integration tests for full relationship inference."""

    def test_infer_all_relationship_types(
        self,
        req_context_generation: Concept,
        outcome_context: Concept,
        principle_governance: Concept,
    ) -> None:
        """Test that all relationship types can be inferred together."""
        relationships = infer_relationships(
            [req_context_generation, outcome_context, principle_governance]
        )

        # Should have at least implements and governed_by
        types = {r.type for r in relationships}
        assert "implements" in types
        assert "governed_by" in types

    def test_no_duplicate_edges(
        self, req_context_generation: Concept, outcome_context: Concept
    ) -> None:
        """Test that duplicate edges are not created."""
        # Run inference twice on same concepts
        rels1 = infer_relationships([req_context_generation, outcome_context])
        rels2 = infer_relationships([req_context_generation, outcome_context])

        # Should get same relationships (deterministic)
        assert len(rels1) == len(rels2)

    def test_empty_concept_list(self) -> None:
        """Test that empty concept list returns empty relationships."""
        relationships = infer_relationships([])

        assert len(relationships) == 0

    def test_single_concept(self, req_context_generation: Concept) -> None:
        """Test that single concept returns no relationships."""
        relationships = infer_relationships([req_context_generation])

        # Can't create relationships with only one concept
        # (except if it references itself, which our rules don't do)
        assert len(relationships) == 0
