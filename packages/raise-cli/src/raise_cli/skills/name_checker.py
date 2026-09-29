"""Skill name checker for ontology compliance.

Checks proposed skill names against:
- {domain}-{action} naming pattern
- Existing skill conflicts
- CLI command conflicts (PAT-132)
- Known lifecycle domains
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from raise_cli.skills.locator import SkillLocator, get_default_skill_dir

# Pattern for {domain}-{action} naming convention
NAMING_PATTERN = re.compile(r"^[a-z]+-[a-z]+(-[a-z]+)*$")

# RaiSE namespace prefix for distributed skills
RAI_PREFIX = "rai-"

# Known lifecycle domains
KNOWN_LIFECYCLES = {
    "session",
    "epic",
    "story",
    "discover",
    "skill",
    "research",
    "debug",
    "framework",
    "project",
    "docs",
}

# CLI commands that conflict with skill names (PAT-132)
# Format: {domain: [actions]} for {domain}-{action} pattern
CLI_COMMANDS = {
    "memory": ["build", "query", "emit-pattern", "emit-calibration"],
    "skill": ["list", "validate", "scaffold", "check-name"],
    "profile": ["show", "update"],
    "session": ["start", "close"],
    "discover": ["scan", "drift", "status"],
    "init": [],  # init is a standalone command
}


class NameCheckResult(BaseModel):
    """Result of checking a skill name."""

    name: str = Field(description="The name that was checked")
    valid_pattern: bool = Field(description="Whether name follows {domain}-{action}")
    no_skill_conflict: bool = Field(
        description="Whether no existing skill has this name"
    )
    no_cli_conflict: bool = Field(description="Whether no CLI command has this name")
    known_lifecycle: bool = Field(description="Whether domain is a known lifecycle")
    conflicting_skill: str | None = Field(
        default=None, description="Name of conflicting skill if any"
    )
    conflicting_command: str | None = Field(
        default=None, description="CLI command that conflicts if any"
    )
    suggestions: list[str] = Field(
        default_factory=lambda: [], description="Positioning suggestions"
    )

    @property
    def is_valid(self) -> bool:
        """Name is valid if pattern OK, no skill conflict, and no CLI conflict."""
        return self.valid_pattern and self.no_skill_conflict and self.no_cli_conflict


def _check_pattern(name: str) -> bool:
    """Check if name follows {domain}-{action} pattern."""
    return bool(NAMING_PATTERN.match(name))


def _check_skill_conflict(
    name: str, existing_names: set[str]
) -> tuple[bool, str | None]:
    """Check for conflict with existing skills."""
    if name in existing_names:
        return False, name
    return True, None


def _check_cli_conflict(name: str) -> tuple[bool, str | None]:
    """Check for conflict with CLI commands."""
    parts = name.split("-")
    if len(parts) < 2:
        return True, None

    domain = parts[0]
    action = "-".join(parts[1:])  # Handle multi-part actions like "emit-pattern"

    # Check if this matches a CLI command
    if domain in CLI_COMMANDS:
        cli_actions = CLI_COMMANDS[domain]
        if action in cli_actions:
            return False, f"{domain} {action}"
        # Also check if domain alone is a command (like "init")
        if not cli_actions and domain == name:
            return False, domain

    return True, None


def _strip_rai_prefix(name: str) -> str:
    """Strip rai- namespace prefix if present."""
    if name.startswith(RAI_PREFIX):
        return name[len(RAI_PREFIX) :]
    return name


def _check_lifecycle(name: str) -> bool:
    """Check if domain is a known lifecycle."""
    unprefixed = _strip_rai_prefix(name)
    parts = unprefixed.split("-")
    if parts:
        domain = parts[0]
        return domain in KNOWN_LIFECYCLES
    return False


def _get_suggestions(
    name: str, existing_skills: list[str], known_lifecycle: bool
) -> list[str]:
    """Generate positioning suggestions."""
    suggestions: list[str] = []

    unprefixed = _strip_rai_prefix(name)
    parts = unprefixed.split("-")
    if len(parts) < 2:
        return suggestions

    domain = parts[0]

    # Find related skills in same domain (check both prefixed and unprefixed)
    related = sorted(
        [s for s in existing_skills if _strip_rai_prefix(s).startswith(f"{domain}-")]
    )

    if related:
        # Suggest positioning relative to existing skills
        if known_lifecycle:
            suggestions.append(f"Related {domain} skills: {', '.join(related)}")
    elif known_lifecycle:
        suggestions.append(f"First skill in '{domain}' lifecycle")

    if not known_lifecycle:
        suggestions.append(
            f"Domain '{domain}' is not a standard lifecycle "
            f"(known: {', '.join(sorted(KNOWN_LIFECYCLES))})"
        )

    return suggestions


def check_name(name: str) -> NameCheckResult:
    """Check a proposed skill name against ontology patterns.

    Args:
        name: Proposed skill name.

    Returns:
        NameCheckResult with validation results and suggestions.
    """
    # Check pattern
    valid_pattern = _check_pattern(name)

    # Get existing skills
    skill_dir = get_default_skill_dir()
    locator = SkillLocator(skill_dir)
    existing_skills = locator.find_skill_dirs()
    existing_names = {s.name for s in existing_skills}

    # Check conflicts
    no_skill_conflict, conflicting_skill = _check_skill_conflict(name, existing_names)
    no_cli_conflict, conflicting_command = _check_cli_conflict(name)

    # Check lifecycle
    known_lifecycle = _check_lifecycle(name)

    # Generate suggestions
    suggestions = _get_suggestions(name, sorted(existing_names), known_lifecycle)

    return NameCheckResult(
        name=name,
        valid_pattern=valid_pattern,
        no_skill_conflict=no_skill_conflict,
        no_cli_conflict=no_cli_conflict,
        known_lifecycle=known_lifecycle,
        conflicting_skill=conflicting_skill,
        conflicting_command=conflicting_command,
        suggestions=suggestions,
    )
