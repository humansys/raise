"""Pydantic models for graph backend boundaries.

Architecture: ADR-036 (KnowledgeGraphBackend)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BackendHealth(BaseModel):
    """Health check result for a graph backend."""

    status: str = Field(..., description="'healthy', 'degraded', or 'unavailable'")
    message: str = Field(default="", description="Human-readable status detail")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific diagnostics"
    )
