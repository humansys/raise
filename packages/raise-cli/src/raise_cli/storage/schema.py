"""SQLite schema definitions and PRAGMA user_version migration."""

from __future__ import annotations

import contextlib
import datetime
import logging
import os
import sqlite3
import time
from collections.abc import Callable

from pydantic import BaseModel

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 79

_BACKUP_DEADLINE_SECONDS = 10.0
_BACKUP_PAGES = 256


class BackupReceipt(BaseModel):
    """Record of a successful pre-migration backup."""

    path: str
    source_version: int
    target_version: int


class MigrationBackupError(RuntimeError):
    """Raised when pre-migration backup fails; no migration has occurred."""

    def __init__(
        self, message: str, *, source_version: int, candidate_path: str
    ) -> None:
        super().__init__(message)
        self.source_version = source_version
        self.candidate_path = candidate_path


def _backup_stamp() -> str:
    """UTC timestamp string for backup filenames."""
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")


def _claim_backup_path(base: str) -> str:
    """Claim a unique final backup path using O_CREAT|O_EXCL.

    If the base name is already taken, appends ``-1``, ``-2``, … until a slot
    is exclusively created.  Returns the claimed path (a zero-byte file).
    """
    for suffix_n in range(0, 1000):
        candidate = base if suffix_n == 0 else f"{base}-{suffix_n}"
        try:
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.close(fd)
            return candidate
        except FileExistsError:
            continue
    raise MigrationBackupError(
        f"Could not claim a unique backup path after 1000 attempts (base={base})",
        source_version=0,
        candidate_path=base,
    )


def _do_backup_copy(
    conn: sqlite3.Connection,
    partial_path: str,
    deadline: float,
    source_version: int,
) -> None:
    """Copy *conn* to *partial_path* via the online backup API.

    Raises ``MigrationBackupError`` on timeout or copy failure.
    """

    def _progress(_status: int, _remaining: int, _total: int) -> None:
        if time.monotonic() > deadline:
            raise MigrationBackupError(
                f"Pre-migration backup timed out after {_BACKUP_DEADLINE_SECONDS}s",
                source_version=source_version,
                candidate_path=partial_path,
            )

    dest_conn = sqlite3.connect(partial_path)
    try:
        dest_conn.execute("PRAGMA busy_timeout=5000")
        conn.backup(dest_conn, pages=_BACKUP_PAGES, progress=_progress)
        # Convert backup to non-WAL mode so it is a single clean file.
        # When the source DB uses WAL mode (set in create_all), the backup API
        # copies WAL-mode state and SQLite creates .partial-wal/.partial-shm
        # sidecars that survive os.replace() and confuse any glob that counts
        # backup files.  PRAGMA journal_mode=DELETE checkpoints and removes them.
        dest_conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        dest_conn.close()  # Must close before verification (Windows file locks).


def _verify_backup(
    partial_path: str,
    db_path: str,
    source_version: int,
) -> int:
    """Open the backup read-only, run integrity_check, return its user_version.

    Raises ``MigrationBackupError`` if integrity_check is not ``ok``.
    """
    check_conn = sqlite3.connect(f"file:{partial_path}?mode=ro", uri=True)
    try:
        ic_result: str = check_conn.execute("PRAGMA integrity_check").fetchone()[0]
        if ic_result != "ok":
            raise MigrationBackupError(
                f"Pre-migration backup integrity_check failed for {db_path}"
                f" at v{source_version}: {ic_result}"
                f" (candidate: {partial_path})",
                source_version=source_version,
                candidate_path=partial_path,
            )
        return int(check_conn.execute("PRAGMA user_version").fetchone()[0])
    finally:
        check_conn.close()


def _cleanup_partial(partial_path: str, final_path: str | None) -> None:
    """Remove the owned partial file and any claimed-but-unreplaced final file."""
    for path in [partial_path, *([final_path] if final_path else [])]:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(path)


def prepare_migration_backup(
    conn: sqlite3.Connection,
    source_version: int,
    target_version: int,
) -> BackupReceipt | None:
    """Create a verified online backup of *conn* before migration.

    Returns ``None`` for in-memory databases and pristine v0 databases (no user
    objects in ``sqlite_master``), so the caller can migrate as today without
    branching on backup state.

    Raises ``MigrationBackupError`` — wrapping the underlying cause — if
    allocation, the backup API, or ``PRAGMA integrity_check`` fails.  The
    partial file is cleaned up before re-raising; the source connection is never
    written to, so source integrity is guaranteed by construction.
    """
    db_path = _main_database_file(conn)
    if not db_path:
        return None

    if source_version == 0:
        user_objects: int = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master"
            " WHERE type IN ('table','index')"
            " AND name NOT LIKE 'sqlite_%'"
        ).fetchone()[0]
        if user_objects == 0:
            return None

    stamp = _backup_stamp()
    base_final = f"{db_path}.backup-v{source_version}-{stamp}"
    partial_path = f"{base_final}.partial"
    final_path: str | None = None
    deadline = time.monotonic() + _BACKUP_DEADLINE_SECONDS

    # Step 1: Claim partial name for this attempt.
    try:
        fd = os.open(partial_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        os.close(fd)
    except OSError as exc:
        raise MigrationBackupError(
            f"Pre-migration backup allocation failed for {db_path} at"
            f" v{source_version}: {exc}",
            source_version=source_version,
            candidate_path=partial_path,
        ) from exc

    try:
        # Step 2: Online backup; Step 3: Verify.
        _do_backup_copy(conn, partial_path, deadline, source_version)
        backup_version = _verify_backup(partial_path, db_path, source_version)

        # Step 4: Claim final name (TOCTOU-free) and promote.
        final_path = _claim_backup_path(base_final)
        os.replace(partial_path, final_path)

    except MigrationBackupError:
        _cleanup_partial(partial_path, final_path)
        raise
    except Exception as exc:
        _cleanup_partial(partial_path, final_path)
        raise MigrationBackupError(
            f"Pre-migration backup failed for {db_path} at v{source_version}: {exc}"
            f" (candidate: {partial_path})",
            source_version=source_version,
            candidate_path=partial_path,
        ) from exc

    receipt = BackupReceipt(
        path=final_path,
        source_version=backup_version,
        target_version=target_version,
    )
    logger.info(
        "Pre-migration backup created: %s (v%d -> v%d)",
        receipt.path,
        receipt.source_version,
        receipt.target_version,
    )
    return receipt


_V1_DDL = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    started TEXT NOT NULL,
    closed TEXT,
    type TEXT NOT NULL DEFAULT 'feature',
    summary TEXT NOT NULL DEFAULT '',
    branch TEXT NOT NULL DEFAULT '',
    prefix TEXT NOT NULL DEFAULT '',
    state_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX IF NOT EXISTS idx_journal_session ON journal_entries(session_id);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(type);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);

CREATE TABLE IF NOT EXISTS active_sessions (
    session_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    started TEXT NOT NULL
);
"""

_V2_DDL = """
ALTER TABLE sessions ADD COLUMN outcomes TEXT NOT NULL DEFAULT '[]';
"""

_V3_DDL = """
ALTER TABLE signals ADD COLUMN session_id TEXT;
CREATE INDEX IF NOT EXISTS idx_signals_session ON signals(session_id);
"""

_V4_DDL = """
DROP TABLE IF EXISTS hansei_events;
"""

_V5_DDL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    issue_id TEXT NOT NULL,
    current_phase_index INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'running',
    phases TEXT NOT NULL DEFAULT '[]',
    started_at TEXT NOT NULL,
    completed_at TEXT,
    metadata TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_issue ON pipeline_runs(issue_id);
"""

_V6_DDL = """
ALTER TABLE pipeline_runs ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE pipeline_runs ADD COLUMN paused_at_phase TEXT;
"""

_V7_DDL = """
CREATE TABLE IF NOT EXISTS agent_session_missions (
    cc_session_id TEXT PRIMARY KEY,
    mission_id    TEXT NOT NULL,
    bound_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""

_V8_DDL = """
ALTER TABLE sessions ADD COLUMN story_points INTEGER;
"""

_V9_DDL = """
CREATE TABLE IF NOT EXISTS missions (
    mission_id         TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    status             TEXT NOT NULL DEFAULT 'active',
    objectives         TEXT NOT NULL DEFAULT '[]',
    linked_epics       TEXT NOT NULL DEFAULT '[]',
    sessions           TEXT NOT NULL DEFAULT '[]',
    learned_patterns   TEXT NOT NULL DEFAULT '[]',
    scratch            INTEGER NOT NULL DEFAULT 0,
    close_note         TEXT,
    retrospective_path TEXT,
    created_at         TEXT NOT NULL,
    last_used_at       TEXT NOT NULL,
    closed_at          TEXT
);
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);

