"""Heuristic segment pre-filter for episodic extraction (E15472 S1).

Detects "interesting" arc segments within a session transcript using zero LLM
calls. The output of detect_interesting_segments() feeds the episodic extractor
(S2) with focused windows of conversational context.

Design refs: D1 (Segment model), D2 (arc emitters, [AR:1]), D3 (merge +
long-arc windows, [AR:3]), D8 (cost-cap + drop-shortest-first, [AR:4]).

Constraint: this module makes zero LLM calls and must NOT alter
detect_evasions() / check_conformance() event outputs.
"""

from __future__ import annotations

import logging
import re
from typing import Literal

from pydantic import BaseModel

# D2: Reuse same-package detection primitives as span-capturing loops.
# # fmt: off + per-item # type: ignore prevent isort from sorting and Pyright from
# flagging private-usage on these intentional intra-package imports.
# fmt: off
from raise_cli.distillation.classifier import (
    _BLOCKER_RE,  # type: ignore[reportPrivateUsage]
    _DECISION_RE,  # type: ignore[reportPrivateUsage]
)
from raise_cli.distillation.conformance import (
    _COMMIT_RE,  # type: ignore[reportPrivateUsage]
    _FAIL_RE,  # type: ignore[reportPrivateUsage]
    _FIX_TOOLS,  # type: ignore[reportPrivateUsage]
    _GATE_CHECK_RE,  # type: ignore[reportPrivateUsage]
    _PYTEST_RE,  # type: ignore[reportPrivateUsage]
    _extract_bash_commands,  # type: ignore[reportPrivateUsage]
    _normalize_cmd_key,  # type: ignore[reportPrivateUsage]
)
from raise_cli.distillation.evasion import (
    _extract_gate_name,  # type: ignore[reportPrivateUsage]
    _is_gate_failure,  # type: ignore[reportPrivateUsage]
    _PendingGate,  # type: ignore[reportPrivateUsage]
)
from raise_cli.distillation.parser import TurnRecord, TurnType

# fmt: on

_log = logging.getLogger(__name__)

# ── D1: Segment model ─────────────────────────────────────────────────────────

ArcType = Literal[
    "blocker_resolution",
    "gate_evasion",
    "jidoka",
    "tool_error",
    "decision_arc",
    "composite",
]


class Segment(BaseModel):
    """A window of session turns forming a heuristically-detected interesting arc.

    All turn indices are in parser-index space (from parse_session_jsonl),
    never legacy fixture turn_index (non-unique, collapses under _load_gt).
    """

    start_turn: int
    end_turn: int
    arc_type: ArcType
    trigger_turn: int
    turns: list[TurnRecord]
    session_id: str = ""
    score: float = 0.0
    window_group: str = ""


# ── D2: Arc-span emitters ─────────────────────────────────────────────────────
# Each emitter reuses detection *primitives* (matchers, state-shape) from
# evasion.py / conformance.py / classifier.py as span-capturing loops.
# None of them call detect_evasions() / detect_jidoka_violations() /
# detect_tool_reliability_violations() or alter their outputs.


# ── gate_evasion helpers ──────────────────────────────────────────────────────


def _close_pending_evasions(
    i: int,
    pending: dict[str, _PendingGate],
    segs: list[Segment],
) -> None:
    """Emit a gate_evasion Segment for each pending gate that has failed."""
    to_remove: list[str] = []
    for tool_use_id, pg in pending.items():
        if pg.failure_turn_idx != -1:
            segs.append(
                Segment(
                    start_turn=pg.gate_turn_idx,
                    end_turn=i,
                    arc_type="gate_evasion",
                    trigger_turn=pg.gate_turn_idx,
                    turns=[],
                )
            )
            to_remove.append(tool_use_id)
    for k in to_remove:
        del pending[k]


def _open_pending_evasions(
    rec: TurnRecord, i: int, pending: dict[str, _PendingGate]
) -> None:
    """Register gate calls on this ASSISTANT turn as pending evasion candidates."""
    for tool_use_id, gate_name in _extract_gate_name(rec).items():
        pending[tool_use_id] = _PendingGate(
            tool_use_id=tool_use_id,
            gate_name=gate_name,
            gate_turn_idx=i,
        )


