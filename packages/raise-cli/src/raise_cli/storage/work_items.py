"""Local work-item registry — Pydantic model (RAISE-14640, S1 of E10622).

ADR-130 collapses "mission" into a level-agnostic work-item registry spanning
theme -> initiative -> epic -> story -> task. `WorkItem` mirrors the
`work_items` DDL (schema.py `_apply_v53`, design.md §2) 1:1.

`WorkItemStore` is a read-side mirror of `SqliteMissionStore`'s shape
(`__init__` -> `get_project_id` + `get_project_db` + `ensure_schema`). S1 scope:
`get`, `get_by_local_key`, `children`, `list_all` — read methods only, no
writes/seeding (S2), no CLI (S3). S3 (RAISE-14642) adds the write path:
`create()` + `get_by_jira_key()` (parent lookup by wire-key) +
`slugify_local_key()` (local_key generation, D2). `get_active()` is
explicitly deferred to S4: `worktrees.workitem_id` does not exist yet
(s1-design.md §6).
"""

from __future__ import annotations

import logging
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import ensure_schema

_log = logging.getLogger(__name__)

_SLUG_MAX_LEN = 40
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

WorkItemType = Literal["theme", "initiative", "epic", "story", "task"]


class WorkItem(BaseModel):
    """Mirrors the `work_items` table (schema.py `_apply_v53`) 1:1.

    `id` is the stable local storage key (RAISE-13467: never re-key).
    `local_key` is the human-facing label (e.g. 'S15.1', 'E15'). `jira_key`
    is the wire identity — nullable, since NULL means local-only work (no
    Jira issue exists; closes RAISE-14069).
    """

    id: str
    type: WorkItemType
    local_key: str
    jira_key: str | None = None
    parent_local_key: str | None = None
    parent_jira_key: str | None = None
    summary: str = ""
    status: str = "todo"
    no_portfolio: bool = False
    created_at: str
    updated_at: str


def _row_to_work_item(row: sqlite3.Row) -> WorkItem:
    d: dict[str, object] = dict(row)
    return WorkItem(
        id=d["id"],  # type: ignore[arg-type]
        type=d["type"],  # type: ignore[arg-type]
        local_key=d["local_key"],  # type: ignore[arg-type]
        jira_key=d.get("jira_key"),  # type: ignore[arg-type]
        parent_local_key=d.get("parent_local_key"),  # type: ignore[arg-type]
        parent_jira_key=d.get("parent_jira_key"),  # type: ignore[arg-type]
        summary=d.get("summary", ""),  # type: ignore[arg-type]
        status=d.get("status", "todo"),  # type: ignore[arg-type]
        no_portfolio=bool(d["no_portfolio"]),
        created_at=d["created_at"],  # type: ignore[arg-type]
        updated_at=d["updated_at"],  # type: ignore[arg-type]
    )


