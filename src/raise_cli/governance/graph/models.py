"""Pydantic models for concept graph representation.

This module defines the core data structures for representing concept graphs,
including nodes (concepts), edges (relationships), and graph operations.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from raise_cli.governance.models import Concept

# Relationship types (E8: extended for work tracking)
RelationshipType = Literal[
    "implements",  # Requirement implements outcome
    "governed_by",  # Artifact governed by principle
    "depends_on",  # Concept depends on another
    "related_to",  # Semantic relationship
    "validates",  # Gate validates concept (future)
    "contains",  # Project contains Epic, Epic contains Feature (E8)
    "current_focus",  # Project's current active Epic (E8)
]


class Relationship(BaseModel):
    """Directed edge in concept graph.

    Represents a semantic relationship between two concepts in the
    governance graph.

    Attributes:
        source: Source concept ID (e.g., 'req-rf-05').
        target: Target concept ID (e.g., 'outcome-context-generation').
        type: Relationship type (implements, governed_by, etc.).
        metadata: Relationship metadata (confidence, inference method, etc.).

    Examples:
        >>> rel = Relationship(
        ...     source="req-rf-05",
        ...     target="outcome-context-generation",
        ...     type="implements",
        ...     metadata={"confidence": 0.8, "method": "keyword_match"}
        ... )
        >>> rel.source
        'req-rf-05'
        >>> rel.type
        'implements'
    """

    source: str = Field(..., description="Source concept ID")
    target: str = Field(..., description="Target concept ID")
    type: RelationshipType = Field(..., description="Relationship type")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Relationship metadata (e.g., confidence, source)",
    )


class ConceptGraph(BaseModel):
    """In-memory concept graph.

    Represents a directed graph of governance concepts with semantic
    relationships. Supports querying, traversal, and JSON serialization.

    Attributes:
        nodes: Concepts indexed by ID.
        edges: Relationships between concepts.
        metadata: Graph metadata (build time, version, stats).

    Examples:
        >>> from raise_cli.governance.models import Concept, ConceptType
        >>> concept = Concept(
        ...     id="req-rf-05",
        ...     type=ConceptType.REQUIREMENT,
        ...     file="prd.md",
        ...     section="RF-05",
        ...     lines=(1, 10),
        ...     content="..."
        ... )
        >>> graph = ConceptGraph(nodes={"req-rf-05": concept})
        >>> graph.get_node("req-rf-05")
        Concept(id='req-rf-05', ...)
    """

    nodes: dict[str, Concept] = Field(
        default_factory=dict, description="Concepts indexed by ID"
    )
    edges: list[Relationship] = Field(
        default_factory=list, description="Relationships between concepts"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Graph metadata (build time, version, stats)",
    )

    def get_node(self, concept_id: str) -> Concept | None:
        """Get concept by ID.

        Args:
            concept_id: Unique concept identifier.

        Returns:
            Concept if found, None otherwise.

        Examples:
            >>> graph = ConceptGraph(nodes={"req-rf-05": concept})
            >>> node = graph.get_node("req-rf-05")
            >>> node.id
            'req-rf-05'
        """
        return self.nodes.get(concept_id)

    def get_outgoing_edges(
        self, concept_id: str, edge_type: RelationshipType | None = None
    ) -> list[Relationship]:
        """Get outgoing edges from a concept.

        Args:
            concept_id: Source concept ID.
            edge_type: Optional relationship type filter.

        Returns:
            List of outgoing relationships.

        Examples:
            >>> edges = graph.get_outgoing_edges("req-rf-05")
            >>> edges = graph.get_outgoing_edges("req-rf-05", edge_type="implements")
        """
        edges: list[Relationship] = [
            e
            for e in self.edges
            if e.source == concept_id and (edge_type is None or e.type == edge_type)
        ]
        return edges

    def get_incoming_edges(
        self, concept_id: str, edge_type: RelationshipType | None = None
    ) -> list[Relationship]:
        """Get incoming edges to a concept.

        Args:
            concept_id: Target concept ID.
            edge_type: Optional relationship type filter.

        Returns:
            List of incoming relationships.

        Examples:
            >>> edges = graph.get_incoming_edges("outcome-context-generation")
            >>> edges = graph.get_incoming_edges("outcome-X", edge_type="implements")
        """
        edges: list[Relationship] = [
            e
            for e in self.edges
            if e.target == concept_id and (edge_type is None or e.type == edge_type)
        ]
        return edges

    def to_json(self) -> str:
        """Serialize graph to JSON.

        Returns:
            JSON string representation of the graph.

        Examples:
            >>> json_str = graph.to_json()
            >>> "nodes" in json_str and "edges" in json_str
            True
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> ConceptGraph:
        """Deserialize graph from JSON.

        Args:
            json_str: JSON string representation.

        Returns:
            Reconstructed ConceptGraph instance.

        Examples:
            >>> json_str = graph.to_json()
            >>> loaded = ConceptGraph.from_json(json_str)
            >>> len(loaded.nodes) == len(graph.nodes)
            True
        """
        return cls.model_validate_json(json_str)
