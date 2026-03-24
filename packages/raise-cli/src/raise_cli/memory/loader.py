"""JSONL loader for memory concepts.

This module provides functions to load memory concepts from JSONL files
in the .raise/rai/memory/ directory.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryLoadResult,
    MemoryScope,
)


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to parse.

    Returns:
        Parsed date object.

    Raises:
        ValueError: If date string is invalid.
    """
    return date.fromisoformat(date_str)


def load_pattern(
    data: dict[str, Any], scope: MemoryScope = MemoryScope.PROJECT
) -> MemoryConcept:
    """Load a pattern concept from JSONL data.

    Args:
        data: Dictionary from JSONL line.
        scope: Memory scope (global, project, or personal).

    Returns:
        MemoryConcept for the pattern.
    """
    # Handle schema variations: 'content' or 'pattern' field
    content = data.get("content") or data.get("pattern", "")
    # Handle date field variations: 'created' or 'date'
    date_str = data.get("created") or data.get("date", "")

    metadata: dict[str, Any] = {
        "sub_type": data.get("type", "unknown"),
        "learned_from": data.get("learned_from"),
        "scope": scope.value,
    }

    # Surface base/version for pattern versioning (F14.6)
    if data.get("base") is not None:
        metadata["base"] = data["base"]
    if data.get("version") is not None:
        metadata["version"] = data["version"]

    return MemoryConcept(
        id=data["id"],
        type=MemoryConceptType.PATTERN,
        content=content,
        context=data.get("context", []),
        created=parse_date(date_str),
        metadata=metadata,
    )


def load_calibration(
    data: dict[str, Any], scope: MemoryScope = MemoryScope.PROJECT
) -> MemoryConcept:
    """Load a calibration concept from JSONL data.

    Args:
        data: Dictionary from JSONL line.
        scope: Memory scope (global, project, or personal).

    Returns:
        MemoryConcept for the calibration.
    """
    # Handle schema variations for name and story fields
    name = data.get("name") or data.get("feature_name", "unknown")
    # Backward compat: try "story" (new), then "feature" (old data)
    story = data.get("story") or data.get("feature") or data.get("story_id", "unknown")
    # Handle date field variations: 'created' or 'date'
    date_str = data.get("created") or data.get("date", "")
    # Handle velocity field variations: 'ratio' or 'velocity'
    velocity = data.get("ratio") or data.get("velocity")

    # Build content summary from calibration data
    content_parts = [f"{name} ({story})"]
    if data.get("actual_min"):
        content_parts.append(f"actual: {data['actual_min']}min")
    if velocity:
        content_parts.append(f"velocity: {velocity}x")
    content = " - ".join(content_parts)

    # Build context from story and size
    context = [story, data["size"].lower()]
    if data.get("kata_cycle"):
        context.append("kata-cycle")

    return MemoryConcept(
        id=data.get("id") or data.get("story_id", "unknown"),
        type=MemoryConceptType.CALIBRATION,
        content=content,
        context=context,
        created=parse_date(date_str),
        metadata={
            "story": story,
            "name": name,
            "size": data["size"],
            "sp": data.get("sp"),
            "estimated_min": data.get("estimated_min"),
            "actual_min": data.get("actual_min"),
            "ratio": velocity,
            "kata_cycle": data.get("kata_cycle", False),
            "notes": data.get("notes"),
            "scope": scope.value,
        },
    )


def load_session(
    data: dict[str, Any], scope: MemoryScope = MemoryScope.PROJECT
) -> MemoryConcept:
    """Load a session concept from JSONL data.

    Args:
        data: Dictionary from JSONL line.
        scope: Memory scope (global, project, or personal).

    Returns:
        MemoryConcept for the session.
    """
    # Handle schema variations: 'topic' or 'summary'
    topic = data.get("topic") or data.get("summary", "unknown")

    # Build content from topic and outcomes
    outcomes_str = ", ".join(data.get("outcomes", [])[:3])
    content = f"{topic}: {outcomes_str}"

    # Build context from type and outcomes keywords
    context = [data["type"]]
    # Extract keywords from topic
    topic_words = topic.lower().split()
    context.extend([w for w in topic_words if len(w) > 3][:3])

    return MemoryConcept(
        id=data["id"],
        type=MemoryConceptType.SESSION,
        content=content,
        context=context,
        created=parse_date(data["date"]),
        metadata={
            "session_type": data["type"],
            "topic": topic,
            "outcomes": data.get("outcomes", []),
            "log_path": data.get("log_path"),
            "scope": scope.value,
        },
    )


def load_jsonl_file(
    file_path: Path,
    concept_type: MemoryConceptType,
    scope: MemoryScope = MemoryScope.PROJECT,
) -> tuple[list[MemoryConcept], list[str]]:
    """Load concepts from a single JSONL file.

    Args:
        file_path: Path to the JSONL file.
        concept_type: Type of concepts in the file.
        scope: Memory scope to assign to loaded concepts.

    Returns:
        Tuple of (concepts list, errors list).
    """
    concepts: list[MemoryConcept] = []
    errors: list[str] = []

    if not file_path.exists():
        return concepts, errors

    loader_map = {
        MemoryConceptType.PATTERN: load_pattern,
        MemoryConceptType.CALIBRATION: load_calibration,
        MemoryConceptType.SESSION: load_session,
    }
    loader = loader_map[concept_type]

    with file_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                concept = loader(data, scope=scope)
                concepts.append(concept)
            except (KeyError, ValueError) as e:
                errors.append(f"{file_path.name}:{line_num}: {e}")

    return concepts, errors


def load_memory_from_directory(memory_dir: Path) -> MemoryLoadResult:
    """Load all memory concepts from a .raise/rai/memory/ directory.

    Args:
        memory_dir: Path to the memory directory.

    Returns:
        MemoryLoadResult with all loaded concepts.
    """
    all_concepts: list[MemoryConcept] = []
    all_errors: list[str] = []
    files_processed = 0

    # Define files and their types
    file_mappings = [
        (memory_dir / "patterns.jsonl", MemoryConceptType.PATTERN),
        (memory_dir / "calibration.jsonl", MemoryConceptType.CALIBRATION),
        (memory_dir / "sessions" / "index.jsonl", MemoryConceptType.SESSION),
    ]

    for file_path, concept_type in file_mappings:
        if file_path.exists():
            concepts, errors = load_jsonl_file(file_path, concept_type)
            all_concepts.extend(concepts)
            all_errors.extend(errors)
            files_processed += 1

    return MemoryLoadResult(
        concepts=all_concepts,
        total=len(all_concepts),
        files_processed=files_processed,
        errors=all_errors,
    )
