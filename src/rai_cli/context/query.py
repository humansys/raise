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

from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import ConceptNode, EdgeType, NodeType


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
    edge_types: list[EdgeType] | None = Field(
        default=None,
        description="Filter by edge types (concept_lookup only)",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    )


class ArchitecturalContext(BaseModel):
    """Full architectural context for a module.

    Combines domain (bounded context), layer, constraints (guardrails),
    and dependencies into a single structured result.

    Attributes:
        module: The module node.
        domain: Bounded context the module belongs to (via belongs_to edge).
        layer: Architectural layer (via in_layer edge).
        constraints: Guardrails applicable via the module's bounded context.
        dependencies: Modules this module depends on (via depends_on edge).

    Examples:
        >>> ctx = engine.get_architectural_context("mod-memory")
        >>> ctx.module.id
        'mod-memory'
        >>> ctx.domain.id if ctx.domain else None
        'bc-ontology'
    """

    module: ConceptNode
    domain: ConceptNode | None = None
    layer: ConceptNode | None = None
    constraints: list[ConceptNode] = Field(default_factory=lambda: [])
    dependencies: list[ConceptNode] = Field(default_factory=lambda: [])


class UnifiedQueryMetadata(BaseModel):
    """Metadata about unified query result.

    Attributes:
        query: Original query string.
        strategy: Strategy used for execution.
        total_concepts: Number of concepts in result.
        total_available: Total matching concepts before limit applied.
        token_estimate: Estimated token count for result.
        execution_time_ms: Query execution time in milliseconds.
        types_found: Count of concepts by type.

    Examples:
        >>> metadata = UnifiedQueryMetadata(
        ...     query="planning",
        ...     strategy=UnifiedQueryStrategy.KEYWORD_SEARCH,
        ...     total_concepts=5,
        ...     total_available=12,
        ...     token_estimate=320,
        ...     execution_time_ms=8.5,
        ...     types_found={"pattern": 2, "calibration": 2, "skill": 1},
        ... )
    """

    query: str = Field(..., description="Original query string")
    strategy: UnifiedQueryStrategy = Field(..., description="Strategy used")
    total_concepts: int = Field(..., description="Number of concepts returned")
    total_available: int = Field(
        0, description="Total matching concepts before limit applied"
    )
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
                f"Memory index not found: {path}\n"
                f"Run 'raise memory build' to create the index first."
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
            concepts, total_available = self._keyword_search(query)
        else:  # CONCEPT_LOOKUP
            concepts, total_available = self._concept_lookup(query)

        execution_time_ms = (time.time() - start_time) * 1000

        # Calculate metadata
        metadata = self._calculate_metadata(
            query, concepts, execution_time_ms, total_available
        )

        return UnifiedQueryResult(concepts=concepts, metadata=metadata)

    def _keyword_search(
        self, query: UnifiedQuery
    ) -> tuple[list[ConceptNode], int]:
        """Execute keyword search strategy.

        Matches keywords against node content, returns top N by relevance.

        Args:
            query: Query parameters.

        Returns:
            Tuple of (matching concepts sorted by relevance, total matches before limit).
        """
        keywords = query.query.lower().split()
        if not keywords:
            return [], 0

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

        total_available = len(scored_concepts)

        # Apply limit
        limited = [concept for _, concept in scored_concepts[: query.limit]]
        return limited, total_available

    def _concept_lookup(
        self, query: UnifiedQuery
    ) -> tuple[list[ConceptNode], int]:
        """Execute concept lookup strategy.

        Direct ID lookup with optional BFS neighbor traversal.

        Args:
            query: Query parameters.

        Returns:
            Tuple of (concepts list, total matches before limit).
        """
        concept_id = query.query

        # Direct lookup
        concept = self.graph.get_concept(concept_id)
        if concept is None:
            return [], 0

        # Apply type filter to main concept
        if query.types and concept.type not in query.types:
            # Still try to get neighbors that match
            concepts: list[ConceptNode] = []
        else:
            concepts = [concept]

        # Get neighbors if depth > 0
        if query.max_depth > 0:
            neighbors = self.graph.get_neighbors(
                concept_id, depth=query.max_depth, edge_types=query.edge_types
            )
            for neighbor in neighbors:
                # Apply type filter
                if query.types and neighbor.type not in query.types:
                    continue
                if neighbor.id not in [c.id for c in concepts]:
                    concepts.append(neighbor)

        total_available = len(concepts)

        # Apply limit
        return concepts[: query.limit], total_available

    def _calculate_metadata(
        self,
        query: UnifiedQuery,
        concepts: list[ConceptNode],
        execution_time_ms: float,
        total_available: int,
    ) -> UnifiedQueryMetadata:
        """Calculate metadata for query result.

        Args:
            query: Original query.
            concepts: Concepts in result.
            execution_time_ms: Execution time in milliseconds.
            total_available: Total matching concepts before limit applied.

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
            total_available=total_available,
            token_estimate=token_estimate,
            execution_time_ms=execution_time_ms,
            types_found=types_found,
        )

    # =========================================================================
    # Architectural Context Helpers (S15.5)
    # =========================================================================

    def find_domain_for(self, module_id: str) -> ConceptNode | None:
        """Find the bounded context a module belongs to.

        Follows outgoing ``belongs_to`` edge from the module node.

        Args:
            module_id: Module node ID (e.g., ``"mod-memory"``).

        Returns:
            The bounded context node, or None if not found.
        """
        neighbors = self.graph.get_neighbors(
            module_id, depth=1, edge_types=["belongs_to"]
        )
        for node in neighbors:
            if node.type == "bounded_context":
                return node
        return None

    def find_layer_for(self, module_id: str) -> ConceptNode | None:
        """Find the architectural layer a module belongs to.

        Follows outgoing ``in_layer`` edge from the module node.

        Args:
            module_id: Module node ID (e.g., ``"mod-memory"``).

        Returns:
            The layer node, or None if not found.
        """
        neighbors = self.graph.get_neighbors(
            module_id, depth=1, edge_types=["in_layer"]
        )
        for node in neighbors:
            if node.type == "layer":
                return node
        return None

    def find_constraints_for(self, module_id: str) -> list[ConceptNode]:
        """Find all guardrails that constrain a module.

        Two-hop traversal: module → ``belongs_to`` → bounded context →
        ``constrained_by`` → guardrails.

        Args:
            module_id: Module node ID (e.g., ``"mod-memory"``).

        Returns:
            List of guardrail nodes. Empty if module has no domain.
        """
        domain = self.find_domain_for(module_id)
        if domain is None:
            return []

        neighbors = self.graph.get_neighbors(
            domain.id, depth=1, edge_types=["constrained_by"]
        )
        return [n for n in neighbors if n.type == "guardrail"]

    def find_release_for(self, epic_id: str) -> ConceptNode | None:
        """Find the release an epic belongs to.

        Follows outgoing ``part_of`` edge from the epic node to find
        a release node.

        Args:
            epic_id: Epic node ID (e.g., ``"epic-e19"``).

        Returns:
            The release node, or None if not found.
        """
        neighbors = self.graph.get_neighbors(
            epic_id, depth=1, edge_types=["part_of"]
        )
        for node in neighbors:
            if node.type == "release":
                return node
        return None

    def get_architectural_context(
        self, module_id: str
    ) -> ArchitecturalContext | None:
        """Get full architectural context for a module.

        Combines domain, layer, constraints, and dependencies into a
        single structured result.

        Args:
            module_id: Module node ID (e.g., ``"mod-memory"``).

        Returns:
            ArchitecturalContext with all available information,
            or None if module doesn't exist.
        """
        module = self.graph.get_concept(module_id)
        if module is None:
            return None

        domain = self.find_domain_for(module_id)
        layer = self.find_layer_for(module_id)
        constraints = self.find_constraints_for(module_id)

        # Dependencies: modules connected via depends_on
        dep_neighbors = self.graph.get_neighbors(
            module_id, depth=1, edge_types=["depends_on"]
        )
        dependencies = [n for n in dep_neighbors if n.type == "module"]

        return ArchitecturalContext(
            module=module,
            domain=domain,
            layer=layer,
            constraints=constraints,
            dependencies=dependencies,
        )
