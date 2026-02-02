"""Relationship inference logic for concept graphs.

This module provides rule-based relationship inference between governance concepts,
extracting semantic connections based on content patterns and references.
"""

from __future__ import annotations

import re

from raise_cli.governance.graph.models import Relationship
from raise_cli.governance.models import Concept, ConceptType


def infer_relationships(concepts: list[Concept]) -> list[Relationship]:
    """Infer relationships between concepts using rule-based patterns.

    Applies four inference rules:
    1. implements: Requirements → Outcomes (keyword matching)
    2. governed_by: Requirements/Outcomes → Principles (§N references)
    3. depends_on: Explicit "depends on RF-XX" or "requires RF-XX"
    4. related_to: Shared keywords (>3 common keywords)

    Args:
        concepts: List of extracted concepts.

    Returns:
        List of inferred relationships with confidence metadata.

    Examples:
        >>> from raise_cli.governance.models import Concept, ConceptType
        >>> req = Concept(
        ...     id="req-rf-05",
        ...     type=ConceptType.REQUIREMENT,
        ...     content="The system must generate context...",
        ...     file="prd.md",
        ...     section="RF-05",
        ...     lines=(1, 10)
        ... )
        >>> outcome = Concept(
        ...     id="outcome-context-generation",
        ...     type=ConceptType.OUTCOME,
        ...     content="...",
        ...     file="vision.md",
        ...     section="Context",
        ...     lines=(1, 5),
        ...     metadata={"title": "Context Generation"}
        ... )
        >>> rels = infer_relationships([req, outcome])
        >>> len([r for r in rels if r.type == "implements"]) > 0
        True
    """
    relationships: list[Relationship] = []

    # Index concepts by type for efficient lookup
    requirements = [c for c in concepts if c.type == ConceptType.REQUIREMENT]
    outcomes = [c for c in concepts if c.type == ConceptType.OUTCOME]
    principles = [c for c in concepts if c.type == ConceptType.PRINCIPLE]

    # Rule 1: implements (requirement → outcome)
    relationships.extend(_infer_implements(requirements, outcomes))

    # Rule 2: governed_by (requirement/outcome → principle)
    relationships.extend(_infer_governed_by(requirements + outcomes, principles))

    # Rule 3: depends_on (explicit dependencies)
    relationships.extend(_infer_depends_on(concepts))

    # Rule 4: related_to (shared keywords)
    relationships.extend(_infer_related_to(concepts))

    # Rule 5: work relationships (contains, current_focus)
    relationships.extend(_infer_work_relationships(concepts))

    return relationships


def _infer_implements(
    requirements: list[Concept], outcomes: list[Concept]
) -> list[Relationship]:
    """Infer 'implements' relationships from requirements to outcomes.

    Args:
        requirements: List of requirement concepts.
        outcomes: List of outcome concepts.

    Returns:
        List of 'implements' relationships.
    """
    relationships: list[Relationship] = []

    for req in requirements:
        for outcome in outcomes:
            # Extract keywords from outcome title
            outcome_title = outcome.metadata.get("title", "")
            outcome_keywords = extract_keywords(outcome_title)

            # Check if requirement content mentions outcome keywords
            req_content_lower = req.content.lower()
            if any(kw in req_content_lower for kw in outcome_keywords):
                relationships.append(
                    Relationship(
                        source=req.id,
                        target=outcome.id,
                        type="implements",
                        metadata={"confidence": 0.8, "method": "keyword_match"},
                    )
                )

    return relationships


def _infer_governed_by(
    concepts: list[Concept], principles: list[Concept]
) -> list[Relationship]:
    """Infer 'governed_by' relationships from concepts to principles.

    Looks for §N references in concept content.

    Args:
        concepts: List of concepts (requirements, outcomes).
        principles: List of principle concepts.

    Returns:
        List of 'governed_by' relationships.
    """
    relationships: list[Relationship] = []

    for concept in concepts:
        # Look for §N references in content
        principle_refs = re.findall(r"§(\d+)", concept.content)

        for ref in principle_refs:
            # Find matching principle
            principle = next(
                (p for p in principles if f"§{ref}" in p.section),
                None,
            )

            if principle:
                relationships.append(
                    Relationship(
                        source=concept.id,
                        target=principle.id,
                        type="governed_by",
                        metadata={"confidence": 1.0, "method": "explicit_reference"},
                    )
                )

    return relationships


