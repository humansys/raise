"""PIT (Probability Integral Transform) normalization for SA scores.

Maps spreading activation scores to percentile rank [0.0, 1.0] using a
pre-computed cartridge histogram. Enables fair comparison across cartridges
with different SA score distributions.

No numpy dependency — uses stdlib only (bisect, statistics).
"""

from __future__ import annotations

import bisect
import statistics
from typing import Final

from pydantic import BaseModel, Field

# Fixed quantile cuts: [p10, p25, p50, p75, p90, p95, p99]
# These 7 cuts give sufficient resolution for SA score discrimination.
_QUANTILE_CUTS: Final[list[int]] = [10, 25, 50, 75, 90, 95, 99]

# Percentile ranks corresponding to the 7 quantile cuts above.
# Used for linear interpolation in pit_normalize().
_QUANTILE_RANKS: Final[list[float]] = [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]

# Minimum sample size required to use full PIT interpolation.
# Below this threshold, fallback to max_sa normalization.
_MIN_SAMPLE_FOR_PIT: Final[int] = 5


class CartridgeHistogram(BaseModel):
    """Distribucion de SA scores de un cartridge para normalizacion PIT.

    Se almacena como metadato del cartridge y se usa en pit_normalize()
    para mapear SA scores brutos a percentile ranks [0.0, 1.0].
    """

    cartridge_name: str
    quantiles: list[float] = Field(
        description="SA scores en cuantiles fijos [p10, p25, p50, p75, p90, p95, p99]"
    )
    max_sa: float = Field(description="Max SA observado en el corpus del cartridge")
    sample_size: int = Field(
        description="Numero de nodos usados para construir el histograma"
    )


def build_histogram(
    sa_scores: dict[str, float],
    cartridge_name: str,
) -> CartridgeHistogram:
    """Build a CartridgeHistogram from a cartridge's SA scores.

    Args:
        sa_scores: Mapping node_id → SA score for the entire cartridge corpus.
                   This is the output of spreading_activation() over all nodes.
        cartridge_name: Name of the cartridge (stored in the histogram).

    Returns:
        CartridgeHistogram with 7 quantile cuts, max_sa, and sample_size.
        If sa_scores is empty, returns a histogram with quantiles=[], max_sa=0.0,
        sample_size=0 — pit_normalize() will treat this as pass-through.
    """
    if not sa_scores:
        return CartridgeHistogram(
            cartridge_name=cartridge_name,
            quantiles=[],
            max_sa=0.0,
            sample_size=0,
        )

    values = list(sa_scores.values())
    max_sa = max(values)

    if len(values) < 2:
        # statistics.quantiles() requires >= 2 values.
        # Return single-value histogram; pit_normalize() will use fallback path
        # (sample_size < _MIN_SAMPLE_FOR_PIT).
        return CartridgeHistogram(
            cartridge_name=cartridge_name,
            quantiles=[values[0]] * 7,
            max_sa=max_sa,
            sample_size=len(values),
        )

    # statistics.quantiles(data, n=100) returns n-1 cut points.
    # We extract the 7 cuts corresponding to _QUANTILE_CUTS.
    all_quantiles = statistics.quantiles(values, n=100)
    selected = [all_quantiles[cut - 1] for cut in _QUANTILE_CUTS]

    return CartridgeHistogram(
        cartridge_name=cartridge_name,
        quantiles=selected,
        max_sa=max_sa,
        sample_size=len(values),
    )


def _interpolate_rank(sa_raw: float, q: list[float], max_sa: float) -> float:
    """Linear interpolation of percentile rank within the quantile array.

    Args:
        sa_raw: Raw SA score.
        q: Sorted quantile values (7 entries for p10..p99).
        max_sa: Maximum SA score observed (used as upper anchor for >p99).

    Returns:
        Percentile rank in [0.0, 1.0].
    """
    idx = bisect.bisect_left(q, sa_raw)

    if idx == 0:
        # Below p10: interpolate from 0.0 to p10 rank
        if q[0] <= 0.0:
            return 0.0
        return max(0.0, _QUANTILE_RANKS[0] * (sa_raw / q[0]))

    if idx >= len(q):
        # Above p99: extrapolate toward 1.0 using max_sa as upper anchor
        remaining = 1.0 - _QUANTILE_RANKS[-1]
        upper = max_sa if max_sa > q[-1] else q[-1] * 1.1
        if upper <= q[-1]:
            return 1.0
        fraction = min((sa_raw - q[-1]) / (upper - q[-1]), 1.0)
        return min(_QUANTILE_RANKS[-1] + remaining * fraction, 1.0)

    # Between two quantile cuts: linear interpolation
    lo_val, hi_val = q[idx - 1], q[idx]
    lo_rank, hi_rank = _QUANTILE_RANKS[idx - 1], _QUANTILE_RANKS[idx]
    if hi_val <= lo_val:
        return (lo_rank + hi_rank) / 2.0
    t = (sa_raw - lo_val) / (hi_val - lo_val)
    return max(0.0, min(lo_rank + t * (hi_rank - lo_rank), 1.0))


def pit_normalize(
    sa_raw: float,
    histogram: CartridgeHistogram | None,
) -> float:
    """Map a raw SA score to a percentile rank in [0.0, 1.0] via PIT.

    Three paths (per ADR-101):
      1. Pass-through: histogram is None or sample_size == 0 → return sa_raw.
      2. Fallback: sample_size < _MIN_SAMPLE_FOR_PIT → sa_raw / max_sa (clamped).
      3. Normal: bisect over quantiles + linear interpolation → [0.0, 1.0].

    Args:
        sa_raw: Raw SA score from spreading_activation().
        histogram: Pre-computed histogram for the cartridge. None = not available.

    Returns:
        Normalized score in [0.0, 1.0].
    """
    # Path 1: pass-through — no calibration data
    if histogram is None or histogram.sample_size == 0:
        return sa_raw

    # Path 2: fallback — too few samples for reliable quantile estimation
    if histogram.sample_size < _MIN_SAMPLE_FOR_PIT:
        if histogram.max_sa <= 0.0:
            return sa_raw
        return min(sa_raw / histogram.max_sa, 1.0)

    # Path 3: normal PIT via quantile interpolation
    q = histogram.quantiles
    if not q:
        return sa_raw  # defensive: empty quantiles despite sample_size > 0
    return _interpolate_rank(sa_raw, q, histogram.max_sa)


def normalize_sa_scores(
    sa_scores: dict[str, float],
    histogram: CartridgeHistogram | None,
) -> dict[str, float]:
    """Apply pit_normalize() to every score in a cartridge result dict.

    Convenience wrapper for the federation layer (I.5) which has
    sa_scores: dict[str, float] from the engine.

    Args:
        sa_scores: Mapping node_id → raw SA score.
        histogram: Pre-computed histogram for the cartridge.

    Returns:
        New dict with same keys, values replaced by normalized scores [0.0, 1.0].
    """
    return {
        node_id: pit_normalize(score, histogram) for node_id, score in sa_scores.items()
    }
