"""SQLAlchemy 2.0 async models for raise-server.

Tables: organizations, members, api_keys, licenses,
        graph_nodes, graph_edges, agent_events, memory_patterns.
Architecture: Epic E275 (DD#3 Mapped[] columns), Epic E616 (members/licenses).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all raise-server models."""


class Organization(Base):
    """Tenant organization. All graph data is scoped to an org."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(63), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MemberRow(Base):
    """Organization member. Inherits org plan features."""

    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("org_id", "email", name="uq_member_org_email"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), server_default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ApiKeyRow(Base):
    """API key for member authentication. N keys per member, show-once pattern."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    member_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("members.id"))
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    key_hash: Mapped[str] = mapped_column(String(128), index=True)
    key_prefix: Mapped[str] = mapped_column(String(12))
    scopes: Mapped[list] = mapped_column(JSONB, server_default='["full_access"]')  # type: ignore[assignment]  # JSONB <-> list
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LicenseRow(Base):
    """Organization license. One active license per org (MVP)."""

    __tablename__ = "licenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    plan: Mapped[str] = mapped_column(String(20))
    features: Mapped[list] = mapped_column(JSONB, server_default="[]")  # type: ignore[assignment]  # JSONB <-> list
    seats: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GraphNodeRow(Base):
    """Persisted knowledge graph node. Maps to raise_core.graph.models.GraphNode."""

    __tablename__ = "graph_nodes"
    __table_args__ = (
        UniqueConstraint(
            "org_id", "repo_id", "node_id", name="uq_node_org_repo_nodeid"
        ),
        Index("ix_graph_nodes_properties", "properties", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    repo_id: Mapped[str] = mapped_column(String(255), index=True)
    scope: Mapped[str] = mapped_column(String(20))
    node_type: Mapped[str] = mapped_column(String(50), index=True)
    node_id: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    properties: Mapped[dict] = mapped_column(JSONB, server_default="{}")  # type: ignore[assignment]  # JSONB <-> dict: SA/pyright incompatibility
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GraphEdgeRow(Base):
    """Persisted knowledge graph edge. Maps to raise_core.graph.models.GraphEdge."""

    __tablename__ = "graph_edges"
    __table_args__ = (
        Index("ix_graph_edges_properties", "properties", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    repo_id: Mapped[str] = mapped_column(String(255))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_nodes.id"))
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_nodes.id"))
    edge_type: Mapped[str] = mapped_column(String(50), index=True)
    weight: Mapped[float] = mapped_column(Float, server_default="1.0")
    properties: Mapped[dict] = mapped_column(JSONB, server_default="{}")  # type: ignore[assignment]  # JSONB <-> dict: SA/pyright incompatibility
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AgentEventRow(Base):
    """Telemetry event from a Rovo agent or CLI action. Append-only."""

    __tablename__ = "agent_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, server_default="{}")  # type: ignore[assignment]  # JSONB <-> dict
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MemoryPatternRow(Base):
    """Learned pattern from Rovo agent or CLI. Append-only for POC."""

    __tablename__ = "memory_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    context: Mapped[list] = mapped_column(JSONB, server_default="[]")  # type: ignore[assignment]  # JSONB <-> list
    properties: Mapped[dict] = mapped_column(JSONB, server_default="{}")  # type: ignore[assignment]  # JSONB <-> dict
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