CREATE TABLE IF NOT EXISTS active_mission (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    mission_id TEXT NOT NULL REFERENCES missions(mission_id)
);
"""

_V10_DDL = """
CREATE TABLE IF NOT EXISTS issue_cache (
    key        TEXT PRIMARY KEY,
    summary    TEXT NOT NULL DEFAULT '',
    fetched_at TEXT NOT NULL
);
"""

_V11_DDL = """
CREATE TABLE IF NOT EXISTS session_records (
    session_id            TEXT PRIMARY KEY,
    closed_at             TEXT NOT NULL,
    summary               TEXT NOT NULL DEFAULT '',
    session_type          TEXT NOT NULL DEFAULT 'feature',
    epic                  TEXT NOT NULL DEFAULT '',
    narrative             TEXT NOT NULL DEFAULT '',
    next_session_prompt   TEXT NOT NULL DEFAULT '',
    notes                 TEXT NOT NULL DEFAULT '',
    outcomes_json         TEXT NOT NULL DEFAULT '[]',
    completed_epics_json  TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS session_patterns (
    id           TEXT PRIMARY KEY,
    session_id   TEXT NOT NULL REFERENCES session_records(session_id),
    content      TEXT NOT NULL,
    sub_type     TEXT NOT NULL DEFAULT 'process',
    context_json TEXT NOT NULL DEFAULT '[]',
    created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_session_patterns_session ON session_patterns(session_id);

CREATE TABLE IF NOT EXISTS session_corrections (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES session_records(session_id),
    what       TEXT NOT NULL,
    lesson     TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_session_corrections_session ON session_corrections(session_id);
"""

_V12_DDL = """
CREATE TABLE IF NOT EXISTS story_stats (
    story_id        TEXT PRIMARY KEY,
    branch          TEXT NOT NULL DEFAULT '',
    commit_count    INTEGER NOT NULL DEFAULT 0,
    last_commit_sha TEXT NOT NULL DEFAULT '',
    updated_at      TEXT NOT NULL
);
"""

_V13_DDL = """
ALTER TABLE sessions ADD COLUMN agent_session_id TEXT;
ALTER TABLE sessions ADD COLUMN agent_runtime TEXT;
"""

_V14_DDL = """
CREATE TABLE IF NOT EXISTS counters (
    name  TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
ALTER TABLE sessions ADD COLUMN session_number INTEGER;
UPDATE sessions
SET session_number = (
    SELECT n FROM (
        SELECT session_id, ROW_NUMBER() OVER (ORDER BY started, session_id) AS n
        FROM sessions
    ) AS numbered
    WHERE numbered.session_id = sessions.session_id
)
WHERE session_number IS NULL;
INSERT OR REPLACE INTO counters (name, value)
SELECT 'session', COALESCE(MAX(session_number), 0) FROM sessions;
"""

_V15_DDL = """
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id    TEXT PRIMARY KEY,
    story_id       TEXT NOT NULL,
    artifact_type  TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 1,
    session_id     TEXT,
    content_json   TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_artifacts_story ON artifacts(story_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_story_type ON artifacts(story_id, artifact_type);
"""

_V16_DDL = """
CREATE TABLE IF NOT EXISTS ledger_entries (
    local_key   TEXT PRIMARY KEY,
    jira_key    TEXT NOT NULL,
    legacy_id   TEXT,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_ledger_jira ON ledger_entries(jira_key);
"""

_V17_DDL = """
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id     TEXT PRIMARY KEY,
    type           TEXT NOT NULL DEFAULT 'process',
    content        TEXT NOT NULL,
    context_json   TEXT NOT NULL DEFAULT '[]',
    learned_from   TEXT NOT NULL DEFAULT '',
    mission_id     TEXT NOT NULL DEFAULT '',
    scope          TEXT NOT NULL DEFAULT 'project',
    base           INTEGER NOT NULL DEFAULT 0,
    version        INTEGER NOT NULL DEFAULT 1,
    positives      INTEGER NOT NULL DEFAULT 0,
    negatives      INTEGER NOT NULL DEFAULT 0,
    evaluations    INTEGER NOT NULL DEFAULT 0,
    last_evaluated TEXT,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(type);
CREATE INDEX IF NOT EXISTS idx_patterns_scope ON patterns(scope);
"""

_V18_DDL = """
ALTER TABLE patterns ADD COLUMN original_id TEXT NOT NULL DEFAULT '';
ALTER TABLE patterns ADD COLUMN developer_prefix TEXT NOT NULL DEFAULT '';
"""

_V19_DDL = """
CREATE TABLE IF NOT EXISTS pending_sync (
    id          INTEGER PRIMARY KEY CHECK (id = 1),
    timestamp   TEXT NOT NULL,
    graph_path  TEXT NOT NULL,
    node_count  INTEGER NOT NULL,
    edge_count  INTEGER NOT NULL,
    error       TEXT NOT NULL
);

"""
# Graph tables removed in V27 when graph data moved to Kuzu storage (S4513.7).
# V30 restores SQLite as the community canonical graph store.

_V20_DDL = """
ALTER TABLE signals ADD COLUMN server_sync_status TEXT NOT NULL DEFAULT 'local_only';
CREATE INDEX IF NOT EXISTS idx_signals_sync_status ON signals(server_sync_status);
"""

_V21_DDL = """
ALTER TABLE signals ADD COLUMN trace_id TEXT;
ALTER TABLE signals ADD COLUMN span_id TEXT;
ALTER TABLE signals ADD COLUMN source TEXT;
CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source);
UPDATE signals
SET trace_id = json_extract(payload, '$.trace_id'),
    span_id  = json_extract(payload, '$.span_id'),
    source   = json_extract(payload, '$.source')
WHERE trace_id IS NULL;
"""

_V22_DDL = """
ALTER TABLE signals ADD COLUMN otel_resource_json TEXT;
"""

_V23_DDL = """
ALTER TABLE signals ADD COLUMN output_tokens INTEGER;
ALTER TABLE signals ADD COLUMN input_tokens INTEGER;
ALTER TABLE signals ADD COLUMN cache_read_tokens INTEGER;
ALTER TABLE signals ADD COLUMN cache_write_tokens INTEGER;
"""

_V24_DDL = ""  # Handled programmatically in _apply_v24()

_V25_DDL = """
CREATE TABLE IF NOT EXISTS worktrees (
    worktree_id     TEXT NOT NULL,
    project_id      TEXT NOT NULL,
    path            TEXT NOT NULL,
    branch          TEXT NOT NULL,
    merge_target    TEXT NOT NULL,
    stories_json    TEXT NOT NULL DEFAULT '[]',
    status          TEXT NOT NULL DEFAULT 'open',
    last_session_id TEXT,
    created_at      TEXT NOT NULL,
    mission_id      TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (worktree_id, project_id)
);
CREATE INDEX IF NOT EXISTS idx_worktrees_project_path   ON worktrees(project_id, path);
CREATE INDEX IF NOT EXISTS idx_worktrees_project_status ON worktrees(project_id, status);
"""


_V26_DDL = """
CREATE TABLE IF NOT EXISTS sync_outbox (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id    TEXT NOT NULL,
    operation     TEXT NOT NULL DEFAULT 'push',
    status        TEXT NOT NULL DEFAULT 'pending',
    retries       INTEGER NOT NULL DEFAULT 0,
    max_retries   INTEGER NOT NULL DEFAULT 5,
    last_attempt  TEXT,
    error_message TEXT,
    created_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_sync_outbox_status ON sync_outbox(status);

CREATE TABLE IF NOT EXISTS sync_state (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""

# V27: graph data moved to Kuzu storage — drop SQLite graph tables (S4513.7)
_V27_DDL = """
DROP INDEX IF EXISTS idx_graph_edges_pid_src;
DROP INDEX IF EXISTS idx_graph_edges_pid_tgt;
DROP INDEX IF EXISTS idx_graph_nodes_pid_type;
DROP INDEX IF EXISTS idx_graph_nodes_type;
DROP INDEX IF EXISTS idx_graph_edges_source;
DROP INDEX IF EXISTS idx_graph_edges_target;
DROP TABLE IF EXISTS graph_edges;
DROP TABLE IF EXISTS graph_nodes;
"""

_V28_DDL = ""  # Handled programmatically in _apply_v28()

_V29_DDL = ""  # Handled programmatically in _apply_v29()

_V30_DDL = """
CREATE TABLE IF NOT EXISTS graph_nodes (
    project_id     TEXT NOT NULL CHECK(length(project_id) > 0),
    node_id        TEXT NOT NULL,
    node_type      TEXT NOT NULL DEFAULT '',
    content        TEXT NOT NULL DEFAULT '',
    source_file    TEXT NOT NULL DEFAULT '',
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    release_id     TEXT NOT NULL DEFAULT '',
    module_id      TEXT NOT NULL DEFAULT '',
    always_on      INTEGER NOT NULL DEFAULT 0,
    foundational   INTEGER NOT NULL DEFAULT 0,
    graph_version  INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, node_id)
);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_type
    ON graph_nodes(project_id, node_type);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_always_on
    ON graph_nodes(project_id, always_on);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_foundational
    ON graph_nodes(project_id, foundational);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_release
    ON graph_nodes(project_id, release_id);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_source
    ON graph_nodes(project_id, source_file);

CREATE TABLE IF NOT EXISTS graph_edges (
    project_id      TEXT NOT NULL CHECK(length(project_id) > 0),
    source_node_id  TEXT NOT NULL,
    target_node_id  TEXT NOT NULL,
    edge_type       TEXT NOT NULL DEFAULT '',
    edge_key        TEXT NOT NULL DEFAULT '0',
    metadata_json   TEXT NOT NULL DEFAULT '{}',
    source_file     TEXT NOT NULL DEFAULT '',
    graph_version   INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, source_node_id, target_node_id, edge_type, edge_key)
);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_source
    ON graph_edges(project_id, source_node_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_target
    ON graph_edges(project_id, target_node_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_type
    ON graph_edges(project_id, edge_type);

CREATE TABLE IF NOT EXISTS governance_cache (
    project_id                TEXT PRIMARY KEY,
    governed_projects         TEXT NOT NULL DEFAULT '[]',
    evaluation_rules          TEXT NOT NULL DEFAULT '[]',
    scanner_relevant_fields   TEXT NOT NULL DEFAULT '[]',
    fetched_at                TEXT NOT NULL DEFAULT ''
);
"""


_V31_DDL = ""  # Data migration only — see _apply_v31()

_V32_DDL = ""  # Handled programmatically in _apply_v32()

_V33_DDL = """
CREATE TABLE IF NOT EXISTS docs_sync (
    local_path  TEXT NOT NULL,
    remote_id   TEXT NOT NULL,
    url         TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    project_id  TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (local_path, project_id)
);
CREATE INDEX IF NOT EXISTS idx_docs_sync_project ON docs_sync(project_id);
"""

_V34_DDL = ""  # Handled programmatically in _apply_v34()

_V35_DDL = """
CREATE TABLE IF NOT EXISTS session_pattern_queries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   TEXT NOT NULL DEFAULT '',
    session_id   TEXT NOT NULL,
    pattern_id   TEXT NOT NULL,
    query_keywords TEXT NOT NULL DEFAULT '',
    returned_at  TEXT NOT NULL,
    UNIQUE(session_id, pattern_id)
);
CREATE INDEX IF NOT EXISTS idx_session_pattern_queries_session
    ON session_pattern_queries(session_id);
"""

_V36_DDL = ""  # Handled programmatically in _apply_v36()

_V37_DDL = """
CREATE TABLE IF NOT EXISTS cartridge_installations (
    project_id     TEXT NOT NULL,
    cartridge_name TEXT NOT NULL,
    source         TEXT NOT NULL DEFAULT 'server',
    status         TEXT NOT NULL DEFAULT 'enabled',
    server_url     TEXT,
    node_count     INTEGER NOT NULL DEFAULT 0,
    installed_at   TEXT NOT NULL,
    updated_at     TEXT,
    PRIMARY KEY (project_id, cartridge_name)
);
"""

_V38_DDL = """
ALTER TABLE cartridge_installations
    ADD COLUMN policy TEXT NOT NULL DEFAULT 'optional';
"""

_V39_DDL = """
CREATE TABLE IF NOT EXISTS worktree_leases (
    worktree_id  TEXT NOT NULL,
    project_id   TEXT NOT NULL,
    session_id   TEXT NOT NULL,
    pid          INTEGER NOT NULL,
    acquired_at  TEXT NOT NULL,
    heartbeat_at TEXT NOT NULL,
    expires_at   TEXT NOT NULL,
    PRIMARY KEY (worktree_id, project_id)
);
CREATE INDEX IF NOT EXISTS idx_worktree_leases_project ON worktree_leases(project_id);
"""

_V24_ALTER_TABLES = [
    "sessions",
    "journal_entries",
    "signals",
    "active_sessions",
    "pipeline_runs",
    "patterns",
    "artifacts",
    "story_stats",
    "session_records",
    "session_patterns",
    "session_corrections",
]

_V24_INDEX_TABLES = [
    "sessions",
    "signals",
    "pipeline_runs",
    "patterns",
    "artifacts",
]

_REQUIRED_CURRENT_COLUMNS: dict[str, set[str]] = {
    "artifacts": {"review_type", "work_item_id"},
    "story_stats": {"work_item_id"},
    "docs_sync": {"local_path", "remote_id", "url", "updated_at", "project_id"},
    "missions": {"project_id", "fix_version", "jira_key"},
    "agent_session_missions": {"project_id"},
    # active_mission: removed in v55 (RAISE-14643/S4) — no longer a required table
    "graph_nodes": {
        "project_id",
        "checkout_id",  # RAISE-15607
        "node_id",
        "node_type",
        "content",
        "source_file",
        "metadata_json",
        "release_id",
        "module_id",
        "always_on",
        "foundational",
        "graph_version",
    },
    "cartridge_installations": {
        "project_id",
        "cartridge_name",
        "source",
        "status",
        "node_count",
        "installed_at",
        "policy",
    },
    "graph_edges": {
        "project_id",
        "checkout_id",  # RAISE-15607
        "source_node_id",
        "target_node_id",
        "edge_type",
        "edge_key",
        "metadata_json",
        "source_file",
        "graph_version",
    },
    "portfolio_components": {"project_id", "id", "name", "domain"},
    "initiative_profiles": {
        "project_id",
        "initiative_key",
        "components_touched",
        "change_mode",
    },
    "portfolio_deps": {"project_id", "source", "target", "type"},
    "epic_profiles": {
        "project_id",
        "epic_key",
        "level",
        "components_touched",
        "change_mode",
    },
    "runtime_sessions": {
        "session_id",
        "project_id",
        "worktree_id",
        "alias",
        "harness",
        "state",
        "governance_session_id",
        "created_at",
        "updated_at",
    },
    "work_items": {
        "project_id",
        "description",
        "labels_json",
        "priority",
        "assignee",
        "fix_versions_json",
        "custom_fields_json",
    },
    "graph_node_annotations": {
        "project_id",
        "checkout_id",
        "node_id",
        "namespace",
        "payload_json",
        "created_at",
        "updated_at",
    },
    "port_allocations": {
        "project_id",
        "worktree_path",
        "base_port",
        "ports_json",
        "allocated_at",
    },
    "worktree_pause_states": {
        "project_id",
        "worktree_id",
        "paused",
        "updated_at",
    },
}


def validate_current_schema(
    conn: sqlite3.Connection, *, require_tables: bool = False
) -> list[str]:
    """Return structural schema problems that must not coexist with current version."""
    problems: list[str] = []
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    for table, required_columns in _REQUIRED_CURRENT_COLUMNS.items():
        if table not in existing:
            if require_tables:
                problems.append(f"missing table: {table}")
            continue
        columns = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        missing = sorted(required_columns - columns)
        if missing:
            problems.append(f"{table} missing columns: {', '.join(missing)}")
    return problems


def _apply_v24(conn: sqlite3.Connection) -> None:
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    existing_cols: dict[str, set[str]] = {}
    for t in existing:
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()}
        existing_cols[t] = cols

    for table in _V24_ALTER_TABLES:
        if table in existing and "project_id" not in existing_cols.get(table, set()):
            conn.execute(
                f"ALTER TABLE {table} ADD COLUMN project_id TEXT NOT NULL DEFAULT ''"
            )

    if "counters" in existing and "project_id" not in existing_cols.get(
        "counters", set()
    ):
        conn.executescript("""
            CREATE TABLE counters_new (
                project_id TEXT NOT NULL DEFAULT '',
                name  TEXT NOT NULL,
                value INTEGER NOT NULL,
                PRIMARY KEY (project_id, name)
            );
            INSERT INTO counters_new (project_id, name, value)
                SELECT '', name, value FROM counters;
            DROP TABLE counters;
            ALTER TABLE counters_new RENAME TO counters;
        """)

    if "pending_sync" in existing and "project_id" not in existing_cols.get(
        "pending_sync", set()
    ):
        conn.executescript("""
            CREATE TABLE pending_sync_new (
                project_id  TEXT NOT NULL DEFAULT '',
                id          INTEGER NOT NULL DEFAULT 1,
                timestamp   TEXT NOT NULL,
                graph_path  TEXT NOT NULL,
                node_count  INTEGER NOT NULL,
                edge_count  INTEGER NOT NULL,
                error       TEXT NOT NULL,
                PRIMARY KEY (project_id, id)
            );
            INSERT INTO pending_sync_new (project_id, id, timestamp, graph_path, node_count, edge_count, error)
                SELECT '', id, timestamp, graph_path, node_count, edge_count, error FROM pending_sync;
            DROP TABLE pending_sync;
            ALTER TABLE pending_sync_new RENAME TO pending_sync;
        """)

    for table in _V24_INDEX_TABLES:
        if table in existing:
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_project ON {table}(project_id)"
            )


def _apply_v26(conn: sqlite3.Connection) -> None:
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "graph_edges" in existing:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_graph_edges_pid_src"
            " ON graph_edges(project_id, source)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_graph_edges_pid_tgt"
            " ON graph_edges(project_id, target)"
        )
    if "graph_nodes" in existing:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_graph_nodes_pid_type"
            " ON graph_nodes(project_id, node_type)"
        )


def _apply_v28(conn: sqlite3.Connection) -> None:
    foreign_keys_enabled = bool(conn.execute("PRAGMA foreign_keys").fetchone()[0])
    if foreign_keys_enabled:
        conn.execute("PRAGMA foreign_keys=OFF")

    try:
        existing = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        existing_cols: dict[str, set[str]] = {}
        for table in existing:
            existing_cols[table] = {
                r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()
            }

        if "missions" in existing and "project_id" not in existing_cols.get(
            "missions", set()
        ):
            conn.execute("DROP TABLE IF EXISTS missions_new")
            conn.executescript("""
                CREATE TABLE missions_new (
                    project_id         TEXT NOT NULL DEFAULT '',
                    mission_id         TEXT NOT NULL,
                    name               TEXT NOT NULL,
                    status             TEXT NOT NULL DEFAULT 'active',
                    objectives         TEXT NOT NULL DEFAULT '[]',
                    linked_epics       TEXT NOT NULL DEFAULT '[]',
                    sessions           TEXT NOT NULL DEFAULT '[]',
                    learned_patterns   TEXT NOT NULL DEFAULT '[]',
                    scratch            INTEGER NOT NULL DEFAULT 0,
                    close_note         TEXT,
                    retrospective_path TEXT,
                    created_at         TEXT NOT NULL,
                    last_used_at       TEXT NOT NULL,
                    closed_at          TEXT,
                    PRIMARY KEY (project_id, mission_id)
                );
                INSERT INTO missions_new (
                    project_id, mission_id, name, status, objectives, linked_epics,
                    sessions, learned_patterns, scratch, close_note,
                    retrospective_path, created_at, last_used_at, closed_at
                )
                SELECT
                    '', mission_id, name, status, objectives, linked_epics,
                    sessions, learned_patterns, scratch, close_note,
                    retrospective_path, created_at, last_used_at, closed_at
                FROM missions;
                DROP TABLE missions;
                ALTER TABLE missions_new RENAME TO missions;
            """)

        if "active_mission" in existing and "project_id" not in existing_cols.get(
            "active_mission", set()
        ):
            conn.execute("DROP TABLE IF EXISTS active_mission_new")
            conn.executescript("""
                CREATE TABLE active_mission_new (
                    project_id TEXT NOT NULL DEFAULT '',
                    id         INTEGER NOT NULL DEFAULT 1 CHECK (id = 1),
                    mission_id TEXT NOT NULL,
                    PRIMARY KEY (project_id, id)
                );
                INSERT INTO active_mission_new (project_id, id, mission_id)
                    SELECT '', id, mission_id FROM active_mission;
                DROP TABLE active_mission;
                ALTER TABLE active_mission_new RENAME TO active_mission;
            """)

        if (
            "agent_session_missions" in existing
            and "project_id" not in existing_cols.get("agent_session_missions", set())
        ):
            conn.execute("DROP TABLE IF EXISTS agent_session_missions_new")
            conn.executescript("""
                CREATE TABLE agent_session_missions_new (
                    project_id    TEXT NOT NULL DEFAULT '',
                    cc_session_id TEXT NOT NULL,
                    mission_id    TEXT NOT NULL,
                    bound_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                    PRIMARY KEY (project_id, cc_session_id)
                );
                INSERT INTO agent_session_missions_new (
                    project_id, cc_session_id, mission_id, bound_at
                )
                SELECT '', cc_session_id, mission_id, bound_at
                FROM agent_session_missions;
                DROP TABLE agent_session_missions;
                ALTER TABLE agent_session_missions_new RENAME TO agent_session_missions;
            """)

        if "missions" in existing:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_missions_project_status"
                " ON missions(project_id, status)"
            )
        if "active_mission" in existing:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_active_mission_project"
                " ON active_mission(project_id)"
            )
        if "agent_session_missions" in existing:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_agent_session_missions_project"
                " ON agent_session_missions(project_id)"
            )
    finally:
        if foreign_keys_enabled:
            conn.execute("PRAGMA foreign_keys=ON")


