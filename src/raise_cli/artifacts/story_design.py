"""Story-design artifact schema and governance validators."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from raise_cli.artifacts.models import ArtifactType, SkillArtifact


class Complexity(StrEnum):
    """Story complexity assessment."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class AcceptanceCriterion(BaseModel):
    """A single acceptance criterion."""

    id: str
    description: str
    verifiable: bool = True


class IntegrationPoint(BaseModel):
    """A codebase integration point affected by the story."""

    module: str
    change_type: str
    files: list[str] = Field(default_factory=list)


class Decision(BaseModel):
    """A design decision with rationale."""

    id: str
    choice: str
    rationale: str
    alternatives_considered: list[str] = Field(default_factory=list)


class StoryDesignContent(BaseModel):
    """Typed content for a story-design artifact.

    Governance rules are encoded as validators.
    """

    summary: str
    complexity: Complexity
    acceptance_criteria: list[AcceptanceCriterion] = Field(min_length=1, max_length=10)
    integration_points: list[IntegrationPoint] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    decisions: list[Decision] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def _validate_decisions_have_rationale(self) -> "StoryDesignContent":
        for decision in self.decisions:
            if not decision.rationale.strip():
                msg = f"Decision {decision.id}: rationale must not be empty"
                raise ValueError(msg)
        return self


class StoryDesignArtifact(SkillArtifact):
    """A story-design artifact with typed content."""

    artifact_type: Literal[ArtifactType.STORY_DESIGN] = ArtifactType.STORY_DESIGN  # pyright: ignore[reportIncompatibleVariableOverride]
    content: StoryDesignContent  # pyright: ignore[reportIncompatibleVariableOverride,reportGeneralTypeIssues]
