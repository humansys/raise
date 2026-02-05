"""Memory graph builder.

This module provides the MemoryGraph class and builder for constructing
graphs from memory concepts with inferred relationships.

.. deprecated::
    MemoryGraph and MemoryGraphBuilder are deprecated.
    Use UnifiedGraph from raise_cli.context instead.
"""

from __future__ import annotations

import warnings
from collections import deque
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryRelationship,
    MemoryRelationshipType,
)


class MemoryGraph(BaseModel):
    """In-memory graph of memory concepts.

    Represents a directed graph of memory concepts (patterns, calibrations,
    sessions) with semantic relationships.

    .. deprecated::
        Use UnifiedGraph from raise_cli.context instead.

    Attributes:
        nodes: Memory concepts indexed by ID.
        edges: Relationships between concepts.
        metadata: Graph metadata (build time, stats).
    """

    def __init__(self, **data: Any) -> None:
        """Initialize MemoryGraph with deprecation warning."""
        warnings.warn(
            "MemoryGraph is deprecated. Use UnifiedGraph from raise_cli.context instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**data)

    nodes: dict[str, MemoryConcept] = Field(
        default_factory=dict, description="Concepts indexed by ID"
    )
    edges: list[MemoryRelationship] = Field(
        default_factory=lambda: list[MemoryRelationship](),
        description="Relationships between concepts",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Graph metadata")

    def get_node(self, concept_id: str) -> MemoryConcept | None:
        """Get concept by ID.

        Args:
            concept_id: Unique concept identifier.

        Returns:
            MemoryConcept if found, None otherwise.
        """
        return self.nodes.get(concept_id)

    def get_outgoing_edges(
        self, concept_id: str, edge_type: MemoryRelationshipType | None = None
    ) -> list[MemoryRelationship]:
        """Get outgoing edges from a concept.

        Args:
            concept_id: Source concept ID.
            edge_type: Optional relationship type filter.

        Returns:
            List of outgoing relationships.
        """
        return [
            e
            for e in self.edges
            if e.source == concept_id and (edge_type is None or e.type == edge_type)
        ]

    def get_incoming_edges(
        self, concept_id: str, edge_type: MemoryRelationshipType | None = None
    ) -> list[MemoryRelationship]:
        """Get incoming edges to a concept.

        Args:
            concept_id: Target concept ID.
            edge_type: Optional relationship type filter.

        Returns:
            List of incoming relationships.
        """
        return [
            e
            for e in self.edges
            if e.target == concept_id and (edge_type is None or e.type == edge_type)
        ]

    def to_json(self) -> str:
        """Serialize graph to JSON.

        Returns:
            JSON string representation.
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> MemoryGraph:
        """Deserialize graph from JSON.

        Args:
            json_str: JSON string representation.

        Returns:
            Reconstructed MemoryGraph instance.
        """
        return cls.model_validate_json(json_str)


def traverse_bfs(
    graph: MemoryGraph,
    start_id: str,
    edge_types: list[MemoryRelationshipType] | None = None,
    max_depth: int = 3,
) -> list[MemoryConcept]:
    """BFS traversal from start node with depth limit.

    Args:
        graph: Memory graph to traverse.
        start_id: ID of the starting concept.
        edge_types: Optional list of relationship types to traverse.
        max_depth: Maximum traversal depth (default: 3).

    Returns:
        List of concepts discovered during traversal.
    """
    if start_id not in graph.nodes:
        return []

    visited: set[str] = {start_id}
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])
    result: list[MemoryConcept] = [graph.nodes[start_id]]

    while queue:
        current_id, depth = queue.popleft()

        if depth >= max_depth:
            continue

        edges = graph.get_outgoing_edges(current_id)
        if edge_types:
            edges = [e for e in edges if e.type in edge_types]

        for edge in edges:
            target_id = edge.target
            if target_id not in visited and target_id in graph.nodes:
                visited.add(target_id)
                result.append(graph.nodes[target_id])
                queue.append((target_id, depth + 1))

    return result


class MemoryGraphBuilder:
    """Builder for constructing memory graphs with inferred relationships.

    Builds a MemoryGraph from a list of MemoryConcepts, inferring relationships
    based on:
    - learned_from: pattern/calibration → session (explicit link)
    - related_to: shared context keywords
    - validates: calibration → pattern (same feature)
    - applies_to: pattern → context domains

    .. deprecated::
        Use UnifiedGraphBuilder from raise_cli.context.builder instead.
    """

    def __init__(self, min_shared_keywords: int = 2) -> None:
        """Initialize builder with deprecation warning.

        Args:
            min_shared_keywords: Minimum shared keywords for related_to inference.
        """
        warnings.warn(
            "MemoryGraphBuilder is deprecated. Use UnifiedGraphBuilder from raise_cli.context.builder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.min_shared_keywords = min_shared_keywords

    def build(self, concepts: list[MemoryConcept]) -> MemoryGraph:
        """Build a memory graph from concepts.

        Args:
            concepts: List of memory concepts.

        Returns:
            MemoryGraph with nodes and inferred relationships.
        """
        # Build nodes index
        nodes = {c.id: c for c in concepts}

        # Infer relationships
        edges: list[MemoryRelationship] = []
        edges.extend(self._infer_learned_from(concepts, nodes))
        edges.extend(self._infer_related_to(concepts))
        edges.extend(self._infer_validates(concepts, nodes))
        edges.extend(self._infer_applies_to(concepts))

        # Build metadata
        metadata = {
            "build_time": datetime.now().isoformat(),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "patterns": sum(1 for c in concepts if c.type == MemoryConceptType.PATTERN),
            "calibrations": sum(
                1 for c in concepts if c.type == MemoryConceptType.CALIBRATION
            ),
            "sessions": sum(1 for c in concepts if c.type == MemoryConceptType.SESSION),
        }

        return MemoryGraph(nodes=nodes, edges=edges, metadata=metadata)

    def _infer_learned_from(
        self, concepts: list[MemoryConcept], nodes: dict[str, MemoryConcept]
    ) -> list[MemoryRelationship]:
        """Infer learned_from relationships from metadata.

        Pattern/calibration → session based on learned_from or feature field.
        """
        relationships: list[MemoryRelationship] = []

        # Build session index by ID prefix
        sessions = {c.id: c for c in concepts if c.type == MemoryConceptType.SESSION}

        for concept in concepts:
            if concept.type == MemoryConceptType.SESSION:
                continue

            # Check learned_from in metadata
            learned_from = concept.metadata.get("learned_from")
            if learned_from:
                # Try to find matching session
                for session_id, session in sessions.items():
                    # Match if learned_from mentions session ID or topic keywords
                    topic = session.metadata.get("topic", "").lower()
                    if session_id in str(learned_from) or any(
                        word in str(learned_from).lower()
                        for word in topic.split()
                        if len(word) > 3
                    ):
                        relationships.append(
                            MemoryRelationship(
                                source=concept.id,
                                target=session_id,
                                type=MemoryRelationshipType.LEARNED_FROM,
                                metadata={"confidence": 0.8, "method": "metadata_link"},
                            )
                        )
                        break

        return relationships

    def _infer_related_to(
        self, concepts: list[MemoryConcept]
    ) -> list[MemoryRelationship]:
        """Infer related_to relationships from shared context keywords."""
        relationships: list[MemoryRelationship] = []
        seen_pairs: set[tuple[str, str]] = set()

        for i, c1 in enumerate(concepts):
            for c2 in concepts[i + 1 :]:
                # Skip if same type (patterns relate to calibrations, not other patterns)
                if c1.type == c2.type:
                    continue

                # Count shared keywords
                shared = set(c1.context) & set(c2.context)
                if len(shared) >= self.min_shared_keywords:
                    # Create sorted pair to avoid duplicates
                    sorted_ids = sorted([c1.id, c2.id])
                    pair: tuple[str, str] = (sorted_ids[0], sorted_ids[1])
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        relationships.append(
                            MemoryRelationship(
                                source=c1.id,
                                target=c2.id,
                                type=MemoryRelationshipType.RELATED_TO,
                                metadata={
                                    "confidence": min(len(shared) / 3, 1.0),
                                    "shared_keywords": list(shared),
                                },
                            )
                        )

        return relationships

    def _infer_validates(
        self, concepts: list[MemoryConcept], nodes: dict[str, MemoryConcept]
    ) -> list[MemoryRelationship]:
        """Infer validates relationships: calibration → pattern.

        Calibration data validates patterns when they share feature context.
        """
        relationships: list[MemoryRelationship] = []

        calibrations = [c for c in concepts if c.type == MemoryConceptType.CALIBRATION]
        patterns = [c for c in concepts if c.type == MemoryConceptType.PATTERN]

        for cal in calibrations:
            feature = cal.metadata.get("feature", "")
            if not feature:
                continue

            for pat in patterns:
                # Check if pattern was learned from this feature
                learned_from = pat.metadata.get("learned_from", "")
                if feature in str(learned_from):
                    relationships.append(
                        MemoryRelationship(
                            source=cal.id,
                            target=pat.id,
                            type=MemoryRelationshipType.VALIDATES,
                            metadata={"confidence": 0.9, "feature": feature},
                        )
                    )

        return relationships

    def _infer_applies_to(
        self, concepts: list[MemoryConcept]
    ) -> list[MemoryRelationship]:
        """Infer applies_to relationships: pattern → context domain.

        Patterns apply to their context domains (for future domain-based queries).
        Note: This creates conceptual edges, not edges to other concepts.
        For now, we skip this as we don't have domain nodes.
        """
        # Future: Create domain nodes and link patterns to them
        return []
