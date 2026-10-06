"""Tactical type validation — micro-average precision gate against GT YAML.

CI-safe: no LLM, no graph backend. Pure computation over a YAML GT file
and a ``classified: dict[str, str]`` mapping of symbol_id → tactical_type.

RAISE-16918: D2 — accuracy gate implementation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

AUTHORITY_SCORES: dict[str, int] = {
    "ratified": 50,
    "pass3": 30,
    "pass2": 20,
    "pass1": 10,
}


class TacticalGTEntry(BaseModel):
    """One row in the tactical ground-truth YAML file."""

    symbol_id: str
    expected_type: str  # TacticalType snake_case value
    bc_name: str
    source: str = "pass3"  # ratified | pass3 | pass2 | pass1
    rationale: str = ""


class DriftEntry(BaseModel):
    """A single classification drift — GT type vs. current annotation."""

    symbol_id: str
    gt_type: str
    gt_source: str
    current_type: str
    authority_score: int  # AUTHORITY_SCORES[gt_source]


class TacticalAccuracyReport(BaseModel):
    """Full accuracy report from validate_tactical_accuracy()."""

    total_gt: int
    classified_count: int
    correct_count: int
    micro_avg_precision: float
    threshold: float
    gate_passed: bool
    per_type: dict[str, dict[str, int]]  # {type: {correct: N, total: M}}
    missing_count: int
    drift_entries: list[DriftEntry]


def load_gt(gt_path: Path) -> list[TacticalGTEntry]:
    """Load and validate the GT YAML file.

    Args:
        gt_path: Path to the gt_tactical.yaml file.

    Returns:
        List of :class:`TacticalGTEntry` instances.

    Raises:
        FileNotFoundError: If *gt_path* does not exist.
        ValueError: If the YAML is malformed or missing ``symbols`` key.
    """
    if not gt_path.exists():
        raise FileNotFoundError(f"GT file not found: {gt_path}")

    raw: Any = yaml.safe_load(gt_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "symbols" not in raw:
        raise ValueError(f"GT file must have a top-level 'symbols' key: {gt_path}")

    return [TacticalGTEntry.model_validate(row) for row in raw["symbols"]]


def validate_tactical_accuracy(
    classified: dict[str, str],
    gt_path: Path,
    threshold: float = 0.80,
) -> TacticalAccuracyReport:
    """Compute micro-average precision of *classified* against the GT YAML.

    Metric: ``correct / len(gt_symbols)``.
    Symbols in GT but missing from *classified* count as wrong (denominator
    includes them, numerator does not). Symbols in *classified* not in GT are
    ignored.

    Args:
        classified: Mapping of symbol_id → tactical_type string (snake_case).
        gt_path:    Path to the gt_tactical.yaml file.
        threshold:  Pass/fail boundary (inclusive — 0.80 passes at 0.80).

    Returns:
        :class:`TacticalAccuracyReport` with per-type breakdown and drift list.
    """
    gt_entries = load_gt(gt_path)

    # Per-type accumulators: {type: {correct: N, total: M}}
    per_type: dict[str, dict[str, int]] = {}
    correct_count = 0
    missing_count = 0
    drift_entries: list[DriftEntry] = []

    for entry in gt_entries:
        t = entry.expected_type
        if t not in per_type:
            per_type[t] = {"correct": 0, "total": 0}
        per_type[t]["total"] += 1

        if entry.symbol_id not in classified:
            # Missing → counts as wrong
            missing_count += 1
            continue

        current = classified[entry.symbol_id]
        if current == entry.expected_type:
            per_type[t]["correct"] += 1
            correct_count += 1
        else:
            drift_entries.append(
                DriftEntry(
                    symbol_id=entry.symbol_id,
                    gt_type=entry.expected_type,
                    gt_source=entry.source,
                    current_type=current,
                    authority_score=AUTHORITY_SCORES.get(entry.source, 0),
                )
            )

    total_gt = len(gt_entries)
    micro_avg = correct_count / total_gt if total_gt > 0 else 0.0

    return TacticalAccuracyReport(
        total_gt=total_gt,
        classified_count=len(classified),
        correct_count=correct_count,
        micro_avg_precision=micro_avg,
        threshold=threshold,
        gate_passed=micro_avg >= threshold,
        per_type=per_type,
        missing_count=missing_count,
        drift_entries=drift_entries,
    )
