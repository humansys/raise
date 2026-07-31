"""Agent-native cartridge extraction (community tier — no external LLM key).

The deterministic pipeline (chunking, validation, hygiene, embeddings) stays
here; only the generative step (chunk -> structured nodes) is delegated to the
agent already driving the CLI. ``emit_work_orders`` writes one prompt per chunk;
the orchestrating agent fills each with its own inference (writing a sibling
``.result.json``); ``ingest_work_results`` runs the results back through the same
validation + hygiene + instance-writing path as the API-based extractor.

This removes the hard requirement of an external API key for the community
tier: a user whose CLI is already driven by an agent (Claude Code, Cursor, ...)
builds their governance cartridge with the inference they already have. An API
key stays an opt-in for unattended/batch extraction.

See work/problem-briefs/agent-native-cartridge-extraction-2026-06-29.md.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from raise_core.cartridges.chunker import GenericChunker
from raise_core.cartridges.extract import (
    CartridgeExtractionResult,
    ExtractorConfig,
    RelationshipSchema,
    cartridge_project_root,
    generate_embeddings,
    load_relationship_schema,
    read_cartridge_name,
    resolve_sources,
    write_instances,
)
from raise_core.cartridges.hygiene import apply_hygiene
from raise_core.cartridges.llm_extract import (
    build_prompt,
    flatten_nodes,
    prefix_ids,
    validate_and_enrich,
)
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

WORK_DIR_NAME = ".agent-work"


class WorkOrder(BaseModel):
    """A single chunk handed to the agent for structured extraction.

    The agent reads ``prompt``, produces a JSON node list, and writes it to the
    sibling ``{stem}.result.json`` file. Everything else here is metadata the
    ingest step needs to validate and place the resulting nodes.
    """

    spec_name: str
    node_type: str
    cartridge_name: str
    source_file: str
    heading: str
    prompt: str


def _work_dir(cartridge_dir: Path) -> Path:
    return cartridge_dir / WORK_DIR_NAME


def emit_work_orders(cartridge_dir: Path, *, heading_level: int = 2) -> list[WorkOrder]:
    """Chunk the corpus and write one work order per chunk.

    Reuses the same chunker and prompt builder as the API extractor, so the
    agent sees exactly the instruction the LLM would have. Stale work orders
    and results from a previous run are cleared first.
    """
    config = ExtractorConfig.from_yaml(cartridge_dir / "extractors" / "config.yaml")
    cartridge_name = read_cartridge_name(cartridge_dir)
    chunker = GenericChunker(heading_level=heading_level)

    work_dir = _work_dir(cartridge_dir)
    if work_dir.exists():
        for stale in work_dir.glob("*.json"):
            stale.unlink()
    work_dir.mkdir(parents=True, exist_ok=True)

    orders: list[WorkOrder] = []
    for spec in config.extractors:
        schema: RelationshipSchema | None = None
        if spec.relationship_mode != "none":
            schema = load_relationship_schema(spec, cartridge_dir)
        paths = resolve_sources(
            spec.sources,
            cartridge_dir,
            project_root=cartridge_project_root(cartridge_dir),
        )
        idx = 0
        for path in paths:
            for chunk in chunker.split(path):
                if not chunk.text.strip():
                    continue
                prompt = build_prompt(
                    chunk, spec.node_type, cartridge_name, schema, spec.domain_context
                )
                order = WorkOrder(
                    spec_name=spec.name,
                    node_type=spec.node_type,
                    cartridge_name=cartridge_name,
                    source_file=str(path),
                    heading=chunk.heading,
                    prompt=prompt,
                )
                out = work_dir / f"{spec.name}__{idx:03d}.work.json"
                out.write_text(order.model_dump_json(indent=2), encoding="utf-8")
                orders.append(order)
                idx += 1
    return orders


def ingest_work_results(
    cartridge_dir: Path, *, embedding_provider: Any | None = None
) -> CartridgeExtractionResult:
    """Validate agent-produced node results and write cartridge instances.

    Mirrors ``extract_cartridge``'s back half: per-chunk validation/enrichment,
    cross-spec hygiene (ID dedup, edge normalization), per-spec instance files,
    and optional embeddings. Missing or malformed results are reported, never
    fatal.
    """
    work_dir = _work_dir(cartridge_dir)
    cartridge_name = read_cartridge_name(cartridge_dir)
    now = datetime.now(tz=UTC).isoformat()

    config = ExtractorConfig.from_yaml(cartridge_dir / "extractors" / "config.yaml")
    schema_by_spec: dict[str, RelationshipSchema | None] = {}
    for spec in config.extractors:
        schema_by_spec[spec.name] = (
            load_relationship_schema(spec, cartridge_dir)
            if spec.relationship_mode != "none"
            else None
        )

    all_nodes: list[GraphNode] = []
    spec_names: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    work_files = sorted(work_dir.glob("*.work.json")) if work_dir.exists() else []
    if not work_files:
        warnings.append(f"No work orders found in {work_dir} — run extract --emit-work")

    for work_file in work_files:
        result_file = work_file.with_name(
            work_file.name.replace(".work.json", ".result.json")
        )
        if not result_file.exists():
            warnings.append(f"No result for {work_file.name}")
            continue
        order = WorkOrder.model_validate_json(work_file.read_text(encoding="utf-8"))
        try:
            data = json.loads(result_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON in {result_file.name}")
            continue
        nodes_list = flatten_nodes(data)
        if not nodes_list:
            continue
        nodes = validate_and_enrich(
            nodes_list,
            now,
            order.source_file,
            order.node_type,
            cartridge_name,
            order.heading,
            schema_by_spec.get(order.spec_name),
        )
        nodes = prefix_ids(nodes, cartridge_name)
        all_nodes.extend(nodes)
        spec_names.extend([order.spec_name] * len(nodes))

    hygiene = apply_hygiene(all_nodes, id_prefix=f"kc-{cartridge_name}-")
    clean_nodes = hygiene.nodes

    by_spec: dict[str, list[GraphNode]] = {}
    for node, source_index in zip(clean_nodes, hygiene.kept_indices, strict=True):
        by_spec.setdefault(spec_names[source_index], []).append(node)
    for spec_name, spec_nodes in by_spec.items():
        write_instances(spec_nodes, spec_name, cartridge_dir / "instances")

    if clean_nodes and embedding_provider is not None:
        warnings.extend(
            generate_embeddings(
                clean_nodes, embedding_provider, cartridge_dir / "instances"
            )
        )

    return CartridgeExtractionResult(
        nodes=clean_nodes,
        node_count=len(clean_nodes),
        errors=errors,
        warnings=warnings,
        hygiene=hygiene.report,
    )


__all__ = [
    "WORK_DIR_NAME",
    "WorkOrder",
    "emit_work_orders",
    "ingest_work_results",
]
