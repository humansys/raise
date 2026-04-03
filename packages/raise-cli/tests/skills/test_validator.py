"""Tests for skill validator."""

from __future__ import annotations

from pathlib import Path

from raise_cli.skills.validator import (
    REQUIRED_SECTIONS,
    ValidationResult,
    validate_skill,
    validate_skill_file,
)

# Full ADR-040 compliant skill fixture (7 sections)
COMPLIANT_SKILL = """\
---
name: session-start
description: Begin a session by loading memory.

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---

# Session Start

## Purpose

Load context and propose work.

## Mastery Levels (ShuHaRi)

- **Shu**: Full explanation
- **Ha**: Brief
- **Ri**: Minimal

## Context

When to use this skill.

## Steps

### Step 1: Do something

Do the thing.

## Output

What this produces.

## Quality Checklist

- [ ] Check 1
- [ ] Check 2

## References

- Link 1
"""


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_is_valid_when_no_errors(self) -> None:
        """A result with only warnings is valid."""
        result = ValidationResult(
            path="test.md",
            errors=[],
            warnings=["Minor issue"],
        )
        assert result.is_valid is True

    def test_is_valid_when_errors_exist(self) -> None:
        """A result with errors is not valid."""
        result = ValidationResult(
            path="test.md",
            errors=["Missing field"],
            warnings=[],
        )
        assert result.is_valid is False

    def test_error_count(self) -> None:
        """Error count matches errors list length."""
        result = ValidationResult(
            path="test.md",
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        assert result.error_count == 2
        assert result.warning_count == 1


class TestValidateSkillFile:
    """Tests for validate_skill_file function."""

    def test_valid_skill(self, tmp_path: Path) -> None:
        """A well-formed skill with all 7 ADR-040 sections passes validation."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(COMPLIANT_SKILL)

        result = validate_skill_file(skill_file)

        assert result.is_valid
        assert result.error_count == 0

    def test_missing_required_field_name(self, tmp_path: Path) -> None:
        """Missing name field is an error."""
        skill_content = COMPLIANT_SKILL.replace("name: session-start\n", "")
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("name" in e.lower() for e in result.errors)

    def test_missing_required_field_description(self, tmp_path: Path) -> None:
        """Missing description field is an error."""
        skill_content = COMPLIANT_SKILL.replace(
            "description: Begin a session by loading memory.\n", ""
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("description" in e.lower() for e in result.errors)

    def test_missing_metadata(self, tmp_path: Path) -> None:
        """Missing metadata section is an error."""
        skill_content = COMPLIANT_SKILL.replace(
            '\nmetadata:\n  raise.work_cycle: session\n  raise.version: "1.0.0"\n',
            "\n",
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("metadata" in e.lower() for e in result.errors)

    def test_missing_required_section(self, tmp_path: Path) -> None:
        """Missing required section is an error."""
        # Remove Steps section
        skill_content = COMPLIANT_SKILL.replace(
            "## Steps\n\n### Step 1: Do something\n\nDo the thing.\n\n", ""
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("steps" in e.lower() for e in result.errors)

    def test_invalid_naming_convention(self, tmp_path: Path) -> None:
        """Name not following {domain}-{action} pattern is a warning."""
        skill_content = COMPLIANT_SKILL.replace("name: session-start", "name: badname")
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        # Invalid naming is a warning, not error
        assert result.is_valid
        assert any(
            "naming" in w.lower() or "pattern" in w.lower() for w in result.warnings
        )

    def test_hook_path_not_found(self, tmp_path: Path) -> None:
        """Hook referencing non-existent script is a warning."""
        skill_content = COMPLIANT_SKILL.replace(
            'metadata:\n  raise.work_cycle: session\n  raise.version: "1.0.0"',
            'metadata:\n  raise.work_cycle: session\n  raise.version: "1.0.0"\n\nhooks:\n  Stop:\n    - hooks:\n        - type: command\n          command: "/nonexistent/script.sh"',
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        # Hook path not found is a warning (script may exist elsewhere)
        assert any(
            "hook" in w.lower() or "script" in w.lower() for w in result.warnings
        )

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Non-existent file returns error."""
        result = validate_skill_file(tmp_path / "nonexistent.md")

        assert not result.is_valid
        assert any("not found" in e.lower() for e in result.errors)

    def test_pydantic_validation_error_surfaces_as_error(self, tmp_path: Path) -> None:
        """ValidationError during Pydantic model construction returns error, not unhandled exception."""
        # metadata has work_cycle but missing version (required field) — valid YAML, invalid schema
        skill_content = """\
---
name: session-start
description: Test skill.
metadata:
  raise.work_cycle: session
---

# Test
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any(
            "schema" in e.lower() or "validation" in e.lower() for e in result.errors
        )

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        """Invalid YAML frontmatter returns error."""
        skill_content = """\
---
name: [invalid yaml
description: Test
---

# Test
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("yaml" in e.lower() or "parse" in e.lower() for e in result.errors)


class TestValidateSkill:
    """Tests for validate_skill function (from Skill object)."""

    def test_validate_parsed_skill(self, tmp_path: Path) -> None:
        """Can validate an already-parsed Skill object."""
        from raise_cli.skills.parser import parse_skill

        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(COMPLIANT_SKILL)

        skill = parse_skill(skill_file)
        result = validate_skill(skill)

        assert result.is_valid


class TestADR040Contract:
    """Tests for ADR-040 contract compliance checks."""

    def test_required_sections_includes_all_seven(self) -> None:
        """REQUIRED_SECTIONS contains all 7 ADR-040 canonical sections."""
        expected = {
            "Purpose",
            "Mastery Levels",
            "Context",
            "Steps",
            "Output",
            "Quality Checklist",
            "References",
        }
        assert set(REQUIRED_SECTIONS) == expected

    def test_mastery_levels_with_shuhari_suffix(self, tmp_path: Path) -> None:
        """'## Mastery Levels (ShuHaRi)' satisfies the Mastery Levels requirement."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(COMPLIANT_SKILL)

        result = validate_skill_file(skill_file)

        assert result.is_valid
        assert not any("mastery" in e.lower() for e in result.errors)

    def test_missing_mastery_levels_is_error(self, tmp_path: Path) -> None:
        """Missing Mastery Levels section is an error."""
        skill_content = COMPLIANT_SKILL.replace(
            "## Mastery Levels (ShuHaRi)\n\n- **Shu**: Full explanation\n- **Ha**: Brief\n- **Ri**: Minimal\n\n",
            "",
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("mastery levels" in e.lower() for e in result.errors)

    def test_missing_quality_checklist_is_error(self, tmp_path: Path) -> None:
        """Missing Quality Checklist section is an error."""
        skill_content = COMPLIANT_SKILL.replace(
            "## Quality Checklist\n\n- [ ] Check 1\n- [ ] Check 2\n\n", ""
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("quality checklist" in e.lower() for e in result.errors)

    def test_missing_references_is_error(self, tmp_path: Path) -> None:
        """Missing References section is an error."""
        skill_content = COMPLIANT_SKILL.replace("## References\n\n- Link 1\n", "")
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("references" in e.lower() for e in result.errors)

    def test_line_count_warning_over_150(self, tmp_path: Path) -> None:
        """Skills with body over 150 lines get a warning."""
        # Add enough lines to exceed 150
        padding = "\n".join(f"Line {i}" for i in range(160))
        skill_content = COMPLIANT_SKILL.replace(
            "- Link 1\n", f"- Link 1\n\n{padding}\n"
        )
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert any("150" in w or "line" in w.lower() for w in result.warnings)

    def test_line_count_under_150_no_warning(self, tmp_path: Path) -> None:
        """Skills with body under 150 lines get no line count warning."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(COMPLIANT_SKILL)

        result = validate_skill_file(skill_file)

        assert not any("line" in w.lower() for w in result.warnings)
