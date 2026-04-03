"""Tests for memory models."""

from datetime import date

from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryLoadResult,
    MemoryRelationship,
    MemoryRelationshipType,
    PatternSubType,
)


class TestMemoryConceptType:
    """Tests for MemoryConceptType enum."""

    def test_pattern_value(self) -> None:
        """Pattern type has correct value."""
        assert MemoryConceptType.PATTERN.value == "pattern"

    def test_calibration_value(self) -> None:
        """Calibration type has correct value."""
        assert MemoryConceptType.CALIBRATION.value == "calibration"

    def test_session_value(self) -> None:
        """Session type has correct value."""
        assert MemoryConceptType.SESSION.value == "session"

    def test_all_types_are_strings(self) -> None:
        """All types are string enums."""
        for concept_type in MemoryConceptType:
            assert isinstance(concept_type.value, str)


class TestPatternSubType:
    """Tests for PatternSubType enum."""

    def test_all_subtypes_exist(self) -> None:
        """All expected subtypes exist."""
        assert PatternSubType.CODEBASE.value == "codebase"
        assert PatternSubType.PROCESS.value == "process"
        assert PatternSubType.ARCHITECTURE.value == "architecture"
        assert PatternSubType.TECHNICAL.value == "technical"
        assert PatternSubType.APPROACH.value == "approach"
        assert PatternSubType.RISK.value == "risk"

    def test_approach_subtype(self) -> None:
        """Approach subtype has correct value."""
        assert PatternSubType.APPROACH == "approach"

    def test_risk_subtype(self) -> None:
        """Risk subtype has correct value."""
        assert PatternSubType.RISK == "risk"


class TestMemoryRelationshipType:
    """Tests for MemoryRelationshipType enum."""

    def test_learned_from_value(self) -> None:
        """Learned from relationship has correct value."""
        assert MemoryRelationshipType.LEARNED_FROM.value == "learned_from"

    def test_related_to_value(self) -> None:
        """Related to relationship has correct value."""
        assert MemoryRelationshipType.RELATED_TO.value == "related_to"

    def test_validates_value(self) -> None:
        """Validates relationship has correct value."""
        assert MemoryRelationshipType.VALIDATES.value == "validates"

    def test_applies_to_value(self) -> None:
        """Applies to relationship has correct value."""
        assert MemoryRelationshipType.APPLIES_TO.value == "applies_to"


class TestMemoryConcept:
    """Tests for MemoryConcept model."""

    def test_create_pattern_concept(self) -> None:
        """Create a pattern concept."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Singleton with get/set/configure",
            context=["testing", "module-design"],
            created=date(2026, 1, 31),
            metadata={"sub_type": "codebase"},
        )
        assert concept.id == "PAT-001"
        assert concept.type == MemoryConceptType.PATTERN
        assert "Singleton" in concept.content
        assert "testing" in concept.context
        assert concept.created == date(2026, 1, 31)
        assert concept.metadata["sub_type"] == "codebase"

    def test_create_calibration_concept(self) -> None:
        """Create a calibration concept."""
        concept = MemoryConcept(
            id="CAL-001",
            type=MemoryConceptType.CALIBRATION,
            content="F2.1 Concept Extraction - actual: 52min - velocity: 3.5x",
            context=["F2.1", "s", "kata-cycle"],
            created=date(2026, 1, 31),
            metadata={"story": "F2.1", "ratio": 3.5},
        )
        assert concept.id == "CAL-001"
        assert concept.type == MemoryConceptType.CALIBRATION
        assert concept.metadata["ratio"] == 3.5

    def test_create_session_concept(self) -> None:
        """Create a session concept."""
        concept = MemoryConcept(
            id="SES-001",
            type=MemoryConceptType.SESSION,
            content="E3 Implementation Plan: /epic-plan skill complete",
            context=["story", "epic", "implementation"],
            created=date(2026, 2, 1),
            metadata={"session_type": "story", "topic": "E3 Implementation Plan"},
        )
        assert concept.id == "SES-001"
        assert concept.type == MemoryConceptType.SESSION
        assert concept.metadata["session_type"] == "story"

    def test_default_context_is_empty_list(self) -> None:
        """Context defaults to empty list."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),
        )
        assert concept.context == []

    def test_default_metadata_is_empty_dict(self) -> None:
        """Metadata defaults to empty dict."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),
        )
        assert concept.metadata == {}

    def test_token_estimate(self) -> None:
        """Token estimate is content length // 4."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="A" * 100,  # 100 chars
            created=date(2026, 1, 31),
        )
        assert concept.token_estimate == 25


class TestMemoryRelationship:
    """Tests for MemoryRelationship model."""

    def test_create_learned_from_relationship(self) -> None:
        """Create a learned_from relationship."""
        rel = MemoryRelationship(
            source="PAT-001",
            target="SES-001",
            type=MemoryRelationshipType.LEARNED_FROM,
            metadata={"confidence": 1.0},
        )
        assert rel.source == "PAT-001"
        assert rel.target == "SES-001"
        assert rel.type == MemoryRelationshipType.LEARNED_FROM
        assert rel.metadata["confidence"] == 1.0

    def test_create_related_to_relationship(self) -> None:
        """Create a related_to relationship."""
        rel = MemoryRelationship(
            source="PAT-001",
            target="PAT-002",
            type=MemoryRelationshipType.RELATED_TO,
        )
        assert rel.type == MemoryRelationshipType.RELATED_TO
        assert rel.metadata == {}


class TestMemoryLoadResult:
    """Tests for MemoryLoadResult model."""

    def test_empty_result(self) -> None:
        """Create an empty load result."""
        result = MemoryLoadResult()
        assert result.concepts == []
        assert result.total == 0
        assert result.files_processed == 0
        assert result.errors == []

    def test_result_with_concepts(self) -> None:
        """Create a result with concepts."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),
        )
        result = MemoryLoadResult(
            concepts=[concept],
            total=1,
            files_processed=1,
            errors=[],
        )
        assert len(result.concepts) == 1
        assert result.total == 1
        assert result.files_processed == 1
