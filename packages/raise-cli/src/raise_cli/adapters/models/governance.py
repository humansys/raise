"""Governance schema boundary models.

Typed inputs and outputs for ``GovernanceSchemaProvider`` and
``GovernanceParser`` protocols.

Architecture: ADR-034 (Governance extensibility)
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CoreArtifactType(StrEnum):
    """Core governance artifact types.

    Protocols accept ``str`` — plugins are not restricted to this enum.
    Use these constants for built-in artifact types.
    """

    BACKLOG = "backlog"
    ADR = "adr"
    CONSTITUTION = "constitution"
    PRD = "prd"
    VISION = "vision"
    GUARDRAILS = "guardrails"
    GLOSSARY = "glossary"
    ROADMAP = "roadmap"
    EPIC_SCOPE = "epic_scope"


class ArtifactLocator(BaseModel):
    """Points to a governance artifact for parsing."""

    path: str = Field(..., description="Relative path from project root")
    artifact_type: str = Field(
        ..., description="Artifact type (CoreArtifactType or custom str)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific context"
    )
