"""Integration tests for graph diff with deterministic fixture data.

Builds a fixture graph with known nodes, makes changes, and verifies
diff_graphs detects them accurately. Decoupled from live codebase state.
"""

from __future__ import annotations

from raise_cli.context.diff import diff_graphs
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode


class TestDiffWithFixtureGraph:
    """Diff against a deterministic fixture graph."""

    def _build_fixture_graph(self) -> Graph:
        """Build a deterministic graph for diff testing."""
        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="mod-alpha",
                type="module",
                content="Alpha module for testing",
                created="2026-01-01",
                metadata={"code_imports": ["config"], "code_exports": ["alpha_func"]},
            )
        )
        graph.add_concept(
            GraphNode(
                id="mod-beta",
                type="module",
                content="Beta module for testing",
                created="2026-01-01",
                metadata={"code_imports": [], "code_exports": []},
            )
        )
        graph.add_concept(
            GraphNode(
                id="PAT-001",
                type="pattern",
                content="Test pattern one",
                created="2026-01-01",
            )
        )
        graph.add_concept(
            GraphNode(
                id="PAT-002",
                type="pattern",
                content="Test pattern two",
                created="2026-01-01",
            )
        )
        graph.add_concept(
            GraphNode(
                id="guard-001",
                type="guardrail",
                content="Test guardrail",
                created="2026-01-01",
            )
        )
        return graph

    def test_identical_graphs_no_changes(self) -> None:
        """Diffing same graph against itself produces no changes."""
        graph = self._build_fixture_graph()
        diff = diff_graphs(graph, graph)
        assert diff.node_changes == []
        assert diff.impact == "none"
        assert diff.summary == "no changes"

    def test_detect_added_node(self) -> None:
        """Adding a node to graph is detected."""
        old_graph = self._build_fixture_graph()
        new_graph = self._build_fixture_graph()

        fake_module = GraphNode(
            id="mod-gamma",
            type="module",
            content="Gamma module added in new graph",
            created="2026-01-02",
            metadata={"code_imports": [], "code_exports": []},
        )
        new_graph.add_concept(fake_module)

        diff = diff_graphs(old_graph, new_graph)
        assert len(diff.node_changes) == 1
        assert diff.node_changes[0].node_id == "mod-gamma"
        assert diff.node_changes[0].change_type == "added"
        assert diff.impact == "module"
        assert "mod-gamma" in diff.affected_modules

    def test_detect_modified_module_metadata(self) -> None:
        """Modifying a module's metadata is detected."""
        old_graph = self._build_fixture_graph()
        new_graph = self._build_fixture_graph()

        mod_node = new_graph.get_concept("mod-alpha")
        assert mod_node is not None, "mod-alpha should exist in fixture graph"

        modified_node = GraphNode(
            id=mod_node.id,
            type=mod_node.type,
            content=mod_node.content,
            created=mod_node.created,
            source_file=mod_node.source_file,
            metadata={**mod_node.metadata, "code_imports": ["config", "new-dep"]},
        )
        new_graph.add_concept(modified_node)

        diff = diff_graphs(old_graph, new_graph)

        mod_changes = [c for c in diff.node_changes if c.node_id == "mod-alpha"]
        assert len(mod_changes) == 1
        assert mod_changes[0].change_type == "modified"
        assert "metadata" in mod_changes[0].changed_fields
        assert "mod-alpha" in diff.affected_modules

    def test_detect_removed_node(self) -> None:
        """Removing a node from graph is detected."""
        old_graph = self._build_fixture_graph()
        new_graph = self._build_fixture_graph()

        # Add a node to old graph only (simulates removal)
        extra_node = GraphNode(
            id="PAT-999",
            type="pattern",
            content="Pattern that gets removed",
            created="2026-01-01",
        )
        old_graph.add_concept(extra_node)

        diff = diff_graphs(old_graph, new_graph)

        removed = [c for c in diff.node_changes if c.node_id == "PAT-999"]
        assert len(removed) == 1
        assert removed[0].change_type == "removed"