class WorkItemStore:
    """Read-side mirror of `SqliteMissionStore` over the `work_items` table.

    Unlike `missions`, `work_items` has no `project_id` column — the local
    DB is already per-checkout (s1-design.md §3.2 scoping note). No
    `_adopt_legacy_rows`-style dance, no `project_id` predicate/filtering.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        self._conn.row_factory = sqlite3.Row
        # RAISE-15605: once-per-process, so constructing a store for a READ
        # does not issue migration backfill WRITEs on the shared DB.
        ensure_schema(self._conn)

    def get(self, id: str) -> WorkItem | None:  # noqa: A002 - mirrors DDL column name
        """Return the work item with this stable local id, or None."""
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE id = ?", (id,)
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def get_by_local_key(self, local_key: str) -> WorkItem | None:
        """Return the work item with this human-facing local_key, or None."""
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE local_key = ?", (local_key,)
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def get_by_jira_key(self, jira_key: str) -> WorkItem | None:
        """Return the work item with this wire-identity jira_key, or None."""
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE jira_key = ?", (jira_key,)
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def find_by_parent_and_summary(
        self, parent_jira_key: str, summary: str
    ) -> WorkItem | None:
        """Return existing child story by parent+summary for idempotency check (S8)."""
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE parent_jira_key = ? AND summary = ?",
            (parent_jira_key, summary),
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def create(self, work_item: WorkItem) -> WorkItem:
        """Insert a fully-populated `WorkItem` row and return it (S3, RAISE-14642).

        Caller is responsible for having resolved `local_key`/`jira_key`/
        parent fields already — no partial rows, no follow-up UPDATE.
        Duplicate `local_key` or non-NULL duplicate `jira_key` raise
        `sqlite3.IntegrityError` (unique indexes `idx_work_items_local_key`,
        `idx_work_items_jira_key`) — let it propagate, do not swallow (AC5).

        The `with self._conn:` block commits on clean exit and ROLLS BACK on
        exception (RAISE-15605): the exception still propagates, but the
        connection no longer keeps the implicit write transaction — and with
        it the shared `~/.rai/raise.db` WAL write lock — open for the life of
        the process.
        """
        with self._conn:
            self._conn.execute(
                "INSERT INTO work_items "
                "(id, type, local_key, jira_key, parent_local_key, parent_jira_key, "
                "summary, status, no_portfolio, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    work_item.id,
                    work_item.type,
                    work_item.local_key,
                    work_item.jira_key,
                    work_item.parent_local_key,
                    work_item.parent_jira_key,
                    work_item.summary,
                    work_item.status,
                    int(work_item.no_portfolio),
                    work_item.created_at,
                    work_item.updated_at,
                ),
            )
        return work_item

    def children(
        self,
        parent_local_key: str,
        type: str | None = None,  # noqa: A002 - mirrors DDL column name
    ) -> list[WorkItem]:
        """Return work items whose parent_local_key matches, optionally by type."""
        if type is None:
            rows = self._conn.execute(
                "SELECT * FROM work_items WHERE parent_local_key = ? "
                "ORDER BY local_key",
                (parent_local_key,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM work_items WHERE parent_local_key = ? AND type = ? "
                "ORDER BY local_key",
                (parent_local_key, type),
            ).fetchall()
        return [_row_to_work_item(row) for row in rows]

    def check_epic_stories_done(
        self, epic_jira_key: str
    ) -> tuple[bool, list[WorkItem]]:
        """Return (all_done, open_stories) for child stories of the epic.

        Queries work_items for type='story' and parent_jira_key=epic_jira_key.
        Status comparison is case-insensitive. Vacuously True when no children.
        """
        rows = self._conn.execute(
            "SELECT * FROM work_items WHERE type = 'story' AND parent_jira_key = ?",
            (epic_jira_key,),
        ).fetchall()
        stories = [_row_to_work_item(row) for row in rows]
        open_stories = [wi for wi in stories if wi.status.lower() != "done"]
        return not bool(open_stories), open_stories

    def list_all(
        self,
        type: str | None = None,  # noqa: A002 - mirrors DDL column name
        status: str | None = None,
    ) -> list[WorkItem]:
        """Return all work items, optionally filtered by type and/or status."""
        clauses: list[str] = []
        params: list[str] = []
        if type is not None:
            clauses.append("type = ?")
            params.append(type)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        query = "SELECT * FROM work_items"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY local_key"
        rows = self._conn.execute(query, params).fetchall()
        return [_row_to_work_item(row) for row in rows]

    # -- Key-store API (replaces SyncLedger YAML) ----------------------------

    def get_jira_key(self, local_key: str) -> str | None:
        """Return jira_key for local_key, or None if unmapped."""
        row = self._conn.execute(
            "SELECT jira_key FROM work_items WHERE local_key = ?", (local_key,)
        ).fetchone()
        return row["jira_key"] if row is not None else None

    def upsert_jira_mapping(
        self, local_key: str, jira_key: str, *, summary: str = ""
    ) -> None:
        """Record or update the local_key → jira_key mapping.

        If the row already exists (created via ontology path), only jira_key
        and updated_at are touched. If the row is new, type is inferred from
        the local_key pattern (E→epic, S→story, default→story).

        Transactional (RAISE-15605): `ON CONFLICT(local_key)` does not cover
        `idx_work_items_jira_key`, so this path can still raise — and must not
        leave the write lock held when it does.
        """
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO work_items
                    (id, type, local_key, jira_key, summary, status,
                     no_portfolio, created_at, updated_at)
                VALUES (lower(hex(randomblob(8))), ?, ?, ?, ?, 'todo', 0,
                        strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                        strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                ON CONFLICT(local_key) DO UPDATE SET
                    jira_key   = excluded.jira_key,
                    updated_at = excluded.updated_at
                """,
                (_infer_type(local_key), local_key, jira_key, summary),
            )

    def remove_jira_mapping(self, local_key: str) -> None:
        """Clear the jira_key for local_key (keeps the row, NULLs the key)."""
        with self._conn:
            self._conn.execute(
                "UPDATE work_items SET jira_key = NULL WHERE local_key = ?",
                (local_key,),
            )

    def seed_jira_keys(
        self,
        keys: list[str],
        *,
        dry_run: bool = False,
    ) -> tuple[int, int]:
        """Backfill work_items from a list of RAISE-XXXXX keys (RAISE-15143).

        Uses ``INSERT OR IGNORE`` so existing rows (by ``local_key`` OR
        ``jira_key``) are silently skipped — safe to run repeatedly and safe
        when a proper entry already maps a different ``local_key`` to the same
        ``jira_key``.

        Args:
            keys: RAISE-XXXXX strings to seed (``local_key = jira_key``).
            dry_run: When True, count but do not write any rows.

        Returns:
            ``(inserted, skipped)`` counts.
        """
        if dry_run:
            return self._count_seed_jira_keys(keys)

        inserted = 0
        skipped = 0
        # Transactional (RAISE-15605): a mid-batch failure rolls the batch back
        # and releases the write lock instead of stranding it open.
        with self._conn:
            for key in keys:
                cur = self._conn.execute(
                    """
                    INSERT OR IGNORE INTO work_items
                        (id, type, local_key, jira_key, summary, status,
                         no_portfolio, created_at, updated_at)
                    VALUES (lower(hex(randomblob(8))), 'story', ?, ?, '', 'todo', 0,
                            strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                            strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                    """,
                    (key, key),
                )
                if cur.rowcount:
                    inserted += 1
                else:
                    skipped += 1
        return inserted, skipped

    def _count_seed_jira_keys(self, keys: list[str]) -> tuple[int, int]:
        """Read-only ``seed_jira_keys`` dry run — count, write nothing."""
        inserted = 0
        skipped = 0
        for key in keys:
            exists = self._conn.execute(
                "SELECT 1 FROM work_items WHERE local_key = ? OR jira_key = ?",
                (key, key),
            ).fetchone()
            if exists:
                skipped += 1
            else:
                inserted += 1
        return inserted, skipped

    def all_jira_mappings(self) -> dict[str, str]:
        """Return {local_key: jira_key} for all rows with a non-NULL jira_key."""
        rows = self._conn.execute(
            "SELECT local_key, jira_key FROM work_items WHERE jira_key IS NOT NULL"
        ).fetchall()
        return {row["local_key"]: row["jira_key"] for row in rows}


