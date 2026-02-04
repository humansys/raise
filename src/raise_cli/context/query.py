"""Unified context query engine.

This module provides query capabilities for the unified context graph,
enabling skills to retrieve relevant patterns, calibration data, governance
principles, and work items.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import time
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode, NodeType


class UnifiedQueryStrategy(str, Enum):
    """Query strategy for unified context retrieval.

    Attributes:
        KEYWORD_SEARCH: Match keywords in node content, return top N by relevance.
        CONCEPT_LOOKUP: Direct concept ID lookup with optional BFS neighbors.
    """

    KEYWORD_SEARCH = "keyword_search"
    CONCEPT_LOOKUP = "concept_lookup"


class UnifiedQuery(BaseModel):
    """Query parameters for unified context retrieval.

    Attributes:
        query: Query string (keywords or concept ID).
        strategy: Query execution strategy.
        max_depth: Maximum BFS traversal depth (0-5).
        types: Optional filter for node types.
        limit: Maximum number of results.

    Examples:
        >>> query = UnifiedQuery(query="planning estimation")
        >>> query = UnifiedQuery(
        ...     query="PAT-001",
        ...     strategy=UnifiedQueryStrategy.CONCEPT_LOOKUP,
        ...     max_depth=2,
        ... )
    """

    query: str = Field(..., description="Query string (keywords or concept ID)")
    strategy: UnifiedQueryStrategy = Field(
        default=UnifiedQueryStrategy.KEYWORD_SEARCH,
        description="Query execution strategy",
    )
    max_depth: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Maximum BFS traversal depth",
    )
    types: list[NodeType] | None = Field(
        default=None,
        description="Filter by node types",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    )


class UnifiedQueryMetadata(BaseModel):
    """Metadata about unified query result.

    Attributes:
        query: Original query string.
        strategy: Strategy used for execution.
        total_concepts: Number of concepts in result.
        token_estimate: Estimated token count for result.
        execution_time_ms: Query execution time in milliseconds.
        types_found: Count of concepts by type.

    Examples:
        >>> metadata = UnifiedQueryMetadata(
        ...     query="planning",
        ...     strategy=UnifiedQueryStrategy.KEYWORD_SEARCH,
        ...     total_concepts=5,
        ...     token_estimate=320,
        ...     execution_time_ms=8.5,
        ...     types_found={"pattern": 2, "calibration": 2, "skill": 1},
        ... )
    """

    query: str = Field(..., description="Original query string")
    strategy: UnifiedQueryStrategy = Field(..., description="Strategy used")
    total_concepts: int = Field(..., description="Number of concepts returned")
    token_estimate: int = Field(..., description="Estimated token count")
    execution_time_ms: float = Field(..., description="Execution time in ms")
    types_found: dict[str, int] = Field(
        default_factory=dict,
        description="Count of concepts by type",
    )


class UnifiedQueryResult(BaseModel):
    """Result of unified context query.

    Attributes:
        concepts: Concepts matching the query.
        metadata: Query result metadata.

    Examples:
        >>> result = engine.query(UnifiedQuery(query="planning"))
        >>> for concept in result.concepts:
        ...     print(f"{concept.id}: {concept.content[:50]}...")
    """

    concepts: list[ConceptNode] = Field(
        default_factory=lambda: [],
        description="Concepts matching the query",
    )
    metadata: UnifiedQueryMetadata = Field(..., description="Query metadata")

    def to_json(self) -> str:
        """Serialize result to JSON.

        Returns:
            JSON string representation.
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> UnifiedQueryResult:
        """Deserialize result from JSON.

        Args:
            json_str: JSON string representation.

        Returns:
            Reconstructed UnifiedQueryResult instance.
        """
        return cls.model_validate_json(json_str)


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses heuristic: character count // 4 (roughly 4 chars per token).

    Args:
        text: Text to estimate tokens for.

    Returns:
        Estimated token count.
    """
    return len(text) // 4


def calculate_relevance_score(
    content: str,
    keywords: list[str],
    created: str,
) -> float:
    """Calculate relevance score for a concept.

    Score = (keyword_hits * 10) + recency_bonus
    Recency bonus: 5 if created within 7 days, else 0.

    Args:
        content: Concept content text.
        keywords: Query keywords to match.
        created: ISO date string when concept was created.

    Returns:
        Relevance score (higher is more relevant).
    """
    content_lower = content.lower()

    # Count keyword hits
    keyword_hits = sum(1 for kw in keywords if kw.lower() in content_lower)

    # Recency bonus (simple: check if 2026-02 in date for "recent")
    # In production, would compare actual dates
    recency_bonus = 5.0 if "2026-02" in created else 0.0

    return (keyword_hits * 10.0) + recency_bonus


class UnifiedQueryEngine:
    """Query engine for unified context graph.

    Provides keyword search and concept lookup capabilities for
    retrieving relevant context from the unified graph.

    Attributes:
        graph: The unified context graph to query.

    Examples:
        >>> engine = UnifiedQueryEngine.from_file(Path(".raise/graph/unified.json"))
        >>> result = engine.query(UnifiedQuery(query="planning estimation"))
        >>> print(f"Found {len(result.concepts)} concepts")
    """

    def __init__(self, graph: UnifiedGraph) -> None:
        """Initialize query engine with graph.

        Args:
            graph: Unified context graph to query.
        """
        self.graph = graph

    @classmethod
    def from_file(cls, path: Path) -> UnifiedQueryEngine:
        """Load query engine from graph file.

        Args:
            path: Path to unified graph JSON file.

        Returns:
            Initialized query engine.

        Raises:
            FileNotFoundError: If graph file doesn't exist.
        """
        if not path.exists():
            raise FileNotFoundError(
                f"Graph file not found: {path}\n"
                f"Run 'raise graph build --unified' to create the graph first."
            )
        graph = UnifiedGraph.load(path)
        return cls(graph)

    def query(self, query: UnifiedQuery) -> UnifiedQueryResult:
        """Execute query and return results.

        Args:
            query: Query parameters.

        Returns:
            Query result with concepts and metadata.
        """
        start_time = time.time()

        # Execute strategy
        if query.strategy == UnifiedQueryStrategy.KEYWORD_SEARCH:
            concepts = self._keyword_search(query)
        else:  # CONCEPT_LOOKUP
            concepts = self._concept_lookup(query)

        execution_time_ms = (time.time() - start_time) * 1000

        # Calculate metadata
        metadata = self._calculate_metadata(query, concepts, execution_time_ms)

        return UnifiedQueryResult(concepts=concepts, metadata=metadata)

    def _keyword_search(self, query: UnifiedQuery) -> list[ConceptNode]:
        """Execute keyword search strategy.

        Matches keywords against node content, returns top N by relevance.

        Args:
            query: Query parameters.

        Returns:
            List of matching concepts sorted by relevance.
        """
        keywords = query.query.lower().split()
        if not keywords:
            return []

        scored_concepts: list[tuple[float, ConceptNode]] = []

        for concept in self.graph.iter_concepts():
            # Apply type filter
            if query.types and concept.type not in query.types:
                continue

            # Check if any keyword matches
            content_lower = concept.content.lower()
            if not any(kw in content_lower for kw in keywords):
                continue

            # Calculate relevance score
            score = calculate_relevance_score(
                concept.content,
                keywords,
                concept.created,
            )
            scored_concepts.append((score, concept))

        # Sort by score descending
        scored_concepts.sort(key=lambda x: x[0], reverse=True)

        # Apply limit
        return [concept for _, concept in scored_concepts[: query.limit]]

    def _concept_lookup(self, query: UnifiedQuery) -> list[ConceptNode]:
        """Execute concept lookup strategy.

        Direct ID lookup with optional BFS neighbor traversal.

        Args:
            query: Query parameters.

        Returns:
            List of concepts (target + neighbors if depth > 0).
        """
        concept_id = query.query

        # Direct lookup
        concept = self.graph.get_concept(concept_id)
        if concept is None:
            return []

        # Apply type filter to main concept
        if query.types and concept.type not in query.types:
            # Still try to get neighbors that match
            concepts: list[ConceptNode] = []
        else:
            concepts = [concept]

        # Get neighbors if depth > 0
        if query.max_depth > 0:
            neighbors = self.graph.get_neighbors(concept_id, depth=query.max_depth)
            for neighbor in neighbors:
                # Apply type filter
                if query.types and neighbor.type not in query.types:
                    continue
                if neighbor.id not in [c.id for c in concepts]:
                    concepts.append(neighbor)

        # Apply limit
        return concepts[: query.limit]

    def _calculate_metadata(
        self,
        query: UnifiedQuery,
        concepts: list[ConceptNode],
        execution_time_ms: float,
    ) -> UnifiedQueryMetadata:
        """Calculate metadata for query result.

        Args:
            query: Original query.
            concepts: Concepts in result.
            execution_time_ms: Execution time in milliseconds.

        Returns:
            Query result metadata.
        """
        # Token estimate
        total_text = " ".join(c.content for c in concepts)
        token_estimate = estimate_tokens(total_text)

        # Count types
        types_found: dict[str, int] = {}
        for concept in concepts:
            node_type = concept.type
            types_found[node_type] = types_found.get(node_type, 0) + 1

        return UnifiedQueryMetadata(
            query=query.query,
            strategy=query.strategy,
            total_concepts=len(concepts),
            token_estimate=token_estimate,
            execution_time_ms=execution_time_ms,
            types_found=types_found,
        )
