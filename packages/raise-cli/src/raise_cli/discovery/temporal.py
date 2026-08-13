"""Temporal ingestion + snapshot/delta for drift detection (S2162.3).

Computes Tufano slope-ratio and Palomba HIST co-change from git history.
Persists results as JSON snapshots under .raise/drift/temporal/.
No graph writes, no LLM, no numpy. ADR-E2162-2 compliant.
"""

from __future__ import annotations

import logging
import subprocess
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config + Report models (T1)
# ---------------------------------------------------------------------------


class TemporalConfig(BaseModel):
    """Configuration for temporal ingestion (window, co-change threshold, cache location)."""

    window_days: int = 180
    min_co_change_support: int = 2
    cache_dir: Path = Path(".raise/drift/temporal")


class TemporalReport(BaseModel):
    """Per-module temporal health report: Tufano slope + Palomba HIST co-change. Schema v1 additive-only."""

    schema_version: int = Field(default=1)
    module_id: str
    loc_slope: float
    churn_total: int
    co_change_partners: list[tuple[str, int]]
    first_seen: str
    last_seen: str
    snapshot_head: str
    window_days: int
    computed_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def module_id_to_slug(module_id: str) -> str:
    """Convert a module path to a filesystem-safe slug for cache file naming."""
    return module_id.replace("/", "-").replace(".", "-").replace("_", "-")


