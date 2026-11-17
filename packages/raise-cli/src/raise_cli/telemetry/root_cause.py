"""Retroactive root-cause analysis via CC conversation logs — S11126.5 (RAISE-11211).

Given AttributionRecords from SZZ + defect_attribution, correlates introducer
commits to CC JSONL sessions via temporal/branch heuristic, extracts structured
metadata (never raw transcript), and clusters root causes by Origin x Type.

Design decisions in effect:
- D1: Temporal/branch correlation (covers pre-trailer commits)
- D2: Structured metadata only, never raw transcript
- D3: In-memory analysis, no new DB migration
- D4: Reuse JSONL parsing from cost_report
- D5: Reuse CrossCell pattern from quality/models.py
- D6: Heuristic condition taxonomy, not LLM-based

Usage:
    from raise_cli.telemetry.root_cause import (
        analyze_root_causes, cluster_root_causes,
    )
    from raise_cli.telemetry.defect_attribution import get_attribution_dataset

    records = get_attribution_dataset(project_root=Path("."))
    root_causes = analyze_root_causes(records, claude_projects_dir=...)
    clustering = cluster_root_causes(root_causes)
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Reuse the skill injection regex from cost_report (D4)
_SKILL_INJECTION_RE = re.compile(
    r"\ABase directory for this skill: \S*?/([a-z0-9-]+)\s"
)

# Gate check pattern in Bash tool_use
_GATE_CHECK_RE = re.compile(r"rai gate check")

# Edit/Write tool names that count as code modifications
_EDIT_TOOLS = frozenset({"Edit", "Write"})

# Design-phase skills (D6)
_DESIGN_PHASE_SKILLS = frozenset(
    {
        "rai-story-design",
        "rai-epic-design",
        "rai-epic-ux-design",
        "rai-problem-shape",
    }
)

# Minimum edits to trigger repeated_edit_rework
_REWORK_EDIT_THRESHOLD = 3

# Minimum gate failures to trigger gate_failure_cascade
_GATE_FAIL_THRESHOLD = 2

# Confidence degradation for unavailable conversations
_UNAVAILABLE_CONFIDENCE = 0.3

# Temporal tolerance (hours)
_TEMPORAL_TOLERANCE_HOURS = 2


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class SessionCorrelation(BaseModel):
    """Result of correlating a commit to a CC JSONL session."""

    jsonl_path: Path
    """Path to the matched JSONL file."""

    match_method: str
    """How the match was found: 'trailer' or 'temporal'."""

    confidence: float = Field(ge=0.0, le=1.0)
    """Confidence in the match (trailer=0.9, temporal=0.7)."""


class SessionMetadata(BaseModel):
    """Structured metadata extracted from a CC JSONL session.

    Contains only counters and labels -- never raw conversation content (D2).
    """

    active_skill: str | None = None
    """Dominant skill active during the session (from injection marker)."""

    edit_count: int = 0
    """Number of Edit/Write tool_use blocks."""

    gate_fail_count: int = 0
    """Number of gate check failures detected."""

    file_spread: int = 0
    """Number of distinct files edited."""

    phase: str | None = None
    """Pipeline phase (from work signal emit patterns)."""

    tool_velocity: float = 0.0
    """Tool uses per minute (0.0 if duration is zero)."""


class RootCause(BaseModel):
    """A single root-cause attribution for an introducer commit."""

    bug_key: str
    """Jira/tracker key for the fix."""

    introducer_commit: str
    """SHA of the introducer commit."""

    condition: str
    """Root-cause condition label (heuristic taxonomy D6)."""

    evidence: list[str]
    """Human-readable evidence strings (structured, never raw transcript)."""

    confidence: float = Field(ge=0.0, le=1.0)
    """Confidence in the root-cause attribution."""

    origin: str | None = None
    """Bug Origin from Jira taxonomy (None if uncategorized)."""

    bug_type: str | None = None
    """Bug Type from Jira taxonomy (None if uncategorized)."""


class RootCauseCell(BaseModel):
    """One Origin x Type cell in the root-cause clustering."""

    origin: str
    bug_type: str
    count: int = 0
    dominant_condition: str = ""
    root_causes: list[RootCause] = Field(default_factory=list)


class RootCauseClustering(BaseModel):
    """Aggregated root-cause clustering by Origin x Type."""

    total: int = 0
    categorized: int = 0
    uncategorized: int = 0
    cells: list[RootCauseCell] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------


def _parse_ts(raw: str | None) -> datetime | None:
    """Parse an ISO timestamp string to a tz-aware datetime, or None."""
    if not isinstance(raw, str) or not raw:
        return None
    try:
        ts = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return ts.replace(tzinfo=UTC) if ts.tzinfo is None else ts


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield parsed JSON objects from a JSONL file, skipping bad lines."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            obj = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            yield obj


def _message_texts(obj: dict[str, Any]) -> list[str]:
    """Extract text strings from a user or assistant message."""
    message = obj.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    return [
        b.get("text", "")
        for b in content
        if isinstance(b, dict)
        and b.get("type") == "text"
        and isinstance(b.get("text"), str)
    ]


def _tool_uses(obj: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Extract (tool_name, input) pairs from an assistant message."""
    message = obj.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    result: list[tuple[str, dict[str, Any]]] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            name = block.get("name", "")
            inp = block.get("input", {})
            if isinstance(name, str) and isinstance(inp, dict):
                result.append((name, inp))
    return result


