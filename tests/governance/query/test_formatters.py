"""Tests for output formatters."""

from pathlib import Path

import pytest

from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.query.formatters import (
    estimate_tokens,
    format_json,
    format_markdown,
)
from raise_cli.governance.query.models import (
    ContextMetadata,
    ContextResult,
    QueryStrategy,
)


class TestEstimateTokens:
    """Tests for token estimation."""

    def test_estimate_tokens_basic(self) -> None:
        """Test basic token estimation."""
        text = "The system must validate inputs"
        tokens = estimate_tokens(text)

        # 5 words * 1.3 = 6.5 → 6
        assert tokens == 6

    def test_estimate_tokens_empty(self) -> None:
        """Test token estimation for empty string."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_single_word(self) -> None:
        """Test token estimation for single word."""
        # 1 word * 1.3 = 1.3 → 1
        assert estimate_tokens("word") == 1

    def test_estimate_tokens_longer_text(self) -> None:
        """Test token estimation for longer text."""
        text = " ".join(["word"] * 100)  # 100 words
        tokens = estimate_tokens(text)

        # 100 * 1.3 = 130
        assert tokens == 130


@pytest.fixture
def sample_result() -> ContextResult:
    """Create sample ContextResult for testing."""
    concept = Concept(
        id="req-rf-05",
        type=ConceptType.REQUIREMENT,
        file="governance/projects/raise-cli/prd.md",
        section="RF-05: Context Generation",
        lines=(206, 214),
        content="The system MUST generate CLAUDE.md files containing governance-derived context...",
        metadata={"requirement_id": "RF-05"},
    )

    metadata = ContextMetadata(
        query="req-rf-05",
        strategy=QueryStrategy.CONCEPT_LOOKUP,
        total_concepts=1,
        token_estimate=100,
        traversal_depth=1,
        paths=[["req-rf-05", "principle-governance-as-code"]],
        execution_time_ms=12.5,
    )

    return ContextResult(concepts=[concept], metadata=metadata)


@pytest.fixture
def empty_result() -> ContextResult:
    """Create empty ContextResult for testing."""
    metadata = ContextMetadata(
        query="nonexistent",
        strategy=QueryStrategy.CONCEPT_LOOKUP,
        total_concepts=0,
        token_estimate=0,
        traversal_depth=0,
        paths=[],
        execution_time_ms=5.0,
    )

    return ContextResult(concepts=[], metadata=metadata)


class TestFormatMarkdown:
    """Tests for markdown formatting."""

    def test_format_markdown_basic(self, sample_result: ContextResult) -> None:
        """Test basic markdown formatting."""
        markdown = format_markdown(sample_result)

        # Check header
        assert "# Minimum Viable Context" in markdown
        assert "**Query:** `req-rf-05`" in markdown
        assert "**Strategy:** concept_lookup" in markdown
        assert "**Concepts:** 1" in markdown

        # Check concept content
        assert "RF-05: Context Generation" in markdown
        assert "The system MUST generate" in markdown

    def test_format_markdown_includes_metadata(
        self, sample_result: ContextResult
    ) -> None:
        """Test markdown includes concept metadata."""
        markdown = format_markdown(sample_result)

        # Type and file information
        assert "**Type:** requirement" in markdown
        assert "**File:** governance/projects/raise-cli/prd.md" in markdown
        assert "**Lines:** 206-214" in markdown

        # Requirement ID
        assert "*Requirement ID: RF-05*" in markdown

    def test_format_markdown_includes_paths(self, sample_result: ContextResult) -> None:
        """Test markdown includes relationship paths."""
        markdown = format_markdown(sample_result)

        assert "## Relationship Paths" in markdown
        assert "`req-rf-05` → `principle-governance-as-code`" in markdown

    def test_format_markdown_includes_execution_metadata(
        self, sample_result: ContextResult
    ) -> None:
        """Test markdown includes execution metadata."""
        markdown = format_markdown(sample_result)

        assert "Execution time: 12.50ms" in markdown
        assert "Token estimate: ~100" in markdown

    def test_format_markdown_includes_savings_estimate(
        self, sample_result: ContextResult
    ) -> None:
        """Test markdown includes token savings estimate."""
        markdown = format_markdown(sample_result)

        # Should estimate savings vs baseline
        assert "Estimated savings:" in markdown
        assert "%" in markdown

    def test_format_markdown_empty_result(self, empty_result: ContextResult) -> None:
        """Test formatting empty result."""
        markdown = format_markdown(empty_result)

        assert "# Minimum Viable Context" in markdown
        assert "*No concepts found matching the query.*" in markdown

    def test_format_markdown_multiple_concepts(self) -> None:
        """Test formatting result with multiple concepts."""
        concepts = [
            Concept(
                id="req-rf-05",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="RF-05",
                lines=(1, 10),
                content="Content 1",
                metadata={},
            ),
            Concept(
                id="principle-governance",
                type=ConceptType.PRINCIPLE,
                file="constitution.md",
                section="§2",
                lines=(20, 30),
                content="Content 2",
                metadata={"principle_number": "2"},
            ),
        ]

        metadata = ContextMetadata(
            query="test",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            total_concepts=2,
            token_estimate=200,
            traversal_depth=1,
            paths=[],
            execution_time_ms=10.0,
        )

        result = ContextResult(concepts=concepts, metadata=metadata)
        markdown = format_markdown(result)

        # Both concepts should be included
        assert "RF-05" in markdown
        assert "§2" in markdown
        assert "Content 1" in markdown
        assert "Content 2" in markdown

        # Separator between concepts
        assert markdown.count("---") >= 2

    def test_format_markdown_truncates_long_content(self) -> None:
        """Test markdown truncates very long content."""
        long_content = "word " * 200  # Very long content

        concept = Concept(
            id="test",
            type=ConceptType.REQUIREMENT,
            file="test.md",
            section="Test",
            lines=(1, 10),
            content=long_content,
            metadata={},
        )

        metadata = ContextMetadata(
            query="test",
            strategy=QueryStrategy.CONCEPT_LOOKUP,
            total_concepts=1,
            token_estimate=100,
            traversal_depth=0,
            paths=[],
            execution_time_ms=5.0,
        )

        result = ContextResult(concepts=[concept], metadata=metadata)
        markdown = format_markdown(result)

        # Content should be truncated
        assert "..." in markdown
        assert len(markdown) < len(long_content)


class TestFormatJson:
    """Tests for JSON formatting."""

    def test_format_json_basic(self, sample_result: ContextResult) -> None:
        """Test basic JSON formatting."""
        json_str = format_json(sample_result)

        assert "concepts" in json_str
        assert "metadata" in json_str
        assert "req-rf-05" in json_str

    def test_format_json_is_valid(self, sample_result: ContextResult) -> None:
        """Test JSON output is valid."""
        import json

        json_str = format_json(sample_result)

        # Should parse without error
        data = json.loads(json_str)
        assert "concepts" in data
        assert "metadata" in data

    def test_format_json_empty_result(self, empty_result: ContextResult) -> None:
        """Test JSON formatting of empty result."""
        import json

        json_str = format_json(empty_result)
        data = json.loads(json_str)

        assert data["concepts"] == []
        assert data["metadata"]["total_concepts"] == 0


class TestContextResultToFile:
    """Tests for ContextResult.to_file() integration."""

    def test_to_file_markdown(
        self, sample_result: ContextResult, tmp_path: Path
    ) -> None:
        """Test saving result to markdown file."""
        output_file = tmp_path / "result.md"

        sample_result.to_file(output_file, format="markdown")

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Minimum Viable Context" in content
        assert "req-rf-05" in content

    def test_to_file_json(self, sample_result: ContextResult, tmp_path: Path) -> None:
        """Test saving result to JSON file."""
        import json

        output_file = tmp_path / "result.json"

        sample_result.to_file(output_file, format="json")

        assert output_file.exists()
        content = output_file.read_text()
        data = json.loads(content)
        assert "concepts" in data
        assert "metadata" in data
