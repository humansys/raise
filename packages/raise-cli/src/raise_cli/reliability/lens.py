"""ReliabilityLens — assembles classifier + SZZ into a 3-denominator report (RAISE-11490).

Assembles existing primitives:
- raise_cli.quality.classifier: parse_commits, classify, resolve_branch
- raise_cli.telemetry.szz: SzzAttributor, IntroducerResult, confidence_band
- raise_cli.telemetry.defect_attribution: get_attribution_dataset

Does NOT rebuild any of these. Integrates optional TargetClassifier (S11487.3)
for origin/bug_type inference and hotspot Origin×Type building.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from raise_cli.quality.classifier import classify, parse_commits, resolve_branch
from raise_cli.quality.models import CommitRecord, CrossCell
from raise_cli.reliability.cfr import ReleaseBoundary, compute_cfr
from raise_cli.reliability.cohort import build_cohorts
from raise_cli.reliability.deployments import DeploymentEventStore
from raise_cli.reliability.gate_escape import DefectWindow, GateEscapeTracker
from raise_cli.reliability.models import (
    ChangeFailureRate,
    CohortBreakdown,
    ConfidenceSummary,
    Denominator,
    DenominatorValue,
    GateEscapeBreakdown,
    ReliabilityReport,
    Target,
    TargetTally,
)
from raise_cli.reliability.recommendations import RecommendationEngine
from raise_cli.reliability.targets import changed_paths, target_from_paths
from raise_cli.telemetry.defect_attribution import get_attribution_dataset
from raise_cli.telemetry.szz import IntroducerResult, SzzAttributor, confidence_band

if TYPE_CHECKING:
    from raise_cli.reliability.target_classifier import TargetClassifier

__all__ = ["ReliabilityLens"]

_log = logging.getLogger(__name__)


class ReliabilityLens:
    """Assemble classifier + SZZ into a 3-denominator escaped-defect report.

    Usage:
        from pathlib import Path
        from datetime import date
        from raise_cli.reliability.lens import ReliabilityLens

        report = ReliabilityLens().run_backfill(Path("."), since=date(2025, 1, 1))
    """

    def __init__(
        self,
        exclude_patterns: list[str] | None = None,
        classifier: TargetClassifier | None = None,
    ) -> None:
        """Initialise with optional SZZ file-exclusion patterns and optional classifier.

        Args:
            exclude_patterns: Forwarded to SzzAttributor; None → defaults.
            classifier: Optional TargetClassifier for origin/bug_type inference and
                hotspot building. When None, hotspots remains [] (existing behavior).
        """
        self._exclude_patterns = exclude_patterns
        self._classifier = classifier

    def run_backfill(
        self,
        repo_path: Path,
        since: date,
        *,
        branch: str | None = None,
        confidence_threshold: float = 0.6,
        cohort_period: Literal["month", "quarter"] = "month",
        maturity_window_days: int = 90,
        release_tag_pattern: str = "v[0-9]*",
        prod_environment: str = "prod",
    ) -> ReliabilityReport:
        """Build a ReliabilityReport from the full git history since ``since``.

        Args:
            repo_path: Path to the git repository root.
            since: Inclusive start date for the analysis window.
            branch: Override the integration branch (default: manifest dev branch).
            confidence_threshold: Minimum SZZ confidence to include an attribution.
            cohort_period: Vintage cohort bin width ('month' or 'quarter').
            maturity_window_days: Days a cohort must age before it counts as MATURE.
            release_tag_pattern: git tag glob used to find release boundaries for CFR.
            prod_environment: Environment name treated as the production boundary
                for per_deployment and gate-stratified escape.

        Returns:
            ReliabilityReport with all 3 denominators, product rate, target tally,
            confidence summary, and structural None slots for deferred features.
        """
        repo_path = repo_path.resolve()

        # 1. Resolve branch
        resolved_branch, _warning = resolve_branch(repo_path, branch)

        # 2. Parse commits
        today = datetime.now().date()
        since_days = max(1, (today - since).days)
        commits = parse_commits(repo_path, since=since_days, branch=resolved_branch)

        # 3. Classify each commit and partition into escaped product fixes
        # Cache changed_paths per SHA to avoid double subprocess calls.
        szz = SzzAttributor(self._exclude_patterns)
        tally: TargetTally = dict.fromkeys(Target, 0)
        paths_cache: dict[str, list[str]] = {}
        total = len(commits)
        escaped_commits: list[CommitRecord] = []

        for commit in commits:
            verdict = classify(commit)
            paths = changed_paths(repo_path, commit.sha)
            paths_cache[commit.sha] = paths
            target = target_from_paths(paths)
            tally[target] += 1
            if verdict.defect_class == "escaped":
                escaped_commits.append(commit)

        # 4. Optional inference: run classifier over escaped commits to infer
        #    origin and bug_type; build hotspot Origin×Type cross-tabulation.
        hotspots: list[CrossCell] = []
        if self._classifier is not None and escaped_commits:
            hotspots = _run_classifier(
                classifier=self._classifier,
                escaped_commits=escaped_commits,
                repo_path=repo_path,
            )

        # 5. SZZ attribution with confidence filtering
        kept_results: list[IntroducerResult] = []
        excluded_count = 0
        net_new_skipped = 0
        bands_acc: dict[str, int] = {"high": 0, "medium": 0, "low": 0}

        for commit in escaped_commits:
            results = szz.attribute_introducer(commit.sha, repo_path)
            if not results:
                # net-new fix: no introducer found — skip (not drop)
                net_new_skipped += 1
                continue
            for r in results:
                band = confidence_band(r.confidence)
                bands_acc[band] = bands_acc.get(band, 0) + 1
                if r.confidence >= confidence_threshold:
                    kept_results.append(r)
                else:
                    excluded_count += 1

        kept_count = len(kept_results)
        confidence_summary = ConfidenceSummary(
            threshold=confidence_threshold,
            kept=kept_count,
            excluded=excluded_count,
            net_new_skipped=net_new_skipped,
            bands=bands_acc,
        )

        # 6. Compute per_change
        escaped_count = len(escaped_commits)
        per_change = _make_rate(escaped_count, total, "no commits in window")

        # 7. Compute product-only per_change (use cache — no second subprocess)
        product_escaped = sum(
            1
            for c in escaped_commits
            if target_from_paths(paths_cache.get(c.sha, [])) == Target.PRODUCT
        )
        product_escaped_rate = _make_rate(
            product_escaped, total, "no product-target escaped commits"
        )

        # 8. per_defect: try persisted dataset first, then live SZZ set, else None
        per_defect = _compute_per_defect(
            kept_count=kept_count,
            repo_path=repo_path,
        )

        # 9. per_deployment: now grounded on real deploy events (S11487.5).
        #    Proxy (escaped product fixes / prod deploys), NOT DORA per-deployment CFR.
        deploy_store = DeploymentEventStore(
            repo_path, prod_environment=prod_environment
        )
        prod_deploy_dates = deploy_store.prod_deploy_dates(since=since)
        per_deployment = _make_per_deployment(product_escaped, prod_deploy_dates)

        # 10. Assemble confidence_note
        total_szz_attempts = kept_count + excluded_count
        if total_szz_attempts > 0:
            exclusion_pct = excluded_count / total_szz_attempts * 100
            note_pct = f"~{round(exclusion_pct / 5) * 5}%"
        else:
            note_pct = "~0%"
        confidence_note = (
            f"{note_pct} of SZZ attributions excluded (low confidence, "
            f"threshold={confidence_threshold:.2f}) — not a DORA metric."
        )

        # 11. Vintage cohorts (right-censoring) — uses introducer dates of kept
        #     escaped defects against the full change stream.
        change_dates = [c.date.date() for c in commits if c.date is not None]
        introducer_dates = _introducer_dates(
            repo_path, [r.introducer_commit for r in kept_results]
        )
        escaped_introducer_dates = list(introducer_dates.values())
        cohorts: CohortBreakdown | None = build_cohorts(
            change_dates,
            escaped_introducer_dates,
            period_kind=cohort_period,
            as_of=today,
            maturity_window_days=maturity_window_days,
        )

        # 12. CFR release-boundary proxy — uses release tags + escaped product fix dates.
        releases = _release_boundaries(repo_path, release_tag_pattern)
        escaped_product_fix_dates = [
            c.date.date()
            for c in escaped_commits
            if c.date is not None
            and target_from_paths(paths_cache.get(c.sha, [])) == Target.PRODUCT
        ]
        cfr: ChangeFailureRate | None = compute_cfr(
            releases,
            escaped_product_fix_dates,
            as_of=today,
            maturity_window_days=maturity_window_days,
        )

        # 13. Gate-stratified escape (trap 8) — window [introducer, fix] per defect.
        defect_windows = _build_defect_windows(
            kept_results, introducer_dates, escaped_commits
        )
        release_dates = [r.released_at for r in releases]
        gate_escape: GateEscapeBreakdown | None = GateEscapeTracker().stratify(
            defect_windows,
            prod_deploy_dates,
            release_dates,
            prod_environment=prod_environment,
        )

        # 14. Assemble report
        repo_name = repo_path.name
        report = ReliabilityReport(
            escaped_rate={
                Denominator.PER_CHANGE: per_change,
                Denominator.PER_DEPLOYMENT: per_deployment,
                Denominator.PER_DEFECT: per_defect,
            },
            product_escaped_rate=product_escaped_rate,
            target_tally=tally,
            hotspots=hotspots,
            cohorts=cohorts,
            cfr=cfr,
            gate_escape=gate_escape,
            recommendations=[],
            confidence=confidence_summary,
            confidence_note=confidence_note,
            repo=repo_name,
            branch=resolved_branch,
            since=since,
        )

        # 15. Prescriptive recommendations (deterministic rules over the report).
        details = RecommendationEngine().recommend(report)
        report.recommendation_details = details
        report.recommendations = [r.message for r in details]
        return report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_defect_windows(
    kept_results: list[IntroducerResult],
    introducer_dates: dict[str, date],
    escaped_commits: list[CommitRecord],
) -> list[DefectWindow]:
    """Build [introducer, fix] windows for gate stratification.

    Skips defects whose introducer date or fix date could not be resolved (partial
    git failure) — consistent with the cohort numerator's degradation.
    """
    fix_dates = {c.sha: c.date.date() for c in escaped_commits if c.date is not None}
    windows: list[DefectWindow] = []
    for r in kept_results:
        introduced = introducer_dates.get(r.introducer_commit)
        discovered = fix_dates.get(r.fix_commit)
        if introduced is None or discovered is None:
            continue
        windows.append(
            DefectWindow(
                bug_key=r.bug_key or r.fix_commit,
                introduced=introduced,
                discovered=discovered,
            )
        )
    return windows


_PER_DEPLOYMENT_PROXY_REASON = (
    "proxy: escaped product fixes / production deploys — NOT the DORA per-deployment "
    "Change Failure Rate (no deploy-failure classification yet; follow-up)"
)


def _make_per_deployment(
    product_escaped: int, prod_deploy_dates: list[date]
) -> DenominatorValue:
    """per_deployment proxy = escaped product fixes / production deploys.

    None+reason when there are no deploy events (production boundary unknown,
    trap 4) — never an invented denominator.
    """
    n_deploys = len(prod_deploy_dates)
    if n_deploys == 0:
        return DenominatorValue(
            value=None,
            numerator=product_escaped,
            reason=(
                "insufficient: no deployment events — register deploys with "
                "`rai reliability deploy register` to ground per-deployment"
            ),
        )
    return DenominatorValue(
        value=product_escaped / n_deploys,
        numerator=product_escaped,
        denominator=n_deploys,
        reason=_PER_DEPLOYMENT_PROXY_REASON,
    )


def _make_rate(numerator: int, denominator: int, empty_reason: str) -> DenominatorValue:
    """Build a DenominatorValue from a numerator/denominator pair.

    Returns None+reason only when the denominator is 0. A 0 numerator over a
    non-zero denominator is a real 0.0 rate, not an empty slot.
    """
    if denominator == 0:
        return DenominatorValue(value=None, reason=f"insufficient: {empty_reason}")
    return DenominatorValue(
        value=numerator / denominator,
        numerator=numerator,
        denominator=denominator,
        reason=None,
    )


_PER_DEFECT_NO_DATASET_REASON = (
    "insufficient: no persisted defect dataset — per-defect requires a real defect "
    "universe (filed/triaged defects), not the SZZ-kept set. "
    "Live-SZZ fallback would force numerator==denominator==1.0 by construction. "
    "Run `rai reliability` after defect attributions are persisted to raise.db."
)

_PER_DEFECT_DATASET_NO_ESCAPED_SIGNAL_REASON = (
    "insufficient: persisted dataset has no escaped signal — "
    "authoring_condition classifies who authored the introducer, not whether "
    "the defect escaped. Per-defect requires an explicit escaped flag on "
    "attribution records (deferred to S11487.4)."
)


def _compute_per_defect(
    *,
    kept_count: int,
    repo_path: Path,
) -> DenominatorValue:
    """Compute per_defect denominator.

    Strategy:
    1. Try persisted attribution dataset from raise.db.
       - The dataset path requires an explicit escaped signal; authoring_condition
         is NOT a proxy for escaped (AR finding M2). Until S11487.4 adds an
         escaped flag to AttributionRecord, this path also yields None+reason.
    2. If no persisted dataset: the live-SZZ fallback would force
       numerator==denominator (kept_count==kept_count → 1.0 by construction),
       which is a definitional artifact, not an honest rate (AR finding M1).
       Emit None+reason instead.
    3. If no SZZ results at all → None with reason.

    The per_defect denominator is the total attributable defect count (unique
    bug-introducing commits). This is a different denominator than the commit
    stream total.
    """
    persisted = get_attribution_dataset(project_root=repo_path)

    if persisted:
        # Dataset exists but lacks an explicit escaped signal.
        # authoring_condition classifies who authored the introducer, not
        # whether the defect escaped — using it as an escaped proxy is a
        # category error (AR M2). Return None+reason until S11487.4 adds
        # an escaped flag.
        return DenominatorValue(
            value=None,
            reason=_PER_DEFECT_DATASET_NO_ESCAPED_SIGNAL_REASON,
        )

    if kept_count > 0:
        # Live-SZZ fallback: the kept set IS the escaped set by construction
        # (we only have SZZ results for escaped fix commits). Setting
        # numerator==denominator==kept_count yields 1.0 definitionally — not
        # an honest rate (AR M1). Disclose honestly.
        return DenominatorValue(
            value=None,
            reason=_PER_DEFECT_NO_DATASET_REASON,
        )

    # No data at all
    return DenominatorValue(
        value=None,
        reason="insufficient: no attributable defects found",
    )


def _introducer_dates(repo_path: Path, shas: list[str]) -> dict[str, date]:
    """Resolve commit dates for a set of introducer SHAs via one ``git log`` call.

    Returns a mapping sha → AUTHOR date (when the code was written — the vintage
    basis; ``%aI`` not ``%cI``, so a rebased/cherry-picked introducer keeps its
    original write date and lands in the correct cohort). The date is the author's
    LOCAL calendar day (the offset in ``%aI`` is honoured by ``fromisoformat`` and
    dropped by ``.date()``); this matches ``parse_commits`` (also ``%aI``) so the
    cohort numerator and denominator share one basis. A commit near local midnight
    may shift ±1 day across a month/quarter boundary — accepted.

    Failures (bad SHA, not a repo, timeout) degrade to an empty mapping. NOTE:
    when this returns FEWER dates than ``shas`` (partial git failure, malformed
    lines), the lost introducers silently drop out of the cohort numerator — see
    RAISE follow-up for numerator/denominator reconciliation disclosure.
    """
    import subprocess

    unique = sorted({s for s in shas if s})
    if not unique:
        return {}

    try:
        result = subprocess.run(
            ["git", "log", "--no-walk", "--format=%H %aI", *unique],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {}
    if result.returncode != 0:
        return {}

    dates: dict[str, date] = {}
    for line in result.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        sha, iso = parts
        try:
            dates[sha] = datetime.fromisoformat(iso).date()
        except ValueError:
            continue
    return dates


def _release_boundaries(repo_path: Path, pattern: str) -> list[ReleaseBoundary]:
    """Resolve release tags matching ``pattern`` into ReleaseBoundary objects.

    Uses ``git tag --list <pattern>`` with creatordate. Failures degrade to an
    empty list — compute_cfr then returns a None+reason rate honestly.
    """
    import subprocess

    try:
        result = subprocess.run(
            [
                "git",
                "tag",
                "--list",
                pattern,
                "--format=%(refname:short)|%(creatordate:short)",
            ],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    if result.returncode != 0:
        return []

    boundaries: list[ReleaseBoundary] = []
    for line in result.stdout.splitlines():
        tag, _, datestr = line.partition("|")
        if not tag or not datestr:
            continue
        try:
            released = date.fromisoformat(datestr.strip())
        except ValueError:
            continue
        boundaries.append(ReleaseBoundary(tag=tag.strip(), released_at=released))
    return boundaries


def _get_commit_diff(repo_path: Path, sha: str) -> str:
    """Get the unified diff for a single commit via ``git diff-tree`` (AR R3).

    Args:
        repo_path: Absolute path to the git repository root.
        sha: Commit SHA (40-char hex).

    Returns:
        Unified diff string, or empty string on error (non-existent SHA,
        not a git repo, timeout, etc.).  Failures are non-fatal.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "-p", sha],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        pass
    return ""


