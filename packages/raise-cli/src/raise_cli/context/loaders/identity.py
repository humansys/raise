"""Identity loader for the context graph.

Loads Rai identity values and boundaries from core.yaml as principle
nodes tagged with always_on=True.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.compat import portable_path
from raise_core.graph.models import GraphNode


def load_identity(project_root: Path) -> list[GraphNode]:
    """Load Rai identity values and boundaries from core.yaml.

    Reads structured YAML with values, boundaries, and principles sections.

    Args:
        project_root: Root directory for the project.

    Returns:
        List of GraphNode for identity concepts.
    """
    identity_file = project_root / ".raise" / "rai" / "identity" / "core.yaml"
    if not identity_file.exists():
        return []

    try:
        raw: Any = yaml.safe_load(identity_file.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []

    if not isinstance(raw, dict):
        return []
    data = cast("dict[str, Any]", raw)

    try:
        source_file = portable_path(identity_file, project_root)
    except ValueError:
        source_file = str(identity_file)

    now = datetime.now(tz=UTC).isoformat()
    nodes: list[GraphNode] = []

    values: list[dict[str, Any]] = data.get("values", [])
    for value in values:
        num = str(value["number"])
        name: str = value["name"]
        desc: str = value.get("description", "")
        content = f"{name} — {desc}" if desc else name

        nodes.append(
            GraphNode(
                id=f"RAI-VAL-{num}",
                type="principle",
                content=content,
                source_file=source_file,
                created=now,
                metadata={
                    "always_on": True,
                    "identity_type": "value",
                    "value_number": num,
                    "value_name": name,
                },
            )
        )

    boundaries: dict[str, Any] = data.get("boundaries", {})
    will_items: list[str] = boundaries.get("will", [])
    wont_items: list[str] = boundaries.get("wont", [])

    counter = 1
    for item in will_items:
        nodes.append(
            GraphNode(
                id=f"RAI-BND-{counter}",
                type="principle",
                content=item,
                source_file=source_file,
                created=now,
                metadata={
                    "always_on": True,
                    "identity_type": "boundary",
                    "boundary_kind": "will",
                },
            )
        )
        counter += 1

    for item in wont_items:
        nodes.append(
            GraphNode(
                id=f"RAI-BND-{counter}",
                type="principle",
                content=item,
                source_file=source_file,
                created=now,
                metadata={
                    "always_on": True,
                    "identity_type": "boundary",
                    "boundary_kind": "wont",
                },
            )
        )
        counter += 1

    return nodes
