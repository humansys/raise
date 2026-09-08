"""Filesystem-to-SQLite migration for personal data (S2780.6).

Auto-imports legacy YAML/JSONL personal data into the project SQLite
database on first access. Original files are renamed to .migrated
(not deleted). Idempotent — subsequent calls are no-ops.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from raise_cli.storage.connection import (
    get_project_db,
    get_project_hash,
    get_project_id,
)
from raise_cli.storage.schema import create_all

logger = logging.getLogger(__name__)

_PERSONAL_REL = Path(".raise") / "rai" / "personal"


@dataclass
class MigrationResult:
    """Result of a filesystem-to-SQLite migration."""

    success: bool = True
    sessions: int = 0
    journals: int = 0
    signals: int = 0
    pipeline_runs: int = 0
    missions: int = 0
    patterns: int = 0
    session_records: int = 0
    hash_to_slug: int = 0
    malformed: int = 0
    errors: list[str] = field(default_factory=lambda: [])

    @property
    def message(self) -> str:
        """Human-readable summary of migration results."""
        parts: list[str] = []
        if self.sessions:
            parts.append(f"{self.sessions} sessions")
        if self.journals:
            parts.append(f"{self.journals} journal entries")
        if self.signals:
            parts.append(f"{self.signals} signals")
        if self.pipeline_runs:
            parts.append(f"{self.pipeline_runs} pipeline runs")
        if self.missions:
            parts.append(f"{self.missions} missions")
        if self.patterns:
            parts.append(f"{self.patterns} patterns")
        if self.session_records:
            parts.append(f"{self.session_records} session records")
        if not parts:
            return "Nothing to migrate"
        msg = f"Migrated: {', '.join(parts)}"
        if self.malformed:
            msg += f" ({self.malformed} malformed skipped)"
        return msg


def _parse_jsonl(path: Path) -> tuple[list[dict[str, object]], int]:
    """Parse a JSONL file, returning valid records and malformed count."""
    if not path.exists():
        return [], 0
    records: list[dict[str, object]] = []
    malformed = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    return records, malformed


def _rename_to_migrated(path: Path) -> None:
    if path.exists():
        path.rename(path.with_suffix(path.suffix + ".migrated"))


def _migrate_signals(project_path: Path, result: MigrationResult) -> None:
    telemetry_dir = project_path / _PERSONAL_REL / "telemetry"
    candidates = [telemetry_dir / "signals.jsonl", telemetry_dir / "events.jsonl"]

    for signals_path in candidates:
        migrated_path = signals_path.with_suffix(".jsonl.migrated")

        if not signals_path.exists() or migrated_path.exists():
            continue

        records, malformed = _parse_jsonl(signals_path)
        result.malformed += malformed

        if not records:
            continue

        pid = get_project_id(project_path)
        conn = get_project_db(project_path)
        create_all(conn)

        batch: list[tuple[str, str, str, str, str | None]] = []
        for rec in records:
            sig_type = str(rec.get("type", "unknown"))
            timestamp = str(rec.get("timestamp", ""))
            payload = json.dumps(rec)
            session_id = str(rec["session_id"]) if "session_id" in rec else None
            batch.append((pid, timestamp, sig_type, payload, session_id))

        conn.executemany(
            "INSERT INTO signals (project_id, timestamp, type, payload, session_id) VALUES (?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()
        conn.close()

        result.signals += len(records)
        _rename_to_migrated(signals_path)
        logger.info(
            "Migrated %d signals from %s to SQLite", len(records), signals_path.name
        )


def _session_row(
    rec: dict[str, object], prefix: str, project_id: str = ""
) -> tuple[str, ...] | None:
    """Extract a sessions table row from a JSONL record. Returns None if invalid."""
    session_id = str(rec.get("id", ""))
    if not session_id:
        return None
    name = str(rec.get("name", rec.get("topic", "")))
    started = str(rec.get("started", rec.get("date", "")))
    closed = rec.get("closed")
    closed_str = str(closed) if closed else ""
    sess_type = str(rec.get("type", "feature"))
    summary = str(rec.get("summary", rec.get("topic", "")))
    outcomes = json.dumps(rec.get("outcomes", []))
    branch = str(rec.get("branch", ""))
    return (
        project_id,
        session_id,
        name,
        started,
        closed_str or "",
        sess_type,
        summary,
        branch,
        prefix,
        outcomes,
    )


_INSERT_SESSION = """INSERT OR IGNORE INTO sessions
    (project_id, session_id, name, started, closed, type, summary, branch, prefix, state_json, outcomes)
    VALUES (?, ?, ?, ?, nullif(?, ''), ?, ?, ?, ?, '{}', ?)"""


def _import_index_file(
    conn: sqlite3.Connection,
    index_path: Path,
    prefix: str,
    result: MigrationResult,
    project_id: str = "",
) -> int:
    """Import a single index.jsonl into sessions table. Returns row count."""
    migrated_path = index_path.with_suffix(".jsonl.migrated")
    if not index_path.exists() or migrated_path.exists():
        return 0

    records, malformed = _parse_jsonl(index_path)
    result.malformed += malformed
    count = 0

    for rec in records:
        row = _session_row(rec, prefix, project_id=project_id)
        if row is None:
            continue
        conn.execute(_INSERT_SESSION, row)
        count += 1

    _rename_to_migrated(index_path)
    return count


def _migrate_session_index(project_path: Path, result: MigrationResult) -> None:
    sessions_dir = project_path / _PERSONAL_REL / "sessions"
    if not sessions_dir.exists():
        return

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    count = 0

    for prefix_dir in sorted(sessions_dir.iterdir()):
        if not prefix_dir.is_dir():
            continue
        count += _import_index_file(
            conn, prefix_dir / "index.jsonl", prefix_dir.name, result, project_id=pid
        )

    count += _import_index_file(
        conn, sessions_dir / "index.jsonl", "", result, project_id=pid
    )

    conn.commit()
    conn.close()

    result.sessions += count
    if count:
        logger.info("Migrated %d session index entries to SQLite", count)


def _migrate_journals(project_path: Path, result: MigrationResult) -> None:
    sessions_dir = project_path / _PERSONAL_REL / "sessions"
    if not sessions_dir.exists():
        return

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    count = 0

    for session_dir in sorted(sessions_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        journal_path = session_dir / "journal.jsonl"
        migrated_path = journal_path.with_suffix(".jsonl.migrated")
        if not journal_path.exists() or migrated_path.exists():
            continue

        records, malformed = _parse_jsonl(journal_path)
        result.malformed += malformed
        session_id = session_dir.name

        conn.execute(
            """INSERT OR IGNORE INTO sessions
               (project_id, session_id, name, started, type, summary, branch, prefix, state_json, outcomes)
               VALUES (?, ?, ?, '', 'feature', '', '', '', '{}', '[]')""",
            (pid, session_id, session_id),
        )

        for rec in records:
            timestamp = str(rec.get("timestamp", ""))
            entry_type = str(rec.get("entry_type", "note"))
            content = str(rec.get("content", ""))
            tags = json.dumps(rec.get("tags", []))

            conn.execute(
                """INSERT INTO journal_entries (project_id, session_id, timestamp, entry_type, content, tags)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (pid, session_id, timestamp, entry_type, content, tags),
            )
            count += 1

        _rename_to_migrated(journal_path)

    conn.commit()
    conn.close()

    result.journals += count
    if count:
        logger.info("Migrated %d journal entries to SQLite", count)


