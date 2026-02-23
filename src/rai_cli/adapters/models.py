"""Pydantic models for adapter boundaries.

Shared data types consumed by adapter Protocols. These models define
the contracts at integration boundaries — what goes in and comes out
of adapters regardless of their concrete implementation.

Architecture: ADR-033 (Open-core adapter architecture), ADR-034 (Governance extensibility)
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


class IssueSpec(BaseModel):
    """Specification for creating a PM issue."""

    summary: str = Field(..., description="Issue title")
    description: str = Field(default="", description="Issue body (markdown)")
    issue_type: str = Field(default="Task", description="Issue type name")
    labels: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="PM-specific fields"
    )


class IssueRef(BaseModel):
    """Reference to an existing PM issue."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    url: str = Field(default="", description="Web URL to the issue")
    metadata: dict[str, Any] = Field(default_factory=dict)


class PublishResult(BaseModel):
    """Result of publishing documentation."""

    success: bool = Field(..., description="Whether publish succeeded")
    url: str = Field(default="", description="URL of published content")
    message: str = Field(default="", description="Status or error message")


class BackendHealth(BaseModel):
    """Health check result for a graph backend."""

    status: str = Field(
        ..., description="'healthy', 'degraded', or 'unavailable'"
    )
    message: str = Field(default="", description="Human-readable status detail")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific diagnostics"
    )
