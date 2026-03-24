"""Tests for governance.models module."""

import pytest
from pydantic import ValidationError

from raise_cli.governance.models import Concept, ConceptType, ExtractionResult


class TestConceptType:
    """Tests for ConceptType enum."""

    def test_all_types_defined(self) -> None:
        """All expected concept types should be defined."""
        assert ConceptType.REQUIREMENT == "requirement"
        assert ConceptType.OUTCOME == "outcome"
        assert ConceptType.PRINCIPLE == "principle"
        assert ConceptType.PATTERN == "pattern"
        assert ConceptType.PRACTICE == "practice"


class TestConcept:
    """Tests for Concept model."""

    def test_create_valid_concept(self) -> None:
        """Should create concept with valid data."""
        concept = Concept(
            id="req-rf-05",
            type=ConceptType.REQUIREMENT,
            file="governance/prd.md",
            section="RF-05: Golden Context Generation",
            lines=(206, 214),
            content="The system MUST generate CLAUDE.md...",
            metadata={"requirement_id": "RF-05", "title": "Golden Context Generation"},
        )

        assert concept.id == "req-rf-05"
        assert concept.type == ConceptType.REQUIREMENT
        assert concept.file == "governance/prd.md"
        assert concept.section == "RF-05: Golden Context Generation"
        assert concept.lines == (206, 214)
        assert "CLAUDE.md" in concept.content
        assert concept.metadata["requirement_id"] == "RF-05"

    def test_create_concept_with_default_metadata(self) -> None:
        """Should create concept with empty metadata by default."""
        concept = Concept(
            id="test-id",
            type=ConceptType.OUTCOME,
            file="test.md",
            section="Test",
            lines=(1, 10),
            content="Test content",
        )

        assert concept.metadata == {}

    def test_invalid_line_range(self) -> None:
        """Should raise ValueError if start line > end line."""
        with pytest.raises(ValueError, match="Invalid line range"):
            Concept(
                id="test-id",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="Test",
                lines=(10, 1),  # Invalid: start > end
                content="Test",
            )

    def test_missing_required_fields(self) -> None:
        """Should raise ValidationError if required fields missing."""
        with pytest.raises(ValidationError):
            Concept(  # type: ignore
                id="test-id",
                # Missing type, file, section, lines, content
            )

    def test_concept_serialization(self) -> None:
        """Should serialize to dict correctly."""
        concept = Concept(
            id="req-rf-01",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-01: Test",
            lines=(1, 5),
            content="Test content",
            metadata={"key": "value"},
        )

        data = concept.model_dump()
        assert data["id"] == "req-rf-01"
        assert data["type"] == "requirement"
        assert data["lines"] == (1, 5)
        assert data["metadata"] == {"key": "value"}

    def test_concept_deserialization(self) -> None:
        """Should deserialize from dict correctly."""
        data = {
            "id": "outcome-test",
            "type": "outcome",
            "file": "vision.md",
            "section": "Test Outcome",
            "lines": [10, 20],
            "content": "Outcome content",
            "metadata": {"outcome_name": "Test"},
        }

        concept = Concept(**data)
        assert concept.id == "outcome-test"
        assert concept.type == ConceptType.OUTCOME
        assert concept.lines == (10, 20)


class TestExtractionResult:
    """Tests for ExtractionResult model."""

    def test_create_valid_result(self) -> None:
        """Should create result with valid data."""
        concept = Concept(
            id="test-id",
            type=ConceptType.REQUIREMENT,
            file="test.md",
            section="Test",
            lines=(1, 5),
            content="Test",
        )

        result = ExtractionResult(
            concepts=[concept],
            total=1,
            files_processed=1,
            errors=[],
        )

        assert len(result.concepts) == 1
        assert result.total == 1
        assert result.files_processed == 1
        assert result.errors == []

    def test_create_result_with_defaults(self) -> None:
        """Should create result with default empty lists."""
        result = ExtractionResult(
            total=0,
            files_processed=0,
        )

        assert result.concepts == []
        assert result.errors == []

    def test_result_with_errors(self) -> None:
        """Should capture errors during extraction."""
        result = ExtractionResult(
            concepts=[],
            total=0,
            files_processed=0,
            errors=["File not found: missing.md", "Parse error in broken.md"],
        )

        assert len(result.errors) == 2
        assert "File not found" in result.errors[0]

    def test_result_serialization(self) -> None:
        """Should serialize to dict correctly."""
        concept = Concept(
            id="test",
            type=ConceptType.PRINCIPLE,
            file="test.md",
            section="Test",
            lines=(1, 1),
            content="Test",
        )

        result = ExtractionResult(
            concepts=[concept],
            total=1,
            files_processed=1,
            errors=["warning"],
        )

        data = result.model_dump()
        assert data["total"] == 1
        assert data["files_processed"] == 1
        assert len(data["concepts"]) == 1
        assert len(data["errors"]) == 1