def _apply_v29(conn: sqlite3.Connection) -> None:
    """Add CHECK(length(project_id) > 0) to mission tables.

    Prevents silent insertion of orphan rows when a stale code path
    omits project_id (root cause: editable install pointing to worktree,
    2026-05-19 debug session).
    """
    foreign_keys_enabled = bool(conn.execute("PRAGMA foreign_keys").fetchone()[0])
    if foreign_keys_enabled:
        conn.execute("PRAGMA foreign_keys=OFF")

    try:
        existing = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        # Guard: skip if CHECK already present (idempotent on fast-path re-runs).
        if "missions" in existing:
            ddl = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='missions'"
            ).fetchone()[0]
            if "CHECK" in ddl:
                return

        if "missions" in existing:
            conn.execute("DROP TABLE IF EXISTS missions_v29")
            conn.executescript("""
                CREATE TABLE missions_v29 (
                    project_id         TEXT NOT NULL CHECK(length(project_id) > 0),
                    mission_id         TEXT NOT NULL,
                    name               TEXT NOT NULL,
                    status             TEXT NOT NULL DEFAULT 'active',
                    objectives         TEXT NOT NULL DEFAULT '[]',
                    linked_epics       TEXT NOT NULL DEFAULT '[]',
                    sessions           TEXT NOT NULL DEFAULT '[]',
                    learned_patterns   TEXT NOT NULL DEFAULT '[]',
                    scratch            INTEGER NOT NULL DEFAULT 0,
                    close_note         TEXT,
                    retrospective_path TEXT,
                    created_at         TEXT NOT NULL,
                    last_used_at       TEXT NOT NULL,
                    closed_at          TEXT,
                    PRIMARY KEY (project_id, mission_id)
                );
                INSERT INTO missions_v29
                    SELECT * FROM missions WHERE length(project_id) > 0;
                DROP TABLE missions;
                ALTER TABLE missions_v29 RENAME TO missions;
                CREATE INDEX IF NOT EXISTS idx_missions_project_status
                    ON missions(project_id, status);
            """)

        if "active_mission" in existing:
            conn.execute("DROP TABLE IF EXISTS active_mission_v29")
            conn.executescript("""
                CREATE TABLE active_mission_v29 (
                    project_id TEXT NOT NULL CHECK(length(project_id) > 0),
                    id         INTEGER NOT NULL DEFAULT 1 CHECK (id = 1),
                    mission_id TEXT NOT NULL,
                    PRIMARY KEY (project_id, id)
                );
                INSERT INTO active_mission_v29
                    SELECT * FROM active_mission WHERE length(project_id) > 0;
                DROP TABLE active_mission;
                ALTER TABLE active_mission_v29 RENAME TO active_mission;
                CREATE INDEX IF NOT EXISTS idx_active_mission_project
                    ON active_mission(project_id);
            """)

        if "agent_session_missions" in existing:
            conn.execute("DROP TABLE IF EXISTS agent_session_missions_v29")
            conn.executescript("""
                CREATE TABLE agent_session_missions_v29 (
                    project_id    TEXT NOT NULL CHECK(length(project_id) > 0),
                    cc_session_id TEXT NOT NULL,
                    mission_id    TEXT NOT NULL,
                    bound_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                    PRIMARY KEY (project_id, cc_session_id)
                );
                INSERT INTO agent_session_missions_v29
                    SELECT * FROM agent_session_missions WHERE length(project_id) > 0;
                DROP TABLE agent_session_missions;
                ALTER TABLE agent_session_missions_v29 RENAME TO agent_session_missions;
                CREATE INDEX IF NOT EXISTS idx_agent_session_missions_project
                    ON agent_session_missions(project_id);
            """)
    finally:
        if foreign_keys_enabled:
            conn.execute("PRAGMA foreign_keys=ON")


# _apply_v30 runs on EVERY create_all() (fast path, schema.py create_all), and it
# recreates the graph tables when their DDL does not match what it expects. It
# must therefore accept every primary key shape the graph tables can legitimately
# have — the pre-V68 one and the checkout-scoped V68 one. Listing only one shape
# makes the other look stale and silently DROPs a live keyspace (RAISE-15607).
_ACCEPTED_GRAPH_PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "graph_nodes": (
        "PRIMARY KEY (project_id, node_id)",
        "PRIMARY KEY (project_id, checkout_id, node_id)",
    ),
    "graph_edges": (
        "PRIMARY KEY (project_id, source_node_id, target_node_id, edge_type, edge_key)",
        "PRIMARY KEY (project_id, checkout_id, source_node_id, target_node_id,"
        " edge_type, edge_key)",
    ),
}

# Columns _apply_v30 requires to consider the graph tables non-stale. This is
# deliberately the PRE-V68 column set: a v67 DB legitimately has no checkout_id,
# and dropping its tables here would move the wipe out of the migration that owns
# it. _REQUIRED_CURRENT_COLUMNS (validated after migration) carries checkout_id.
_V30_GRAPH_COLUMNS: dict[str, set[str]] = {
    "graph_nodes": {
        "project_id",
        "node_id",
        "node_type",
        "content",
        "source_file",
        "metadata_json",
        "release_id",
        "module_id",
        "always_on",
        "foundational",
        "graph_version",
    },
    "graph_edges": {
        "project_id",
        "source_node_id",
        "target_node_id",
        "edge_type",
        "edge_key",
        "metadata_json",
        "source_file",
        "graph_version",
    },
}


def _apply_v30(conn: sqlite3.Connection) -> None:
    """Restore canonical graph tables, replacing stale pre-V27 shapes if present.

    A V68 DB is NOT stale here: the checkout-scoped primary key is an accepted
    shape. When this function does drop and recreate, it recreates the pre-V68
    shape and ``_apply_v68`` (which always runs after it, both in the migration
    chain and in the ``create_all()`` fast path) restores the checkout scope.
    """
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    stale_graph_tables = False
    for table in ("graph_nodes", "graph_edges"):
        if table not in existing:
            continue
        columns = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if not _V30_GRAPH_COLUMNS[table].issubset(columns):
            stale_graph_tables = True
            break
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()[0]
        normalized = " ".join(ddl.split())
        accepted = _ACCEPTED_GRAPH_PRIMARY_KEYS[table]
        if "CHECK(length(project_id) > 0)" not in ddl or not any(
            " ".join(pk.split()) in normalized for pk in accepted
        ):
            stale_graph_tables = True
            break

    if stale_graph_tables:
        conn.executescript("""
            DROP INDEX IF EXISTS idx_graph_edges_pid_src;
            DROP INDEX IF EXISTS idx_graph_edges_pid_tgt;
            DROP INDEX IF EXISTS idx_graph_nodes_pid_type;
            DROP INDEX IF EXISTS idx_graph_nodes_type;
            DROP INDEX IF EXISTS idx_graph_edges_source;
            DROP INDEX IF EXISTS idx_graph_edges_target;
            DROP INDEX IF EXISTS idx_graph_nodes_project_type;
            DROP INDEX IF EXISTS idx_graph_nodes_project_always_on;
            DROP INDEX IF EXISTS idx_graph_nodes_project_foundational;
            DROP INDEX IF EXISTS idx_graph_nodes_project_release;
            DROP INDEX IF EXISTS idx_graph_nodes_project_source;
            DROP INDEX IF EXISTS idx_graph_edges_project_source;
            DROP INDEX IF EXISTS idx_graph_edges_project_target;
            DROP INDEX IF EXISTS idx_graph_edges_project_type;
            DROP TABLE IF EXISTS graph_edges;
            DROP TABLE IF EXISTS graph_nodes;
        """)

    _execute_ddl(conn, _V30_DDL)


def _apply_v32(conn: sqlite3.Connection) -> None:
    """Add token_summary_json to session_records if the table exists."""
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "session_records" not in existing:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(session_records)").fetchall()}
    if "token_summary_json" not in cols:
        conn.execute(
            "ALTER TABLE session_records ADD COLUMN token_summary_json TEXT NOT NULL DEFAULT '{}'"
        )


def _apply_v34(conn: sqlite3.Connection) -> None:
    """Add archived column to patterns table if it exists."""
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "patterns" not in existing:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(patterns)").fetchall()}
    if "archived" not in cols:
        conn.execute(
            "ALTER TABLE patterns ADD COLUMN archived INTEGER NOT NULL DEFAULT 0"
        )


def _apply_v36(conn: sqlite3.Connection) -> None:
    """Add mission_id column to worktrees table if not already present."""
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "worktrees" not in tables:
        return  # table absent (partial schema) — validate_current_schema will report it
    cols = {r[1] for r in conn.execute("PRAGMA table_info(worktrees)").fetchall()}
    if "mission_id" not in cols:
        conn.execute(
            "ALTER TABLE worktrees ADD COLUMN mission_id TEXT NOT NULL DEFAULT ''"
        )


def _apply_v40(conn: sqlite3.Connection) -> None:
    """Add progress cache columns to missions table if it exists (ADR-099)."""
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "missions" not in tables:
        return  # partial schema in migration tests — skip gracefully
    cols = {r[1] for r in conn.execute("PRAGMA table_info(missions)").fetchall()}
    if "progress_done" not in cols:
        conn.execute("ALTER TABLE missions ADD COLUMN progress_done INT")
    if "progress_total" not in cols:
        conn.execute("ALTER TABLE missions ADD COLUMN progress_total INT")
    if "progress_cached_at" not in cols:
        conn.execute("ALTER TABLE missions ADD COLUMN progress_cached_at TEXT")


def _apply_v41(conn: sqlite3.Connection) -> None:
    """Scope active_sessions per agent — add cc_session_id column."""
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "active_sessions" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(active_sessions)").fetchall()}
    if "cc_session_id" not in cols:
        conn.execute(
            "ALTER TABLE active_sessions ADD COLUMN cc_session_id TEXT NOT NULL DEFAULT ''"
        )


