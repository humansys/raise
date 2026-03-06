"""Tests for PRD parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.prd import extract_requirements


@pytest.fixture
def tmp_prd_file(tmp_path: Path) -> Path:
    """Create a temporary PRD file for testing.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary PRD file.
    """
    prd_content = dedent(
        """
        # Product Requirements Document

        ## Requirements

        ### RF-01: First Requirement
        This is the first requirement.
        It has multiple lines.

        **Priority**: High

        ### RF-02: Second Requirement
        This is the second requirement.

        | Field | Value |
        |-------|-------|
        | Priority | Medium |

        ### RF-10: Tenth Requirement
        This requirement has a higher number.
        """
    )

    prd_file = tmp_path / "governance" / "prd.md"
    prd_file.parent.mkdir(parents=True, exist_ok=True)
    prd_file.write_text(prd_content)

    return prd_file


class TestExtractRequirements:
    """Tests for extract_requirements function."""

    def test_extract_from_valid_prd(self, tmp_prd_file: Path) -> None:
        """Should extract all requirements from valid PRD."""
        requirements = extract_requirements(
            tmp_prd_file, tmp_prd_file.parent.parent.parent.parent
        )

        assert len(requirements) == 3
        assert all(r.type == ConceptType.REQUIREMENT for r in requirements)

    def test_requirement_ids(self, tmp_prd_file: Path) -> None:
        """Should generate correct IDs from requirement numbers."""
        requirements = extract_requirements(tmp_prd_file)

        ids = [r.id for r in requirements]
        assert "req-rf-01" in ids
        assert "req-rf-02" in ids
        assert "req-rf-10" in ids

    def test_requirement_metadata(self, tmp_prd_file: Path) -> None:
        """Should extract requirement ID and title to metadata."""
        requirements = extract_requirements(tmp_prd_file)

        req = next(r for r in requirements if r.id == "req-rf-01")
        assert req.metadata["requirement_id"] == "RF-01"
        assert req.metadata["title"] == "First Requirement"

    def test_requirement_sections(self, tmp_prd_file: Path) -> None:
        """Should extract correct section headers."""
        requirements = extract_requirements(tmp_prd_file)

        req = next(r for r in requirements if r.id == "req-rf-02")
        assert req.section == "RF-02: Second Requirement"

    def test_requirement_content(self, tmp_prd_file: Path) -> None:
        """Should extract section content."""
        requirements = extract_requirements(tmp_prd_file)

        req = next(r for r in requirements if r.id == "req-rf-01")
        assert "first requirement" in req.content.lower()
        assert "multiple lines" in req.content.lower()

    def test_line_numbers(self, tmp_prd_file: Path) -> None:
        """Should track line numbers correctly."""
        requirements = extract_requirements(tmp_prd_file)

        # All requirements should have valid line ranges
        for req in requirements:
            start, end = req.lines
            assert start > 0
            assert end >= start

    def test_relative_file_path(self, tmp_prd_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_prd_file.parent.parent
        requirements = extract_requirements(tmp_prd_file, project_root)

        req = requirements[0]
        assert req.file == "governance/prd.md"

    def test_empty_file(self, tmp_path: Path) -> None:
        """Should return empty list for empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        requirements = extract_requirements(empty_file)
        assert requirements == []

    def test_missing_file(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        requirements = extract_requirements(missing_file)
        assert requirements == []

    def test_no_requirements(self, tmp_path: Path) -> None:
        """Should return empty list for file with no requirements."""
        no_reqs_file = tmp_path / "no_reqs.md"
        no_reqs_file.write_text(
            dedent(
                """
                # Document

                This document has no RF-XX requirements.

                ### Just a heading
                Not a requirement.
                """
            )
        )

        requirements = extract_requirements(no_reqs_file)
        assert requirements == []

    def test_special_characters_in_title(self, tmp_path: Path) -> None:
        """Should handle special characters in requirement titles."""
        prd_file = tmp_path / "special.md"
        prd_file.write_text(
            dedent(
                """
                ### RF-01: Requirement with (parentheses) & symbols!
                Content here.
                """
            )
        )

        requirements = extract_requirements(prd_file)
        assert len(requirements) == 1
        assert (
            requirements[0].metadata["title"]
            == "Requirement with (parentheses) & symbols!"
        )

    def test_content_truncation_by_lines(self, tmp_path: Path) -> None:
        """Should truncate content to ~20 lines."""
        long_content = "\n".join([f"Line {i}" for i in range(50)])
        prd_file = tmp_path / "long.md"
        prd_file.write_text(f"### RF-01: Long Requirement\n{long_content}")

        requirements = extract_requirements(prd_file)
        req = requirements[0]

        # Content should be truncated
        assert "Line 0" in req.content
        assert "Line 19" in req.content
        # But not include line 40+
        lines_in_content = req.content.count("\n")
        assert lines_in_content <= 21  # 20 lines + header line

    def test_content_truncation_by_chars(self, tmp_path: Path) -> None:
        """Should truncate content to 500 chars with ellipsis."""
        long_line = "x" * 600
        prd_file = tmp_path / "long_line.md"
        prd_file.write_text(f"### RF-01: Long Line\n{long_line}")

        requirements = extract_requirements(prd_file)
        req = requirements[0]

        assert len(req.content) <= 504  # 500 + "..."
        assert req.content.endswith("...")

    def test_file_path_outside_project_root(self, tmp_path: Path) -> None:
        """Should use file name when file is outside project root."""
        prd_file = tmp_path / "prd.md"
        prd_file.write_text("### RF-01: Test\nContent")

        # Pass a project_root that doesn't contain prd_file
        other_root = tmp_path / "different_root"
        other_root.mkdir()

        requirements = extract_requirements(prd_file, other_root)

        # Should fall back to file name
        assert requirements[0].file == "prd.md"

    def test_integration_with_real_prd(self) -> None:
        """Should extract requirements from real raise-cli PRD."""
        # This test verifies integration with actual project files
        prd_path = Path("governance/prd.md")

        if not prd_path.exists():
            pytest.skip("Real PRD file not found")

        requirements = extract_requirements(prd_path)

        # Should extract multiple requirements
        assert len(requirements) >= 8

        # Should have proper structure
        for req in requirements:
            assert req.id.startswith("req-rf-")
            assert req.type == ConceptType.REQUIREMENT
            assert "RF-" in req.metadata["requirement_id"]
            assert len(req.metadata["title"]) > 0
            assert len(req.content) > 0
