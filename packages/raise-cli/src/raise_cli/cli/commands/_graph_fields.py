"""Field discovery for graph nodes (S4, RAISE-16891).

Scans a loaded graph to discover queryable metadata fields per node type,
infers coarse types from Python values, resolves custom-field display names
from existing ``backlog.custom_field`` nodes, and maps each inferred type
to its allowed filter operators.
"""

from __future__ import annotations

import re
from typing import Any

from raise_core.graph.engine import Graph

_CUSTOMFIELD_RE = re.compile(r"^customfield_\d+$")

_ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$"
)

_OPERATORS_BY_TYPE: dict[str, list[str]] = {
    "string": ["eq", "neq", "contains", "startswith", "in"],
    "number": ["eq", "neq", "lt", "lte", "gt", "gte", "in"],
    "list": ["contains", "in", "eq", "neq"],
    "bool": ["eq", "neq", "exists"],
    "date": ["eq", "neq", "lt", "lte", "gt", "gte"],
    "unknown": ["eq", "neq", "exists"],
}


def _infer_type(value: Any) -> str:
    """Infer a coarse type label from a Python value."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, list):
        return "list"
    if isinstance(value, str):
        if _ISO_DATE_RE.match(value):
            return "date"
        return "string"
    if isinstance(value, dict):
        return "dict"
    if value is None:
        return "unknown"
    return "unknown"


def _merge_type(existing: str, new: str) -> str:
    """Merge two inferred types — prefer the more specific one."""
    if existing == "unknown":
        return new
    if new == "unknown":
        return existing
    if existing == new:
        return existing
    return "string"


def _build_custom_field_map(graph: Graph) -> dict[str, str]:
    """Build customfield_NNNNN → display_name from backlog.custom_field nodes."""
    name_map: dict[str, str] = {}
    for concept in graph.iter_concepts():
        if concept.type == "backlog.custom_field":
            field_id = concept.metadata.get("field_id", "")
            if field_id and concept.content:
                name_map[field_id] = concept.content
    return name_map


def _scan_metadata_types(
    graph: Graph,
    type_filter: str | None,
) -> dict[str, str]:
    """Scan graph nodes and collect {field_name: inferred_type} for all metadata keys."""
    field_types: dict[str, str] = {}
    for concept in graph.iter_concepts():
        if type_filter and not _type_matches(concept.type, type_filter):
            continue
        meta = concept.metadata
        if not meta:
            continue
        for key, value in meta.items():
            if key == "custom_fields" and isinstance(value, dict):
                for cf_key, cf_value in value.items():
                    full_key = f"custom_fields.{cf_key}"
                    inferred = _infer_type(cf_value)
                    field_types[full_key] = _merge_type(
                        field_types.get(full_key, "unknown"), inferred
                    )
            else:
                inferred = _infer_type(value)
                field_types[key] = _merge_type(
                    field_types.get(key, "unknown"), inferred
                )
    return field_types


def _resolve_display_name(field_name: str, cf_name_map: dict[str, str]) -> str | None:
    """Resolve a custom-field display name from the backlog.custom_field map."""
    if field_name.startswith("custom_fields."):
        raw_id = field_name.split(".", 1)[1]
        if raw_id in cf_name_map:
            return f"{cf_name_map[raw_id]} ({raw_id})"
    elif _CUSTOMFIELD_RE.match(field_name) and field_name in cf_name_map:
        return f"{cf_name_map[field_name]} ({field_name})"
    return None


def discover_fields(
    graph: Graph,
    type_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Discover queryable metadata fields from the graph.

    Args:
        graph: Loaded knowledge graph to scan.
        type_filter: Optional type prefix filter (e.g. "backlog.story").
            Uses prefix match: "backlog" matches "backlog.story", etc.

    Returns:
        List of field descriptors sorted by field name, each with:
        ``field``, ``type``, ``operators``, ``display_name``.
    """
    all_fields = _scan_metadata_types(graph, type_filter)
    cf_name_map = _build_custom_field_map(graph)

    results: list[dict[str, Any]] = []
    for field_name, field_type in sorted(all_fields.items()):
        operators = _OPERATORS_BY_TYPE.get(field_type, _OPERATORS_BY_TYPE["unknown"])
        results.append(
            {
                "field": field_name,
                "type": field_type,
                "operators": operators,
                "display_name": _resolve_display_name(field_name, cf_name_map),
            }
        )

    return results


def _type_matches(node_type: str, filter_type: str) -> bool:
    """Check if node_type matches filter (exact or prefix with dot separator)."""
    return node_type == filter_type or node_type.startswith(filter_type + ".")