def _emit_gate_evasion_spans(records: list[TurnRecord]) -> list[Segment]:
    """Mirror detect_evasions() state machine, emit gate_evasion spans.

    Reuses _extract_gate_name, _is_gate_failure, _PendingGate from evasion.py.
    Span = [gate_turn_idx, pivot_turn_idx] for any gate that failed.
    """
    segs: list[Segment] = []
    pending: dict[str, _PendingGate] = {}

    for i, rec in enumerate(records):
        if rec.turn_type == TurnType.TOOL_RESULT:
            if pending and _is_gate_failure(rec.content_text):
                for pg in pending.values():
                    if pg.failure_turn_idx == -1:
                        pg.failure_turn_idx = i
        elif rec.turn_type == TurnType.ASSISTANT:
            _close_pending_evasions(i, pending, segs)
            _open_pending_evasions(rec, i, pending)

    # Drain remaining failures (session ended without resolution)
    if records:
        last_idx = records[-1].index
        for pg in pending.values():
            if pg.failure_turn_idx != -1:
                segs.append(
                    Segment(
                        start_turn=pg.gate_turn_idx,
                        end_turn=last_idx,
                        arc_type="gate_evasion",
                        trigger_turn=pg.gate_turn_idx,
                        turns=[],
                    )
                )

    return segs


# ── jidoka emitter ────────────────────────────────────────────────────────────


def _emit_jidoka_spans(records: list[TurnRecord]) -> list[Segment]:
    """Mirror detect_jidoka_violations(), emit jidoka spans with start=fail_idx.

    [AR:1]: Violation carries only one turn_index (the commit turn); the span
    start (fail_idx) lives in pending_failure local var and is discarded into
    prose by the original. Here we retain it as Segment.start_turn.
    """
    segs: list[Segment] = []
    pending_failure: tuple[int, str] | None = None
    last_check_type: str | None = None
    last_assistant_had_fix: bool = False

    for rec in records:
        if rec.turn_type == TurnType.ASSISTANT:
            had_fix = bool(_FIX_TOOLS & set(rec.tool_names))
            commands = _extract_bash_commands(rec)
            is_gate = any(_GATE_CHECK_RE.search(c) for c in commands)
            is_test = any(_PYTEST_RE.search(c) for c in commands)

            if is_gate or is_test:
                last_check_type = "gate-fail" if is_gate else "test-fail"
                pending_failure = None
                last_assistant_had_fix = had_fix
                continue

            if pending_failure is not None:
                if had_fix:
                    pending_failure = None
                    last_assistant_had_fix = had_fix
                    continue
                is_commit = any(_COMMIT_RE.search(c) for c in commands)
                if is_commit:
                    fail_idx, _ = pending_failure
                    segs.append(
                        Segment(
                            start_turn=fail_idx,
                            end_turn=rec.index,
                            arc_type="jidoka",
                            trigger_turn=fail_idx,
                            turns=[],
                            score=0.8,
                        )
                    )
                    pending_failure = None

            last_assistant_had_fix = had_fix

        elif rec.turn_type == TurnType.TOOL_RESULT and _FAIL_RE.search(
            rec.content_text
        ):
            if pending_failure is None and not last_assistant_had_fix:
                pending_failure = (rec.index, last_check_type or "test-fail")

    return segs


# ── tool_error helpers ────────────────────────────────────────────────────────

_IMPORT_ERROR_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|cannot import name|AttributeError:.*has no attribute)",
    re.IGNORECASE,
)
_COMMAND_NOT_FOUND_RE = re.compile(
    r"(command not found|No such file or directory:.*|zsh: command not found|bash: \S+: command not found)",
    re.IGNORECASE,
)
_BASH_NONZERO_RE = re.compile(r"Exit code [1-9]\d*", re.IGNORECASE)


def _is_tool_result_error(text: str) -> bool:
    return bool(
        _IMPORT_ERROR_RE.search(text)
        or _COMMAND_NOT_FOUND_RE.search(text)
        or _BASH_NONZERO_RE.search(text)
    )


def _is_retry_identical(commands: list[str], last_bash_cmds: list[str]) -> bool:
    """True if any command in this turn key-matches a prior failing command."""
    return any(
        _normalize_cmd_key(cmd) == _normalize_cmd_key(prev)
        for cmd in commands
        for prev in last_bash_cmds
        if prev.strip()
    )


