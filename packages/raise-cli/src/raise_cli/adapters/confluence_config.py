"""Confluence configuration — instance, routing, and multi-instance schema.

Models for .raise/confluence.yaml with loader function.
Supports full multi-instance and flat minimal formats.

RAISE-1054 (S1051.1), RAISE-1056 (S1051.3)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArtifactRouting(BaseModel):
    """Routing config for one artifact type (e.g. adr, roadmap)."""

    parent_title: str = Field(..., description="Parent page title to publish under")
    labels: list[str] = Field(default_factory=list, description="Labels to apply on publish")


class ConfluenceInstanceConfig(BaseModel):
    """Single Confluence instance connection config."""

    url: str = Field(..., description="Confluence base URL (e.g. https://x.atlassian.net/wiki)")
    username: str = Field(..., description="Atlassian account email")
    space_key: str = Field(..., description="Default space key")
    instance_name: str = Field(
        default="default",
        description="Instance identifier for token resolution",
    )