def _tool_results(obj: dict[str, Any]) -> list[str]:
    """Extract tool_result content strings from a user message."""
    message = obj.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    return [
        b.get("content", "")
        for b in content
        if isinstance(b, dict)
        and b.get("type") == "tool_result"
        and isinstance(b.get("content"), str)
    ]


# ---------------------------------------------------------------------------
# Session correlation (D1)
# ---------------------------------------------------------------------------


def _get_session_time_range(jsonl_path: Path) -> tuple[datetime, datetime] | None:
    """Extract the first and last timestamps from a JSONL file."""
    earliest: datetime | None = None
    latest: datetime | None = None

    for obj in _iter_jsonl(jsonl_path):
        ts = _parse_ts(obj.get("timestamp"))
        if ts is None:
            continue
        if earliest is None or ts < earliest:
            earliest = ts
        if latest is None or ts > latest:
            latest = ts

    if earliest is not None and latest is not None:
        return earliest, latest
    return None


def _collect_search_dirs(
    claude_projects_dir: Path,
    cc_archive_dir: Path | None,
) -> list[Path]:
    """Collect existing search directories."""
    dirs: list[Path] = []
    if claude_projects_dir.exists():
        dirs.append(claude_projects_dir)
    if cc_archive_dir is not None and cc_archive_dir.exists():
        dirs.append(cc_archive_dir)
    return dirs


def _find_by_trailer(
    session_id: str, search_dirs: list[Path]
) -> SessionCorrelation | None:
    """Fast-path: find JSONL by filename matching session_id."""
    for search_dir in search_dirs:
        for jsonl_path in search_dir.rglob("*.jsonl"):
            if jsonl_path.stem == session_id:
                return SessionCorrelation(
                    jsonl_path=jsonl_path,
                    match_method="trailer",
                    confidence=0.9,
                )
    return None


def _find_by_temporal(
    commit_date: datetime, search_dirs: list[Path]
) -> SessionCorrelation | None:
    """Temporal correlation: find JSONL whose time range spans commit_date."""
    best: SessionCorrelation | None = None
    best_distance = float("inf")
    tolerance = _TEMPORAL_TOLERANCE_HOURS * 3600

    for search_dir in search_dirs:
        for jsonl_path in search_dir.rglob("*.jsonl"):
            time_range = _get_session_time_range(jsonl_path)
            if time_range is None:
                continue
            earliest, latest = time_range
            commit_ts = commit_date.timestamp()
            if (
                (earliest.timestamp() - tolerance)
                <= commit_ts
                <= (latest.timestamp() + tolerance)
            ):
                center = (earliest.timestamp() + latest.timestamp()) / 2
                distance = abs(commit_ts - center)
                if distance < best_distance:
                    best_distance = distance
                    best = SessionCorrelation(
                        jsonl_path=jsonl_path,
                        match_method="temporal",
                        confidence=0.7,
                    )
    return best


