"""Pydantic models for SKILL.md frontmatter and structure.

These models define the schema for RaiSE skills, enabling:
- Parsing of SKILL.md YAML frontmatter
- Validation of skill structure
- Type-safe access to skill metadata
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata for a RaiSE skill.

    Maps from YAML frontmatter with 'raise.' prefix to clean attributes.
    """

    work_cycle: str = Field(
        description="Lifecycle: session, epic, story, discovery, utility, meta"
    )
    version: str = Field(description="Semantic version of the skill")
    frequency: str | None = Field(
        default=None, description="How often invoked: per-session, per-epic, etc."
    )
    fase: str | None = Field(default=None, description="Phase number or 'meta'")
    prerequisites: str | None = Field(
        default=None, description="Skills that must run before this one"
    )
    next: str | None = Field(
        default=None, description="Skill that typically follows this one"
    )
    gate: str | None = Field(default=None, description="Validation gate for this skill")
    adaptable: bool = Field(
        default=True, description="Whether skill can be adapted by mastery level"
    )
    output_type: str | None = Field(
        default=None,
        description="Artifact type this skill produces (e.g., story-design)",
    )

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> SkillMetadata:
        """Parse metadata from raw YAML dict with 'raise.' prefix.

        Args:
            raw: Dictionary with keys like 'raise.work_cycle', 'raise.version', etc.

        Returns:
            SkillMetadata instance with cleaned attributes.
        """
        # Strip 'raise.' prefix and convert to clean dict
        cleaned: dict[str, Any] = {}
        for key, value in raw.items():
            if key.startswith("raise."):
                clean_key = key[6:]  # Remove 'raise.' prefix
                # Handle boolean conversion
                if clean_key == "adaptable" and isinstance(value, str):
                    value = value.lower() == "true"
                cleaned[clean_key] = value

        return cls(**cleaned)


class SkillHookCommand(BaseModel):
    """A single hook command in a skill."""

    type: str = Field(description="Hook type: 'command'")
    command: str = Field(description="Shell command to execute")


class SkillHook(BaseModel):
    """A hook configuration with nested commands."""

    hooks: list[SkillHookCommand] = Field(
        default_factory=lambda: [], description="List of hook commands"
    )


class SkillFrontmatter(BaseModel):
    """YAML frontmatter for a SKILL.md file.

    This is the structured data at the top of each skill file,
    containing name, description, metadata, and hooks.
    """

    name: str = Field(description="Skill name in {domain}-{action} format")
    description: str = Field(description="Brief description of the skill")
    license: str | None = Field(default=None, description="License (typically MIT)")
    metadata: SkillMetadata | None = Field(
        default=None, description="RaiSE-specific metadata"
    )
    hooks: dict[str, list[SkillHook]] | None = Field(
        default=None, description="Claude Code hooks (e.g., Stop)"
    )


class Skill(BaseModel):
    """A complete RaiSE skill with frontmatter and markdown body.

    Represents a parsed SKILL.md file with all its components.
    """

    frontmatter: SkillFrontmatter = Field(description="Parsed YAML frontmatter")
    body: str = Field(description="Markdown content after frontmatter")
    path: str = Field(description="Path to the SKILL.md file")

    @property
    def name(self) -> str:
        """Shortcut to skill name."""
        return self.frontmatter.name

    @property
    def version(self) -> str | None:
        """Skill version from metadata, or None if no metadata."""
        if self.frontmatter.metadata:
            return self.frontmatter.metadata.version
        return None

    @property
    def lifecycle(self) -> str | None:
        """Skill lifecycle from metadata work_cycle."""
        if self.frontmatter.metadata:
            return self.frontmatter.metadata.work_cycle
        return None

    @property
    def description(self) -> str:
        """Shortcut to skill description."""
        return self.frontmatter.description
