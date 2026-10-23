r"""Shadow policy: compare serial vs bounded xdist vs auto-scaling execution (RAISE-14877).

This module provides:
- Data models (Pydantic) for the shadow policy artifact schema.
- ``check_equivalence``: detect tests that fail in some execution modes but not others
  (concurrency-induced flakiness).
- ``compare_baseline``: flag tests whose serial shadow duration is significantly slower
  than the S1 profiling baseline (potential regression or environment noise).
- ``artifact_from_results``: compose a ``ShadowPolicyArtifact`` from raw per-test records
  and produce a policy recommendation.

## Shadow run commands (documented here; execution is out of scope for this story)

Serial::

    pytest packages/raise-cli/tests/ \\
        -n 0 \\
        -m "not integration and not slow and not ml and not e2e and not perf" \\
        --shadow-output=shadow_serial.json

Bounded xdist (4 workers, loadscope)::

    pytest packages/raise-cli/tests/ \\
        -n 4 --dist=loadscope \\
        -m "not integration and not slow and not ml and not e2e and not perf" \\
        --shadow-output=shadow_bounded.json

Auto-scaling::

    pytest packages/raise-cli/tests/ \\
        -n auto \\
        -m "not integration and not slow and not ml and not e2e and not perf" \\
        --shadow-output=shadow_auto.json

See ``work/epics/e14851-test-execution-economy/baseline/SHADOW_POLICY.md`` for full
methodology and interpretation guide.

## Integration points

- **RAISE-9025 S9025.5 Shadow Reports**: the ``ShadowPolicyArtifact`` schema is designed
  to be consumed by the S9025.5 shadow-report pipeline once it is implemented.
  The ``mode_results`` and ``equivalence_violations`` fields map directly to the
  metrics S9025.5 will collect (time saved, confidence, false-negative evidence).

- **RAISE-11087 Testing Pyramid**: ``equivalence_violations`` identify tests that
  require serial execution and should be reclassified in the pyramid's "no_xdist"
  tier.  ``baseline_anomalies`` identify tests where parallelism introduces
  non-deterministic slowdowns (candidates for ``@pytest.mark.serial``).
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Literal

from pydantic import BaseModel, field_validator

__all__ = [
    "ExecutionMode",
    "ShadowTestRecord",
    "ShadowModeResult",
    "EquivalenceViolation",
    "BaselineAnomaly",
    "ShadowPolicyArtifact",
    "artifact_from_results",
    "check_equivalence",
    "compare_baseline",
]

# Ratio above which a shadow duration is considered anomalous vs. the baseline.
_ANOMALY_THRESHOLD: float = 2.0

# Recommendations emitted by ``artifact_from_results``.
Recommendation = Literal[
    "bounded_xdist_safe",  # no violations; bounded mode duration within baseline range
    "auto_safe",  # no violations; auto mode also safe
    "serial_required",  # equivalence violations detected
    "insufficient_data",  # fewer than 2 modes present in the records
]


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ExecutionMode(str, Enum):
    """Pytest execution mode for the shadow run."""

    SERIAL = "serial"  # -n 0
    BOUNDED = "bounded"  # -n 4 --dist loadscope
    AUTO = "auto"  # -n auto


# ---------------------------------------------------------------------------
# Per-test record
# ---------------------------------------------------------------------------

_VALID_OUTCOMES = frozenset({"passed", "failed", "skipped", "error"})


class ShadowTestRecord(BaseModel):
    """Outcome and duration for one test in one execution mode."""

    node_id: str
    mode: ExecutionMode
    outcome: Literal["passed", "failed", "skipped", "error"]
    duration: float
    workers: int | None = None

    @field_validator("outcome", mode="before")
    @classmethod
    def _validate_outcome(cls, v: str) -> str:
        if v not in _VALID_OUTCOMES:
            raise ValueError(
                f"outcome must be one of {sorted(_VALID_OUTCOMES)!r}, got {v!r}"
            )
        return v


# ---------------------------------------------------------------------------
# Aggregate results per mode
# ---------------------------------------------------------------------------


class ShadowModeResult(BaseModel):
    """Aggregate statistics for one execution mode."""

    mode: ExecutionMode
    total_tests: int
    passed: int
    failed: int
    pass_rate: float
    wall_clock: float
    duration_variance: float

    @classmethod
    def from_records(
        cls,
        records: list[ShadowTestRecord],
        mode: ExecutionMode,
    ) -> ShadowModeResult:
        """Compute aggregate stats from a list of records for a single mode."""
        mode_records = [r for r in records if r.mode == mode]
        total = len(mode_records)
        passed = sum(1 for r in mode_records if r.outcome == "passed")
        failed = sum(1 for r in mode_records if r.outcome == "failed")
        durations = [r.duration for r in mode_records]
        wall_clock = sum(durations)
        if total > 1:
            mean = wall_clock / total
            variance = sum((d - mean) ** 2 for d in durations) / total
        else:
            variance = 0.0
        return cls(
            mode=mode,
            total_tests=total,
            passed=passed,
            failed=failed,
            pass_rate=passed / total if total > 0 else 0.0,
            wall_clock=wall_clock,
            duration_variance=variance,
        )


# ---------------------------------------------------------------------------
# Violations and anomalies
# ---------------------------------------------------------------------------


class EquivalenceViolation(BaseModel):
    """A test that fails in some execution modes but not others.

    This is the primary signal for concurrency-induced flakiness.  A test
    that fails in *all* modes is a real failure and is not reported here.
    """

    node_id: str
    failing_modes: list[ExecutionMode]
    passing_modes: list[ExecutionMode]


class BaselineAnomaly(BaseModel):
    """A test whose serial shadow duration significantly exceeds the S1 baseline.

    Only serial-mode records are compared (the baseline was captured serially).
    """

    node_id: str
    baseline_duration: float
    shadow_duration: float
    ratio: float


# ---------------------------------------------------------------------------
# Top-level artifact
# ---------------------------------------------------------------------------


class ShadowPolicyArtifact(BaseModel):
    """Top-level shadow policy artifact.

    Designed to be serialized to JSON and committed as a governance evidence
    artifact under ``work/epics/e14851-test-execution-economy/``.

    Compatible with RAISE-9025 S9025.5 Shadow Reports consumption:
    - ``mode_results`` maps to time-saved and confidence metrics.
    - ``equivalence_violations`` maps to false-negative evidence.
    - ``baseline_anomalies`` maps to regression signals.
    """

    meta: dict[str, object]
    mode_results: dict[ExecutionMode, ShadowModeResult]
    equivalence_violations: list[EquivalenceViolation]
    baseline_anomalies: list[BaselineAnomaly]
    recommendation: Recommendation


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------


def check_equivalence(records: list[ShadowTestRecord]) -> list[EquivalenceViolation]:
    """Detect tests that fail in some modes but pass in others.

    A test that fails in *all* modes where it was run is a real failure and is
    excluded — this function reports only mode-differential failures (candidates
    for concurrency-induced flakiness or ordering sensitivity).

    Args:
        records: Mixed-mode list of ``ShadowTestRecord`` instances.

    Returns:
        List of ``EquivalenceViolation`` instances, one per affected test.
    """
    by_test: dict[str, dict[ExecutionMode, str]] = defaultdict(dict)
    for r in records:
        by_test[r.node_id][r.mode] = r.outcome

    violations: list[EquivalenceViolation] = []
    for node_id, mode_outcomes in by_test.items():
        passing = [m for m, o in mode_outcomes.items() if o == "passed"]
        failing = [m for m, o in mode_outcomes.items() if o != "passed"]
        if failing and passing:
            violations.append(
                EquivalenceViolation(
                    node_id=node_id,
                    failing_modes=sorted(failing, key=lambda m: m.value),
                    passing_modes=sorted(passing, key=lambda m: m.value),
                )
            )
    return violations


def compare_baseline(
    records: list[ShadowTestRecord],
    baseline: dict[str, float],
    threshold: float = _ANOMALY_THRESHOLD,
) -> list[BaselineAnomaly]:
    """Flag tests whose serial shadow duration exceeds the S1 baseline by ``threshold`` ×.

    Only ``ExecutionMode.SERIAL`` records are compared — the S1 profiling baseline
    was captured in serial mode and duration comparisons across modes are not
    meaningful (parallelism changes absolute durations due to contention).

    Args:
        records: Mixed-mode list of ``ShadowTestRecord`` instances.
        baseline: Mapping of ``node_id`` → serial duration from the S1 profiling
            baseline (``profiling_baseline.json``).
        threshold: Ratio above which a test is considered anomalous.  Default: 2.0.

    Returns:
        List of ``BaselineAnomaly`` instances for tests exceeding the threshold.
    """
    serial_records = {r.node_id: r for r in records if r.mode == ExecutionMode.SERIAL}
    anomalies: list[BaselineAnomaly] = []
    for node_id, record in serial_records.items():
        if node_id not in baseline:
            continue
        base_dur = baseline[node_id]
        if base_dur <= 0:
            continue
        ratio = record.duration / base_dur
        if ratio > threshold:
            anomalies.append(
                BaselineAnomaly(
                    node_id=node_id,
                    baseline_duration=base_dur,
                    shadow_duration=record.duration,
                    ratio=ratio,
                )
            )
    return anomalies


def artifact_from_results(
    records: list[ShadowTestRecord],
    baseline: dict[str, float],
    meta: dict[str, object] | None = None,
) -> ShadowPolicyArtifact:
    """Compose a ``ShadowPolicyArtifact`` from raw records and emit a recommendation.

    Recommendation logic:
    - ``"insufficient_data"``: fewer than 2 distinct modes present.
    - ``"serial_required"``: at least one equivalence violation found.
    - ``"bounded_xdist_safe"``: no violations; both modes present (serial + at least one xdist).
    - ``"auto_safe"``: no violations AND auto mode was tested.

    Args:
        records: Per-test records from all shadow runs (multiple modes).
        baseline: Dict mapping ``node_id`` → serial duration from S1 baseline.
        meta: Free-form metadata dict (generated_at, suite, machine, etc.).

    Returns:
        ``ShadowPolicyArtifact`` ready for JSON serialization.
    """
    modes_present = {r.mode for r in records}
    violations = check_equivalence(records)
    anomalies = compare_baseline(records, baseline)

    mode_results: dict[ExecutionMode, ShadowModeResult] = {}
    for mode in modes_present:
        mode_results[mode] = ShadowModeResult.from_records(records, mode)

    if len(modes_present) < 2:
        recommendation: Recommendation = "insufficient_data"
    elif violations:
        recommendation = "serial_required"
    elif ExecutionMode.AUTO in modes_present:
        recommendation = "auto_safe"
    else:
        recommendation = "bounded_xdist_safe"

    return ShadowPolicyArtifact(
        meta=meta or {},
        mode_results=mode_results,
        equivalence_violations=violations,
        baseline_anomalies=anomalies,
        recommendation=recommendation,
    )
