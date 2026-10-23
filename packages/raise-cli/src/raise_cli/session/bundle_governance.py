"""Server-sourced governance formatting for context bundle (S5593.4).

Reads governance_cache SQLite table populated by pull_governance() at session
start. Returns formatted section for AI consumption. Returns empty string if
no cached data exists (local-only mode fallback handled by caller).
"""

from __future__ import annotations

import json
import sqlite3


def format_governance_cached(conn: sqlite3.Connection, project_id: str) -> str:
    """Format governance from SQLite cache for context bundle."""
    row = conn.execute(
        "SELECT governed_projects, evaluation_rules, scanner_relevant_fields "
        "FROM governance_cache WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    if row is None:
        return ""

    governed: list[dict[str, object]] = json.loads(row[0])
    rules: list[dict[str, object]] = json.loads(row[1])
    fields: list[str] = json.loads(row[2])

    if not governed and not rules and not fields:
        return ""

    lines: list[str] = ["# Server Governance"]

    if governed:
        lines.append(f"Governed projects ({len(governed)}):")
        for p in governed:
            slug = p.get("slug", p.get("name", "unknown"))
            lines.append(f"  - {slug}")

    if rules:
        lines.append(f"Evaluation rules ({len(rules)}):")
        for r in rules:
            name = r.get("name", "unnamed")
            severity = r.get("severity", "")
            suffix = f" [{severity}]" if severity else ""
            lines.append(f"  - {name}{suffix}")

    if fields:
        lines.append(f"Scanner fields: {', '.join(fields)}")

    return "\n".join(lines)
