"""Tests for concept_to_node conversion utility."""

from __future__ import annotations

import pytest

from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node


class TestConceptToNode:
    """Tests for concept_to_node conversion."""

    def test_basic_conversion(self) -> None:
        """Given a Concept, returns GraphNode with mapped fields."""
        concept = Concept(
            id="req-rf-01",
            type=ConceptType.REQUIREMENT,
            file="governance/prd.md",
            section="RF-01: Feature",
            lines=(10, 20),
            content="The system MUST do X",
            metadata={"requirement_id": "RF-01"},
        )

        node = concept_to_node(concept)

        assert node.id == "req-rf-01"
        assert node.type == "requirement"
        assert node.content == "The system MUST do X"
        assert node.source_file == "governance/prd.md"
        assert node.metadata["requirement_id"] == "RF-01"

    def test_preserves_section_and_lines(self) -> None:
        """Section and lines are stored in metadata to avoid silent data loss."""
        concept = Concept(
            id="principle-1",
            type=ConceptType.PRINCIPLE,
            file="framework/reference/constitution.md",
            section="§1: Honesty",
            lines=(5, 15),
            content="Honesty over agreement",
        )

        node = concept_to_node(concept)

        assert node.metadata["section"] == "§1: Honesty"
        assert node.metadata["lines"] == (5, 15)

    @pytest.mark.parametrize(
        ("concept_type", "expected_node_type"),
        [
            (ConceptType.REQUIREMENT, "requirement"),
            (ConceptType.OUTCOME, "outcome"),
            (ConceptType.PRINCIPLE, "principle"),
            (ConceptType.PROJECT, "project"),
            (ConceptType.EPIC, "epic"),
            (ConceptType.STORY, "story"),
            (ConceptType.DECISION, "decision"),
            (ConceptType.GUARDRAIL, "guardrail"),
            (ConceptType.TERM, "term"),
            (ConceptType.RELEASE, "release"),
        ],
    )
    def test_preserves_all_types(
        self, concept_type: ConceptType, expected_node_type: str
    ) -> None:
        """Each ConceptType maps to the correct node type string."""
        concept = Concept(
            id=f"test-{expected_node_type}",
            type=concept_type,
            file="test.md",
            section="Test",
            lines=(1, 1),
            content="test content",
        )

        node = concept_to_node(concept)

        assert node.type == expected_node_type

    def test_metadata_does_not_overwrite_existing(self) -> None:
        """Concept metadata is preserved; section/lines are added alongside."""
        concept = Concept(
            id="guardrail-must-code-001",
            type=ConceptType.GUARDRAIL,
            file="governance/guardrails.md",
            section="Code Quality: MUST-CODE-001",
            lines=(10, 20),
            content="Type hints required",
            metadata={"level": "MUST", "always_on": True},
        )

        node = concept_to_node(concept)

        assert node.metadata["level"] == "MUST"
        assert node.metadata["always_on"] is True
        assert node.metadata["section"] == "Code Quality: MUST-CODE-001"
        assert node.metadata["lines"] == (10, 20)
