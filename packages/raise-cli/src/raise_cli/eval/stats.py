"""Bootstrap confidence intervals and significance tests."""

from __future__ import annotations

import numpy as np


def bootstrap_ci(
    scores: list[float],
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    seed: int | None = None,
) -> tuple[float, float]:
    """Compute bootstrap confidence interval for the mean.

    Returns:
        (lower_bound, upper_bound) tuple. Empty input returns (0.0, 0.0).
    """
    if not scores:
        return (0.0, 0.0)
    if len(scores) == 1:
        return (scores[0], scores[0])

    rng = np.random.default_rng(seed)
    arr = np.array(scores)
    means = np.array(
        [
            float(rng.choice(arr, size=len(arr), replace=True).mean())
            for _ in range(n_bootstrap)
        ]
    )
    alpha = 1.0 - confidence
    lower = float(np.percentile(means, 100 * alpha / 2))
    upper = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return (lower, upper)


def paired_permutation_test(
    baseline: list[float],
    candidate: list[float],
    n_permutations: int = 10000,
    seed: int | None = None,
) -> tuple[float, float]:
    """Two-sided paired permutation test for mean difference.

    Compares per-query metric scores between baseline and candidate systems.
    No scipy dependency — uses numpy permutation sampling.

    Returns:
        (p_value, delta) where delta = mean(candidate) - mean(baseline).
    """
    if len(baseline) != len(candidate):
        msg = "baseline and candidate must have the same length"
        raise ValueError(msg)
    if not baseline:
        return (1.0, 0.0)

    bl = np.array(baseline)
    cd = np.array(candidate)
    diffs = cd - bl
    observed_delta = float(diffs.mean())

    if observed_delta == 0.0:
        return (1.0, 0.0)

    rng = np.random.default_rng(seed)
    count = 0
    abs_observed = abs(observed_delta)
    for _ in range(n_permutations):
        signs = rng.choice([-1.0, 1.0], size=len(diffs))
        perm_delta = float((diffs * signs).mean())
        if abs(perm_delta) >= abs_observed:
            count += 1

    p_value = (count + 1) / (n_permutations + 1)
    return (p_value, observed_delta)
