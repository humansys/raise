"""CC Session → Epic attribution via cascading heuristics.

Processes CC sessions without epic assignment and infers the epic
using branch name patterns, session_records lookup, or temporal
correlation with git commits.
"""

from __future__ import annotations

import re
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

BRANCH_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"story/s(\d+)"), "E{0}"),
    (re.compile(r"story/RAISE-(\d+)"), "RAISE-{0}"),
    (re.compile(r"epic/e(\d+)"), "E{0}"),
    (re.compile(r"worktree-e(\d+)"), "E{0}"),
    (re.compile(r"worktree-epic-e(\d+)"), "E{0}"),
    (re.compile(r"worktree-epic-(\d+)"), "E{0}"),
    (re.compile(r"worktree-raise-(\d+)"), "RAISE-{0}"),
    (re.compile(r"chore/e(\d+)"), "E{0}"),
    (re.compile(r"hotfix/.*?e(\d{4,})"), "E{0}"),
    (re.compile(r"bug/RAISE-(\d+)"), "RAISE-{0}"),
    (re.compile(r"fix/RAISE-(\d+)"), "RAISE-{0}"),
]

Method = Literal["branch_parse", "session_record", "temporal", "unresolved"]
Confidence = Literal["high", "medium", "low"]


@dataclass
class AttributionResult:
    """Result of attributing a CC session to an epic."""

    cc_session_id: str
    epic_id: str | None
    method: Method
    confidence: Confidence
    evidence: str
    output_tokens: int


def attribute_by_branch(session: dict[str, Any]) -> AttributionResult | None:
    """Heuristic 1: Parse branch name to extract epic ID."""
    branch = session.get("branch", "")
    for pattern, template in BRANCH_PATTERNS:
        m = pattern.search(branch)
        if m:
            epic_id = template.format(m.group(1))
            return AttributionResult(
                cc_session_id=session["cc_session_id"],
                epic_id=epic_id,
                method="branch_parse",
                confidence="high",
                evidence=f"branch={branch}",
                output_tokens=session.get("output_tokens", 0),
            )
    return None


def attribute_by_session_record(
    session: dict[str, Any], db_path: Path
) -> AttributionResult | None:
    """Heuristic 2: Lookup rai_session_ids in session_records table."""
    rai_ids = session.get("rai_session_ids", [])
    if not rai_ids or not db_path.exists():
        return None

    conn = sqlite3.connect(str(db_path))
    try:
        placeholders = ",".join("?" for _ in rai_ids)
        rows = conn.execute(
            f"SELECT session_id, epic FROM session_records WHERE session_id IN ({placeholders}) AND epic != ''",  # noqa: S608  # nosec B608
            rai_ids,
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    session_id, epic = rows[0]
    return AttributionResult(
        cc_session_id=session["cc_session_id"],
        epic_id=epic,
        method="session_record",
        confidence="medium",
        evidence=f"session={session_id}→{epic}",
        output_tokens=session.get("output_tokens", 0),
    )


def attribute_by_temporal(
    session: dict[str, Any], repo_path: Path
) -> AttributionResult | None:
    """Heuristic 3: Correlate session timestamps with git commits."""
    first_ts = session.get("first_ts")
    last_ts = session.get("last_ts")
    if not first_ts or not last_ts:
        return None

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                f"--after={first_ts}",
                f"--before={last_ts}",
                "--all",
            ],
            capture_output=True,
            text=True,
            cwd=str(repo_path),
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if result.returncode != 0 or not result.stdout.strip():
        return None

    epic_counts: dict[str, int] = {}
    epic_re = re.compile(r"(?:e|E)(\d{3,})")
    for line in result.stdout.strip().splitlines():
        m = epic_re.search(line)
        if m:
            eid = f"E{m.group(1)}"
            epic_counts[eid] = epic_counts.get(eid, 0) + 1

    if not epic_counts:
        return None

    best_epic = max(epic_counts, key=lambda k: epic_counts[k])
    return AttributionResult(
        cc_session_id=session["cc_session_id"],
        epic_id=best_epic,
        method="temporal",
        confidence="low",
        evidence=f"git_commits={epic_counts[best_epic]} in range {first_ts[:10]}..{last_ts[:10]}",
        output_tokens=session.get("output_tokens", 0),
    )


def attribute_sessions(
    sessions: list[dict[str, Any]],
    *,
    db_path: Path | None = None,
    repo_path: Path | None = None,
) -> list[AttributionResult]:
    """Attribute all sessions using cascading heuristics."""
    results: list[AttributionResult] = []

    for session in sessions:
        result = attribute_by_branch(session)
        if result:
            results.append(result)
            continue

        if db_path:
            result = attribute_by_session_record(session, db_path)
            if result:
                results.append(result)
                continue

        if repo_path:
            result = attribute_by_temporal(session, repo_path)
            if result:
                results.append(result)
                continue

        results.append(
            AttributionResult(
                cc_session_id=session["cc_session_id"],
                epic_id=None,
                method="unresolved",
                confidence="low",
                evidence="no heuristic matched",
                output_tokens=session.get("output_tokens", 0),
            )
        )

    return results


def attribution_report(results: list[AttributionResult]) -> dict[str, Any]:
    """Generate summary report from attribution results."""
    total = len(results)
    by_method: dict[str, int] = {}
    tokens_by_method: dict[str, int] = {}

    for r in results:
        by_method[r.method] = by_method.get(r.method, 0) + 1
        tokens_by_method[r.method] = tokens_by_method.get(r.method, 0) + r.output_tokens

    attributed = total - by_method.get("unresolved", 0)
    rate = (attributed / total * 100) if total > 0 else 0.0

    return {
        "total_sessions": total,
        "attributed": attributed,
        "attribution_rate": round(rate, 1),
        "by_method": by_method,
        "tokens_by_method": tokens_by_method,
    }
