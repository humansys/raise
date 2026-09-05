"""SQLite persistence for post-session distillation runs."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import NamedTuple


@dataclass
class DistillationRun:
    """Structured record of a single post-session distillation run."""

    session_id: str
    date: str
    project: str = ""
    runtime: str = "claude-code"
    turns_total: int = 0
    decisions_count: int = 0
    corrections_count: int = 0
    patterns_count: int = 0
    blockers_count: int = 0
    tool_use_count: int = 0
    journal_path: str = ""
    journal_md: str = ""
    created_at: str = field(default="")


def persist_run(conn: sqlite3.Connection, run: DistillationRun) -> None:
    """Insert or update a distillation run record."""
    conn.execute(
        """
        INSERT INTO distillation_runs
            (session_id, date, project, runtime, turns_total,
             decisions_count, corrections_count, patterns_count,
             blockers_count, tool_use_count, journal_path, journal_md)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(session_id) DO UPDATE SET
            date=excluded.date,
            project=excluded.project,
            runtime=excluded.runtime,
            turns_total=excluded.turns_total,
            decisions_count=excluded.decisions_count,
            corrections_count=excluded.corrections_count,
            patterns_count=excluded.patterns_count,
            blockers_count=excluded.blockers_count,
            tool_use_count=excluded.tool_use_count,
            journal_path=excluded.journal_path,
            journal_md=excluded.journal_md
        """,
        (
            run.session_id,
            run.date,
            run.project,
            run.runtime,
            run.turns_total,
            run.decisions_count,
            run.corrections_count,
            run.patterns_count,
            run.blockers_count,
            run.tool_use_count,
            run.journal_path,
            run.journal_md,
        ),
    )
    conn.commit()


def _row_to_run(row: sqlite3.Row) -> DistillationRun:
    return DistillationRun(
        session_id=row["session_id"],
        date=row["date"],
        project=row["project"],
        runtime=row["runtime"],
        turns_total=row["turns_total"],
        decisions_count=row["decisions_count"],
        corrections_count=row["corrections_count"],
        patterns_count=row["patterns_count"],
        blockers_count=row["blockers_count"],
        tool_use_count=row["tool_use_count"],
        journal_path=row["journal_path"],
        journal_md=row["journal_md"],
        created_at=row["created_at"],
    )


def get_run(conn: sqlite3.Connection, session_id: str) -> DistillationRun | None:
    """Return a single distillation run by session_id, or None if not found."""
    row = conn.execute(
        "SELECT * FROM distillation_runs WHERE session_id = ?", (session_id,)
    ).fetchone()
    return _row_to_run(row) if row else None


def list_runs(
    conn: sqlite3.Connection,
    *,
    since: str | None = None,
    runtime: str | None = None,
) -> list[DistillationRun]:
    """Return distillation runs ordered by date DESC, with optional filters."""
    query = "SELECT * FROM distillation_runs WHERE 1=1"
    params: list[str] = []
    if since:
        query += " AND date >= ?"
        params.append(since)
    if runtime:
        query += " AND runtime = ?"
        params.append(runtime)
    query += " ORDER BY date DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    return [_row_to_run(r) for r in rows]


class JidokaScore(NamedTuple):
    """Jidoka (gate-honoring) score for a single session."""

    session_id: str
    honored: int  # gate failures that were fixed and re-run (resolved=True)
    total_failures: int  # all gate failure events (honored + active evasions)
    score: float | None  # honored/total_failures; None when total_failures=0
    bypass_flags: int  # BYPASS_FLAG events (--no-verify / RAISE_SKIP_*)
    omissions: int  # OMISSION_EVASION events (commit without prior gate)
    no_failures: bool  # True when total_failures=0 (all gates passed or no gates ran)


def jidoka_score(conn: sqlite3.Connection, session_id: str) -> JidokaScore:
    """Compute the Jidoka score for a session from its evasion_events rows.

    Score = honored / total_gate_failures, or None when total_gate_failures=0.
    A score of None with no_failures=True means either all gates passed or none ran.
    """
    rows = conn.execute(
        """
        SELECT evasion_type, resolved
        FROM evasion_events
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchall()

    honored = 0
    total_gate_failures = 0
    bypass_flags = 0
    omissions = 0
    for row in rows:
        etype, resolved = row[0], row[1]
        if etype == "GATE_EVASION":
            total_gate_failures += 1
            if resolved:
                honored += 1
        elif etype == "BYPASS_FLAG":
            bypass_flags += 1
        elif etype == "OMISSION_EVASION":
            omissions += 1

    score = honored / total_gate_failures if total_gate_failures > 0 else None
    return JidokaScore(
        session_id=session_id,
        honored=honored,
        total_failures=total_gate_failures,
        score=score,
        bypass_flags=bypass_flags,
        omissions=omissions,
        no_failures=total_gate_failures == 0,
    )


def stats(
    conn: sqlite3.Connection,
    *,
    since: str | None = None,
) -> dict[str, int]:
    """Aggregate distillation counts across runs, with optional date filter."""
    query = """
        SELECT
            COUNT(*) as total_runs,
            COALESCE(SUM(turns_total), 0) as total_turns,
            COALESCE(SUM(decisions_count), 0) as total_decisions,
            COALESCE(SUM(corrections_count), 0) as total_corrections,
            COALESCE(SUM(patterns_count), 0) as total_patterns,
            COALESCE(SUM(blockers_count), 0) as total_blockers,
            COALESCE(SUM(tool_use_count), 0) as total_tool_use
        FROM distillation_runs
    """
    params: list[str] = []
    if since:
        query += " WHERE date >= ?"
        params.append(since)
    row = conn.execute(query, params).fetchone()
    if row is None:
        return {
            "total_runs": 0,
            "total_turns": 0,
            "total_decisions": 0,
            "total_corrections": 0,
            "total_patterns": 0,
            "total_blockers": 0,
            "total_tool_use": 0,
        }
    return {
        "total_runs": row["total_runs"],
        "total_turns": row["total_turns"],
        "total_decisions": row["total_decisions"],
        "total_corrections": row["total_corrections"],
        "total_patterns": row["total_patterns"],
        "total_blockers": row["total_blockers"],
        "total_tool_use": row["total_tool_use"],
    }
