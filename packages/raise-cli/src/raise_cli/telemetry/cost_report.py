"""Cost-per-task harness over CC session JSONL logs — S7884.1 (E7884 K0).

Parses ``~/.claude/projects/*/*.jsonl`` and produces API-equivalent cost
reports per model. Read-only and offline: the projects directory is
injectable and no network calls are made.

Dedupe contract: streaming repeats share ``(message.id, requestId)`` and
must count once. Records with ``model == "<synthetic>"`` or ``isMeta`` are
excluded — they carry no billable usage.

Known limitation (AR S7884.1): skill attribution depends on observed CC log
formats (skill-body injection marker, Skill tool_use shape). If CC changes
those formats, attribution degrades silently to ``(sin-skill)`` — totals per
model remain correct. Validate attribution against a known period after CC
upgrades.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, computed_field

logger = logging.getLogger(__name__)

SYNTHETIC_MODEL = "<synthetic>"

# Regex to extract subagent token counts embedded in tool_result content blocks.
# CC logs Agent() subagent usage as:
#   <usage>subagent_tokens: N\ntool_uses: M\nduration_ms: D</usage>
SUBAGENT_TOKENS_RE = re.compile(r"subagent_tokens:\s*(\d+)")

SIN_SKILL = "(sin-skill)"

SIN_FASE = "(sin-fase)"

# Slash-command invocations leave no Skill tool_use — only this injection
# marker in a user record. Both forms MUST be detected (AC2). Anchored at the
# start of the text: compaction summaries quote the marker mid-text and must
# not count as runs.
SKILL_INJECTION_RE = re.compile(r"\ABase directory for this skill: \S*?/([a-z0-9-]+)\s")

# Superset of session_tokens._SIGNAL_RE: also captures work_type and work_id
# (needed for the cost-per-story headline).
WORK_SIGNAL_RE = re.compile(
    r"rai signal emit-work\s+(\w+)\s+(\S+)\s+--event\s+(\w+)\s+--phase\s+(\w[\w-]*)"
)

# Lean waste taxonomy (auditoría 2026-06-10). Unmapped skills -> "otros".
LEAN_CATEGORIES: dict[str, str] = {
    "rai-session-start": "ceremonia",
    "rai-session-close": "ceremonia",
    "rai-session-journal": "ceremonia",
    "rai-story-start": "ceremonia",
    "rai-story-close": "ceremonia",
    "rai-epic-start": "ceremonia",
    "rai-epic-close": "ceremonia",
    "rai-epic-journal": "ceremonia",
    "rai-bugfix-triage": "ceremonia",
    "rai-worktree-open": "ceremonia",
    "rai-worktree-close": "ceremonia",
    "rai-story-design": "produccion",
    "rai-story-plan": "produccion",
    "rai-story-implement": "produccion",
    "rai-epic-design": "produccion",
    "rai-epic-plan": "produccion",
    "rai-epic-ux-design": "produccion",
    "rai-bugfix-analyse": "produccion",
    "rai-bugfix-plan": "produccion",
    "rai-bugfix-fix": "produccion",
    "rai-problem-shape": "produccion",
    "rai-research": "produccion",
    "rai-architecture-review": "verificacion",
    "rai-quality-review": "verificacion",
    "rai-story-review": "verificacion",
    "rai-bugfix-review": "verificacion",
    "rai-bugfix-pir": "verificacion",
    "rai-mr-create": "verificacion",
    SIN_SKILL: "conversacion",
}


def lean_category(skill: str) -> str:
    """Lean taxonomy bucket for a skill (unmapped -> 'otros')."""
    return LEAN_CATEGORIES.get(skill, "otros")


# Default pricing fallback for unknown model families.
_FALLBACK_PRICE_KEY = "sonnet"


class ModelPricing(BaseModel):
    """USD per MTok for each billing component."""

    input: float
    output: float
    cache_write: float
    cache_read: float


# USD per MTok (cache write 1.25x input, cache read 0.1x input).
PRICING: dict[str, ModelPricing] = {
    "fable": ModelPricing(input=10.0, output=50.0, cache_write=12.5, cache_read=1.0),
    "opus": ModelPricing(input=5.0, output=25.0, cache_write=6.25, cache_read=0.5),
    "sonnet": ModelPricing(input=3.0, output=15.0, cache_write=3.75, cache_read=0.30),
    "haiku": ModelPricing(input=1.0, output=5.0, cache_write=1.25, cache_read=0.10),
}


def price_key(model: str) -> str:
    """Map a full model id to its pricing family (fallback: sonnet)."""
    for key in PRICING:
        if key in model:
            return key
    return _FALLBACK_PRICE_KEY


class UsageRecord(BaseModel):
    """One deduplicated assistant API call extracted from a session JSONL."""

    model: str
    project: str
    session: str
    timestamp: datetime
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write: int = 0
    cache_read: int = 0


class ModelTotals(BaseModel):
    """Aggregated usage and cost for one model."""

    model: str
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write: int = 0
    cache_read: int = 0
    cost_usd: float = 0.0


class SkillRunStats(BaseModel):
    """Aggregated runs, messages, and cost attributed to one skill."""

    skill: str
    category: str = "otros"
    runs: int = 0
    messages: int = 0
    cost_usd: float = 0.0
    models: dict[str, float] = Field(default_factory=dict)

    @computed_field  # type: ignore[misc]
    @property
    def usd_per_run(self) -> float:
        """Cost per run (0.0 when runs=0)."""
        return self.cost_usd / self.runs if self.runs > 0 else 0.0

    @computed_field  # type: ignore[misc]
    @property
    def msgs_per_run(self) -> float:
        """Messages per run (0.0 when runs=0)."""
        return self.messages / self.runs if self.runs > 0 else 0.0


class PhaseRunStats(BaseModel):
    """Aggregated messages and cost attributed to one pipeline phase."""

    phase: str
    messages: int = 0
    cost_usd: float = 0.0


class TaskRunStats(BaseModel):
    """Aggregated messages and cost for one boundary-to-boundary task window.

    A task window spans from the previous ``raise_task_complete`` boundary
    (exclusive) to this one (inclusive). The FIRST window (session start to the
    first boundary) is one-time orientation overhead, not a task — it is counted
    in ``CostReport.setup_overhead_*`` instead, so ``msgs_per_task`` reflects the
    marginal steady-state cost per task rather than warmup.
    """

    task: str  # task_name from the tool input
    work_id: str  # work_id from the tool input (correlation)
    messages: int = (
        0  # assistant turns attributed to this task (boundary turn included)
    )
    cost_usd: float = 0.0


class CostReport(BaseModel):
    """Cost report over a date range."""

    since: datetime | None = None
    until: datetime | None = None
    session_id: str | None = None
    repo_slug: str | None = None
    models: list[ModelTotals] = []
    skills: list[SkillRunStats] = []
    phases: list[PhaseRunStats] = []
    tasks: list[TaskRunStats] = []
    setup_overhead_msgs: int = 0  # one-time turns before first task boundary
    setup_overhead_cost_usd: float = 0.0
    categories: dict[str, float] = {}
    stories_completed: int = 0
    cost_per_story: float | None = None
    total_cost_usd: float = 0.0
    msgs_per_task: float | None = None
    approvals_total: int = 0
    approvals_with_edits: int = 0
    rubber_stamp_rate: float | None = None
    tool_fail_ratio: float | None = None
    edit_revert_files: int = 0
    session_duration_minutes: float | None = None
    max_gate_fail_streak: int = 0
    story_attributions: list[StoryAttribution] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def avg_cost_per_story(self) -> float | None:
        """Mean attributed cost per story (overhead and unresolved entries excluded)."""
        costs = [
            a.cost_usd
            for a in self.story_attributions
            if not a.overhead and a.cost_usd is not None
        ]
        return sum(costs) / len(costs) if costs else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def median_cost_per_story(self) -> float | None:
        """Median attributed cost per story (overhead and unresolved entries excluded)."""
        import statistics

        costs = sorted(
            a.cost_usd
            for a in self.story_attributions
            if not a.overhead and a.cost_usd is not None
        )
        return statistics.median(costs) if costs else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def p95_cost_per_story(self) -> float | None:
        """95th-percentile attributed cost per story (overhead and unresolved entries excluded)."""
        costs = sorted(
            a.cost_usd
            for a in self.story_attributions
            if not a.overhead and a.cost_usd is not None
        )
        if not costs:
            return None
        return costs[min(int(len(costs) * 0.95), len(costs) - 1)]


class Delta(BaseModel):
    """Before/after pair for one named metric."""

    name: str
    before: float = 0.0
    after: float = 0.0

    @property
    def pct(self) -> float | None:
        """Relative change vs before (None when before is zero)."""
        if self.before == 0.0:
            return None
        return (self.after - self.before) / self.before * 100.0


class ReportComparison(BaseModel):
    """Deltas between a baseline report and a current report."""

    total: Delta
    categories: list[Delta] = []
    skills: list[Delta] = []


def save_baseline(report: CostReport, path: Path) -> None:
    """Persist a report as a JSON baseline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def load_baseline(path: Path) -> CostReport:
    """Load a previously saved baseline report."""
    return CostReport.model_validate_json(path.read_text(encoding="utf-8"))


