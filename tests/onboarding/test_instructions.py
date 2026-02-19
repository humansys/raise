"""Tests for agent instructions file generation from detected conventions."""

from __future__ import annotations

import pytest

from rai_cli.config.agents import get_agent_config
from rai_cli.onboarding.instructions import InstructionsGenerator, generate_instructions
from rai_cli.onboarding.conventions import (
    Confidence,
    ConventionResult,
    IndentationConvention,
    LineLengthConvention,
    NamingConvention,
    NamingConventions,
    QuoteConvention,
    StructureConventions,
    StyleConventions,
)
from rai_cli.onboarding.detection import DetectionResult, ProjectType

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def brownfield_detection() -> DetectionResult:
    """Detection result for a brownfield project."""
    return DetectionResult(
        project_type=ProjectType.BROWNFIELD,
        code_file_count=25,
    )


@pytest.fixture
def greenfield_detection() -> DetectionResult:
    """Detection result for a greenfield project."""
    return DetectionResult(
        project_type=ProjectType.GREENFIELD,
        code_file_count=0,
    )


@pytest.fixture
def conventions() -> ConventionResult:
    """Convention result with typical Python conventions."""
    return ConventionResult(
        style=StyleConventions(
            indentation=IndentationConvention(
                style="spaces",
                width=4,
                confidence=Confidence.HIGH,
                sample_count=25,
                consistent_count=24,
            ),
            quote_style=QuoteConvention(
                style="double",
                confidence=Confidence.HIGH,
                sample_count=100,
                consistent_count=95,
            ),
            line_length=LineLengthConvention(
                max_length=88,
                confidence=Confidence.HIGH,
                sample_count=500,
            ),
        ),
        naming=NamingConventions(
            functions=NamingConvention(
                pattern="snake_case",
                confidence=Confidence.HIGH,
                sample_count=50,
                consistent_count=48,
            ),
            classes=NamingConvention(
                pattern="PascalCase",
                confidence=Confidence.HIGH,
                sample_count=15,
                consistent_count=15,
            ),
            constants=NamingConvention(
                pattern="UPPER_SNAKE_CASE",
                confidence=Confidence.MEDIUM,
                sample_count=8,
                consistent_count=7,
            ),
        ),
        structure=StructureConventions(
            source_dir="src/mypackage",
            test_dir="tests",
            has_src_layout=True,
            common_patterns=["api/", "models/", "services/"],
        ),
        overall_confidence=Confidence.HIGH,
        files_analyzed=25,
        analysis_time_ms=100,
    )


# =============================================================================
# Basic Generation Tests
# =============================================================================


class TestInstructionsGenerator:
    """Tests for InstructionsGenerator class."""

    def test_generates_markdown_string(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should generate a markdown string."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_project_name(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include project name in header."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="awesome-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "awesome-api" in result

    def test_includes_project_type(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should indicate project type."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "brownfield" in result.lower()


class TestConventionsSummary:
    """Tests for conventions summary section."""

    def test_includes_indentation_convention(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include indentation convention."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "4" in result and "space" in result.lower()

    def test_includes_naming_conventions(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include naming conventions."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "snake_case" in result
        assert "PascalCase" in result

    def test_includes_line_length(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include line length convention."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "88" in result


class TestStructureSection:
    """Tests for project structure section."""

    def test_includes_source_directory(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include source directory."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "src/mypackage" in result

    def test_includes_test_directory(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include test directory."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "tests" in result

    def test_includes_common_patterns(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include common directory patterns."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        # Should mention at least one of the patterns
        assert "api" in result.lower() or "models" in result.lower()


class TestGuardrailsReference:
    """Tests for guardrails reference."""

    def test_references_guardrails_file(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should reference the guardrails file."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "guardrails" in result.lower()


class TestGreenfieldHandling:
    """Tests for greenfield project handling."""

    def test_greenfield_generates_minimal_content(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """Greenfield should generate minimal CLAUDE.md."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        assert "new-project" in result
        assert "greenfield" in result.lower()

    def test_greenfield_suggests_defining_conventions(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """Greenfield should suggest defining conventions."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        # Should indicate conventions will be established
        assert "convention" in result.lower() or "establish" in result.lower()


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunction:
    """Tests for generate_instructions convenience function."""

    def test_returns_markdown_string(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """generate_instructions should return markdown string."""
        result = generate_instructions(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert isinstance(result, str)
        assert "my-api" in result

    def test_works_without_conventions(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """generate_instructions should work without conventions."""
        result = generate_instructions(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        assert "new-project" in result

    def test_accepts_ide_config(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """generate_instructions should accept ide_config parameter."""
        config = get_agent_config("antigravity")
        result = generate_instructions(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
            agent_config=config,
        )
        # Content is IDE-agnostic — same output regardless of config
        assert isinstance(result, str)
        assert "my-api" in result
