"""Cartridge ingestion — load extracted instances into the knowledge graph."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from raise_core.cartridges.instances import iter_instance_files
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode

if TYPE_CHECKING:
    from raise_core.cartridges.models import ReferenceConfig

logger = logging.getLogger(__name__)

# RAISE-16226: cartridge directory names that are always self-snapshots of
# the build graph — raise_core.cartridges.repo:generate_repo_cartridge always
# writes CARTRIDGE.yaml with snapshot: true for these (RAISE-13378), so a
# missing/invalid manifest here is a data problem, not a signal to ingest
# normally. Defaulting such a cartridge to snapshot=False (the general
# RAISE-13378 fallback) would let a stale repo.json get re-ingested as a node
# source alongside a fresh code scan, producing ID collisions that later trip
# RepoCartridgeCollapseError in generate_repo_cartridge. Every other
# cartridge name keeps the original "ingest normally" fallback below.
_SELF_SNAPSHOT_CARTRIDGE_NAMES: frozenset[str] = frozenset({"repo"})


def _default_snapshot_for(cartridge_name: str) -> bool:
    """Return the snapshot default to use when a manifest can't be trusted.

    True only for well-known self-snapshot cartridge names (RAISE-16226);
    False (the RAISE-13378 "ingest normally" default) for everything else.
    """
    return cartridge_name in _SELF_SNAPSHOT_CARTRIDGE_NAMES


def _parse_manifest(
    manifest_path: Path, default_name: str
) -> tuple[str, ReferenceConfig | None, bool]:
    """Parse CARTRIDGE.yaml and return (cartridge_name, reference_config, snapshot).

    Falls back to (default_name, None, snapshot_default) if the file is
    missing, malformed, or fails Pydantic validation, where snapshot_default
    is True only for well-known self-snapshot cartridge names (RAISE-16226,
    e.g. ``repo``) and False for everything else — a malformed manifest for
    any other cartridge degrades to "ingest normally" (snapshot=False), never
    to "silently vanish". Uses a lazy import to avoid circular deps. Single
    parse of CARTRIDGE.yaml, shared by ``ingest_cartridge`` and
    ``is_snapshot_cartridge`` (RAISE-13378 AR R1).
    """
    if not manifest_path.exists():
        snapshot_default = _default_snapshot_for(default_name)
        if snapshot_default:
            logger.warning(
                "No CARTRIDGE.yaml found for cartridge %r at %s; treating as "
                "a self-snapshot (snapshot=True) to avoid re-ingesting stale "
                "nodes (RAISE-16226)",
                default_name,
                manifest_path.parent,
            )
        return default_name, None, snapshot_default
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError):
        snapshot_default = _default_snapshot_for(default_name)
        logger.warning(
            "CARTRIDGE.yaml at %s could not be parsed, using defaults (snapshot=%s)%s",
            manifest_path.parent,
            snapshot_default,
            " — treating as a self-snapshot (RAISE-16226)" if snapshot_default else "",
        )
        return default_name, None, snapshot_default
    if not isinstance(raw, dict):
        return default_name, None, _default_snapshot_for(default_name)
    cartridge_name: str = raw.get("name", default_name)
    try:
        from raise_core.cartridges.models import CartridgeManifest

        manifest = CartridgeManifest.model_validate(raw)
        return manifest.name, manifest.reference_config, manifest.snapshot
    except Exception:  # noqa: BLE001
        snapshot_default = _default_snapshot_for(cartridge_name)
        logger.warning(
            "Manifest validation failed for %s, using defaults (snapshot=%s)%s",
            manifest_path.parent,
            snapshot_default,
            " — treating as a self-snapshot (RAISE-16226)" if snapshot_default else "",
        )
        return cartridge_name, None, snapshot_default


def is_snapshot_cartridge(cartridge_dir: Path) -> bool:
    """Return True if this cartridge's manifest declares ``snapshot: true``.

    Used by ``GraphBuilder.load_cartridges`` (read side, RAISE-13378 Option A)
    to skip re-ingesting a cartridge that is itself a snapshot of the build
    graph (e.g. the repo cartridge) — ingesting it would feed stale, relabeled
    nodes back into the next build, an echo loop.

    Reuses ``_parse_manifest`` rather than re-implementing the yaml-load +
    validate + forgiving-fallback logic a second time. Returns False for a
    missing/malformed manifest, matching ``_parse_manifest``'s fail-open
    default — a corrupted manifest must never cause a cartridge to silently
    vanish from the graph.
    """
    _name, _reference_config, snapshot = _parse_manifest(
        cartridge_dir / "CARTRIDGE.yaml", cartridge_dir.name
    )
    return snapshot


def ingest_cartridge(
    cartridge_dir: Path,
    *,
    graph: Graph | None = None,
) -> Graph:
    """Load cartridge instances into a Graph.

    Reads all JSON files from the ``instances/`` directory. Each node
    gets ``metadata["cartridge"]`` set to the manifest name. When
    *graph* is provided, nodes are added to the existing graph after
    removing any previous nodes from the same cartridge (idempotent).

    Returns the graph with cartridge nodes loaded.
    """
    if graph is None:
        graph = Graph()

    cartridge_name, reference_config, _snapshot = _parse_manifest(
        cartridge_dir / "CARTRIDGE.yaml", cartridge_dir.name
    )

    _remove_cartridge_nodes(graph, cartridge_name)

    instances_dir = cartridge_dir / "instances"
    if not instances_dir.is_dir():
        return graph

    loaded = 0
    for json_file in iter_instance_files(instances_dir):
        nodes = json.loads(json_file.read_text(encoding="utf-8"))
        if not isinstance(nodes, list):
            logger.warning(
                "Skipping %s — expected list, got %s", json_file, type(nodes).__name__
            )
            continue
        for raw_node in nodes:
            if not isinstance(raw_node, dict):
                continue
            raw_node.setdefault("metadata", {})
            raw_node["metadata"]["cartridge"] = cartridge_name
            node = GraphNode.model_validate(raw_node)
            graph.add_concept(node)
            loaded += 1

    ref_kwargs: dict[str, Any] = {}
    if reference_config is not None:
        ref_kwargs["min_name_tokens"] = reference_config.min_name_tokens
        ref_kwargs["min_char_length"] = reference_config.min_char_length

    edges = materialize_edges(graph, cartridge_name)
    ref_edges = materialize_reference_edges(graph, cartridge_name, **ref_kwargs)
    logger.info(
        "Ingested %d nodes, %d structural edges, %d reference edges from cartridge %r",
        loaded,
        edges,
        ref_edges,
        cartridge_name,
    )
    return graph


# Low weight for structural co-occurrence edges — they connect the graph for
# spreading activation without dominating explicit governance edges (weight 1.0).
_CO_OCCURS_WEIGHT: float = 0.3


def materialize_structural_edges(graph: Graph, cartridge_name: str) -> int:
    """Create deterministic co-occurrence edges from source_file grouping.

    Nodes sharing a ``source_file`` are chained in corpus order via
    ``co_occurs_with`` edges (node[i] → node[i+1]). A chain, not a clique:
    every node gains degree ~2 and the source_file becomes one connected
    component, without creating mega-hubs that flood spreading activation
    with uniform activation (ADR-119, Layer 1).

    No inference — purely structural. Complements ``materialize_edges``.
    Returns the number of edges created.
    """
    by_source: dict[str, list[str]] = {}
    for node in graph.iter_concepts():
        if node.metadata.get("cartridge") != cartridge_name:
            continue
        source = node.metadata.get("source_file") or node.source_file
        if not source:
            continue
        by_source.setdefault(source, []).append(node.id)

    created = 0
    for node_ids in by_source.values():
        for prev_id, next_id in zip(node_ids, node_ids[1:], strict=False):
            if prev_id == next_id:
                continue
            graph.add_relationship(
                GraphEdge(
                    source=prev_id,
                    target=next_id,
                    type="co_occurs_with",
                    weight=_CO_OCCURS_WEIGHT,
                )
            )
            created += 1
    return created


# Stop-words excluded when counting "significant" tokens in a node name, so that
# a node like "main branch" (2 significant) links but "end of story" (1) does not.
_NAME_STOPWORDS: frozenset[str] = frozenset(
    {"and", "or", "of", "the", "a", "an", "to", "for", "in", "on", "with", "is", "are"}
)
_MIN_SIGNIFICANT_TOKENS: int = 2


def _node_name_from_id(node_id: str, cartridge_name: str) -> str:
    """Derive a distinctive phrase from a node ID slug.

    ``kc-raise-dev-workflow-main-branch`` → ``main branch``. The cartridge
    prefix (``kc-<cartridge>-``) is stripped; hyphens become spaces.
    """
    prefix = f"kc-{cartridge_name}-"
    slug = node_id.removeprefix(prefix)
    return slug.replace("-", " ").strip().lower()


def materialize_reference_edges(
    graph: Graph,
    cartridge_name: str,
    *,
    min_name_tokens: int | None = None,
    min_char_length: int = 5,
) -> int:
    """Create cross-section ``references`` edges from name-mention detection.

    A node B that textually mentions node A's distinctive name (derived from
    A's ID slug) gets an edge ``references`` B → A. Grounded in source text —
    the mention IS in B's content, so no hallucination (ADR-119, Layer 2).

    Only names with >= *min_name_tokens* significant tokens (excluding
    stop-words) are used, to avoid spurious edges from common short phrases.
    Names shorter than *min_char_length* characters are also excluded.
    Defaults preserve the original behaviour: 2 significant tokens, 5 chars.

    Per-cartridge overrides are read from ``CartridgeManifest.reference_config``
    by ``ingest_cartridge`` and forwarded via kwargs (S10328.1, DA-6).

    ``references`` carries governance weight (1.0) so it dominates structural
    co-occurrence (0.3).

    Returns the number of edges created.
    """
    threshold = (
        min_name_tokens if min_name_tokens is not None else _MIN_SIGNIFICANT_TOKENS
    )
    # Build (node_id, name) for nodes with distinctive enough names.
    named: list[tuple[str, str]] = []
    for node in graph.iter_concepts():
        if node.metadata.get("cartridge") != cartridge_name:
            continue
        name = _node_name_from_id(node.id, cartridge_name)
        if len(name) < min_char_length:
            continue
        significant = [t for t in name.split() if t not in _NAME_STOPWORDS]
        if len(significant) >= threshold:
            named.append((node.id, name))

    created = 0
    for node in graph.iter_concepts():
        if node.metadata.get("cartridge") != cartridge_name:
            continue
        content = node.content.lower()
        for target_id, target_name in named:
            if target_id == node.id:
                continue
            if target_name in content:
                graph.add_relationship(
                    GraphEdge(source=node.id, target=target_id, type="references")
                )
                created += 1
    return created


def materialize_edges(graph: Graph, cartridge_name: str) -> int:
    """Create graph edges from relationship metadata in cartridge nodes.

    Processes three metadata patterns:
    - ``relationships``: ``[{target, type}]`` — prefixed target resolution
    - ``depends_on``: ``[str]`` — name-based resolution
    - ``module``: ``str`` — belongs_to edge to module node

    Public API — also used by the eval harness to activate SA in fixtures.
    """
    node_ids = frozenset(graph.graph.nodes)
    name_index = _build_name_index(graph, cartridge_name)
    created = 0

    for node in graph.iter_concepts():
        if node.metadata.get("cartridge") != cartridge_name:
            continue

        for rel in node.metadata.get("relationships", []):
            target_id = resolve_relationship_target(
                rel.get("target", ""), cartridge_name, node_ids
            )
            if target_id is not None:
                graph.add_relationship(
                    GraphEdge(
                        source=node.id,
                        target=target_id,
                        type=rel.get("type", "related_to"),
                    )
                )
                created += 1

        for dep_name in node.metadata.get("depends_on", []):
            target_id = name_index.get(dep_name)
            if target_id is not None and target_id != node.id:
                graph.add_relationship(
                    GraphEdge(source=node.id, target=target_id, type="depends_on")
                )
                created += 1

        module_id = node.metadata.get("module")
        if module_id and module_id in node_ids and module_id != node.id:
            graph.add_relationship(
                GraphEdge(source=node.id, target=module_id, type="belongs_to")
            )
            created += 1

    return created


def resolve_relationship_target(
    target_slug: str, cartridge_name: str, node_ids: frozenset[str]
) -> str | None:
    """Resolve a relationship target slug to a node ID.

    Tries direct match first, then prefixed with ``kc-{cartridge}-``.
    """
    if not target_slug:
        return None
    if target_slug in node_ids:
        return target_slug
    prefixed = f"kc-{cartridge_name}-{target_slug}"
    if prefixed in node_ids:
        return prefixed
    return None


def _is_memory_node(node: GraphNode) -> bool:
    """Return True for a ``type=memory`` node (RAISE-13911 DD-4).

    Memory nodes (Claude Code personal/team memory notes, ingested via the
    external memory cartridge) must never gain cross-cartridge ``references``
    edges — v1 ships with zero edges for this cartridge, by design. Mirrors
    ``is_snapshot_cartridge`` (RAISE-13378 Option A): a single named
    predicate, checked at both the source and target side of
    ``materialize_cross_cartridge_edges``, rather than two divergent
    ad-hoc checks.
    """
    return node.type == "memory"


def _build_cross_cartridge_names(
    graph: Graph,
    min_name_tokens: int,
    min_char_length: int,
) -> list[tuple[str, str, str]]:
    """Build (node_id, name, cartridge) tuples for cross-cartridge matching."""
    named: list[tuple[str, str, str]] = []
    for node in graph.iter_concepts():
        cartridge = node.metadata.get("cartridge")
        if not cartridge:
            continue
        if _is_memory_node(node):
            # DD-4: never a target — no edge should point at a memory node.
            continue
        name = _node_name_from_id(node.id, cartridge)
        if len(name) < min_char_length:
            continue
        significant = [t for t in name.split() if t not in _NAME_STOPWORDS]
        if len(significant) >= min_name_tokens:
            named.append((node.id, name, cartridge))
    return named


def materialize_cross_cartridge_edges(
    graph: Graph,
    *,
    min_name_tokens: int = _MIN_SIGNIFICANT_TOKENS,
    min_char_length: int = 5,
) -> int:
    """Create ``references`` edges between nodes of different cartridges.

    Complements the per-cartridge ``materialize_reference_edges`` by
    detecting name mentions **across** cartridge boundaries.  Only edges
    where source and target belong to different cartridges are created,
    so intra-cartridge edges (already materialized during ingest) are
    never duplicated.

    Performance: O(N * M) where N = total nodes, M = named nodes.  For
    the current corpus (~6 700 nodes) this completes in <2 s.

    Returns the number of edges created.
    """
    named = _build_cross_cartridge_names(graph, min_name_tokens, min_char_length)
    created = 0
    for node in graph.iter_concepts():
        node_cartridge = node.metadata.get("cartridge")
        if not node_cartridge:
            continue
        if _is_memory_node(node):
            # DD-4: never a source — a memory node's content never
            # generates outbound cross-cartridge reference edges.
            continue
        content = node.content.lower()
        for target_id, target_name, target_cartridge in named:
            if target_cartridge == node_cartridge or target_id == node.id:
                continue
            if target_name in content:
                graph.add_relationship(
                    GraphEdge(source=node.id, target=target_id, type="references")
                )
                created += 1
    return created


def _build_name_index(graph: Graph, cartridge_name: str) -> dict[str, str]:
    """Build name → node_id index for depends_on resolution."""
    index: dict[str, str] = {}
    for node in graph.iter_concepts():
        if node.metadata.get("cartridge") != cartridge_name:
            continue
        name = node.metadata.get("name")
        if name and name not in index:
            index[name] = node.id
    return index


def _remove_cartridge_nodes(graph: Graph, cartridge_name: str) -> int:
    """Remove all nodes belonging to a cartridge (for idempotent reload)."""
    to_remove = [
        n.id
        for n in graph.iter_concepts()
        if n.metadata.get("cartridge") == cartridge_name
    ]
    for node_id in to_remove:
        graph.graph.remove_node(node_id)
    return len(to_remove)
