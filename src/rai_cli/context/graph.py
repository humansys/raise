"""Unified context graph implementation.

This module provides the UnifiedGraph class that wraps NetworkX MultiDiGraph
for storing and querying cross-domain concepts. This is a pure in-memory graph;
persistence is handled by KnowledgeGraphBackend implementations (ADR-036).

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from rai_cli.context.models import (
    ConceptEdge,
    ConceptNode,
    EdgeType,
    GraphNode,
    NodeType,
)

logger = logging.getLogger(__name__)


class UnifiedGraph:
    """NetworkX-based unified context graph.

    Wraps a NetworkX MultiDiGraph to provide typed operations for adding,
    retrieving, and persisting concepts and relationships.

    Attributes:
        graph: The underlying NetworkX MultiDiGraph.

    Examples:
        >>> graph = UnifiedGraph()
        >>> node = ConceptNode(
        ...     id="PAT-001",
        ...     type="pattern",
        ...     content="Test pattern",
        ...     created="2026-02-03"
        ... )
        >>> graph.add_concept(node)
        >>> graph.node_count
        1
    """

    def __init__(self) -> None:
        """Initialize an empty unified graph."""
        self.graph: nx.MultiDiGraph[str] = nx.MultiDiGraph()

    def _reconstruct_node(self, node_id: str, data: dict[str, Any]) -> GraphNode:
        """Reconstruct a typed GraphNode from serialized dict."""
        data["id"] = node_id
        node_type = data.get("type", "")
        cls = GraphNode.registered_types().get(node_type)
        if cls:
            return cls.model_validate(data)
        if node_type:
            logger.warning(
                "Node type '%s' not registered (missing plugin?). "
                "Run 'rai memory build' to regenerate graph.",
                node_type,
            )
        return GraphNode.model_validate(data)

    def add_concept(self, node: ConceptNode) -> None:
        """Add a concept node to the graph.

        Args:
            node: The concept node to add.

        Examples:
            >>> graph = UnifiedGraph()
            >>> node = ConceptNode(
            ...     id="PAT-001",
            ...     type="pattern",
            ...     content="Test",
            ...     created="2026-02-03"
            ... )
            >>> graph.add_concept(node)
            >>> graph.get_concept("PAT-001") is not None
            True
        """
        self.graph.add_node(node.id, **node.model_dump())

    def add_relationship(self, edge: ConceptEdge) -> None:
        """Add a relationship edge to the graph.

        Args:
            edge: The concept edge to add.

        Examples:
            >>> graph = UnifiedGraph()
            >>> edge = ConceptEdge(
            ...     source="PAT-001",
            ...     target="SES-015",
            ...     type="learned_from"
            ... )
            >>> graph.add_relationship(edge)
            >>> graph.edge_count
            1
        """
        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            weight=edge.weight,
            **edge.metadata,
        )

    def get_concept(self, concept_id: str) -> ConceptNode | None:
        """Get a concept by ID.

        Args:
            concept_id: The unique concept identifier.

        Returns:
            The ConceptNode if found, None otherwise.

        Examples:
            >>> node = graph.get_concept("PAT-001")
            >>> node.type if node else None
            'pattern'
        """
        if concept_id not in self.graph.nodes:
            return None
        data = dict(self.graph.nodes[concept_id])
        return self._reconstruct_node(concept_id, data)

    def get_concepts_by_type(self, node_type: NodeType) -> list[ConceptNode]:
        """Get all concepts of a specific type.

        Args:
            node_type: The node type to filter by.

        Returns:
            List of ConceptNode instances matching the type.

        Examples:
            >>> patterns = graph.get_concepts_by_type("pattern")
            >>> all(p.type == "pattern" for p in patterns)
            True
        """
        concepts: list[ConceptNode] = []
        node_id: str
        for node_id in self.graph.nodes:
            data: dict[str, Any] = dict(self.graph.nodes[node_id])
            if data.get("type") == node_type:
                concepts.append(self._reconstruct_node(node_id, data))
        return concepts

    def get_neighbors(
        self,
        concept_id: str,
        depth: int = 1,
        edge_types: list[EdgeType] | None = None,
    ) -> list[ConceptNode]:
        """Get neighboring concepts via BFS traversal.

        Args:
            concept_id: Starting concept ID.
            depth: Maximum traversal depth (default 1).
            edge_types: Optional filter for edge types.

        Returns:
            List of neighboring ConceptNode instances.

        Examples:
            >>> neighbors = graph.get_neighbors("PAT-001", depth=2)
            >>> len(neighbors) >= 0
            True
        """
        if concept_id not in self.graph.nodes:
            return []

        visited: set[str] = {concept_id}
        current_level: set[str] = {concept_id}
        neighbors: list[ConceptNode] = []

        for _ in range(depth):
            next_level: set[str] = set()
            for nid in current_level:
                # Get outgoing edges
                out_edge: tuple[str, str, dict[str, Any]]
                for out_edge in self.graph.out_edges(nid, data=True):
                    target: str = out_edge[1]
                    edge_data: dict[str, Any] = out_edge[2]
                    edge_matches = (
                        edge_types is None or edge_data.get("type") in edge_types
                    )
                    if edge_matches and target not in visited:
                        visited.add(target)
                        next_level.add(target)
                # Get incoming edges
                in_edge: tuple[str, str, dict[str, Any]]
                for in_edge in self.graph.in_edges(nid, data=True):
                    source: str = in_edge[0]
                    edge_data = in_edge[2]
                    edge_matches = (
                        edge_types is None or edge_data.get("type") in edge_types
                    )
                    if edge_matches and source not in visited:
                        visited.add(source)
                        next_level.add(source)
            current_level = next_level

        # Convert to ConceptNode instances
        node_id: str
        for node_id in visited:
            if node_id != concept_id:
                concept = self.get_concept(node_id)
                if concept:
                    neighbors.append(concept)

        return neighbors

    def iter_concepts(self) -> Iterator[ConceptNode]:
        """Iterate over all concepts in the graph.

        Skips nodes that fail deserialization (e.g. schema drift from a removed
        plugin) and emits a warning instead of crashing. See RAISE-136.

        Yields:
            ConceptNode instances for each node.

        Examples:
            >>> for concept in graph.iter_concepts():
            ...     print(concept.id)
        """
        node_id: str
        for node_id in self.graph.nodes:
            data: dict[str, Any] = dict(self.graph.nodes[node_id])
            try:
                yield self._reconstruct_node(node_id, data)
            except Exception as e:
                logger.warning(
                    "Skipping node '%s' (type=%s): %s",
                    node_id,
                    data.get("type", "unknown"),
                    e,
                )

    def iter_relationships(self) -> Iterator[ConceptEdge]:
        """Iterate over all relationships in the graph.

        Yields:
            ConceptEdge instances for each edge.

        Examples:
            >>> for edge in graph.iter_relationships():
            ...     print(f"{edge.source} -> {edge.target}")
        """
        edge_tuple: tuple[str, str, dict[str, Any]]
        for edge_tuple in self.graph.edges(data=True):
            source: str = edge_tuple[0]
            target: str = edge_tuple[1]
            data: dict[str, Any] = edge_tuple[2]
            edge_type: str = data.get("type", "related_to")
            weight: float = float(data.get("weight", 1.0))
            metadata: dict[str, Any] = {
                k: v for k, v in data.items() if k not in ("type", "weight")
            }
            yield ConceptEdge(
                source=source,
                target=target,
                type=edge_type,
                weight=weight,
                metadata=metadata,
            )

    @property
    def node_count(self) -> int:
        """Get the number of nodes in the graph.

        Returns:
            Number of concept nodes.
        """
        return self.graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        """Get the number of edges in the graph.

        Returns:
            Number of relationship edges.
        """
        return self.graph.number_of_edges()