def _parse_log_lines(output: str) -> list[tuple[str, str]]:
    """Parse 'git log --format=%H|%aI' output into [(sha, iso_timestamp)], oldest-first."""
    result: list[tuple[str, str]] = []
    for line in reversed(output.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = line.split("|", maxsplit=1)
        if len(parts) == 2:  # noqa: PLR2004
            result.append((parts[0], parts[1]))
    return result


def _linear_slope(points: list[tuple[float, float]]) -> float:
    """OLS slope. Returns 0.0 for < 2 points."""
    n = len(points)
    if n < 2:  # noqa: PLR2004
        return 0.0
    sum_x = sum(x for x, _ in points)
    sum_y = sum(y for _, y in points)
    sum_xy = sum(x * y for x, y in points)
    sum_x2 = sum(x * x for x, _ in points)
    denom = n * sum_x2 - sum_x**2
    return (n * sum_xy - sum_x * sum_y) / denom if denom else 0.0


# ---------------------------------------------------------------------------
# TemporalIngester (T2-T4): git subprocess wrappers as instance methods
# PAT-E-709: instance methods enable clean patch.object() in tests
# ---------------------------------------------------------------------------


class TemporalIngester:
    """Computes temporal metrics for a module from git history.

    Args:
        repo_root: Path to the git repository root.
        cfg:       Temporal configuration (window, thresholds, cache dir).
        now_fn:    Optional callable returning current UTC datetime (for tests).
    """

    def __init__(
        self,
        repo_root: Path,
        cfg: TemporalConfig,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._repo_root = repo_root
        self._cfg = cfg
        self._now_fn: Callable[[], datetime] = now_fn or (lambda: datetime.now(tz=UTC))

    # ------------------------------------------------------------------
    # T2 — Git helpers
    # ------------------------------------------------------------------

    def _run_git(self, cmd: list[str]) -> str:
        """Run a git command and return stdout.

        PAT-E-979: omit cwd when paths are already repo-root-relative;
        git auto-finds the repo root.
        """
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=self._repo_root,
        )
        return result.stdout

    def get_head(self) -> str:
        """Return current git HEAD SHA (stripped)."""
        return self._run_git(["git", "rev-parse", "HEAD"]).strip()

    def _get_commits_for_module(
        self, module_path: Path, since_days: int
    ) -> list[tuple[str, str]]:
        """Return [(sha, iso_timestamp)] for commits touching module_path within window.

        Commits are ordered oldest-first (chronological).
        """
        since_date = (datetime.now(tz=UTC) - timedelta(days=since_days)).date()
        output = self._run_git(
            [
                "git",
                "log",
                "--format=%H|%aI",
                f"--after={since_date.isoformat()}",
                "--",
                str(module_path),
            ]
        )
        return _parse_log_lines(output)

    # ------------------------------------------------------------------
    # T3 — LOC delta + Tufano slope
    # ------------------------------------------------------------------

    def _get_loc_delta(self, sha: str, module_path: Path) -> int:
        """Return net LOC change (additions - deletions) for sha touching module_path."""
        output = self._run_git(
            [
                "git",
                "diff-tree",
                "--numstat",
                "--no-commit-id",
                "-r",
                sha,
                "--",
                str(module_path),
            ]
        )
        total = 0
        for line in output.strip().splitlines():
            parts = line.split("\t", maxsplit=2)
            if len(parts) < 2:  # noqa: PLR2004
                continue
            try:
                additions = int(parts[0])
                deletions = int(parts[1])
                total += additions - deletions
            except ValueError:
                continue
        return total

    def _compute_loc_slope(
        self, commits: list[tuple[str, str]], module_path: Path
    ) -> float:
        """Compute Tufano slope: OLS regression of running LOC over unix timestamps."""
        if not commits:
            return 0.0
        running_loc = 0
        points: list[tuple[float, float]] = []
        for sha, iso_ts in commits:
            delta = self._get_loc_delta(sha, module_path)
            running_loc = max(0, running_loc + delta)
            try:
                ts = datetime.fromisoformat(iso_ts).timestamp()
            except ValueError:
                continue
            points.append((ts, float(running_loc)))
        return _linear_slope(points)

    # ------------------------------------------------------------------
    # T4 — HIST co-change
    # ------------------------------------------------------------------

    def _get_changed_files_in_commit(self, sha: str) -> list[str]:
        """Return list of files changed in this commit."""
        output = self._run_git(
            [
                "git",
                "diff-tree",
                "--no-commit-id",
                "-r",
                "--name-only",
                sha,
            ]
        )
        return [line.strip() for line in output.strip().splitlines() if line.strip()]

    def _compute_co_change_partners(
        self,
        commits: list[tuple[str, str]],
        module_path: Path,
    ) -> list[tuple[str, int]]:
        """Palomba HIST: count co-occurring files filtered by min_co_change_support."""
        target = str(module_path)
        counter: Counter[str] = Counter()
        for sha, _ in commits:
            changed = self._get_changed_files_in_commit(sha)
            others = [f for f in changed if f != target]
            for f in others:
                counter[f] += 1
        result = [
            (f, count)
            for f, count in counter.items()
            if count >= self._cfg.min_co_change_support
        ]
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    # ------------------------------------------------------------------
    # T5 — snapshot + delta
    # ------------------------------------------------------------------

    def compute(self, module_path: Path) -> TemporalReport:
        """Compute full TemporalReport for module_path from scratch."""
        commits = self._get_commits_for_module(module_path, self._cfg.window_days)
        head = self.get_head()
        loc_slope = self._compute_loc_slope(commits, module_path)
        co_change_partners = self._compute_co_change_partners(commits, module_path)
        now = self._now_fn().isoformat()
        first_seen = commits[0][1] if commits else now
        last_seen = commits[-1][1] if commits else now
        return TemporalReport(
            module_id=str(module_path),
            loc_slope=loc_slope,
            churn_total=len(commits),
            co_change_partners=co_change_partners,
            first_seen=first_seen,
            last_seen=last_seen,
            snapshot_head=head,
            window_days=self._cfg.window_days,
            computed_at=now,
        )

    def compute_delta(
        self, existing: TemporalReport, module_path: Path
    ) -> TemporalReport:
        """Compute delta from existing.snapshot_head to current HEAD, merge results."""
        head = self.get_head()
        output = self._run_git(
            [
                "git",
                "log",
                "--format=%H|%aI",
                f"{existing.snapshot_head}..HEAD",
                "--",
                str(module_path),
            ]
        )
        new_commits = _parse_log_lines(output)

        if not new_commits:
            return TemporalReport(
                module_id=existing.module_id,
                loc_slope=existing.loc_slope,
                churn_total=existing.churn_total,
                co_change_partners=existing.co_change_partners,
                first_seen=existing.first_seen,
                last_seen=existing.last_seen,
                snapshot_head=head,
                window_days=existing.window_days,
                computed_at=existing.computed_at,
            )

        # Rebuild full commit list for slope recomputation (slope is not additive)
        all_commits = self._get_commits_for_module(module_path, self._cfg.window_days)
        loc_slope = self._compute_loc_slope(all_commits, module_path)

        # Merge co-change: re-run on full window
        co_change_partners = self._compute_co_change_partners(all_commits, module_path)

        now = self._now_fn().isoformat()
        last_seen = all_commits[-1][1] if all_commits else existing.last_seen
        return TemporalReport(
            module_id=existing.module_id,
            loc_slope=loc_slope,
            churn_total=len(all_commits),
            co_change_partners=co_change_partners,
            first_seen=existing.first_seen,
            last_seen=last_seen,
            snapshot_head=head,
            window_days=self._cfg.window_days,
            computed_at=now,
        )


# ---------------------------------------------------------------------------
# Public API (T5)
# ---------------------------------------------------------------------------


def snapshot(
    module_path: Path,
    repo_root: Path,
    cfg: TemporalConfig | None = None,
    *,
    now_fn: Callable[[], datetime] | None = None,
) -> TemporalReport:
    """Compute or load cached TemporalReport for module_path.

    Returns cached report when snapshot_head matches current HEAD.
    Computes delta when HEAD has advanced. Computes from scratch otherwise.

    Args:
        module_path: Path to the module file (repo-root-relative).
        repo_root:   Path to the git repository root.
        cfg:         TemporalConfig (uses defaults if None).
        now_fn:      Optional datetime supplier for deterministic tests.
    """
    if cfg is None:
        cfg = TemporalConfig()

    ingester = TemporalIngester(repo_root, cfg, now_fn=now_fn)
    head = ingester.get_head()

    module_id = str(module_path)
    slug = module_id_to_slug(module_id)
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cfg.cache_dir / f"{slug}.json"

    if cache_file.exists():
        try:
            cached = TemporalReport.model_validate_json(
                cache_file.read_text(encoding="utf-8")
            )
            if cached.snapshot_head == head and cached.window_days == cfg.window_days:
                return cached
            if cached.window_days != cfg.window_days:
                report = ingester.compute(module_path)
            else:
                report = ingester.compute_delta(cached, module_path)
        except (ValueError, KeyError) as exc:
            logger.debug("Cache invalid (%s), recomputing", exc)
            report = ingester.compute(module_path)
    else:
        report = ingester.compute(module_path)

    cache_file.write_text(report.model_dump_json(), encoding="utf-8")
    return report


def delta_update(
    existing: TemporalReport,
    module_path: Path,
    repo_root: Path,
    cfg: TemporalConfig | None = None,
    *,
    now_fn: Callable[[], datetime] | None = None,
) -> TemporalReport:
    """Compute delta from existing report to current HEAD and persist."""
    if cfg is None:
        cfg = TemporalConfig()
    ingester = TemporalIngester(repo_root, cfg, now_fn=now_fn)
    report = ingester.compute_delta(existing, module_path)
    slug = module_id_to_slug(existing.module_id)
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cfg.cache_dir / f"{slug}.json"
    cache_file.write_text(report.model_dump_json(), encoding="utf-8")
    return report
