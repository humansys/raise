"""Pydantic models for structured story lifecycle artifacts.

Each skill execution produces one artifact with typed, validated content.
The LLM provides values via MCP tool; the system serializes and persists.

Architecture: ADR-066 (Construction-Time Artifact Validation)
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ArtifactBase(BaseModel):
    """Base for all artifact types — carries schema_version for additive evolution."""

    model_config = ConfigDict(frozen=True)
    schema_version: int = 1


class ComponentRef(BaseModel):
    """A file or module affected by a story."""

    model_config = ConfigDict(frozen=True)
    name: str
    change: Literal["create", "modify", "delete"]
    purpose: str


class AcceptanceCriterion(BaseModel):
    """A single testable acceptance criterion."""

    model_config = ConfigDict(frozen=True)
    id: str
    description: str
    verifiable: bool = True
    test_link: str | None = None
    severity: Literal["must", "should", "must_not"] = "must"


class Decision(BaseModel):
    """An architectural or design decision with rationale."""

    model_config = ConfigDict(frozen=True)
    id: str
    title: str
    rationale: str
    body: str = ""


class Example(BaseModel):
    """A concrete code example from a design document."""

    model_config = ConfigDict(frozen=True)
    title: str
    language: str = "python"
    code: str
    explanation: str = ""


class DriftRisk(BaseModel):
    """An architectural drift risk assessment entry."""

    model_config = ConfigDict(frozen=True)
    id: str
    description: str
    mitigation: str = ""


class VerificationScenario(BaseModel):
    """A testing strategy entry from a design document."""

    model_config = ConfigDict(frozen=True)
    layer: str
    name: str
    purpose: str


class Dependency(BaseModel):
    """A dependency that blocks or gates work."""

    model_config = ConfigDict(frozen=True)
    description: str
    blocks: str = ""


class DesignArtifact(ArtifactBase):
    """Output of rai-story-design — problem, approach, components, AC."""

    problem: str
    value: str
    approach: str
    components: list[ComponentRef]
    decisions: list[Decision]
    acceptance_criteria: list[AcceptanceCriterion]
    examples: list[Example] = []
    complexity: Literal["simple", "moderate", "complex"] | None = None
    dependencies: list[Dependency] = []
    legacy_sweep: str = ""
    drift_risks: list[DriftRisk] = []
    testing_strategy: list[VerificationScenario] = []
    open_questions: list[str] = []


class PlanArtifact(ArtifactBase):
    """Output of rai-story-plan — task decomposition with ordering."""

    tasks: list[dict[str, Any]]
    risk_order: list[str] = []
    estimated_points: int | None = None


class ImplementArtifact(ArtifactBase):
    """Output of rai-story-implement — files changed and tests added."""

    files_changed: list[str]
    tests_added: list[str]
    coverage_percent: float | None = None


class ReviewArtifact(ArtifactBase):
    """Output of rai-architecture-review or rai-quality-review."""

    review_type: Literal["architecture", "quality"]
    findings: list[dict[str, Any]]
    verdict: Literal["approved", "needs_changes", "rejected"]


class RetroArtifact(ArtifactBase):
    """Output of rai-story-review — patterns, reinforcements, velocity."""

    patterns_learned: list[str]
    reinforcements: list[str]
    velocity_ratio: float | None = None
    notes: str = ""


ARTIFACT_TYPES: dict[str, type[ArtifactBase]] = {
    "design": DesignArtifact,
    "plan": PlanArtifact,
    "implement": ImplementArtifact,
    "review": ReviewArtifact,
    "retro": RetroArtifact,
}