def correlate_session(
    *,
    commit_sha: str,  # noqa: ARG001 — reserved for logging/tracing
    commit_date: datetime,
    session_id: str | None,
    claude_projects_dir: Path,
    cc_archive_dir: Path | None = None,
) -> SessionCorrelation | None:
    """Correlate an introducer commit to a CC JSONL session.

    Resolution order:
    1. Fast-path: if session_id provided, search by filename match (trailer-based)
    2. Temporal: scan all JSONL files for timestamp overlap with commit_date

    Args:
        commit_sha: SHA of the introducer commit (reserved for logging).
        commit_date: Timestamp of the introducer commit.
        session_id: Claude-Session UUID from trailer, or None.
        claude_projects_dir: Path to ~/.claude/projects/ (or test override).
        cc_archive_dir: Path to ~/.rai/cc-archive/ (or None to skip).

    Returns:
        SessionCorrelation if a match is found, None otherwise.
    """
    search_dirs = _collect_search_dirs(claude_projects_dir, cc_archive_dir)
    if not search_dirs:
        return None

    # Fast-path: trailer-based filename match (D1)
    if session_id:
        result = _find_by_trailer(session_id, search_dirs)
        if result is not None:
            return result

    return _find_by_temporal(commit_date, search_dirs)


# ---------------------------------------------------------------------------
# Metadata extraction (D2)
# ---------------------------------------------------------------------------


class _MetadataAccumulator:
    """Stateful accumulator for session metadata extraction.

    Broken out of extract_session_metadata to reduce cyclomatic complexity.
    """

    def __init__(self) -> None:
        self.active_skill: str | None = None
        self.edit_count: int = 0
        self.gate_fail_count: int = 0
        self.edited_files: set[str] = set()
        self.phase: str | None = None
        self.tool_use_count: int = 0
        self.first_ts: datetime | None = None
        self.last_ts: datetime | None = None
        self.pending_gate_check: bool = False

    def track_timestamp(self, obj: dict[str, Any]) -> None:
        """Update first/last timestamps from a JSONL record."""
        ts = _parse_ts(obj.get("timestamp"))
        if ts is None:
            return
        if self.first_ts is None or ts < self.first_ts:
            self.first_ts = ts
        if self.last_ts is None or ts > self.last_ts:
            self.last_ts = ts

    def process_user_record(self, obj: dict[str, Any]) -> None:
        """Process a user-type JSONL record."""
        # Check skill injection
        for text in _message_texts(obj):
            m = _SKILL_INJECTION_RE.match(text)
            if m:
                self.active_skill = m.group(1)
            # Check phase signals
            if "emit-work" in text:
                phase_match = re.search(r"--phase\s+(\S+)", text)
                if phase_match:
                    self.phase = phase_match.group(1)

        # Check tool_result for gate failures
        for result_text in _tool_results(obj):
            if self.pending_gate_check and "FAILED" in result_text.upper():
                self.gate_fail_count += 1
            self.pending_gate_check = False

    def process_assistant_record(self, obj: dict[str, Any]) -> None:
        """Process an assistant-type JSONL record."""
        for tool_name, tool_input in _tool_uses(obj):
            self.tool_use_count += 1

            if tool_name in _EDIT_TOOLS:
                self.edit_count += 1
                file_path = tool_input.get("file_path", "")
                if isinstance(file_path, str) and file_path:
                    self.edited_files.add(file_path)

            if tool_name == "Bash":
                cmd = tool_input.get("command", "")
                if isinstance(cmd, str) and _GATE_CHECK_RE.search(cmd):
                    self.pending_gate_check = True

    def build(self) -> SessionMetadata:
        """Build the final SessionMetadata."""
        tool_velocity = 0.0
        if self.first_ts is not None and self.last_ts is not None:
            duration_minutes = (self.last_ts - self.first_ts).total_seconds() / 60
            if duration_minutes > 0:
                tool_velocity = self.tool_use_count / duration_minutes

        return SessionMetadata(
            active_skill=self.active_skill,
            edit_count=self.edit_count,
            gate_fail_count=self.gate_fail_count,
            file_spread=len(self.edited_files),
            phase=self.phase,
            tool_velocity=round(tool_velocity, 2),
        )


