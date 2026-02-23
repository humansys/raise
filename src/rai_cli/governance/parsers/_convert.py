"""Concept to GraphNode conversion utility.

Extracted from UnifiedGraphBuilder._concept_to_node() for reuse
by GovernanceParser wrapper classes.
"""

from __future__ import annotations

from datetime import UTC, datetime

from rai_cli.context.models import ConceptNode
from rai_cli.governance.models import Concept


def concept_to_node(concept: Concept) -> ConceptNode:
    """Convert governance Concept to ConceptNode (GraphNode).

    Preserves section and lines in metadata since GraphNode has no
    dedicated fields for these (R3 from quality review).

    Args:
        concept: Governance concept to convert.

    Returns:
        ConceptNode with mapped fields.
    """
    metadata = dict(concept.metadata)
    metadata["section"] = concept.section
    metadata["lines"] = concept.lines

    return ConceptNode(
        id=concept.id,
        type=concept.type.value,
        content=concept.content,
        source_file=concept.file,
        created=datetime.now(tz=UTC).isoformat(),
        metadata=metadata,
    )
