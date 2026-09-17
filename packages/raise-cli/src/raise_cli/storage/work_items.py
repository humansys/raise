"""Local work-item registry — Pydantic model (RAISE-14640, S1 of E10622).

ADR-130 collapses "mission" into a level-agnostic work-item registry spanning
theme -> initiative -> epic -> story -> task (-> bug, RAISE-16622). `WorkItem`
mirrors the `work_items` DDL (schema.py `_apply_v72`, design.md §2) 1:1.

`WorkItemStore` is a read-side mirror of `SqliteMissionStore`'s shape
(`__init__` -> `get_project_id` + `get_project_db` + `ensure_schema`). S1 scope:
`get`, `get_by_local_key`, `children`, `list_all` — read methods only, no
writes/seeding (S2), no CLI (S3). S3 (RAISE-14642) adds the write path:
`create()` + `get_by_jira_key()` (parent lookup by wire-key) +
`slugify_local_key()` (local_key generation, D2). `get_active()` is
explicitly deferred to S4: `worktrees.workitem_id` does not exist yet
(s1-design.md §6).

RAISE-16622 (S16533.2, V72) adds `project_id` scoping (MUST-ARCH-003 — the
shared `~/.rai/raise.db` has no per-project isolation on this table
otherwise) plus six data columns (description, labels, priority, assignee,
fix_versions, custom_fields) and three child tables (comments, links,
changelog). Compat window (D-S2.2, story design.md §4.1): reads are lenient
— `project_id IN (self, '')` with the caller's own scoped row preferred over
a legacy `''` row — until `rai backlog migrate` (S16533.4) claims every
row. Writes always stamp `self._project_id`. `upsert_jira_mapping` and
`seed_jira_keys` run an *adoption* step first: a matching legacy `''` row is
claimed into the caller's project before the write, so post-V72 they neither
raise (V5: stale `ON CONFLICT(local_key)`) nor silently duplicate (V6: a
legacy row no longer blocking a scoped insert).
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import ensure_schema

_log = logging.getLogger(__name__)

_SLUG_MAX_LEN = 40
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

WorkItemType = Literal["theme", "initiative", "epic", "story", "task", "bug"]


class WorkItem(BaseModel):
    """Mirrors the `work_items` table (schema.py `_apply_v53`) 1:1.

    `id` is the stable local storage key (RAISE-13467: never re-key).
    `local_key` is the human-facing label (e.g. 'S15.1', 'E15'). `jira_key`
    is the wire identity — nullable, since NULL means local-only work (no
    Jira issue exists; closes RAISE-14069).
    """

    id: str
    type: WorkItemType
    project_id: str = ""
    local_key: str
    jira_key: str | None = None
    parent_local_key: str | None = None
    parent_jira_key: str | None = None
    summary: str = ""
    status: str = "todo"
    no_portfolio: bool = False
    description: str = ""
    labels: list[str] = Field(default_factory=list)
    priority: str | None = None
    assignee: str | None = None
    fix_versions: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class WorkItemComment(BaseModel):
    """Mirrors the `work_item_comments` table (schema.py `_apply_v72`)."""

    id: str
    work_item_id: str
    body: str = ""
    author: str = ""
    created_at: str = ""


class WorkItemLink(BaseModel):
    """Mirrors the `work_item_links` table (schema.py `_apply_v72`).

    `id` is `None` for an as-yet-unpersisted instance; the DB assigns the
    AUTOINCREMENT rowid on insert.
    """

    id: int | None = None
    work_item_id: str
    target_key: str
    link_type: str = ""


class WorkItemChangelogEntry(BaseModel):
    """Mirrors the `work_item_changelog` table (schema.py `_apply_v72`).

    Append-only audit trail (D15/D-S2.7) — no update/delete API exists on
    the store; `id` is `None` for an as-yet-unpersisted instance.
    """

    id: int | None = None
    work_item_id: str
    field: str
    old_value: str | None = None
    new_value: str | None = None
    author: str = ""
    changed_at: str = ""


def _json_list(raw: object) -> list[str]:
    """Decode a `*_json` TEXT column into a list, tolerating malformed data.

    A poison row (hand-edited DB, partial write) must not brick reads — log
    and fall back to `[]` rather than raise (story design.md §3).
    """
    if not raw:
        return []
    try:
        value = json.loads(str(raw))
    except (TypeError, ValueError):
        _log.warning("work_items: malformed JSON column, falling back to []: %r", raw)
        return []
    return value if isinstance(value, list) else []


def _json_dict(raw: object) -> dict[str, Any]:
    """Decode a `*_json` TEXT column into a dict, tolerating malformed data."""
    if not raw:
        return {}
    try:
        value = json.loads(str(raw))
    except (TypeError, ValueError):
        _log.warning("work_items: malformed JSON column, falling back to {}: %r", raw)
        return {}
    return value if isinstance(value, dict) else {}


def _row_to_work_item(row: sqlite3.Row) -> WorkItem:
    d: dict[str, object] = dict(row)
    return WorkItem(
        id=d["id"],  # type: ignore[arg-type]
        type=d["type"],  # type: ignore[arg-type]
        project_id=d.get("project_id", "") or "",  # type: ignore[arg-type]
        local_key=d["local_key"],  # type: ignore[arg-type]
        jira_key=d.get("jira_key"),  # type: ignore[arg-type]
        parent_local_key=d.get("parent_local_key"),  # type: ignore[arg-type]
        parent_jira_key=d.get("parent_jira_key"),  # type: ignore[arg-type]
        summary=d.get("summary", ""),  # type: ignore[arg-type]
        status=d.get("status", "todo"),  # type: ignore[arg-type]
        no_portfolio=bool(d["no_portfolio"]),
        description=d.get("description", "") or "",  # type: ignore[arg-type]
        labels=_json_list(d.get("labels_json")),
        priority=d.get("priority") or None,  # type: ignore[arg-type]
        assignee=d.get("assignee") or None,  # type: ignore[arg-type]
        fix_versions=_json_list(d.get("fix_versions_json")),
        custom_fields=_json_dict(d.get("custom_fields_json")),
        created_at=d["created_at"],  # type: ignore[arg-type]
        updated_at=d["updated_at"],  # type: ignore[arg-type]
    )


def _row_to_comment(row: sqlite3.Row) -> WorkItemComment:
    d: dict[str, object] = dict(row)
    return WorkItemComment(
        id=d["id"],  # type: ignore[arg-type]
        work_item_id=d["work_item_id"],  # type: ignore[arg-type]
        body=d.get("body", ""),  # type: ignore[arg-type]
        author=d.get("author", ""),  # type: ignore[arg-type]
        created_at=d.get("created_at", ""),  # type: ignore[arg-type]
    )


def _row_to_link(row: sqlite3.Row) -> WorkItemLink:
    d: dict[str, object] = dict(row)
    return WorkItemLink(
        id=d["id"],  # type: ignore[arg-type]
        work_item_id=d["work_item_id"],  # type: ignore[arg-type]
        target_key=d["target_key"],  # type: ignore[arg-type]
        link_type=d.get("link_type", ""),  # type: ignore[arg-type]
    )


def _row_to_changelog(row: sqlite3.Row) -> WorkItemChangelogEntry:
    d: dict[str, object] = dict(row)
    return WorkItemChangelogEntry(
        id=d["id"],  # type: ignore[arg-type]
        work_item_id=d["work_item_id"],  # type: ignore[arg-type]
        field=d["field"],  # type: ignore[arg-type]
        old_value=d.get("old_value"),  # type: ignore[arg-type]
        new_value=d.get("new_value"),  # type: ignore[arg-type]
        author=d.get("author", ""),  # type: ignore[arg-type]
        changed_at=d.get("changed_at", ""),  # type: ignore[arg-type]
    )


class WorkItemStore:
    """Read-side mirror of `SqliteMissionStore` over the `work_items` table.

    RAISE-16622 (V72): `work_items` now carries `project_id` (MUST-ARCH-003 —
    the shared `~/.rai/raise.db` was previously unscoped). Compat window
    (D-S2.2): reads by key are *lenient* — a row is visible whether it
    belongs to this project or is a legacy `''` row, with this project's own
    row preferred when both exist. Writes always stamp `self._project_id`.
    Strict scoping lands after `rai backlog migrate` (S16533.4) has claimed
    every legacy row.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        self._conn.row_factory = sqlite3.Row
        # RAISE-15605: once-per-process, so constructing a store for a READ
        # does not issue migration backfill WRITEs on the shared DB.
        ensure_schema(self._conn)

    def get(self, id: str) -> WorkItem | None:
        """Return the work item with this stable local id, or None.

        Unscoped by project_id: `id` is a globally-unique surrogate PK.
        """
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE id = ?", (id,)
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def get_by_local_key(self, local_key: str) -> WorkItem | None:
        """Return the work item with this human-facing local_key, or None.

        Lenient read (D-S2.2): visible if it belongs to this project or is a
        legacy `''` row; this project's own row wins when both exist.
        """
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE local_key = ? AND project_id IN (?, '') "
            "ORDER BY CASE WHEN project_id = ? THEN 0 ELSE 1 END LIMIT 1",
            (local_key, self._project_id, self._project_id),
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def get_by_jira_key(self, jira_key: str) -> WorkItem | None:
        """Return the work item with this wire-identity jira_key, or None.

        Lenient read (D-S2.2) — see `get_by_local_key`.
        """
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE jira_key = ? AND project_id IN (?, '') "
            "ORDER BY CASE WHEN project_id = ? THEN 0 ELSE 1 END LIMIT 1",
            (jira_key, self._project_id, self._project_id),
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def find_by_parent_and_summary(
        self, parent_jira_key: str, summary: str
    ) -> WorkItem | None:
        """Return existing child story by parent+summary for idempotency check (S8).

        Lenient read (D-S2.2) — see `get_by_local_key`.
        """
        row = self._conn.execute(
            "SELECT * FROM work_items WHERE parent_jira_key = ? AND summary = ? "
            "AND project_id IN (?, '') "
            "ORDER BY CASE WHEN project_id = ? THEN 0 ELSE 1 END LIMIT 1",
            (parent_jira_key, summary, self._project_id, self._project_id),
        ).fetchone()
        return _row_to_work_item(row) if row is not None else None

    def create(self, work_item: WorkItem) -> WorkItem:
        """Insert a fully-populated `WorkItem` row and return it (S3, RAISE-14642).

        Caller is responsible for having resolved `local_key`/`jira_key`/
        parent fields already — no partial rows, no follow-up UPDATE.
        Duplicate `local_key` *within this project* still raises
        `sqlite3.IntegrityError` (project-scoped unique index
        `idx_work_items_project_local`, RAISE-16622/V72) — let it propagate,
        do not swallow (AC5).

        A non-NULL duplicate `jira_key` *within this project* does NOT raise:
        it is resolved as an upsert against `idx_work_items_project_jira`
        (RAISE-16845). The MCP server syncs "ghost" rows — `jira_key` set,
        `summary` empty — for new Jira issues concurrently with the CLI's own
        `create()` call for that same issue; without this, the CLI's INSERT
        would lose that race with an IntegrityError. On conflict, this
        row's data columns (summary, status, description, labels, priority,
        assignee, fix_versions, custom_fields, type, parent_*, no_portfolio,
        updated_at) overwrite the ghost's — the full-data payload wins.
        Identity columns of the pre-existing row (`id`, `project_id`,
        `local_key`, `jira_key`, `created_at`) are deliberately left alone:
        `create()` fills in an existing shell, it does not re-key it.

        The `with self._conn:` block commits on clean exit and ROLLS BACK on
        exception (RAISE-15605): the exception still propagates, but the
        connection no longer keeps the implicit write transaction — and with
        it the shared `~/.rai/raise.db` WAL write lock — open for the life of
        the process.

        Writes always stamp `self._project_id` (D-S2.2) — `work_item.project_id`
        on the passed-in model, if any, is not used for the write; the method
        still returns the exact object passed in, unmutated.
        """
        with self._conn:
            self._conn.execute(
                "INSERT INTO work_items "
                "(id, type, project_id, local_key, jira_key, parent_local_key, "
                "parent_jira_key, summary, status, no_portfolio, description, "
                "labels_json, priority, assignee, fix_versions_json, "
                "custom_fields_json, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(project_id, jira_key) WHERE jira_key IS NOT NULL "
                "DO UPDATE SET "
                "type = excluded.type, "
                "parent_local_key = excluded.parent_local_key, "
                "parent_jira_key = excluded.parent_jira_key, "
                "summary = excluded.summary, "
                "status = excluded.status, "
                "no_portfolio = excluded.no_portfolio, "
                "description = excluded.description, "
                "labels_json = excluded.labels_json, "
                "priority = excluded.priority, "
                "assignee = excluded.assignee, "
                "fix_versions_json = excluded.fix_versions_json, "
                "custom_fields_json = excluded.custom_fields_json, "
                "updated_at = excluded.updated_at",
                (
                    work_item.id,
                    work_item.type,
                    self._project_id,
                    work_item.local_key,
                    work_item.jira_key,
                    work_item.parent_local_key,
                    work_item.parent_jira_key,
                    work_item.summary,
                    work_item.status,
                    int(work_item.no_portfolio),
                    work_item.description,
                    json.dumps(work_item.labels),
                    work_item.priority or "",
                    work_item.assignee or "",
                    json.dumps(work_item.fix_versions),
                    json.dumps(work_item.custom_fields),
                    work_item.created_at,
                    work_item.updated_at,
                ),
            )
        return work_item

    def claim_legacy_row(self, id: str) -> bool:
        """Claim a legacy `project_id=''` row into this project (D6, S16533.4).

        Only claims rows currently at `project_id=''` — a no-op (returns
        `False`) for a row already scoped to any project (this one or
        another's, MUST-ARCH-003) or for an unknown `id`. `update_fields`
        deliberately excludes `project_id` from its whitelist (identity
        column); this is the dedicated write path `rai backlog migrate`
        uses to adopt matched legacy rows.
        """
        with self._conn:
            cur = self._conn.execute(
                "UPDATE work_items SET project_id = ?, "
                "updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') "
                "WHERE id = ? AND project_id = ''",
                (self._project_id, id),
            )
        return bool(cur.rowcount)

    def children(
        self,
        parent_local_key: str,
        type: str | None = None,
    ) -> list[WorkItem]:
        """Return work items whose parent_local_key matches, optionally by type.

        Lenient scoping (D-S2.2): includes this project's rows and legacy
        `''` rows.
        """
        if type is None:
            rows = self._conn.execute(
                "SELECT * FROM work_items WHERE parent_local_key = ? "
                "AND project_id IN (?, '') ORDER BY local_key",
                (parent_local_key, self._project_id),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM work_items WHERE parent_local_key = ? AND type = ? "
                "AND project_id IN (?, '') ORDER BY local_key",
                (parent_local_key, type, self._project_id),
            ).fetchall()
        return [_row_to_work_item(row) for row in rows]

    def check_epic_stories_done(
        self, epic_jira_key: str
    ) -> tuple[bool, list[WorkItem]]:
        """Return (all_done, open_stories) for child stories of the epic.

        Queries work_items for type='story' and parent_jira_key=epic_jira_key,
        scoped leniently (D-S2.2) to this project + legacy `''` rows. Status
        comparison is case-insensitive. Vacuously True when no children.
        """
        rows = self._conn.execute(
            "SELECT * FROM work_items WHERE type = 'story' AND parent_jira_key = ? "
            "AND project_id IN (?, '')",
            (epic_jira_key, self._project_id),
        ).fetchall()
        stories = [_row_to_work_item(row) for row in rows]
        open_stories = [wi for wi in stories if wi.status.lower() != "done"]
        return not bool(open_stories), open_stories

    def list_all(
        self,
        type: str | None = None,
        status: str | None = None,
    ) -> list[WorkItem]:
        """Return all work items, optionally filtered by type and/or status.

        Lenient scoping (D-S2.2): includes this project's rows and legacy
        `''` rows.
        """
        clauses: list[str] = ["project_id IN (?, '')"]
        params: list[str] = [self._project_id]
        if type is not None:
            clauses.append("type = ?")
            params.append(type)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        # `clauses` entries are fixed literals from this function only (never
        # caller input) — values are always bound via `params`.
        query = "SELECT * FROM work_items WHERE " + " AND ".join(clauses)  # noqa: S608
        query += " ORDER BY local_key"
        rows = self._conn.execute(query, params).fetchall()
        return [_row_to_work_item(row) for row in rows]

    def list_by_jira_project(self, project_key: str) -> list[WorkItem]:
        """Return all items whose jira_key matches the given project prefix.

        Matches ``{project_key}-*`` (e.g. ``"RAISE"`` matches ``RAISE-1``,
        ``RAISE-100``, but not ``RAISE2-1``). Lenient scoping: includes this
        project's rows and legacy ``''`` rows, this project's row preferred.

        RAISE-16901: used by cartridge projection to rebuild items.json from
        the shared raise.db so graph builds in any worktree see the same data.
        """
        prefix = f"{project_key}-%"
        rows = self._conn.execute(
            "SELECT * FROM work_items "
            "WHERE jira_key LIKE ? AND project_id IN (?, '') "
            "ORDER BY CASE WHEN project_id = ? THEN 0 ELSE 1 END, jira_key",
            (prefix, self._project_id, self._project_id),
        ).fetchall()
        # De-duplicate: when both a scoped and legacy row exist for the same
        # jira_key, only the first (scoped, due to ORDER BY) is kept.
        seen: set[str] = set()
        items: list[WorkItem] = []
        for row in rows:
            wi = _row_to_work_item(row)
            key = wi.jira_key or wi.local_key
            if key not in seen:
                seen.add(key)
                items.append(wi)
        return items

    def has_any_jira_items(self) -> bool:
        """Return True if ANY *hydrated* row exists for this project.

        RAISE-16901: used by ``_backlog_cold_start`` to detect whether sync
        has ever run (in any worktree sharing this RAI_HOME), without
        depending on items.json presence in the current checkout.

        C2 fix: a stub row (jira_key IS NOT NULL but summary == '' or NULL)
        must NOT be counted as evidence that sync has run.  With 2225 stubs in
        the RAISE DB, the old predicate returned True on a stub-only DB, making
        ``_backlog_cold_start`` silently skip the cold-start flow for users who
        had lost their items.json.  We now require at least one *hydrated* row —
        one that has a non-empty summary — before returning True.
        """
        row = self._conn.execute(
            "SELECT 1 FROM work_items "
            "WHERE jira_key IS NOT NULL "
            "AND summary IS NOT NULL AND summary != '' "
            "AND project_id IN (?, '') LIMIT 1",
            (self._project_id,),
        ).fetchone()
        return row is not None

    # -- Key-store API (replaces SyncLedger YAML) ----------------------------

    def get_jira_key(self, local_key: str) -> str | None:
        """Return jira_key for local_key, or None if unmapped.

        Lenient read (D-S2.2) — see `get_by_local_key`.
        """
        row = self._conn.execute(
            "SELECT jira_key FROM work_items WHERE local_key = ? "
            "AND project_id IN (?, '') "
            "ORDER BY CASE WHEN project_id = ? THEN 0 ELSE 1 END LIMIT 1",
            (local_key, self._project_id, self._project_id),
        ).fetchone()
        return row["jira_key"] if row is not None else None

    def upsert_jira_mapping(  # noqa: PLR0913 — one kwarg per convergeable column
        self,
        local_key: str,
        jira_key: str,
        *,
        summary: str | None = None,
        status: str | None = None,
        issue_type: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        labels: list[str] | None = None,
        assignee: str | None = None,
        fix_versions: list[str] | None = None,
        parent_jira_key: str | None = None,
    ) -> None:
        """Record or update the local_key → jira_key mapping for this project.

        Convergence (RAISE-16938): every field the caller *supplies* is written
        on both arms — INSERT and ON CONFLICT. Previously the conflict arm set
        only `jira_key`/`updated_at`, so a row created empty by a registration
        path (`upsert_jira_mapping(key, key)` with no field values) could never
        be corrected: `rai backlog sync` calls this same method, so syncing
        could not heal it either, and `rai backlog migrate` only fills from
        filesystem YAML. The row stayed a stub — empty `summary`, `status`
        `'todo'`, `type` guessed — and every local-first read served it as
        truth. `pipeline_start` rejected a Jira Bug as a Story on that basis.

        Supplied-vs-absent is `None`, not falsy: passing `summary=""`
        deliberately clears the summary, passing nothing leaves it untouched.
        Absent fields are never reset to defaults — this is not a full replace.

        `type` is the one asymmetric column. When `issue_type` is supplied it
        wins on both arms (mapped through `issue_type_to_work_item_type`). When
        it is absent, `_infer_type(local_key)` seeds the INSERT only and is
        never written on conflict: a key-shape guess must not overwrite a type
        that is already known. `_infer_type` falls back to `"story"` for every
        key that is not the bare `E<n>`/`S<n>` local form — which is every
        remote-native key — so that default is a seed of last resort, not an
        answer (MUST-ARCH-003: key shape is a raise-commons convention, not a
        product contract).

        Adoption step (D-S2.2, fixes V5/V6): before the upsert, a legacy
        `''`-project row matching `local_key` — and not already shadowed by
        an existing row scoped to this project — is claimed into
        `self._project_id`. This makes `ON CONFLICT(project_id, local_key)`
        the correct conflict target post-V72 (the bare `ON CONFLICT(local_key)`
        no longer matches any constraint once the unique index is
        project-scoped) and prevents a legacy row from surviving alongside a
        newly-inserted scoped duplicate.

        Transactional (RAISE-15605): the two statements share a single
        ``with self._conn:`` block — a failure rolls back cleanly and never
        strands the write lock. UNIQUE violations no longer propagate: the
        first ON CONFLICT arm handles (project_id, local_key) duplicates
        (DO UPDATE), the second handles (project_id, jira_key) duplicates
        (DO NOTHING, RAISE-17037).
        """
        supplied = _supplied_columns(
            summary=summary,
            status=status,
            issue_type=issue_type,
            description=description,
            priority=priority,
            labels=labels,
            assignee=assignee,
            fix_versions=fix_versions,
            parent_jira_key=parent_jira_key,
        )

        # INSERT-arm values: supplied wins, else the seed default.
        insert_row: dict[str, object] = {
            "type": supplied.get("type", _infer_type(local_key)),
            "project_id": self._project_id,
            "local_key": local_key,
            "jira_key": jira_key,
            "summary": supplied.get("summary", ""),
            "status": supplied.get("status", "todo"),
            "no_portfolio": 0,
        }
        for column in (
            "description",
            "priority",
            "labels_json",
            "assignee",
            "fix_versions_json",
            "parent_jira_key",
        ):
            if column in supplied:
                insert_row[column] = supplied[column]

        # Conflict arm: jira_key always, plus every supplied column. `type` is
        # absent here unless supplied — never overwrite a known type with a
        # key-shape guess.
        set_columns = ["jira_key", *supplied]
        set_clause = ", ".join(f"{c} = excluded.{c}" for c in set_columns)
        columns = ", ".join(insert_row)
        placeholders = ", ".join("?" for _ in insert_row)
        now = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"

        with self._conn:
            self._conn.execute(
                """
                UPDATE work_items SET project_id = ?
                WHERE project_id = '' AND local_key = ?
                  AND NOT EXISTS (
                      SELECT 1 FROM work_items
                      WHERE project_id = ? AND local_key = ?
                  )
                """,
                (self._project_id, local_key, self._project_id, local_key),
            )
            self._conn.execute(
                f"""
                INSERT INTO work_items (id, {columns}, created_at, updated_at)
                VALUES (lower(hex(randomblob(8))), {placeholders}, {now}, {now})
                ON CONFLICT(project_id, local_key) DO UPDATE SET
                    {set_clause},
                    updated_at = {now}
                ON CONFLICT(project_id, jira_key) WHERE jira_key IS NOT NULL DO NOTHING
                """,  # noqa: S608 — column names are allowlisted by _CONVERGEABLE_COLUMNS
                # Second ON CONFLICT (RAISE-17037): if the same jira_key already maps
                # to a different local_key within this project (parallel agents racing),
                # the first mapping wins silently — no IntegrityError propagates.
                tuple(insert_row.values()),
            )

    def remove_jira_mapping(self, local_key: str) -> None:
        """Clear the jira_key for local_key (keeps the row, NULLs the key)."""
        with self._conn:
            self._conn.execute(
                "UPDATE work_items SET jira_key = NULL"
                " WHERE local_key = ? AND project_id IN (?, '')",
                (local_key, self._project_id),
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
                # Adoption step (D-S2.2, fixes V6): claim a matching legacy
                # `''` row into this project *before* the INSERT OR IGNORE,
                # so it — not a new scoped duplicate — is the row that
                # survives. Without this, a legacy `('', key)` row no longer
                # blocks `INSERT OR IGNORE (self._project_id, key, ...)`
                # once the unique index is project-scoped (V72).
                self._conn.execute(
                    """
                    UPDATE work_items SET project_id = ?
                    WHERE project_id = '' AND local_key = ?
                      AND NOT EXISTS (
                          SELECT 1 FROM work_items
                          WHERE project_id = ? AND local_key = ?
                      )
                    """,
                    (self._project_id, key, self._project_id, key),
                )
                cur = self._conn.execute(
                    """
                    INSERT OR IGNORE INTO work_items
                        (id, type, project_id, local_key, jira_key, summary, status,
                         no_portfolio, created_at, updated_at)
                    VALUES (lower(hex(randomblob(8))), 'story', ?, ?, ?, '', 'todo', 0,
                            strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                            strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                    """,
                    (self._project_id, key, key),
                )
                if cur.rowcount:
                    inserted += 1
                else:
                    skipped += 1
        return inserted, skipped

    def _count_seed_jira_keys(self, keys: list[str]) -> tuple[int, int]:
        """Read-only ``seed_jira_keys`` dry run — count, write nothing.

        Lenient scoping (D-S2.2): a key is "existing" if it has a row scoped
        to this project OR a legacy `''` row (which the real run would
        adopt) — never another project's scoped row (MUST-ARCH-003).
        """
        inserted = 0
        skipped = 0
        for key in keys:
            exists = self._conn.execute(
                "SELECT 1 FROM work_items WHERE (local_key = ? OR jira_key = ?) "
                "AND project_id IN (?, '')",
                (key, key, self._project_id),
            ).fetchone()
            if exists:
                skipped += 1
            else:
                inserted += 1
        return inserted, skipped

    def all_jira_mappings(self) -> dict[str, str]:
        """Return {local_key: jira_key} for all rows with a non-NULL jira_key.

        Lenient scoping (D-S2.2): includes this project's rows and legacy
        `''` rows.
        """
        rows = self._conn.execute(
            "SELECT local_key, jira_key FROM work_items WHERE jira_key IS NOT NULL "
            "AND project_id IN (?, '')",
            (self._project_id,),
        ).fetchall()
        return {row["local_key"]: row["jira_key"] for row in rows}

    # -- Comments / links / changelog CRUD (V72, RAISE-16622) ----------------

    def add_comment(
        self,
        work_item_id: str,
        body: str,
        author: str = "",
        *,
        id: str | None = None,
        created_at: str | None = None,
    ) -> WorkItemComment:
        """Insert (or idempotently upsert) a comment (D-S2.8).

        `id=None` generates a fresh id (same idiom as `work_items.id`).
        An explicit `id` uses `INSERT OR REPLACE` — a Jira comment mirrored
        more than once by id survives without duplicating. FK enforcement is
        ON: a missing `work_item_id` raises `sqlite3.IntegrityError`.

        `created_at` (D7, S16533.4): when provided, the column is written
        explicitly so migrated comments keep their original timestamp
        instead of being stamped with the DDL's `now()` default.
        """
        comment_id = id
        if comment_id is None:
            comment_id = self._conn.execute(
                "SELECT lower(hex(randomblob(8)))"
            ).fetchone()[0]
        with self._conn:
            if created_at is not None:
                self._conn.execute(
                    "INSERT OR REPLACE INTO work_item_comments "
                    "(id, work_item_id, body, author, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (comment_id, work_item_id, body, author, created_at),
                )
            else:
                self._conn.execute(
                    "INSERT OR REPLACE INTO work_item_comments "
                    "(id, work_item_id, body, author) VALUES (?, ?, ?, ?)",
                    (comment_id, work_item_id, body, author),
                )
        row = self._conn.execute(
            "SELECT * FROM work_item_comments WHERE id = ?", (comment_id,)
        ).fetchone()
        return _row_to_comment(row)

    def get_comments(self, work_item_id: str) -> list[WorkItemComment]:
        """Return comments for a work item, ordered by created_at."""
        rows = self._conn.execute(
            "SELECT * FROM work_item_comments WHERE work_item_id = ? "
            "ORDER BY created_at",
            (work_item_id,),
        ).fetchall()
        return [_row_to_comment(row) for row in rows]

    def add_link(self, work_item_id: str, target_key: str, link_type: str = "") -> bool:
        """Insert a link; returns False when the natural UNIQUE suppressed a duplicate."""
        with self._conn:
            cur = self._conn.execute(
                "INSERT OR IGNORE INTO work_item_links "
                "(work_item_id, target_key, link_type) VALUES (?, ?, ?)",
                (work_item_id, target_key, link_type),
            )
        return bool(cur.rowcount)

    def get_links(self, work_item_id: str) -> list[WorkItemLink]:
        """Return links for a work item, ordered by id."""
        rows = self._conn.execute(
            "SELECT * FROM work_item_links WHERE work_item_id = ? ORDER BY id",
            (work_item_id,),
        ).fetchall()
        return [_row_to_link(row) for row in rows]

    def remove_link(self, link_id: int) -> bool:
        """Delete a link by rowid; True if a row went away."""
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM work_item_links WHERE id = ?", (link_id,)
            )
        return bool(cur.rowcount)

    def append_changelog(
        self,
        work_item_id: str,
        field: str,
        old_value: str | None,
        new_value: str | None,
        author: str = "",
    ) -> None:
        """Append a field-level changelog entry (D15/D-S2.7 — append-only, no mutation API)."""
        with self._conn:
            self._conn.execute(
                "INSERT INTO work_item_changelog "
                "(work_item_id, field, old_value, new_value, author) "
                "VALUES (?, ?, ?, ?, ?)",
                (work_item_id, field, old_value, new_value, author),
            )

    def get_changelog(
        self, work_item_id: str, field: str | None = None
    ) -> list[WorkItemChangelogEntry]:
        """Return changelog entries for a work item, optionally filtered by field."""
        if field is None:
            rows = self._conn.execute(
                "SELECT * FROM work_item_changelog WHERE work_item_id = ? ORDER BY id",
                (work_item_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM work_item_changelog WHERE work_item_id = ? "
                "AND field = ? ORDER BY id",
                (work_item_id, field),
            ).fetchall()
        return [_row_to_changelog(row) for row in rows]

    def update_fields(self, id: str, changes: Mapping[str, object]) -> WorkItem | None:
        """Update whitelisted mutable columns and bump updated_at (D-S2.6).

        Raises `ValueError` for any key outside `_UPDATE_FIELDS_WHITELIST` —
        this store owns work_items' SQL; callers must not grow ad hoc raw
        UPDATE statements against it (S16533.3's update_issue/transition_issue
        compose this + `append_changelog`; the store does not auto-write the
        changelog, D-S2.7).
        """
        unknown = set(changes) - set(_UPDATE_FIELDS_WHITELIST)
        if unknown:
            raise ValueError(f"update_fields: unsupported field(s): {sorted(unknown)}")
        if not changes:
            return self.get(id)
        set_clauses: list[str] = []
        params: list[object] = []
        for field, value in changes.items():
            column = _UPDATE_FIELDS_WHITELIST[field]
            if field in _FIELD_VALIDATORS:
                validator = _FIELD_VALIDATORS[field]
                try:
                    value = validator.validate_python(value)
                except ValidationError as exc:
                    raise ValueError(
                        f"Invalid value for {field!r}: expected "
                        f"{validator.core_schema['type']}, got {type(value).__name__}"
                    ) from exc
                value = json.dumps(value)
            elif field in ("priority", "assignee"):
                value = value or ""
            set_clauses.append(f"{column} = ?")
            params.append(value)
        set_clauses.append("updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")
        params.append(id)
        with self._conn:
            # `column` values come only from _UPDATE_FIELDS_WHITELIST above,
            # never from caller input — safe despite the f-string.
            self._conn.execute(
                f"UPDATE work_items SET {', '.join(set_clauses)} WHERE id = ?",  # noqa: S608
                params,
            )
        return self.get(id)


# Columns `upsert_jira_mapping` may converge on the ON CONFLICT arm
# (RAISE-16938). Allowlist for the f-string-interpolated SET clause: every name
# here is a literal column, never caller input.
_CONVERGEABLE_COLUMNS: frozenset[str] = frozenset(
    {
        "summary",
        "status",
        "type",
        "description",
        "priority",
        "labels_json",
        "assignee",
        "fix_versions_json",
        "parent_jira_key",
    }
)


def _supplied_columns(  # noqa: PLR0913 — one kwarg per convergeable column
    *,
    summary: str | None,
    status: str | None,
    issue_type: str | None,
    description: str | None,
    priority: str | None,
    labels: list[str] | None,
    assignee: str | None,
    fix_versions: list[str] | None,
    parent_jira_key: str | None,
) -> dict[str, object]:
    """Map the non-`None` kwargs of `upsert_jira_mapping` to column values.

    `None` means "caller did not supply this", so the column is left out and
    the existing value survives the upsert. A falsy-but-present value (`""`,
    `[]`) IS supplied and is written — clearing a field is a legitimate intent.
    """
    from raise_cli.adapters.key_gen import issue_type_to_work_item_type

    # Table-driven rather than a chain of ifs: one row per convergeable column,
    # `None` filtered out at the end.
    raw: dict[str, object | None] = {
        "summary": summary,
        "status": status,
        "type": None
        if issue_type is None
        else issue_type_to_work_item_type(issue_type),
        "description": description,
        "priority": priority,
        "labels_json": None if labels is None else json.dumps(labels),
        "assignee": assignee,
        "fix_versions_json": (
            None if fix_versions is None else json.dumps(fix_versions)
        ),
        "parent_jira_key": parent_jira_key,
    }
    supplied: dict[str, object] = {c: v for c, v in raw.items() if v is not None}

    unknown = set(supplied) - _CONVERGEABLE_COLUMNS
    if unknown:  # pragma: no cover — guards the f-string interpolation downstream
        raise ValueError(f"non-convergeable columns: {sorted(unknown)}")
    return supplied


# Whitelisted mutable work_items columns for `WorkItemStore.update_fields`
# (D-S2.6) — model field name -> DB column name. Deliberately excludes
# identity/key columns (id, project_id, local_key, jira_key, type,
# created_at) — those have dedicated write paths (create, upsert_jira_mapping,
# promote_key) with their own invariants.
_UPDATE_FIELDS_WHITELIST: dict[str, str] = {
    "summary": "summary",
    "status": "status",
    "description": "description",
    "labels": "labels_json",
    "priority": "priority",
    "assignee": "assignee",
    "fix_versions": "fix_versions_json",
    "custom_fields": "custom_fields_json",
    "parent_local_key": "parent_local_key",
    "parent_jira_key": "parent_jira_key",
}

# Type validators for the JSON-serialized columns in `_UPDATE_FIELDS_WHITELIST`
# (RAISE-16949). `update_fields` json.dumps()'d these without validating shape
# first — an invalid value (e.g. `fix_versions=[{"name": "3.1.1"}]`, a dict
# where `list[str]` is expected) would write cleanly, only to blow up
# `WorkItem` model validation on every subsequent read of that row, corrupting
# the shared `~/.rai/raise.db` for all readers. Validating here rejects the
# bad value with `ValueError` before the UPDATE is issued.
_FIELD_VALIDATORS: dict[str, TypeAdapter[Any]] = {
    "labels": TypeAdapter(list[str]),
    "fix_versions": TypeAdapter(list[str]),
    "custom_fields": TypeAdapter(dict[str, Any]),
}


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


def slugify_local_key(store: WorkItemStore, type: str, title: str) -> str:
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
            row = conn.execute(
                "SELECT workitem_id FROM agent_session_workitems"
                " WHERE project_id = ? AND cc_session_id = ?",
                (pid, session_id),
            ).fetchone()
            if row and row[0]:
                return WorkItemStore(project).get(row[0])
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug("resolve_active_work_item failed", exc_info=True)
    return None