def compare_reports(baseline: CostReport, current: CostReport) -> ReportComparison:
    """Compute cost deltas (total, per lean category, per skill)."""
    categories = [
        Delta(
            name=name,
            before=baseline.categories.get(name, 0.0),
            after=current.categories.get(name, 0.0),
        )
        for name in sorted(set(baseline.categories) | set(current.categories))
    ]
    base_skills = {s.skill: s.cost_usd for s in baseline.skills}
    cur_skills = {s.skill: s.cost_usd for s in current.skills}
    skills = [
        Delta(
            name=name,
            before=base_skills.get(name, 0.0),
            after=cur_skills.get(name, 0.0),
        )
        for name in sorted(set(base_skills) | set(cur_skills))
    ]
    return ReportComparison(
        total=Delta(
            name="total", before=baseline.total_cost_usd, after=current.total_cost_usd
        ),
        categories=categories,
        skills=skills,
    )


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    """Parse a JSONL line into a dict, or None for blanks and garbage."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        obj: Any = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _billable_parts(
    raw: str,
) -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any]] | None:
    """Return (obj, message, model, usage) for a billable assistant line, else None."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        obj: Any = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or obj.get("type") != "assistant" or obj.get("isMeta"):
        return None
    message = obj.get("message")
    if not isinstance(message, dict):
        return None
    model = message.get("model")
    if not isinstance(model, str) or not model or model == SYNTHETIC_MODEL:
        return None
    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None
    return obj, message, model, usage


