"""Entity resolution — canonicalize duplicate nodes via LLM clustering.

Groups nodes by type, asks an LLM to identify merge candidates within
each group, then deterministically merges (first-seen ID wins, aliases
stored in metadata).
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from pydantic import BaseModel, Field

from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)


class NodeCluster(BaseModel):
    """A cluster of nodes identified as semantically equivalent."""

    canonical_id: str
    alias_ids: list[str] = Field(default_factory=list)


class CanonicalizeResult(BaseModel):
    """Result of entity resolution."""

    nodes: list[GraphNode] = Field(default_factory=list)
    merged_count: int = 0
    clusters: list[NodeCluster] = Field(default_factory=list)


_MERGE_PROMPT = """\
You are an entity resolution engine. Given a list of entities of the same type, \
identify groups of entities that refer to the same real-world concept.

## Rules
- Only group entities that are clearly the same concept (synonyms, abbreviations, \
different phrasings of the same thing)
- Do NOT group entities that are merely related or similar
- Each entity can appear in at most one cluster
- If no duplicates exist, return an empty clusters array

## Entities (type: {node_type})
{entities}

## Output format
Return a JSON object:
```json
{{
  "clusters": [
    ["canonical-id", "alias-id-1", "alias-id-2"]
  ]
}}
```

Each cluster is an array of entity IDs that refer to the same concept. \
The first ID in each cluster is the canonical ID."""


def _format_entities(nodes: list[GraphNode]) -> str:
    """Format nodes for the merge prompt."""
    lines: list[str] = []
    for node in nodes:
        lines.append(f"- {node.id}: {node.content[:200]}")
    return "\n".join(lines)


def _merge_cluster(
    cluster_ids: list[str], nodes_by_id: dict[str, GraphNode]
) -> tuple[GraphNode, int]:
    """Merge a cluster: first ID is canonical, rest become aliases."""
    canonical_id = cluster_ids[0]
    alias_ids = cluster_ids[1:]
    canonical = nodes_by_id[canonical_id].model_copy(deep=True)
    canonical.metadata["canonical_aliases"] = alias_ids
    return canonical, len(alias_ids)


def _resolve_type_group(
    nodes: list[GraphNode], node_type: str, llm_client: Any
) -> tuple[list[GraphNode], int, list[NodeCluster]]:
    """Resolve duplicates within a single type group."""
    if len(nodes) <= 1:
        return list(nodes), 0, []

    prompt = _MERGE_PROMPT.format(node_type=node_type, entities=_format_entities(nodes))

    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash-lite",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or ""
    except Exception:
        logger.warning(
            "LLM call failed during entity resolution for type %s", node_type
        )
        return list(nodes), 0, []

    if not raw_text.strip():
        return list(nodes), 0, []

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON from LLM in entity resolution")
        return list(nodes), 0, []

    raw_clusters: list[list[str]] = data.get("clusters", [])
    if not raw_clusters:
        return list(nodes), 0, []

    nodes_by_id = {n.id: n for n in nodes}
    merged_ids: set[str] = set()
    result_nodes: list[GraphNode] = []
    result_clusters: list[NodeCluster] = []
    total_merged = 0

    for cluster_ids in raw_clusters:
        valid_ids = [cid for cid in cluster_ids if cid in nodes_by_id]
        if len(valid_ids) < 2:
            continue
        canonical, merge_count = _merge_cluster(valid_ids, nodes_by_id)
        result_nodes.append(canonical)
        result_clusters.append(
            NodeCluster(canonical_id=valid_ids[0], alias_ids=valid_ids[1:])
        )
        merged_ids.update(valid_ids)
        total_merged += merge_count

    for node in nodes:
        if node.id not in merged_ids:
            result_nodes.append(node)

    return result_nodes, total_merged, result_clusters


def canonicalize_nodes(nodes: list[GraphNode], llm_client: Any) -> CanonicalizeResult:
    """Canonicalize nodes by resolving semantic duplicates.

    Groups nodes by type, uses LLM to identify merge candidates within
    each group, merges deterministically (first-seen ID = canonical).
    """
    if not nodes:
        return CanonicalizeResult()

    by_type: dict[str, list[GraphNode]] = defaultdict(list)
    for node in nodes:
        by_type[node.type].append(node)

    all_nodes: list[GraphNode] = []
    total_merged = 0
    all_clusters: list[NodeCluster] = []

    for node_type, type_nodes in by_type.items():
        resolved, merged, clusters = _resolve_type_group(
            type_nodes, node_type, llm_client
        )
        all_nodes.extend(resolved)
        total_merged += merged
        all_clusters.extend(clusters)

    return CanonicalizeResult(
        nodes=all_nodes, merged_count=total_merged, clusters=all_clusters
    )
