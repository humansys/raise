"""Pydantic models for graph sync and query endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NodeInput(BaseModel):
    """A graph node in a sync request."""

    node_id: str = Field(min_length=1)
    node_type: str = Field(min_length=1)
    scope: str = Field(default="project", max_length=20)
    content: str = Field(min_length=1)
    source_file: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class EdgeInput(BaseModel):
    """A graph edge in a sync request."""

    source_node_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    edge_type: str = Field(min_length=1)
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphSyncRequest(BaseModel):
    """Full graph sync payload — replaces all nodes/edges for a project."""

    project_id: str = Field(min_length=1)
    nodes: list[NodeInput]
    edges: list[EdgeInput]


class GraphSyncResponse(BaseModel):
    """Response after a successful graph sync."""

    status: str = "ok"
    project_id: str
    nodes_upserted: int
    edges_created: int
    edges_skipped: int
    nodes_pruned: int


class NodeResult(BaseModel):
    """A single node in query results."""

    node_id: str
    node_type: str
    scope: str
    content: str
    source_file: str | None
    properties: dict[str, Any]
    rank: float


class GraphQueryResponse(BaseModel):
    """Response for a graph keyword query."""

    results: list[NodeResult]
    total: int
    query: str
    limit: int
