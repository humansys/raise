"""Extraction review cycle — summarize results and apply schema feedback.

Provides the data layer for the extract→review→refine loop:
- summarize_extraction() aggregates nodes by type and source document
- apply_feedback() modifies extractor config based on drop/add type feedback
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy

from pydantic import BaseModel, Field

from raise_core.graph.models import GraphNode


class ExtractionSummary(BaseModel):
    """Summary of extraction results for review."""

    total_nodes: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    type_names: list[str] = Field(default_factory=list)


def summarize_extraction(nodes: list[GraphNode]) -> ExtractionSummary:
    """Summarize extraction results by type and source document."""
    if not nodes:
        return ExtractionSummary()

    type_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()

    for node in nodes:
        type_counts[node.type] += 1
        if node.source_file:
            source_counts[node.source_file] += 1

    return ExtractionSummary(
        total_nodes=len(nodes),
        by_type=dict(type_counts),
        by_source=dict(source_counts),
        type_names=sorted(type_counts.keys()),
    )


def apply_feedback(
    config: dict[str, list[dict[str, object]]],
    *,
    drop_types: list[str] | None = None,
    add_types: list[str] | None = None,
) -> dict[str, list[dict[str, object]]]:
    """Apply review feedback to an extractor config dict.

    - drop_types: remove extractor specs with matching node_type
    - add_types: add new LLM extractor specs for types not already present

    Both operations are idempotent.
    """
    result = deepcopy(config)
    specs: list[dict[str, object]] = result.get("extractors", [])

    if drop_types:
        drop_set = set(drop_types)
        specs = [s for s in specs if s.get("node_type") not in drop_set]

    if add_types:
        existing_types = {s.get("node_type") for s in specs}
        template = _find_template(specs)
        for type_name in add_types:
            if type_name not in existing_types:
                new_spec = _make_spec_from_template(type_name, template)
                specs.append(new_spec)

    result["extractors"] = specs
    return result


def _find_template(specs: list[dict[str, object]]) -> dict[str, object]:
    """Find an existing spec to use as template for new specs."""
    if specs:
        return specs[0]
    return {
        "type": "llm",
        "sources": ["corpus/*.md"],
        "schema_ref": "extractors/schemas/relationships.yaml",
        "relationship_mode": "guided",
    }


def _make_spec_from_template(
    type_name: str, template: dict[str, object]
) -> dict[str, object]:
    """Create a new extractor spec based on a template."""
    new_spec: dict[str, object] = {
        "name": type_name,
        "type": "llm",
        "sources": template.get("sources", ["corpus/*.md"]),
        "node_type": type_name,
    }
    if "schema_ref" in template:
        new_spec["schema_ref"] = template["schema_ref"]
    if "relationship_mode" in template:
        new_spec["relationship_mode"] = template["relationship_mode"]
    if "domain_context" in template:
        new_spec["domain_context"] = template["domain_context"]
    return new_spec
