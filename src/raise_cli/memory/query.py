"""Memory query engine with keyword search, BFS, and recency weighting.

This module provides MemoryQuery for searching memory concepts
using keyword matching, graph traversal, and recency scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import perf_counter

from pydantic import BaseModel, Field

from raise_cli.memory.builder import MemoryGraph, traverse_bfs
from raise_cli.memory.cache import MemoryCache
from raise_cli.memory.models import (
    MemoryConcept,
    MemoryRelationship,
    MemoryRelationshipType,
)


class MemoryQueryResult(BaseModel):
    """Result of a memory query.

    Attributes:
        concepts: List of matching concepts.
        relationships: Relationships between matched concepts.
        token_estimate: Estimated token count for results.
        query_time_ms: Query execution time in milliseconds.
        total_nodes: Total nodes in the graph.
        matched_nodes: Number of directly matched nodes.
    """

    concepts: list[MemoryConcept] = Field(default_factory=lambda: list[MemoryConcept]())
    relationships: list[MemoryRelationship] = Field(
        default_factory=lambda: list[MemoryRelationship]()
    )
    token_estimate: int = Field(default=0)
    query_time_ms: float = Field(default=0.0)
    total_nodes: int = Field(default=0)
    matched_nodes: int = Field(default=0)


@dataclass
class ScoredConcept:
    """A concept with a relevance score for ranking."""

    concept: MemoryConcept
    score: float
    match_type: str  # "keyword", "traversal", "both"


class MemoryQuery:
    """Query engine for memory graph with keyword search and recency weighting.

    Searches memory concepts using:
    1. Keyword matching in content and context
    2. BFS traversal from matched concepts
    3. Recency weighting (newer entries score higher)

    Attributes:
        graph: The memory graph to search.
        recency_weight: Weight for recency scoring (0.0-1.0).
    """

    # Common stopwords to filter from keyword matching
    STOPWORDS = frozenset(
        [
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
        ]
    )

    def __init__(self, graph: MemoryGraph, recency_weight: float = 0.3) -> None:
        """Initialize query engine.

        Args:
            graph: Memory graph to search.
            recency_weight: Weight for recency scoring (0.0-1.0, default: 0.3).
        """
        self.graph = graph
        self.recency_weight = max(0.0, min(1.0, recency_weight))
        self._today = date.today()

    def _extract_keywords(self, query: str) -> set[str]:
        """Extract keywords from query string.

        Args:
            query: Query string.

        Returns:
            Set of lowercase keywords (stopwords removed).
        """
        words = query.lower().split()
        return {w for w in words if len(w) > 2 and w not in self.STOPWORDS}

    def _calculate_recency_score(self, concept: MemoryConcept) -> float:
        """Calculate recency score for a concept.

        Newer concepts get higher scores (exponential decay over 30 days).

        Args:
            concept: The concept to score.

        Returns:
            Recency score (0.0-1.0).
        """
        days_old = (self._today - concept.created).days
        # Exponential decay: score halves every 30 days
        return 0.5 ** (days_old / 30)

    def _calculate_keyword_score(
        self, concept: MemoryConcept, keywords: set[str]
    ) -> float:
        """Calculate keyword match score for a concept.

        Args:
            concept: The concept to score.
            keywords: Query keywords.

        Returns:
            Keyword match score (0.0-1.0).
        """
        if not keywords:
            return 0.0

        # Search in content and context
        content_lower = concept.content.lower()
        context_set = {c.lower() for c in concept.context}

        matches = 0
        for kw in keywords:
            if kw in content_lower:
                matches += 1
            elif kw in context_set:
                matches += 0.8  # Slightly lower weight for context match

        return min(matches / len(keywords), 1.0)

    def _find_keyword_matches(
        self, keywords: set[str], min_score: float = 0.3
    ) -> list[ScoredConcept]:
        """Find concepts matching keywords.

        Args:
            keywords: Query keywords.
            min_score: Minimum keyword score to include.

        Returns:
            List of scored concepts above minimum score.
        """
        matches: list[ScoredConcept] = []

        for concept in self.graph.nodes.values():
            kw_score = self._calculate_keyword_score(concept, keywords)
            if kw_score >= min_score:
                recency = self._calculate_recency_score(concept)
                # Combined score: (1 - recency_weight) * keyword + recency_weight * recency
                combined = (1 - self.recency_weight) * kw_score + (
                    self.recency_weight * recency
                )
                matches.append(
                    ScoredConcept(concept=concept, score=combined, match_type="keyword")
                )

        return matches

    def _expand_with_traversal(
        self, seed_ids: set[str], max_depth: int = 2
    ) -> list[MemoryConcept]:
        """Expand seed concepts via BFS traversal.

        Args:
            seed_ids: IDs of seed concepts.
            max_depth: Maximum traversal depth.

        Returns:
            List of concepts discovered via traversal.
        """
        discovered: set[str] = set()

        for seed_id in seed_ids:
            concepts = traverse_bfs(
                self.graph,
                seed_id,
                edge_types=[
                    MemoryRelationshipType.LEARNED_FROM,
                    MemoryRelationshipType.RELATED_TO,
                    MemoryRelationshipType.VALIDATES,
                ],
                max_depth=max_depth,
            )
            for c in concepts:
                if c.id not in seed_ids:
                    discovered.add(c.id)

        return [self.graph.nodes[cid] for cid in discovered if cid in self.graph.nodes]

    def _collect_relationships(self, concept_ids: set[str]) -> list[MemoryRelationship]:
        """Collect relationships between a set of concepts.

        Args:
            concept_ids: Set of concept IDs.

        Returns:
            List of relationships where both source and target are in the set.
        """
        return [
            edge
            for edge in self.graph.edges
            if edge.source in concept_ids and edge.target in concept_ids
        ]

    def _estimate_tokens(self, concepts: list[MemoryConcept]) -> int:
        """Estimate token count for a list of concepts.

        Args:
            concepts: List of concepts.

        Returns:
            Estimated token count.
        """
        return sum(c.token_estimate for c in concepts)

    def search(
        self,
        query: str,
        max_results: int = 10,
        expand_traversal: bool = True,
        max_depth: int = 2,
    ) -> MemoryQueryResult:
        """Search memory graph for relevant concepts.

        Args:
            query: Search query (keywords).
            max_results: Maximum number of results.
            expand_traversal: Whether to expand via BFS traversal.
            max_depth: Maximum traversal depth for expansion.

        Returns:
            MemoryQueryResult with matching concepts and metadata.
        """
        start_time = perf_counter()

        # Extract keywords
        keywords = self._extract_keywords(query)
        if not keywords:
            # No valid keywords, return empty result
            return MemoryQueryResult(
                total_nodes=len(self.graph.nodes),
                query_time_ms=(perf_counter() - start_time) * 1000,
            )

        # Find keyword matches
        matches = self._find_keyword_matches(keywords)
        matched_ids = {m.concept.id for m in matches}
        matched_count = len(matched_ids)

        # Optionally expand via traversal
        if expand_traversal and matches:
            expanded = self._expand_with_traversal(matched_ids, max_depth)
            # Add expanded concepts with lower scores
            for concept in expanded:
                recency = self._calculate_recency_score(concept)
                matches.append(
                    ScoredConcept(
                        concept=concept,
                        score=0.3 * recency,  # Lower base score for traversal
                        match_type="traversal",
                    )
                )

        # Sort by score descending and limit
        matches.sort(key=lambda m: m.score, reverse=True)
        top_matches = matches[:max_results]

        # Collect concepts and relationships
        concepts = [m.concept for m in top_matches]
        concept_ids = {c.id for c in concepts}
        relationships = self._collect_relationships(concept_ids)

        # Calculate metrics
        query_time = (perf_counter() - start_time) * 1000
        token_estimate = self._estimate_tokens(concepts)

        return MemoryQueryResult(
            concepts=concepts,
            relationships=relationships,
            token_estimate=token_estimate,
            query_time_ms=query_time,
            total_nodes=len(self.graph.nodes),
            matched_nodes=matched_count,
        )


def create_memory_query(
    memory_dir: Path, recency_weight: float = 0.3
) -> tuple[MemoryQuery, MemoryGraph]:
    """Create a MemoryQuery from a memory directory.

    Convenience function that loads/caches the graph and creates a query engine.

    Args:
        memory_dir: Path to .rai/memory/ directory.
        recency_weight: Weight for recency scoring.

    Returns:
        Tuple of (MemoryQuery, MemoryGraph).
    """
    cache = MemoryCache(memory_dir)
    graph = cache.get_graph()
    query = MemoryQuery(graph, recency_weight)
    return query, graph