def _infer_type(local_key: str) -> WorkItemType:
    """Infer work-item type from local_key pattern (E→epic, S→story, else story)."""
    if re.fullmatch(r"E\d+", local_key):
        return "epic"
    if re.fullmatch(r"S\d+(\.\d+)?", local_key):
        return "story"
    return "story"


def _slugify(title: str) -> str:
    """Pure slug computation: Unicode transliteration -> lowercase -> collapse.

    NFKD-normalize then strip combining marks (accents) to transliterate to
    ASCII, lowercase, collapse non-alphanumeric runs to a single `-`, strip
    leading/trailing `-`, truncate to `_SLUG_MAX_LEN` chars.
    """
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = _NON_ALNUM_RE.sub("-", ascii_only.lower()).strip("-")
    return slug[:_SLUG_MAX_LEN].rstrip("-")


def slugify_local_key(store: WorkItemStore, type: str, title: str) -> str:  # noqa: A002 - mirrors DDL column name
    """Return a free `local_key` for `type`/`title` — `{type}-{slug(title)}` (D2, ratified).

    Proactive collision handling: query `store.get_by_local_key()` and retry
    with a `-2`, `-3`, ... suffix (appended to the slug portion, not the type
    prefix) until a free key is found. This is query-then-use, not
    exception-driven — `idx_work_items_local_key`'s unique index remains the
    fail-safe for the genuine concurrent-write race, out of scope to solve
    here (single-writer local SQLite).
    """
    base = f"{type}-{_slugify(title)}"
    candidate = base
    suffix = 2
    while store.get_by_local_key(candidate) is not None:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def resolve_active_work_item(
    project: Path,
    session_id: str | None,
    *,
    cwd: Path | None = None,
) -> WorkItem | None:
    """Canonical silent resolver for the active WorkItem.

    Replaces resolve_active_mission (S7 ADR-130 D2). Resolution order:
    1. workitem_id on the worktree whose path matches ``cwd``
    2. workitem_id from agent_session_workitems for ``session_id``
    3. None (never raises)
    """
    try:
        if cwd is not None:
            from raise_cli.storage.worktrees import (
                SqliteWorktreeStore,
                WorktreeNotFoundError,
            )

            try:
                worktree = SqliteWorktreeStore(project).get_by_path(str(cwd.resolve()))
                if worktree.workitem_id:
                    return WorkItemStore(project).get(worktree.workitem_id)
            except WorktreeNotFoundError:
                pass
            except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                _log.debug("Worktree workitem_id lookup failed", exc_info=True)

        if session_id is not None:
            conn = get_project_db(project)
            pid = get_project_id(project)
            row = conn.execute(  # noqa: S608 — internal DB, not user-supplied SQL
                "SELECT workitem_id FROM agent_session_workitems"
                " WHERE project_id = ? AND cc_session_id = ?",
                (pid, session_id),
            ).fetchone()
            if row and row[0]:
                return WorkItemStore(project).get(row[0])
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("resolve_active_work_item failed", exc_info=True)
    return None
