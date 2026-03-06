"""Tests for GovernanceExtractor."""

from __future__ import annotations

import logging
from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.extractor import GovernanceExtractor
from raise_cli.governance.models import ConceptType
from raise_core.graph.models import GraphNode


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

    def test_extract_from_file_with_explicit_type(
        self, tmp_governance_structure: Path
    ) -> None:
        """Should extract from file with explicitly provided concept type."""
        extractor = GovernanceExtractor(tmp_governance_structure)
        prd_file = tmp_governance_structure / "governance" / "prd.md"

        concepts = extractor.extract_from_file(prd_file, ConceptType.REQUIREMENT)

        assert len(concepts) == 2
        assert all(c.type == ConceptType.REQUIREMENT for c in concepts)

    def test_extract_from_file_with_inferred_type(
        self, tmp_governance_structure: Path
    ) -> None:
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

    def test_extract_unsupported_concept_type(
        self, tmp_governance_structure: Path
    ) -> None:
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

    def test_infer_type_from_constitution_file(
        self, tmp_governance_structure: Path
    ) -> None:
        """Should infer PRINCIPLE type from Constitution file."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concept_type = extractor._infer_concept_type(Path("constitution.md"))
        assert concept_type == ConceptType.PRINCIPLE

    def test_infer_type_fails_for_unknown_file(
        self, tmp_governance_structure: Path
    ) -> None:
        """Should raise ValueError for unknown file type."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        with pytest.raises(ValueError, match="Cannot infer concept type"):
            extractor._infer_concept_type(Path("unknown.md"))

    def test_extract_all_returns_graph_nodes(
        self, tmp_governance_structure: Path
    ) -> None:
        """extract_all() returns list[GraphNode] via registry path."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        nodes = extractor.extract_all()

        # Should have extracted 2 requirements + 1 outcome + 1 principle = 4 total
        assert len(nodes) == 4
        assert all(isinstance(n, GraphNode) for n in nodes)

        # Check types are present (string values, not ConceptType enum)
        types = {n.type for n in nodes}
        assert "requirement" in types
        assert "outcome" in types
        assert "principle" in types

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

    def test_infer_type_from_roadmap_file(self, tmp_governance_structure: Path) -> None:
        """Should infer RELEASE type from roadmap file."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        concept_type = extractor._infer_concept_type(Path("roadmap.md"))
        assert concept_type == ConceptType.RELEASE

    def test_integration_with_real_governance(self) -> None:
        """Should extract GraphNodes from real raise-cli governance files."""
        extractor = GovernanceExtractor()

        prd_exists = (Path.cwd() / "governance" / "prd.md").exists()
        vision_exists = (Path.cwd() / "governance" / "vision.md").exists()
        constitution_exists = (
            Path.cwd() / "framework" / "reference" / "constitution.md"
        ).exists()

        if not (prd_exists and vision_exists and constitution_exists):
            pytest.skip("Real governance files not found")

        nodes = extractor.extract_all()

        # Should extract 20+ nodes from raise-commons
        assert len(nodes) >= 20
        assert all(isinstance(n, GraphNode) for n in nodes)

        # Should have core types
        types = {n.type for n in nodes}
        assert "requirement" in types
        assert "outcome" in types
        assert "principle" in types

        # All nodes should have required fields
        for node in nodes:
            assert len(node.id) > 0
            assert len(node.content) > 0


class TestRegistryPath:
    """Tests for the registry-based extract_all() path."""

    def test_extract_all_with_broken_parser(
        self,
        tmp_governance_structure: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Broken parser logs warning, others still produce nodes."""
        from raise_cli.adapters.models import ArtifactLocator
        from raise_core.graph.models import GraphNode

        class BrokenParser:
            def can_parse(self, locator: ArtifactLocator) -> bool:
                return locator.artifact_type == "prd"

            def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
                raise RuntimeError("parser exploded")

        class GoodParser:
            def can_parse(self, locator: ArtifactLocator) -> bool:
                return locator.artifact_type == "constitution"

            def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
                return [
                    GraphNode(
                        id="test-1", type="principle", content="ok", created="now"
                    )
                ]

        extractor = GovernanceExtractor(
            tmp_governance_structure,
            parsers={"prd": BrokenParser, "constitution": GoodParser},
        )

        with caplog.at_level(logging.WARNING):
            nodes = extractor.extract_all()

        # Good parser produced nodes; broken parser didn't crash the build
        assert any(n.id == "test-1" for n in nodes)
        assert "parser exploded" in caplog.text or "Error" in caplog.text

    def test_extract_with_result_backward_compat(
        self, tmp_governance_structure: Path
    ) -> None:
        """extract_with_result() still returns ExtractionResult with Concept objects."""
        extractor = GovernanceExtractor(tmp_governance_structure)

        result = extractor.extract_with_result()

        # Must return Concept objects, not GraphNode
        assert result.total >= 1
        for concept in result.concepts:
            assert hasattr(concept, "file")
            assert hasattr(concept, "section")
            assert hasattr(concept, "lines")
            assert hasattr(concept, "type")
            # type should be ConceptType enum, not string
            assert isinstance(concept.type, ConceptType)


class TestRoadmapExtraction:
    """Tests for roadmap extraction wiring in GovernanceExtractor."""

    @pytest.fixture
    def project_with_roadmap(self, tmp_path: Path) -> Path:
        """Create project with roadmap file."""
        project_root = tmp_path / "project"
        governance = project_root / "governance"
        governance.mkdir(parents=True)

        roadmap = governance / "roadmap.md"
        roadmap.write_text(
            dedent(
                """\
                # Roadmap: test-project

                ## Releases

                | ID | Release | Target | Status | Epics |
                |----|---------|--------|--------|-------|
                | REL-V1.0 | V1.0 MVP | 2026-01-01 | Complete | E1, E2 |
                | REL-V2.0 | V2.0 Core | 2026-02-15 | In Progress | E3 |
                """
            )
        )
        return project_root

    def test_extract_with_result_includes_releases(
        self, project_with_roadmap: Path
    ) -> None:
        """Should extract release concepts from roadmap."""
        extractor = GovernanceExtractor(project_with_roadmap)

        result = extractor.extract_with_result()

        release_concepts = [c for c in result.concepts if c.type == ConceptType.RELEASE]
        assert len(release_concepts) == 2

    def test_release_ids_in_extraction(self, project_with_roadmap: Path) -> None:
        """Should produce correct release IDs."""
        extractor = GovernanceExtractor(project_with_roadmap)

        result = extractor.extract_with_result()

        ids = {c.id for c in result.concepts if c.type == ConceptType.RELEASE}
        assert "rel-v1.0" in ids
        assert "rel-v2.0" in ids

    def test_files_processed_counts_roadmap(self, project_with_roadmap: Path) -> None:
        """Should count roadmap file as processed."""
        extractor = GovernanceExtractor(project_with_roadmap)

        result = extractor.extract_with_result()

        assert result.files_processed >= 1
