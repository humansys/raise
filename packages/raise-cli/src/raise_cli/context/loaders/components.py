"""Components loader for the context graph.

Loads discovered component nodes from validated JSON files.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from raise_core.graph.models import GraphNode


def load_components(project_root: Path) -> list[GraphNode]:
    """Load discovered components from validated JSON.

    Reads components-validated.json from work/discovery directory.

    Args:
        project_root: Root directory for the project.

    Returns:
        List of GraphNode for component concepts.
    """
    validated_file = project_root / "work" / "discovery" / "components-validated.json"
    if not validated_file.exists():
        return []

    try:
        raw: Any = json.loads(validated_file.read_text(encoding="utf-8"))
        # Accept both {"components": [...]} wrapper and bare [...] array
        if isinstance(raw, list):
            components_list: list[dict[str, Any]] = raw  # type: ignore[assignment]
        else:
            components_list = raw.get("components", [])

        nodes: list[GraphNode] = []
        for comp in components_list:
            node = GraphNode(
                id=comp.get("id", ""),
                type="component",
                content=comp.get("content", ""),
                source_file=comp.get("source_file"),
                created=comp.get("created", datetime.now(tz=UTC).isoformat()),
                metadata=comp.get("metadata", {}),
            )
            nodes.append(node)

        return nodes
    except (json.JSONDecodeError, KeyError):
        return []
