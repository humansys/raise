"""Typed models for impact analysis reports."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ImpactConfidence = Literal["high", "medium", "low"]
GateId = Literal[
    "gate-tests",
    "gate-lint",
    "gate-types",
    "gate-format",
    "release-check",
]
ValidationScope = Literal["file", "app", "repo", "full-release"]
FileCategory = Literal[
    "source",
    "test",
    "docs",
    "config",
    "lockfile",
    "ci",
    "governance",
    "unknown",
]


class ChangedFileImpact(BaseModel):
    """Impact classification for one changed repository path."""

    path: str
    owner_app: str | None = None
    owner_path: str | None = None
    category: FileCategory = "unknown"
    high_risk: bool = False
    reasons: list[str] = Field(default_factory=list)


class RecommendedGate(BaseModel):
    """Validation gate recommendation derived from impact analysis."""

    gate_id: GateId
    scope: ValidationScope
    path: str | None = None
    reason: str


class FullRunReason(BaseModel):
    """Stable reason for broadening validation beyond local/app scope."""

    code: str
    message: str
    paths: list[str] = Field(default_factory=list)


class AffectedApp(BaseModel):
    """Manifest-owned app/package affected by a change."""

    name: str
    path: str
    direct_files: list[str] = Field(default_factory=list)
    inferred: bool = False
    reasons: list[str] = Field(default_factory=list)


class GraphImpactContext(BaseModel):
    """Optional graph context; explanatory only, never a skip oracle."""

    modules: list[str] = Field(default_factory=list)
    docs: list[str] = Field(default_factory=list)
    stories: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ImpactReport(BaseModel):
    """Top-level advisory impact report."""

    base_ref: str
    head_ref: str
    changed_files: list[ChangedFileImpact] = Field(default_factory=list)
    affected_apps: list[AffectedApp] = Field(default_factory=list)
    recommended_gates: list[RecommendedGate] = Field(default_factory=list)
    full_run_reasons: list[FullRunReason] = Field(default_factory=list)
    confidence: ImpactConfidence = "high"
    graph_context: GraphImpactContext | None = None
    advisory_only: bool = True


class OwnershipReport(BaseModel):
    """Manifest ownership classification for changed files."""

    files: list[ChangedFileImpact] = Field(default_factory=list)
    affected_apps: list[AffectedApp] = Field(default_factory=list)
