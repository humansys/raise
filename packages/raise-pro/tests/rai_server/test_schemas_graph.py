"""Tests for graph sync/query Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError


class TestNodeInput:
    """NodeInput validates graph node data for sync requests."""

    def test_minimal_valid(self) -> None:
        from raise_server.schemas.graph import NodeInput

        node = NodeInput(
            node_id="mod-memory", node_type="module", content="Memory management"
        )
        assert node.node_id == "mod-memory"
        assert node.node_type == "module"
        assert node.content == "Memory management"
        assert node.scope == "project"
        assert node.source_file is None
        assert node.properties == {}

    def test_all_fields(self) -> None:
        from raise_server.schemas.graph import NodeInput

        node = NodeInput(
            node_id="mod-graph",
            node_type="module",
            scope="org",
            content="Graph engine",
            source_file="src/graph/__init__.py",
            properties={"language": "python", "lines": 380},
        )
        assert node.scope == "org"
        assert node.source_file == "src/graph/__init__.py"
        assert node.properties["language"] == "python"

    def test_missing_content_field(self) -> None:
        from raise_server.schemas.graph import NodeInput

        with pytest.raises(ValidationError) as exc_info:
            NodeInput(node_id="mod-x", node_type="module")  # type: ignore[call-arg]
        assert "content" in str(exc_info.value)

    def test_empty_content_rejected(self) -> None:
        from raise_server.schemas.graph import NodeInput

        with pytest.raises(ValidationError):
            NodeInput(node_id="mod-x", node_type="module", content="")

    def test_scope_too_long_rejected(self) -> None:
        from raise_server.schemas.graph import NodeInput

        with pytest.raises(ValidationError):
            NodeInput(node_id="x", node_type="t", content="c", scope="a" * 21)

    def test_empty_node_id_rejected(self) -> None:
        from raise_server.schemas.graph import NodeInput

        with pytest.raises(ValidationError):
            NodeInput(node_id="", node_type="module", content="x")


class TestEdgeInput:
    """EdgeInput validates graph edge data for sync requests."""

    def test_minimal_valid(self) -> None:
        from raise_server.schemas.graph import EdgeInput

        edge = EdgeInput(
            source_node_id="mod-a", target_node_id="mod-b", edge_type="depends_on"
        )
        assert edge.source_node_id == "mod-a"
        assert edge.target_node_id == "mod-b"
        assert edge.weight == 1.0
        assert edge.properties == {}

    def test_custom_weight(self) -> None:
        from raise_server.schemas.graph import EdgeInput

        edge = EdgeInput(
            source_node_id="a", target_node_id="b", edge_type="contains", weight=0.5
        )
        assert edge.weight == 0.5

    def test_missing_edge_type(self) -> None:
        from raise_server.schemas.graph import EdgeInput

        with pytest.raises(ValidationError) as exc_info:
            EdgeInput(source_node_id="a", target_node_id="b")  # type: ignore[call-arg]
        assert "edge_type" in str(exc_info.value)


class TestGraphSyncRequest:
    """GraphSyncRequest validates the full sync payload."""

    def test_valid_request(self) -> None:
        from raise_server.schemas.graph import EdgeInput, GraphSyncRequest, NodeInput

        req = GraphSyncRequest(
            project_id="raise-commons",
            nodes=[NodeInput(node_id="mod-a", node_type="module", content="Module A")],
            edges=[
                EdgeInput(
                    source_node_id="mod-a",
                    target_node_id="mod-b",
                    edge_type="depends_on",
                )
            ],
        )
        assert req.project_id == "raise-commons"
        assert len(req.nodes) == 1
        assert len(req.edges) == 1

    def test_empty_nodes_allowed(self) -> None:
        from raise_server.schemas.graph import GraphSyncRequest

        req = GraphSyncRequest(project_id="empty-project", nodes=[], edges=[])
        assert req.nodes == []
        assert req.edges == []

    def test_missing_project_id(self) -> None:
        from raise_server.schemas.graph import GraphSyncRequest

        with pytest.raises(ValidationError) as exc_info:
            GraphSyncRequest(nodes=[], edges=[])  # type: ignore[call-arg]
        assert "project_id" in str(exc_info.value)

    def test_empty_project_id_rejected(self) -> None:
        from raise_server.schemas.graph import GraphSyncRequest

        with pytest.raises(ValidationError):
            GraphSyncRequest(project_id="", nodes=[], edges=[])


class TestGraphSyncResponse:
    """GraphSyncResponse serializes sync results."""

    def test_serialization(self) -> None:
        from raise_server.schemas.graph import GraphSyncResponse

        resp = GraphSyncResponse(
            project_id="raise-commons",
            nodes_upserted=12,
            edges_created=8,
            edges_skipped=1,
            nodes_pruned=1,
        )
        data = resp.model_dump()
        assert data["status"] == "ok"
        assert data["nodes_upserted"] == 12
        assert data["edges_skipped"] == 1
        assert data["nodes_pruned"] == 1


class TestNodeResult:
    """NodeResult serializes a single query result."""

    def test_serialization(self) -> None:
        from raise_server.schemas.graph import NodeResult

        result = NodeResult(
            node_id="mod-memory",
            node_type="module",
            scope="project",
            content="Memory management",
            source_file="src/memory/__init__.py",
            properties={"language": "python"},
            rank=0.075,
        )
        data = result.model_dump()
        assert data["node_id"] == "mod-memory"
        assert data["rank"] == 0.075

    def test_null_source_file(self) -> None:
        from raise_server.schemas.graph import NodeResult

        result = NodeResult(
            node_id="x",
            node_type="t",
            scope="project",
            content="c",
            source_file=None,
            properties={},
            rank=0.1,
        )
        assert result.source_file is None


class TestGraphQueryResponse:
    """GraphQueryResponse serializes query results."""

    def test_serialization(self) -> None:
        from raise_server.schemas.graph import GraphQueryResponse, NodeResult

        resp = GraphQueryResponse(
            results=[
                NodeResult(
                    node_id="mod-memory",
                    node_type="module",
                    scope="project",
                    content="Memory",
                    source_file=None,
                    properties={},
                    rank=0.5,
                ),
            ],
            total=1,
            query="memory",
            limit=10,
        )
        data = resp.model_dump()
        assert data["total"] == 1
        assert len(data["results"]) == 1
        assert data["query"] == "memory"

    def test_empty_results(self) -> None:
        from raise_server.schemas.graph import GraphQueryResponse

        resp = GraphQueryResponse(results=[], total=0, query="nonexistent", limit=10)
        assert resp.results == []
        assert resp.total == 0
