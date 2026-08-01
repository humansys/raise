"""Client-side Pydantic models for the cartridge server API (S5877.4).

Mirrors raise-server schemas/cartridge.py — decoupled to avoid cross-package imports.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CartridgeNodePayload(BaseModel):
    """A graph node to publish as part of a cartridge."""

    node_id: str = Field(min_length=1)
    node_type: str = Field(min_length=1)
    scope: str = Field(default="project", max_length=20)
    content: str = Field(min_length=1)
    source_file: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class CartridgeEdgePayload(BaseModel):
    """A graph edge to publish as part of a cartridge."""

    source_node_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    edge_type: str = Field(min_length=1)
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


class PublishRequest(BaseModel):
    """Payload to publish a cartridge to the server registry."""

    cartridge_name: str = Field(min_length=1, max_length=255)
    project_id: str = Field(min_length=1)
    nodes: list[CartridgeNodePayload]
    edges: list[CartridgeEdgePayload] = Field(default_factory=list)
    visibility: Literal["private", "public"] = "private"


class CartridgeInstallResult(BaseModel):
    """Response after publishing a cartridge."""

    cartridge_name: str
    nodes_inserted: int
    edges_inserted: int
    visibility: str | None = None
    org_plan: str | None = None


class CartridgeInfo(BaseModel):
    """Summary of an installed cartridge (list endpoint)."""

    cartridge_name: str
    node_count: int


class CartridgeNodeResult(BaseModel):
    """A single node returned from the server."""

    node_id: str
    node_type: str
    scope: str
    content: str
    source_file: str | None
    properties: dict[str, Any]


class CartridgeDetail(BaseModel):
    """Full cartridge detail: name + nodes."""

    cartridge_name: str
    node_count: int
    nodes: list[CartridgeNodeResult]


class ExtractionRequest(BaseModel):
    """Payload to submit a server-side LLM extraction job."""

    corpus: str = Field(min_length=1, max_length=500_000)
    node_type: str = Field(default="concept", min_length=1)
    project_id: str = Field(min_length=1)


class ExtractionJobStatus(BaseModel):
    """Response for extraction job status polling."""

    job_id: str
    status: str
    cartridge_name: str
    node_count: int | None = None
    error: str | None = None


class OrgInstallResponse(BaseModel):
    """Response after an org-level cartridge install (S-KC4.7).

    Mirrors server CartridgeOrgInstallResponse.
    """

    model_config = {"extra": "ignore"}

    cartridge_id: str
    cartridge_name: str
    org_id: str
    installed_by: str
    installed_at: str | None = None


class PublicCartridgeItem(BaseModel):
    """A cartridge entry from the public catalog endpoint (S-KC4.6).

    Mirrors server CartridgeInfo with richer optional fields.
    Extra fields from the server response (e.g. installed_at) are ignored.
    """

    model_config = {"extra": "ignore"}

    cartridge_name: str
    node_count: int
    description: str | None = None
    author_org_id: str | None = None
    visibility: Literal["private", "public"] | None = None


class ProjectCartridgeInfo(BaseModel):
    """A cartridge assigned to a project, with its policy (S-KC4.8).

    Mirrors server ProjectCartridgeInfo. Extra fields ignored.
    """

    model_config = {"extra": "ignore"}

    cartridge_name: str
    cartridge_id: str
    policy: str
    visibility: Literal["private", "public"]
    author_org_id: str
    assigned_at: str | None = None