def _emit_tool_error_spans(records: list[TurnRecord]) -> list[Segment]:
    """Mirror detect_tool_reliability_violations(), emit spans for retry arcs.

    [AR:1]: Original violations carry no span-start; here we track fail_idx
    in a local variable and retain it into Segment.start_turn on retry-identical.
    """
    segs: list[Segment] = []
    last_bash_cmds: list[str] = []
    had_failure: bool = False
    fail_idx: int = -1

    for rec in records:
        if rec.turn_type == TurnType.ASSISTANT:
            commands = _extract_bash_commands(rec)
            if bool(_FIX_TOOLS & set(rec.tool_names)):
                had_failure = False
                fail_idx = -1
            elif (
                had_failure
                and commands
                and _is_retry_identical(commands, last_bash_cmds)
            ):
                if fail_idx >= 0:
                    segs.append(
                        Segment(
                            start_turn=fail_idx,
                            end_turn=rec.index,
                            arc_type="tool_error",
                            trigger_turn=fail_idx,
                            turns=[],
                            score=0.5,
                        )
                    )
                had_failure = False
                fail_idx = -1
            if commands:
                last_bash_cmds = commands
        elif rec.turn_type == TurnType.TOOL_RESULT:
            if (
                _is_tool_result_error(rec.content_text)
                and last_bash_cmds
                and not had_failure
            ):
                had_failure = True
                fail_idx = rec.index

    return segs


# ── remaining arc types ───────────────────────────────────────────────────────


def _emit_blocker_resolution_spans(records: list[TurnRecord]) -> list[Segment]:
    """Detect STOP/blocked turn → resolution (DECISION or fix/commit) arc."""
    segs: list[Segment] = []
    blocker_idx: int | None = None

    for rec in records:
        if rec.turn_type != TurnType.ASSISTANT:
            continue
        if blocker_idx is None:
            if _BLOCKER_RE.search(rec.content_text):
                blocker_idx = rec.index
        else:
            commands = _extract_bash_commands(rec)
            is_fix = bool(_FIX_TOOLS & set(rec.tool_names))
            is_commit = any(_COMMIT_RE.search(c) for c in commands)
            is_decision = bool(_DECISION_RE.search(rec.content_text))
            if is_fix or is_commit or is_decision:
                segs.append(
                    Segment(
                        start_turn=blocker_idx,
                        end_turn=rec.index,
                        arc_type="blocker_resolution",
                        trigger_turn=blocker_idx,
                        turns=[],
                        score=0.7,
                    )
                )
                blocker_idx = None

    return segs


def _emit_decision_arc_spans(records: list[TurnRecord]) -> list[Segment]:
    """Detect DECISION approval → next substantive assistant output arc."""
    segs: list[Segment] = []
    decision_idx: int | None = None

    for rec in records:
        if rec.turn_type != TurnType.ASSISTANT:
            continue
        if decision_idx is None:
            if (
                _DECISION_RE.search(rec.content_text)
                and len(rec.content_text.strip()) > 50
            ):
                decision_idx = rec.index
        elif len(rec.content_text.strip()) > 100:
            segs.append(
                Segment(
                    start_turn=decision_idx,
                    end_turn=rec.index,
                    arc_type="decision_arc",
                    trigger_turn=decision_idx,
                    turns=[],
                    score=0.4,
                )
            )
            decision_idx = None

    return segs


# ── D3: Merge overlapping/adjacent spans ──────────────────────────────────────

_MERGE_GAP = 5  # turns; spans ≤ this gap apart are merged into one composite
_PAD_BEFORE = 3  # turns of context to prepend before the arc start
_PAD_AFTER = 2  # turns of context to append after the arc end


def _merge_spans(spans: list[Segment]) -> list[Segment]:
    """Merge overlapping or near-adjacent (gap ≤ MERGE_GAP) spans.

    Two spans with the same arc_type keep their type; differing types become
    "composite". Never drops a covered turn.
    """
    if not spans:
        return []

    sorted_spans = sorted(spans, key=lambda s: s.start_turn)
    merged: list[Segment] = [sorted_spans[0]]

    for seg in sorted_spans[1:]:
        last = merged[-1]
        gap = seg.start_turn - last.end_turn - 1
        if seg.start_turn <= last.end_turn or gap <= _MERGE_GAP:
            new_arc: ArcType = (
                last.arc_type if last.arc_type == seg.arc_type else "composite"
            )
            merged[-1] = last.model_copy(
                update={
                    "end_turn": max(last.end_turn, seg.end_turn),
                    "arc_type": new_arc,
                }
            )
        else:
            merged.append(seg)

    return merged


def _pad_and_clamp(seg: Segment, max_idx: int) -> Segment:
    """Widen segment by PAD_BEFORE/PAD_AFTER, clamped to [0, max_idx]."""
    return seg.model_copy(
        update={
            "start_turn": max(0, seg.start_turn - _PAD_BEFORE),
            "end_turn": min(max_idx, seg.end_turn + _PAD_AFTER),
        }
    )


