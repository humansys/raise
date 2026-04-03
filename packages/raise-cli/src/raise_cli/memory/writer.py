"""Writer module for appending memory entries to JSONL files.

This module provides functions to append new patterns, calibrations,
and sessions to the memory JSONL files, with auto-ID generation
and cache invalidation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter
from raise_cli.config.paths import get_global_rai_dir, get_memory_dir, get_personal_dir
from raise_cli.memory.models import MemoryScope, PatternSubType


@dataclass
class SessionIndexValidation:
    """Result of session index validation.

    Attributes:
        is_valid: True if no issues found.
        total_entries: Number of entries in index.
        entries_without_id: Entries missing ID field.
        non_standard_ids: IDs not matching SES-NNN format.
        duplicate_ids: IDs that appear more than once.
        max_id: Highest SES-NNN number found.
        gaps: List of (start, end) tuples for gaps > 5 in sequence.
    """

    is_valid: bool
    total_entries: int
    entries_without_id: int
    non_standard_ids: list[str]
    duplicate_ids: list[str]
    max_id: int
    gaps: list[tuple[int, int]]

    def summary(self) -> str:
        """Generate human-readable summary of validation issues."""
        if self.is_valid:
            return f"Session index OK: {self.total_entries} entries, max ID: SES-{self.max_id:03d}"

        issues: list[str] = []
        if self.entries_without_id > 0:
            issues.append(f"{self.entries_without_id} entries missing ID")
        if self.non_standard_ids:
            issues.append(f"{len(self.non_standard_ids)} non-standard IDs")
        if self.duplicate_ids:
            issues.append(f"duplicates: {', '.join(self.duplicate_ids)}")
        if self.gaps:
            gap_strs = [f"{s}-{e}" for s, e in self.gaps]
            issues.append(f"gaps: {', '.join(gap_strs)}")

        return f"Session index issues: {'; '.join(issues)}"


@dataclass
class _ParsedSessionEntries:
    """Intermediate result from parsing session index entries."""

    total_entries: int
    entries_without_id: int
    non_standard_ids: list[str]
    id_counts: dict[str, int]
    ses_numbers: list[int]


def _parse_session_entries(file_path: Path) -> _ParsedSessionEntries:
    """Parse session index JSONL and collect statistics."""
    ses_pattern = re.compile(r"^SES-(\d{3})$")
    entries_without_id = 0
    non_standard_ids: list[str] = []
    id_counts: dict[str, int] = {}
    ses_numbers: list[int] = []

    with file_path.open("r", encoding="utf-8") as f:
        total_entries = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_entries += 1
            try:
                data = json.loads(line)
                entry_id = data.get("id")

                if entry_id is None:
                    entries_without_id += 1
                    continue

                id_counts[entry_id] = id_counts.get(entry_id, 0) + 1

                match = ses_pattern.match(entry_id)
                if match:
                    ses_numbers.append(int(match.group(1)))
                else:
                    non_standard_ids.append(entry_id)

            except json.JSONDecodeError:
                entries_without_id += 1

    return _ParsedSessionEntries(
        total_entries=total_entries,
        entries_without_id=entries_without_id,
        non_standard_ids=non_standard_ids,
        id_counts=id_counts,
        ses_numbers=ses_numbers,
    )


def _find_sequence_gaps(
    ses_numbers: list[int], gap_threshold: int = 5
) -> tuple[int, list[tuple[int, int]]]:
    """Find gaps in session number sequence.

    Returns:
        Tuple of (max_id, list of gap tuples).
    """
    if not ses_numbers:
        return 0, []

    sorted_nums = sorted(ses_numbers)
    max_id = sorted_nums[-1]
    gaps: list[tuple[int, int]] = []

    for i in range(1, len(sorted_nums)):
        gap = sorted_nums[i] - sorted_nums[i - 1]
        if gap > gap_threshold:
            gaps.append((sorted_nums[i - 1], sorted_nums[i]))

    return max_id, gaps


def validate_session_index(memory_dir: Path) -> SessionIndexValidation:
    """Validate session index for data quality issues.

    Jidoka check: detect entries without IDs, non-standard formats,
    duplicates, and large gaps in sequence.

    Args:
        memory_dir: Path to .raise/rai/memory/ directory.

    Returns:
        SessionIndexValidation with findings.
    """
    file_path = memory_dir / "sessions" / "index.jsonl"

    if not file_path.exists():
        return SessionIndexValidation(
            is_valid=True,
            total_entries=0,
            entries_without_id=0,
            non_standard_ids=[],
            duplicate_ids=[],
            max_id=0,
            gaps=[],
        )

    parsed = _parse_session_entries(file_path)
    duplicate_ids = [k for k, v in parsed.id_counts.items() if v > 1]
    max_id, gaps = _find_sequence_gaps(parsed.ses_numbers)

    is_valid = (
        parsed.entries_without_id == 0
        and len(parsed.non_standard_ids) == 0
        and len(duplicate_ids) == 0
        and len(gaps) == 0
    )

    return SessionIndexValidation(
        is_valid=is_valid,
        total_entries=parsed.total_entries,
        entries_without_id=parsed.entries_without_id,
        non_standard_ids=parsed.non_standard_ids,
        duplicate_ids=duplicate_ids,
        max_id=max_id,
        gaps=gaps,
    )


class PatternInput(BaseModel):
    """Input for creating a new pattern entry.

    Attributes:
        content: Pattern description.
        sub_type: Pattern sub-type (codebase, process, architecture, technical).
        context: Context keywords for retrieval.
        learned_from: Story/session where pattern was learned.
    """

    content: str = Field(..., description="Pattern description")
    sub_type: PatternSubType = Field(
        default=PatternSubType.PROCESS, description="Pattern sub-type"
    )
    context: list[str] = Field(default_factory=list, description="Context keywords")
    learned_from: str | None = Field(
        default=None, description="Story/session where learned"
    )
    base: bool = Field(default=False, description="Whether this is a base pattern")
    version: int | None = Field(
        default=None, description="Base pattern version (for update tracking)"
    )


class CalibrationInput(BaseModel):
    """Input for creating a new calibration entry.

    Attributes:
        story: Story ID (e.g., 'F3.5').
        name: Story name.
        size: T-shirt size (XS, S, M, L, XL).
        sp: Story points.
        estimated_min: Estimated minutes (if any).
        actual_min: Actual minutes.
        kata_cycle: Whether kata cycle was followed.
        notes: Additional notes.
    """

    story: str = Field(..., description="Story ID (e.g., 'F3.5')")
    name: str = Field(..., description="Story name")
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
        session_type: Session type (story, research, maintenance, etc.).
        outcomes: List of session outcomes.
        log_path: Path to session log file (if any).
    """

    topic: str = Field(..., description="Session topic")
    session_type: str = Field(
        default="story", description="Session type (story, research, etc.)"
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


class ReinforceResult(BaseModel):
    """Result of a pattern reinforcement operation.

    Attributes:
        pattern_id: ID of the reinforced pattern.
        vote: Vote applied (+1, 0, -1).
        positives: Updated positive evaluation count.
        negatives: Updated negative evaluation count.
        evaluations: Updated total evaluation count.
        last_evaluated: ISO date of last evaluation (None if vote=0 and never evaluated).
        was_updated: False when vote=0 (N/A — file not modified).
    """

    pattern_id: str = Field(..., description="ID of the reinforced pattern")
    vote: int = Field(..., description="Vote applied (+1, 0, -1)")
    positives: int = Field(..., description="Positive evaluation count")
    negatives: int = Field(..., description="Negative evaluation count")
    evaluations: int = Field(..., description="Total evaluation count")
    last_evaluated: str | None = Field(
        default=None, description="ISO date of last evaluation"
    )
    was_updated: bool = Field(..., description="False when vote=0 (file not modified)")


def get_memory_dir_for_scope(
    scope: MemoryScope, project_root: Path | None = None
) -> Path:
    """Get the appropriate memory directory for a given scope.

    Args:
        scope: Memory scope (GLOBAL, PROJECT, or PERSONAL).
        project_root: Project root path. Defaults to cwd.

    Returns:
        Path to the memory directory for that scope.

    Example:
        >>> dir_path = get_memory_dir_for_scope(MemoryScope.GLOBAL)
        >>> # Returns ~/.rai/
        >>> dir_path = get_memory_dir_for_scope(MemoryScope.PROJECT, Path("."))
        >>> # Returns .raise/rai/memory/
    """
    if scope == MemoryScope.GLOBAL:
        return get_global_rai_dir()
    if scope == MemoryScope.PERSONAL:
        return get_personal_dir(project_root)
    # PROJECT
    return get_memory_dir(project_root)


def get_next_id(  # noqa: C901
    file_path: Path, prefix: str, developer_prefix: str | None = None
) -> str:
    """Get next available ID for a JSONL file.

    Scans existing entries to find max ID and increments.

    Args:
        file_path: Path to JSONL file.
        prefix: ID prefix (e.g., 'PAT', 'CAL', 'SES').
        developer_prefix: Optional developer prefix for multi-dev safety.
            When provided, generates e.g. 'PAT-E-001' and only counts
            IDs matching that developer's prefix.

    Returns:
        Next ID. With developer_prefix='E': 'PAT-E-001'.
        Without: 'PAT-001' (backward compatible).
    """
    max_num = 0

    # Build the full prefix to match against
    full_prefix = f"{prefix}-{developer_prefix}-" if developer_prefix else f"{prefix}-"

    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry_id = data.get("id", "")
                    if entry_id.startswith(full_prefix):
                        num_str = entry_id[len(full_prefix) :]
                        num = int(num_str)
                        max_num = max(max_num, num)
                except ValueError:
                    continue

    # Fallback: scan sibling directories matching {PREFIX}-{NNN} pattern.
    # Guards against counter reset when index.jsonl is lost.
    parent = file_path.parent
    if parent.is_dir():
        dir_pattern = re.compile(rf"^{re.escape(full_prefix)}(\d+)$")
        for entry in parent.iterdir():
            if entry.is_dir():
                m = dir_pattern.match(entry.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))

    if developer_prefix:
        return f"{prefix}-{developer_prefix}-{max_num + 1:03d}"
    return f"{prefix}-{max_num + 1:03d}"


