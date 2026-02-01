"""Query strategy implementations for MVC extraction.

This module implements the 4 core query strategies:
- CONCEPT_LOOKUP: Direct ID lookup with dependencies
- KEYWORD_SEARCH: Keyword matching with type filtering
- RELATIONSHIP_TRAVERSAL: Follow specific edge types
- RELATED_CONCEPTS: Semantic similarity via keywords
"""

from __future__ import annotations

import re

from raise_cli.governance.graph.models import ConceptGraph, RelationshipType
from raise_cli.governance.models import Concept


def normalize_concept_id(query: str) -> str:
    """Normalize concept ID from various formats.

    Converts user-friendly formats (RF-05, §2) to canonical IDs.

    Args:
        query: Query string (may be RF-05, req-rf-05, §2, etc.).

    Returns:
        Normalized concept ID.

    Examples:
        >>> normalize_concept_id("RF-05")
        'req-rf-05'
        >>> normalize_concept_id("req-rf-05")
        'req-rf-05'
        >>> normalize_concept_id("§2")
        'principle-governance-as-code'
    """
    # Already normalized
    if query.startswith(("req-", "outcome-", "principle-")):
        return query

    # RF-XX format → req-rf-xx
    if re.match(r"^RF-\d+$", query, re.IGNORECASE):
        return f"req-{query.lower()}"

    # §N format → look up by section (handled by caller)
    return query.lower().replace(" ", "-")


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text.

    Args:
        text: Text to extract keywords from.

    Returns:
        Set of lowercase keywords (>3 chars, no stopwords).

    Examples:
        >>> keywords = extract_keywords("The system MUST validate inputs")
        >>> "system" in keywords
        True
        >>> "the" in keywords
        False
    """
    stopwords = {
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
        "with",
        "from",
        "must",
        "should",
        "will",
        "can",
        "may",
    }
    words = re.findall(r"\b\w+\b", text.lower())
    return {w for w in words if len(w) > 3 and w not in stopwords}


def query_concept_lookup(
    graph: ConceptGraph,
    query: str,
    max_depth: int = 1,
    edge_types: list[RelationshipType] | None = None,
) -> list[Concept]:
    """Lookup concept by ID and include immediate dependencies.

    Strategy: Direct lookup + 1-hop traversal for dependencies.

    Args:
        graph: Concept graph to query.
        query: Concept ID or user-friendly ID (RF-05, §2, etc.).
        max_depth: Maximum traversal depth (default: 1).
        edge_types: Edge types to follow (default: governed_by, implements).

    Returns:
        List of concepts (query concept + dependencies).

    Examples:
        >>> concepts = query_concept_lookup(graph, "req-rf-05")
        >>> concepts[0].id
        'req-rf-05'
    """
    concept_id = normalize_concept_id(query)

    # Check if concept exists
    if concept_id not in graph.nodes:
        return []

    # Start with the concept itself
    concepts = [graph.nodes[concept_id]]

    # Default edge types for dependencies
    if edge_types is None:
        edge_types = ["governed_by", "implements"]

    # Add dependencies (1-hop by default)
    if max_depth > 0:
        for edge_type in edge_types:
            edges = graph.get_outgoing_edges(concept_id, edge_type=edge_type)
            for edge in edges:
                if edge.target in graph.nodes:
                    target = graph.nodes[edge.target]
                    if target not in concepts:
                        concepts.append(target)

    return concepts


def query_keyword_search(
    graph: ConceptGraph,
    query: str,
    concept_type: str | None = None,
    limit: int = 10,
) -> list[Concept]:
    """Search concepts by keyword with optional type filter.

    Strategy: Match keywords in section/content, filter by type.

    Args:
        graph: Concept graph to query.
        query: Keywords to search for.
        concept_type: Optional type filter (requirement, principle, outcome).
        limit: Maximum results to return (default: 10).

    Returns:
        List of matching concepts, sorted by relevance.

    Examples:
        >>> concepts = query_keyword_search(graph, "validation", concept_type="requirement")
        >>> all(c.type.value == "requirement" for c in concepts)
        True
    """
    keywords = extract_keywords(query)

    if not keywords:
        return []

    matches: list[tuple[Concept, int]] = []

    for concept in graph.nodes.values():
        # Type filter
        if concept_type and concept.type.value != concept_type:
            continue

        # Keyword match (section + first 500 chars of content)
        text = (concept.section + " " + concept.content[:500]).lower()
        match_count = sum(1 for kw in keywords if kw in text)

        if match_count > 0:
            matches.append((concept, match_count))

    # Sort by relevance (match count)
    matches.sort(key=lambda x: x[1], reverse=True)

    # Return top N
    return [concept for concept, _ in matches[:limit]]


def query_relationship_traversal(
    graph: ConceptGraph,
    query: str,
    edge_types: list[RelationshipType],
    max_depth: int = 2,
) -> list[Concept]:
    """Traverse graph following specific relationship types.

    Strategy: BFS traversal from starting concept.

    Args:
        graph: Concept graph to query.
        query: Starting concept ID.
        edge_types: Edge types to follow.
        max_depth: Maximum traversal depth (default: 2).

    Returns:
        List of concepts reachable via specified edges.

    Examples:
        >>> # Find principles governing a requirement
        >>> concepts = query_relationship_traversal(
        ...     graph, "req-rf-05", edge_types=["governed_by"]
        ... )
        >>> all(c.type.value == "principle" or c.id == "req-rf-05" for c in concepts)
        True
    """
    from raise_cli.governance.graph.traversal import traverse_bfs

    concept_id = normalize_concept_id(query)

    # Use F2.2's BFS traversal
    concepts = traverse_bfs(
        graph, start_id=concept_id, edge_types=edge_types, max_depth=max_depth
    )

    return concepts


def query_related_concepts(
    graph: ConceptGraph,
    query: str,
    min_shared_keywords: int = 2,
    limit: int = 5,
) -> list[Concept]:
    """Find concepts related to query via keyword overlap.

    Strategy: Semantic similarity based on shared keywords.

    Args:
        graph: Concept graph to query.
        query: Query text (concept ID or keywords).
        min_shared_keywords: Minimum shared keywords for match (default: 2).
        limit: Maximum results to return (default: 5).

    Returns:
        List of related concepts, sorted by relevance score.

    Examples:
        >>> concepts = query_related_concepts(graph, "context generation")
        >>> len(concepts) <= 5
        True
    """
    query_keywords = extract_keywords(query)

    if not query_keywords:
        return []

    scored_concepts: list[tuple[Concept, float, set[str]]] = []

    for concept in graph.nodes.values():
        # Extract keywords from concept
        concept_text = concept.section + " " + concept.content[:500]
        concept_keywords = extract_keywords(concept_text)

        # Calculate overlap
        shared = query_keywords & concept_keywords

        if len(shared) >= min_shared_keywords:
            # Relevance score: shared keywords / query keywords
            score = len(shared) / len(query_keywords) if query_keywords else 0
            scored_concepts.append((concept, score, shared))

    # Sort by score (descending)
    scored_concepts.sort(key=lambda x: x[1], reverse=True)

    # Return top N concepts
    return [concept for concept, score, _ in scored_concepts[:limit]]
