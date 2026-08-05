"""Writer module for appending memory entries to JSONL files.

This module provides functions to append new patterns, calibrations,
and sessions to the memory JSONL files, with auto-ID generation
and cache invalidation.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter
from raise_cli.config.paths import get_global_rai_dir, get_memory_dir, get_personal_dir
from raise_cli.memory.models import MemoryScope, PatternSubType

logger = logging.getLogger(__name__)

# mtime-based cache for get_next_id() — avoids re-scanning unchanged files
_id_cache: dict[str, tuple[float, int]] = {}  # cache_key → (mtime, max_num)


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
    mission_id: str | None = Field(
        default=None, description="Active mission ID when pattern was created"
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


def _scan_max_id(file_path: Path, full_prefix: str) -> int:
    """Scan a JSONL file and sibling directories for the max numeric ID."""
    max_num = 0

    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as f:
            for raw_line in f:
                stripped = raw_line.strip()
                if not stripped:
                    continue
                try:
                    data = json.loads(stripped)
                    entry_id = data.get("id", "")
                    if entry_id.startswith(full_prefix):
                        num = int(entry_id[len(full_prefix) :])
                        max_num = max(max_num, num)
                except ValueError:
                    continue

    parent = file_path.parent
    if parent.is_dir():
        dir_pattern = re.compile(rf"^{re.escape(full_prefix)}(\d+)$")
        for entry in parent.iterdir():
            if entry.is_dir():
                m = dir_pattern.match(entry.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))

    return max_num


def get_next_id(
    file_path: Path, prefix: str, developer_prefix: str | None = None
) -> str:
    """Get next available ID for a JSONL file.

    Uses an mtime-based cache to avoid re-scanning unchanged files.

    Args:
        file_path: Path to JSONL file.
        prefix: ID prefix (e.g., 'PAT', 'CAL', 'SES').
        developer_prefix: Optional developer prefix for multi-dev safety.

    Returns:
        Next ID. With developer_prefix='E': 'PAT-E-001'.
        Without: 'PAT-001' (backward compatible).
    """
    full_prefix = f"{prefix}-{developer_prefix}-" if developer_prefix else f"{prefix}-"
    cache_key = f"{file_path}::{full_prefix}"

    current_mtime = file_path.stat().st_mtime if file_path.exists() else 0.0
    cached = _id_cache.get(cache_key)
    if cached and cached[0] == current_mtime:
        max_num = cached[1]
    else:
        max_num = _scan_max_id(file_path, full_prefix)
        _id_cache[cache_key] = (current_mtime, max_num)

    # Bump cache so next call within same process sees incremented value
    _id_cache[cache_key] = (current_mtime, max_num + 1)

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


def derive_project_root(memory_dir: Path) -> Path:
    """Derive project root from a memory directory path."""
    resolved = memory_dir.resolve()
    for parent in [resolved] + list(resolved.parents):
        if (parent / ".raise").is_dir() or (parent / ".git").is_dir():
            return parent
    return Path.cwd()


_derive_project_root = derive_project_root


def append_pattern(
    memory_dir: Path,
    input_data: PatternInput,
    created: date | None = None,
    scope: MemoryScope = MemoryScope.PROJECT,
    developer_prefix: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> WriteResult:
    """Append a new pattern to SQLite.

    Args:
        memory_dir: Used to derive project root for DB connection.
        input_data: Pattern input data.
        created: Date created (defaults to today).
        scope: Memory scope for this pattern.
        developer_prefix: Optional developer prefix for multi-dev safety.
        conn: Optional SQLite connection (resolved from project DB if None).

    Returns:
        WriteResult with generated ID and status.
    """
    from raise_cli.memory.patterns_backend import upsert_pattern, validate_pattern_add

    pid = ""
    if conn is None:
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        project_root = _derive_project_root(memory_dir)
        pid = get_project_id(project_root)
        conn = get_project_db(project_root)
        create_all(conn)

    normalized = validate_pattern_add(input_data.content, input_data.context)

    prefix = f"PAT-{developer_prefix}" if developer_prefix else "PAT"
    created_date = created or date.today()

    result = upsert_pattern(
        conn,
        project_id=pid,
        content=normalized,
        pattern_type=input_data.sub_type.value,
        context=input_data.context,
        learned_from=input_data.learned_from or "",
        mission_id=input_data.mission_id or "",
        scope=scope.value,
        base=1 if input_data.base else 0,
        version=input_data.version or 1,
        created_at=created_date.isoformat(),
        id_prefix=prefix,
        on_conflict="reject",
    )
    pattern_id = result.pattern_id

    return WriteResult(
        success=True,
        id=pattern_id,
        file_path="raise.db",
        message=f"Pattern {pattern_id} appended to raise.db (scope: {scope.value})",
    )


def _resolve_local_pattern_id(conn: sqlite3.Connection, pattern_id: str) -> str | None:
    """Resolve pattern_id, falling back to an original_id lookup.

    A bare server UUID has no local `pattern_id` row — it must resolve via
    the shadow row keyed by `original_id` (RAISE-11074, mirrors the MCP-side
    `_resolve_local_pattern_id` in mcp_tools_pattern.py).

    The original_id fallback only applies when pattern_id is UUID-shaped:
    `original_id` defaults to `''` for every unlinked local pattern, so an
    unguarded `WHERE original_id = ?` would match an arbitrary unlinked row
    for any other non-matching input (e.g. an empty string or typo).
    """
    row = conn.execute(
        "SELECT pattern_id FROM patterns WHERE pattern_id = ?", (pattern_id,)
    ).fetchone()
    if row is not None:
        return row[0]
    try:
        uuid.UUID(pattern_id)
    except ValueError:
        return None
    row = conn.execute(
        "SELECT pattern_id FROM patterns WHERE original_id = ?", (pattern_id,)
    ).fetchone()
    return row[0] if row is not None else None


def reinforce_pattern(
    file_path: Path,  # noqa: ARG001 — kept for API compat, SQLite resolves internally
    pattern_id: str,
    vote: int,
    story_id: str | None = None,  # noqa: ARG001
    conn: sqlite3.Connection | None = None,
) -> ReinforceResult:
    """Update reinforcement counters for a pattern in SQLite.

    Vote semantics:
        +1 = implementation followed the pattern (positives + evaluations++)
        -1 = implementation contradicted the pattern (negatives + evaluations++)
         0 = not relevant to this story (N/A — no update)

    A bare server UUID resolves via original_id; on miss, and only when
    server credentials are configured, a pull is attempted once before
    retrying (RAISE-11074). After a non-zero vote, the pattern is enqueued
    for push (best-effort — a push failure never blocks the result).

    Args:
        file_path: Ignored (kept for API compat). SQLite resolves internally.
        pattern_id: ID of the pattern to reinforce (e.g., 'PAT-E-183') or a
            bare server UUID.
        vote: +1, 0, or -1.
        story_id: Optional story ID for traceability.
        conn: Optional SQLite connection (resolved from project DB if None).

    Returns:
        ReinforceResult with updated counts.

    Raises:
        KeyError: If pattern_id is not found (distinct message when a
            server pull was attempted and still missed, per PAT-E-9272).
    """
    if conn is None:
        from raise_cli.storage.connection import get_project_db
        from raise_cli.storage.schema import create_all

        conn = get_project_db(Path.cwd())
        create_all(conn)

    local_pattern_id = _resolve_local_pattern_id(conn, pattern_id)
    if local_pattern_id is None:
        from raise_cli.config.server import get_server_credentials

        creds = get_server_credentials()
        if creds is not None:
            from raise_cli.memory.sync import pull_patterns
            from raise_cli.storage.connection import get_project_id

            pull_patterns(conn, project_id=get_project_id(Path.cwd()))
            local_pattern_id = _resolve_local_pattern_id(conn, pattern_id)
        if local_pattern_id is None:
            if creds is not None:
                raise KeyError(f"Pattern '{pattern_id}' not found after server pull")
            raise KeyError(f"Pattern '{pattern_id}' not found")

    row = conn.execute(
        "SELECT positives, negatives, evaluations, last_evaluated FROM patterns WHERE pattern_id = ?",
        (local_pattern_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"Pattern '{pattern_id}' not found")

    if vote == 0:
        return ReinforceResult(
            pattern_id=local_pattern_id,
            vote=0,
            positives=row[0],
            negatives=row[1],
            evaluations=row[2],
            last_evaluated=row[3],
            was_updated=False,
        )

    # last_evaluated is a human-facing date; updated_at must be a full ISO
    # instant — a date-only value floors client_updated_at to midnight and
    # can lose an LWW race against a same-day server row (RAISE-11074 Q1).
    today = date.today().isoformat()
    now = datetime.now(UTC).isoformat()
    pos_delta = 1 if vote == 1 else 0
    neg_delta = 1 if vote == -1 else 0
    conn.execute(
        "UPDATE patterns SET "
        "positives = positives + ?, negatives = negatives + ?, "
        "evaluations = evaluations + 1, last_evaluated = ?, updated_at = ? "
        "WHERE pattern_id = ?",
        (pos_delta, neg_delta, today, now, local_pattern_id),
    )
    conn.commit()

    updated = conn.execute(
        "SELECT positives, negatives, evaluations, last_evaluated FROM patterns WHERE pattern_id = ?",
        (local_pattern_id,),
    ).fetchone()

    try:
        from raise_cli.memory.sync import attempt_immediate_push, enqueue_push

        enqueue_push(conn, local_pattern_id)
        attempt_immediate_push(conn, local_pattern_id)
    except Exception:  # noqa: BLE001 — push failure must never block reinforce
        logger.debug(
            "Pattern push failed after reinforce (queued for retry): %s",
            local_pattern_id,
            exc_info=True,
        )

    return ReinforceResult(
        pattern_id=local_pattern_id,
        vote=vote,
        positives=updated[0],
        negatives=updated[1],
        evaluations=updated[2],
        last_evaluated=updated[3],
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
