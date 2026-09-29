"""Cartridge data hygiene — ID dedup, edge type normalization, broken rel report.

Pure post-processing over extracted GraphNodes, no I/O. Fixes the three
data quality failures found in the S-KC7.6 blast-radius study: silent
last-wins on duplicate IDs at ingest, relationships lost with their
overwritten source nodes, and unnormalized edge type vocabulary.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, Field

from raise_core.cartridges.reconcile import BrokenRelationship, reconcile_nodes
from raise_core.graph.models import CoreEdgeTypes, GraphNode

CANONICAL_EDGE_TYPES: frozenset[str] = frozenset(
    value
    for name, value in vars(CoreEdgeTypes).items()
    if name.isupper() and isinstance(value, str)
)

# Safe synonyms only — types whose semantics clearly match a canonical type.
# Anything not listed here is preserved (open type system) and reported.
EDGE_TYPE_SYNONYMS: dict[str, str] = {
    "related": CoreEdgeTypes.RELATED_TO,
    "relates_to": CoreEdgeTypes.RELATED_TO,
    "uses": CoreEdgeTypes.DEPENDS_ON,
    "requires": CoreEdgeTypes.DEPENDS_ON,
    "depends": CoreEdgeTypes.DEPENDS_ON,
    "is_part_of": CoreEdgeTypes.PART_OF,
    "belongs": CoreEdgeTypes.BELONGS_TO,
    "member_of": CoreEdgeTypes.BELONGS_TO,
}


class DedupReport(BaseModel):
    """Metrics from an ID dedup pass."""

    total_in: int = 0
    total_out: int = 0
    dropped_duplicates: int = 0
    disambiguated: int = 0
    collisions: dict[str, int] = Field(default_factory=dict)


class DedupResult(BaseModel):
    """Deduplicated nodes plus metrics.

    ``kept_indices[i]`` is the index in the input list that produced
    ``nodes[i]`` — callers use it to map clean nodes back to their origin
    (e.g. per-spec instance files).
    """

    nodes: list[GraphNode] = Field(default_factory=list)
    kept_indices: list[int] = Field(default_factory=list)
    report: DedupReport = Field(default_factory=DedupReport)


class EdgeTypeReport(BaseModel):
    """Metrics from an edge type normalization pass."""

    types_before: int = 0
    types_after: int = 0
    mapped: dict[str, str] = Field(default_factory=dict)
    non_canonical: dict[str, int] = Field(default_factory=dict)


class NormalizeResult(BaseModel):
    """Nodes with normalized edge types plus metrics."""

    nodes: list[GraphNode] = Field(default_factory=list)
    report: EdgeTypeReport = Field(default_factory=EdgeTypeReport)


class HygieneReport(BaseModel):
    """Combined report for the full hygiene pipeline."""

    dedup: DedupReport = Field(default_factory=DedupReport)
    edge_types: EdgeTypeReport = Field(default_factory=EdgeTypeReport)
    broken_relationships: list[BrokenRelationship] = Field(default_factory=list)


class HygieneResult(BaseModel):
    """Clean nodes plus the combined hygiene report.

    ``kept_indices`` maps each clean node back to its index in the input
    list (normalization is 1:1, so dedup's mapping carries through).
    """

    nodes: list[GraphNode] = Field(default_factory=list)
    kept_indices: list[int] = Field(default_factory=list)
    report: HygieneReport = Field(default_factory=HygieneReport)


def dedup_nodes(nodes: list[GraphNode]) -> DedupResult:
    """Deduplicate node IDs deterministically.

    Same ID + same content + same relationships → true duplicate, dropped.
    Same ID + distinct content → kept under a stable disambiguation suffix
    derived from the source file stem (``{id}--{stem}``, sequence fallback
    on collision). The first occurrence always keeps the canonical ID so
    existing relationship targets keep resolving.
    """
    occurrences: dict[str, int] = {}
    fingerprints_by_id: dict[str, list[str]] = {}
    taken_ids: set[str] = set()
    kept: list[GraphNode] = []
    kept_indices: list[int] = []
    dropped = 0
    disambiguated = 0

    for index, node in enumerate(nodes):
        occurrences[node.id] = occurrences.get(node.id, 0) + 1
        seen_fingerprints = fingerprints_by_id.setdefault(node.id, [])
        fingerprint = _node_fingerprint(node)
        if node.id not in taken_ids:
            taken_ids.add(node.id)
            seen_fingerprints.append(fingerprint)
            kept.append(node)
            kept_indices.append(index)
            continue
        if fingerprint in seen_fingerprints:
            dropped += 1
            continue
        seen_fingerprints.append(fingerprint)
        new_id = _disambiguate_id(node.id, node.source_file, taken_ids)
        taken_ids.add(new_id)
        disambiguated += 1
        kept.append(
            node.model_copy(
                update={
                    "id": new_id,
                    "metadata": {**node.metadata, "hygiene_original_id": node.id},
                }
            )
        )
        kept_indices.append(index)

    collisions = {nid: count for nid, count in occurrences.items() if count > 1}
    return DedupResult(
        nodes=kept,
        kept_indices=kept_indices,
        report=DedupReport(
            total_in=len(nodes),
            total_out=len(kept),
            dropped_duplicates=dropped,
            disambiguated=disambiguated,
            collisions=collisions,
        ),
    )


def _node_fingerprint(node: GraphNode) -> str:
    """Identity for true-duplicate detection — content plus relationships.

    Two nodes with equal content but different relationships are NOT
    duplicates: dropping one would silently lose its edges.
    """
    rels = node.metadata.get("relationships", [])
    return f"{node.content}\x00{json.dumps(rels, sort_keys=True, default=str)}"


def _disambiguate_id(node_id: str, source_file: str | None, taken_ids: set[str]) -> str:
    """Build a stable suffixed ID that does not collide with taken IDs."""
    stem = _slug(Path(source_file).stem) if source_file else ""
    if stem:
        candidate = f"{node_id}--{stem}"
        if candidate not in taken_ids:
            return candidate
        seq = 2
        while f"{candidate}-{seq}" in taken_ids:
            seq += 1
        return f"{candidate}-{seq}"
    seq = 2
    while f"{node_id}--{seq}" in taken_ids:
        seq += 1
    return f"{node_id}--{seq}"


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w-]+", "-", text.lower().strip())
    return slug.strip("-")


def normalize_edge_types(nodes: list[GraphNode]) -> NormalizeResult:
    """Normalize relationship types lexically and via the synonym map.

    Lexical pass always applies (lowercase, whitespace/hyphens →
    underscore). Synonyms map to canonical CoreEdgeTypes only where
    semantics are unambiguous. Everything else is preserved post-lexical
    and reported in ``non_canonical`` — the edge type system is open.
    """
    mapped: dict[str, str] = {}
    types_before: set[str] = set()
    types_after: set[str] = set()
    non_canonical: dict[str, int] = {}
    out: list[GraphNode] = []

    for node in nodes:
        rels = node.metadata.get("relationships")
        if not isinstance(rels, list) or not rels:
            out.append(node)
            continue
        new_rels: list[dict[str, str]] = []
        changed = False
        for rel in rels:
            raw_type = str(rel.get("type", ""))
            types_before.add(raw_type)
            normalized = _normalize_type(raw_type)
            types_after.add(normalized)
            if normalized != raw_type:
                mapped[raw_type] = normalized
                changed = True
            if normalized not in CANONICAL_EDGE_TYPES:
                non_canonical[normalized] = non_canonical.get(normalized, 0) + 1
            new_rels.append({**rel, "type": normalized})
        if changed:
            out.append(
                node.model_copy(
                    update={"metadata": {**node.metadata, "relationships": new_rels}}
                )
            )
        else:
            out.append(node)

    return NormalizeResult(
        nodes=out,
        report=EdgeTypeReport(
            types_before=len(types_before),
            types_after=len(types_after),
            mapped=mapped,
            non_canonical=non_canonical,
        ),
    )


def _normalize_type(raw: str) -> str:
    lexical = re.sub(r"[\s\-]+", "_", raw.strip().lower())
    lexical = re.sub(r"_+", "_", lexical).strip("_")
    return EDGE_TYPE_SYNONYMS.get(lexical, lexical)


def apply_hygiene(
    nodes: list[GraphNode], *, id_prefix: str | None = None
) -> HygieneResult:
    """Run the full hygiene pipeline: dedup → normalize → reconcile.

    *id_prefix* is the cartridge slug prefix (``kc-{name}-``) used to
    resolve relationship targets the same way ingest does.
    """
    deduped = dedup_nodes(nodes)
    normalized = normalize_edge_types(deduped.nodes)
    reconciliation = reconcile_nodes(normalized.nodes, id_prefix=id_prefix)
    return HygieneResult(
        nodes=normalized.nodes,
        kept_indices=deduped.kept_indices,
        report=HygieneReport(
            dedup=deduped.report,
            edge_types=normalized.report,
            broken_relationships=reconciliation.broken_relationships,
        ),
    )


__all__ = [
    "CANONICAL_EDGE_TYPES",
    "EDGE_TYPE_SYNONYMS",
    "DedupReport",
    "DedupResult",
    "EdgeTypeReport",
    "HygieneReport",
    "HygieneResult",
    "NormalizeResult",
    "apply_hygiene",
    "dedup_nodes",
    "normalize_edge_types",
]
