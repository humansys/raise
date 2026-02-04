"""MVC Query Engine for extracting Minimum Viable Context from concept graphs.

This module orchestrates the query process: load graph, execute strategy,
calculate metadata, and return formatted results.
"""

from __future__ import annotations

import time
from pathlib import Path

from raise_cli.governance.graph.models import ConceptGraph
from raise_cli.governance.models import Concept
from raise_cli.governance.query.formatters import estimate_tokens
from raise_cli.governance.query.models import (
    ContextMetadata,
    ContextQuery,
    ContextResult,
    QueryStrategy,
)
from raise_cli.governance.query.strategies import (
    query_concept_lookup,
    query_keyword_search,
    query_related_concepts,
    query_relationship_traversal,
)


class ContextQueryEngine:
    """Query engine for extracting Minimum Viable Context from concept graphs.

    Orchestrates the query workflow: strategy selection, graph traversal,
    metadata calculation, and result formatting.

    Attributes:
        graph: Concept graph to query.

    Examples:
        >>> from raise_cli.governance.query import ContextQueryEngine, ContextQuery
        >>> engine = ContextQueryEngine.from_cache()
        >>> result = engine.query(ContextQuery(query="req-rf-05"))
        >>> print(f"Tokens: {result.metadata.token_estimate}")
    """

    def __init__(self, graph: ConceptGraph) -> None:
        """Initialize query engine with concept graph.

        Args:
            graph: Concept graph to query.
        """
        self.graph = graph

    @classmethod
    def from_cache(
        cls, cache_path: Path = Path(".raise/cache/graph.json")
    ) -> ContextQueryEngine:
        """Load query engine from cached graph file.

        Args:
            cache_path: Path to cached graph JSON (default: .raise/cache/graph.json).

        Returns:
            Initialized query engine.

        Raises:
            FileNotFoundError: If graph file doesn't exist.

        Examples:
            >>> engine = ContextQueryEngine.from_cache()
            >>> engine = ContextQueryEngine.from_cache(Path("custom/graph.json"))
        """
        if not cache_path.exists():
            raise FileNotFoundError(
                f"Graph file not found: {cache_path}\n"
                f"Run 'raise graph build' to create the graph first."
            )

        json_str = cache_path.read_text()
        graph = ConceptGraph.from_json(json_str)

        return cls(graph)

    def query(self, query: ContextQuery) -> ContextResult:
        """Execute MVC query and return result.

        Orchestrates: strategy execution → metadata calculation → result creation.

        Args:
            query: Query parameters.

        Returns:
            Query result with concepts and metadata.

        Examples:
            >>> result = engine.query(ContextQuery(query="req-rf-05"))
            >>> result = engine.query(ContextQuery(
            ...     query="validation",
            ...     strategy=QueryStrategy.KEYWORD_SEARCH,
            ...     filters={"type": "requirement"}
            ... ))
        """
        # Track execution time
        start_time = time.time()

        # Execute strategy
        concepts = self._execute_strategy(query)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Calculate metadata
        metadata = self._calculate_metadata(
            query, concepts, execution_time_ms
        )

        return ContextResult(concepts=concepts, metadata=metadata)

    def _execute_strategy(self, query: ContextQuery) -> list[Concept]:
        """Execute query strategy and return matching concepts.

        Args:
            query: Query parameters.

        Returns:
            List of concepts matching the query.
        """
        strategy = query.strategy

        if strategy == QueryStrategy.CONCEPT_LOOKUP:
            edge_types = query.filters.get("edge_types", ["governed_by", "implements"])
            return query_concept_lookup(
                self.graph,
                query.query,
                max_depth=query.max_depth,
                edge_types=edge_types,
            )

        elif strategy == QueryStrategy.KEYWORD_SEARCH:
            concept_type = query.filters.get("type")
            limit = query.filters.get("limit", 10)
            return query_keyword_search(
                self.graph,
                query.query,
                concept_type=concept_type,
                limit=limit,
            )

        elif strategy == QueryStrategy.RELATIONSHIP_TRAVERSAL:
            edge_types = query.filters.get("edge_types", ["governed_by", "implements"])
            return query_relationship_traversal(
                self.graph,
                query.query,
                edge_types=edge_types,
                max_depth=query.max_depth,
            )

        elif strategy == QueryStrategy.RELATED_CONCEPTS:
            min_shared = query.filters.get("min_shared_keywords", 2)
            limit = query.filters.get("limit", 5)
            return query_related_concepts(
                self.graph,
                query.query,
                min_shared_keywords=min_shared,
                limit=limit,
            )

        # Default: empty result
        return []

    def _calculate_metadata(
        self, query: ContextQuery, concepts: list[Concept], execution_time_ms: float
    ) -> ContextMetadata:
        """Calculate metadata for query result.

        Args:
            query: Original query.
            concepts: Concepts in result.
            execution_time_ms: Execution time in milliseconds.

        Returns:
            Query result metadata.
        """
        # Estimate tokens
        total_text = " ".join(c.section + " " + c.content for c in concepts)
        token_estimate = estimate_tokens(total_text)

        # Trace relationship paths
        paths = self._trace_paths(query, concepts)

        # Determine actual traversal depth
        traversal_depth = len(max(paths, default=[])) - 1 if paths else 0

        return ContextMetadata(
            query=query.query,
            strategy=query.strategy,
            total_concepts=len(concepts),
            token_estimate=token_estimate,
            traversal_depth=traversal_depth,
            paths=paths,
            execution_time_ms=execution_time_ms,
        )

    def _trace_paths(
        self, query: ContextQuery, concepts: list[Concept]
    ) -> list[list[str]]:
        """Trace relationship paths from query concept to result concepts.

        Args:
            query: Original query.
            concepts: Result concepts.

        Returns:
            List of paths (each path is a list of concept IDs).
        """
        paths: list[list[str]] = []

        # Only trace paths for strategies that follow relationships
        if query.strategy not in [
            QueryStrategy.CONCEPT_LOOKUP,
            QueryStrategy.RELATIONSHIP_TRAVERSAL,
        ]:
            return paths

        # Find query concept ID
        from raise_cli.governance.query.strategies import normalize_concept_id

        query_id = normalize_concept_id(query.query)

        # If query concept not in graph, no paths
        if query_id not in self.graph.nodes:
            return paths

        # For each result concept, find path from query concept
        for concept in concepts:
            if concept.id == query_id:
                # Query concept itself
                continue

            # Find direct relationship
            edges = self.graph.get_outgoing_edges(query_id)
            for edge in edges:
                if edge.target == concept.id:
                    paths.append([query_id, concept.id])
                    break

        return paths