def _parse_record(
    raw: str,
    *,
    project: str,
    session: str,
    seen: set[tuple[str, str]],
) -> UsageRecord | None:
    parts = _billable_parts(raw)
    if parts is None:
        return None
    obj, message, model, usage = parts

    timestamp = _parse_timestamp(obj.get("timestamp"))
    if timestamp is None:
        return None

    msg_id = str(message.get("id") or "")
    request_id = str(obj.get("requestId") or "")
    dedupe_key = (msg_id, request_id)
    if msg_id and request_id:
        if dedupe_key in seen:
            return None
        seen.add(dedupe_key)

    return UsageRecord(
        model=model,
        project=project,
        session=session,
        timestamp=timestamp,
        input_tokens=_safe_int(usage.get("input_tokens")),
        output_tokens=_safe_int(usage.get("output_tokens")),
        cache_write=_safe_int(usage.get("cache_creation_input_tokens")),
        cache_read=_safe_int(usage.get("cache_read_input_tokens")),
    )


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        ts = datetime.fromisoformat(value)
    except ValueError:
        return None
    # Naive timestamps are treated as UTC: comparing naive vs aware raises
    # TypeError and one malformed line must not crash the whole report.
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts


def _safe_int(val: Any) -> int:
    return val if isinstance(val, int) else 0


def record_cost_usd(record: UsageRecord, pricing: dict[str, ModelPricing]) -> float:
    """API-equivalent USD cost of one record under the given pricing table."""
    p = pricing.get(price_key(record.model), PRICING[_FALLBACK_PRICE_KEY])
    return (
        record.input_tokens * p.input
        + record.output_tokens * p.output
        + record.cache_write * p.cache_write
        + record.cache_read * p.cache_read
    ) / 1e6


def _injected_skill(obj: dict[str, Any]) -> str | None:
    """Skill name from a user record carrying a skill-body injection."""
    if obj.get("type") != "user":
        return None
    message = obj.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    texts: list[str] = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        texts.extend(
            c.get("text", "")
            for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )
    for text in texts:
        match = SKILL_INJECTION_RE.match(text)
        if match:
            return match.group(1)
    return None


