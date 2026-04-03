"""Concept to GraphNode conversion utility.

Extracted from GraphBuilder._concept_to_node() for reuse
by GovernanceParser wrapper classes.
"""

from __future__ import annotations

from datetime import UTC, datetime

from raise_cli.governance.models import Concept
from raise_core.graph.models import GraphNode


def concept_to_node(concept: Concept) -> GraphNode:
    """Convert governance Concept to GraphNode (GraphNode).

    Preserves section and lines in metadata since GraphNode has no
    dedicated fields for these (R3 from quality review).

    Args:
        concept: Governance concept to convert.

    Returns:
        GraphNode with mapped fields.
    """
    metadata = dict(concept.metadata)
    metadata["section"] = concept.section
    metadata["lines"] = concept.lines

    return GraphNode(
        id=concept.id,
        type=concept.type.value,
        content=concept.content,
        source_file=concept.file,
        created=datetime.now(tz=UTC).isoformat(),
        metadata=metadata,
    )
