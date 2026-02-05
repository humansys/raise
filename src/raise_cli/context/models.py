"""Pydantic models for unified context graph.

This module defines the core data structures for the unified context graph
that merges governance, memory, and work concepts into a single queryable
structure.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# Node types for unified context graph
NodeType = Literal[
    "pattern",  # PAT-* — learned patterns from memory
    "calibration",  # CAL-* — velocity/estimation data
    "session",  # SES-* — session history records
    "principle",  # §N — constitution principles
    "requirement",  # RF-* — PRD requirements
    "outcome",  # OUT-* — vision outcomes
    "project",  # PRJ-* — project definitions
    "epic",  # E* — epic scopes
    "feature",  # F*.* — feature work items
    "skill",  # /name — skill metadata
    "decision",  # ADR-* — architecture decisions (E12)
    "guardrail",  # GR-* — code standards (E12)
    "term",  # TERM-* — glossary definitions (E12)
    "component",  # comp-* — discovered code components (E13)
]

# Edge types for relationships between concepts
EdgeType = Literal[
    "learned_from",  # pattern → session (memory origin)
    "governed_by",  # requirement → principle (governance link)
    "applies_to",  # pattern → skill (usage context)
    "needs_context",  # skill → concept types (context requirements)
    "implements",  # feature → requirement (traceability)
    "part_of",  # feature → epic (hierarchy)
    "related_to",  # generic semantic relationship
]


class ConceptNode(BaseModel):
    """A node in the unified context graph.

    Represents any concept type (pattern, principle, skill, etc.) with
    its content and metadata. All concept types share this schema.

    Attributes:
        id: Unique identifier (e.g., 'PAT-001', '§2', 'F11.1', '/feature-plan').
        type: Node type from NodeType literal.
        content: Main text content or description.
        source_file: Path to source file (if applicable).
        created: ISO timestamp when concept was created.
        metadata: Type-specific additional attributes.

    Examples:
        >>> node = ConceptNode(
        ...     id="PAT-001",
        ...     type="pattern",
        ...     content="Singleton with get/set/configure pattern",
        ...     source_file=".raise/rai/memory/patterns.jsonl",
        ...     created="2026-01-31",
        ...     metadata={"sub_type": "codebase", "context": ["testing"]}
        ... )
        >>> node.id
        'PAT-001'
        >>> node.type
        'pattern'
    """

    id: str = Field(..., description="Unique identifier (e.g., 'PAT-001', '§2')")
    type: NodeType = Field(..., description="Node type")
    content: str = Field(..., description="Main text content or description")
    source_file: str | None = Field(default=None, description="Path to source file")
    created: str = Field(..., description="ISO timestamp when created")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific attributes"
    )

    @property
    def token_estimate(self) -> int:
        """Estimate tokens for this concept.

        Returns:
            Estimated token count (content length // 4).
        """
        return len(self.content) // 4


class ConceptEdge(BaseModel):
    """An edge in the unified context graph.

    Represents a directed relationship between two concepts.

    Attributes:
        source: Source node ID.
        target: Target node ID.
        type: Relationship type from EdgeType literal.
        weight: Edge weight for ranking (default 1.0).
        metadata: Additional relationship attributes.

    Examples:
        >>> edge = ConceptEdge(
        ...     source="PAT-001",
        ...     target="SES-015",
        ...     type="learned_from",
        ...     weight=1.0,
        ...     metadata={"confidence": 0.9}
        ... )
        >>> edge.source
        'PAT-001'
        >>> edge.type
        'learned_from'
    """

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Edge weight for ranking")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional relationship attributes"
    )
