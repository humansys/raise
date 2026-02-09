"""Integration tests for graph diff against real raise-commons data.

Builds the actual unified graph, makes a change, and verifies
diff_graphs detects it accurately.
"""

from __future__ import annotations

from raise_cli.context.builder import UnifiedGraphBuilder
from raise_cli.context.diff import diff_graphs
from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode


class TestDiffWithRealGraph:
    """Diff against actual raise-commons unified graph."""

    def _build_real_graph(self) -> UnifiedGraph:
        """Build the real raise-commons graph."""
        builder = UnifiedGraphBuilder()
        return builder.build()

    def test_identical_real_graphs_no_changes(self) -> None:
        """Diffing same graph against itself produces no changes."""
        graph = self._build_real_graph()
        diff = diff_graphs(graph, graph)
        assert diff.node_changes == []
        assert diff.impact == "none"
        assert diff.summary == "no changes"

    def test_detect_added_node_in_real_graph(self) -> None:
        """Adding a node to real graph is detected."""
        old_graph = self._build_real_graph()
        new_graph = self._build_real_graph()

        # Add a fake module node
        fake_module = ConceptNode(
            id="mod-fake-test",
            type="module",
            content="Fake test module for diff validation",
            created="2026-02-09",
            metadata={"code_imports": [], "code_exports": []},
        )
        new_graph.add_concept(fake_module)

        diff = diff_graphs(old_graph, new_graph)
        assert len(diff.node_changes) == 1
        assert diff.node_changes[0].node_id == "mod-fake-test"
        assert diff.node_changes[0].change_type == "added"
        assert diff.impact == "module"
        assert "mod-fake-test" in diff.affected_modules

    def test_detect_modified_module_metadata(self) -> None:
        """Modifying a real module's metadata is detected."""
        old_graph = self._build_real_graph()
        new_graph = self._build_real_graph()

        # Find a real module and modify its metadata in new graph
        mod_node = new_graph.get_concept("mod-memory")
        assert mod_node is not None, "mod-memory should exist in graph"

        modified_node = ConceptNode(
            id=mod_node.id,
            type=mod_node.type,
            content=mod_node.content,
            created=mod_node.created,
            source_file=mod_node.source_file,
            metadata={**mod_node.metadata, "code_imports": ["config", "fake-dep"]},
        )
        # Replace in graph by re-adding (overwrites)
        new_graph.add_concept(modified_node)

        diff = diff_graphs(old_graph, new_graph)

        # Should detect the modification
        mod_changes = [c for c in diff.node_changes if c.node_id == "mod-memory"]
        assert len(mod_changes) == 1
        assert mod_changes[0].change_type == "modified"
        assert "metadata" in mod_changes[0].changed_fields
        assert "mod-memory" in diff.affected_modules

    def test_detect_removed_node(self) -> None:
        """Removing a node from real graph is detected."""
        old_graph = self._build_real_graph()
        new_graph = self._build_real_graph()

        # Add a node to old graph only (simulates removal)
        fake_node = ConceptNode(
            id="PAT-FAKE-999",
            type="pattern",
            content="Fake pattern to be removed",
            created="2026-02-09",
        )
        old_graph.add_concept(fake_node)

        diff = diff_graphs(old_graph, new_graph)

        removed = [c for c in diff.node_changes if c.node_id == "PAT-FAKE-999"]
        assert len(removed) == 1
        assert removed[0].change_type == "removed"

    def test_real_graph_has_sufficient_nodes(self) -> None:
        """Sanity check: real graph has expected node count."""
        graph = self._build_real_graph()
        # S16.5 established 345 nodes; should be in that range
        assert graph.node_count >= 300, f"Expected ~345 nodes, got {graph.node_count}"