_V42_DDL = ""  # Handled programmatically in _apply_v42()


def _apply_v42(conn: sqlite3.Connection) -> None:
    """Add sync_state marker column to pipeline_runs for S8371.2 local buffer.

    sync_state TEXT nullable: NULL = synced, 'pending' = needs push to server,
    'pending_delete' = needs server delete.

    SQLite does not support ALTER TABLE ADD COLUMN IF NOT EXISTS, so we guard
    by inspecting PRAGMA table_info before issuing the ALTER.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "pipeline_runs" not in tables:
        return  # partial schema in migration tests — skip gracefully
    cols = {r[1] for r in conn.execute("PRAGMA table_info(pipeline_runs)").fetchall()}
    if "sync_state" not in cols:
        conn.execute("ALTER TABLE pipeline_runs ADD COLUMN sync_state TEXT")
    # Partial index — CREATE INDEX IF NOT EXISTS is idempotent
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_pipeline_runs_pending"
        " ON pipeline_runs(project_id, sync_state) WHERE sync_state IS NOT NULL"
    )


_V43_DDL = ""  # Handled programmatically in _apply_v43()

_V45_DDL = ""  # Handled programmatically in _apply_v45()

_V46_DDL = ""  # Handled programmatically in _apply_v46()

_V47_DDL = ""  # Handled programmatically in _apply_v47()

_V48_DDL = ""  # Handled programmatically in _apply_v48()

_V49_DDL = """
CREATE TABLE IF NOT EXISTS session_ledger_entries (
    session_id   TEXT NOT NULL,
    natural_key  TEXT NOT NULL,
    kind         TEXT NOT NULL,
    project_id   TEXT,
    timestamp    TEXT NOT NULL,
    fields_json  TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (session_id, natural_key)
);
-- idx_ledger_session intentionally omitted (AR F4, RAISE-13146): the PK
-- (session_id, natural_key) already provides a leftmost-prefix index on
-- session_id, so a standalone index on that column is dead weight.
CREATE INDEX IF NOT EXISTS idx_ledger_kind ON session_ledger_entries(kind);
"""

_V50_DDL = ""  # Handled programmatically in _apply_v50() (missions.jira_key)

_V51_DDL = ""  # Handled programmatically in _apply_v51() (patterns.content_hash)

_V52_DDL = ""  # Handled programmatically in _apply_v52() (defensive UNIQUE index)

_V53_DDL = ""  # programmatic — see _apply_v53 (work_items table, RAISE-14640/S1)

_V54_DDL = """
CREATE TABLE IF NOT EXISTS graph_builds (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   TEXT NOT NULL DEFAULT '',
    built_at     TEXT NOT NULL,
    node_count   INTEGER NOT NULL DEFAULT 0,
    symbol_depth TEXT NOT NULL DEFAULT 'functions'
);
CREATE INDEX IF NOT EXISTS idx_graph_builds_project
    ON graph_builds(project_id, built_at);
"""

_V55_DDL = ""  # programmatic — see _apply_v55 (ADR-130 D2/D5, RAISE-14643/S4)

_V56_DDL = ""  # programmatic — see _apply_v56 (work_items_outbox + FK columns, RAISE-14649/S10)

_V57_DDL = (
    ""  # programmatic — see _apply_v57 (project-scoped artifact identity, RAISE-14954)
)

_V58_DDL = ""  # programmatic — see _apply_v58 (review artifact identity)

_V59_DDL = ""  # programmatic — see _apply_v59 (worktree attribution, RAISE-15003)

_V60_DDL = ""  # programmatic — see _apply_v60 (ledger stack elimination, RAISE-15135)

_V65_DDL = """
CREATE TABLE IF NOT EXISTS distillation_runs (
    session_id        TEXT PRIMARY KEY,
    date              TEXT NOT NULL,
    project           TEXT NOT NULL DEFAULT '',
    runtime           TEXT NOT NULL DEFAULT 'claude-code',
    turns_total       INTEGER NOT NULL DEFAULT 0,
    decisions_count   INTEGER NOT NULL DEFAULT 0,
    corrections_count INTEGER NOT NULL DEFAULT 0,
    patterns_count    INTEGER NOT NULL DEFAULT 0,
    blockers_count    INTEGER NOT NULL DEFAULT 0,
    tool_use_count    INTEGER NOT NULL DEFAULT 0,
    journal_path      TEXT NOT NULL DEFAULT '',
    journal_md        TEXT NOT NULL DEFAULT '',
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

_V66_DDL = """
CREATE TABLE IF NOT EXISTS session_developer_turns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL,
    turn_idx     INTEGER NOT NULL,
    content      TEXT NOT NULL DEFAULT '',
    turn_class   TEXT NOT NULL DEFAULT 'NEUTRAL',
    skill_name   TEXT NOT NULL DEFAULT '',
    occurred_at  TEXT,
    ingested_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(session_id, turn_idx)
);

CREATE TABLE IF NOT EXISTS evasion_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT NOT NULL,
    evasion_type     TEXT NOT NULL DEFAULT 'GATE_EVASION'
                         CHECK(evasion_type IN ('GATE_EVASION', 'BYPASS_FLAG', 'OMISSION_EVASION')),
    gate_name        TEXT NOT NULL DEFAULT '',
    tool_use_id      TEXT NOT NULL DEFAULT '',
    gate_turn_idx    INTEGER NOT NULL DEFAULT 0,
    failure_turn_idx INTEGER NOT NULL DEFAULT 0,
    pivot_turn_idx   INTEGER NOT NULL DEFAULT 0,
    resolved         INTEGER NOT NULL DEFAULT 0,
    severity         TEXT NOT NULL DEFAULT 'HIGH',
    error_snippet    TEXT NOT NULL DEFAULT '',
    occurred_at      TEXT,
    ingested_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS proposed_patterns (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name       TEXT NOT NULL DEFAULT '',
    cluster_theme    TEXT NOT NULL,
    correction_count INTEGER NOT NULL DEFAULT 0,
    sample_keys      TEXT NOT NULL DEFAULT '[]',
    status           TEXT NOT NULL DEFAULT 'pending'
                         CHECK(status IN ('pending', 'accepted', 'rejected')),
    pattern_id       TEXT NOT NULL DEFAULT '',
    occurred_window  TEXT NOT NULL DEFAULT '',
    reviewed_at      TEXT,
    ingested_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE VIEW IF NOT EXISTS skill_corrections AS
SELECT
    id, session_id, turn_idx, content AS correction,
    skill_name, occurred_at, ingested_at
FROM session_developer_turns
WHERE turn_class = 'CORRECTION'
  AND skill_name != ''
"""


_V67_DDL = ""  # programmatic — see _apply_v67 (session scope attribution, RAISE-15463)

_V68_DDL = ""  # programmatic — see _apply_v68 (checkout-scoped graph, RAISE-15607)

_V69_DDL = (
    ""  # programmatic — see _apply_v69 (pipeline run status normalization, RAISE-15795)
)

_V70_DDL = """
CREATE TABLE IF NOT EXISTS mcp_server_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event       TEXT NOT NULL,
    pid         INTEGER NOT NULL,
    server_root TEXT NOT NULL DEFAULT '',
    version     TEXT NOT NULL DEFAULT '',
    transport   TEXT NOT NULL DEFAULT '',
    session_id  TEXT NOT NULL DEFAULT '',
    recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_mcp_server_events_session
    ON mcp_server_events(session_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_mcp_server_events_event
    ON mcp_server_events(event, recorded_at);
"""

_V71_DDL = ""  # programmatic — see _apply_v71 (runtime_sessions table, RAISE-15839/S1)
_V74_DDL = (
    ""  # programmatic — see _apply_v74 (work_items project_id + data cols, RAISE-16622)
)

# Canonical (post-V68) graph keyspace: keyed by (project_id, checkout_id, ...).
# `checkout_id` is the resolved checkout root path; '' means repo-wide (cartridge
# nodes, shared by every checkout of the project). See RAISE-15607 / ADR.
_V68_GRAPH_DDL = """
CREATE TABLE IF NOT EXISTS graph_nodes (
    project_id     TEXT NOT NULL CHECK(length(project_id) > 0),
    checkout_id    TEXT NOT NULL DEFAULT '',
    node_id        TEXT NOT NULL,
    node_type      TEXT NOT NULL DEFAULT '',
    content        TEXT NOT NULL DEFAULT '',
    source_file    TEXT NOT NULL DEFAULT '',
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    release_id     TEXT NOT NULL DEFAULT '',
    module_id      TEXT NOT NULL DEFAULT '',
    always_on      INTEGER NOT NULL DEFAULT 0,
    foundational   INTEGER NOT NULL DEFAULT 0,
    graph_version  INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, checkout_id, node_id)
);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_type
    ON graph_nodes(project_id, checkout_id, node_type);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_always_on
    ON graph_nodes(project_id, checkout_id, always_on);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_foundational
    ON graph_nodes(project_id, checkout_id, foundational);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_release
    ON graph_nodes(project_id, checkout_id, release_id);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_project_source
    ON graph_nodes(project_id, checkout_id, source_file);

CREATE TABLE IF NOT EXISTS graph_edges (
    project_id      TEXT NOT NULL CHECK(length(project_id) > 0),
    checkout_id     TEXT NOT NULL DEFAULT '',
    source_node_id  TEXT NOT NULL,
    target_node_id  TEXT NOT NULL,
    edge_type       TEXT NOT NULL DEFAULT '',
    edge_key        TEXT NOT NULL DEFAULT '0',
    metadata_json   TEXT NOT NULL DEFAULT '{}',
    source_file     TEXT NOT NULL DEFAULT '',
    graph_version   INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, checkout_id, source_node_id, target_node_id, edge_type, edge_key)
);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_source
    ON graph_edges(project_id, checkout_id, source_node_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_target
    ON graph_edges(project_id, checkout_id, target_node_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_project_type
    ON graph_edges(project_id, checkout_id, edge_type);
"""

_V68_GRAPH_BUILDS_DDL = """
CREATE TABLE IF NOT EXISTS graph_builds (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   TEXT NOT NULL DEFAULT '',
    checkout_id  TEXT NOT NULL DEFAULT '',
    built_at     TEXT NOT NULL,
    node_count   INTEGER NOT NULL DEFAULT 0,
    symbol_depth TEXT NOT NULL DEFAULT 'functions'
);
CREATE INDEX IF NOT EXISTS idx_graph_builds_project
    ON graph_builds(project_id, built_at);
CREATE INDEX IF NOT EXISTS idx_graph_builds_checkout
    ON graph_builds(project_id, checkout_id, built_at);
"""

# RAISE-16596: durable node annotations, separated from the rebuildable
# graph_nodes.metadata_json blob. persist()/upsert_nodes() (graph_nodes'
# writers) never touch this table — that separation IS the fix. A rebuild
# (GraphAutoUpdateHook, or any future GraphBuilder.build() -> persist()
# call) can freely DELETE+INSERT graph_nodes without risk of destroying a
# curated/derived annotation, because the annotation was never in that row.
#
# namespace lets multiple independent writers (ddd today, future review/
# ownership/security annotations) share the table without collision; each
# owns its own namespace and its own payload shape. checkout_id follows the
# same REPO_WIDE-vs-checkout-scope convention as graph_nodes — a writer
# chooses per namespace (ddd writes REPO_WIDE: classification is a property
# of the symbol's content, not the worktree; see ddd_content_hash for the
# staleness guard that makes sharing safe).
_V72_DDL = """
CREATE TABLE IF NOT EXISTS graph_node_annotations (
    project_id     TEXT NOT NULL CHECK(length(project_id) > 0),
    checkout_id    TEXT NOT NULL DEFAULT '',
    node_id        TEXT NOT NULL,
    namespace      TEXT NOT NULL,
    payload_json   TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, checkout_id, node_id, namespace)
);
CREATE INDEX IF NOT EXISTS idx_graph_node_annotations_lookup
    ON graph_node_annotations(project_id, checkout_id, node_id);
CREATE INDEX IF NOT EXISTS idx_graph_node_annotations_namespace
    ON graph_node_annotations(project_id, checkout_id, namespace);
"""

_V73_DDL = """
CREATE TABLE IF NOT EXISTS port_allocations (
    project_id    TEXT NOT NULL CHECK(length(project_id) > 0),
    worktree_path TEXT NOT NULL,
    base_port     INTEGER NOT NULL,
    ports_json    TEXT NOT NULL DEFAULT '{}',
    allocated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (project_id, worktree_path)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_port_allocations_base
    ON port_allocations(base_port);
"""

_V75_DDL = (
    ""  # programmatic — see _apply_v75 (signals.signal_schema_version, RAISE-16689)
)

_V76_DDL = """
CREATE TABLE IF NOT EXISTS worktree_pause_states (
    project_id  TEXT NOT NULL,
    worktree_id TEXT NOT NULL,
    paused      INTEGER NOT NULL DEFAULT 0,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (project_id, worktree_id)
);
CREATE INDEX IF NOT EXISTS idx_worktree_pause_project
    ON worktree_pause_states(project_id);
"""

_V77_DDL = """
CREATE TABLE IF NOT EXISTS cc_token_daily (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    cc_session_id     TEXT NOT NULL,
    date              TEXT NOT NULL,
    source            TEXT NOT NULL DEFAULT 'stats-cache',
    output_tokens     INTEGER NOT NULL DEFAULT 0,
    estimated_cost_usd REAL NOT NULL DEFAULT 0,
    models_json       TEXT NOT NULL DEFAULT '{}',
    epic              TEXT NOT NULL DEFAULT 'unknown',
    epic_source       TEXT NOT NULL DEFAULT 'git',
    prompts           INTEGER NOT NULL DEFAULT 0,
    sessions_count    INTEGER NOT NULL DEFAULT 1,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(cc_session_id, date)
);
"""

_V78_DDL = """
ALTER TABLE graph_node_annotations ADD COLUMN written_by_checkout TEXT;
ALTER TABLE graph_node_annotations ADD COLUMN written_at_ms INTEGER;
"""

_V79_DDL = "ALTER TABLE graph_node_annotations ADD COLUMN ddd_tactical_type TEXT;"

_V68_GRAPH_INDEX_DROPS = """
DROP INDEX IF EXISTS idx_graph_nodes_project_type;
DROP INDEX IF EXISTS idx_graph_nodes_project_always_on;
DROP INDEX IF EXISTS idx_graph_nodes_project_foundational;
DROP INDEX IF EXISTS idx_graph_nodes_project_release;
DROP INDEX IF EXISTS idx_graph_nodes_project_source;
DROP INDEX IF EXISTS idx_graph_edges_project_source;
DROP INDEX IF EXISTS idx_graph_edges_project_target;
DROP INDEX IF EXISTS idx_graph_edges_project_type;
DROP INDEX IF EXISTS idx_graph_nodes_pid_type;
DROP INDEX IF EXISTS idx_graph_edges_pid_src;
DROP INDEX IF EXISTS idx_graph_edges_pid_tgt;
"""


_V61_DDL = """
CREATE TABLE IF NOT EXISTS portfolio_components (
    project_id  TEXT NOT NULL,
    id          TEXT NOT NULL,
    name        TEXT NOT NULL,
    domain      TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    layer       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (project_id, id)
);
CREATE TABLE IF NOT EXISTS initiative_profiles (
    project_id         TEXT NOT NULL,
    initiative_key     TEXT NOT NULL,
    components_touched TEXT NOT NULL DEFAULT '[]',
    change_mode        TEXT NOT NULL DEFAULT '',
    contracts_affected TEXT NOT NULL DEFAULT '[]',
    rationale          TEXT NOT NULL DEFAULT '',
    created_at         TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (project_id, initiative_key)
);
CREATE TABLE IF NOT EXISTS portfolio_deps (
    project_id   TEXT NOT NULL,
    source       TEXT NOT NULL,
    target       TEXT NOT NULL,
    type         TEXT NOT NULL,
    rationale    TEXT NOT NULL DEFAULT '',
    confirmed_by TEXT NOT NULL DEFAULT '',
    confirmed_at TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (project_id, source, target, type)
)
"""

_V62_DDL = """
CREATE TABLE IF NOT EXISTS pipeline_backlog_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  TEXT NOT NULL DEFAULT '',
    run_id      TEXT NOT NULL,
    phase_id    TEXT NOT NULL,
    issue_key   TEXT NOT NULL,
    from_status TEXT NOT NULL DEFAULT '',
    to_slug     TEXT NOT NULL DEFAULT '',
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pipeline_backlog_events_run
    ON pipeline_backlog_events(project_id, run_id, phase_id, issue_key);
"""

_V63_DDL = """
CREATE TABLE IF NOT EXISTS epic_profiles (
    project_id         TEXT NOT NULL,
    epic_key           TEXT NOT NULL,
    level              TEXT NOT NULL DEFAULT 'epic',
    components_touched TEXT NOT NULL DEFAULT '[]',
    change_mode        TEXT NOT NULL DEFAULT '',
    created_at         TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (project_id, epic_key)
)
"""

_V64_DDL = (
    ""  # programmatic — see _apply_v64 (active_sessions.worktree_id, RAISE-15131)
)


def _apply_v55(conn: sqlite3.Connection) -> None:
    """ADR-130 D2/D5: worktrees.workitem_id, DROP active_mission, CREATE agent_session_workitems.

    Three operations:
    1. ADD COLUMN worktrees.workitem_id TEXT DEFAULT '' (guarded via PRAGMA table_info)
    2. DROP TABLE IF EXISTS active_mission (zero SELECT callers in prod — safe)
    3. CREATE TABLE agent_session_workitems + seed from agent_session_missions
       (LEFT JOIN missions.jira_key -> work_items.id; workitem_id='' when no match)

    S4 (RAISE-14643): resolver seam plumbing only. workitem_id path is dormant until
    S7 adds 'rai worktree register --work-item'. agent_session_missions preserved until S7.
    """
    # Pre-compute table inventory — used for guards in steps 1 and 4.
    # Both worktrees (step 1) and agent_session_missions (step 4) may not
    # exist on very old DBs that are migrating up through many versions.
    existing_tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    # 1 — ADD COLUMN (guard: SQLite has no ALTER TABLE ADD COLUMN IF NOT EXISTS)
    if "worktrees" in existing_tables:
        existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(worktrees)")}
        if "workitem_id" not in existing_cols:
            conn.execute("ALTER TABLE worktrees ADD COLUMN workitem_id TEXT DEFAULT ''")

    # 2 — DROP active_mission (vestigial singleton, never SELECT'd in prod)
    conn.execute("DROP TABLE IF EXISTS active_mission")

    # 3 — CREATE agent_session_workitems
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_session_workitems (
            project_id    TEXT NOT NULL DEFAULT '',
            cc_session_id TEXT NOT NULL,
            workitem_id   TEXT NOT NULL DEFAULT '',
            is_primary    INTEGER NOT NULL DEFAULT 0,
            bound_at      TEXT NOT NULL
                          DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
            PRIMARY KEY (project_id, cc_session_id)
        )
        """
    )

    # 4 — Seed from agent_session_missions (workitem_id='' when no match).
    if "agent_session_missions" in existing_tables:
        conn.execute(
            """
            INSERT OR IGNORE INTO agent_session_workitems
                (project_id, cc_session_id, workitem_id)
            SELECT
                asm.project_id,
                asm.cc_session_id,
                COALESCE(wi.id, '') AS workitem_id
            FROM agent_session_missions asm
            LEFT JOIN missions m
                ON m.project_id = asm.project_id
                AND m.mission_id = asm.mission_id
            LEFT JOIN work_items wi
                ON wi.jira_key = m.jira_key
                AND m.jira_key IS NOT NULL
            """
        )
    conn.commit()


def _apply_v56(conn: sqlite3.Connection) -> None:
    """S10 (RAISE-14649): work_items_outbox table + work_item_id FK columns.

    Three operations:
    1. CREATE TABLE IF NOT EXISTS work_items_outbox (idempotent)
    2. ALTER TABLE story_stats ADD COLUMN work_item_id TEXT (guarded)
    3. ALTER TABLE artifacts ADD COLUMN work_item_id TEXT (guarded)
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_items_outbox (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id  TEXT NOT NULL,
            jira_key      TEXT,
            operation     TEXT NOT NULL,
            payload_json  TEXT NOT NULL DEFAULT '{}',
            status        TEXT NOT NULL DEFAULT 'pending',
            retries       INTEGER NOT NULL DEFAULT 0,
            max_retries   INTEGER NOT NULL DEFAULT 3,
            error_message TEXT,
            created_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_items_outbox_status "
        "ON work_items_outbox(status)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_items_outbox_work_item "
        "ON work_items_outbox(work_item_id)"
    )

    existing_tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "story_stats" in existing_tables:
        story_stats_cols = {
            r[1] for r in conn.execute("PRAGMA table_info(story_stats)")
        }
        if "work_item_id" not in story_stats_cols:
            conn.execute("ALTER TABLE story_stats ADD COLUMN work_item_id TEXT")

    if "artifacts" in existing_tables:
        artifacts_cols = {r[1] for r in conn.execute("PRAGMA table_info(artifacts)")}
        if "work_item_id" not in artifacts_cols:
            conn.execute("ALTER TABLE artifacts ADD COLUMN work_item_id TEXT")

    conn.commit()


def _apply_v57(conn: sqlite3.Connection) -> None:
    """Scope artifact uniqueness to the natural project/story/type identity."""
    artifacts = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='artifacts'"
    ).fetchone()
    if artifacts is None:
        return
    columns = {row[1] for row in conn.execute("PRAGMA table_info(artifacts)")}
    if "review_type" in columns:
        # V58+ owns artifact uniqueness once review_type exists. Recreating the
        # V57 index here would reject valid architecture + quality review rows
        # before _apply_v58 can restore the current index.
        return
    conn.execute("DROP INDEX IF EXISTS idx_artifacts_story_type")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_project_story_type "
        "ON artifacts(project_id, story_id, artifact_type)"
    )


