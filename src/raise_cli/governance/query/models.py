"""Pydantic models for MVC query system.

This module defines the data structures for querying the concept graph
and representing query results.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.governance.models import Concept


class QueryStrategy(str, Enum):
    """Query strategy for MVC extraction.

    Attributes:
        CONCEPT_LOOKUP: Direct concept ID lookup with dependencies.
        KEYWORD_SEARCH: Keyword matching across concepts.
        RELATIONSHIP_TRAVERSAL: Follow specific relationship types.
        RELATED_CONCEPTS: Semantic similarity via shared keywords.
    """

    CONCEPT_LOOKUP = "concept_lookup"
    KEYWORD_SEARCH = "keyword_search"
    RELATIONSHIP_TRAVERSAL = "relationship_traversal"
    RELATED_CONCEPTS = "related_concepts"


class ContextQuery(BaseModel):
    """MVC query parameters.

    Represents a query for extracting Minimum Viable Context from the
    concept graph.

    Attributes:
        query: Query string (concept ID, keywords, or natural language).
        strategy: Query execution strategy.
        max_depth: Maximum graph traversal depth (0-5).
        filters: Query filters (type, edge_types, confidence_threshold, etc.).

    Examples:
        >>> # Direct concept lookup
        >>> query = ContextQuery(query="req-rf-05", strategy=QueryStrategy.CONCEPT_LOOKUP)
        >>> # Keyword search in requirements only
        >>> query = ContextQuery(
        ...     query="validation",
        ...     strategy=QueryStrategy.KEYWORD_SEARCH,
        ...     filters={"type": "requirement"}
        ... )
        >>> # Traverse governed_by relationships
        >>> query = ContextQuery(
        ...     query="req-rf-05",
        ...     strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
        ...     filters={"edge_types": ["governed_by"]},
        ...     max_depth=2
        ... )
    """

    query: str = Field(..., description="Query string (concept ID or keywords)")
    strategy: QueryStrategy = Field(
        default=QueryStrategy.CONCEPT_LOOKUP,
        description="Query execution strategy",
    )
    max_depth: int = Field(
        default=1, ge=0, le=5, description="Maximum traversal depth"
    )
    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Query filters (type, edge_types, confidence_threshold)",
    )


class ContextMetadata(BaseModel):
    """Metadata about MVC query result.

    Attributes:
        query: Original query string.
        strategy: Strategy used for execution.
        total_concepts: Number of concepts in result.
        token_estimate: Estimated token count for result.
        traversal_depth: Actual graph traversal depth.
        paths: Relationship paths from query to results.
        execution_time_ms: Query execution time in milliseconds.

    Examples:
        >>> metadata = ContextMetadata(
        ...     query="req-rf-05",
        ...     strategy=QueryStrategy.CONCEPT_LOOKUP,
        ...     total_concepts=3,
        ...     token_estimate=350,
        ...     traversal_depth=1,
        ...     paths=[["req-rf-05", "principle-governance-as-code"]],
        ...     execution_time_ms=12.5
        ... )
        >>> metadata.token_estimate
        350
    """

    query: str = Field(..., description="Original query")
    strategy: QueryStrategy = Field(..., description="Strategy used")
    total_concepts: int = Field(..., description="Number of concepts returned")
    token_estimate: int = Field(..., description="Estimated token count")
    traversal_depth: int = Field(..., description="Actual depth traversed")
    paths: list[list[str]] = Field(
        default_factory=list,
        description="Relationship paths from query to results",
    )
    execution_time_ms: float = Field(..., description="Execution time in ms")


class ContextResult(BaseModel):
    """MVC query result with concepts and metadata.

    Represents the result of a Minimum Viable Context query, including
    the concepts that match the query and metadata about the result.

    Attributes:
        concepts: Concepts included in the MVC.
        metadata: Result metadata (token count, paths, execution time).

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
        >>> result = ContextResult(
        ...     concepts=[concept],
        ...     metadata=ContextMetadata(
        ...         query="req-rf-05",
        ...         strategy=QueryStrategy.CONCEPT_LOOKUP,
        ...         total_concepts=1,
        ...         token_estimate=100,
        ...         traversal_depth=0,
        ...         paths=[],
        ...         execution_time_ms=5.0
        ...     )
        ... )
        >>> len(result.concepts)
        1
    """

    concepts: list[Concept] = Field(
        default_factory=list, description="Concepts included in MVC"
    )
    metadata: ContextMetadata = Field(..., description="Result metadata")

    def to_json(self) -> str:
        """Serialize result to JSON.

        Returns:
            JSON string representation.

        Examples:
            >>> result = ContextResult(concepts=[], metadata=...)
            >>> json_str = result.to_json()
            >>> "concepts" in json_str and "metadata" in json_str
            True
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> ContextResult:
        """Deserialize result from JSON.

        Args:
            json_str: JSON string representation.

        Returns:
            Reconstructed ContextResult instance.

        Examples:
            >>> json_str = result.to_json()
            >>> loaded = ContextResult.from_json(json_str)
            >>> len(loaded.concepts) == len(result.concepts)
            True
        """
        return cls.model_validate_json(json_str)

    def to_file(self, path: Path, format: str = "markdown") -> None:
        """Save result to file.

        Args:
            path: Output file path.
            format: Output format ("markdown" or "json").

        Examples:
            >>> from pathlib import Path
            >>> result.to_file(Path("context.md"), format="markdown")
            >>> result.to_file(Path("context.json"), format="json")
        """
        if format == "markdown":
            from raise_cli.governance.query.formatters import format_markdown

            content = format_markdown(self)
            path.write_text(content)
        else:
            path.write_text(self.to_json())
