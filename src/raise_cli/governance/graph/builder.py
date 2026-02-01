"""Graph builder for constructing concept graphs from concepts.

This module provides the GraphBuilder class that orchestrates graph construction
from extracted concepts, including relationship inference and metadata population.
"""

from __future__ import annotations

from datetime import UTC, datetime

from raise_cli.governance.graph.models import ConceptGraph
from raise_cli.governance.graph.relationships import infer_relationships
from raise_cli.governance.models import Concept


class GraphBuilder:
    """Builder for constructing concept graphs from concepts.

    Orchestrates graph construction by:
    1. Creating nodes dict from concepts
    2. Inferring relationships between concepts
    3. Populating graph metadata (build time, statistics)

    Examples:
        >>> from raise_cli.governance.extractor import GovernanceExtractor
        >>> extractor = GovernanceExtractor()
        >>> concepts = extractor.extract_all()
        >>> builder = GraphBuilder()
        >>> graph = builder.build(concepts)
        >>> print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    """

    def build(self, concepts: list[Concept]) -> ConceptGraph:
        """Build concept graph from extracted concepts.

        Args:
            concepts: List of extracted concepts.

        Returns:
            Constructed ConceptGraph with nodes, edges, and metadata.

        Examples:
            >>> concepts = [concept1, concept2, concept3]
            >>> builder = GraphBuilder()
            >>> graph = builder.build(concepts)
            >>> len(graph.nodes) == 3
            True
        """
        # Build nodes dict indexed by ID
        nodes = {c.id: c for c in concepts}

        # Infer relationships
        edges = infer_relationships(concepts)

        # Build metadata
        metadata = self._build_metadata(concepts, edges)

        return ConceptGraph(nodes=nodes, edges=edges, metadata=metadata)

    def _build_metadata(
        self, concepts: list[Concept], edges: list
    ) -> dict[str, str | int | dict[str, int]]:
        """Build graph metadata with build time and statistics.

        Args:
            concepts: List of concepts in the graph.
            edges: List of relationships in the graph.

        Returns:
            Metadata dictionary with build info and statistics.
        """
        # Count edges by type
        edge_counts: dict[str, int] = {}
        for edge in edges:
            edge_counts[edge.type] = edge_counts.get(edge.type, 0) + 1

        return {
            "build_time": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "stats": {
                "total_nodes": len(concepts),
                "total_edges": len(edges),
                "edges_by_type": edge_counts,
            },
        }
