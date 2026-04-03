"""Retrieval models and DomainAdapter protocol.

All domain-agnostic types for the retrieval engine live here:
data models (DomainHints, TraversalAdvice, ScoredNode, RetrievalResult)
and the DomainAdapter Protocol that domain-specific adapters implement.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from raise_core.graph.models import GraphNode


class DomainHints(BaseModel):
    """Query interpretation hints from a domain adapter.

    Base model with extra="allow" so unknown domains can pass
    arbitrary fields without schema changes.
    """

    model_config = ConfigDict(extra="allow")

    domain: str = Field(..., description="Domain identifier (e.g. 'scaleup', 'gtd')")


class TraversalAdvice(BaseModel):
    """Adapter's recommendation for how the engine should traverse the graph."""

    start_node_ids: list[str] = Field(
        default_factory=list,
        description="Seed node IDs to start traversal from",
    )
    edge_type_filter: list[str] | None = Field(
        default=None,
        description="Edge types to follow (None = all)",
    )
    node_type_filter: list[str] | None = Field(
        default=None,
        description="Node types to include in results (None = all)",
    )
    max_depth: int = Field(
        default=2,
        description="Maximum BFS traversal depth",
    )
    edge_weights: dict[str, float] = Field(
        default_factory=dict,
        description="Edge type → weight for SA propagation (empty = uniform 1.0)",
    )


class ScoredNode(BaseModel):
    """A graph node with a relevance score and explanation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node: GraphNode = Field(..., description="The graph node")
    score: float = Field(..., description="Composite relevance score (0.0–1.0)")
    explanation: str = Field(default="", description="Human-readable scoring breakdown")

    def __lt__(self, other: ScoredNode) -> bool:
        return self.score < other.score

    def __gt__(self, other: ScoredNode) -> bool:
        return self.score > other.score

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScoredNode):
            return NotImplemented
        return self.score == other.score

    def __le__(self, other: ScoredNode) -> bool:
        return self.score <= other.score

    def __ge__(self, other: ScoredNode) -> bool:
        return self.score >= other.score


class RetrievalResult(BaseModel):
    """Result of a retrieval query."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    nodes: list[ScoredNode] = Field(
        default_factory=lambda: list[ScoredNode](),
        description="Scored nodes, sorted by relevance",
    )
    query: str = Field(..., description="Original query text")
    hints: DomainHints | None = Field(
        default=None, description="Domain hints used (if any)"
    )


@runtime_checkable
class DomainAdapter(Protocol):
    """Protocol for domain-specific retrieval adapters.

    Adapters ADVISE the engine — they never traverse the graph themselves.
    Three-step contract: interpret → advise → annotate.
    """

    def interpret_query(self, query: str) -> DomainHints:
        """Parse a natural-language query into structured domain hints."""
        ...

    def advise_traversal(
        self, hints: DomainHints, available_types: frozenset[str]
    ) -> TraversalAdvice:
        """Recommend traversal strategy based on interpreted hints."""
        ...

    def annotate_results(
        self, nodes: list[GraphNode], hints: DomainHints
    ) -> list[ScoredNode]:
        """Attach domain-specific scoring metadata to traversed nodes."""
        ...
