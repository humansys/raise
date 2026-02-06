"""Tests for skill validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.skills.validator import (
    ValidationResult,
    ValidationSeverity,
    validate_skill,
    validate_skill_file,
)


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
        """A well-formed skill passes validation."""
        skill_content = """\
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

## Context

When to use this skill.

## Steps (1)

### Step 1: Do something

Do the thing.

## Output

What this produces.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert result.is_valid
        assert result.error_count == 0

    def test_missing_required_field_name(self, tmp_path: Path) -> None:
        """Missing name field is an error."""
        skill_content = """\
---
description: Some description.

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("name" in e.lower() for e in result.errors)

    def test_missing_required_field_description(self, tmp_path: Path) -> None:
        """Missing description field is an error."""
        skill_content = """\
---
name: test-skill

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("description" in e.lower() for e in result.errors)

    def test_missing_metadata(self, tmp_path: Path) -> None:
        """Missing metadata section is an error."""
        skill_content = """\
---
name: test-skill
description: Test description.
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("metadata" in e.lower() for e in result.errors)

    def test_missing_required_section(self, tmp_path: Path) -> None:
        """Missing required section (Purpose, Context, Steps, Output) is an error."""
        skill_content = """\
---
name: test-skill
description: Test description.

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Output

Test output.
"""
        # Missing Steps section
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        assert not result.is_valid
        assert any("steps" in e.lower() for e in result.errors)

    def test_invalid_naming_convention(self, tmp_path: Path) -> None:
        """Name not following {domain}-{action} pattern is a warning."""
        skill_content = """\
---
name: badname
description: Test description.

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        # Invalid naming is a warning, not error
        assert result.is_valid
        assert any("naming" in w.lower() or "pattern" in w.lower() for w in result.warnings)

    def test_hook_path_not_found(self, tmp_path: Path) -> None:
        """Hook referencing non-existent script is a warning."""
        skill_content = """\
---
name: test-skill
description: Test description.

metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "/nonexistent/script.sh"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        result = validate_skill_file(skill_file)

        # Hook path not found is a warning (script may exist elsewhere)
        assert any("hook" in w.lower() or "script" in w.lower() for w in result.warnings)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Non-existent file returns error."""
        result = validate_skill_file(tmp_path / "nonexistent.md")

        assert not result.is_valid
        assert any("not found" in e.lower() for e in result.errors)

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

        skill_content = """\
---
name: test-action
description: Test description.

metadata:
  raise.work_cycle: utility
  raise.version: "1.0.0"
---

# Test

## Purpose

Test purpose.

## Context

Test context.

## Steps (1)

Test steps.

## Output

Test output.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill(skill_file)
        result = validate_skill(skill)

        assert result.is_valid
