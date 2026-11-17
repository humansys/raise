"""Second-pass relationship extraction (RAISE-11566).

Per-chunk entity extraction only links entities that co-occur in the same
section, so cross-section / cross-type relationships are missed (spike
RAISE-11565 measured ~28% coverage). This pass runs AFTER entities exist: it
shows the model the full node inventory and asks it to propose relationships
between EXISTING nodes, constrained to the cartridge's relationship schema.

Provider-agnostic and pure — no network I/O. The generative call (chunk of text
→ proposals) is supplied by the caller, exactly like the entity extractors:
the API path passes an OpenAI-compatible client; the agent-native path emits a
work order and the agent fills it.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from raise_core.cartridges.agent_extract import WORK_DIR_NAME
from raise_core.cartridges.extract import (
    ExtractorConfig,
    RelationshipSchema,
    RelationshipType,
    load_relationship_schema,
    read_cartridge_name,
)
from raise_core.cartridges.ingest import resolve_relationship_target
from raise_core.cartridges.instances import iter_instance_files
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

_RELATIONSHIP_WORK_FILE = "relationships.work.json"
_RELATIONSHIP_RESULT_FILE = "relationships.result.json"


def _node_name(node: GraphNode) -> str:
    meta = node.metadata or {}
    return str(meta.get("source_heading") or meta.get("name") or node.id)


_RELATIONSHIP_PROMPT = """\
You are a knowledge-graph relationship extractor. Below is the full inventory of
already-extracted nodes for one cartridge, followed by the allowed relationship
types. Propose relationships BETWEEN EXISTING NODES only.

## Rules
- Use ONLY the node ids listed in the inventory for "source" and "target".
- Use ONLY the relationship types listed in the schema.
- Do not invent nodes. Do not relate a node to itself.
- Only assert a relationship when the inventory makes it clearly justified.

## Node inventory
{inventory}

## Relationship schema
{schema}