def _apply_v58(conn: sqlite3.Connection) -> None:
    """Add review_type and scope artifact uniqueness to review identity."""
    artifacts = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='artifacts'"
    ).fetchone()
    if artifacts is None:
        return

    columns = {row[1] for row in conn.execute("PRAGMA table_info(artifacts)")}
    if "review_type" not in columns:
        _execute_ddl(
            conn,
            "ALTER TABLE artifacts ADD COLUMN review_type TEXT NOT NULL DEFAULT ''",
        )
        columns = {row[1] for row in conn.execute("PRAGMA table_info(artifacts)")}

    # V57 could persist review payloads, but did not persist their discriminator
    # as part of the relational identity. Backfill only valid review payloads;
    # malformed legacy rows retain the empty compatibility value.
    if "review_type" in columns:
        import json

        rows = conn.execute(
            "SELECT artifact_id, content_json FROM artifacts "
            "WHERE artifact_type = 'review' AND review_type = ''"
        ).fetchall()
        for artifact_id, content_json in rows:
            try:
                payload = json.loads(content_json)
            except (TypeError, json.JSONDecodeError):
                continue
            review_type = (
                payload.get("review_type") if isinstance(payload, dict) else None
            )
            if isinstance(review_type, str) and review_type:
                conn.execute(
                    "UPDATE artifacts SET review_type = ? WHERE artifact_id = ?",
                    (review_type, artifact_id),
                )

    conn.execute("DROP INDEX IF EXISTS idx_artifacts_project_story_type")
    conn.execute("DROP INDEX IF EXISTS idx_artifacts_story_type")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_project_story_type_review "
        "ON artifacts(project_id, story_id, artifact_type, review_type)"
    )


def _apply_v59(conn: sqlite3.Connection) -> None:
    """Add agent attribution columns to worktrees table (RAISE-15003, S2 of E14998).

    Three TEXT NOT NULL DEFAULT '' columns:
    - agent_id: agent session ID at registration time (discover_agent_session_id)
    - harness: agent runtime identifier (discover_agent_runtime)
    - parent_session_id: parent session ID for sub-agent attribution chains

    Guard: SQLite has no ALTER TABLE ADD COLUMN IF NOT EXISTS — use PRAGMA
    table_info before issuing each ALTER (PAT-E-1688).
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "worktrees" not in tables:
        return  # partial schema in migration tests — skip gracefully
    cols = {r[1] for r in conn.execute("PRAGMA table_info(worktrees)").fetchall()}
    if "agent_id" not in cols:
        conn.execute(
            "ALTER TABLE worktrees ADD COLUMN agent_id TEXT NOT NULL DEFAULT ''"
        )
    if "harness" not in cols:
        conn.execute(
            "ALTER TABLE worktrees ADD COLUMN harness TEXT NOT NULL DEFAULT ''"
        )
    if "parent_session_id" not in cols:
        conn.execute(
            "ALTER TABLE worktrees ADD COLUMN parent_session_id TEXT NOT NULL DEFAULT ''"
        )


def _apply_v60(conn: sqlite3.Connection) -> None:
    """Ledger stack elimination: seed work_items from ledger_entries, then drop it (RAISE-15135).

    Idempotent: INSERT OR IGNORE skips rows already in work_items; DROP TABLE IF EXISTS
    is a no-op when the table is gone. Type inferred from local_key pattern.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "ledger_entries" in tables:
        conn.execute(
            """
            INSERT OR IGNORE INTO work_items
                (id, type, local_key, jira_key, summary, status,
                 no_portfolio, created_at, updated_at)
            SELECT
                lower(hex(randomblob(8))),
                CASE
                    WHEN local_key GLOB 'E[0-9]*' THEN 'epic'
                    WHEN local_key GLOB 'S[0-9]*' THEN 'story'
                    ELSE 'story'
                END,
                local_key,
                jira_key,
                '',
                'todo',
                0,
                strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
            FROM ledger_entries
            WHERE local_key IS NOT NULL AND jira_key IS NOT NULL
            """
        )
    conn.execute("DROP TABLE IF EXISTS ledger_entries")
    conn.commit()


