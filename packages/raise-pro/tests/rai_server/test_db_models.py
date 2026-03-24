"""Unit tests for raise_server DB models using SQLAlchemy inspection API.

No real database needed — tests validate model structure, columns,
types, foreign keys, indexes, and constraints.
"""

from __future__ import annotations

from raise_server.db.models import (
    AgentEventRow,
    ApiKey,
    Base,
    GraphEdgeRow,
    GraphNodeRow,
    MemoryPatternRow,
    Organization,
)
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB, UUID

# --- Table registration ---


class TestTableRegistration:
    """All 4 tables must be registered in Base.metadata."""

    def test_all_tables_registered(self) -> None:
        tables = set(Base.metadata.tables.keys())
        assert tables == {
            "organizations",
            "api_keys",
            "graph_nodes",
            "graph_edges",
            "agent_events",
            "memory_patterns",
        }


# --- Organization ---


class TestOrganizationModel:
    def test_tablename(self) -> None:
        assert Organization.__tablename__ == "organizations"

    def test_columns_exist(self) -> None:
        mapper = inspect(Organization)
        cols = {c.key for c in mapper.columns}
        assert cols == {"id", "name", "slug", "created_at"}

    def test_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(Organization)
        col = mapper.columns["id"]
        assert isinstance(col.type, UUID)
        assert col.primary_key

    def test_slug_is_unique_and_indexed(self) -> None:
        mapper = inspect(Organization)
        col = mapper.columns["slug"]
        assert col.unique
        assert col.index


# --- ApiKey ---


