"""Cross-cutting adapter health model.

Shared by all adapter types for health check reporting.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdapterHealth(BaseModel):
    """Health check result for an adapter."""

    name: str = Field(..., description="Adapter name (e.g., 'jira')")
    healthy: bool = Field(..., description="Whether the adapter is healthy")
    message: str = Field(default="", description="Status or error message")
    latency_ms: int | None = Field(
        default=None, description="Response latency in milliseconds"
    )
