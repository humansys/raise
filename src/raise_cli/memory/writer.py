"""Writer module for appending memory entries to JSONL files.

This module provides functions to append new patterns, calibrations,
and sessions to the memory JSONL files, with auto-ID generation
and cache invalidation.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.memory.cache import MemoryCache
from raise_cli.memory.models import PatternSubType


class PatternInput(BaseModel):
    """Input for creating a new pattern entry.

    Attributes:
        content: Pattern description.
        sub_type: Pattern sub-type (codebase, process, architecture, technical).
        context: Context keywords for retrieval.
        learned_from: Feature/session where pattern was learned.
    """

    content: str = Field(..., description="Pattern description")
    sub_type: PatternSubType = Field(
        default=PatternSubType.PROCESS, description="Pattern sub-type"
    )
    context: list[str] = Field(default_factory=list, description="Context keywords")
    learned_from: str | None = Field(
        default=None, description="Feature/session where learned"
    )


class CalibrationInput(BaseModel):
    """Input for creating a new calibration entry.

    Attributes:
        feature: Feature ID (e.g., 'F3.5').
        name: Feature name.
        size: T-shirt size (XS, S, M, L, XL).
        sp: Story points.
        estimated_min: Estimated minutes (if any).
        actual_min: Actual minutes.
        kata_cycle: Whether kata cycle was followed.
        notes: Additional notes.
    """

    feature: str = Field(..., description="Feature ID (e.g., 'F3.5')")
    name: str = Field(..., description="Feature name")
    size: str = Field(..., description="T-shirt size (XS, S, M, L, XL)")
    sp: int | None = Field(default=None, description="Story points")
    estimated_min: int | None = Field(default=None, description="Estimated minutes")
    actual_min: int = Field(..., description="Actual minutes")
    kata_cycle: bool = Field(default=True, description="Kata cycle followed")
    notes: str | None = Field(default=None, description="Additional notes")


class SessionInput(BaseModel):
    """Input for creating a new session entry.

    Attributes:
        topic: Session topic.
        session_type: Session type (feature, research, maintenance, etc.).
        outcomes: List of session outcomes.
        log_path: Path to session log file (if any).
    """

    topic: str = Field(..., description="Session topic")
    session_type: str = Field(
        default="feature", description="Session type (feature, research, etc.)"
    )
    outcomes: list[str] = Field(default_factory=list, description="Session outcomes")
    log_path: str | None = Field(default=None, description="Path to session log")


class WriteResult(BaseModel):
    """Result of a write operation.

    Attributes:
        success: Whether write succeeded.
        id: Generated ID for the entry.
        file_path: Path to the file written.
        message: Status message.
    """

    success: bool = Field(..., description="Whether write succeeded")
    id: str = Field(..., description="Generated ID")
    file_path: str = Field(..., description="Path to file written")
    message: str = Field(default="", description="Status message")


def _get_next_id(file_path: Path, prefix: str) -> str:
    """Get next available ID for a JSONL file.

    Scans existing entries to find max ID and increments.

    Args:
        file_path: Path to JSONL file.
        prefix: ID prefix (e.g., 'PAT', 'CAL', 'SES').

    Returns:
        Next ID (e.g., 'PAT-031' if max is 'PAT-030').
    """
    max_num = 0

    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry_id = data.get("id", "")
                    if entry_id.startswith(prefix + "-"):
                        num_str = entry_id[len(prefix) + 1 :]
                        num = int(num_str)
                        max_num = max(max_num, num)
                except (json.JSONDecodeError, ValueError):
                    continue

    return f"{prefix}-{max_num + 1:03d}"


def _append_jsonl(file_path: Path, data: dict[str, Any]) -> None:
    """Append a JSON object as a line to a JSONL file.

    Args:
        file_path: Path to JSONL file.
        data: Dictionary to serialize as JSON line.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def append_pattern(
    memory_dir: Path,
    input_data: PatternInput,
    created: date | None = None,
) -> WriteResult:
    """Append a new pattern to patterns.jsonl.

    Args:
        memory_dir: Path to .rai/memory/ directory.
        input_data: Pattern input data.
        created: Date created (defaults to today).

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir / "patterns.jsonl"
    pattern_id = _get_next_id(file_path, "PAT")
    created_date = created or date.today()

    entry = {
        "id": pattern_id,
        "type": input_data.sub_type.value,
        "content": input_data.content,
        "context": input_data.context,
        "learned_from": input_data.learned_from,
        "created": created_date.isoformat(),
    }

    _append_jsonl(file_path, entry)

    # Invalidate cache to trigger rebuild
    cache = MemoryCache(memory_dir)
    cache.invalidate()

    return WriteResult(
        success=True,
        id=pattern_id,
        file_path=str(file_path),
        message=f"Pattern {pattern_id} appended to {file_path.name}",
    )


def append_calibration(
    memory_dir: Path,
    input_data: CalibrationInput,
    created: date | None = None,
) -> WriteResult:
    """Append a new calibration to calibration.jsonl.

    Args:
        memory_dir: Path to .rai/memory/ directory.
        input_data: Calibration input data.
        created: Date created (defaults to today).

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir / "calibration.jsonl"
    cal_id = _get_next_id(file_path, "CAL")
    created_date = created or date.today()

    # Calculate ratio if both estimated and actual present
    ratio: float | None = None
    if input_data.estimated_min and input_data.actual_min:
        ratio = round(input_data.estimated_min / input_data.actual_min, 1)

    entry = {
        "id": cal_id,
        "feature": input_data.feature,
        "name": input_data.name,
        "size": input_data.size,
        "sp": input_data.sp,
        "estimated_min": input_data.estimated_min,
        "actual_min": input_data.actual_min,
        "ratio": ratio,
        "kata_cycle": input_data.kata_cycle,
        "notes": input_data.notes,
        "created": created_date.isoformat(),
    }

    _append_jsonl(file_path, entry)

    # Invalidate cache to trigger rebuild
    cache = MemoryCache(memory_dir)
    cache.invalidate()

    return WriteResult(
        success=True,
        id=cal_id,
        file_path=str(file_path),
        message=f"Calibration {cal_id} appended to {file_path.name}",
    )


def append_session(
    memory_dir: Path,
    input_data: SessionInput,
    session_date: date | None = None,
) -> WriteResult:
    """Append a new session to sessions/index.jsonl.

    Args:
        memory_dir: Path to .rai/memory/ directory.
        input_data: Session input data.
        session_date: Session date (defaults to today).

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir / "sessions" / "index.jsonl"
    session_id = _get_next_id(file_path, "SES")
    session_date_val = session_date or date.today()

    entry = {
        "id": session_id,
        "date": session_date_val.isoformat(),
        "type": input_data.session_type,
        "topic": input_data.topic,
        "outcomes": input_data.outcomes,
        "log_path": input_data.log_path,
    }

    _append_jsonl(file_path, entry)

    # Invalidate cache to trigger rebuild
    cache = MemoryCache(memory_dir)
    cache.invalidate()

    return WriteResult(
        success=True,
        id=session_id,
        file_path=str(file_path),
        message=f"Session {session_id} appended to {file_path.name}",
    )
