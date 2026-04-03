"""Memory loader for the context graph.

Loads memory concepts from JSONL files across global, project,
and personal tiers with scope-based deduplication.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from raise_cli.compat import portable_path
from raise_cli.config.paths import get_global_rai_dir, get_memory_dir, get_personal_dir
from raise_cli.memory.models import MemoryScope
from raise_core.graph.models import GraphNode


def load_memory(project_root: Path) -> list[GraphNode]:
    """Load concepts from memory JSONL files across all tiers.

    Loads from three directories with scope tracking:
    - Global (~/.rai/): Universal patterns and calibration
    - Project (.raise/rai/memory/): Shared project patterns
    - Personal (.raise/rai/personal/): Developer-specific data

    Sessions are only loaded from personal directory (developer-specific).

    Args:
        project_root: Root directory for the project.

    Returns:
        List of GraphNode for memory concepts with scope metadata.
    """
    nodes: list[GraphNode] = []

    # 1. Load from global directory (~/.rai/)
    global_dir = get_global_rai_dir()
    if global_dir.exists():
        nodes.extend(
            _load_memory_from_dir(
                global_dir, MemoryScope.GLOBAL, project_root, sessions=False
            )
        )

    # 2. Load from project directory (.raise/rai/memory/)
    project_dir = get_memory_dir(project_root)
    if project_dir.exists():
        nodes.extend(
            _load_memory_from_dir(
                project_dir, MemoryScope.PROJECT, project_root, sessions=False
            )
        )

    # 3. Load from personal directory (.raise/rai/personal/)
    personal_dir = get_personal_dir(project_root)
    if personal_dir.exists():
        nodes.extend(
            _load_memory_from_dir(
                personal_dir, MemoryScope.PERSONAL, project_root, sessions=True
            )
        )

    # Apply precedence: personal > project > global
    return _deduplicate_by_precedence(nodes)


def _load_memory_from_dir(
    memory_dir: Path,
    scope: MemoryScope,
    project_root: Path,
    sessions: bool = True,
) -> list[GraphNode]:
    """Load memory concepts from a single directory with scope.

    Args:
        memory_dir: Directory containing JSONL files.
        scope: Scope to assign to loaded concepts.
        project_root: Root directory for portable path computation.
        sessions: Whether to load sessions from this directory.

    Returns:
        List of GraphNode with scope in metadata.
    """
    nodes: list[GraphNode] = []

    # Load patterns
    patterns_file = memory_dir / "patterns.jsonl"
    if patterns_file.exists():
        nodes.extend(_load_jsonl(patterns_file, "pattern", project_root, scope))

    # Load calibration
    calibration_file = memory_dir / "calibration.jsonl"
    if calibration_file.exists():
        nodes.extend(_load_jsonl(calibration_file, "calibration", project_root, scope))

    # Load sessions (only if requested)
    if sessions:
        sessions_file = memory_dir / "sessions" / "index.jsonl"
        if sessions_file.exists():
            nodes.extend(_load_jsonl(sessions_file, "session", project_root, scope))

    return nodes


def _deduplicate_by_precedence(nodes: list[GraphNode]) -> list[GraphNode]:
    """Deduplicate nodes by ID using scope precedence.

    When the same ID appears in multiple tiers, keep only the
    highest-precedence version: personal > project > global.

    Args:
        nodes: List of nodes potentially with duplicate IDs.

    Returns:
        Deduplicated list with highest-precedence version of each ID.
    """
    # Precedence order: higher number = higher priority
    scope_priority = {
        MemoryScope.GLOBAL.value: 1,
        MemoryScope.PROJECT.value: 2,
        MemoryScope.PERSONAL.value: 3,
    }

    # Track best node for each ID
    best_by_id: dict[str, GraphNode] = {}

    for node in nodes:
        node_scope = node.metadata.get("scope", MemoryScope.PROJECT.value)
        node_priority = scope_priority.get(node_scope, 0)

        if node.id not in best_by_id:
            best_by_id[node.id] = node
        else:
            existing_scope = best_by_id[node.id].metadata.get(
                "scope", MemoryScope.PROJECT.value
            )
            existing_priority = scope_priority.get(existing_scope, 0)

            if node_priority > existing_priority:
                best_by_id[node.id] = node

    return list(best_by_id.values())


def _load_jsonl(
    file_path: Path,
    node_type: str,
    project_root: Path,
    scope: MemoryScope = MemoryScope.PROJECT,
) -> list[GraphNode]:
    """Load concepts from a JSONL file.

    Args:
        file_path: Path to JSONL file.
        node_type: Type to assign to nodes (pattern, calibration, session).
        project_root: Root directory for portable path computation.
        scope: Memory scope to assign to loaded concepts.

    Returns:
        List of GraphNode parsed from file.
    """
    nodes: list[GraphNode] = []

    # Try to make path relative, fallback to absolute
    try:
        source_file = portable_path(file_path, project_root)
    except ValueError:
        source_file = str(file_path)

    for line in file_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        try:
            record: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            continue

        node = _memory_record_to_node(record, node_type, source_file, scope)
        if node:
            nodes.append(node)

    return nodes


def _memory_record_to_node(
    record: dict[str, Any],
    node_type: str,
    source_file: str,
    scope: MemoryScope = MemoryScope.PROJECT,
) -> GraphNode | None:
    """Convert memory JSONL record to GraphNode.

    Args:
        record: Parsed JSON record.
        node_type: Type of memory concept.
        source_file: Source file path.
        scope: Memory scope for this concept.

    Returns:
        GraphNode or None if record is invalid.
    """
    record_id = record.get("id")
    if not record_id:
        return None

    # Build content based on type
    if node_type == "pattern":
        content = record.get("content", "")
    elif node_type == "calibration":
        # Calibration uses story + name (backward compat: old "feature" key)
        story = record.get("story") or record.get("feature", "")
        name = record.get("name", "")
        content = f"{story}: {name}" if story else name
    elif node_type == "session":
        content = record.get("topic", record.get("summary", ""))
    else:
        content = record.get("content", "")

    # Get created date
    created = record.get("created") or record.get("date", "")
    if not created:
        created = datetime.now(tz=UTC).isoformat()

    # Core fields to exclude from metadata
    core_fields = {"id", "type", "content", "created", "date"}

    # Build metadata from remaining fields
    metadata: dict[str, Any] = {k: v for k, v in record.items() if k not in core_fields}

    # Add scope to metadata
    metadata["scope"] = scope.value

    return GraphNode(
        id=str(record_id),
        type=node_type,  # type: ignore[arg-type]
        content=str(content),
        source_file=source_file,
        created=str(created),
        metadata=metadata,
    )
