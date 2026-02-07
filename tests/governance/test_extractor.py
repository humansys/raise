"""Tests for GovernanceExtractor."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.extractor import GovernanceExtractor
from raise_cli.governance.models import ConceptType


@pytest.fixture
def tmp_governance_structure(tmp_path: Path) -> Path:
    """Create a temporary governance directory structure.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary project root.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create PRD
    prd_file = project_root / "governance" / "prd.md"
    prd_file.parent.mkdir(parents=True)
    prd_file.write_text(
        dedent(
            """
            ### RF-01: First Requirement
            Description of first requirement.

            ### RF-02: Second Requirement
            Description of second requirement.
            """
        )
    )

    # Create Vision
    vision_file = project_root / "governance" / "vision.md"
    vision_file.write_text(
        dedent(
            """
            | **Outcome** | Description |
            |-------------|-------------|
            | **Test Outcome** | Test description |
            """
        )
    )

    # Create Constitution
    constitution_file = project_root / "framework" / "reference" / "constitution.md"
    constitution_file.parent.mkdir(parents=True)
    constitution_file.write_text(
        dedent(
            """
            ### §1. First Principle
            Description of first principle.
            """
        )
    )

    return project_root


class TestGovernanceExtractor:
    """Tests for GovernanceExtractor class."""

    def test_init_with_default_root(self) -> None:
        """Should initialize with current directory as project root."""
        extractor = GovernanceExtractor()
        assert extractor.project_root == Path.cwd()

    def test_init_with_custom_root(self, tmp_path: Path) -> None:
        """Should initialize with custom project root."""
        extractor = GovernanceExtractor(tmp_path)
        assert extractor.project_root == tmp_path

    def test_extract_from_file_with_explicit_type(self, tmp_governance_structure: Path) -> None:
        """Should extract from file with explicitly provided concept type."""
        extractor = GovernanceExtractor(tmp_governance_structure)
        prd_file = tmp_governance_structure / "governance" / "prd.md"

        concepts = extractor.extract_from_file(prd_file, ConceptType.REQUIREMENT)

        assert len(concepts) == 2
        assert all(c.type == ConceptType.REQUIREMENT for c in concepts)

    def test_extract_from_file_with_inferred_type(self, tmp_governance_structure: Path) -> None:
        """Should infer concept type from file path."""
        extractor = GovernanceExtractor(tmp_governance_structure)
        prd_file = tmp_governance_structure / "governance" / "prd.md"

        concepts = extractor.extract_from_file(prd_file)

        assert len(concepts) == 2
        assert all(c.type == ConceptType.REQUIREMENT for c in concepts)

    def test_extract_from_missing_file(self, tmp_governance_structure: Path) -> None:
        """Should return empty list for missing file with warning."""
        extractor = GovernanceExtractor(tmp_governance_structure)
        missing_file = tmp_governance_structure / "missing.md"

        concepts = extractor.extract_from_file(missing_file, ConceptType.REQUIREMENT)

        assert concepts == []

    def test_extract_unsupported_concept_type(self, tmp_governance_structure: Path) -> None:
        """Should return empty list for unsupported concept type."""
        extractor = GovernanceExtractor(tmp_governance_structure)
        prd_file = tmp_governance_structure / "governance" / "prd.md"

        # PATTERN and PRACTICE are not yet supported
        concepts = extractor.extract_from_file(prd_file, ConceptType.PATTERN)
        assert concepts == []

    def test_infer_type_from_prd_file(self, tmp_governance_structure: Path) -> None:
        """Should infer REQUIREMENT type from PRD file."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concept_type = extractor._infer_concept_type(Path("prd.md"))
        assert concept_type == ConceptType.REQUIREMENT

        concept_type = extractor._infer_concept_type(Path("requirements.md"))
        assert concept_type == ConceptType.REQUIREMENT

    def test_infer_type_from_vision_file(self, tmp_governance_structure: Path) -> None:
        """Should infer OUTCOME type from Vision file."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concept_type = extractor._infer_concept_type(Path("vision.md"))
        assert concept_type == ConceptType.OUTCOME

    def test_infer_type_from_constitution_file(self, tmp_governance_structure: Path) -> None:
        """Should infer PRINCIPLE type from Constitution file."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concept_type = extractor._infer_concept_type(Path("constitution.md"))
        assert concept_type == ConceptType.PRINCIPLE

    def test_infer_type_fails_for_unknown_file(self, tmp_governance_structure: Path) -> None:
        """Should raise ValueError for unknown file type."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        with pytest.raises(ValueError, match="Cannot infer concept type"):
            extractor._infer_concept_type(Path("unknown.md"))

    def test_extract_all(self, tmp_governance_structure: Path) -> None:
        """Should extract all concepts from standard locations."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concepts = extractor.extract_all()

        # Should have extracted 2 requirements + 1 outcome + 1 principle = 4 total
        assert len(concepts) == 4

        # Check types are present
        types = {c.type for c in concepts}
        assert ConceptType.REQUIREMENT in types
        assert ConceptType.OUTCOME in types
        assert ConceptType.PRINCIPLE in types

    def test_extract_with_result(self, tmp_governance_structure: Path) -> None:
        """Should return ExtractionResult with metadata."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        result = extractor.extract_with_result()

        assert result.total == 4
        assert result.files_processed == 3
        assert len(result.errors) == 0
        assert len(result.concepts) == 4

    def test_extract_with_errors(self, tmp_path: Path) -> None:
        """Should capture errors during extraction."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create a malformed file (will cause extraction error if parser is strict)
        # For now, parsers are lenient, so this test might not trigger errors
        # But it demonstrates the error handling path

        extractor = GovernanceExtractor(project_root)
        result = extractor.extract_with_result()

        # Should not crash, even with no files
        assert result.total == 0
        assert result.files_processed == 0

    def test_integration_with_real_governance(self) -> None:
        """Should extract concepts from real raise-cli governance files."""
        # This test runs against actual project files
        extractor = GovernanceExtractor()

        # Check if real files exist
        prd_exists = (Path.cwd() / "governance" / "prd.md").exists()
        vision_exists = (Path.cwd() / "governance" / "vision.md").exists()
        constitution_exists = (
            Path.cwd() / "framework" / "reference" / "constitution.md"
        ).exists()

        if not (prd_exists and vision_exists and constitution_exists):
            pytest.skip("Real governance files not found")

        concepts = extractor.extract_all()

        # Should extract 20+ concepts from raise-commons
        assert len(concepts) >= 20

        # Should have all three types
        types = {c.type for c in concepts}
        assert ConceptType.REQUIREMENT in types
        assert ConceptType.OUTCOME in types
        assert ConceptType.PRINCIPLE in types

        # All concepts should have required fields
        for concept in concepts:
            assert len(concept.id) > 0
            assert len(concept.file) > 0
            assert len(concept.section) > 0
            assert len(concept.content) > 0
            assert concept.lines[0] > 0
            assert concept.lines[1] >= concept.lines[0]