def _infer_depends_on(concepts: list[Concept]) -> list[Relationship]:
    """Infer 'depends_on' relationships from explicit references.

    Looks for "depends on RF-XX" or "requires RF-XX" in content.

    Args:
        concepts: List of all concepts.

    Returns:
        List of 'depends_on' relationships.
    """
    relationships: list[Relationship] = []
    concept_ids = {c.id for c in concepts}

    for concept in concepts:
        # Look for "depends on RF-XX" or "requires RF-XX"
        dep_refs = re.findall(
            r"(?:depends on|requires)\s+(RF-\d+)", concept.content, re.IGNORECASE
        )

        for ref in dep_refs:
            target_id = f"req-{ref.lower()}"

            if target_id in concept_ids:
                relationships.append(
                    Relationship(
                        source=concept.id,
                        target=target_id,
                        type="depends_on",
                        metadata={"confidence": 1.0, "method": "explicit_reference"},
                    )
                )

    return relationships


def _infer_related_to(concepts: list[Concept]) -> list[Relationship]:
    """Infer 'related_to' relationships from shared keywords.

    Creates bidirectional relationships when concepts share >3 keywords.

    Args:
        concepts: List of all concepts.

    Returns:
        List of 'related_to' relationships.
    """
    relationships: list[Relationship] = []

    for i, c1 in enumerate(concepts):
        for c2 in concepts[i + 1 :]:
            # Extract keywords from both concepts
            kw1 = extract_keywords(c1.section + " " + c1.content[:200])
            kw2 = extract_keywords(c2.section + " " + c2.content[:200])

            # If >3 shared keywords, create related_to edge
            shared = kw1 & kw2

            if len(shared) >= 3:
                relationships.append(
                    Relationship(
                        source=c1.id,
                        target=c2.id,
                        type="related_to",
                        metadata={
                            "confidence": 0.6,
                            "method": "keyword_overlap",
                            "shared_keywords": sorted(shared),
                        },
                    )
                )

    return relationships


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text.

    Filters out stopwords and keeps only words longer than 3 characters.

    Args:
        text: Text to extract keywords from.

    Returns:
        Set of lowercase keywords.

    Examples:
        >>> keywords = extract_keywords("The Context Generation System")
        >>> keywords == {"context", "generation", "system"}
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
        "of",
        "with",
        "from",
        "by",
        "this",
        "that",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
    }

    words = re.findall(r"\b\w+\b", text.lower())
    return {w for w in words if len(w) > 3 and w not in stopwords}


def _infer_work_relationships(concepts: list[Concept]) -> list[Relationship]:
    """Infer relationships between work tracking concepts.

    Infers:
    - contains: Project → Epic, Epic → Feature
    - current_focus: Project → Epic (for current epic)

    Args:
        concepts: List of all concepts including work tracking types.

    Returns:
        List of work relationships.
    """
    relationships: list[Relationship] = []

    # Index work concepts by type
    projects = [c for c in concepts if c.type == ConceptType.PROJECT]
    epics = [c for c in concepts if c.type == ConceptType.EPIC]
    features = [c for c in concepts if c.type == ConceptType.FEATURE]

    # Project contains Epic (based on project_id in epic metadata)
    for project in projects:
        project_name = project.metadata.get("name")
        if not project_name:
            continue

        for epic in epics:
            epic_project_id = epic.metadata.get("project_id")
            if epic_project_id and epic_project_id == project_name:
                relationships.append(
                    Relationship(
                        source=project.id,
                        target=epic.id,
                        type="contains",
                        metadata={"confidence": 1.0, "method": "explicit"},
                    )
                )

        # Current focus relationship
        current_epic_id = project.metadata.get("current_epic")
        if current_epic_id:
            # Find the epic with matching epic_id
            current_epic = next(
                (e for e in epics if e.metadata.get("epic_id") == current_epic_id),
                None,
            )
            if current_epic:
                relationships.append(
                    Relationship(
                        source=project.id,
                        target=current_epic.id,
                        type="current_focus",
                        metadata={"confidence": 1.0, "method": "explicit"},
                    )
                )

    # Epic contains Feature (based on epic_id in feature metadata)
    for epic in epics:
        epic_id = epic.metadata.get("epic_id")
        if not epic_id:
            continue

        for feature in features:
            feature_epic_id = feature.metadata.get("epic_id")
            if feature_epic_id and feature_epic_id == epic_id:
                relationships.append(
                    Relationship(
                        source=epic.id,
                        target=feature.id,
                        type="contains",
                        metadata={"confidence": 1.0, "method": "explicit"},
                    )
                )

    return relationships
