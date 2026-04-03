"""Structural extraction for the context graph.

Extracts bounded contexts, architectural layers, and constraint edges
from architecture documentation nodes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from raise_core.graph.models import GraphEdge, GraphNode


def extract_bounded_contexts(  # noqa: C901 -- complexity 15, refactor deferred
    all_nodes: list[GraphNode],  # noqa: ARG001 — kept for consistent extract_* signature
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Extract bounded context nodes and belongs_to edges from domain model."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    dm_node = node_by_id.get("arch-domain-model")
    if dm_node is None:
        return nodes, edges

    now = datetime.now(tz=UTC).isoformat()

    bcs: list[dict[str, Any]] = dm_node.metadata.get("bounded_contexts", [])
    for bc in bcs:
        bc_name: str = bc.get("name", "")
        if not bc_name:
            continue
        bc_id = f"bc-{bc_name}"
        nodes.append(
            GraphNode(
                id=bc_id,
                type="bounded_context",
                content=bc.get("description", ""),
                source_file=dm_node.source_file,
                created=now,
                metadata={
                    "bc_type": "bounded_context",
                    "modules": bc.get("modules", []),
                },
            )
        )
        modules: list[str] = bc.get("modules", [])
        for mod_name in modules:
            mod_id = f"mod-{mod_name}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=mod_id, target=bc_id, type="belongs_to", weight=1.0
                    )
                )

    shared: dict[str, Any] = dm_node.metadata.get("shared_kernel", {})
    if shared:
        nodes.append(
            GraphNode(
                id="bc-shared-kernel",
                type="bounded_context",
                content=shared.get("description", ""),
                source_file=dm_node.source_file,
                created=now,
                metadata={
                    "bc_type": "shared_kernel",
                    "modules": shared.get("modules", []),
                },
            )
        )
        for mod_name in shared.get("modules", []):
            mod_id = f"mod-{mod_name}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=mod_id,
                        target="bc-shared-kernel",
                        type="belongs_to",
                        weight=1.0,
                    )
                )

    app_layer: dict[str, Any] = dm_node.metadata.get("application_layer", {})
    if app_layer:
        nodes.append(
            GraphNode(
                id="bc-application-layer",
                type="bounded_context",
                content=app_layer.get("description", ""),
                source_file=dm_node.source_file,
                created=now,
                metadata={
                    "bc_type": "application_layer",
                    "modules": app_layer.get("modules", []),
                },
            )
        )
        for mod_name in app_layer.get("modules", []):
            mod_id = f"mod-{mod_name}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=mod_id,
                        target="bc-application-layer",
                        type="belongs_to",
                        weight=1.0,
                    )
                )

    dist: dict[str, Any] = dm_node.metadata.get("distribution", {})
    if dist:
        nodes.append(
            GraphNode(
                id="bc-distribution",
                type="bounded_context",
                content=dist.get("description", ""),
                source_file=dm_node.source_file,
                created=now,
                metadata={
                    "bc_type": "distribution",
                    "modules": dist.get("modules", []),
                },
            )
        )
        for mod_name in dist.get("modules", []):
            mod_id = f"mod-{mod_name}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=mod_id,
                        target="bc-distribution",
                        type="belongs_to",
                        weight=1.0,
                    )
                )

    return nodes, edges


def extract_layers(
    all_nodes: list[GraphNode],  # noqa: ARG001 — kept for consistent extract_* signature
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Extract layer nodes and in_layer edges from system design."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    design_node = node_by_id.get("arch-design")
    if design_node is None:
        return nodes, edges

    now = datetime.now(tz=UTC).isoformat()

    layers: list[dict[str, Any]] = design_node.metadata.get("layers", [])
    for layer in layers:
        layer_name: str = layer.get("name", "")
        if not layer_name:
            continue
        layer_id = f"lyr-{layer_name}"
        nodes.append(
            GraphNode(
                id=layer_id,
                type="layer",
                content=layer.get("description", ""),
                source_file=design_node.source_file,
                created=now,
                metadata={"modules": layer.get("modules", [])},
            )
        )
        modules: list[str] = layer.get("modules", [])
        for mod_name in modules:
            mod_id = f"mod-{mod_name}"
            if mod_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=mod_id, target=layer_id, type="in_layer", weight=1.0
                    )
                )

    return nodes, edges


def extract_constraints(
    all_nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Extract constrained_by edges from guardrail scope metadata."""
    edges: list[GraphEdge] = []
    bc_ids = [n.id for n in node_by_id.values() if n.type == "bounded_context"]

    for node in all_nodes:
        if node.type != "guardrail":
            continue

        scope: Any = node.metadata.get("constraint_scope")
        if scope is None:
            continue

        if scope == "all_bounded_contexts":
            targets = bc_ids
        elif isinstance(scope, list):
            targets = [t for t in cast("list[str]", scope) if t in node_by_id]
        else:
            continue

        for target_id in targets:
            edges.append(
                GraphEdge(
                    source=target_id,
                    target=node.id,
                    type="constrained_by",
                    weight=1.0,
                )
            )

    return edges