## Output format
Return a JSON object:
{{"relationships": [{{"source": "<node-id>", "target": "<node-id>", "type": "<type>"}}]}}
"""


def build_relationship_prompt(
    nodes: list[GraphNode], schema: RelationshipSchema
) -> str:
    """Build the relationship-proposal prompt over the full node inventory.

    The model sees every node id (with type + name) and the allowed relationship
    types, so it can link across sections and types — what per-chunk extraction
    cannot do.
    """
    inventory = "\n".join(
        f"- {node.id} ({node.type}): {_node_name(node)}" for node in nodes
    )
    if schema.relationship_types:
        schema_lines = "\n".join(
            f"- {rt.type}: {rt.description}" if rt.description else f"- {rt.type}"
            for rt in schema.relationship_types
        )
    else:
        # RAISE-15999 chain step 3: an empty schema section must not sit
        # under a Rules block that still says "use ONLY the types listed in
        # the schema" — that is an empty menu with a mandatory order. Say so
        # explicitly instead of rendering a blank line.
        schema_lines = "(none declared — do not propose any relationships)"
    return _RELATIONSHIP_PROMPT.format(inventory=inventory, schema=schema_lines)


def apply_proposed_relationships(
    nodes: list[GraphNode],
    proposals: list[dict[str, str]],
    cartridge_name: str,
    *,
    schema: RelationshipSchema | None = None,
) -> int:
    """Attach proposed relationships onto source nodes, pruning invalid ones.

    Each proposal is ``{source, target, type}``. Source and target slugs are
    resolved to real node ids (direct or ``kc-{cartridge}-{slug}``); proposals
    that don't resolve, point a node at itself, use a type outside the schema,
    or duplicate an existing edge are dropped. Returns the number attached.
    """
    node_ids = frozenset(n.id for n in nodes)
    by_id = {n.id: n for n in nodes}
    allowed = (
        {rt.type for rt in schema.relationship_types} if schema is not None else None
    )

    attached = 0
    for prop in proposals:
        rel_type = prop.get("type", "")
        if allowed is not None and rel_type not in allowed:
            continue
        source_id = resolve_relationship_target(
            prop.get("source", ""), cartridge_name, node_ids
        )
        target_id = resolve_relationship_target(
            prop.get("target", ""), cartridge_name, node_ids
        )
        if source_id is None or target_id is None or source_id == target_id:
            continue

        source = by_id[source_id]
        rels = source.metadata.setdefault("relationships", [])
        edge = {"target": target_id, "type": rel_type}
        if edge in rels:
            continue
        rels.append(edge)
        attached += 1

    return attached


def combined_schema(cartridge_dir: Path) -> RelationshipSchema:
    """Union the relationship types declared across all extractor specs.

    Raises RelationshipSchemaError if any spec's schema_ref is malformed
    (RAISE-15999) — that must fail the pass loudly, not be laundered into
    an empty-but-present schema indistinguishable from "no schema declared
    anywhere", which silently drops every proposed relationship downstream.
    ``schema is None`` below only ever means the latter, legitimate case.
    """
    config = ExtractorConfig.from_yaml(cartridge_dir / "extractors" / "config.yaml")
    seen: dict[str, RelationshipType] = {}
    for spec in config.extractors:
        schema = load_relationship_schema(spec, cartridge_dir)
        if schema is None:
            continue
        for rt in schema.relationship_types:
            seen.setdefault(rt.type, rt)
    return RelationshipSchema(relationship_types=list(seen.values()))


def _load_instances(instances_dir: Path) -> dict[Path, list[GraphNode]]:
    """Load instance nodes grouped by their per-spec JSON file.

    Sidecar files (embedding index, synonyms, ...) are excluded at the file
    level via ``iter_instance_files`` — never entered into ``grouped`` at
    all, so ``ingest_relationship_work``'s "rewrite every key" write-back
    can't truncate them (RAISE-15998).
    """
    grouped: dict[Path, list[GraphNode]] = {}
    for json_path in iter_instance_files(instances_dir):
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        grouped[json_path] = [GraphNode.model_validate(d) for d in raw]
    return grouped


def emit_relationship_work(cartridge_dir: Path) -> Path:
    """Write a single relationship work order over the full node inventory.

    Agent-native counterpart of the API relationship pass: the agent fills the
    prompt with its own inference (no API key) and writes the sibling
    ``relationships.result.json``.
    """
    grouped = _load_instances(cartridge_dir / "instances")
    nodes = [n for nodes in grouped.values() for n in nodes]
    schema = combined_schema(cartridge_dir)
    prompt = build_relationship_prompt(nodes, schema)

    work_dir = cartridge_dir / WORK_DIR_NAME
    work_dir.mkdir(parents=True, exist_ok=True)
    order_path = work_dir / _RELATIONSHIP_WORK_FILE
    order_path.write_text(json.dumps({"prompt": prompt}, indent=2), encoding="utf-8")
    return order_path


def ingest_relationship_work(cartridge_dir: Path) -> int:
    """Apply the agent's relationship result and rewrite instance files.

    Reads ``relationships.result.json``, resolves and attaches the proposed
    relationships (pruning dangling/out-of-schema), and persists the updated
    nodes back to their per-spec instance files. Returns the count attached.
    """
    result_path = cartridge_dir / WORK_DIR_NAME / _RELATIONSHIP_RESULT_FILE
    if not result_path.exists():
        logger.warning("No relationship result at %s", result_path)
        return 0

    data = json.loads(result_path.read_text(encoding="utf-8"))
    proposals = data.get("relationships", []) if isinstance(data, dict) else []
    if not proposals:
        return 0

    cartridge_name = read_cartridge_name(cartridge_dir)
    schema = combined_schema(cartridge_dir)
    grouped = _load_instances(cartridge_dir / "instances")
    all_nodes = [n for nodes in grouped.values() for n in nodes]

    count = apply_proposed_relationships(
        all_nodes, proposals, cartridge_name, schema=schema
    )

    # Persist mutated nodes back to their original per-spec files.
    for json_path, nodes in grouped.items():
        json_path.write_text(
            json.dumps(
                [n.model_dump(mode="json") for n in nodes],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    return count


__all__ = [
    "apply_proposed_relationships",
    "build_relationship_prompt",
    "combined_schema",
    "emit_relationship_work",
    "ingest_relationship_work",
]
