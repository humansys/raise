"""Schema and node diff models for knowledge discovery.

Migrated from rai-agent in S2674.6. LLM-dependent models
(discovery prompts, refinement) remain in rai-agent.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NodeTypeSpec(BaseModel):
    """A discovered node type with its fields."""

    name: str = Field(..., description="Node type name (e.g. 'concept', 'tool')")
    fields: list[str] = Field(
        default_factory=list, description="Field names for this type"
    )


class SchemaSpec(BaseModel):
    """Schema discovered from a corpus — types, fields, relationships."""

    node_types: list[NodeTypeSpec] = Field(default_factory=lambda: list[NodeTypeSpec]())
    relationship_types: list[str] = Field(default_factory=list)


class FieldDiff(BaseModel):
    """Per-type field comparison between discovered and reference."""

    common: list[str] = Field(default_factory=list)
    only_discovered: list[str] = Field(default_factory=list)
    only_reference: list[str] = Field(default_factory=list)


class SchemaDiffReport(BaseModel):
    """Comparison of discovered schema spec vs a reference Pydantic model."""

    types_both: list[str] = Field(default_factory=list)
    types_only_discovered: list[str] = Field(default_factory=list)
    types_only_reference: list[str] = Field(default_factory=list)
    field_diffs: dict[str, FieldDiff] = Field(default_factory=dict)


class DecisionDiff(BaseModel):
    """Per-decision-area breakdown for content diff."""

    both: list[str] = Field(default_factory=list)
    only_extracted: list[str] = Field(default_factory=list)
    only_curated: list[str] = Field(default_factory=list)


class NodeDiffReport(BaseModel):
    """Comparison of extracted nodes vs curated nodes by ID."""

    nodes_both: list[str] = Field(default_factory=list)
    nodes_only_extracted: list[str] = Field(default_factory=list)
    nodes_only_curated: list[str] = Field(default_factory=list)
    total_extracted: int = 0
    total_curated: int = 0
    overlap_pct: float = 0.0
    by_decision: dict[str, DecisionDiff] = Field(default_factory=dict)


class ReconcileReport(BaseModel):
    """Report from reconcile_extracted: what was fixed."""

    nodes_created: list[str] = Field(default_factory=list)
    refs_resolved: int = 0
    refs_removed: int = 0
    total_broken_before: int = 0
    total_broken_after: int = 0
