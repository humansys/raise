"""Tests for graph diff engine.

Tests diff_graphs() pure function, NodeChange/GraphDiff models,
impact classification, and affected_modules derivation.
"""

from __future__ import annotations

from raise_cli.context.diff import GraphDiff, NodeChange, diff_graphs
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode


def _make_node(
    id: str,
    type: str = "pattern",
    content: str = "test content",
    metadata: dict | None = None,
) -> GraphNode:
    """Helper to create a GraphNode with minimal boilerplate."""
    return GraphNode(
        id=id,
        type=type,  # type: ignore[arg-type]
        content=content,
        created="2026-02-09",
        metadata=metadata or {},
    )


class TestDiffGraphsIdenticalGraphs:
    """Diffing identical graphs produces no changes."""

    def test_empty_graphs(self) -> None:
        old = Graph()
        new = Graph()
        diff = diff_graphs(old, new)
        assert diff.node_changes == []
        assert diff.impact == "none"
        assert diff.affected_modules == []

    def test_identical_nodes(self) -> None:
        old = Graph()
        new = Graph()
        node = _make_node("PAT-001", content="some pattern")
        old.add_concept(node)
        new.add_concept(node)
        diff = diff_graphs(old, new)
        assert diff.node_changes == []
        assert diff.impact == "none"

    def test_identical_modules(self) -> None:
        old = Graph()
        new = Graph()
        node = _make_node(
            "mod-memory",
            type="module",
            content="memory module",
            metadata={"code_imports": ["config"]},
        )
        old.add_concept(node)
        new.add_concept(node)
        diff = diff_graphs(old, new)
        assert diff.node_changes == []
        assert diff.affected_modules == []


