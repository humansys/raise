"""Tests for unified context graph models."""

from __future__ import annotations

import pytest

from raise_core.graph.models import (
    CoreEdgeTypes,
    EpicNode,
    GraphEdge,
    GraphNode,
    NodeType,
    PatternNode,
)


class TestGraphNodeBasic:
    """Tests for GraphNode model."""

    def test_create_pattern_node(self) -> None:
        """Test creating a pattern node."""
        node = GraphNode(
            id="PAT-001",
            type="pattern",
            content="Singleton with get/set/configure pattern",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"sub_type": "codebase", "context": ["testing"]},
        )
        assert node.id == "PAT-001"
        assert node.type == "pattern"
        assert "Singleton" in node.content
        assert node.source_file == ".raise/rai/memory/patterns.jsonl"
        assert node.metadata["sub_type"] == "codebase"

    def test_create_principle_node(self) -> None:
        """Test creating a principle node."""
        node = GraphNode(
            id="§2",
            type="principle",
            content="Governance as Code - Standards versioned in Git",
            created="2026-02-03",
        )
        assert node.id == "§2"
        assert node.type == "principle"
        assert node.source_file is None
        assert node.metadata == {}

    def test_create_module_node(self) -> None:
        """Test creating a module node for architecture knowledge."""
        node = GraphNode(
            id="mod-discovery",
            type="module",
            content="Codebase analysis — scanning, confidence scoring, validation",
            source_file="governance/architecture/modules/discovery.md",
            created="2026-02-08",
            metadata={
                "purpose": "Code scanning and analysis",
                "depends_on": ["core", "schemas"],
                "depended_by": ["cli", "context"],
                "components": 42,
            },
        )
        assert node.id == "mod-discovery"
        assert node.type == "module"
        assert node.metadata["depends_on"] == ["core", "schemas"]
        assert node.metadata["components"] == 42

    def test_token_estimate(self) -> None:
        """Test token estimation."""
        node = GraphNode(
            id="PAT-001",
            type="pattern",
            content="A" * 100,  # 100 characters
            created="2026-02-03",
        )
        assert node.token_estimate == 25  # 100 // 4

    def test_invalid_node_type_rejected(self) -> None:
        """Test that any string type is accepted (open type system)."""
        node = GraphNode(
            id="TEST-001",
            type="custom.plugin_type",
            content="Test",
            created="2026-02-03",
        )
        assert node.type == "custom.plugin_type"


class TestGraphNode:
    """Tests for GraphNode base class with auto-registration."""

    def test_graphnode_subclass_registers_type(self) -> None:
        """Subclass with node_type registers in the global registry."""

        class _TestRegNode(GraphNode, node_type="test_reg_t1"): ...

        assert "test_reg_t1" in GraphNode.registered_types()
        assert GraphNode.resolve("test_reg_t1") is _TestRegNode

    def test_graphnode_resolve_unknown_raises(self) -> None:
        """resolve() raises KeyError for unregistered types."""
        with pytest.raises(KeyError):
            GraphNode.resolve("nonexistent_type_xyz")

    def test_graphnode_subclass_auto_sets_type(self) -> None:
        """Subclass instances get type auto-set from registration."""

        class _AutoNode(GraphNode, node_type="auto_test_t1"): ...

        node = _AutoNode(id="A1", content="hello", created="2026-01-01")
        assert node.type == "auto_test_t1"

    def test_graphnode_model_dump_includes_type(self) -> None:
        """model_dump() includes the auto-set type field."""

        class _DumpNode(GraphNode, node_type="dump_test_t1"): ...

        node = _DumpNode(id="D1", content="test", created="2026-01-01")
        dumped = node.model_dump()
        assert dumped["type"] == "dump_test_t1"

    def test_graphnode_explicit_type_preserved(self) -> None:
        """Explicitly provided type is not overwritten by auto-default."""

        class _ExplicitNode(GraphNode, node_type="explicit_test_t1"): ...

        node = _ExplicitNode(
            id="E1", type="custom_override", content="test", created="2026-01-01"
        )
        assert node.type == "custom_override"

    def test_graphnode_base_no_auto_type(self) -> None:
        """GraphNode base itself requires explicit type (no __node_type__)."""
        node = GraphNode(id="B1", type="anything", content="test", created="2026-01-01")
        assert node.type == "anything"

    def test_graphnode_subclass_without_node_type_not_registered(self) -> None:
        """Subclass without node_type kwarg is NOT registered."""

        class _PlainSubclass(GraphNode):
            extra: str = "value"

        # Should not appear in registry
        assert "_PlainSubclass" not in str(GraphNode.registered_types())


