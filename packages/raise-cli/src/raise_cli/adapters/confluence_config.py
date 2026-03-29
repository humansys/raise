"""Confluence instance configuration.

Minimal Pydantic model for S1051.1. S1051.3 extends with routing,
labels, and multi-instance config loading from .raise/confluence.yaml.

RAISE-1054 (S1051.1)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConfluenceInstanceConfig(BaseModel):
    """Single Confluence instance connection config."""

    url: str = Field(..., description="Confluence base URL (e.g. https://x.atlassian.net/wiki)")
    username: str = Field(..., description="Atlassian account email")
    space_key: str = Field(..., description="Default space key")
    instance_name: str = Field(
        default="default",
        description="Instance identifier for token resolution",
    )