def extract_session_metadata(jsonl_path: Path) -> SessionMetadata:
    """Extract structured metadata from a CC JSONL session.

    Privacy boundary (D2): extracts only counters and labels, never raw text.

    Args:
        jsonl_path: Path to the JSONL file to analyse.

    Returns:
        SessionMetadata with structured counters.
    """
    acc = _MetadataAccumulator()

    for obj in _iter_jsonl(jsonl_path):
        acc.track_timestamp(obj)
        record_type = obj.get("type")
        if record_type == "user":
            acc.process_user_record(obj)
        elif record_type == "assistant":
            acc.process_assistant_record(obj)

    return acc.build()


# ---------------------------------------------------------------------------
# Root-cause analysis (D6)
# ---------------------------------------------------------------------------


def _classify_no_trailer(
    authoring_condition: str, confidence: float
) -> tuple[str, list[str], float]:
    """Clasificar un commit sin trailer resoluble (RAISE-11898).

    raise-commons es 100%-IA — 'ai_unknown' es IA con condición irrecuperable,
    NO humano. Se conserva 'human' por si existiera evidencia POSITIVA de autoría
    humana (no instrumentada hoy) — nunca se produce por defecto.
    """
    if authoring_condition == "human":
        return (
            "human_commit_no_session",
            ["no Claude-Session trailer -- human-authored commit"],
            confidence,
        )
    return (
        "ai_pre_trailer_no_session",
        [
            "no Claude-Session trailer -- código IA anterior a la "
            "instrumentación del trailer (repo 100%-IA)"
        ],
        confidence,
    )


def _classify_condition(
    record: object,  # AttributionRecord — imported conditionally
    meta: SessionMetadata | None,
    correlation: SessionCorrelation | None,
) -> tuple[str, list[str], float]:
    """Classify the root-cause condition from attribution + session metadata.

    Returns (condition, evidence, confidence).
    """
    # Lazy import to break circular dependency
    from raise_cli.telemetry.defect_attribution import AttributionRecord

    rec: AttributionRecord = record  # type: ignore[assignment]

    # Path 1: commit sin trailer resoluble → helper (RAISE-11898).
    if rec.authoring_condition in ("ai_unknown", "human"):
        return _classify_no_trailer(rec.authoring_condition, rec.confidence)

    # Path 2: Conversation unavailable
    if correlation is None or meta is None:
        return (
            "conversation_unavailable",
            [f"no JSONL session found for introducer {rec.introducer_commit[:7]}"],
            min(rec.confidence, _UNAVAILABLE_CONFIDENCE),
        )

    evidence: list[str] = []
    confidence = rec.confidence * correlation.confidence

    # Path 3: Repeated edit rework
    if meta.edit_count > _REWORK_EDIT_THRESHOLD:
        evidence.append(f"{meta.edit_count} edits across {meta.file_spread} files")
        if meta.active_skill:
            evidence.append(f"skill active: {meta.active_skill}")
        return "repeated_edit_rework", evidence, confidence

    # Path 4: Gate failure cascade
    if meta.gate_fail_count >= _GATE_FAIL_THRESHOLD:
        evidence.append(f"{meta.gate_fail_count} gate failures in session")
        if meta.active_skill:
            evidence.append(f"skill active: {meta.active_skill}")
        return "gate_failure_cascade", evidence, confidence

    # Path 5: Design-phase defect
    if meta.active_skill and meta.active_skill in _DESIGN_PHASE_SKILLS:
        evidence.append(f"defect introduced during design skill: {meta.active_skill}")
        return "design_phase_defect", evidence, confidence

    # Path 6: Implementation rush
    if meta.tool_velocity > 2.0 and meta.gate_fail_count == 0 and meta.edit_count > 0:
        evidence.append(
            f"high tool velocity ({meta.tool_velocity:.1f}/min) with no gate checks"
        )
        return "implementation_rush", evidence, confidence

    # Path 7: Generic
    evidence.append("session correlated but no dominant pattern detected")
    if meta.active_skill:
        evidence.append(f"skill active: {meta.active_skill}")
    return "unclassified", evidence, confidence


