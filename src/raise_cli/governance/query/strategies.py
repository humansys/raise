"""Query strategy implementations for MVC extraction.

This module implements the 4 core query strategies:
- CONCEPT_LOOKUP: Direct ID lookup with dependencies
- KEYWORD_SEARCH: Keyword matching with type filtering
- RELATIONSHIP_TRAVERSAL: Follow specific edge types
- RELATED_CONCEPTS: Semantic similarity via keywords
"""

from __future__ import annotations

import re

from raise_cli.core.text import extract_keywords
from raise_cli.governance.graph.models import ConceptGraph, RelationshipType
from raise_cli.governance.models import Concept


def normalize_concept_id(query: str) -> str:
    """Normalize concept ID from various formats.

    Converts user-friendly formats (RF-05, §2, E8, F8.1) to canonical IDs.

    Args:
        query: Query string (may be RF-05, req-rf-05, §2, E8, F8.1, etc.).

    Returns:
        Normalized concept ID.

    Examples:
        >>> normalize_concept_id("RF-05")
        'req-rf-05'
        >>> normalize_concept_id("req-rf-05")
        'req-rf-05'
        >>> normalize_concept_id("§2")
        'principle-governance-as-code'
        >>> normalize_concept_id("E8")
        'epic-e8'
        >>> normalize_concept_id("F8.1")
        'feature-f8-1'
    """
    # Already normalized
    if query.startswith(
        ("req-", "outcome-", "principle-", "epic-", "feature-", "project-")
    ):
        return query

    # RF-XX format → req-rf-xx
    if re.match(r"^RF-\d+$", query, re.IGNORECASE):
        return f"req-{query.lower()}"

    # EN format → epic-eN
    if re.match(r"^E\d+$", query, re.IGNORECASE):
        return f"epic-{query.lower()}"

    # FN.N format → feature-fN-N
    if re.match(r"^F\d+\.\d+$", query, re.IGNORECASE):
        return f"feature-{query.lower().replace('.', '-')}"

    # §N format → look up by section (handled by caller)
    return query.lower().replace(" ", "-")


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
    return [concept for concept, _score, _ in scored_concepts[:limit]]


def _query_current_work(graph: ConceptGraph) -> list[Concept]:
    """Get current work focus (project + epic + features)."""
    concepts: list[Concept] = []
    for edge in graph.edges:
        if edge.type == "current_focus":
            project = graph.get_node(edge.source)
            epic = graph.get_node(edge.target)
            if project:
                concepts.append(project)
            if epic:
                concepts.append(epic)
                for feature_edge in graph.get_outgoing_edges(epic.id, edge_type="contains"):
                    feature = graph.get_node(feature_edge.target)
                    if feature:
                        concepts.append(feature)
            break
    return concepts


def _query_epic_with_features(graph: ConceptGraph, epic_id: str) -> list[Concept]:
    """Get epic and all its features."""
    concepts: list[Concept] = []
    epic = graph.get_node(epic_id)
    if epic:
        concepts.append(epic)
        for edge in graph.get_outgoing_edges(epic_id, edge_type="contains"):
            feature = graph.get_node(edge.target)
            if feature:
                concepts.append(feature)
    return concepts


def _query_feature_with_parent(graph: ConceptGraph, feature_id: str) -> list[Concept]:
    """Get feature and its parent epic."""
    from raise_cli.governance.models import ConceptType

    concepts: list[Concept] = []
    feature = graph.get_node(feature_id)
    if feature:
        concepts.append(feature)
        for edge in graph.edges:
            if edge.type == "contains" and edge.target == feature_id:
                epic = graph.get_node(edge.source)
                if epic and epic.type == ConceptType.EPIC:
                    concepts.insert(0, epic)
                    break
    return concepts


def _query_all_projects(graph: ConceptGraph) -> list[Concept]:
    """Get all project concepts."""
    from raise_cli.governance.models import ConceptType

    return [c for c in graph.nodes.values() if c.type == ConceptType.PROJECT]


def _deduplicate_concepts(concepts: list[Concept], limit: int = 10) -> list[Concept]:
    """Deduplicate concepts by ID, keeping first occurrence."""
    seen_ids: set[str] = set()
    unique: list[Concept] = []
    for c in concepts:
        if c.id not in seen_ids:
            seen_ids.add(c.id)
            unique.append(c)
    return unique[:limit]


def query_work_context(
    graph: ConceptGraph,
    query: str,
) -> list[Concept]:
    """Query work tracking concepts (projects, epics, features).

    Handles special queries:
    - "current work" / "current epic" → project's current_focus epic
    - "E8" → epic with its features
    - "F8.1" → specific feature
    - "E8 features" → all features in epic

    Args:
        graph: Concept graph to query.
        query: Work-related query string.

    Returns:
        List of matching work concepts with context.

    Examples:
        >>> concepts = query_work_context(graph, "current work")
        >>> concepts[0].type.value in ("project", "epic")
        True
    """
    from raise_cli.governance.models import ConceptType

    query_lower = query.lower().strip()

    # "current work" / "current epic" / "what am I working on"
    if any(kw in query_lower for kw in ["current work", "current epic", "working on"]):
        return _query_current_work(graph)

    # "E8 features" pattern
    epic_features_match = re.match(r"^(E\d+)\s+features?$", query, re.IGNORECASE)
    if epic_features_match:
        epic_id = normalize_concept_id(epic_features_match.group(1))
        return _query_epic_with_features(graph, epic_id)

    # Direct epic/feature lookup (E8, F8.1)
    concept_id = normalize_concept_id(query)
    if concept_id.startswith("epic-"):
        return _query_epic_with_features(graph, concept_id)

    if concept_id.startswith("feature-"):
        return _query_feature_with_parent(graph, concept_id)

    # Project lookup
    if concept_id.startswith("project-") or "project" in query_lower:
        return _query_all_projects(graph)

    # Fallback: keyword search in work concepts
    concepts: list[Concept] = []
    for concept in graph.nodes.values():
        if concept.type in (ConceptType.PROJECT, ConceptType.EPIC, ConceptType.FEATURE):
            text = (concept.section + " " + concept.content[:300]).lower()
            if any(kw in text for kw in extract_keywords(query)):
                concepts.append(concept)

    return _deduplicate_concepts(concepts)
