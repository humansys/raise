"""Gate evasion detector for the post-session distillation pipeline — RAISE-15327.

Detects three evasion sub-types from a sequence of TurnRecords:
- GATE_EVASION: a gate fails and the agent advances without honoring it
- BYPASS_FLAG: --no-verify or RAISE_SKIP_* in a Bash command
- OMISSION_EVASION: governance action (commit/close) with no prior gate in session

fix→rerun→pass sequences are stored as HONORED (resolved=1), not as active evasions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from raise_cli.distillation.parser import TurnRecord, TurnType

# ──────────────────────────────────────────────────────────────────────────────
# Gate detection patterns
# ──────────────────────────────────────────────────────────────────────────────

_GATE_CMD_RE = re.compile(r"rai gate check\s+([\w.-]+)", re.IGNORECASE)
_MCP_GATE_NAMES = frozenset(
    {"mcp__rai-workspace__raise_gate_check", "raise_gate_check"}
)

_GATE_FAILURE_RES = [
    re.compile(r"Exit code [1-9]"),
    re.compile(r"\bFAIL(?:ED)?\b"),
    re.compile(r"gate[- ].*fail", re.IGNORECASE),
    re.compile(r"attestation.*missing", re.IGNORECASE),
    re.compile(r"status.*fail", re.IGNORECASE),
]

_BYPASS_RES = [
    re.compile(r"--no-verify"),
    re.compile(r"RAISE_AR_SKIP_REASON\s*="),
    re.compile(r"RAISE_SKIP_[A-Z_]+\s*=\s*1"),
]

_GOVERNANCE_COMMIT_CMDS = frozenset(
    {"git commit", "git push", "raise_story_close_full", "pipeline_advance"}
)


def _is_gate_failure(text: str) -> bool:
    return any(r.search(text) for r in _GATE_FAILURE_RES)


def _extract_gate_name(record: TurnRecord) -> dict[str, str]:
    """Return {tool_use_id: gate_name} for all gate invocations in an assistant turn."""
    gates: dict[str, str] = {}
    for tool_use_id, info in record.tool_inputs.items():
        tool_name = info.get("name", "")
        inp = info.get("input", {})
        if tool_name == "Bash":
            cmd = inp.get("command", "") if isinstance(inp, dict) else ""
            m = _GATE_CMD_RE.search(cmd)
            if m:
                gates[tool_use_id] = m.group(1)
        elif tool_name in _MCP_GATE_NAMES:
            gate_name = inp.get("gate_id", inp.get("gate_name", tool_name))
            gates[tool_use_id] = str(gate_name)
    return gates


def _extract_bypass(record: TurnRecord) -> str | None:
    """Return the matching bypass pattern text, or None."""
    for info in record.tool_inputs.values():
        if info.get("name") == "Bash":
            cmd = (
                info.get("input", {}).get("command", "")
                if isinstance(info.get("input"), dict)
                else ""
            )
            for pat in _BYPASS_RES:
                m = pat.search(cmd)
                if m:
                    return m.group(0)
    return None


def _is_governance_commit(record: TurnRecord) -> bool:
    """True if this assistant turn triggers a commit/close governance action."""
    for info in record.tool_inputs.values():
        tool_name = info.get("name", "")
        if tool_name in _MCP_GATE_NAMES:
            continue
        inp = info.get("input", {})
        if tool_name == "Bash":
            cmd = inp.get("command", "") if isinstance(inp, dict) else ""
            if any(g in cmd for g in _GOVERNANCE_COMMIT_CMDS):
                return True
        elif tool_name in {"raise_story_close_full", "pipeline_advance"}:
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Result types
# ──────────────────────────────────────────────────────────────────────────────

EvasionType = Literal["GATE_EVASION", "BYPASS_FLAG", "OMISSION_EVASION"]


@dataclass
class EvasionEvent:
    """A detected gate evasion event from a session."""

    session_id: str
    evasion_type: EvasionType
    gate_name: str
    tool_use_id: str
    gate_turn_idx: int
    failure_turn_idx: int
    pivot_turn_idx: int
    resolved: bool  # True = fix→rerun→pass (HONORED)
    severity: str
    error_snippet: str


@dataclass
class _PendingGate:
    tool_use_id: str
    gate_name: str
    gate_turn_idx: int
    failure_turn_idx: int = -1
    error_snippet: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers for detect_evasions (split out to satisfy C901)
# ──────────────────────────────────────────────────────────────────────────────


def _make_gate_event(
    session_id: str, pg: _PendingGate, pivot_turn_idx: int, resolved: bool
) -> EvasionEvent:
    return EvasionEvent(
        session_id=session_id,
        evasion_type="GATE_EVASION",
        gate_name=pg.gate_name,
        tool_use_id=pg.tool_use_id,
        gate_turn_idx=pg.gate_turn_idx,
        failure_turn_idx=pg.failure_turn_idx,
        pivot_turn_idx=pivot_turn_idx,
        resolved=resolved,
        severity="HIGH",
        error_snippet=pg.error_snippet,
    )


def _process_tool_result(
    record: TurnRecord, pending_failures: dict[str, _PendingGate], idx: int
) -> None:
    if not pending_failures or not _is_gate_failure(record.content_text):
        return
    snippet = record.content_text[:200].strip()
    for pg in pending_failures.values():
        if pg.failure_turn_idx == -1:
            pg.failure_turn_idx = idx
            pg.error_snippet = snippet


def _drain_pending(
    pending_failures: dict[str, _PendingGate],
    session_id: str,
    total: int,
    events: list[EvasionEvent],
) -> None:
    for pg in pending_failures.values():
        if pg.failure_turn_idx != -1:
            events.append(_make_gate_event(session_id, pg, total, resolved=False))


def _close_pending_gates(
    record: TurnRecord,
    session_id: str,
    idx: int,
    pending_failures: dict[str, _PendingGate],
    events: list[EvasionEvent],
) -> None:
    gate_invocations = _extract_gate_name(record)
    to_remove: list[str] = []
    for pg in list(pending_failures.values()):
        if pg.failure_turn_idx == -1:
            continue
        resolved = pg.gate_name in gate_invocations.values()
        events.append(_make_gate_event(session_id, pg, idx, resolved))
        to_remove.append(pg.tool_use_id)
    for k in to_remove:
        pending_failures.pop(k, None)


# ──────────────────────────────────────────────────────────────────────────────
# Main detector
# ──────────────────────────────────────────────────────────────────────────────


def detect_evasions(
    records: list[TurnRecord],
    session_id: str = "",
) -> list[EvasionEvent]:
    """Scan a session's TurnRecords and return all detected evasion events.

    Algorithm (three independent detectors):
    1. GATE_EVASION: assistant invokes gate → tool_result has failure →
       subsequent assistant doesn't re-invoke same gate (or does → HONORED)
    2. BYPASS_FLAG: --no-verify or RAISE_SKIP_* in any Bash command
    3. OMISSION_EVASION: governance commit action without any gate seen since
       last commit (or since session start)
    """
    events: list[EvasionEvent] = []
    pending_failures: dict[str, _PendingGate] = {}
    gate_seen_since_commit = False

    for i, record in enumerate(records):
        if record.turn_type != TurnType.ASSISTANT and not record.is_developer:
            if record.turn_type == TurnType.TOOL_RESULT:
                _process_tool_result(record, pending_failures, i)
            continue

        if record.turn_type != TurnType.ASSISTANT:
            continue

        bypass_match = _extract_bypass(record)
        if bypass_match:
            events.append(
                EvasionEvent(
                    session_id=session_id,
                    evasion_type="BYPASS_FLAG",
                    gate_name="",
                    tool_use_id="",
                    gate_turn_idx=i,
                    failure_turn_idx=i,
                    pivot_turn_idx=i,
                    resolved=False,
                    severity="HIGH",
                    error_snippet=bypass_match[:200],
                )
            )

        _close_pending_gates(record, session_id, i, pending_failures, events)

        for tool_use_id, gate_name in _extract_gate_name(record).items():
            pending_failures[tool_use_id] = _PendingGate(
                tool_use_id=tool_use_id,
                gate_name=gate_name,
                gate_turn_idx=i,
            )
            gate_seen_since_commit = True

        if _is_governance_commit(record):
            if not gate_seen_since_commit:
                events.append(
                    EvasionEvent(
                        session_id=session_id,
                        evasion_type="OMISSION_EVASION",
                        gate_name="",
                        tool_use_id="",
                        gate_turn_idx=-1,
                        failure_turn_idx=-1,
                        pivot_turn_idx=i,
                        resolved=False,
                        severity="HIGH",
                        error_snippet="governance action without prior gate check",
                    )
                )
            gate_seen_since_commit = False

    _drain_pending(pending_failures, session_id, len(records), events)
    return events
