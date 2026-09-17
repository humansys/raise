"""``rai backlog migrate`` — core migration logic (scan -> plan -> execute).

Imports the filesystem YAML backlog (``.raise/backlog/``) into the SQLite
``work_items`` table (plus ``work_item_comments``/``work_item_links``).
Follows the ``rai clean`` purge pattern (D1, story design.md): planning is
read-only and produces a serializable ``MigrationPlan``; dry-run means
``execute_migration`` is never called.

Story: RAISE-16624 (S16533.4)
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from raise_cli.adapters.filesystem import FilesystemPMAdapter
from raise_cli.adapters.filesystem_models import BacklogItem
from raise_cli.adapters.key_gen import issue_type_to_work_item_type
from raise_cli.storage.work_items import WorkItem, WorkItemStore

# D5: strict wire-key shape. Excludes local-only keys (E1, S1.1) and
# hex-suffixed staged keys (TMP-7D983BB0) that `_save_item`'s looser
# `not key.startswith("e")` heuristic would mis-tag as Jira keys.
_WIRE_KEY_RE = re.compile(r"[A-Z][A-Z0-9]*-\d+")

# D11: work_items columns eligible for the fill-only-empty update rule,
# in a fixed order so `MigrationAction.fields` is deterministic.
_FILL_ONLY_EMPTY_FIELDS: tuple[str, ...] = (
    "summary",
    "status",
    "description",
    "labels",
    "priority",
    "assignee",
    "fix_versions",
    "parent_local_key",
    "parent_jira_key",
)


def _wire_key(key: str | None) -> str | None:
    """Return *key* iff it strictly matches the wire-key shape (D5), else None."""
    if key and _WIRE_KEY_RE.fullmatch(key):
        return key
    return None


def _is_empty(value: object) -> bool:
    """D11 'empty' predicate: '' / [] / {} / None all count as unset."""
    if value is None:
        return True
    if isinstance(value, str):
        return value == ""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


class MigrationAction(BaseModel):
    """A single planned per-item migration action.

    `item`/`matched_id` are implementation additions beyond the design
    sketch (§4.2 "exact shapes may be refined at plan phase"): they let
    `execute_migration` be a pure application of the plan — no second
    filesystem scan or store re-match — mirroring how `rai clean`'s
    `CleanAction` embeds the full `Residue` rather than a bare path.
    """

    key: str
    action: Literal["insert", "update", "skip", "error"]
    fields: list[str] = []
    claim_project: bool = False
    comments: int = 0
    links: int = 0
    orphan: bool = False
    source_path: str = ""
    detail: str = ""
    item: BacklogItem | None = None
    matched_id: str | None = None


class MigrationPlan(BaseModel):
    """Read-only, JSON-serializable output of `plan_migration`."""

    actions: list[MigrationAction]
    orphan_keys_excluded: list[str]
    invalid_files: list[str]
    db_only_rows: int

    @property
    def actionable(self) -> bool:
        """True when at least one action would change the DB (D14 exit codes)."""
        return any(a.action in ("insert", "update") for a in self.actions)


class MigrationOutcome(BaseModel):
    """Per-action result of `execute_migration`."""

    action: MigrationAction
    status: Literal["done", "skipped", "failed"]
    detail: str = ""


class MigrationResult(BaseModel):
    """Aggregated result of `execute_migration`."""

    outcomes: list[MigrationOutcome]
    ok: bool


def scan_orphans(
    backlog_root: Path, visible_keys: set[str]
) -> tuple[list[tuple[BacklogItem, Path]], list[str]]:
    """Return (orphan items with their source paths, unparseable file paths).

    D12 algorithm: every subdirectory of *backlog_root* except ``items/`` is
    scanned (robust against future glob misses of any naming scheme, and
    immune to double-counting `e*/` dirs — those are already in
    *visible_keys*). Per-file try/except (§4.8) isolates a malformed orphan
    YAML into the second return value instead of raising.
    """
    orphans: list[tuple[BacklogItem, Path]] = []
    invalid_files: list[str] = []
    if not backlog_root.is_dir():
        return orphans, invalid_files

    seen: set[str] = set()
    for entry in sorted(backlog_root.iterdir()):
        if not entry.is_dir() or entry.name == "items":
            continue
        for yaml_path in sorted(entry.glob("*.yaml")):
            try:
                raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                item = BacklogItem.model_validate(raw)
            except Exception:  # noqa: BLE001 — per-file fault isolation (D12/§4.8)
                invalid_files.append(str(yaml_path))
                continue
            if item.key in visible_keys or item.key in seen:
                continue
            seen.add(item.key)
            orphans.append((item, yaml_path))
    return orphans, invalid_files


def _fields_to_fill(existing: WorkItem, item: BacklogItem) -> list[str]:
    """D11 fill-only-empty: DB field is empty/default AND filesystem value is non-empty."""
    candidates: dict[str, tuple[object, object]] = {
        "summary": (existing.summary, item.summary),
        "status": (existing.status, item.status),
        "description": (existing.description, item.description),
        "labels": (existing.labels, item.labels),
        "priority": (existing.priority, item.priority),
        "assignee": (existing.assignee, item.assignee),
        "fix_versions": (existing.fix_versions, item.fix_versions),
        "parent_local_key": (existing.parent_local_key, item.parent),
        "parent_jira_key": (existing.parent_jira_key, _wire_key(item.parent)),
    }
    fields: list[str] = []
    for field in _FILL_ONLY_EMPTY_FIELDS:
        db_value, fs_value = candidates[field]
        db_empty = (
            db_value in ("", "todo") if field == "status" else _is_empty(db_value)
        )
        if db_empty and not _is_empty(fs_value) and fs_value != db_value:
            fields.append(field)
    return fields


def _resolve_existing(store: WorkItemStore, key: str) -> WorkItem | None:
    """D4 match order: local_key first, jira_key fallback (mirrors `_resolve_work_item`)."""
    existing = store.get_by_local_key(key)
    if existing is None:
        existing = store.get_by_jira_key(key)
    return existing


def plan_migration(
    root: Path, store: WorkItemStore, *, include_orphans: bool
) -> MigrationPlan:
    """Read-only: iterate `FilesystemPMAdapter(root).load_all_items()` + orphans.

    No `.raise/backlog/` directory -> empty plan (§4.8 "nothing to migrate").
    Malformed YAML in `items/` is NOT caught here (§4.8 — `_load_all_items()`
    error semantics are out of scope for this story); the CLI layer wraps
    this call and reports the failing file.
    """
    backlog_root = root / ".raise" / "backlog"
    if not backlog_root.is_dir():
        return MigrationPlan(
            actions=[], orphan_keys_excluded=[], invalid_files=[], db_only_rows=0
        )

    adapter = FilesystemPMAdapter(project_root=root)
    canonical_items = adapter.load_all_items()
    canonical_keys = {item.key for item in canonical_items}
    orphan_pairs, invalid_files = scan_orphans(backlog_root, canonical_keys)

    entries: list[tuple[BacklogItem, Path | None, bool]] = [
        (item, None, False) for item in canonical_items
    ]
    entries.extend((item, path, True) for item, path in orphan_pairs)

    actions: list[MigrationAction] = []
    orphan_keys_excluded: list[str] = []
    matched_ids: set[str] = set()

    for item, path, is_orphan in entries:
        existing = _resolve_existing(store, item.key)
        if existing is not None:
            matched_ids.add(existing.id)

        if is_orphan and not include_orphans:
            orphan_keys_excluded.append(item.key)
            continue

        source_path = str(path.relative_to(root)) if path is not None else ""

        if existing is None:
            actions.append(
                MigrationAction(
                    key=item.key,
                    action="insert",
                    comments=len(item.comments),
                    links=len(item.links),
                    orphan=is_orphan,
                    source_path=source_path,
                    item=item,
                )
            )
            continue

        fields = _fields_to_fill(existing, item)
        claim_project = existing.project_id == ""
        verb: Literal["update", "skip"] = (
            "update" if (fields or claim_project) else "skip"
        )
        actions.append(
            MigrationAction(
                key=item.key,
                action=verb,
                fields=fields,
                claim_project=claim_project,
                comments=len(item.comments),
                links=len(item.links),
                orphan=is_orphan,
                source_path=source_path,
                item=item,
                matched_id=existing.id,
            )
        )

    db_only_rows = len({wi.id for wi in store.list_all()} - matched_ids)

    return MigrationPlan(
        actions=actions,
        orphan_keys_excluded=orphan_keys_excluded,
        invalid_files=invalid_files,
        db_only_rows=db_only_rows,
    )


def _build_insert_work_item(item: BacklogItem, now: str) -> WorkItem:
    """§4.4 field mapping for a brand-new `work_items` row."""
    wi_type = issue_type_to_work_item_type(item.issue_type)
    custom_fields: dict[str, object] = {}
    if wi_type != item.issue_type.lower():
        # D8: the mapping was lossy — preserve the original so it is not
        # silently destroyed.
        custom_fields["source_issue_type"] = item.issue_type
    return WorkItem(
        id=str(uuid.uuid4()),
        type=wi_type,  # type: ignore[arg-type]
        local_key=item.key,
        jira_key=_wire_key(item.key),
        parent_local_key=item.parent,
        parent_jira_key=_wire_key(item.parent),
        summary=item.summary,
        status=item.status,
        description=item.description,
        labels=item.labels,
        priority=item.priority,
        assignee=item.assignee,
        fix_versions=item.fix_versions,
        custom_fields=custom_fields,
        created_at=item.created or now,
        updated_at=item.updated or now,
    )


def _build_update_changes(item: BacklogItem, fields: list[str]) -> dict[str, object]:
    """Map the D11 fill-only-empty `fields` selection to `update_fields` changes."""
    mapping: dict[str, object] = {
        "summary": item.summary,
        "status": item.status,
        "description": item.description,
        "labels": item.labels,
        "priority": item.priority,
        "assignee": item.assignee,
        "fix_versions": item.fix_versions,
        "parent_local_key": item.parent,
        "parent_jira_key": _wire_key(item.parent),
    }
    return {field: mapping[field] for field in fields}


def _apply_comments_and_links(
    store: WorkItemStore, work_item_id: str, item: BacklogItem
) -> None:
    """Add-only comments/links — DB wins if comment already exists (F2 fix, D11 coherent)."""
    existing_comment_ids = {c.id for c in store.get_comments(work_item_id)}
    for comment in item.comments:
        cid = comment.id or None
        if cid and cid in existing_comment_ids:
            continue
        store.add_comment(
            work_item_id,
            comment.body,
            comment.author,
            id=cid,
            created_at=comment.created or None,
        )
    for link in item.links:
        store.add_link(work_item_id, link.target, link.link_type)


def execute_migration(
    plan: MigrationPlan,
    root: Path,  # noqa: ARG001 - root kept for signature parity with plan_migration (§4.2)
    store: WorkItemStore,
) -> MigrationResult:
    """Apply insert/update actions; per-item fault isolation (§4.8, D8).

    A failed item (e.g. `sqlite3.IntegrityError` from a concurrent write
    between plan and execute) is recorded as a failed outcome and the batch
    continues — never raised. `action == "skip"` still re-applies
    comments/links (cheap, idempotent by constraint) so a re-run after a
    partial failure converges.
    """
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    outcomes: list[MigrationOutcome] = []

    for action in plan.actions:
        if action.action == "error":
            outcomes.append(
                MigrationOutcome(action=action, status="failed", detail=action.detail)
            )
            continue

        try:
            if action.item is None:
                msg = f"migration action for {action.key!r} carries no item data"
                raise ValueError(msg)

            if action.action == "insert":
                work_item = _build_insert_work_item(action.item, now)
                store.create(work_item)
                work_item_id = work_item.id
            else:
                if action.matched_id is None:
                    msg = f"migration action for {action.key!r} has no matched row id"
                    raise ValueError(msg)
                work_item_id = action.matched_id
                if action.claim_project:
                    store.claim_legacy_row(work_item_id)
                if action.fields:
                    changes = _build_update_changes(action.item, action.fields)
                    store.update_fields(work_item_id, changes)

            _apply_comments_and_links(store, work_item_id, action.item)

            status: Literal["done", "skipped"] = (
                "skipped" if action.action == "skip" else "done"
            )
            outcomes.append(MigrationOutcome(action=action, status=status))
        except Exception as exc:  # noqa: BLE001 — per-item fault isolation (D8/§4.8)
            outcomes.append(
                MigrationOutcome(action=action, status="failed", detail=str(exc))
            )

    ok = not any(o.status == "failed" for o in outcomes)
    return MigrationResult(outcomes=outcomes, ok=ok)