def analyze_root_causes(
    records: list[object],  # list[AttributionRecord]
    *,
    claude_projects_dir: Path,
    cc_archive_dir: Path | None = None,
    commit_dates: dict[str, datetime] | None = None,
) -> list[RootCause]:
    """Analyse AttributionRecords and produce root-cause attributions.

    Args:
        records: List of AttributionRecord from defect_attribution.
        claude_projects_dir: Path to ~/.claude/projects/ (or test override).
        cc_archive_dir: Path to ~/.rai/cc-archive/ (or None to skip).
        commit_dates: Override commit dates for testing (maps commit SHA to datetime).
            When None, uses the record's resolved_at as proxy.

    Returns:
        List of RootCause records with condition labels and evidence.
    """
    from raise_cli.telemetry.defect_attribution import AttributionRecord

    result: list[RootCause] = []

    for raw_record in records:
        record: AttributionRecord = raw_record  # type: ignore[assignment]

        # Determine commit date
        commit_date = record.resolved_at
        if commit_dates and record.introducer_commit in commit_dates:
            commit_date = commit_dates[record.introducer_commit]

        # Correlate to session
        correlation = correlate_session(
            commit_sha=record.introducer_commit,
            commit_date=commit_date,
            session_id=record.introducer_session_id,
            claude_projects_dir=claude_projects_dir,
            cc_archive_dir=cc_archive_dir,
        )

        # Extract metadata if session found
        meta: SessionMetadata | None = None
        if correlation is not None:
            meta = extract_session_metadata(correlation.jsonl_path)

        # Classify condition
        condition, evidence, confidence = _classify_condition(record, meta, correlation)

        result.append(
            RootCause(
                bug_key=record.bug_key,
                introducer_commit=record.introducer_commit,
                condition=condition,
                evidence=evidence,
                confidence=round(confidence, 3),
            )
        )

    return result


# ---------------------------------------------------------------------------
# Clustering (D5)
# ---------------------------------------------------------------------------


def cluster_root_causes(
    root_causes: list[RootCause],
) -> RootCauseClustering:
    """Cluster root causes into an Origin x Type matrix.

    Root causes without origin or bug_type are counted as uncategorized.

    Args:
        root_causes: List of RootCause records (with optional origin/bug_type).

    Returns:
        RootCauseClustering with cells and dominant_condition per cell.
    """
    if not root_causes:
        return RootCauseClustering()

    total = len(root_causes)
    categorized_causes: list[RootCause] = []
    uncategorized = 0

    for rc in root_causes:
        if rc.origin is not None and rc.bug_type is not None:
            categorized_causes.append(rc)
        else:
            uncategorized += 1

    # Group by (origin, bug_type) — only categorized entries reach here
    groups: dict[tuple[str, str], list[RootCause]] = {}
    for rc in categorized_causes:
        key = (rc.origin or "", rc.bug_type or "")  # guaranteed non-None above
        groups.setdefault(key, []).append(rc)

    # Build cells with dominant condition
    cells: list[RootCauseCell] = []
    for (origin, bug_type), group in sorted(
        groups.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        condition_counts: Counter[str] = Counter(rc.condition for rc in group)
        dominant = condition_counts.most_common(1)[0][0] if condition_counts else ""

        cells.append(
            RootCauseCell(
                origin=origin,
                bug_type=bug_type,
                count=len(group),
                dominant_condition=dominant,
                root_causes=group,
            )
        )

    return RootCauseClustering(
        total=total,
        categorized=len(categorized_causes),
        uncategorized=uncategorized,
        cells=cells,
    )
