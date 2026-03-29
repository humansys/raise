"""Confluence configuration — instance, routing, and multi-instance schema.

Models for .raise/confluence.yaml with loader function.
Supports full multi-instance and flat minimal formats.

RAISE-1054 (S1051.1), RAISE-1056 (S1051.3)
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


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
    routing: dict[str, ArtifactRouting] = Field(
        default_factory=dict,
        description="Artifact type → routing config (parent page + labels)",
    )


class ConfluenceConfig(BaseModel):
    """Root config — multi-instance with default.

    Supports two formats:
    1. Full: {default_instance: "name", instances: {name: {...}}}
    2. Flat: {url, username, space_key} → auto-normalized to single "default" instance
    """

    default_instance: str = Field(default="default")
    instances: dict[str, ConfluenceInstanceConfig]

    @model_validator(mode="after")
    def _validate_default_exists(self) -> ConfluenceConfig:
        if self.default_instance not in self.instances:
            msg = (
                f"default_instance '{self.default_instance}' not found in instances "
                f"(available: {', '.join(self.instances)})"
            )
            raise ValueError(msg)
        return self

    def get_instance(self, name: str | None = None) -> ConfluenceInstanceConfig:
        """Get instance by name, or default."""
        target = name or self.default_instance
        if target not in self.instances:
            msg = f"Confluence instance '{target}' not found (available: {', '.join(self.instances)})"
            raise KeyError(msg)
        return self.instances[target]

    def resolve_routing(
        self, artifact_type: str, instance: str | None = None
    ) -> ArtifactRouting | None:
        """Resolve routing for artifact type on instance. Returns None if not configured."""
        inst = self.get_instance(instance)
        return inst.routing.get(artifact_type)
