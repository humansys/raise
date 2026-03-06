"""Validator for SKILL.md files.

Validates skill structure against ADR-040 contract including:
- Required fields (name, description, metadata)
- Required sections (7 canonical: Purpose through References)
- Line count target (≤150 body lines)
- Naming conventions ({domain}-{action})
- Hook paths (warns if script not found)
"""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from raise_cli.skills.parser import ParseError, parse_skill
from raise_cli.skills.schema import Skill


class ValidationSeverity(Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"


class ValidationResult(BaseModel):
    """Result of validating a skill file."""

    path: str = Field(description="Path to the validated file")
    errors: list[str] = Field(
        default_factory=lambda: [], description="Validation errors"
    )
    warnings: list[str] = Field(
        default_factory=lambda: [], description="Validation warnings"
    )

    @property
    def is_valid(self) -> bool:
        """Skill is valid if there are no errors (warnings OK)."""
        return len(self.errors) == 0

    @property
    def error_count(self) -> int:
        """Number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Number of warnings."""
        return len(self.warnings)


# ADR-040 canonical sections (7, fixed order)
REQUIRED_SECTIONS = [
    "Purpose",
    "Mastery Levels",
    "Context",
    "Steps",
    "Output",
    "Quality Checklist",
    "References",
]

# ADR-040 line count target for skill body
MAX_BODY_LINES = 150

# Pattern for {domain}-{action} naming convention
NAMING_PATTERN = re.compile(r"^[a-z]+-[a-z]+(-[a-z]+)*$")


def _validate_required_fields(skill: Skill, errors: list[str]) -> None:
    """Check required frontmatter fields."""
    if not skill.frontmatter.name:
        errors.append("Missing required field: name")

    if not skill.frontmatter.description:
        errors.append("Missing required field: description")

    if not skill.frontmatter.metadata:
        errors.append("Missing required field: metadata")


def _validate_required_sections(skill: Skill, errors: list[str]) -> None:
    """Check required sections in body (ADR-040: 7 canonical sections)."""
    body_lower = skill.body.lower()

    for section in REQUIRED_SECTIONS:
        # Match "## Section" with optional suffix (e.g., "## Mastery Levels (ShuHaRi)")
        pattern = f"## {section.lower()}"
        if pattern not in body_lower:
            errors.append(f"Missing required section: {section}")


def _validate_line_count(skill: Skill, warnings: list[str]) -> None:
    """Warn if skill body exceeds ADR-040 line count target."""
    body_lines = len(skill.body.strip().splitlines())
    if body_lines > MAX_BODY_LINES:
        warnings.append(f"Body has {body_lines} lines (target: ≤{MAX_BODY_LINES})")


def _validate_naming_convention(skill: Skill, warnings: list[str]) -> None:
    """Check naming follows {domain}-{action} pattern."""
    name = skill.frontmatter.name
    if name and not NAMING_PATTERN.match(name):
        warnings.append(
            f"Name '{name}' doesn't follow {{domain}}-{{action}} pattern (e.g., session-start)"
        )


def _validate_hook_paths(skill: Skill, warnings: list[str]) -> None:
    """Check that hook script paths exist (warning only)."""
    if not skill.frontmatter.hooks:
        return

    for hook_name, hook_list in skill.frontmatter.hooks.items():
        for hook in hook_list:
            for cmd in hook.hooks:
                # Extract script path from command
                # Handles: "RAISE_SKILL_NAME=x \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/script.sh"
                # Also handles: "/absolute/path/script.sh"
                command = cmd.command

                # Skip variable-based paths (we can't resolve them)
                if "$" in command:
                    continue

                # Check if command looks like a path
                if command.startswith("/"):
                    path = Path(command.split()[0])  # Get first word (the path)
                    if not path.exists():
                        warnings.append(f"Hook '{hook_name}' script not found: {path}")


def validate_skill(skill: Skill) -> ValidationResult:
    """Validate a parsed Skill object.

    Args:
        skill: Parsed Skill object.

    Returns:
        ValidationResult with errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    _validate_required_fields(skill, errors)
    _validate_required_sections(skill, errors)
    _validate_line_count(skill, warnings)
    _validate_naming_convention(skill, warnings)
    _validate_hook_paths(skill, warnings)

    return ValidationResult(
        path=skill.path,
        errors=errors,
        warnings=warnings,
    )


def validate_skill_file(path: str | Path) -> ValidationResult:
    """Validate a SKILL.md file.

    Args:
        path: Path to the SKILL.md file.

    Returns:
        ValidationResult with errors and warnings.
    """
    path = Path(path)
    str_path = str(path)

    # Check file exists
    if not path.exists():
        return ValidationResult(
            path=str_path,
            errors=[f"File not found: {path}"],
        )

    # Try to parse
    try:
        skill = parse_skill(path)
    except ParseError as e:
        return ValidationResult(
            path=str_path,
            errors=[f"Parse error: {e}"],
        )
    except ValidationError as e:
        return ValidationResult(
            path=str_path,
            errors=[f"Schema error: {e}"],
        )

    # Validate the parsed skill
    return validate_skill(skill)
