"""Commit-stream defect/rework classifier (RAISE-11187).

Self-contained: depends only on stdlib + ``raise_cli`` config helpers. Does NOT
import ``raise_cli.scm`` (that lives on an unmerged branch). Productionizes the
discovery logic from ``dev-prototype-classify.py``.

The integration branch is resolved from ``.raise/manifest.yaml``
(``branches.development``), never hardcoded — org calibration matters. On a
fresh clone whose local ``main`` lags, ``main`` yields a false-negative (~0
signal); the real fix/rework stream lives on the development branch
(``release/3.1.0`` here). Reading the manifest avoids analysing the wrong ref.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

from raise_cli.onboarding.manifest import load_manifest
from raise_cli.quality.models import (
    CommitCategory,
    CommitClassification,
    CommitRecord,
    DefectClass,
    DefectRateReport,
    WindowMetrics,
)

# Conventional-commit prefix: type(scope)?(!)?:
_PREFIX_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]*)\))?!?:\s*(?P<rest>.*)$")

# Ticket references: RAISE-1234, story s11126.6 / S-1234, epic e-foo / E10328.
_TICKET_RE = re.compile(
    r"RAISE-\d+|\b[sSeE]-?\d{3,}(?:\.\d+)*\b|\(e-[a-z0-9-]+\)", re.IGNORECASE
)

# Fix-intent detection for commits that lack a clean conventional prefix.
_FIX_INTENT_RE = re.compile(
    r"\b(fix|fixup|hotfix|repair|correct|typo|address review|review comment|"
    r"pre-?commit|gate fail|ci fail)\b",
    re.IGNORECASE,
)

# In-process rework markers: review remediation + CI/gate/quality churn.
_REWORK_MARKER_RE = re.compile(
    r"\b(AR-\d+|QR-\d+|architecture.?review|quality.?review|reaper|review|"
    r"ci|lint|gate|format|pre-?commit|pyright|ruff|mypy|type[sd]?)\b",
    re.IGNORECASE,
)

# git log record separator (unlikely to appear in commit text).
_FIELD_SEP = "\x1f"
_RECORD_SEP = "\x1e"
_PRETTY = f"%H{_FIELD_SEP}%an{_FIELD_SEP}%aI{_FIELD_SEP}%s{_RECORD_SEP}"

# Map conventional-commit type aliases onto our category vocabulary.
_TYPE_MAP: dict[str, CommitCategory] = {
    "feat": "feat",
    "feature": "feat",
    "fix": "fix",
    "bugfix": "fix",
    "bug": "bug",
    "test": "test",
    "tests": "test",
    "docs": "docs",
    "doc": "docs",
    "chore": "chore",
    "build": "chore",
    "ci": "chore",
    "refactor": "chore",
    "style": "chore",
    "perf": "chore",
}

_VALID_CATEGORIES = {"feat", "fix", "bug", "test", "docs", "chore", "other"}


def resolve_branch(
    repo_path: Path, override: str | None = None
) -> tuple[str, str | None]:
    """Resolve the integration branch for analysis.

    Precedence: explicit ``override`` > manifest ``branches.development`` >
    current branch (with a warning).

    Args:
        repo_path: Path inside the git repository.
        override: Explicit branch from the caller (e.g. ``--branch``).

    Returns:
        ``(branch, warning)`` where ``warning`` is ``None`` unless we fell back
        to the current branch because no manifest/development branch was found.
    """
    if override:
        return override, None

    manifest = load_manifest(repo_path)
    if manifest is not None and manifest.branches.development:
        return manifest.branches.development, None

    current = _current_branch(repo_path)
    warning = (
        "No .raise/manifest.yaml branches.development found; "
        f"falling back to current branch '{current}'. "
        "Org calibration disabled — results may be a false signal."
    )
    return current, warning


def _current_branch(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "HEAD"


def parse_commits(repo_path: Path, since: int, branch: str) -> list[CommitRecord]:
    """Parse the commit stream via ``git log`` into typed records.

    Args:
        repo_path: Path inside the git repository.
        since: Look back this many days.
        branch: Ref to read (e.g. ``release/3.1.0``).

    Returns:
        Commit records (no merge commits), newest first.
    """
    result = subprocess.run(
        [
            "git",
            "log",
            branch,
            f"--since={since} days ago",
            "--no-merges",
            f"--pretty=format:{_PRETTY}",
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    return parse_git_log(result.stdout)


def parse_git_log(raw: str) -> list[CommitRecord]:
    """Parse raw ``git log`` output (custom pretty format) into records.

    Split out from :func:`parse_commits` so tests can feed a recorded fixture
    without spawning git.
    """
    records: list[CommitRecord] = []
    for chunk in raw.split(_RECORD_SEP):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        fields = chunk.split(_FIELD_SEP)
        if len(fields) != 4:
            continue
        sha, author, date_str, subject = fields
        records.append(_record_from_fields(sha, author, date_str, subject))
    return records


def _record_from_fields(
    sha: str, author: str, date_str: str, subject: str
) -> CommitRecord:
    category, scope = _parse_prefix(subject)
    date = _parse_date(date_str)
    refs = sorted({m.group(0) for m in _TICKET_RE.finditer(subject)})
    return CommitRecord(
        sha=sha.strip(),
        type=category,
        scope=scope,
        subject=subject.strip(),
        ticket_refs=refs,
        author=author.strip(),
        date=date,
    )


def _parse_prefix(subject: str) -> tuple[CommitCategory, str | None]:
    match = _PREFIX_RE.match(subject.strip())
    if not match:
        # No conventional prefix — infer fix-intent, else "other".
        if _FIX_INTENT_RE.search(subject):
            return "fix", None
        return "other", None
    raw_type = match.group("type").lower()
    scope = match.group("scope")
    category: CommitCategory = _TYPE_MAP.get(raw_type, "other")
    return category, scope.strip() if scope else None


def _parse_date(date_str: str) -> datetime | None:
    date_str = date_str.strip()
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


def classify(commit: CommitRecord) -> CommitClassification:
    """Classify one commit (category, traceability, defect class).

    Heuristic defect logic for fix/bug commits:
      - has in-process rework marker (AR/QR/CI/gate/lint/type/review)
        -> ``rework_in_process``
      - no in-process marker -> ``escaped`` (candidate escaped defect)
    Non-fix commits are ``n/a``.
    """
    category: CommitCategory = (
        commit.type if commit.type in _VALID_CATEGORIES else "other"
    )
    traceable = bool(commit.ticket_refs) or bool(commit.scope)

    defect_class: DefectClass
    if category not in {"fix", "bug"}:
        defect_class = "n/a"
    elif _REWORK_MARKER_RE.search(commit.subject):
        defect_class = "rework_in_process"
    else:
        defect_class = "escaped"

    return CommitClassification(
        category=category,
        traceable=traceable,
        defect_class=defect_class,
    )


def defect_rate(
    commits: list[CommitRecord],
    branch: str,
    since_days: int,
    window_days: int = 30,
) -> DefectRateReport:
    """Aggregate defect/rework metrics over the commit stream.

    Args:
        commits: Parsed commit records.
        branch: Branch the records came from (for the report header).
        since_days: Look-back used to produce ``commits`` (report header).
        window_days: Bucket size, in days, for the by-window breakdown.
            Must be >= 1.

    Raises:
        ValueError: If ``window_days`` < 1.

    Returns:
        A report with overall metrics plus per-window buckets (newest first).
    """
    if window_days < 1:
        msg = f"window_days must be >= 1, got {window_days}"
        raise ValueError(msg)
    overall = WindowMetrics(label=f"all ({since_days}d)")
    buckets: dict[str, WindowMetrics] = {}
    now = datetime.now().astimezone()

    for commit in commits:
        verdict = classify(commit)
        _accumulate(overall, verdict)

        label = _window_label(commit.date, now, window_days)
        bucket = buckets.get(label)
        if bucket is None:
            bucket = WindowMetrics(label=label)
            buckets[label] = bucket
        _accumulate(bucket, verdict)

    windows = sorted(buckets.values(), key=lambda w: w.label, reverse=True)
    return DefectRateReport(
        branch=branch,
        since_days=since_days,
        overall=overall,
        windows=windows,
    )


def _accumulate(metrics: WindowMetrics, verdict: CommitClassification) -> None:
    metrics.total += 1
    if verdict.category == "fix":
        metrics.fix_count += 1
    elif verdict.category == "bug":
        metrics.bug_count += 1
    if verdict.defect_class == "rework_in_process":
        metrics.rework_count += 1
    elif verdict.defect_class == "escaped":
        metrics.escaped_count += 1


def _window_label(date: datetime | None, now: datetime, window_days: int) -> str:
    """Bucket a commit into an N-day window ending now (e.g. ``0-30d ago``)."""
    if date is None:
        return "undated"
    delta_days = (now - date).days
    delta_days = max(delta_days, 0)
    bucket_index = delta_days // window_days
    start = bucket_index * window_days
    end = start + window_days
    return f"{start:03d}-{end:03d}d ago"
