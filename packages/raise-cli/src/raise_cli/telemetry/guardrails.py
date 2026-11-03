"""Cost guardrails for story cost telemetry.

Circuit breaker (S8741.1):
- GuardrailResult: Pydantic model for circuit breaker evaluation output.
- check_circuit_breaker: Evaluate a CostReport against a rolling average.
- rolling_avg_from_sqlite: Read rolling average from local SQLite agent_events.

Loop detection (S8741.2):
- LoopDetectionResult: Pydantic model for loop pattern evaluation output.
- check_loop_patterns: Detect unproductive loop patterns in a CostReport.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from raise_cli.telemetry.cost_report import CostReport

__all__ = [
    # Circuit breaker (S8741.1)
    "GuardrailResult",
    "check_circuit_breaker",
    "rolling_avg_from_sqlite",
    # Loop detection (S8741.2)
    "LoopDetectionResult",
    "check_loop_patterns",
]


class GuardrailResult(BaseModel):
    """Result of a circuit breaker evaluation."""

    triggered: bool
    reason: str | None = None
    severity: Literal["warn", "block"] = "warn"
    threshold: float | None = None
    actual: float | None = None


def check_circuit_breaker(
    report: CostReport,
    rolling_avg_usd: float,
    multiplier: float = 2.5,
) -> GuardrailResult:
    """Evaluate whether story cost exceeds the rolling average by a multiplier.

    Fail-open: when rolling_avg_usd <= 0.0 (no baseline), returns triggered=False.

    Thresholds:
    - warn:  actual >= 2.0 × rolling_avg_usd
    - block: actual >= multiplier × rolling_avg_usd  (default 2.5×)

    Args:
        report: Cost report for the current story/session.
        rolling_avg_usd: Rolling average cost over recent stories. 0.0 = fail-open.
        multiplier: Block threshold multiplier (default 2.5). Warn threshold is
            always 2.0× regardless of multiplier.

    Returns:
        GuardrailResult with triggered/severity/reason/threshold/actual populated.
    """
    if rolling_avg_usd <= 0.0:
        return GuardrailResult(triggered=False)

    actual = report.total_cost_usd
    warn_threshold = rolling_avg_usd * 2.0
    block_threshold = rolling_avg_usd * multiplier

    if actual >= block_threshold:
        return GuardrailResult(
            triggered=True,
            severity="block",
            reason=f"Cost ${actual:.2f} exceeds {multiplier}× rolling avg ${rolling_avg_usd:.2f}",
            threshold=block_threshold,
            actual=actual,
        )
    if actual >= warn_threshold:
        return GuardrailResult(
            triggered=True,
            severity="warn",
            reason=f"Cost ${actual:.2f} exceeds 2.0× rolling avg ${rolling_avg_usd:.2f}",
            threshold=warn_threshold,
            actual=actual,
        )
    return GuardrailResult(triggered=False)


# ---------------------------------------------------------------------------
# S8741.2 — Loop detection: 3 patterns
# ---------------------------------------------------------------------------

# Thresholds — hardcoded, configurability is post-MVP
_GATE_STREAK_WARN = 3
_GATE_STREAK_BLOCK = 5
_TOOL_ERROR_WARN = 0.25
_TOOL_ERROR_BLOCK = 0.40
_EDIT_CHURN_WARN = 3
_EDIT_CHURN_BLOCK = 5


class LoopDetectionResult(BaseModel):
    """Result of a loop pattern detection evaluation.

    Fields:
        triggered: True when one or more unproductive loop patterns are active.
        patterns_active: List of pattern names that fired (e.g. 'gate_fail_streak').
        severity: 'warn' (1 pattern below block threshold) or 'block' (2+ patterns
            or a single pattern at its block threshold). None when not triggered.
        reason: Human-readable summary of active patterns. None when not triggered.
    """

    triggered: bool
    patterns_active: list[str] = []
    severity: Literal["warn", "block"] | None = None
    reason: str | None = None


def check_loop_patterns(report: CostReport) -> LoopDetectionResult:
    """Detect unproductive loop patterns in a cost report.

    Pure function — no I/O, no env vars, no side effects.
    Fail-open: None metrics are treated as inactive (not 0).

    Pattern names:
        'gate_fail_streak' — repeated gate failures indicate a stuck fix loop.
        'tool_error_ratio' — high tool error rate signals flailing tool usage.
        'edit_churn'       — many reverted edits indicate unproductive churn.

    Severity rules:
        - block if 2+ patterns active OR gate_fail_streak >= _GATE_STREAK_BLOCK alone.
        - warn  if exactly 1 pattern active (below its individual block threshold).

    Args:
        report: Cost report for the current story/session.

    Returns:
        LoopDetectionResult with triggered/patterns_active/severity/reason populated.
    """
    active: list[str] = []
    # Each pattern is evaluated at its block threshold independently;
    # the streak pattern has its own solo-block rule.
    streak = report.max_gate_fail_streak
    if streak >= _GATE_STREAK_WARN:
        active.append("gate_fail_streak")

    ratio = report.tool_fail_ratio
    if ratio is not None and ratio >= _TOOL_ERROR_WARN:
        active.append("tool_error_ratio")

    churn = report.edit_revert_files
    if churn >= _EDIT_CHURN_WARN:
        active.append("edit_churn")

    if not active:
        return LoopDetectionResult(triggered=False)

    # Determine severity
    # Block conditions: 2+ active patterns, OR gate_fail_streak alone at block threshold
    is_block = (
        len(active) >= 2
        or (
            "gate_fail_streak" in active
            and streak >= _GATE_STREAK_BLOCK
            and len(active) == 1
        )
        or (
            "tool_error_ratio" in active
            and ratio is not None
            and ratio >= _TOOL_ERROR_BLOCK
            and len(active) == 1
        )
        or ("edit_churn" in active and churn >= _EDIT_CHURN_BLOCK and len(active) == 1)
    )

    severity: Literal["warn", "block"] = "block" if is_block else "warn"
    reason = f"Loop pattern(s) detected: {', '.join(active)}"

    return LoopDetectionResult(
        triggered=True,
        patterns_active=active,
        severity=severity,
        reason=reason,
    )


def rolling_avg_from_sqlite(db_path: Path, n: int = 10) -> float:
    """Read last n story_cost_summary events and return avg cost_usd.

    Returns 0.0 on any error (fail-open): missing DB, missing table, no rows,
    or any SQLite exception.

    Args:
        db_path: Path to the SQLite database containing agent_events table.
        n: Number of most recent story_cost_summary events to average.

    Returns:
        Average cost_usd over the last n events, or 0.0 if unavailable.
    """
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cur = conn.execute(
            """
            SELECT json_extract(payload, '$.cost_usd')
            FROM agent_events
            WHERE event_type = 'story_cost_summary'
              AND json_extract(payload, '$.cost_usd') IS NOT NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (n,),
        )
        costs = [row[0] for row in cur.fetchall() if isinstance(row[0], (int, float))]
        conn.close()
        return sum(costs) / len(costs) if costs else 0.0
    except Exception:  # noqa: BLE001
        return 0.0
