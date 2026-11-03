"""Pydantic models + pure decision function for FF promotion (RAISE-14679).

Answers: has a given fitness function (CI drift guard) earned promotion from
advisory (``allow_failure: true``) to hard-blocking, based on its measured
false-positive rate over recorded stories? See the package docstring
(``gates/calibration/__init__.py``) for how this differs from the top-level
``raise_cli.calibration`` (velocity/estimation) package.

``evaluate_promotion()`` is pure: no I/O, no clock reads. Timestamping and
persistence are the caller's concern (``gates/calibration/log.py``).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class StorySample(BaseModel):
    """One story's worth of calibration data for a single fitness function."""

    story_id: str
    flags_raised: int = Field(ge=0)
    false_positives: int = Field(ge=0)


class CalibrationRecord(BaseModel):
    """Calibration data for a fitness function across one or more stories."""

    ff_name: str
    samples: list[StorySample]


class PromotionPolicy(BaseModel):
    """Configurable promotion thresholds (AC: not hard-coded literals)."""

    max_fp_rate: float = 0.10
    min_stories: int = 3


class PromotionDecision(BaseModel):
    """Result of evaluating a `CalibrationRecord` against a `PromotionPolicy`."""

    ff_name: str
    approved: bool
    stories_count: int
    total_flags: int
    total_false_positives: int
    fp_rate: float | None
    reason: str


def _insufficient_data_decision(
    record: CalibrationRecord,
    policy: PromotionPolicy,
    stories_count: int,
    total_flags: int,
    total_false_positives: int,
) -> PromotionDecision:
    """Deny: fewer than `policy.min_stories` samples recorded."""
    reason = (
        f"Fitness function '{record.ff_name}' has {stories_count} story of "
        f"calibration data; promotion requires >= {policy.min_stories}. "
        "Promotion denied (insufficient data)."
        if stories_count == 1
        else (
            f"Fitness function '{record.ff_name}' has {stories_count} stories "
            f"of calibration data; promotion requires >= {policy.min_stories}. "
            "Promotion denied (insufficient data)."
        )
    )
    return PromotionDecision(
        ff_name=record.ff_name,
        approved=False,
        stories_count=stories_count,
        total_flags=total_flags,
        total_false_positives=total_false_positives,
        fp_rate=None,
        reason=reason,
    )


def _no_signal_decision(
    record: CalibrationRecord,
    stories_count: int,
) -> PromotionDecision:
    """Deny: the FF never fired — zero flags provide no calibration evidence."""
    reason = (
        f"Fitness function '{record.ff_name}' raised 0 flags over "
        f"{stories_count} stories; no false-positive signal to calibrate. "
        "Promotion denied."
    )
    return PromotionDecision(
        ff_name=record.ff_name,
        approved=False,
        stories_count=stories_count,
        total_flags=0,
        total_false_positives=0,
        fp_rate=None,
        reason=reason,
    )


def _budget_decision(
    record: CalibrationRecord,
    policy: PromotionPolicy,
    stories_count: int,
    total_flags: int,
    total_false_positives: int,
    fp_rate: float,
) -> PromotionDecision:
    """Approve or deny based on `fp_rate` vs. `policy.max_fp_rate`."""
    threshold_pct = policy.max_fp_rate * 100
    observed_pct = fp_rate * 100
    approved = fp_rate <= policy.max_fp_rate
    if approved:
        reason = (
            f"Fitness function '{record.ff_name}' is within the "
            f"{threshold_pct:.0f}% FP budget ({observed_pct:.1f}% observed over "
            f"{stories_count} stories); promotion approved."
        )
    else:
        reason = (
            f"Fitness function '{record.ff_name}' exceeds {threshold_pct:.0f}% "
            f"FP budget ({observed_pct:.1f}% observed over {stories_count} "
            "stories); promotion denied."
        )
    return PromotionDecision(
        ff_name=record.ff_name,
        approved=approved,
        stories_count=stories_count,
        total_flags=total_flags,
        total_false_positives=total_false_positives,
        fp_rate=fp_rate,
        reason=reason,
    )


def evaluate_promotion(
    record: CalibrationRecord,
    policy: PromotionPolicy | None = None,
) -> PromotionDecision:
    """Decide whether `record`'s fitness function earns promotion under `policy`.

    Deny precedence (checked in this order, first match wins):
    1. `stories_count < policy.min_stories` -> insufficient data.
    2. `total_flags == 0` -> no calibration signal (never approve on a vacuous 0%).
    3. `fp_rate > policy.max_fp_rate` -> FP budget exceeded.
    Otherwise: approved.

    `fp_rate = total_false_positives / total_flags` (sum across samples).
    """
    effective_policy = policy if policy is not None else PromotionPolicy()
    stories_count = len(record.samples)
    total_flags = sum(sample.flags_raised for sample in record.samples)
    total_false_positives = sum(sample.false_positives for sample in record.samples)

    if stories_count < effective_policy.min_stories:
        return _insufficient_data_decision(
            record, effective_policy, stories_count, total_flags, total_false_positives
        )

    if total_flags == 0:
        return _no_signal_decision(record, stories_count)

    fp_rate = total_false_positives / total_flags
    return _budget_decision(
        record,
        effective_policy,
        stories_count,
        total_flags,
        total_false_positives,
        fp_rate,
    )
