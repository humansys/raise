"""Local cc_token_daily ingestion — RAISE-16866.

Builds one row per CC session JSONL and upserts it into the local
~/.rai/raise.db cc_token_daily table.  Never requires server credentials.

Source: session JSONLs (not stats-cache.json which is frozen since 2026-07-13).
Idempotent: INSERT ... ON CONFLICT(cc_session_id, date) DO UPDATE.

Design decisions (see design.md):
  D1: source = 'jsonl' (distinguishes from legacy 'stats-cache-*')
  D2: reuse scan_single_session() + attribute_by_branch()
  D3: DDL in storage/schema.py (V77)
  D4: called at session close, not inside _emit_token_usage_daily
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# DDL for cc_token_daily — verbatim from .schema cc_token_daily on live DB.
# Also added to storage/schema.py as _V77_DDL for fresh installs.

_CC_TOKEN_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS cc_token_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cc_session_id TEXT NOT NULL,
    date TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'stats-cache',
    output_tokens INTEGER NOT NULL DEFAULT 0,
    estimated_cost_usd REAL NOT NULL DEFAULT 0,
    models_json TEXT NOT NULL DEFAULT '{}',
    epic TEXT NOT NULL DEFAULT 'unknown',
    epic_source TEXT NOT NULL DEFAULT 'git',
    prompts INTEGER NOT NULL DEFAULT 0,
    sessions_count INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(cc_session_id, date)
)
"""


def extract_git_branch(jsonl_path: Path) -> str | None:
    """Return the first gitBranch value found in any JSONL record, or None."""
    try:
        for raw in jsonl_path.open(encoding="utf-8", errors="replace"):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj: Any = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "gitBranch" in obj:
                branch = obj["gitBranch"]
                if isinstance(branch, str) and branch:
                    return branch
    except OSError as exc:
        logger.debug("extract_git_branch: cannot read %s — %s", jsonl_path, exc)
    return None


def count_prompts(jsonl_path: Path) -> int:
    """Count user records that are text prompts (not tool_result)."""
    count = 0
    try:
        for raw in jsonl_path.open(encoding="utf-8", errors="replace"):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj: Any = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict) or obj.get("type") != "user":
                continue
            message = obj.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, str):
                # Plain text content — counts as prompt
                count += 1
            elif isinstance(content, list):
                # Has at least one non-tool_result text block?
                has_text = any(
                    isinstance(c, dict) and c.get("type") == "text" for c in content
                )
                if has_text:
                    count += 1
    except OSError as exc:
        logger.debug("count_prompts: cannot read %s — %s", jsonl_path, exc)
    return count


def build_token_daily_row(jsonl_path: Path) -> dict[str, Any] | None:
    """Build a cc_token_daily row dict from a session JSONL, or None if empty.

    Returns None for empty or unreadable files.  All heavy lifting is delegated
    to scan_single_session() (deduplication, model totals, cost) and
    attribution.attribute_by_branch() (epic id).
    """
    from raise_cli.telemetry.attribution import attribute_by_branch
    from raise_cli.telemetry.backfill import (
        _extract_session_date,  # pyright: ignore[reportPrivateUsage]
    )
    from raise_cli.telemetry.cost_report import scan_single_session

    if not jsonl_path.exists() or jsonl_path.stat().st_size == 0:
        logger.debug("build_token_daily_row: skipping empty/missing %s", jsonl_path)
        return None

    report = scan_single_session(jsonl_path)
    if not report.models:
        # No billable assistant messages — nothing to store.
        logger.debug("build_token_daily_row: no billable records in %s", jsonl_path)
        return None

    # Date: first assistant message date (same logic as backfill.py)
    date = _extract_session_date(jsonl_path)
    if date is None:
        logger.debug(
            "build_token_daily_row: no assistant timestamp found in %s — skipping",
            jsonl_path,
        )
        return None

    # Epic attribution via gitBranch
    branch = extract_git_branch(jsonl_path)
    epic_id = "unknown"
    if branch:
        result = attribute_by_branch(
            {"cc_session_id": jsonl_path.stem, "branch": branch}
        )
        if result is not None and result.epic_id:
            epic_id = result.epic_id

    # models_json: full per-model breakdown (keyed by full model id)
    models_dict: dict[str, dict[str, Any]] = {}
    for m in report.models:
        models_dict[m.model] = {
            "input": m.input_tokens,
            "output": m.output_tokens,
            "cache_write": m.cache_write,
            "cache_read": m.cache_read,
            "cost": m.cost_usd,
        }

    return {
        "cc_session_id": jsonl_path.stem,
        "date": date,
        "source": "jsonl",
        "output_tokens": sum(m.output_tokens for m in report.models),
        "estimated_cost_usd": report.total_cost_usd,
        "models_json": json.dumps(models_dict),
        "epic": epic_id,
        "epic_source": "git",
        "prompts": count_prompts(jsonl_path),
        "sessions_count": 1,
    }


def ensure_table(conn: sqlite3.Connection) -> None:
    """CREATE TABLE IF NOT EXISTS cc_token_daily. Idempotent."""
    conn.executescript(_CC_TOKEN_DAILY_DDL)


def upsert_token_daily(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    """INSERT or UPDATE a cc_token_daily row. Idempotent on (cc_session_id, date)."""
    conn.execute(
        """
        INSERT INTO cc_token_daily
            (cc_session_id, date, source, output_tokens, estimated_cost_usd,
             models_json, epic, epic_source, prompts, sessions_count)
        VALUES
            (:cc_session_id, :date, :source, :output_tokens, :estimated_cost_usd,
             :models_json, :epic, :epic_source, :prompts, :sessions_count)
        ON CONFLICT(cc_session_id, date) DO UPDATE SET
            source             = excluded.source,
            output_tokens      = excluded.output_tokens,
            estimated_cost_usd = excluded.estimated_cost_usd,
            models_json        = excluded.models_json,
            epic               = excluded.epic,
            epic_source        = excluded.epic_source,
            prompts            = excluded.prompts,
            sessions_count     = excluded.sessions_count
        """,
        row,
    )
    conn.commit()


def ingest_session_file(db_path: Path, jsonl_path: Path) -> None:
    """Build a row from *jsonl_path* and upsert into *db_path*.

    No-op for empty or unreadable files.  All exceptions are logged at DEBUG
    and suppressed — must never block session close (D4).
    """
    try:
        row = build_token_daily_row(jsonl_path)
        if row is None:
            logger.debug("ingest_session_file: no row built for %s — skip", jsonl_path)
            return
        conn = sqlite3.connect(str(db_path), timeout=5)
        try:
            ensure_table(conn)
            upsert_token_daily(conn, row)
            logger.debug(
                "ingest_session_file: wrote cc_token_daily row for %s date=%s",
                row["cc_session_id"],
                row["date"],
            )
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "ingest_session_file: suppressed error for %s — %s",
            jsonl_path,
            exc,
        )