def _tool_use_events(message: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (tool_name, input) for each tool_use block in an assistant message."""
    content = message.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            name = block.get("name")
            tool_input = block.get("input")
            if isinstance(name, str) and isinstance(tool_input, dict):
                yield name, tool_input


def _signal_from_tool_use(
    name: str, tool_input: dict[str, Any]
) -> tuple[str, str, str, str] | None:
    """Extract (work_type, work_id, event, phase) from a signal tool call."""
    if name.endswith("raise_signal_emit"):
        work_type = tool_input.get("work_type")
        work_id = tool_input.get("work_id")
        event = tool_input.get("event")
        phase = tool_input.get("phase", "init")
        if (
            isinstance(work_type, str)
            and isinstance(work_id, str)
            and isinstance(event, str)
        ):
            return work_type, work_id, event, str(phase)
        return None
    command = tool_input.get("command")
    if isinstance(command, str):
        match = WORK_SIGNAL_RE.search(command)
        if match:
            return match.group(1), match.group(2), match.group(3), match.group(4)
    return None


def _task_boundary_from_tool_use(
    name: str, tool_input: dict[str, Any]
) -> tuple[str, str] | None:
    """Extract (work_id, task_name) from a raise_task_complete tool call.

    Returns None when the tool is not raise_task_complete or required fields
    are missing. Matching uses endswith so any MCP namespace prefix works.
    """
    if not name.endswith("raise_task_complete"):
        return None
    work_id = tool_input.get("work_id")
    task_name = tool_input.get("task_name")
    if isinstance(work_id, str) and isinstance(task_name, str):
        return work_id, task_name
    return None


class _SessionScanner:
    """Stateful per-session walk: attribution, signals, and billable usage."""

    def __init__(
        self,
        table: dict[str, ModelPricing],
        since: datetime | None,
        until: datetime | None,
    ) -> None:
        self.table = table
        self.since = since
        self.until = until
        self.model_totals: dict[str, ModelTotals] = {}
        self.skill_stats: dict[str, SkillRunStats] = {}
        self.phase_stats: dict[str, PhaseRunStats] = {}
        self.closed_stories: set[str] = set()
        self._current_phase: str = SIN_FASE
        self._approvals_total: int = 0
        self._approvals_with_edits: int = 0
        self._post_approve_window: int = 0
        self._post_approve_edited: bool = False
        # Skill set by a Skill tool_use whose body injection has not arrived
        # yet — the injection must not count as a second run.
        self._pending_tool_skill: str | None = None
        # Subagent tokens accumulated from tool_result user records; added to
        # the next assistant turn's output_tokens before pricing (S6456.5).
        self._pending_subagent_tokens: int = 0
        # Trajectory quality counters (S8743.1)
        self._tool_results_total: int = 0
        self._tool_results_errors: int = 0
        self._file_edit_counts: dict[str, int] = {}
        self._first_timestamp: datetime | None = None
        self._last_timestamp: datetime | None = None
        self._current_gate_streak: int = 0
        self._max_gate_streak: int = 0
        self._pending_gate_check: bool = False
        # Per-task aggregation (S8370.3/T3)
        # Turns are accumulated into _pending_task_* until a raise_task_complete
        # boundary is hit; at that point a TaskRunStats is created and the pending
        # counters are reset. This avoids needing to know the task name in advance.
        self._task_stats_ordered: list[TaskRunStats] = []
        self._pending_task_msgs: int = 0
        self._pending_task_cost: float = 0.0
        self._pending_task_boundary: tuple[str, str] | None = (
            None  # (work_id, task_name)
        )
        # The first window (start -> first boundary) is one-time orientation
        # overhead, not a task. _first_boundary_seen resets per file so each
        # session contributes its own setup window; the totals accumulate.
        self._first_boundary_seen: bool = False
        self._setup_overhead_msgs: int = 0
        self._setup_overhead_cost: float = 0.0

    def _reset_file_state(self) -> None:
        """Per-file state: pending tool-skill, phase, and approve window must not leak."""
        self._pending_tool_skill = None
        self._current_phase = SIN_FASE
        self._pending_subagent_tokens = 0
        self._close_approve_window()
        self._file_edit_counts = {}
        self._pending_gate_check = False
        self._pending_task_msgs = 0
        self._pending_task_cost = 0.0
        self._pending_task_boundary = None
        self._first_boundary_seen = False

    _POST_APPROVE_WINDOW_SIZE = 5

    def _close_approve_window(self) -> None:
        """Close the post-approve observation window if open."""
        if self._post_approve_window > 0:
            if self._post_approve_edited:
                self._approvals_with_edits += 1
            self._post_approve_window = 0
            self._post_approve_edited = False

    def _stats(self, skill: str) -> SkillRunStats:
        return self.skill_stats.setdefault(
            skill, SkillRunStats(skill=skill, category=lean_category(skill))
        )

    def _phase(self, phase: str) -> PhaseRunStats:
        return self.phase_stats.setdefault(phase, PhaseRunStats(phase=phase))

    def flush_approve_window(self) -> None:
        """Close any open post-approve observation window (end of scan)."""
        self._close_approve_window()

    @property
    def tool_fail_ratio(self) -> float | None:
        if self._tool_results_total == 0:
            return None
        return self._tool_results_errors / self._tool_results_total

    @property
    def edit_revert_files(self) -> int:
        return sum(1 for count in self._file_edit_counts.values() if count > 1)

    @property
    def session_duration_minutes(self) -> float | None:
        if self._first_timestamp is None or self._last_timestamp is None:
            return None
        delta = (self._last_timestamp - self._first_timestamp).total_seconds()
        if delta == 0.0:
            return None
        return delta / 60.0

    @property
    def max_gate_fail_streak(self) -> int:
        return self._max_gate_streak

    @property
    def task_stats(self) -> list[TaskRunStats]:
        """Ordered list of completed task buckets (insertion order)."""
        return self._task_stats_ordered

    @property
    def setup_overhead(self) -> tuple[int, float]:
        """One-time orientation overhead (msgs, cost) before first task boundary."""
        return self._setup_overhead_msgs, self._setup_overhead_cost

    @property
    def approvals_total(self) -> int:
        return self._approvals_total

    @property
    def approvals_with_edits(self) -> int:
        return self._approvals_with_edits

    def _update_timestamp(self, ts: datetime) -> None:
        """Track first/last timestamps across all record types."""
        if self._first_timestamp is None or ts < self._first_timestamp:
            self._first_timestamp = ts
        if self._last_timestamp is None or ts > self._last_timestamp:
            self._last_timestamp = ts

    def _process_tool_results(self, content: list[Any]) -> None:
        """Count tool_result blocks (total and errors) in user record content."""
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            self._tool_results_total += 1
            if block.get("is_error"):
                self._tool_results_errors += 1
            if self._pending_gate_check:
                content_str = str(block.get("content", ""))
                if "passed" in content_str.lower():
                    self._current_gate_streak = 0
                else:
                    self._current_gate_streak += 1
                    self._max_gate_streak = max(
                        self._max_gate_streak, self._current_gate_streak
                    )
                self._pending_gate_check = False

    def _process_user_record(self, obj: dict[str, Any]) -> None:
        """Extract tool_result signals from a user-type record."""
        message = obj.get("message")
        if not isinstance(message, dict):
            return
        content = message.get("content")
        if not isinstance(content, list):
            return
        self._process_tool_results(content)
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            text = block.get("content")
            if isinstance(text, str):
                for m in SUBAGENT_TOKENS_RE.finditer(text):
                    self._pending_subagent_tokens += int(m.group(1))

    def scan_file(self, jsonl_path: Path, seen: set[tuple[str, str]]) -> None:
        project = jsonl_path.parent.name
        session = jsonl_path.stem
        try:
            lines = jsonl_path.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
        except OSError:
            return
        current_skill = SIN_SKILL
        self._reset_file_state()
        for raw in lines:
            obj = _parse_json_object(raw)
            if obj is None:
                continue

            ts = _parse_timestamp(obj.get("timestamp"))
            if ts is not None:
                self._update_timestamp(ts)

            injected = _injected_skill(obj)
            if injected is not None:
                current_skill = injected
                in_range = ts is not None and self._in_range(ts)
                if in_range and injected != self._pending_tool_skill:
                    self._stats(current_skill).runs += 1
                self._pending_tool_skill = None
                continue

            if obj.get("type") == "user":
                self._process_user_record(obj)

            record = _parse_record(raw, project=project, session=session, seen=seen)
            if record is None or not self._in_range(record.timestamp):
                continue

            message = obj.get("message")
            if isinstance(message, dict):
                current_skill = self._process_tool_uses(message, current_skill)

            self._accumulate(record, current_skill)

    def _in_range(self, timestamp: datetime) -> bool:
        if self.since is not None and timestamp < self.since:
            return False
        return self.until is None or timestamp < self.until

    def _process_tool_uses(self, message: dict[str, Any], current_skill: str) -> str:
        for name, tool_input in _tool_use_events(message):
            if name == "Skill":
                skill = tool_input.get("skill")
                if isinstance(skill, str) and skill:
                    current_skill = skill
                    self._stats(current_skill).runs += 1
                    self._pending_tool_skill = skill
                continue
            if name in ("Edit", "Write"):
                if self._post_approve_window > 0:
                    self._post_approve_edited = True
                file_path = tool_input.get("file_path")
                if isinstance(file_path, str) and file_path:
                    self._file_edit_counts[file_path] = (
                        self._file_edit_counts.get(file_path, 0) + 1
                    )
            if name == "Bash":
                cmd = tool_input.get("command")
                if isinstance(cmd, str) and "rai gate check" in cmd:
                    self._pending_gate_check = True
            if name.endswith("pipeline_advance") and tool_input.get("approve") is True:
                self._record_approval()
            self._process_signal(name, tool_input)
            self._check_task_boundary(name, tool_input)
        return current_skill

    def _check_task_boundary(self, name: str, tool_input: dict[str, Any]) -> None:
        """Record a pending task boundary when raise_task_complete is detected."""
        boundary = _task_boundary_from_tool_use(name, tool_input)
        if boundary is not None:
            self._pending_task_boundary = boundary

    def _record_approval(self) -> None:
        self._close_approve_window()
        self._approvals_total += 1
        self._post_approve_window = self._POST_APPROVE_WINDOW_SIZE
        self._post_approve_edited = False

    def _process_signal(self, name: str, tool_input: dict[str, Any]) -> None:
        signal = _signal_from_tool_use(name, tool_input)
        if signal is not None:
            work_type, work_id, event, phase = signal
            if event == "start":
                self._current_phase = phase
            if work_type == "story" and event == "complete" and phase == "close":
                self.closed_stories.add(work_id)

    def _accumulate(self, record: UsageRecord, current_skill: str) -> None:
        # Consume any subagent tokens accumulated from preceding tool_result records.
        if self._pending_subagent_tokens:
            record = record.model_copy(
                update={
                    "output_tokens": record.output_tokens
                    + self._pending_subagent_tokens
                }
            )
            self._pending_subagent_tokens = 0
        m = self.model_totals.setdefault(record.model, ModelTotals(model=record.model))
        cost = record_cost_usd(record, self.table)
        m.calls += 1
        m.input_tokens += record.input_tokens
        m.output_tokens += record.output_tokens
        m.cache_write += record.cache_write
        m.cache_read += record.cache_read
        m.cost_usd += cost

        s = self._stats(current_skill)
        s.messages += 1
        s.cost_usd += cost
        s.models[record.model] = s.models.get(record.model, 0.0) + cost

        p = self._phase(self._current_phase)
        p.messages += 1
        p.cost_usd += cost

        # Per-task accumulation (S8370.3/T3): track pending turns until boundary.
        self._pending_task_msgs += 1
        self._pending_task_cost += cost
        if self._pending_task_boundary is not None:
            work_id, task_name = self._pending_task_boundary
            if not self._first_boundary_seen:
                # First window = one-time orientation (PRIME, plan load, first
                # task) — attributed to setup overhead, not a task bucket.
                self._setup_overhead_msgs += self._pending_task_msgs
                self._setup_overhead_cost += self._pending_task_cost
                self._first_boundary_seen = True
            else:
                self._task_stats_ordered.append(
                    TaskRunStats(
                        task=task_name,
                        work_id=work_id,
                        messages=self._pending_task_msgs,
                        cost_usd=self._pending_task_cost,
                    )
                )
            self._pending_task_msgs = 0
            self._pending_task_cost = 0.0
            self._pending_task_boundary = None

        if self._post_approve_window > 0:
            self._post_approve_window -= 1
            if self._post_approve_window == 0 and self._post_approve_edited:
                self._approvals_with_edits += 1
                self._post_approve_edited = False


class StoryAttribution(BaseModel):
    """Per-story cost attributed to the CC session that closed it."""

    work_id: str
    session_id: str
    cost_usd: float | None  # None = JSONL not found on disk
    jsonl_found: bool
    window_start: str | None = None  # ISO ts of prev close (or None = session start)
    window_end: str | None = None  # ISO ts of this close (or None = no upper bound)
    overhead: bool = False  # True = post-last-close remainder, not a story


def _query_sqlite_work_closes(
    db_path: Path,
    since: datetime | None,
    until: datetime | None,
    work_types: tuple[str, ...] = ("story", "bugfix"),
) -> dict[str, tuple[str, str]]:
    """Return {work_id: (agent_session_id, close_iso_ts)} from work close signals.

    Falls back to empty dict when DB is absent or query fails.
    Post-E7884: pipeline_advance emits signals to SQLite, not JSONL tool calls.
    S9463.5/T1: returns close timestamp alongside session_id for time-sliced windows.
    RAISE-9685: parameterized work_types includes bugfix in addition to story.
    """
    if not work_types:
        raise ValueError("work_types must not be empty")
    if not db_path.exists():
        return {}
    import sqlite3

    try:
        conn = sqlite3.connect(str(db_path))
        try:
            placeholders = ",".join("?" * len(work_types))
            # Only generated "?" placeholders are interpolated.
            sql = (
                "SELECT DISTINCT"  # noqa: S608  # nosec B608
                " json_extract(payload, '$.work_id'),"
                " json_extract(payload, '$.agent_session_id'),"
                " timestamp"
                " FROM signals"
                " WHERE type = 'work_lifecycle'"
                f"   AND json_extract(payload, '$.work_type') IN ({placeholders})"
                "   AND json_extract(payload, '$.event') = 'complete'"
                "   AND json_extract(payload, '$.phase') = 'close'"
                "   AND json_extract(payload, '$.agent_session_id') IS NOT NULL"
            )
            params: list[str] = list(work_types)
            if since is not None:
                sql += " AND timestamp >= ?"
                params.append(since.isoformat())
            if until is not None:
                sql += " AND timestamp < ?"
                params.append(until.isoformat())
            rows = conn.execute(sql, params).fetchall()
        finally:
            conn.close()
        return {
            row[0]: (row[1], row[2]) for row in rows if row[0] and row[1] and row[2]
        }
    except sqlite3.Error:
        logger.warning(
            "SQLite query failed in _query_sqlite_work_closes", exc_info=True
        )
        return {}


class WeeklyRow(BaseModel):
    """Cost aggregation for one ISO week."""

    iso_week: str  # e.g. "2026-W25"
    n_stories: int
    total_usd: float
    avg_usd: float


def build_weekly_report(attributions: list[StoryAttribution]) -> list[WeeklyRow]:
    """Group story attributions by ISO week of window_end.

    Skips entries with no window_end and overhead entries.
    Returns rows sorted ascending by week.
    S9463.5/T4 — AC5.
    """
    from collections import defaultdict

    week_totals: dict[str, list[float]] = defaultdict(list)
    for a in attributions:
        if a.overhead or a.window_end is None or a.cost_usd is None:
            continue
        ts = _parse_timestamp(a.window_end)
        if ts is None:
            continue
        iso_cal = ts.isocalendar()
        week_label = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
        week_totals[week_label].append(a.cost_usd)

    rows: list[WeeklyRow] = []
    for week_label in sorted(week_totals):
        costs = week_totals[week_label]
        total = sum(costs)
        rows.append(
            WeeklyRow(
                iso_week=week_label,
                n_stories=len(costs),
                total_usd=total,
                avg_usd=total / len(costs),
            )
        )
    return rows


def infer_epic(work_id: str) -> str | None:
    r"""Infer epic identifier from a story work_id.

    Patterns (S9463.5/T5 — D5):
    - S(\d+)\.\d+ -> E{N}   (e.g. S9463.5 -> E9463)
    - S-([A-Z][A-Z0-9.-]*?)\.\d+ -> prefix  (e.g. S-RFCC.I.3 -> RFCC.I)
    - anything else -> None  (displayed as "(sin-epica)")
    """
    m = re.match(r"^S(\d+)\.\d+$", work_id)
    if m:
        return f"E{m.group(1)}"
    m = re.match(r"^S-([A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)*)\.\d+", work_id)
    if m:
        return m.group(1)
    return None


class EpicRow(BaseModel):
    """Cost aggregation for one inferred epic."""

    epic: str
    n_stories: int
    total_usd: float
    avg_usd: float


def build_epic_report(attributions: list[StoryAttribution]) -> list[EpicRow]:
    """Group story attributions by inferred epic.

    None → "(sin-épica)". Overhead entries excluded.
    Sorted by total_usd descending.
    S9463.5/T5 — AC6.
    """
    from collections import defaultdict

    epic_costs: dict[str, list[float]] = defaultdict(list)
    for a in attributions:
        if a.overhead or a.cost_usd is None:
            continue
        epic = infer_epic(a.work_id) or "(sin-épica)"
        epic_costs[epic].append(a.cost_usd)

    rows: list[EpicRow] = []
    for epic, costs in epic_costs.items():
        total = sum(costs)
        rows.append(
            EpicRow(
                epic=epic,
                n_stories=len(costs),
                total_usd=total,
                avg_usd=total / len(costs),
            )
        )
    return sorted(rows, key=lambda r: -r.total_usd)


class TrendReport(BaseModel):
    """8-week trend report with delta% and sparkline. S9463.5/T6 — AC7."""

    weeks: list[str]  # ISO week labels, oldest first
    costs: list[float]  # total USD per week (parallel to weeks)
    sparkline: str
    current_week: str
    current_usd: float
    prior_week: str | None
    prior_usd: float | None
    delta_pct: float | None  # (current - prior) / prior * 100, or None


def _collect_iso_weeks(n_weeks: int) -> list[str]:
    """Return the last n_weeks distinct ISO week labels, oldest first."""
    from datetime import date, timedelta

    today = date.today()
    weeks: list[str] = []
    d = today
    while len(weeks) < n_weeks:
        iso_cal = d.isocalendar()
        label = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
        if label not in weeks:
            weeks.insert(0, label)
        d -= timedelta(days=7)
    return weeks


def build_trend_report(
    attributions: list[StoryAttribution],
    n_weeks: int = 8,
) -> TrendReport:
    """Compute last n_weeks ISO weeks from today and sum costs per week.

    S9463.5/T6 — AC7.
    """
    weeks = _collect_iso_weeks(n_weeks)

    # Build a set of all weeks in window
    week_set = set(weeks)

    # Sum costs per week from attributions
    week_totals: dict[str, float] = dict.fromkeys(weeks, 0.0)
    for a in attributions:
        if a.overhead or a.window_end is None or a.cost_usd is None:
            continue
        ts = _parse_timestamp(a.window_end)
        if ts is None:
            continue
        iso_cal = ts.isocalendar()
        label = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
        if label in week_set:
            week_totals[label] += a.cost_usd

    costs = [week_totals[w] for w in weeks]
    sparkline = build_sparkline(costs)

    current_week = weeks[-1] if weeks else ""
    current_usd = costs[-1] if costs else 0.0
    prior_week = weeks[-2] if len(weeks) >= 2 else None
    prior_usd = costs[-2] if len(costs) >= 2 else None

    delta_pct: float | None = None
    if prior_usd is not None and prior_usd > 0:
        delta_pct = (current_usd - prior_usd) / prior_usd * 100.0

    return TrendReport(
        weeks=weeks,
        costs=costs,
        sparkline=sparkline,
        current_week=current_week,
        current_usd=current_usd,
        prior_week=prior_week,
        prior_usd=prior_usd,
        delta_pct=delta_pct,
    )


_SPARKLINE_BLOCKS_CR = "▁▂▃▄▅▆▇█"


def build_sparkline(values: list[float]) -> str:
    """Map list of floats to sparkline string using 8 Unicode block levels.

    Used by build_trend_report. For CLI display use _sparkline in telemetry.py.
    All equal → all ▄. Single value → █. Empty → "".
    """
    if not values:
        return ""
    if len(values) == 1:
        return "█"
    min_v = min(values)
    max_v = max(values)
    if max_v == min_v:
        return _SPARKLINE_BLOCKS_CR[3] * len(values)
    span = max_v - min_v
    return "".join(
        _SPARKLINE_BLOCKS_CR[min(7, int((v - min_v) / span * 8))] for v in values
    )


def _dedup_story_closes(
    raw: dict[str, tuple[str, str]],
) -> dict[str, tuple[str, str]]:
    """Dedup story-close signal pairs that share (session_id, ±120s bucket).

    Each story-close emits two signals ~10-60s apart — one with the story-ID
    form (e.g. "S9463.5") and one with the Jira-key form (e.g. "RAISE-9603").
    When both appear within 120s for the same session, keep the story-ID form
    and drop the Jira-key form (story-ID preserves epic inference).

    S9463.5/T3 — AC3: dedup keeps story-ID; AC11: missing session_id skipped.
    """
    # Regex for the story-ID form: S{N}.{M} or S-{PREFIX}…
    story_id_re = re.compile(r"^S\d+\.\d+$|^S-[A-Z]")

    # Group by (session_id, bucket), where bucket = int(ts // 120)
    from collections import defaultdict

    # bucket_key → list of (work_id, session_id, close_ts_str)
    buckets: dict[tuple[str, int], list[tuple[str, str, str]]] = defaultdict(list)
    for work_id, (session_id, close_ts_str) in raw.items():
        if not session_id:
            continue  # AC11: no session_id → skip grouping, preserve below
        ts = _parse_timestamp(close_ts_str)
        if ts is None:
            continue
        bucket = int(ts.timestamp() // 120)
        buckets[(session_id, bucket)].append((work_id, session_id, close_ts_str))

    # Build set of work_ids to drop
    to_drop: set[str] = set()
    for entries in buckets.values():
        if len(entries) < 2:
            continue
        story_ids = [w for w, _, _ in entries if story_id_re.match(w)]
        jira_keys = [w for w, _, _ in entries if not story_id_re.match(w)]
        if story_ids and jira_keys:
            # Keep story-ID form; drop Jira-key form
            to_drop.update(jira_keys)

    return {wid: val for wid, val in raw.items() if wid not in to_drop}


def _build_windowed_story_costs(
    story_sessions: dict[str, tuple[str, str]],
    projects_dir: Path,
    pricing: dict[str, ModelPricing] | None,
) -> list[StoryAttribution]:
    """Build disjoint time-window attributions for stories sharing a session.

    Groups story closes by session_id, sorts by close_ts, then for each story
    computes the window [prev_close, this_close). Appends an overhead entry for
    tokens after the last close per session.

    S9463.5/T2: replaces the full-session scan that caused identical inflated costs
    when multiple stories were closed in one CC session.
    """
    from collections import defaultdict

    # Group by session_id: {session_id: [(work_id, close_ts_str), ...]}
    by_session: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for work_id, (session_id, close_ts_str) in story_sessions.items():
        by_session[session_id].append((work_id, close_ts_str))

    result: list[StoryAttribution] = []

    for session_id, entries in by_session.items():
        # Resolve JSONL path; if absent, record all stories as missing
        if projects_dir.exists():
            matches = list(projects_dir.glob(f"*/{session_id}.jsonl"))
        else:
            matches = []

        if not matches:
            for work_id, _ in entries:
                result.append(
                    StoryAttribution(
                        work_id=work_id,
                        session_id=session_id,
                        cost_usd=None,
                        jsonl_found=False,
                    )
                )
            continue

        # Pick the largest file: worktree dirs often contain stub copies with 0 tokens.
        jsonl_path = max(matches, key=lambda p: p.stat().st_size)

        # Sort closes ascending by timestamp string (ISO lexicographic = chronological)
        sorted_entries = sorted(entries, key=lambda e: e[1])

        prev_dt: datetime | None = None
        for work_id, close_ts_str in sorted_entries:
            close_dt = _parse_timestamp(close_ts_str)
            report = scan_single_session(
                jsonl_path,
                pricing,
                since=prev_dt,
                until=close_dt,
            )
            result.append(
                StoryAttribution(
                    work_id=work_id,
                    session_id=session_id,
                    cost_usd=report.total_cost_usd,
                    jsonl_found=True,
                    window_start=prev_dt.isoformat() if prev_dt is not None else None,
                    window_end=close_ts_str,
                )
            )
            prev_dt = close_dt

        # Overhead: tokens after the last close
        if prev_dt is not None:
            oh_report = scan_single_session(
                jsonl_path,
                pricing,
                since=prev_dt,
                until=None,
            )
            result.append(
                StoryAttribution(
                    work_id=f"overhead({session_id[:8]})",
                    session_id=session_id,
                    cost_usd=oh_report.total_cost_usd,
                    jsonl_found=True,
                    window_start=prev_dt.isoformat(),
                    window_end=None,
                    overhead=True,
                )
            )

    return result


def build_story_attribution(
    projects_dir: Path,
    db_path: Path | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    pricing: dict[str, ModelPricing] | None = None,
) -> list[StoryAttribution]:
    """Correlate story close signals to JSONL cost via agent_session_id.

    For each story in the SQLite signals table, resolves the CC session JSONL
    by matching agent_session_id to the file stem under projects_dir. Returns
    attributions sorted by cost descending (unresolvable stories sort last).
    """
    from raise_cli.storage.connection import get_project_db_path

    resolved_db = db_path if db_path is not None else get_project_db_path()
    story_sessions = _query_sqlite_work_closes(resolved_db, since, until)
    # AC3: dedup Jira-key/story-ID signal pairs before windowing
    story_sessions = _dedup_story_closes(story_sessions)

    result = _build_windowed_story_costs(story_sessions, projects_dir, pricing)

    # Sort: real stories by cost desc; overhead entries at end
    def _sort_key(a: StoryAttribution) -> tuple[int, float]:
        return (1 if a.overhead else 0, -(a.cost_usd or 0.0))

    return sorted(result, key=_sort_key)


def build_report(
    projects_dir: Path,
    since: datetime | None = None,
    until: datetime | None = None,
    pricing: dict[str, ModelPricing] | None = None,
) -> CostReport:
    """Aggregate all sessions in *projects_dir* into a cost report."""
    table = pricing if pricing is not None else PRICING
    scanner = _SessionScanner(table, since, until)
    if projects_dir.exists():
        seen: set[tuple[str, str]] = set()
        for jsonl_path in sorted(projects_dir.glob("*/*.jsonl")):
            scanner.scan_file(jsonl_path, seen)

    models = sorted(scanner.model_totals.values(), key=lambda m: -m.cost_usd)
    skills = sorted(scanner.skill_stats.values(), key=lambda s: -s.cost_usd)
    phases = sorted(scanner.phase_stats.values(), key=lambda p: -p.cost_usd)
    categories: dict[str, float] = {}
    for s in skills:
        categories[s.category] = categories.get(s.category, 0.0) + s.cost_usd

    total = sum(m.cost_usd for m in models)
    n_stories = len(scanner.closed_stories)
    scanner.flush_approve_window()
    n_approvals = scanner.approvals_total
    n_edits = scanner.approvals_with_edits
    tasks = sorted(scanner.task_stats, key=lambda t: -t.cost_usd)
    n_tasks = len(tasks)
    msgs_per_task = sum(t.messages for t in tasks) / n_tasks if n_tasks else None
    setup_msgs, setup_cost = scanner.setup_overhead
    return CostReport(
        since=since,
        until=until,
        models=models,
        skills=skills,
        phases=phases,
        tasks=tasks,
        setup_overhead_msgs=setup_msgs,
        setup_overhead_cost_usd=setup_cost,
        categories=categories,
        stories_completed=n_stories,
        cost_per_story=(total / n_stories) if n_stories else None,
        total_cost_usd=total,
        msgs_per_task=msgs_per_task,
        approvals_total=n_approvals,
        approvals_with_edits=n_edits,
        rubber_stamp_rate=(n_edits / n_approvals) if n_approvals else None,
        tool_fail_ratio=scanner.tool_fail_ratio,
        edit_revert_files=scanner.edit_revert_files,
        session_duration_minutes=scanner.session_duration_minutes,
        max_gate_fail_streak=scanner.max_gate_fail_streak,
    )


def scan_single_session(
    jsonl_path: Path,
    pricing: dict[str, ModelPricing] | None = None,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
) -> CostReport:
    """Produce a CostReport from a single CC session JSONL file.

    Args:
        jsonl_path: Path to the CC session JSONL file.
        pricing: Optional pricing table override. Defaults to PRICING.
        since: Optional lower bound (inclusive). Messages before this are excluded.
        until: Optional upper bound (exclusive). Messages at or after this are excluded.
    """
    from raise_cli.telemetry.backfill import repo_slug_from_project_dir

    table = pricing if pricing is not None else PRICING
    scanner = _SessionScanner(table, since=since, until=until)
    seen: set[tuple[str, str]] = set()

    if jsonl_path.exists() and jsonl_path.stat().st_size > 0:
        scanner.scan_file(jsonl_path, seen)

    scanner.flush_approve_window()

    models = sorted(scanner.model_totals.values(), key=lambda m: -m.cost_usd)
    skills = sorted(scanner.skill_stats.values(), key=lambda s: -s.cost_usd)
    phases = sorted(scanner.phase_stats.values(), key=lambda p: -p.cost_usd)
    categories: dict[str, float] = {}
    for s in skills:
        categories[s.category] = categories.get(s.category, 0.0) + s.cost_usd

    total = sum(m.cost_usd for m in models)
    n_stories = len(scanner.closed_stories)
    n_approvals = scanner.approvals_total
    n_edits = scanner.approvals_with_edits
    tasks = sorted(scanner.task_stats, key=lambda t: -t.cost_usd)
    n_tasks = len(tasks)
    msgs_per_task = sum(t.messages for t in tasks) / n_tasks if n_tasks else None
    setup_msgs, setup_cost = scanner.setup_overhead

    repo_slug = repo_slug_from_project_dir(jsonl_path.parent.name)

    return CostReport(
        session_id=jsonl_path.stem,
        repo_slug=repo_slug,
        models=models,
        skills=skills,
        phases=phases,
        tasks=tasks,
        setup_overhead_msgs=setup_msgs,
        setup_overhead_cost_usd=setup_cost,
        categories=categories,
        stories_completed=n_stories,
        cost_per_story=(total / n_stories) if n_stories else None,
        total_cost_usd=total,
        msgs_per_task=msgs_per_task,
        approvals_total=n_approvals,
        approvals_with_edits=n_edits,
        rubber_stamp_rate=(n_edits / n_approvals) if n_approvals else None,
        tool_fail_ratio=scanner.tool_fail_ratio,
        edit_revert_files=scanner.edit_revert_files,
        session_duration_minutes=scanner.session_duration_minutes,
        max_gate_fail_streak=scanner.max_gate_fail_streak,
    )