def _apply_v64(conn: sqlite3.Connection) -> None:
    """Add worktree_id column to active_sessions (RAISE-15131, S7 of E14777).

    Enables the Sessions tab to join active session pointers with worktree
    leases by a stable key instead of the fragile cc_session_id path.

    Guard: SQLite has no ALTER TABLE ADD COLUMN IF NOT EXISTS — use PRAGMA
    table_info before issuing the ALTER (PAT-E-1688).
    Best-effort backfill from worktree_leases via cc_session_id.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "active_sessions" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(active_sessions)").fetchall()}
    if "worktree_id" not in cols:
        conn.execute(
            "ALTER TABLE active_sessions ADD COLUMN worktree_id TEXT NOT NULL DEFAULT ''"
        )
    # Best-effort backfill: match via cc_session_id in worktree_leases
    if "worktree_leases" in tables:
        conn.execute("""
            UPDATE active_sessions
            SET worktree_id = COALESCE(
                (SELECT wl.worktree_id FROM worktree_leases wl
                 WHERE wl.session_id = active_sessions.cc_session_id
                   AND wl.project_id = active_sessions.project_id
                 LIMIT 1),
                ''
            )
            WHERE worktree_id = ''
        """)


def _apply_v67(conn: sqlite3.Connection) -> None:
    """Session scope attribution columns + backfill (S15456.1, RAISE-15463, E15456).

    Adds:
    - sessions.worktree_id TEXT NOT NULL DEFAULT ''
    - session_records.worktree_id / agent_session_id / branch TEXT NOT NULL DEFAULT ''

    Backfill signals (design v2), in precedence order:
    1. reverse-map via worktrees.last_session_id
    2. branch heuristic: sessions.branch matches a registered worktree's branch
    Rows with no signal keep worktree_id='' — they are UNATTRIBUTABLE history
    and MUST be excluded from future donor pools (D2; enforced in S15456.3).
    '' on a legacy row means "no scope evidence", not "verifiably main".
    Nothing is deleted.

    Guards: PRAGMA table_info before every ALTER (PAT-E-1688). The backfill
    only runs in the same call that adds the columns — create_all()'s
    fast-path re-runs this function on every open, and re-running the branch
    heuristic would misattribute post-V67 main-scope rows (legitimately '')
    to worktrees that happen to share their branch.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    added = False
    if "sessions" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()}
        if "worktree_id" not in cols:
            conn.execute(
                "ALTER TABLE sessions ADD COLUMN worktree_id TEXT NOT NULL DEFAULT ''"
            )
            added = True
    if "session_records" in tables:
        cols = {
            r[1] for r in conn.execute("PRAGMA table_info(session_records)").fetchall()
        }
        for col in ("worktree_id", "agent_session_id", "branch"):
            if col not in cols:
                conn.execute(
                    f"ALTER TABLE session_records ADD COLUMN {col} TEXT NOT NULL DEFAULT ''"
                )

    if not added:
        return  # columns already present — backfill ran with the original migration

    if "sessions" in tables and "worktrees" in tables:
        # Signal 1: reverse-map from worktrees.last_session_id
        conn.execute("""
            UPDATE sessions
            SET worktree_id = (
                SELECT w.worktree_id FROM worktrees w
                WHERE w.last_session_id = sessions.session_id
                  AND w.project_id = sessions.project_id
                LIMIT 1
            )
            WHERE worktree_id = ''
              AND EXISTS (
                  SELECT 1 FROM worktrees w
                  WHERE w.last_session_id = sessions.session_id
                    AND w.project_id = sessions.project_id
              )
            """)
        # Signal 2: branch heuristic — restricted to story/*/bug/* branches
        # (design D2): a worktree registered on a shared integration branch
        # (release/*, dev, main) must not mass-attribute main-checkout
        # sessions. Most recently registered worktree wins on collisions.
        conn.execute("""
            UPDATE sessions
            SET worktree_id = (
                SELECT w.worktree_id FROM worktrees w
                WHERE w.branch = sessions.branch
                  AND w.project_id = sessions.project_id
                ORDER BY w.created_at DESC
                LIMIT 1
            )
            WHERE worktree_id = ''
              AND branch != ''
              AND (sessions.branch LIKE 'story/%' OR sessions.branch LIKE 'bug/%')
              AND EXISTS (
                  SELECT 1 FROM worktrees w
                  WHERE w.branch = sessions.branch
                    AND w.project_id = sessions.project_id
              )
            """)

    if "session_records" in tables and "sessions" in tables:
        # session_records inherits attribution from its sessions row (FK).
        # NULL sessions.agent_session_id normalizes to '' (D1/D3).
        conn.execute("""
            UPDATE session_records
            SET worktree_id = (
                    SELECT s.worktree_id FROM sessions s
                    WHERE s.session_id = session_records.session_id
                      AND s.project_id = session_records.project_id
                ),
                branch = COALESCE((
                    SELECT s.branch FROM sessions s
                    WHERE s.session_id = session_records.session_id
                      AND s.project_id = session_records.project_id
                ), ''),
                agent_session_id = COALESCE((
                    SELECT s.agent_session_id FROM sessions s
                    WHERE s.session_id = session_records.session_id
                      AND s.project_id = session_records.project_id
                ), '')
            WHERE EXISTS (
                SELECT 1 FROM sessions s
                WHERE s.session_id = session_records.session_id
                  AND s.project_id = session_records.project_id
            )
            """)


def _apply_v68(conn: sqlite3.Connection) -> None:
    """Checkout-scoped graph keyspace (RAISE-15607).

    ``graph_nodes`` / ``graph_edges`` / ``graph_builds`` were keyed by
    ``project_id`` alone. ``project_id`` derives from ``.raise/manifest.yaml``
    (git-tracked), so every worktree and every clone of a repo resolves the SAME
    value and writes the SAME partition — ``persist()`` then deleted the other
    checkouts' rows and queries silently returned symbols from the wrong tree.
    This adds ``checkout_id``: the resolved checkout root path, or ``''`` for
    repo-wide rows (cartridge nodes, shared by every checkout).

    **Zero node/edge rows are migrated.** The pre-V68 partition is a
    last-writer-wins mixture of every checkout that ever built, and no
    authoritative provenance marker exists (the RAISE-15388 ``cartridge_name``
    guard matched zero live rows), so attributing legacy rows to any checkout
    would fabricate evidence. All content is regenerable: ``rai graph build``
    per checkout re-derives scan nodes, ``rai cartridge sync`` restores server
    cartridges.

    ``cartridge_installations`` is deliberately untouched — it stays keyed by
    ``project_id`` because installs are repo-wide.

    Idempotency (R1): every step is guarded on the presence of ``checkout_id``,
    and the staging table is dropped first so a crash mid-recreate re-runs
    cleanly. Fast-path replay (R4) is a no-op once the column exists.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    needs_rebuild = False
    for table in ("graph_nodes", "graph_edges"):
        if table not in tables:
            needs_rebuild = True
            continue
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if "checkout_id" not in cols:
            needs_rebuild = True

    if needs_rebuild:
        # create-copy-drop-rename, copying ZERO rows (see docstring).
        conn.executescript(f"""
            {_V68_GRAPH_INDEX_DROPS}
            DROP TABLE IF EXISTS graph_nodes;
            DROP TABLE IF EXISTS graph_edges;
        """)
        _execute_ddl(conn, _V68_GRAPH_DDL)

    if "graph_builds" not in tables:
        _execute_ddl(conn, _V68_GRAPH_BUILDS_DDL)
    else:
        cols = {
            r[1] for r in conn.execute("PRAGMA table_info(graph_builds)").fetchall()
        }
        if "checkout_id" not in cols:
            # Additive: legacy build records keep checkout_id='' and become
            # inert for per-checkout freshness/debounce reads, which is the
            # correct reading — their originating checkout is unknown.
            conn.execute(
                "ALTER TABLE graph_builds ADD COLUMN checkout_id TEXT NOT NULL DEFAULT ''"
            )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_graph_builds_checkout"
            " ON graph_builds(project_id, checkout_id, built_at)"
        )


def _apply_v69(conn: sqlite3.Connection) -> None:
    """Normalize pipeline run status 'started' -> 'running' (RAISE-15795).

    ``pipeline_runs.status`` had two spellings for the same "in progress"
    state: MCP-initiated runs wrote ``'started'`` (matching the DDL DEFAULT)
    while engine-initiated runs wrote ``'running'`` (``RunStatus.RUNNING``).
    This UPDATEs existing rows so every run uses ``'running'`` going forward;
    write sites are normalized in code separately. Table-existence guard
    prevents a crash on early-version DBs that migrate through v69 before
    ``pipeline_runs`` exists (mirrors the v68 guard pattern, PAT-E-9580).
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "pipeline_runs" not in tables:
        return
    conn.execute("UPDATE pipeline_runs SET status='running' WHERE status='started'")


def _apply_v71(conn: sqlite3.Connection) -> None:
    """Create runtime_sessions table with partial unique index on alias (RAISE-15839/S1).

    ``runtime_sessions`` tracks harness processes running under tmux.  It is
    intentionally separate from the ``sessions`` governance table — runtime
    sessions outlive governance sessions and require host-scope queries across
    worktrees (ADR-055 Phase-3 explicit deviation, documented in design).

    The partial unique index enforces alias uniqueness only among active rows
    (state IN ('provisioning', 'live')).  Exited rows may share the same alias
    with future provisioning rows.

    Guard: idempotent — safe to re-run on the fast-path.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runtime_sessions (
            session_id            TEXT NOT NULL PRIMARY KEY,
            project_id            TEXT NOT NULL,
            worktree_id           TEXT NOT NULL DEFAULT '',
            alias                 TEXT NOT NULL,
            harness               TEXT NOT NULL,
            state                 TEXT NOT NULL DEFAULT 'provisioning',
            governance_session_id TEXT,
            created_at            TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at            TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_runtime_sessions_alias_active
        ON runtime_sessions(alias)
        WHERE state IN ('provisioning', 'live')
        """
    )


def _apply_v74(conn: sqlite3.Connection) -> None:
    """Recreate `work_items` with project_id scoping + data columns; add child tables.

    RAISE-16622 (S16533.2, story design.md D-S2.1). SQLite cannot ALTER a CHECK
    constraint — adding 'bug' to the type enum forces a table recreation, so
    this single pass folds in `project_id` (MUST-ARCH-003: the shared
    ``~/.rai/raise.db`` has no project scoping on work_items today, D11) and
    six new data columns (description, labels_json, priority, assignee,
    fix_versions_json, custom_fields_json) at the same time.

    Idempotency guard: PRAGMA table_info probe for `project_id` (same idiom
    as `_apply_v24`/`_apply_v51`) — column-present implies the CHECK and both
    scoped indexes are present too, since recreation is a single atomic step.
    Crash-recovery: `DROP TABLE IF EXISTS work_items_v72` on entry clears any
    scratch table left by an interrupted prior run (V48 pattern).

    project_id backfill is explicitly NOT done here — existing rows land at
    `project_id=''` ("unattributed"); `rai backlog migrate` (S16533.4) claims
    rows per-project.

    FK ordering (story design.md V4): the three child tables
    (work_item_comments, work_item_links, work_item_changelog) declare
    `FOREIGN KEY (work_item_id) REFERENCES work_items(id)`. They are created
    AFTER the work_items recreation below — nothing today declares a FK
    *into* work_items (grepped: zero hits), so DROP/RENAME is safe. Any
    future migration that recreates work_items again must account for these
    FK children first (PRAGMA foreign_keys is a no-op inside this
    transaction, per SQLite semantics — it is not re-checked retroactively).

    No internal `conn.commit()` (D-S2.5) — `create_all()` wraps every
    migration in `with conn:`; a failure here rolls back cleanly.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "work_items" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(work_items)").fetchall()}
        if "project_id" not in cols:
            conn.execute("DROP TABLE IF EXISTS work_items_v72")
            conn.execute(
                """
                CREATE TABLE work_items_v72 (
                    id                  TEXT PRIMARY KEY,
                    type                TEXT NOT NULL
                        CHECK (type IN ('theme','initiative','epic','story','task','bug')),
                    project_id          TEXT NOT NULL DEFAULT '',
                    local_key           TEXT NOT NULL,
                    jira_key            TEXT,
                    parent_local_key    TEXT,
                    parent_jira_key     TEXT,
                    summary             TEXT NOT NULL DEFAULT '',
                    status              TEXT NOT NULL DEFAULT 'todo',
                    no_portfolio        INTEGER NOT NULL DEFAULT 0,
                    description         TEXT NOT NULL DEFAULT '',
                    labels_json         TEXT NOT NULL DEFAULT '[]',
                    priority            TEXT NOT NULL DEFAULT '',
                    assignee            TEXT NOT NULL DEFAULT '',
                    fix_versions_json   TEXT NOT NULL DEFAULT '[]',
                    custom_fields_json  TEXT NOT NULL DEFAULT '{}',
                    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
                    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                )
                """
            )
            conn.execute(
                """
                INSERT INTO work_items_v72
                    (id, type, project_id, local_key, jira_key, parent_local_key,
                     parent_jira_key, summary, status, no_portfolio,
                     created_at, updated_at)
                SELECT id, type, '', local_key, jira_key, parent_local_key,
                       parent_jira_key, summary, status, no_portfolio,
                       created_at, updated_at
                FROM work_items
                """
            )
            conn.execute("DROP TABLE work_items")
            conn.execute("ALTER TABLE work_items_v72 RENAME TO work_items")

        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_work_items_project_local "
            "ON work_items(project_id, local_key)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_work_items_project_jira "
            "ON work_items(project_id, jira_key) WHERE jira_key IS NOT NULL"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_work_items_parent_local "
            "ON work_items(parent_local_key)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_work_items_parent_jira "
            "ON work_items(parent_jira_key)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_work_items_type ON work_items(type)"
        )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_item_comments (
            id           TEXT PRIMARY KEY,
            work_item_id TEXT NOT NULL,
            body         TEXT NOT NULL DEFAULT '',
            author       TEXT NOT NULL DEFAULT '',
            created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            FOREIGN KEY (work_item_id) REFERENCES work_items(id)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_item_comments_item "
        "ON work_item_comments(work_item_id)"
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_item_links (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id TEXT NOT NULL,
            target_key   TEXT NOT NULL,
            link_type    TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (work_item_id) REFERENCES work_items(id),
            UNIQUE (work_item_id, target_key, link_type)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_item_links_item "
        "ON work_item_links(work_item_id)"
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_item_changelog (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id TEXT NOT NULL,
            field        TEXT NOT NULL,
            old_value    TEXT,
            new_value    TEXT,
            author       TEXT NOT NULL DEFAULT '',
            changed_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            FOREIGN KEY (work_item_id) REFERENCES work_items(id)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_item_changelog_item "
        "ON work_item_changelog(work_item_id)"
    )


def _apply_v75(conn: sqlite3.Connection) -> None:
    """Add signal_schema_version to signals table (RAISE-16689, S16430.1).

    Guard: table may not exist in partial-schema test fixtures.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "signals" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(signals)").fetchall()}
    if "signal_schema_version" not in cols:
        conn.execute("ALTER TABLE signals ADD COLUMN signal_schema_version TEXT")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_signals_schema_version"
        " ON signals(signal_schema_version) WHERE signal_schema_version IS NOT NULL"
    )


