"""Graph diff engine for detecting changes between unified graph builds.

Compares two Graph instances by node presence and semantic fields
(content, type, metadata). Produces a structured GraphDiff with impact
classification and affected module list.

Architecture: E16 Incremental Coherence — Layer 1 (deterministic)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode, NodeType

# Node types that indicate module-level impact
_MODULE_IMPACT_TYPES: frozenset[NodeType] = frozenset({"module", "component"})

# Node types that indicate architectural impact
_ARCHITECTURAL_IMPACT_TYPES: frozenset[NodeType] = frozenset(
    {"bounded_context", "layer"}
)

# Fields compared for modification detection
_COMPARED_FIELDS: tuple[str, ...] = ("content", "type", "metadata")


class NodeChange(BaseModel):
    """A change to a single node between two graph builds.

    Attributes:
        node_id: The unique node identifier.
        change_type: Whether the node was added, removed, or modified.
        old_value: The node in the old graph (None for added).
        new_value: The node in the new graph (None for removed).
        changed_fields: Which semantic fields changed (for modified nodes).
    """

    node_id: str
    change_type: Literal["added", "removed", "modified"]
    old_value: GraphNode | None = None
    new_value: GraphNode | None = None
    changed_fields: list[str] = Field(default_factory=list)


class GraphDiff(BaseModel):
    """Structured diff between two unified graph builds.

    Attributes:
        node_changes: List of individual node changes.
        impact: Overall impact level for downstream consumers.
        affected_modules: Module node IDs that changed (sorted).
        summary: Deterministic human-readable summary string.
    """

    node_changes: list[NodeChange] = Field(default_factory=lambda: [])
    impact: Literal["none", "module", "architectural"] = "none"
    affected_modules: list[str] = Field(default_factory=lambda: [])
    summary: str = "no changes"


def diff_graphs(old: Graph, new: Graph) -> GraphDiff:
    """Compare two unified graphs and return structured diff.

    Compares nodes by presence (added/removed) and by semantic fields
    (content, type, metadata) for modification detection. Ignores
    created and source_file fields.

    Args:
        old: The previous graph (before build).
        new: The current graph (after build).

    Returns:
        GraphDiff with node changes, impact classification, and affected modules.
    """
    old_ids = {node.id for node in old.iter_concepts()}
    new_ids = {node.id for node in new.iter_concepts()}

    changes: list[NodeChange] = []

    # Added nodes
    for node_id in sorted(new_ids - old_ids):
        node = new.get_concept(node_id)
        changes.append(
            NodeChange(
                node_id=node_id,
                change_type="added",
                old_value=None,
                new_value=node,
                changed_fields=[],
            )
        )

    # Removed nodes
    for node_id in sorted(old_ids - new_ids):
        node = old.get_concept(node_id)
        changes.append(
            NodeChange(
                node_id=node_id,
                change_type="removed",
                old_value=node,
                new_value=None,
                changed_fields=[],
            )
        )

    # Modified nodes
    for node_id in sorted(old_ids & new_ids):
        old_node = old.get_concept(node_id)
        new_node = new.get_concept(node_id)
        if old_node is None or new_node is None:
            continue

        changed_fields = _compare_nodes(old_node, new_node)
        if changed_fields:
            changes.append(
                NodeChange(
                    node_id=node_id,
                    change_type="modified",
                    old_value=old_node,
                    new_value=new_node,
                    changed_fields=changed_fields,
                )
            )

    if not changes:
        return GraphDiff()

    impact = _classify_impact(changes)
    affected_modules = _derive_affected_modules(changes)
    summary = _build_summary(changes, affected_modules)

    return GraphDiff(
        node_changes=changes,
        impact=impact,
        affected_modules=affected_modules,
        summary=summary,
    )


def _compare_nodes(old: GraphNode, new: GraphNode) -> list[str]:
    """Compare two nodes on semantic fields only.

    Returns list of field names that differ. Ignores created and source_file.
    """
    changed: list[str] = []
    for field in _COMPARED_FIELDS:
        old_val = getattr(old, field)
        new_val = getattr(new, field)
        if old_val != new_val:
            changed.append(field)
    return changed


def _classify_impact(
    changes: list[NodeChange],
) -> Literal["none", "module", "architectural"]:
    """Classify overall impact from node changes.

    architectural > module > none.
    """
    has_module = False

    for change in changes:
        node = change.new_value or change.old_value
        if node is None:
            continue
        if node.type in _ARCHITECTURAL_IMPACT_TYPES:
            return "architectural"
        if node.type in _MODULE_IMPACT_TYPES:
            has_module = True

    return "module" if has_module else "none"


def _derive_affected_modules(changes: list[NodeChange]) -> list[str]:
    """Extract sorted list of module IDs from changed nodes."""
    modules: list[str] = []
    for change in changes:
        node = change.new_value or change.old_value
        if node is not None and node.type == "module":
            modules.append(change.node_id)
    return sorted(modules)


def _build_summary(changes: list[NodeChange], affected_modules: list[str]) -> str:
    """Build deterministic summary string from changes."""
    added = sum(1 for c in changes if c.change_type == "added")
    removed = sum(1 for c in changes if c.change_type == "removed")
    modified = sum(1 for c in changes if c.change_type == "modified")

    total = len(changes)
    parts: list[str] = []
    if added:
        parts.append(f"{added} added")
    if removed:
        parts.append(f"{removed} removed")
    if modified:
        parts.append(f"{modified} modified")

    detail = ", ".join(parts)
    summary = f"{total} nodes changed ({detail})"

    if affected_modules:
        mod_list = ", ".join(affected_modules)
        count = len(affected_modules)
        label = "module" if count == 1 else "modules"
        summary += f", {count} {label} affected ({mod_list})"

    return summary