def _migrate_session_state(project_path: Path, result: MigrationResult) -> None:
    state_path = project_path / _PERSONAL_REL / "session-state.yaml"
    migrated_path = state_path.with_suffix(".yaml.migrated")

    if not state_path.exists() or migrated_path.exists():
        return

    try:
        import yaml

        raw = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Could not parse session-state.yaml, skipping")
        return

    if not isinstance(raw, dict):
        return

    content = cast("dict[str, object]", raw)
    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    state_json = json.dumps(content)
    ls_raw = content.get("last_session")
    ls: dict[str, object] = (
        cast("dict[str, object]", ls_raw) if isinstance(ls_raw, dict) else {}
    )
    name = str(ls.get("id", "flat"))
    started = str(ls.get("date", ""))
    summary = str(ls.get("summary", ""))
    cw_raw = content.get("current_work")
    cw: dict[str, object] = (
        cast("dict[str, object]", cw_raw) if isinstance(cw_raw, dict) else {}
    )
    branch = str(cw.get("branch", ""))

    conn.execute(
        """INSERT OR REPLACE INTO sessions
           (project_id, session_id, name, started, closed, type, summary, branch, prefix, state_json, outcomes)
           VALUES (?, ?, ?, ?, NULL, 'feature', ?, ?, '', ?, '[]')""",
        (pid, "flat", name, started, summary, branch, state_json),
    )
    conn.commit()
    conn.close()

    result.sessions += 1
    _rename_to_migrated(state_path)
    logger.info("Migrated session-state.yaml to SQLite")