def _append_jsonl(file_path: Path, data: dict[str, Any]) -> None:
    """Append a JSON object as a line to a JSONL file.

    Uses FilesystemAdapter for atomic append semantics.

    Args:
        file_path: Path to JSONL file.
        data: Dictionary to serialize as JSON line.
    """
    adapter = FilesystemAdapter(root=file_path.parent)
    adapter.append(Path(file_path.name), json.dumps(data))


def append_pattern(
    memory_dir: Path,
    input_data: PatternInput,
    created: date | None = None,
    scope: MemoryScope = MemoryScope.PROJECT,
    developer_prefix: str | None = None,
) -> WriteResult:
    """Append a new pattern to patterns.jsonl.

    Args:
        memory_dir: Path to memory directory (global, project, or personal).
        input_data: Pattern input data.
        created: Date created (defaults to today).
        scope: Memory scope for this pattern (affects ID generation context).
        developer_prefix: Optional developer prefix for multi-dev safety.
            When provided, generates IDs like 'PAT-E-001' instead of 'PAT-001'.

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir.resolve() / "patterns.jsonl"
    pattern_id = get_next_id(file_path, "PAT", developer_prefix=developer_prefix)
    created_date = created or date.today()

    entry: dict[str, Any] = {
        "id": pattern_id,
        "type": input_data.sub_type.value,
        "content": input_data.content,
        "context": input_data.context,
        "learned_from": input_data.learned_from,
        "created": created_date.isoformat(),
    }

    # Include base/version only for base patterns (clean output for personal patterns)
    if input_data.base:
        entry["base"] = True
        entry["version"] = input_data.version or 1

    _append_jsonl(file_path, entry)

    return WriteResult(
        success=True,
        id=pattern_id,
        file_path=str(file_path),
        message=f"Pattern {pattern_id} appended to {file_path.name} (scope: {scope.value})",
    )


def reinforce_pattern(
    file_path: Path,
    pattern_id: str,
    vote: int,
    story_id: str | None = None,  # noqa: ARG001  # NOSONAR — kept for API compat, stored in v2
) -> ReinforceResult:
    """Update reinforcement fields for a pattern in a JSONL file.

    ``story_id`` is accepted for traceability but not stored in v1.

    Vote semantics:
        +1 = implementation followed the pattern (positives + evaluations++)
        -1 = implementation contradicted the pattern (negatives + evaluations++)
         0 = not relevant to this story (N/A — file not modified)

    Rewrites the JSONL file atomically (temp file + rename) to prevent
    corruption on crash.

    Args:
        file_path: Path to the patterns.jsonl file.
        pattern_id: ID of the pattern to reinforce (e.g., 'PAT-E-183').
        vote: +1, 0, or -1.
        story_id: Optional story ID for traceability (not stored in JSONL v1).

    Returns:
        ReinforceResult with updated counts.

    Raises:
        KeyError: If pattern_id is not found in the file.
        ValueError: If file_path does not resolve to a .jsonl file.
    """
    file_path = file_path.resolve()
    if file_path.suffix != ".jsonl":
        raise ValueError(f"Expected a .jsonl file, got: {file_path.suffix!r}")
    lines = file_path.read_text(encoding="utf-8").splitlines()
    records: list[dict[str, Any]] = []
    found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        record: dict[str, Any] = json.loads(line)
        if record.get("id") == pattern_id:
            found = True
            if vote != 0:
                record["positives"] = (record.get("positives") or 0) + (
                    1 if vote == 1 else 0
                )
                record["negatives"] = (record.get("negatives") or 0) + (
                    1 if vote == -1 else 0
                )
                record["evaluations"] = (record.get("evaluations") or 0) + 1
                record["last_evaluated"] = date.today().isoformat()
        records.append(record)

    if not found:
        raise KeyError(f"Pattern '{pattern_id}' not found in {file_path}")

    target = next(r for r in records if r.get("id") == pattern_id)
    positives = target.get("positives") or 0
    negatives = target.get("negatives") or 0
    evaluations = target.get("evaluations") or 0
    last_evaluated: str | None = target.get("last_evaluated")

    if vote == 0:
        return ReinforceResult(
            pattern_id=pattern_id,
            vote=0,
            positives=positives,
            negatives=negatives,
            evaluations=evaluations,
            last_evaluated=last_evaluated,
            was_updated=False,
        )

    # Atomic rewrite via FilesystemAdapter
    content = "\n".join(json.dumps(r) for r in records) + "\n"
    adapter = FilesystemAdapter(root=file_path.parent)
    adapter.write(Path(file_path.name), content)

    return ReinforceResult(
        pattern_id=pattern_id,
        vote=vote,
        positives=positives,
        negatives=negatives,
        evaluations=evaluations,
        last_evaluated=last_evaluated,
        was_updated=True,
    )


def append_calibration(
    memory_dir: Path,
    input_data: CalibrationInput,
    created: date | None = None,
    scope: MemoryScope = MemoryScope.PROJECT,
) -> WriteResult:
    """Append a new calibration to calibration.jsonl.

    Args:
        memory_dir: Path to memory directory (global, project, or personal).
        input_data: Calibration input data.
        created: Date created (defaults to today).
        scope: Memory scope for this calibration (affects ID generation context).

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir / "calibration.jsonl"
    cal_id = get_next_id(file_path, "CAL")
    created_date = created or date.today()

    # Calculate ratio if both estimated and actual present
    ratio: float | None = None
    if input_data.estimated_min and input_data.actual_min:
        ratio = round(input_data.estimated_min / input_data.actual_min, 1)

    entry = {
        "id": cal_id,
        "story": input_data.story,
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

    return WriteResult(
        success=True,
        id=cal_id,
        file_path=str(file_path),
        message=f"Calibration {cal_id} appended to {file_path.name} (scope: {scope.value})",
    )


def append_session(
    memory_dir: Path,
    input_data: SessionInput,
    session_date: date | None = None,
) -> WriteResult:
    """Append a new session to sessions/index.jsonl.

    Args:
        memory_dir: Path to .raise/rai/memory/ directory.
        input_data: Session input data.
        session_date: Session date (defaults to today).

    Returns:
        WriteResult with generated ID and status.
    """
    file_path = memory_dir / "sessions" / "index.jsonl"
    session_id = get_next_id(file_path, "SES")
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

    return WriteResult(
        success=True,
        id=session_id,
        file_path=str(file_path),
        message=f"Session {session_id} appended to {file_path.name}",
    )
