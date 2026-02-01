"""Graph traversal utilities for concept graphs.

This module provides breadth-first search (BFS) traversal for concept graphs,
supporting depth limits and edge type filtering.
"""

from __future__ import annotations

from collections import deque

from raise_cli.governance.graph.models import ConceptGraph, RelationshipType
from raise_cli.governance.models import Concept


def traverse_bfs(
    graph: ConceptGraph,
    start_id: str,
    edge_types: list[RelationshipType] | None = None,
    max_depth: int = 3,
) -> list[Concept]:
    """BFS traversal from start node with depth limit.

    Performs breadth-first search traversal of the concept graph starting
    from the given concept ID, optionally filtering by edge types and
    respecting a maximum depth limit.

    Args:
        graph: Concept graph to traverse.
        start_id: ID of the starting concept.
        edge_types: Optional list of relationship types to traverse.
            If None, all edge types are traversed.
        max_depth: Maximum traversal depth (default: 3).

    Returns:
        List of concepts discovered during traversal, including start concept.

    Examples:
        >>> graph = ConceptGraph(...)
        >>> # Traverse all edges up to depth 2
        >>> concepts = traverse_bfs(graph, "req-rf-05", max_depth=2)
        >>> # Traverse only 'governed_by' edges
        >>> principles = traverse_bfs(
        ...     graph, "req-rf-05",
        ...     edge_types=["governed_by"],
        ...     max_depth=2
        ... )
    """
    if start_id not in graph.nodes:
        return []

    visited: set[str] = {start_id}
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])  # (concept_id, depth)
    result: list[Concept] = [graph.nodes[start_id]]

    while queue:
        current_id, depth = queue.popleft()

        # Stop if we've reached max depth
        if depth >= max_depth:
            continue

        # Get outgoing edges (optionally filtered by type)
        edges = graph.get_outgoing_edges(current_id)
        if edge_types:
            edges = [e for e in edges if e.type in edge_types]

        # Add unvisited neighbors to queue
        for edge in edges:
            target_id = edge.target
            if target_id not in visited and target_id in graph.nodes:
                visited.add(target_id)
                result.append(graph.nodes[target_id])
                queue.append((target_id, depth + 1))

    return result