class TestDiffGraphsAddedNodes:
    """Nodes in new graph but not old are 'added'."""

    def test_single_added_node(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("PAT-001"))
        diff = diff_graphs(old, new)
        assert len(diff.node_changes) == 1
        change = diff.node_changes[0]
        assert change.node_id == "PAT-001"
        assert change.change_type == "added"
        assert change.old_value is None
        assert change.new_value is not None

    def test_added_module_affects_modules(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-new", type="module", content="new module"))
        diff = diff_graphs(old, new)
        assert "mod-new" in diff.affected_modules
        assert diff.impact == "module"

    def test_added_pattern_no_module_impact(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("PAT-999"))
        diff = diff_graphs(old, new)
        assert diff.affected_modules == []
        assert diff.impact == "none"


class TestDiffGraphsRemovedNodes:
    """Nodes in old graph but not new are 'removed'."""

    def test_single_removed_node(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(_make_node("PAT-001"))
        diff = diff_graphs(old, new)
        assert len(diff.node_changes) == 1
        change = diff.node_changes[0]
        assert change.node_id == "PAT-001"
        assert change.change_type == "removed"
        assert change.old_value is not None
        assert change.new_value is None

    def test_removed_module_affects_modules(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(_make_node("mod-old", type="module", content="old module"))
        diff = diff_graphs(old, new)
        assert "mod-old" in diff.affected_modules
        assert diff.impact == "module"


class TestDiffGraphsModifiedNodes:
    """Nodes with same ID but different content/type/metadata are 'modified'."""

    def test_content_change(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(_make_node("PAT-001", content="old content"))
        new.add_concept(_make_node("PAT-001", content="new content"))
        diff = diff_graphs(old, new)
        assert len(diff.node_changes) == 1
        change = diff.node_changes[0]
        assert change.change_type == "modified"
        assert "content" in change.changed_fields

    def test_metadata_change(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(
            _make_node("mod-ctx", type="module", metadata={"code_imports": ["config"]})
        )
        new.add_concept(
            _make_node(
                "mod-ctx",
                type="module",
                metadata={"code_imports": ["config", "memory"]},
            )
        )
        diff = diff_graphs(old, new)
        assert len(diff.node_changes) == 1
        change = diff.node_changes[0]
        assert change.change_type == "modified"
        assert "metadata" in change.changed_fields
        assert "mod-ctx" in diff.affected_modules

    def test_type_change(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(_make_node("X-001", type="pattern"))
        new.add_concept(_make_node("X-001", type="calibration"))
        diff = diff_graphs(old, new)
        assert len(diff.node_changes) == 1
        assert "type" in diff.node_changes[0].changed_fields

    def test_ignores_created_field(self) -> None:
        old = Graph()
        new = Graph()
        node_old = GraphNode(
            id="PAT-001",
            type="pattern",
            content="same",
            created="2026-01-01",
            metadata={},
        )
        node_new = GraphNode(
            id="PAT-001",
            type="pattern",
            content="same",
            created="2026-02-09",
            metadata={},
        )
        old.add_concept(node_old)
        new.add_concept(node_new)
        diff = diff_graphs(old, new)
        assert diff.node_changes == []

    def test_ignores_source_file_field(self) -> None:
        old = Graph()
        new = Graph()
        node_old = GraphNode(
            id="PAT-001",
            type="pattern",
            content="same",
            created="2026-02-09",
            source_file="old/path.md",
            metadata={},
        )
        node_new = GraphNode(
            id="PAT-001",
            type="pattern",
            content="same",
            created="2026-02-09",
            source_file="new/path.md",
            metadata={},
        )
        old.add_concept(node_old)
        new.add_concept(node_new)
        diff = diff_graphs(old, new)
        assert diff.node_changes == []


class TestImpactClassification:
    """Impact is derived from the types of changed nodes."""

    def test_no_changes_is_none(self) -> None:
        diff = diff_graphs(Graph(), Graph())
        assert diff.impact == "none"

    def test_pattern_changes_is_none(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("PAT-001"))
        new.add_concept(_make_node("SES-001", type="session"))
        diff = diff_graphs(old, new)
        assert diff.impact == "none"

    def test_module_change_is_module(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-x", type="module"))
        diff = diff_graphs(old, new)
        assert diff.impact == "module"

    def test_component_change_is_module(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("comp-x", type="component"))
        diff = diff_graphs(old, new)
        assert diff.impact == "module"

    def test_bounded_context_change_is_architectural(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("bc-ontology", type="bounded_context"))
        diff = diff_graphs(old, new)
        assert diff.impact == "architectural"

    def test_layer_change_is_architectural(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("lyr-leaf", type="layer"))
        diff = diff_graphs(old, new)
        assert diff.impact == "architectural"

    def test_architectural_trumps_module(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-x", type="module"))
        new.add_concept(_make_node("bc-new", type="bounded_context"))
        diff = diff_graphs(old, new)
        assert diff.impact == "architectural"


class TestAffectedModules:
    """affected_modules lists module IDs from changed nodes."""

    def test_module_node_added(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-memory", type="module"))
        diff = diff_graphs(old, new)
        assert diff.affected_modules == ["mod-memory"]

    def test_non_module_not_in_affected(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("PAT-001"))
        diff = diff_graphs(old, new)
        assert diff.affected_modules == []

    def test_multiple_modules_sorted(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-context", type="module"))
        new.add_concept(_make_node("mod-memory", type="module"))
        diff = diff_graphs(old, new)
        assert diff.affected_modules == ["mod-context", "mod-memory"]


class TestSummary:
    """Summary is a deterministic template string."""

    def test_no_changes(self) -> None:
        diff = diff_graphs(Graph(), Graph())
        assert diff.summary == "no changes"

    def test_changes_summary_format(self) -> None:
        old = Graph()
        new = Graph()
        new.add_concept(_make_node("mod-x", type="module"))
        new.add_concept(_make_node("PAT-001"))
        diff = diff_graphs(old, new)
        assert "2 nodes changed" in diff.summary
        assert "2 added" in diff.summary
        assert "mod-x" in diff.summary

    def test_mixed_changes(self) -> None:
        old = Graph()
        new = Graph()
        old.add_concept(_make_node("PAT-001", content="old"))
        new.add_concept(_make_node("PAT-001", content="new"))
        new.add_concept(_make_node("PAT-002"))
        old.add_concept(_make_node("PAT-003"))
        diff = diff_graphs(old, new)
        assert "3 nodes changed" in diff.summary
        assert "1 added" in diff.summary
        assert "1 removed" in diff.summary
        assert "1 modified" in diff.summary


class TestNodeChangeModel:
    """NodeChange model validation."""

    def test_added_node_has_no_old_value(self) -> None:
        change = NodeChange(
            node_id="PAT-001",
            change_type="added",
            old_value=None,
            new_value=_make_node("PAT-001"),
            changed_fields=[],
        )
        assert change.old_value is None
        assert change.new_value is not None

    def test_removed_node_has_no_new_value(self) -> None:
        change = NodeChange(
            node_id="PAT-001",
            change_type="removed",
            old_value=_make_node("PAT-001"),
            new_value=None,
            changed_fields=[],
        )
        assert change.old_value is not None
        assert change.new_value is None


class TestGraphDiffModel:
    """GraphDiff model validation."""

    def test_serialization_roundtrip(self) -> None:
        diff = GraphDiff(
            node_changes=[
                NodeChange(
                    node_id="mod-x",
                    change_type="added",
                    old_value=None,
                    new_value=_make_node("mod-x", type="module"),
                    changed_fields=[],
                )
            ],
            impact="module",
            affected_modules=["mod-x"],
            summary="1 nodes changed (1 added), 1 module affected (mod-x)",
        )
        data = diff.model_dump()
        restored = GraphDiff.model_validate(data)
        assert restored.impact == "module"
        assert len(restored.node_changes) == 1
        assert restored.affected_modules == ["mod-x"]
