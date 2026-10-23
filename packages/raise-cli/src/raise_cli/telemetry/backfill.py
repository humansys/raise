"""Backfill token usage from CC JSONL conversation files.

Scans ~/.claude/projects/ for JSONL files, extracts full token usage
(including cache metrics missing from early emissions), and emits
token_usage_daily events to raise-server.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from raise_cli.telemetry.session_tokens import SessionTokenTotals, parse_totals


class BackfillEntry(BaseModel):
    """One CC session's extracted token data, ready to emit."""

    jsonl_path: str
    session_id: str
    date: str
    repo_slug: str
    totals: SessionTokenTotals


def _extract_session_date(jsonl_path: Path) -> str | None:
    """Extract the date of the first assistant message in a JSONL."""
    for raw in jsonl_path.open(encoding="utf-8", errors="replace"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj: Any = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or obj.get("type") != "assistant":
            continue
        ts = obj.get("timestamp")
        if isinstance(ts, str) and len(ts) >= 10:
            return ts[:10]
    return None


def repo_slug_from_project_dir(
    project_dir_name: str,
    known_repos: frozenset[str] | None = None,
) -> str | None:
    """Infer repo slug from CC project directory name.

    CC encodes paths replacing '/' and '.' with '-':
    - Direct: '-home-user-Code-raise-commons' → 'raise-commons'
    - Worktree (double-dash): '-home-user-Code-raise-commons--worktree-...' → 'raise-commons'
    - Worktree (dot-encoded): '-home-user-Code-raise-commons-epic-e4835-...'
      → matched against known_repos to extract 'raise-commons'
    """
    parts = project_dir_name.split("-")
    try:
        code_idx = parts.index("Code")
    except ValueError:
        return None
    rest = parts[code_idx + 1 :]
    repo_parts: list[str] = []
    for p in rest:
        if p == "":
            break
        repo_parts.append(p)
    candidate = "-".join(repo_parts) if repo_parts else None
    if candidate is None:
        return None

    if known_repos and candidate not in known_repos:
        for repo in sorted(known_repos, key=len, reverse=True):
            if candidate.startswith(repo + "-"):
                return repo

    return candidate


def _discover_known_repos(project_dirs: list[Path]) -> frozenset[str]:
    """Build the set of base repo slugs (shortest unique prefixes)."""
    all_slugs: list[str] = []
    for d in project_dirs:
        slug = repo_slug_from_project_dir(d.name)
        if slug:
            all_slugs.append(slug)
    all_slugs.sort(key=len)
    base_repos: set[str] = set()
    for slug in all_slugs:
        if not any(slug.startswith(r + "-") for r in base_repos):
            base_repos.add(slug)
    return frozenset(base_repos)


def _parse_session_entry(
    jsonl: Path, repo_slug: str, since: str | None
) -> BackfillEntry | None:
    """Parse a single JSONL into a BackfillEntry, or None if skipped."""
    if jsonl.stat().st_size == 0:
        return None
    totals = parse_totals(jsonl)
    if totals is None or totals.message_count == 0:
        return None
    date = _extract_session_date(jsonl) or datetime.now(UTC).strftime("%Y-%m-%d")
    if since and date < since:
        return None
    return BackfillEntry(
        jsonl_path=str(jsonl),
        session_id=jsonl.stem,
        date=date,
        repo_slug=repo_slug,
        totals=totals,
    )


def scan_cc_sessions(
    *,
    repo_filter: str | None = None,
    since: str | None = None,
) -> list[BackfillEntry]:
    """Scan all CC JSONL files and extract token totals.

    Args:
        repo_filter: Only include sessions from this repo slug.
        since: Only include sessions on or after this date (YYYY-MM-DD).
    """
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return []

    project_dirs = sorted(d for d in base.iterdir() if d.is_dir())
    known_repos = _discover_known_repos(project_dirs)

    entries: list[BackfillEntry] = []
    for project_dir in project_dirs:
        repo_slug = repo_slug_from_project_dir(project_dir.name, known_repos)
        if repo_slug is None:
            continue
        if repo_filter and repo_slug != repo_filter:
            continue
        for jsonl in sorted(project_dir.glob("*.jsonl")):
            entry = _parse_session_entry(jsonl, repo_slug, since)
            if entry is not None:
                entries.append(entry)

    return entries


def build_backfill_events(
    entries: list[BackfillEntry],
    *,
    work_item_ref: str | None = None,
) -> list[dict[str, Any]]:
    """Convert BackfillEntry list into AgentEventCreate dicts for server POST."""
    from raise_cli.telemetry.session_tokens import build_token_usage_daily_event

    events: list[dict[str, Any]] = []
    for entry in entries:
        event = build_token_usage_daily_event(
            entry.totals,
            session_id=entry.session_id,
            work_item_ref=work_item_ref,
            date=entry.date,
            repo_slug=entry.repo_slug,
        )
        events.append(event.model_dump())
    return events


def build_enriched_report(
    *,
    repo_filter: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> dict[str, Any]:
    """Run build_report over CC JSONL and return enriched payload for server.

    Returns a dict with cost, phases, skills, categories, rubber-stamp data
    ready to POST as a token_usage_daily event payload.
    """
    from datetime import datetime as dt

    from raise_cli.telemetry.cost_report import build_report

    base = Path.home() / ".claude" / "projects"
    since_dt = dt.fromisoformat(since).astimezone() if since else None
    until_dt = dt.fromisoformat(until).astimezone() if until else None

    report = build_report(projects_dir=base, since=since_dt, until=until_dt)

    return {
        "total_cost_usd": report.total_cost_usd,
        "stories_completed": report.stories_completed,
        "cost_per_story": report.cost_per_story,
        "models": [m.model_dump() for m in report.models],
        "skills": [s.model_dump() for s in report.skills],
        "phases": [p.model_dump() for p in report.phases],
        "categories": report.categories,
        "approvals_total": report.approvals_total,
        "approvals_with_edits": report.approvals_with_edits,
        "rubber_stamp_rate": report.rubber_stamp_rate,
        "repo_filter": repo_filter,
        "since": since,
        "until": until,
    }
