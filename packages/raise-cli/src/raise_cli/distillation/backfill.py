"""Heuristic backfill of historical Claude Code session JSONLs into distillation_runs."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path


def enumerate_jsonls(
    *,
    since: str | None = None,
    limit: int | None = None,
) -> list[Path]:
    """Return JSONL paths from ~/.claude/projects/, optionally filtered by mtime."""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return []

    paths = sorted(
        projects_dir.glob("**/*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if since:
        cutoff = datetime.fromisoformat(since).replace(tzinfo=UTC).timestamp()
        paths = [p for p in paths if p.stat().st_mtime >= cutoff]

    if limit is not None:
        paths = paths[:limit]

    return paths


def _project_name_from_path(path: Path) -> str:
    """Extract project identifier from ~/.claude/projects/{hash}/{session}.jsonl."""
    parts = path.parts
    try:
        idx = parts.index(".claude")
        if idx + 2 < len(parts):
            return parts[idx + 2]
    except ValueError:
        pass
    return path.parent.name


def backfill_session(
    conn: sqlite3.Connection,
    path: Path,
    *,
    dry_run: bool = False,
) -> dict[str, int] | None:
    """Parse and classify a single JSONL; persist to distillation_runs unless dry_run.

    Returns a dict with signal counts, or None on parse error.
    """
    from raise_cli.distillation.classifier import TurnClass, classify_turn
    from raise_cli.distillation.parser import parse_session_jsonl
    from raise_cli.distillation.storage import DistillationRun, persist_run

    try:
        records = parse_session_jsonl(path)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None

    if not records:
        return None

    classes = [classify_turn(r) for r in records]

    decisions = sum(1 for c in classes if c == TurnClass.DECISION)
    corrections = sum(1 for c in classes if c == TurnClass.CORRECTION)
    patterns = sum(1 for c in classes if c == TurnClass.INSIGHT)
    blockers = sum(1 for c in classes if c == TurnClass.BLOCKER)
    tool_use = sum(1 for c in classes if c == TurnClass.TOOL_USE)

    counts = {
        "turns": len(records),
        "decisions": decisions,
        "corrections": corrections,
        "patterns": patterns,
        "blockers": blockers,
        "tool_use": tool_use,
    }

    if not dry_run:
        mtime = path.stat().st_mtime
        date = datetime.fromtimestamp(mtime, tz=UTC).strftime("%Y-%m-%d")
        project = _project_name_from_path(path)
        run = DistillationRun(
            session_id=path.stem,
            date=date,
            project=project,
            runtime="claude-code",
            turns_total=len(records),
            decisions_count=decisions,
            corrections_count=corrections,
            patterns_count=patterns,
            blockers_count=blockers,
            tool_use_count=tool_use,
        )
        persist_run(conn, run)

    return counts


def generate_report(
    results: list[tuple[Path, dict[str, int]]],
    *,
    dry_run: bool = False,
) -> str:
    """Build a Markdown summary report from backfill results."""
    total = len(results)
    totals: dict[str, int] = defaultdict(int)
    for _, counts in results:
        for k, v in counts.items():
            totals[k] += v

    mode = "DRY RUN (not persisted)" if dry_run else "persisted to distillation_runs"
    lines = [
        f"# Distillation Backfill Report — {mode}",
        "",
        f"**Sessions processed:** {total}",
        f"**Total turns:** {totals['turns']}",
        "",
        "## Signal Summary",
        "",
        "| Signal | Count | Rate |",
        "|--------|-------|------|",
    ]
    for key in ("decisions", "corrections", "patterns", "blockers", "tool_use"):
        count = totals[key]
        rate = f"{count / total:.1f}/session" if total > 0 else "—"
        lines.append(f"| {key} | {count} | {rate} |")

    return "\n".join(lines)