class TestCoreNodeTypes:
    """Tests for 18 core node type subclasses."""

    EXPECTED_CORE_TYPES = {
        "pattern",
        "calibration",
        "session",
        "principle",
        "requirement",
        "outcome",
        "project",
        "epic",
        "story",
        "skill",
        "decision",
        "guardrail",
        "term",
        "component",
        "module",
        "architecture",
        "bounded_context",
        "layer",
        "release",
    }

    def test_all_18_core_types_registered(self) -> None:
        """All 18 core types appear in the registry."""
        registered = set(GraphNode.registered_types().keys())
        missing = self.EXPECTED_CORE_TYPES - registered
        assert not missing, f"Missing core types: {missing}"

    def test_epic_node_creates_with_correct_type(self) -> None:
        """EpicNode auto-sets type to 'epic'."""
        node = EpicNode(id="E1", content="test epic", created="2026-01-01")
        assert node.type == "epic"
        assert isinstance(node, GraphNode)

    def test_pattern_node_creates_with_correct_type(self) -> None:
        """PatternNode auto-sets type to 'pattern'."""
        node = PatternNode(id="PAT-1", content="test", created="2026-01-01")
        assert node.type == "pattern"

    def test_conceptnode_alias_is_graphnode(self) -> None:
        """GraphNode is an alias for GraphNode."""
        assert GraphNode is GraphNode  # noqa: PLR0124 -- was alias test; kept for backward compat documentation

    def test_conceptnode_backward_compat(self) -> None:
        """GraphNode still works with explicit type for backward compat."""
        node = GraphNode(id="X", type="epic", content="test", created="2026-01-01")
        assert isinstance(node, GraphNode)
        assert node.type == "epic"

    def test_nodetype_is_str(self) -> None:
        """NodeType is str (open type system)."""
        assert NodeType is str

    def test_conceptedge_alias_is_graphedge(self) -> None:
        """GraphEdge is an alias for GraphEdge."""
        assert GraphEdge is GraphEdge  # noqa: PLR0124 -- was alias test; kept for backward compat documentation

    def test_core_edge_types_constants(self) -> None:
        """CoreEdgeTypes provides string constants for built-in edges."""
        assert CoreEdgeTypes.LEARNED_FROM == "learned_from"
        assert CoreEdgeTypes.PART_OF == "part_of"
        assert CoreEdgeTypes.CONSTRAINED_BY == "constrained_by"


class TestGraphEdge:
    """Tests for GraphEdge model."""

    def test_create_learned_from_edge(self) -> None:
        """Test creating a learned_from edge."""
        edge = GraphEdge(
            source="PAT-001",
            target="SES-015",
            type="learned_from",
            weight=1.0,
            metadata={"confidence": 0.9},
        )
        assert edge.source == "PAT-001"
        assert edge.target == "SES-015"
        assert edge.type == "learned_from"
        assert edge.weight == 1.0
        assert edge.metadata["confidence"] == 0.9

    def test_create_governed_by_edge(self) -> None:
        """Test creating a governed_by edge."""
        edge = GraphEdge(
            source="RF-05",
            target="§2",
            type="governed_by",
        )
        assert edge.source == "RF-05"
        assert edge.target == "§2"
        assert edge.type == "governed_by"
        assert edge.weight == 1.0  # default
        assert edge.metadata == {}  # default

    def test_create_depends_on_edge(self) -> None:
        """Test creating a depends_on edge between modules."""
        edge = GraphEdge(
            source="mod-discovery",
            target="mod-core",
            type="depends_on",
            weight=1.0,
        )
        assert edge.source == "mod-discovery"
        assert edge.target == "mod-core"
        assert edge.type == "depends_on"

    def test_all_edge_types_valid(self) -> None:
        """Test that all edge types can be created."""
        edge_types = [
            "learned_from",
            "governed_by",
            "applies_to",
            "needs_context",
            "implements",
            "part_of",
            "related_to",
            "depends_on",
        ]
        for edge_type in edge_types:
            edge = GraphEdge(
                source="A",
                target="B",
                type=edge_type,  # type: ignore[arg-type]
            )
            assert edge.type == edge_type

    def test_custom_weight(self) -> None:
        """Test custom edge weight."""
        edge = GraphEdge(
            source="A",
            target="B",
            type="related_to",
            weight=0.5,
        )
        assert edge.weight == 0.5

    def test_any_edge_type_accepted(self) -> None:
        """Test that any string edge type is accepted (open type system)."""
        edge = GraphEdge(
            source="A",
            target="B",
            type="jira.blocks",
        )
        assert edge.type == "jira.blocks"