def _run_classifier(
    *,
    classifier: TargetClassifier,
    escaped_commits: list[CommitRecord],
    repo_path: Path,
) -> list[CrossCell]:
    """Run TargetClassifier over escaped commits and build Origin×Type hotspots.

    AR R3 fix: calls classify() per commit with the actual per-commit diff
    obtained via ``git diff-tree``.  Title-only signal caused origin to collapse
    to "Code" because the Design-vs-Code dimension requires reading the diff.

    Wrapped in try/except so classifier failures degrade gracefully — lens
    returns an empty hotspots list rather than crashing the whole report.

    Args:
        classifier: Instantiated TargetClassifier.
        escaped_commits: Commits classified as escaped fixes.
        repo_path: Repository root for ``git diff-tree`` subprocess calls.

    Returns:
        List of CrossCell (Origin×Type counts) from classified escaped commits.
    """
    from raise_cli.reliability.classification_models import BugRecord

    try:
        # AR R3: call classify() per commit with per-commit diff
        cross: dict[tuple[str, str], int] = {}
        for c in escaped_commits:
            diff = _get_commit_diff(repo_path, c.sha)
            bug = BugRecord(key=c.sha, title=c.subject or c.sha)
            tc = classifier.classify(bug, fix_diff=diff, commit=c.subject or "")
            key = (tc.origin, tc.bug_type)
            cross[key] = cross.get(key, 0) + 1

        return [
            CrossCell(origin=origin, type=bug_type, fix_bug_count=count)
            for (origin, bug_type), count in sorted(cross.items())
        ]

    except Exception as exc:  # noqa: BLE001
        _log.warning(
            "TargetClassifier.classify failed — hotspots will be empty: %s", exc
        )
        return []
