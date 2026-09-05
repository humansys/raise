"""Release-boundary Change Failure Rate proxy (RAISE-11492).

This is a PROXY, never the per-deployment DORA Change Failure Rate. It counts
releases that were followed by an escaped product fix before the next release —
a hotfix signal. The honest per-deployment CFR requires a real deployment-event
boundary (DeploymentEventStore, S11487.5).

``compute_cfr`` always sets ``is_proxy=True`` and a non-empty ``proxy_basis`` so
a consumer cannot mistake it for DORA. Zero releases in the window yields a
None+reason rate — never a naked number (measurement trap 1).

Pure module: takes release boundaries and fix dates, performs no git work. The
lens resolves git tags into ReleaseBoundary objects and calls in here.
"""

from __future__ import annotations

from datetime import date, timedelta

from pydantic import BaseModel

from raise_cli.reliability.models import ChangeFailureRate, DenominatorValue

__all__ = ["ReleaseBoundary", "compute_cfr"]

_PROXY_BASIS = (
    "release-boundary hotfix proxy — counts releases followed by an escaped "
    "product fix before the next release. NOT the DORA per-deployment Change "
    "Failure Rate (that needs a real deployment-event boundary, S11487.5). "
    "Recent releases are right-censored (excluded) until enough time has passed "
    "for a hotfix to surface."
)


class ReleaseBoundary(BaseModel):
    """One release marker — a git tag and its date."""

    tag: str
    released_at: date


def compute_cfr(
    releases: list[ReleaseBoundary],
    escaped_product_fix_dates: list[date],
    *,
    as_of: date,
    maturity_window_days: int = 90,
) -> ChangeFailureRate:
    """Compute the release-boundary CFR proxy with right-censoring.

    A release is *mature* only if at least ``maturity_window_days`` have elapsed
    since it was cut — otherwise a hotfix has not had time to surface and counting
    it as healthy would deflate the rate (measurement trap 2, same as cohorts).
    In-flight releases are reported via ``releases_in_flight`` but excluded from
    the rate. The fix-attribution window for each mature release still runs to the
    next release (or ``as_of`` for the most recent mature release).

    Args:
        releases: Release boundaries (tag + date). Releases dated after ``as_of``
            are ignored.
        escaped_product_fix_dates: Landing dates of escaped product-target fixes.
        as_of: End of the analysis window.
        maturity_window_days: Days a release must age before it counts toward CFR.

    Returns:
        ChangeFailureRate with is_proxy=True always; rate None+reason when there
        are no mature releases (none at all, or all too recent).
    """
    in_window = sorted(
        (r for r in releases if r.released_at <= as_of),
        key=lambda r: r.released_at,
    )

    cutoff = as_of - timedelta(days=maturity_window_days)
    mature = [r for r in in_window if r.released_at <= cutoff]
    in_flight = len(in_window) - len(mature)

    if not mature:
        reason = (
            "insufficient: no releases in the analysis window — "
            "release-boundary CFR needs at least one tagged release"
            if not in_window
            else (
                f"insufficient: all {in_flight} release(s) are right-censored "
                f"(younger than {maturity_window_days}d) — too recent for hotfixes "
                "to have surfaced"
            )
        )
        return ChangeFailureRate(
            rate=DenominatorValue(
                value=None, numerator=0, denominator=0, reason=reason
            ),
            is_proxy=True,
            proxy_basis=_PROXY_BASIS,
            releases_considered=0,
            releases_failed=0,
            releases_in_flight=in_flight,
            window_start=in_window[0].released_at if in_window else None,
            window_end=as_of,
        )

    # Attribution windows span the full in-window release sequence so a fix is
    # credited to the correct release even when the next release is in-flight.
    fixes = sorted(escaped_product_fix_dates)
    failed = 0
    for i, rel in enumerate(in_window):
        if rel.released_at > cutoff:  # in-flight — recompute predicate directly (O(1))
            continue
        window_start = rel.released_at
        is_last = i + 1 >= len(in_window)
        window_end = as_of if is_last else in_window[i + 1].released_at
        if _any_in_window(fixes, window_start, window_end, inclusive_end=is_last):
            failed += 1

    total = len(mature)
    return ChangeFailureRate(
        rate=DenominatorValue(
            value=failed / total, numerator=failed, denominator=total
        ),
        is_proxy=True,
        proxy_basis=_PROXY_BASIS,
        releases_considered=total,
        releases_failed=failed,
        releases_in_flight=in_flight,
        window_start=mature[0].released_at,
        window_end=as_of,
    )


def _any_in_window(
    sorted_fixes: list[date], start: date, end: date, *, inclusive_end: bool
) -> bool:
    """True if any fix date falls in the window.

    Inner windows are half-open [start, end): a fix exactly on a later release
    boundary belongs to that later release. The last window (end = as_of) is
    closed [start, as_of] so a fix landing on the analysis edge is not lost.
    """
    if inclusive_end:
        return any(start <= f <= end for f in sorted_fixes)
    return any(start <= f < end for f in sorted_fixes)
