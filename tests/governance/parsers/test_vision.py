"""Tests for Vision parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.vision import extract_outcomes

# Note: sanitize_id tests are in tests/core/test_text.py


@pytest.fixture
def tmp_vision_file(tmp_path: Path) -> Path:
    """Create a temporary Vision file for testing.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary Vision file.
    """
    vision_content = dedent(
        """
        # Vision Document

        ## Key Outcomes

        | **Outcome** | Description |
        |-------------|-------------|
        | **Context Generation** | Generate AI context from governance |
        | **Token Optimization** | Reduce token usage by 97% |
        | **Observable Workflow** | Every decision traceable |
        """
    )

    vision_file = tmp_path / "governance" / "vision.md"
    vision_file.parent.mkdir(parents=True, exist_ok=True)
    vision_file.write_text(vision_content)

    return vision_file


class TestExtractOutcomes:
    """Tests for extract_outcomes function."""

    def test_extract_from_valid_vision(self, tmp_vision_file: Path) -> None:
        """Should extract all outcomes from valid Vision file."""
        outcomes = extract_outcomes(tmp_vision_file, tmp_vision_file.parent.parent)

        assert len(outcomes) == 3
        assert all(o.type == ConceptType.OUTCOME for o in outcomes)

    def test_outcome_ids(self, tmp_vision_file: Path) -> None:
        """Should generate correct IDs from outcome names."""
        outcomes = extract_outcomes(tmp_vision_file)

        ids = [o.id for o in outcomes]
        assert "outcome-context-generation" in ids
        assert "outcome-token-optimization" in ids
        assert "outcome-observable-workflow" in ids

    def test_outcome_metadata(self, tmp_vision_file: Path) -> None:
        """Should extract outcome name to metadata."""
        outcomes = extract_outcomes(tmp_vision_file)

        outcome = next(o for o in outcomes if o.id == "outcome-context-generation")
        assert outcome.metadata["outcome_name"] == "Context Generation"

    def test_outcome_sections(self, tmp_vision_file: Path) -> None:
        """Should use outcome name as section."""
        outcomes = extract_outcomes(tmp_vision_file)

        outcome = next(o for o in outcomes if o.id == "outcome-token-optimization")
        assert outcome.section == "Token Optimization"

    def test_outcome_content(self, tmp_vision_file: Path) -> None:
        """Should extract description as content."""
        outcomes = extract_outcomes(tmp_vision_file)

        outcome = next(o for o in outcomes if o.id == "outcome-context-generation")
        assert outcome.content == "Generate AI context from governance"

    def test_relative_file_path(self, tmp_vision_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_vision_file.parent.parent
        outcomes = extract_outcomes(tmp_vision_file, project_root)

        outcome = outcomes[0]
        assert outcome.file == "governance/vision.md"

    def test_empty_file(self, tmp_path: Path) -> None:
        """Should return empty list for empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        outcomes = extract_outcomes(empty_file)
        assert outcomes == []

    def test_missing_file(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        outcomes = extract_outcomes(missing_file)
        assert outcomes == []

    def test_no_outcomes_table(self, tmp_path: Path) -> None:
        """Should return empty list if no outcomes table found."""
        no_table_file = tmp_path / "no_table.md"
        no_table_file.write_text(
            dedent(
                """
                # Vision

                Some text but no outcomes table.
                """
            )
        )

        outcomes = extract_outcomes(no_table_file)
        assert outcomes == []

    def test_table_with_context_header(self, tmp_path: Path) -> None:
        """Should detect table with 'Context' in header."""
        vision_file = tmp_path / "vision.md"
        vision_file.write_text(
            dedent(
                """
                | **Context** | Description |
                |-------------|-------------|
                | **Test Context** | Test description |
                """
            )
        )

        outcomes = extract_outcomes(vision_file)
        assert len(outcomes) == 1
        assert outcomes[0].metadata["outcome_name"] == "Test Context"

    def test_outcome_with_special_characters(self, tmp_path: Path) -> None:
        """Should handle special characters in outcome names."""
        vision_file = tmp_path / "special.md"
        vision_file.write_text(
            dedent(
                """
                | **Outcome** | Description |
                |-------------|-------------|
                | **MVC (Minimum Viable Context)** | Description here |
                """
            )
        )

        outcomes = extract_outcomes(vision_file)
        assert len(outcomes) == 1
        assert outcomes[0].id == "outcome-mvc-minimum-viable-context"
        assert outcomes[0].metadata["outcome_name"] == "MVC (Minimum Viable Context)"

    def test_table_with_varying_spacing(self, tmp_path: Path) -> None:
        """Should handle varying whitespace in table rows."""
        vision_file = tmp_path / "spacing.md"
        vision_file.write_text(
            dedent(
                """
                | **Outcome** | Description |
                |---|---|
                |  **Test**  |  Description  |
                """
            )
        )

        outcomes = extract_outcomes(vision_file)
        assert len(outcomes) == 1
        assert outcomes[0].metadata["outcome_name"] == "Test"
        assert outcomes[0].content == "Description"

    def test_integration_with_real_vision(self) -> None:
        """Should extract outcomes from real raise-cli Vision."""
        vision_path = Path("governance/vision.md")

        if not vision_path.exists():
            pytest.skip("Real Vision file not found")

        outcomes = extract_outcomes(vision_path)

        # Should extract at least some outcomes (count varies as vision evolves)
        assert len(outcomes) >= 1

        # Should have proper structure
        for outcome in outcomes:
            assert outcome.id.startswith("outcome-")
            assert outcome.type == ConceptType.OUTCOME
            assert len(outcome.metadata["outcome_name"]) > 0
            assert len(outcome.content) > 0