def _apply_v51(conn: sqlite3.Connection) -> None:
    """Add content_hash column + NON-unique index + NULL-only backfill (S14056.1, RAISE-14561).

    UNIQUE index is DEFERRED to S14056.2 (cannot create UNIQUE while dups
    exist in the live ~/.rai/raise.db — see design D2).
    Guard por PRAGMA table_info (PAT-E-1688): idempotente ante branches
    concurrentes; SQLite no soporta ADD COLUMN IF NOT EXISTS.
    Backfill reutiliza memory/content_hash.py::content_hash() (ADR-069) — NO
    se reimplementa el hash canónico (design D4/AG2 mitigation).
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "patterns" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(patterns)").fetchall()}
    if "content_hash" not in cols:
        conn.execute("ALTER TABLE patterns ADD COLUMN content_hash TEXT")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_content_hash "
        "ON patterns(project_id, content_hash)"
    )

    # Backfill NULL-only (idempotent, cheap re-run guard: WHERE content_hash IS NULL)
    import json

    from raise_cli.memory.content_hash import content_hash

    rows = conn.execute(
        "SELECT pattern_id, content, type, context_json FROM patterns "
        "WHERE content_hash IS NULL"
    ).fetchall()
    for pid, content, ptype, ctx_json in rows:
        ctx = json.loads(ctx_json) if ctx_json else []
        h = content_hash(content, ptype, ctx)
        try:
            conn.execute(
                "UPDATE patterns SET content_hash = ? WHERE pattern_id = ?",
                (h, pid),
            )
        except sqlite3.IntegrityError:
            # RAISE-16296: V52's partial UNIQUE index on (project_id, content_hash)
            # WHERE archived=0 may already contain this hash from a sibling row.
            # Archive the duplicate so it exits the partial index predicate.
            conn.execute(
                "UPDATE patterns SET content_hash = ?, archived = 1 "
                "WHERE pattern_id = ?",
                (h, pid),
            )


def _apply_v52(conn: sqlite3.Connection) -> None:
    """Índice UNIQUE (project_id, content_hash) — DEFENSIVO (S14056.2, RAISE-14579).

    Skip si hay dups activos (DB viva pre-dedup) para no romper create_all().
    Co-llamado por create_all() (fast-path) y por `rai memory dedup --apply`
    (mismo call-site, no clon — DD-2). `IF NOT EXISTS` lo hace idempotente
    entre ambos.

    Guard de columnas (además del guard de tabla): el fast-path de create_all()
    puede correr sobre un `patterns` parcialmente migrado (p.ej. tests que fuerzan
    user_version sin aplicar todas las ALTER TABLE intermedias) — sin `content_hash`
    (V50) o `archived` (V34) la query de dups explota con OperationalError.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "patterns" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(patterns)").fetchall()}
    if "content_hash" not in cols or "archived" not in cols:
        return
    dups = conn.execute(
        "SELECT 1 FROM patterns WHERE content_hash IS NOT NULL AND archived=0 "
        "GROUP BY project_id, content_hash HAVING COUNT(*) > 1 LIMIT 1"
    ).fetchone()
    if dups:
        logger.warning(
            "patterns: dups activos presentes — índice UNIQUE diferido. "
            "Corre `rai memory dedup --apply`."
        )
        return
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_patterns_content_hash_unique "
        "ON patterns(project_id, content_hash) "
        "WHERE content_hash IS NOT NULL AND archived = 0"
    )


def _apply_v53(conn: sqlite3.Connection) -> None:
    """Create `work_items` — local work-item registry (RAISE-14640, S1 of E10622).

    Create-only migration: every statement is `IF NOT EXISTS` / a
    partial-index, so it is idempotent by construction — no `PRAGMA
    table_info` pre-check needed (unlike `_apply_v51`, which does `ALTER
    TABLE ADD COLUMN`). DDL is copy-paste verbatim from
    `work/epics/e10622-local-work-item-registry/design.md` §2 (source of
    truth, ratified D0.1). S1 seeds nothing — seeding from
    `ledger_entries`/`missions` is S2.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS work_items (
            id                TEXT PRIMARY KEY,
            type              TEXT NOT NULL
                              CHECK (type IN ('theme','initiative','epic','story','task')),
            local_key         TEXT NOT NULL,
            jira_key          TEXT,
            parent_local_key  TEXT,
            parent_jira_key   TEXT,
            summary           TEXT NOT NULL DEFAULT '',
            status            TEXT NOT NULL DEFAULT 'todo',
            no_portfolio      INTEGER NOT NULL DEFAULT 0,
            created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        )
        """
    )
    # RAISE-16622 (V72) replaces these two global-UNIQUE indexes with
    # project_id-scoped equivalents (idx_work_items_project_local/_jira) once
    # `project_id` exists on the table. Guard so the create_all() fast path —
    # which re-runs _apply_v53 unconditionally on every process start,
    # ordered BEFORE _apply_v74 — does not resurrect the pre-V72 global
    # uniques (a regression of the exact bug V72 fixes, MUST-ARCH-003) on a
    # DB that has already been migrated past V72. On a genuinely pre-V72
    # table (project_id absent), this still creates them exactly as before —
    # historical migration behavior for the v0..SCHEMA_VERSION replay path is
    # unchanged; V72 drops this table (indexes included) and recreates it
    # scoped a few migrations later in the same transaction.
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    has_project_id = False
    if "work_items" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(work_items)").fetchall()}
        has_project_id = "project_id" in cols
    if not has_project_id:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_work_items_local_key "
            "ON work_items(local_key)"
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_work_items_jira_key "
            "ON work_items(jira_key) WHERE jira_key IS NOT NULL"
        )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_items_parent_local "
        "ON work_items(parent_local_key)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_work_items_parent_jira "
        "ON work_items(parent_jira_key)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_type ON work_items(type)")


def _apply_v48(conn: sqlite3.Connection) -> None:
    """Recrea introducer_attributions con UNIQUE(project_id, bug_key, fix_commit, introducer_commit, carril) — M1.

    Estrategia: create-new + copy + drop + rename.
    Guard de idempotencia via PRAGMA index_list/index_info:
    si el UNIQUE ya incluye bug_key y carril, V48 ya fue aplicada.
    """
    # Guard 1: tabla debe existir
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "introducer_attributions" not in tables:
        return

    # Guard 2 (idempotencia): UNIQUE ya incluye carril y bug_key → V48 aplicada
    for idx in conn.execute("PRAGMA index_list('introducer_attributions')").fetchall():
        if idx[2]:  # unique flag
            cols = {
                r[2] for r in conn.execute(f"PRAGMA index_info('{idx[1]}')").fetchall()
            }
            if "carril" in cols and "bug_key" in cols:
                return  # V48 ya aplicada — evita recreate

    # Recreate: create-new + copy + drop + rename
    conn.execute("DROP TABLE IF EXISTS introducer_attributions_v48")
    conn.execute("""
        CREATE TABLE introducer_attributions_v48 (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id            TEXT NOT NULL DEFAULT '',
            bug_key               TEXT NOT NULL DEFAULT '',
            fix_commit            TEXT NOT NULL,
            introducer_commit     TEXT NOT NULL,
            introducer_author     TEXT NOT NULL DEFAULT '',
            introducer_session_id TEXT,
            authoring_condition   TEXT NOT NULL,
            resolution_reason     TEXT NOT NULL DEFAULT '',
            confidence            REAL NOT NULL DEFAULT 0.0,
            resolved_at           TEXT NOT NULL,
            carril                TEXT,
            tier                  TEXT,
            UNIQUE (project_id, bug_key, fix_commit, introducer_commit, carril)
        )
    """)
    conn.execute("""
        INSERT INTO introducer_attributions_v48
            SELECT id, project_id, bug_key, fix_commit, introducer_commit,
                   introducer_author, introducer_session_id, authoring_condition,
                   resolution_reason, confidence, resolved_at, carril, tier
            FROM introducer_attributions
    """)
    conn.execute("DROP TABLE introducer_attributions")
    conn.execute(
        "ALTER TABLE introducer_attributions_v48 RENAME TO introducer_attributions"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_introducer_attributions_project"
        " ON introducer_attributions(project_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_introducer_attributions_fix"
        " ON introducer_attributions(fix_commit)"
    )
    conn.commit()


def _apply_v45(conn: sqlite3.Connection) -> None:
    """Create introducer_attributions table for defect attribution (S11126.4).

    Guards with table-existence check (PAT-E-1688) — safe to call on DBs
    that already have the table from a concurrent branch.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "introducer_attributions" not in tables:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS introducer_attributions (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id            TEXT NOT NULL DEFAULT '',
                bug_key               TEXT NOT NULL DEFAULT '',
                fix_commit            TEXT NOT NULL,
                introducer_commit     TEXT NOT NULL,
                introducer_author     TEXT NOT NULL DEFAULT '',
                introducer_session_id TEXT,
                authoring_condition   TEXT NOT NULL,
                resolution_reason     TEXT NOT NULL DEFAULT '',
                confidence            REAL NOT NULL DEFAULT 0.0,
                resolved_at           TEXT NOT NULL,
                UNIQUE (project_id, fix_commit, introducer_commit)
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_introducer_attributions_project"
            " ON introducer_attributions(project_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_introducer_attributions_fix"
            " ON introducer_attributions(fix_commit)"
        )


def _apply_v46(conn: sqlite3.Connection) -> None:
    """Add fix_version column to missions table (RAISE-11665).

    Guard: missions table may not exist in partial-migration test DBs.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "missions" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(missions)").fetchall()}
    if "fix_version" not in cols:
        conn.execute(
            "ALTER TABLE missions ADD COLUMN fix_version TEXT NOT NULL DEFAULT ''"
        )


def _apply_v50(conn: sqlite3.Connection) -> None:
    """Add jira_key column to missions table (RAISE-14385, ADR-130 §D1).

    Guard: missions table may not exist in partial-migration test DBs.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "missions" not in tables:
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(missions)").fetchall()}
    if "jira_key" not in cols:
        conn.execute("ALTER TABLE missions ADD COLUMN jira_key TEXT")


def _apply_v47(conn: sqlite3.Connection) -> None:
    """Añade carril/tier a introducer_attributions (S11899.1, E11899).

    provenance-tier: Carril A=high / B=medium / C=low — distinto del confidence-band SZZ.
    introducer_commit se mantiene TEXT NOT NULL; Carril C / no-attr usan sentinel ""
    (no se recrea la tabla ni se toca el UNIQUE — evita riesgo de pérdida de datos).
    PAT-E-1688: guard por PRAGMA table_info (idempotente ante branches concurrentes;
    SQLite no soporta ADD COLUMN IF NOT EXISTS).
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "introducer_attributions" not in tables:
        return
    cols = {
        r[1]
        for r in conn.execute("PRAGMA table_info(introducer_attributions)").fetchall()
    }
    if "carril" not in cols:
        conn.execute("ALTER TABLE introducer_attributions ADD COLUMN carril TEXT")
    if "tier" not in cols:
        conn.execute("ALTER TABLE introducer_attributions ADD COLUMN tier TEXT")


def _apply_v44(conn: sqlite3.Connection) -> None:
    """Add promoted_at/promoted_by to patterns table (RAISE-9511).

    Guard: patterns table may not exist in partial-migration test DBs.
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "patterns" not in tables:
        return
    existing_cols = {
        r[1] for r in conn.execute("PRAGMA table_info(patterns)").fetchall()
    }
    if "promoted_at" not in existing_cols:
        conn.execute("ALTER TABLE patterns ADD COLUMN promoted_at TEXT")
    if "promoted_by" not in existing_cols:
        conn.execute("ALTER TABLE patterns ADD COLUMN promoted_by TEXT")


def _apply_v43(conn: sqlite3.Connection) -> None:
    """Create maintenance_locks table for global DB consolidation lock (S8371.3).

    The table lives in the global DB (``~/.rai/raise.db``) and is guarded by
    ``MaintenanceLockStore``.  Absent table degrades fail-open — callers wrap
    reads in bare ``except Exception`` (AC9 / ADR-104).
    """
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "maintenance_locks" not in tables:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_locks (
                name        TEXT PRIMARY KEY,
                pid         INTEGER NOT NULL,
                acquired_at TEXT NOT NULL,
                expires_at  TEXT NOT NULL
            )
        """)