_PIPELINE_STATE_SUBPATH = Path(".rai-state") / "pipeline" / "runs"


def _migrate_pipeline_runs(project_path: Path, result: MigrationResult) -> None:
    """Migrate .rai-state/pipeline/runs/*.json into SQLite pipeline_runs table."""
    state_dir = project_path / _PIPELINE_STATE_SUBPATH
    if not state_dir.is_dir():
        return

    json_files = list(state_dir.glob("*.json"))
    if not json_files:
        return

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    count = 0
    migrated_paths: list[Path] = []
    for path in json_files:
        try:
            if path.stat().st_size == 0:
                _rename_to_migrated(path)
                continue
            run = json.loads(path.read_text(encoding="utf-8"))
            conn.execute(
                """INSERT OR IGNORE INTO pipeline_runs
                   (project_id, run_id, pipeline_name, issue_id, current_phase_index,
                    status, phases, started_at, completed_at, metadata,
                    paused_at_phase)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pid,
                    run["run_id"],
                    run.get("pipeline_name", ""),
                    run.get("issue_id", ""),
                    run.get("current_phase_index", 0),
                    run.get("status", "running"),
                    json.dumps(run.get("phases", [])),
                    run.get("started_at", ""),
                    run.get("completed_at"),
                    json.dumps(run.get("metadata", {})),
                    run.get("paused_at_phase"),
                ),
            )
            count += 1
            migrated_paths.append(path)
        except (json.JSONDecodeError, KeyError, OSError):
            result.malformed += 1
            continue

    conn.commit()
    conn.close()

    for path in migrated_paths:
        _rename_to_migrated(path)

    result.pipeline_runs += count
    if count:
        logger.info("Migrated %d pipeline runs to SQLite", count)


def _migrate_missions(_project_path: Path, _result: MigrationResult) -> None:
    """No-op: missions dissolved in S7 (ADR-130)."""


def _backfill_session_records(project_path: Path, result: MigrationResult) -> None:
    """Backfill sessions table → session_records for historical closed sessions.

    Reads all closed sessions from the sessions table and inserts them into
    session_records using INSERT OR IGNORE. Idempotent — rows already present
    (e.g. from write_session_record() on post-S2780.12 closes) are untouched.
    Epic is inferred from branch name via s{N}.{M} pattern.
    """
    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    rows = conn.execute(
        """SELECT session_id, closed, summary, type, outcomes, branch
           FROM sessions
           WHERE project_id = ?
             AND (closed IS NOT NULL AND closed != '')
             AND session_id NOT IN (SELECT session_id FROM session_records WHERE project_id = ?)""",
        (pid, pid),
    ).fetchall()

    count = 0
    for row in rows:
        branch = row["branch"] or ""
        m = re.search(r"s(\d+)\.\d+", branch)
        epic = f"E{m.group(1)}" if m else ""
        outcomes = row["outcomes"] if row["outcomes"] else "[]"
        conn.execute(
            """INSERT OR IGNORE INTO session_records
               (project_id, session_id, closed_at, summary, session_type, epic,
                narrative, next_session_prompt, notes, outcomes_json, completed_epics_json)
               VALUES (?, ?, ?, ?, ?, ?, '', '', '', ?, '[]')""",
            (
                pid,
                row["session_id"],
                row["closed"],
                row["summary"] or "",
                row["type"] or "feature",
                epic,
                outcomes,
            ),
        )
        count += 1

    conn.commit()
    conn.close()

    result.session_records += count
    if count:
        logger.info("Backfilled %d session records from sessions table", count)


_PROJECT_ID_TABLES = (
    "sessions",
    "journal_entries",
    "signals",
    "active_sessions",
    "pipeline_runs",
    "session_records",
    "session_patterns",
    "session_corrections",
    "story_stats",
    "artifacts",
    "ledger_entries",
    "patterns",
    "counters",
    "worktrees",
    "missions",
    # active_mission: removed in v55 (RAISE-14643/S4, ADR-130 D5)
    "agent_session_missions",
    "graph_nodes",
    "graph_edges",
)


def _migrate_project_id_hash_to_slug(
    project_path: Path, result: MigrationResult
) -> None:
    """Convert hash-based project_ids to human-readable slugs (RAISE-6143)."""
    old_hash = get_project_hash(str(project_path))
    new_slug = get_project_id(project_path)
    if old_hash == new_slug:
        return

    conn = get_project_db(project_path)
    create_all(conn)
    try:
        # Merge counters first: composite PK(project_id, name) causes UNIQUE
        # conflict when both hash and slug rows exist for the same counter name.
        conflicts = conn.execute(
            "SELECT h.name, h.value AS hash_val, s.value AS slug_val "
            "FROM counters h JOIN counters s "
            "ON h.name = s.name AND h.project_id = ? AND s.project_id = ?",
            (old_hash, new_slug),
        ).fetchall()
        for row in conflicts:
            merged = max(row[1], row[2])
            conn.execute(
                "UPDATE counters SET value = ? WHERE project_id = ? AND name = ?",
                (merged, new_slug, row[0]),
            )
            conn.execute(
                "DELETE FROM counters WHERE project_id = ? AND name = ?",
                (old_hash, row[0]),
            )

        total = 0
        for table in _PROJECT_ID_TABLES:
            table_info = conn.execute(f"PRAGMA table_info({table})").fetchall()
            cols = {r[1] for r in table_info}
            if "project_id" not in cols:
                continue
            # RAISE-17158: patterns has a partial UNIQUE index on (project_id,
            # content_hash) WHERE archived=0 (V52). pattern_id is globally unique
            # (not per-project), so the generic PK-conflict DELETE below is a
            # no-op for patterns. Pre-archive old_hash rows whose content_hash
            # already exists and is active under new_slug — same pattern as V51.
            if table == "patterns":
                conn.execute(
                    "UPDATE patterns SET archived = 1 "
                    "WHERE project_id = ? AND content_hash IS NOT NULL AND archived = 0 "
                    "AND EXISTS ("
                    "SELECT 1 FROM patterns p2 WHERE p2.project_id = ? "
                    "AND p2.content_hash = patterns.content_hash AND p2.archived = 0"
                    ")",
                    (old_hash, new_slug),
                )
            # Delete hash rows that conflict with existing slug rows on the composite PK.
            # Without this, the UPDATE below would raise UNIQUE constraint (RAISE-6255).
            pk_cols = [r[1] for r in table_info if r[5] > 0 and r[1] != "project_id"]
            if pk_cols:
                pk_where = " AND ".join(f"h.{c} = s.{c}" for c in pk_cols)
                conn.execute(
                    f"DELETE FROM {table} AS h WHERE h.project_id = ? "  # noqa: S608  # nosec B608
                    f"AND EXISTS (SELECT 1 FROM {table} s WHERE s.project_id = ? AND {pk_where})",
                    (old_hash, new_slug),
                )
            updated = conn.execute(
                f"UPDATE {table} SET project_id = ? WHERE project_id = ?",  # noqa: S608  # nosec B608
                (new_slug, old_hash),
            ).rowcount
            total += updated

        conn.commit()
        result.hash_to_slug = total
    finally:
        conn.close()

    if total:
        logger.info(
            "RAISE-6143: migrated %d rows from project_id=%s to %s",
            total,
            old_hash,
            new_slug,
        )


def _migrate_patterns(project_path: Path, result: MigrationResult) -> None:
    from raise_cli.config.paths import get_memory_dir
    from raise_cli.memory.patterns_backend import migrate_patterns_to_sqlite

    jsonl_path = get_memory_dir(project_path) / "patterns.jsonl"
    if not jsonl_path.exists():
        return

    pid = get_project_id(project_path)
    conn = get_project_db(project_path)
    create_all(conn)

    count = migrate_patterns_to_sqlite(conn, jsonl_path=jsonl_path, project_id=pid)
    conn.commit()
    conn.close()
    result.patterns += count
    if count:
        logger.info("Migrated %d patterns from %s to SQLite", count, jsonl_path)


def migrate_if_needed(project_path: Path) -> MigrationResult:
    """Migrate legacy JSONL/YAML personal data to SQLite.

    Imports session index, journal entries, telemetry signals, and session
    state from their legacy file locations into the project SQLite database.
    Original files are renamed to .migrated. Idempotent — already-migrated
    sources are skipped.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        MigrationResult with counts and status.
    """
    result = MigrationResult()

    try:
        _migrate_signals(project_path, result)
        _migrate_session_index(project_path, result)
        _migrate_journals(project_path, result)
        _migrate_session_state(project_path, result)
        _migrate_pipeline_runs(project_path, result)
        _migrate_missions(project_path, result)
        _migrate_patterns(project_path, result)
        _backfill_session_records(project_path, result)
        _migrate_project_id_hash_to_slug(project_path, result)
    except Exception as exc:
        result.success = False
        result.errors.append(str(exc))
        logger.exception("Migration failed: %s", exc)

    return result
