"""Knowledge graph query engine.

Provides query capabilities for the knowledge graph, enabling skills to
retrieve relevant patterns, calibration data, governance principles,
and work items.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import time
from datetime import date
from enum import StrEnum
from math import exp, log, sqrt
from typing import Any

from pydantic import BaseModel, Field

from raise_core.graph.engine import Graph
from raise_core.graph.models import EdgeType, GraphNode, NodeType

# --- Scoring constants ---
SCORING_HALF_LIFE_DAYS: int = 30
SCORING_W_RECENCY: float = 0.3
SCORING_W_RELEVANCE: float = 0.7
SCORING_WILSON_Z: float = 1.96
SCORING_LOW_WILSON_THRESHOLD: float = 0.15
SCORING_MISSION_BOOST_FACTOR: float = 1.5


class QueryStrategy(StrEnum):
    """Query strategy for context retrieval.

    Attributes:
        KEYWORD_SEARCH: Match keywords in node content, return top N by relevance.
        KEYWORD_SEARCH_FORCED: Keyword search forced by absent semantic index.
            Functionally identical to KEYWORD_SEARCH but signals that semantic
            retrieval was requested and unavailable (RAISE-15987).
        CONCEPT_LOOKUP: Direct concept ID lookup with optional BFS neighbors.
    """

    KEYWORD_SEARCH = "keyword_search"
    KEYWORD_SEARCH_FORCED = "keyword_search_forced"
    CONCEPT_LOOKUP = "concept_lookup"


class Query(BaseModel):
    """Query parameters for context retrieval.

    Attributes:
        query: Query string (keywords or concept ID).
        strategy: Query execution strategy.
        max_depth: Maximum BFS traversal depth (0-5).
        types: Optional filter for node types.
        limit: Maximum number of results.

    Examples:
        >>> query = Query(query="planning estimation")
        >>> query = Query(
        ...     query="PAT-001",
        ...     strategy=QueryStrategy.CONCEPT_LOOKUP,
        ...     max_depth=2,
        ... )
    """

    query: str = Field(..., description="Query string (keywords or concept ID)")
    strategy: QueryStrategy = Field(
        default=QueryStrategy.KEYWORD_SEARCH,
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
    subtypes: list[str] | None = Field(
        default=None,
        description="Filter by pattern subtypes (approach, risk, etc.)",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    )
    module: str | None = Field(
        default=None,
        description="Filter by module ID (metadata.module)",
    )
    file: str | None = Field(
        default=None,
        description="Filter by source file (substring match on source_file)",
    )
    cartridge: str | None = Field(
        default=None,
        description="Filter by cartridge name (metadata.cartridge)",
    )
    callers: bool = Field(
        default=False,
        description="Reverse lookup — return callers of matched symbols via calls edges",
    )


class ArchitecturalContext(BaseModel):
    """Full architectural context for a module.

    Combines domain (bounded context), layer, constraints (guardrails),
    and dependencies into a single structured result.
    """

    module: GraphNode
    domain: GraphNode | None = None
    layer: GraphNode | None = None
    constraints: list[GraphNode] = Field(default_factory=lambda: [])
    dependencies: list[GraphNode] = Field(default_factory=lambda: [])


class QueryMetadata(BaseModel):
    """Metadata about query result.

    Attributes:
        query: Original query string.
        strategy: Strategy used for execution.
        total_concepts: Number of concepts in result.
        total_available: Total matching concepts before limit applied.
        token_estimate: Estimated token count for result.
        execution_time_ms: Query execution time in milliseconds.
        types_found: Count of concepts by type.
    """

    query: str = Field(..., description="Original query string")
    strategy: QueryStrategy = Field(..., description="Strategy used")
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


class QueryResult(BaseModel):
    """Result of context query.

    Attributes:
        concepts: Concepts matching the query.
        metadata: Query result metadata.
    """

    concepts: list[GraphNode] = Field(
        default_factory=lambda: [],
        description="Concepts matching the query",
    )
    metadata: QueryMetadata = Field(..., description="Query metadata")

    def to_json(self) -> str:
        """Serialize result to JSON."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> QueryResult:
        """Deserialize result from JSON."""
        return cls.model_validate_json(json_str)


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses heuristic: character count // 4 (roughly 4 chars per token).
    """
    return len(text) // 4


def wilson_lower_bound(
    positives: int,
    negatives: int,
    z: float = SCORING_WILSON_Z,
) -> float:
    """Compute Wilson score lower bound for binary ratings.

    Proven at Reddit/Yelp/Amazon scale. Conservative with small sample sizes —
    the correct approach for patterns with few evaluations.

    Args:
        positives: Number of positive evaluations.
        negatives: Number of negative evaluations.
        z: Z-score for confidence level (default: 1.96 = 95%).

    Returns:
        Wilson lower bound in [0, 1].

    Raises:
        ValueError: If total observations is 0.
    """
    n = positives + negatives
    if n == 0:
        raise ValueError("Cannot compute Wilson lower bound with 0 observations")
    p_hat = positives / n
    z2 = z * z
    numerator = (
        p_hat + z2 / (2 * n) - z * sqrt((p_hat * (1 - p_hat) + z2 / (4 * n)) / n)
    )
    denominator = 1 + z2 / n
    return numerator / denominator


def calculate_relevance_score(
    content: str,
    keywords: list[str],
    created: str,
    metadata: dict[str, Any] | None = None,
) -> float:
    """Calculate composite relevance score for a concept.

    Foundational patterns (foundational=True or base=True) are exempt from
    temporal decay and score on keyword relevance only. All other patterns use:
        score = (w_r * recency + w_k * keyword_relevance) * wilson_modifier

    Where recency uses half-life exponential decay (H=30d) and wilson_modifier
    is the Wilson score lower bound of positive evaluations.
    """
    if metadata is None:
        metadata = {}

    content_lower = content.lower()

    # Normalized keyword relevance
    if keywords:
        hits = sum(1 for kw in keywords if kw.lower() in content_lower)
        relevance = hits / len(keywords)
    else:
        relevance = 0.0

    # Foundational patterns: exempt from decay — check both field names (PAT-E-153)
    if metadata.get("foundational") or metadata.get("base"):
        return round(relevance, 4)

    # Recency: half-life exponential decay
    try:
        created_date = date.fromisoformat(created[:10])
        age_days = max(0, (date.today() - created_date).days)
    except (ValueError, IndexError):
        age_days = 0
    recency = exp(-log(2) / SCORING_HALF_LIFE_DAYS * age_days)

    base = SCORING_W_RECENCY * recency + SCORING_W_RELEVANCE * relevance

    # Wilson validation modifier
    evaluations = metadata.get("evaluations") or 0
    if not evaluations:
        return round(base, 4)

    positives = metadata.get("positives") or 0
    negatives = metadata.get("negatives") or 0
    if positives + negatives == 0:
        return round(base, 4)  # defensive guard for data inconsistency

    modifier = wilson_lower_bound(positives, negatives)
    return round(base * modifier, 4)


class QueryEngine:
    """Query engine for the knowledge graph.

    Provides keyword search and concept lookup capabilities for
    retrieving relevant context from the graph.

    Attributes:
        graph: The knowledge graph to query.

    Examples:
        >>> engine = QueryEngine(graph)
        >>> result = engine.query(Query(query="planning estimation"))
        >>> print(f"Found {len(result.concepts)} concepts")
    """

    def __init__(
        self,
        graph: Graph,
        boost_ids: set[str] | None = None,
        boost_factor: float = SCORING_MISSION_BOOST_FACTOR,
    ) -> None:
        """Initialize query engine with graph.

        Args:
            graph: Knowledge graph to query.
            boost_ids: Node IDs to boost in keyword search scoring.
            boost_factor: Multiplier for boosted nodes (default 1.5).
        """
        self.graph = graph
        self.boost_ids = boost_ids
        self.boost_factor = boost_factor

    def query(self, query: Query) -> QueryResult:
        """Execute query and return results."""
        start_time = time.time()

        # Execute strategy
        if query.strategy in (
            QueryStrategy.KEYWORD_SEARCH,
            QueryStrategy.KEYWORD_SEARCH_FORCED,
        ):
            concepts, total_available = self._keyword_search(query)
        else:  # CONCEPT_LOOKUP
            concepts, total_available = self._concept_lookup(query)

        # Callers reverse lookup: replace results with their callers
        if query.callers and concepts:
            concepts = self._resolve_callers(concepts, query)
            total_available = len(concepts)

        execution_time_ms = (time.time() - start_time) * 1000

        # Calculate metadata
        metadata = self._calculate_metadata(
            query, concepts, execution_time_ms, total_available
        )

        return QueryResult(concepts=concepts, metadata=metadata)

    @staticmethod
    def _passes_keyword_filters(concept: GraphNode, query: Query) -> bool:
        """Apply type/subtype/module/file/cartridge filters for keyword search."""
        if query.types and concept.type not in query.types:
            return False
        if query.subtypes and concept.metadata.get("sub_type") not in query.subtypes:
            return False
        if query.module and concept.metadata.get("module") != query.module:
            return False
        if query.file and query.file not in (concept.source_file or ""):
            return False
        return not (
            query.cartridge and concept.metadata.get("cartridge") != query.cartridge
        )

    def _keyword_search(self, query: Query) -> tuple[list[GraphNode], int]:
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

        # RAISE-11150: a query equal (case-insensitive) to a node's own id
        # must resolve that node — deterministically, not merely "somewhere
        # in the results". Including id in the searchable text below is not
        # enough on a large corpus: another node whose content happens to
        # also mention this id can out-score the node itself (verified
        # against production data, ~9K nodes). An exact id match short-
        # circuits to a sentinel score guaranteeing rank 0.
        exact_query = query.query.strip().lower()

        scored_concepts: list[tuple[float, GraphNode]] = []

        for concept in self.graph.iter_concepts():
            if not self._passes_keyword_filters(concept, query):
                continue

            if concept.id.lower() == exact_query:
                scored_concepts.append((float("inf"), concept))
                continue

            # Check if any keyword matches (include node id and type in
            # searchable text — RAISE-11150: also lets partial/id-adjacent
            # queries surface a node, matching the precedent already set
            # by raise-server's search_nodes full-text concat)
            searchable = f"{concept.id} {concept.type} {concept.content}".lower()
            if not any(kw in searchable for kw in keywords):
                continue

            # Calculate relevance score
            score = calculate_relevance_score(
                concept.content,
                keywords,
                concept.created,
                concept.metadata,
            )
            if self.boost_ids and concept.id in self.boost_ids:
                score = round(score * self.boost_factor, 4)
            scored_concepts.append((score, concept))

        # Sort by score descending
        scored_concepts.sort(key=lambda x: x[0], reverse=True)

        total_available = len(scored_concepts)

        # Apply limit
        limited = [concept for _, concept in scored_concepts[: query.limit]]
        return limited, total_available

    def _concept_lookup(self, query: Query) -> tuple[list[GraphNode], int]:
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
            concepts: list[GraphNode] = []
        elif (
            query.subtypes
            and concept.metadata.get("sub_type") not in query.subtypes
            or (
                query.cartridge and concept.metadata.get("cartridge") != query.cartridge
            )
        ):
            concepts = []
        else:
            concepts = [concept]

        # Get neighbors if depth > 0
        if query.max_depth > 0:
            neighbors = self.graph.get_neighbors(
                concept_id, depth=query.max_depth, edge_types=query.edge_types
            )
            for neighbor in neighbors:
                if query.types and neighbor.type not in query.types:
                    continue
                if (
                    query.subtypes
                    and neighbor.metadata.get("sub_type") not in query.subtypes
                ):
                    continue
                if (
                    query.cartridge
                    and neighbor.metadata.get("cartridge") != query.cartridge
                ):
                    continue
                if neighbor.id not in [c.id for c in concepts]:
                    concepts.append(neighbor)

        total_available = len(concepts)

        # Apply limit
        return concepts[: query.limit], total_available

    def _resolve_callers(
        self, matched: list[GraphNode], query: Query
    ) -> list[GraphNode]:
        """Find callers of matched symbols via 'calls' edges."""
        caller_ids: set[str] = set()
        matched_ids = {c.id for c in matched}

        for node_id in matched_ids:
            if node_id not in self.graph.graph.nodes:
                continue
            for source, _, edge_data in self.graph.graph.in_edges(node_id, data=True):
                if edge_data.get("type") == "calls" and source not in matched_ids:
                    caller_ids.add(source)

        callers: list[GraphNode] = []
        for cid in caller_ids:
            node = self.graph.get_concept(cid)
            if node is None:
                continue
            if query.module and node.metadata.get("module") != query.module:
                continue
            if query.file and query.file not in (node.source_file or ""):
                continue
            callers.append(node)

        return callers[: query.limit]

    def _calculate_metadata(
        self,
        query: Query,
        concepts: list[GraphNode],
        execution_time_ms: float,
        total_available: int,
    ) -> QueryMetadata:
        """Calculate metadata for query result."""
        total_text = " ".join(c.content for c in concepts)
        token_estimate = estimate_tokens(total_text)

        types_found: dict[str, int] = {}
        for concept in concepts:
            node_type = concept.type
            types_found[node_type] = types_found.get(node_type, 0) + 1

        return QueryMetadata(
            query=query.query,
            strategy=query.strategy,
            total_concepts=len(concepts),
            total_available=total_available,
            token_estimate=token_estimate,
            execution_time_ms=execution_time_ms,
            types_found=types_found,
        )

    # =========================================================================
    # Architectural Context Helpers
    # =========================================================================

    def find_domain_for(self, module_id: str) -> GraphNode | None:
        """Find the bounded context a module belongs to."""
        neighbors = self.graph.get_neighbors(
            module_id, depth=1, edge_types=["belongs_to"]
        )
        for node in neighbors:
            if node.type == "bounded_context":
                return node
        return None

    def find_layer_for(self, module_id: str) -> GraphNode | None:
        """Find the architectural layer a module belongs to."""
        neighbors = self.graph.get_neighbors(
            module_id, depth=1, edge_types=["in_layer"]
        )
        for node in neighbors:
            if node.type == "layer":
                return node
        return None

    def find_constraints_for(self, module_id: str) -> list[GraphNode]:
        """Find all guardrails that constrain a module."""
        domain = self.find_domain_for(module_id)
        if domain is None:
            return []

        neighbors = self.graph.get_neighbors(
            domain.id, depth=1, edge_types=["constrained_by"]
        )
        return [n for n in neighbors if n.type == "guardrail"]

    def find_release_for(self, epic_id: str) -> GraphNode | None:
        """Find the release an epic belongs to.

        Follows outgoing ``part_of`` edge from the epic node to find
        a release node.

        Args:
            epic_id: Epic node ID (e.g., ``"epic-e19"``).

        Returns:
            The release node, or None if not found.
        """
        neighbors = self.graph.get_neighbors(epic_id, depth=1, edge_types=["part_of"])
        for node in neighbors:
            if node.type == "release":
                return node
        return None

    def get_architectural_context(self, module_id: str) -> ArchitecturalContext | None:
        """Get full architectural context for a module.

        Combines domain, layer, constraints, and dependencies into a
        single structured result.

        Args:
            module_id: Module node ID (e.g., ``"mod-memory"``, or
                ``"mod-raise-core--memory"`` — package-qualified ids in a
                packages/* monorepo, RAISE-16033).

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