# ── D3: Long-arc overlapping-window policy ([AR:3]) ───────────────────────────

_MAX_TURNS = 30  # max turns per sub-window
_STRIDE = 5  # stride between consecutive sub-window starts


def _split_long_arc(seg: Segment) -> list[Segment]:
    """Split arcs longer than MAX_TURNS into overlapping sub-windows.

    Each sub-window shares a window_group id so that cross-window dedup in S2
    can collapse duplicate insights. Never drops a covered turn.
    """
    turn_count = seg.end_turn - seg.start_turn + 1
    if turn_count <= _MAX_TURNS:
        return [seg]

    window_group = f"wg-{seg.start_turn}-{seg.end_turn}"
    sub_windows: list[Segment] = []
    start = seg.start_turn

    while start <= seg.end_turn:
        end = min(start + _MAX_TURNS - 1, seg.end_turn)
        sub_windows.append(
            seg.model_copy(
                update={
                    "start_turn": start,
                    "end_turn": end,
                    "window_group": window_group,
                    "turns": [],
                }
            )
        )
        if end >= seg.end_turn:
            break
        start += _STRIDE

    return sub_windows


# ── D8: Cost-cap + drop-shortest-first ([AR:4]) ───────────────────────────────

_MAX_SEGMENTS = 20  # hard cap on total segments sent to the extractor


def _apply_cost_cap(
    segments: list[Segment], max_segments: int = _MAX_SEGMENTS
) -> list[Segment]:
    """Enforce max_segments cap. Drop SHORTEST segments first; score tie-breaks.

    Dropped segments are logged (observability), never silently discarded.
    Drop order: (fewest turns ASC, lowest score ASC) → front = candidates to drop.
    """
    if len(segments) <= max_segments:
        return segments

    def _sort_key(s: Segment) -> tuple[int, float]:
        return (s.end_turn - s.start_turn + 1, s.score)

    sorted_segs = sorted(segments, key=_sort_key)
    drop_count = len(segments) - max_segments
    dropped = sorted_segs[:drop_count]
    kept = sorted_segs[drop_count:]

    for seg in dropped:
        _log.debug(
            "segment dropped by cost cap: arc_type=%s start=%d end=%d score=%.2f",
            seg.arc_type,
            seg.start_turn,
            seg.end_turn,
            seg.score,
        )

    return kept


# ── Public API ────────────────────────────────────────────────────────────────


def detect_interesting_segments(
    records: list[TurnRecord],
    *,
    session_id: str = "",
    max_segments: int = _MAX_SEGMENTS,
) -> list[Segment]:
    """Detect heuristic arc segments in a session transcript.

    Pipeline:
      1. Union all arc emitters (zero LLM, high-recall bias).
      2. Merge overlapping/adjacent spans (gap ≤ MERGE_GAP → composite).
      3. Pad windows (PAD_BEFORE / PAD_AFTER context turns).
      4. Split long arcs (> MAX_TURNS) into overlapping sub-windows.
      5. Apply cost cap (drop shortest first, score tie-break).
      6. Fill turns list and session_id.

    Returns parser-index-spaced Segments ready for the episodic extractor.
    """
    if not records:
        return []

    max_idx = max(r.index for r in records)
    idx_to_record = {r.index: r for r in records}

    # 1. Union all emitters
    raw: list[Segment] = (
        _emit_gate_evasion_spans(records)
        + _emit_jidoka_spans(records)
        + _emit_tool_error_spans(records)
        + _emit_blocker_resolution_spans(records)
        + _emit_decision_arc_spans(records)
    )

    if not raw:
        return []

    # 2. Merge
    merged = _merge_spans(raw)

    # 3. Pad and clamp
    padded = [_pad_and_clamp(seg, max_idx) for seg in merged]

    # 4. Split long arcs
    split: list[Segment] = []
    for seg in padded:
        split.extend(_split_long_arc(seg))

    # 5. Cost cap
    capped = _apply_cost_cap(split, max_segments=max_segments)

    # 6. Fill turns and session_id (parser-index space)
    result: list[Segment] = []
    for seg in capped:
        turns = [
            idx_to_record[i]
            for i in range(seg.start_turn, seg.end_turn + 1)
            if i in idx_to_record
        ]
        result.append(seg.model_copy(update={"turns": turns, "session_id": session_id}))

    return result
