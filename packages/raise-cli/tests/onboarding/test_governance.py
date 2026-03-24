"""Tests for governance generation from detected conventions."""

from __future__ import annotations

import pytest

from raise_cli.onboarding.conventions import (
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
from raise_cli.onboarding.governance import (
    GeneratedGuardrail,
    GuardrailGenerator,
    GuardrailLevel,
    generate_guardrails,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def high_confidence_conventions() -> ConventionResult:
    """Convention result with all HIGH confidence detections."""
    return ConventionResult(
        style=StyleConventions(
            indentation=IndentationConvention(
                style="spaces",
                width=4,
                confidence=Confidence.HIGH,
                sample_count=50,
                consistent_count=48,
            ),
            quote_style=QuoteConvention(
                style="double",
                confidence=Confidence.HIGH,
                sample_count=200,
                consistent_count=190,
            ),
            line_length=LineLengthConvention(
                max_length=88,
                confidence=Confidence.HIGH,
                sample_count=1000,
            ),
        ),
        naming=NamingConventions(
            functions=NamingConvention(
                pattern="snake_case",
                confidence=Confidence.HIGH,
                sample_count=100,
                consistent_count=95,
            ),
            classes=NamingConvention(
                pattern="PascalCase",
                confidence=Confidence.HIGH,
                sample_count=30,
                consistent_count=29,
            ),
            constants=NamingConvention(
                pattern="UPPER_SNAKE_CASE",
                confidence=Confidence.MEDIUM,
                sample_count=15,
                consistent_count=12,
            ),
        ),
        structure=StructureConventions(
            source_dir="src/mypackage",
            test_dir="tests",
            has_src_layout=True,
            common_patterns=["api/", "models/", "services/"],
        ),
        overall_confidence=Confidence.HIGH,
        files_analyzed=50,
        analysis_time_ms=150,
    )


@pytest.fixture
def low_confidence_conventions() -> ConventionResult:
    """Convention result with LOW confidence (small project)."""
    return ConventionResult(
        style=StyleConventions(
            indentation=IndentationConvention(
                style="spaces",
                width=2,
                confidence=Confidence.LOW,
                sample_count=3,
                consistent_count=2,
            ),
            quote_style=QuoteConvention(
                style="single",
                confidence=Confidence.LOW,
                sample_count=10,
                consistent_count=6,
            ),
            line_length=LineLengthConvention(
                max_length=120,
                confidence=Confidence.LOW,
                sample_count=50,
            ),
        ),
        naming=NamingConventions(
            functions=NamingConvention(
                pattern="snake_case",
                confidence=Confidence.LOW,
                sample_count=4,
                consistent_count=3,
            ),
            classes=NamingConvention(
                pattern="PascalCase",
                confidence=Confidence.LOW,
                sample_count=2,
                consistent_count=2,
            ),
            constants=NamingConvention(
                pattern="UPPER_SNAKE_CASE",
                confidence=Confidence.LOW,
                sample_count=1,
                consistent_count=1,
            ),
        ),
        structure=StructureConventions(
            source_dir=None,
            test_dir=None,
            has_src_layout=False,
            common_patterns=[],
        ),
        overall_confidence=Confidence.LOW,
        files_analyzed=3,
        analysis_time_ms=10,
    )


# =============================================================================
# Confidence to Level Mapping Tests
# =============================================================================


class TestConfidenceMapping:
    """Test confidence to guardrail level mapping."""

    def test_high_confidence_maps_to_must(self) -> None:
        """HIGH confidence conventions become MUST guardrails."""
        generator = GuardrailGenerator()
        level = generator.confidence_to_level(Confidence.HIGH)
        assert level == GuardrailLevel.MUST

    def test_medium_confidence_maps_to_should(self) -> None:
        """MEDIUM confidence conventions become SHOULD guardrails."""
        generator = GuardrailGenerator()
        level = generator.confidence_to_level(Confidence.MEDIUM)
        assert level == GuardrailLevel.SHOULD

    def test_low_confidence_maps_to_could(self) -> None:
        """LOW confidence conventions become COULD (optional) guardrails."""
        generator = GuardrailGenerator()
        level = generator.confidence_to_level(Confidence.LOW)
        assert level == GuardrailLevel.COULD


# =============================================================================
# Guardrail Generation Tests
# =============================================================================


class TestGuardrailGeneration:
    """Test individual guardrail generation."""

    def test_generates_indentation_guardrail(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate indentation guardrail from style conventions."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(high_confidence_conventions)

        indentation = next(
            (g for g in guardrails if "indent" in g.description.lower()), None
        )
        assert indentation is not None
        assert indentation.level == GuardrailLevel.MUST
        assert "4" in indentation.description and "space" in indentation.description

    def test_generates_quote_style_guardrail(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate quote style guardrail."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(high_confidence_conventions)

        quotes = next((g for g in guardrails if "quote" in g.description.lower()), None)
        assert quotes is not None
        assert "double" in quotes.description.lower()

    def test_generates_line_length_guardrail(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate line length guardrail."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(high_confidence_conventions)

        line_length = next(
            (g for g in guardrails if "line" in g.description.lower()), None
        )
        assert line_length is not None
        assert "88" in line_length.description

    def test_generates_naming_guardrails(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate naming convention guardrails."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(high_confidence_conventions)

        naming_guardrails = [g for g in guardrails if "naming" in g.id.lower()]
        assert len(naming_guardrails) >= 1  # At least function naming

    def test_generates_structure_guardrail_when_detected(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate structure guardrail when src layout detected."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(high_confidence_conventions)

        structure = next((g for g in guardrails if "structure" in g.id.lower()), None)
        assert structure is not None
        assert "src/" in structure.description

    def test_skips_structure_guardrail_when_not_detected(
        self, low_confidence_conventions: ConventionResult
    ) -> None:
        """Should not generate structure guardrail if no clear structure."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(low_confidence_conventions)

        structure = next((g for g in guardrails if "structure" in g.id.lower()), None)
        assert structure is None


class TestLowConfidenceHandling:
    """Test handling of low confidence conventions."""

    def test_low_confidence_generates_could_guardrails(
        self, low_confidence_conventions: ConventionResult
    ) -> None:
        """LOW confidence should generate COULD level guardrails."""
        generator = GuardrailGenerator()
        guardrails = generator.generate(low_confidence_conventions)

        # All guardrails should be COULD level
        for g in guardrails:
            assert g.level == GuardrailLevel.COULD


# =============================================================================
# Markdown Output Tests
# =============================================================================


class TestMarkdownGeneration:
    """Test markdown output generation."""

    def test_generates_valid_markdown(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate valid markdown content."""
        generator = GuardrailGenerator()
        markdown = generator.to_markdown(high_confidence_conventions)

        assert "# Guardrails" in markdown
        assert "MUST" in markdown
        assert "### Code Style" in markdown

    def test_generates_parser_compatible_format(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Output must be parseable by the guardrails parser.

        Parser requires:
        - YAML frontmatter with type: guardrails
        - ### section headings (not ##)
        - 5-column table with Derived from column
        - No backticks around IDs
        """
        generator = GuardrailGenerator()
        markdown = generator.to_markdown(
            high_confidence_conventions, project_name="test-proj"
        )

        # YAML frontmatter
        assert markdown.startswith("---\n")
        assert "type: guardrails" in markdown

        # ### section headings (parser regex: ^###\s+(.+?)$)
        assert "### Code Style" in markdown
        assert "### Naming" in markdown

        # 5-column table with Derived from
        assert "| Derived from |" in markdown

        # No backticks around IDs in table rows
        assert "| `" not in markdown

        # IDs are lowercase
        assert "| must-style-001 |" in markdown or "| should-" in markdown

    def test_includes_project_context(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should include project analysis context."""
        generator = GuardrailGenerator()
        markdown = generator.to_markdown(
            high_confidence_conventions, project_name="my-api"
        )

        assert "my-api" in markdown
        assert "50" in markdown  # files_analyzed count

    def test_includes_confidence_note(
        self, low_confidence_conventions: ConventionResult
    ) -> None:
        """Should note when confidence is low."""
        generator = GuardrailGenerator()
        markdown = generator.to_markdown(low_confidence_conventions)

        assert "low confidence" in markdown.lower() or "COULD" in markdown

    def test_generates_table_format(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """Should generate guardrails in table format."""
        generator = GuardrailGenerator()
        markdown = generator.to_markdown(high_confidence_conventions)

        # Should have table headers
        assert "| ID |" in markdown
        assert "| Level |" in markdown


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunction:
    """Test the generate_guardrails convenience function."""

    def test_generate_guardrails_returns_markdown(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """generate_guardrails should return markdown string."""
        result = generate_guardrails(high_confidence_conventions)
        assert isinstance(result, str)
        assert "# Guardrails" in result

    def test_generate_guardrails_with_project_name(
        self, high_confidence_conventions: ConventionResult
    ) -> None:
        """generate_guardrails should accept project_name."""
        result = generate_guardrails(
            high_confidence_conventions, project_name="test-project"
        )
        assert "test-project" in result


# =============================================================================
# Generated Guardrail Model Tests
# =============================================================================


class TestGeneratedGuardrailModel:
    """Test GeneratedGuardrail Pydantic model."""

    def test_guardrail_model_validation(self) -> None:
        """GeneratedGuardrail should validate fields."""
        guardrail = GeneratedGuardrail(
            id="MUST-STYLE-001",
            level=GuardrailLevel.MUST,
            category="Code Style",
            description="Use 4-space indentation",
            verification="ruff check .",
        )
        assert guardrail.id == "MUST-STYLE-001"
        assert guardrail.level == GuardrailLevel.MUST

    def test_guardrail_without_verification(self) -> None:
        """GeneratedGuardrail should allow optional verification."""
        guardrail = GeneratedGuardrail(
            id="SHOULD-STYLE-001",
            level=GuardrailLevel.SHOULD,
            category="Code Style",
            description="Prefer double quotes",
        )
        assert guardrail.verification is None
