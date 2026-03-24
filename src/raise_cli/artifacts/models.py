"""Pydantic models for typed skill artifacts."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(StrEnum):
    """Types of skill artifacts.

    Each value corresponds to a skill's output type declared
    in SKILL.md frontmatter as ``raise.output_type``.
    """

    STORY_DESIGN = "story-design"


class ArtifactRefs(BaseModel):
    """References from an artifact to external items."""

    backlog_item: str | None = None
    epic_scope: str | None = None
    related_artifacts: list[str] = Field(default_factory=list)


class SkillArtifact(BaseModel):
    """Base artifact produced by a skill execution.

    Subclasses replace ``content`` with a typed model for
    specific artifact types (e.g., StoryDesignContent).
    """

    artifact_type: ArtifactType
    version: int = Field(default=1, ge=1)
    skill: str
    created: datetime
    story: str | None = None
    epic: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    refs: ArtifactRefs = Field(default_factory=ArtifactRefs)
    metadata: dict[str, Any] = Field(default_factory=dict)