_MIGRATIONS: dict[int, str] = {
    0: _V1_DDL,
    1: _V2_DDL,
    2: _V3_DDL,
    3: _V4_DDL,
    4: _V5_DDL,
    5: _V6_DDL,
    6: _V7_DDL,
    7: _V8_DDL,
    8: _V9_DDL,
    9: _V10_DDL,
    10: _V11_DDL,
    11: _V12_DDL,
    12: _V13_DDL,
    13: _V14_DDL,
    14: _V15_DDL,
    15: _V16_DDL,
    16: _V17_DDL,
    17: _V18_DDL,
    18: _V19_DDL,
    19: _V20_DDL,
    20: _V21_DDL,
    21: _V22_DDL,
    22: _V23_DDL,
    23: _V24_DDL,
    24: _V25_DDL,
    25: _V26_DDL,
    26: _V27_DDL,
    27: _V28_DDL,
    28: _V29_DDL,
    29: _V30_DDL,
    30: _V31_DDL,
    31: _V32_DDL,
    32: _V33_DDL,
    33: _V34_DDL,
    34: _V35_DDL,
    35: _V36_DDL,
    36: _V37_DDL,
    37: _V38_DDL,
    38: _V39_DDL,
    39: "",  # programmatic — see _apply_v40
    40: "",  # programmatic — see _apply_v41
    41: _V42_DDL,  # programmatic — see _apply_v42
    42: _V43_DDL,  # programmatic — see _apply_v43
    43: "",  # programmatic — see _apply_v44
    44: _V45_DDL,  # programmatic — see _apply_v45
    45: _V46_DDL,  # programmatic — see _apply_v46 (origin fix_version/missions)
    46: _V47_DDL,  # programmatic — see _apply_v47 (carril/tier)
    47: _V48_DDL,  # programmatic — see _apply_v48 (M1 UNIQUE recreate)
    48: _V49_DDL,  # session_ledger_entries (RAISE-13146, O2 self-surfacing)
    49: _V50_DDL,  # programmatic — see _apply_v50 (RAISE-14385, missions.jira_key)
    50: _V51_DDL,  # programmatic — see _apply_v51 (patterns.content_hash, S14056.1)
    51: _V52_DDL,  # programmatic — see _apply_v52 (defensive UNIQUE index, S14056.2)
    52: _V53_DDL,  # programmatic — see _apply_v53 (work_items table, RAISE-14640/S1)
    53: _V54_DDL,  # graph_builds table (RAISE-14852)
    54: _V55_DDL,  # programmatic — see _apply_v55 (ADR-130 D2/D5, RAISE-14643/S4)
    55: _V56_DDL,  # programmatic — see _apply_v56 (work_items_outbox + FK cols, RAISE-14649/S10)
    56: _V57_DDL,  # programmatic — see _apply_v57 (project-scoped artifact identity, RAISE-14954)
    57: _V58_DDL,  # programmatic — see _apply_v58 (review artifact identity)
    58: _V59_DDL,  # programmatic — see _apply_v59 (worktree attribution, RAISE-15003)
    59: _V60_DDL,  # programmatic — see _apply_v60 (ledger stack elimination, RAISE-15135)
    60: _V61_DDL,  # portfolio_components/initiative_profiles/portfolio_deps (RAISE-15200/S1)
    61: _V62_DDL,  # pipeline_backlog_events table (RAISE-15051/P4)
    62: _V63_DDL,  # epic_profiles table (RAISE-15254/S4)
    63: _V64_DDL,  # programmatic — see _apply_v64 (active_sessions.worktree_id, RAISE-15131)
    64: _V65_DDL,  # distillation_runs (RAISE-15271)
    65: _V66_DDL,  # session_developer_turns, evasion_events, proposed_patterns, view skill_corrections (RAISE-15327)
    66: _V67_DDL,  # programmatic — see _apply_v67 (session scope attribution, RAISE-15463)
    67: _V68_DDL,  # programmatic — see _apply_v68 (checkout-scoped graph, RAISE-15607)
    68: _V69_DDL,  # programmatic — see _apply_v69 (pipeline run status normalization, RAISE-15795)
    69: _V70_DDL,  # mcp_server_events table (RAISE-15784)
    70: _V71_DDL,  # programmatic — see _apply_v71 (runtime_sessions table, RAISE-15839/S1)
    71: _V72_DDL,  # graph_node_annotations table (RAISE-16596)
    72: _V73_DDL,  # port_allocations table (RAISE-16541, S16534.1)
    73: _V74_DDL,  # programmatic — see _apply_v74 (work_items data cols, RAISE-16622)
    74: _V75_DDL,  # programmatic — see _apply_v75 (signals.signal_schema_version, RAISE-16689)
    75: _V76_DDL,  # worktree_pause_states table (RAISE-16708, S16702.3)
    76: _V77_DDL,  # cc_token_daily table (RAISE-16866)
    77: _V78_DDL,  # graph_node_annotations provenance columns (RAISE-16850)
    78: _V79_DDL,  # ddd_tactical_type column (RAISE-16915)
}


def _execute_ddl(conn: sqlite3.Connection, ddl: str) -> None:
    """Execute a DDL string, tolerating already-applied statements.

    SQLite's ALTER TABLE … ADD COLUMN has no IF NOT EXISTS clause.  When a
    background thread partially applies a migration and the schema version
    PRAGMA hasn't been committed yet, a second connection re-runs the same
    migration and hits a duplicate-column error.  We treat these errors as
    "already applied" so migrations are idempotent.
    """
    _idempotent_msgs = ("duplicate column name", "already exists")
    for stmt in ddl.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as exc:
                msg = str(exc).lower()
                if any(m in msg for m in _idempotent_msgs):
                    logger.debug(
                        "DDL already applied, skipping: %s — %s", stmt[:80], exc
                    )
                else:
                    raise


def _apply_v31(conn: sqlite3.Connection) -> None:
    """Backfill state_json for sessions with branch info but empty state."""
    import json
    import re as _re

    # Guard: sessions table may not exist during early-version migration tests
    existing = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
    ).fetchone()
    if not existing:
        return

    rows = conn.execute(
        "SELECT session_id, branch, started, summary FROM sessions "
        "WHERE state_json = '{}' AND branch IS NOT NULL AND branch != '' AND branch != 'dev'"
    ).fetchall()
    if not rows:
        return
    story_pat = _re.compile(r"story/s(\d+)\.(\d+)")
    for session_id, branch, started, summary in rows:
        m = story_pat.search(branch or "")
        epic = f"E{m.group(1)}" if m else ""
        story = f"S{m.group(1)}.{m.group(2)}" if m else ""
        state = {
            "current_work": {
                "release": "3.0.0",
                "epic": epic,
                "story": story,
                "phase": "",
                "branch": branch or "",
            },
            "last_session": {
                "id": session_id,
                "date": (started or "")[:10],
                "developer": "",
                "summary": summary or "",
            },
        }
        conn.execute(
            "UPDATE sessions SET state_json = ? WHERE session_id = ?",
            (json.dumps(state), session_id),
        )


_PROGRAMMATIC_MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {
    23: _apply_v24,
    27: _apply_v28,
    28: _apply_v29,
    29: _apply_v30,
    30: _apply_v31,
    31: _apply_v32,
    33: _apply_v34,
    35: _apply_v36,
    39: _apply_v40,
    40: _apply_v41,
    41: _apply_v42,
    42: _apply_v43,
    43: _apply_v44,
    44: _apply_v45,
    45: _apply_v46,
    46: _apply_v47,
    47: _apply_v48,
    49: _apply_v50,
    50: _apply_v51,
    51: _apply_v52,
    52: _apply_v53,
    54: _apply_v55,
    55: _apply_v56,
    56: _apply_v57,
    57: _apply_v58,
    58: _apply_v59,
    59: _apply_v60,
    63: _apply_v64,
    66: _apply_v67,
    67: _apply_v68,
    68: _apply_v69,
    70: _apply_v71,
    73: _apply_v74,
    74: _apply_v75,
}


def _apply_migration(conn: sqlite3.Connection, version: int, ddl: str) -> None:
    if version == 25:
        _apply_v26(conn)
        _execute_ddl(conn, ddl)
    elif version in _PROGRAMMATIC_MIGRATIONS:
        _PROGRAMMATIC_MIGRATIONS[version](conn)
    elif ddl:
        _execute_ddl(conn, ddl)


def create_all(conn: sqlite3.Connection) -> None:
    """Create or migrate schema to current version. Idempotent.

    Both branches run under ``with conn:`` so a failure leaves the connection
    clean (RAISE-15605). Without it, ``validate_current_schema`` raising after
    a helper has written strands an open write transaction — and with it the
    WAL write lock — for the life of the process, blocking every writer against
    the shared ``~/.rai/raise.db``. That is the defect this bug exists to fix,
    and this function sits on the read path: every store constructor reaches it
    on first construction in each process.

    This releases the lock; it does NOT make migration atomic. Several helpers
    commit internally — ``_apply_v28``, ``_apply_v29``, ``_apply_v30`` via
    ``executescript`` (which issues a COMMIT before the script), and
    ``_apply_v48``, ``_apply_v55``, ``_apply_v56``, ``_apply_v60`` via explicit
    ``conn.commit()`` — so partial migration was already possible and still is.
    Making the whole migration atomic is a separate change.
    """
    # WAL mode must be set on the file, not per-connection — once enabled it
    # persists for all subsequent connections. Setting it here ensures databases
    # created by tests or tools that bypass get_project_db() still get WAL mode.
    conn.execute("PRAGMA journal_mode=WAL")
    version: int = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= SCHEMA_VERSION:
        with conn:
            _apply_v24(conn)
            _apply_v28(conn)
            _apply_v29(conn)
            _apply_v30(conn)
            # _apply_v31 intentionally excluded: one-time data backfill that
            # overwrites intentionally-cleared state_json and assumes full
            # sessions schema — not safe to re-run on every create_all().
            _apply_v32(conn)
            _apply_v34(conn)
            _apply_v36(conn)
            _apply_v40(conn)
            _apply_v41(conn)
            _apply_v42(conn)
            _apply_v43(conn)
            _apply_v44(conn)
            _apply_v45(conn)
            _apply_v46(conn)
            _apply_v47(conn)
            _apply_v48(conn)
            _apply_v50(conn)
            _apply_v51(conn)
            _apply_v52(conn)
            _apply_v53(conn)
            _apply_v55(conn)
            _apply_v56(conn)
            _apply_v57(conn)
            _apply_v58(conn)
            _apply_v59(conn)
            _apply_v60(conn)
            _execute_ddl(conn, _V61_DDL)
            _execute_ddl(conn, _V62_DDL)
            _execute_ddl(conn, _V63_DDL)
            _apply_v64(conn)
            _execute_ddl(conn, _V65_DDL)
            _execute_ddl(conn, _V66_DDL)
            _apply_v67(conn)
            _apply_v68(conn)
            _apply_v69(conn)
            _execute_ddl(conn, _V70_DDL)
            _apply_v71(conn)
            _execute_ddl(conn, _V72_DDL)
            _execute_ddl(conn, _V73_DDL)
            _apply_v74(conn)
            _apply_v75(conn)
            _execute_ddl(conn, _V76_DDL)
            _execute_ddl(conn, _V77_DDL)
            _execute_ddl(conn, _V78_DDL)
            _execute_ddl(conn, _V79_DDL)
            problems = validate_current_schema(conn)
            if problems:
                raise RuntimeError(
                    "Schema invariant check failed: " + "; ".join(problems)
                )
        return
    # Guard: take a verified backup before the first migration mutation.
    # prepare_migration_backup() returns None for in-memory DBs and pristine
    # v0 creation, so those paths are unaffected.  Raises MigrationBackupError
    # (a RuntimeError) on any failure — no source mutation has occurred.
    receipt = prepare_migration_backup(conn, version, SCHEMA_VERSION)
    if receipt is not None:
        # Re-read user_version: another process may have migrated while we
        # were snapshotting (§5.3 step 8).
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version >= SCHEMA_VERSION:
            return
    with conn:
        for v in range(version, SCHEMA_VERSION):
            _apply_migration(conn, v, _MIGRATIONS[v])
        problems = validate_current_schema(conn)
        if problems:
            raise RuntimeError("Schema invariant check failed: " + "; ".join(problems))
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


# ---------------------------------------------------------------------------
# Once-per-process migration guard (RAISE-15605)
# ---------------------------------------------------------------------------
# `create_all()` is idempotent but not free: its fast path re-runs every
# programmatic migration, and some of those issue unconditional backfill
# UPDATEs (`_apply_v64`). Calling it from a store constructor therefore puts a
# WRITE in the READ path — which is what turned a single orphaned write
# transaction on the shared `~/.rai/raise.db` into a whole-CLI outage: even
# `rai backlog get` had to take the write lock before it could read.

_SCHEMA_ENSURED: dict[str, int] = {}


def _main_database_file(conn: sqlite3.Connection) -> str:
    """Return the file backing `main`, or '' for in-memory/temporary databases."""
    for row in conn.execute("PRAGMA database_list").fetchall():
        if row[1] == "main":
            return str(row[2] or "")
    return ""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Run `create_all()` at most once per (process, database file).

    The guard is per-PROCESS, deliberately not per-database-lifetime: the first
    call in every process still migrates, so a database that has not yet seen
    the newest migration always receives it (RAISE-15607's v68 and every
    migration after it reach disk exactly as before). The `user_version`
    re-check makes the guard self-healing — a cached path whose file is behind
    on disk is migrated again rather than skipped.

    In-memory databases report an empty path; they are never cached, since each
    connection is its own distinct database.
    """
    path = _main_database_file(conn)
    if path and _SCHEMA_ENSURED.get(path) == SCHEMA_VERSION:
        on_disk: int = conn.execute("PRAGMA user_version").fetchone()[0]
        if on_disk == SCHEMA_VERSION:
            return
    create_all(conn)
    if path:
        _SCHEMA_ENSURED[path] = SCHEMA_VERSION


def reset_schema_cache() -> None:
    """Forget which databases this process has already migrated.

    For tests, and for any caller that recreates a database file in place.
    """
    _SCHEMA_ENSURED.clear()