class TestApiKeyModel:
    def test_tablename(self) -> None:
        assert ApiKey.__tablename__ == "api_keys"

    def test_columns_exist(self) -> None:
        mapper = inspect(ApiKey)
        cols = {c.key for c in mapper.columns}
        assert cols == {"id", "org_id", "key_hash", "prefix", "is_active", "created_at"}

    def test_org_id_foreign_key(self) -> None:
        mapper = inspect(ApiKey)
        col = mapper.columns["org_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "organizations.id" in fk_targets

    def test_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(ApiKey)
        col = mapper.columns["id"]
        assert isinstance(col.type, UUID)
        assert col.primary_key


# --- GraphNodeRow ---


class TestGraphNodeRowModel:
    def test_tablename(self) -> None:
        assert GraphNodeRow.__tablename__ == "graph_nodes"

    def test_columns_exist(self) -> None:
        mapper = inspect(GraphNodeRow)
        cols = {c.key for c in mapper.columns}
        expected = {
            "id",
            "org_id",
            "repo_id",
            "scope",
            "node_type",
            "node_id",
            "content",
            "source_file",
            "properties",
            "created_at",
            "updated_at",
        }
        assert cols == expected

    def test_properties_is_jsonb(self) -> None:
        mapper = inspect(GraphNodeRow)
        col = mapper.columns["properties"]
        assert isinstance(col.type, JSONB)

    def test_org_id_foreign_key(self) -> None:
        mapper = inspect(GraphNodeRow)
        col = mapper.columns["org_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "organizations.id" in fk_targets

    def test_org_id_indexed(self) -> None:
        mapper = inspect(GraphNodeRow)
        col = mapper.columns["org_id"]
        assert col.index

    def test_node_type_indexed(self) -> None:
        mapper = inspect(GraphNodeRow)
        col = mapper.columns["node_type"]
        assert col.index

    def test_source_file_nullable(self) -> None:
        mapper = inspect(GraphNodeRow)
        col = mapper.columns["source_file"]
        assert col.nullable

    def test_composite_unique_org_repo_node_id(self) -> None:
        """SHOULD: Composite unique constraint prevents duplicate domain IDs per org+repo."""
        table = GraphNodeRow.__table__
        unique_constraints = [
            c for c in table.constraints if hasattr(c, "columns") and len(c.columns) > 1
        ]
        # Find the unique constraint covering (org_id, repo_id, node_id)
        found = False
        for uc in unique_constraints:
            col_names = {c.name for c in uc.columns}
            if col_names == {"org_id", "repo_id", "node_id"}:
                found = True
                break
        assert found, (
            "Missing composite unique constraint on (org_id, repo_id, node_id)"
        )


# --- GraphEdgeRow ---


class TestGraphEdgeRowModel:
    def test_tablename(self) -> None:
        assert GraphEdgeRow.__tablename__ == "graph_edges"

    def test_columns_exist(self) -> None:
        mapper = inspect(GraphEdgeRow)
        cols = {c.key for c in mapper.columns}
        expected = {
            "id",
            "org_id",
            "repo_id",
            "source_id",
            "target_id",
            "edge_type",
            "weight",
            "properties",
            "created_at",
        }
        assert cols == expected

    def test_properties_is_jsonb(self) -> None:
        mapper = inspect(GraphEdgeRow)
        col = mapper.columns["properties"]
        assert isinstance(col.type, JSONB)

    def test_source_id_foreign_key(self) -> None:
        mapper = inspect(GraphEdgeRow)
        col = mapper.columns["source_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "graph_nodes.id" in fk_targets

    def test_target_id_foreign_key(self) -> None:
        mapper = inspect(GraphEdgeRow)
        col = mapper.columns["target_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "graph_nodes.id" in fk_targets

    def test_org_id_foreign_key(self) -> None:
        mapper = inspect(GraphEdgeRow)
        col = mapper.columns["org_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "organizations.id" in fk_targets

    def test_edge_type_indexed(self) -> None:
        mapper = inspect(GraphEdgeRow)
        col = mapper.columns["edge_type"]
        assert col.index


# --- AgentEventRow ---


class TestAgentEventRowModel:
    def test_tablename(self) -> None:
        assert AgentEventRow.__tablename__ == "agent_events"

    def test_columns_exist(self) -> None:
        mapper = inspect(AgentEventRow)
        cols = {c.key for c in mapper.columns}
        assert cols == {"id", "org_id", "event_type", "payload", "created_at"}

    def test_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(AgentEventRow)
        col = mapper.columns["id"]
        assert isinstance(col.type, UUID)
        assert col.primary_key

    def test_org_id_foreign_key(self) -> None:
        mapper = inspect(AgentEventRow)
        col = mapper.columns["org_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "organizations.id" in fk_targets

    def test_org_id_indexed(self) -> None:
        mapper = inspect(AgentEventRow)
        col = mapper.columns["org_id"]
        assert col.index

    def test_event_type_indexed(self) -> None:
        mapper = inspect(AgentEventRow)
        col = mapper.columns["event_type"]
        assert col.index

    def test_payload_is_jsonb(self) -> None:
        mapper = inspect(AgentEventRow)
        col = mapper.columns["payload"]
        assert isinstance(col.type, JSONB)


# --- MemoryPatternRow ---


class TestMemoryPatternRowModel:
    def test_tablename(self) -> None:
        assert MemoryPatternRow.__tablename__ == "memory_patterns"

    def test_columns_exist(self) -> None:
        mapper = inspect(MemoryPatternRow)
        cols = {c.key for c in mapper.columns}
        assert cols == {
            "id",
            "org_id",
            "content",
            "context",
            "properties",
            "created_at",
        }

    def test_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(MemoryPatternRow)
        col = mapper.columns["id"]
        assert isinstance(col.type, UUID)
        assert col.primary_key

    def test_org_id_foreign_key(self) -> None:
        mapper = inspect(MemoryPatternRow)
        col = mapper.columns["org_id"]
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "organizations.id" in fk_targets

    def test_org_id_indexed(self) -> None:
        mapper = inspect(MemoryPatternRow)
        col = mapper.columns["org_id"]
        assert col.index

    def test_context_is_jsonb(self) -> None:
        mapper = inspect(MemoryPatternRow)
        col = mapper.columns["context"]
        assert isinstance(col.type, JSONB)

    def test_properties_is_jsonb(self) -> None:
        mapper = inspect(MemoryPatternRow)
        col = mapper.columns["properties"]
        assert isinstance(col.type, JSONB)
