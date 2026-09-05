"""SQLite-backed PM adapter — local leg using work_items table.

Implements the full ``ProjectManagementAdapter`` protocol (21 methods) plus
the composite duck contract (``promote_key``, ``_save_item``). Uses
``WorkItemStore`` as data layer (D-S3.1) — no raw sqlite3 calls except for
``promote_key`` which updates identity columns excluded from the store's
``update_fields`` whitelist (D-S3.7).

Story: RAISE-16623 (S16533.3)
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from raise_cli.adapters.filesystem_models import BacklogItem
from raise_cli.adapters.key_gen import (
    developer_name,
    issue_type_to_work_item_type,
    resolve_key_prefix,
    seed_from_work_items,
    status_category_for,
)
from raise_cli.adapters.models import (
    AdapterHealth,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    CustomField,
    FailureDetail,
    FieldDefinition,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    IssueTypeInfo,
    LinkTypeDefinition,
    WorkflowState,
)
from raise_cli.adapters.models.pm import IssueLink
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.counter import next_counter
from raise_cli.storage.schema import create_all
from raise_cli.storage.work_items import WorkItem, WorkItemStore

logger = logging.getLogger(__name__)

# Jira REST API field name aliases (same as filesystem.py)
_JIRA_FIELD_ALIASES: dict[str, str] = {
    "fixVersions": "fix_versions",
    "issuetype": "issue_type",
}

# Fields that must not be mutated via update_issue()
_IMMUTABLE_FIELDS: frozenset[str] = frozenset({"key", "created", "comments", "links"})

# WorkItemStore.update_fields model field → store field mapping
_UPDATABLE_FIELDS: frozenset[str] = frozenset(
    {
        "summary",
        "status",
        "description",
        "labels",
        "priority",
        "assignee",
        "fix_versions",
        "custom_fields",
        "parent_local_key",
        "parent_jira_key",
    }
)


def _capitalize_type(type_str: str) -> str:
    """Capitalize the first letter of a work item type for display."""
    if not type_str:
        return type_str
    return type_str[0].upper() + type_str[1:]


class SQLitePMAdapter:
    """PM adapter backed by work_items SQLite table.

    Local-leg adapter for community (without Jira) and composite
    (with Jira) modes. Reads/writes via WorkItemStore.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        self._store = WorkItemStore(self._root)

    # -- Field mapping helpers ------------------------------------------------

    def _to_issue_detail(self, wi: WorkItem) -> IssueDetail:
        """Map a WorkItem to IssueDetail boundary model."""
        comments = self._store.get_comments(wi.id)
        links = self._store.get_links(wi.id)
        return IssueDetail(
            key=wi.local_key,
            summary=wi.summary,
            status=wi.status,
            status_category=status_category_for(
                self._root, _capitalize_type(wi.type), wi.status
            ),
            issue_type=_capitalize_type(wi.type),
            description=wi.description,
            labels=wi.labels,
            parent_key=wi.parent_local_key,
            priority=wi.priority,
            assignee=wi.assignee,
            created=wi.created_at,
            updated=wi.updated_at,
            fix_versions=wi.fix_versions,
            comment_count=len(comments),
            links=[
                IssueLink(target=lnk.target_key, link_type=lnk.link_type)
                for lnk in links
            ],
        )

    def _to_issue_summary(self, wi: WorkItem) -> IssueSummary:
        """Map a WorkItem to IssueSummary boundary model."""
        return IssueSummary(
            key=wi.local_key,
            summary=wi.summary,
            status=wi.status,
            issue_type=_capitalize_type(wi.type),
            parent_key=wi.parent_local_key,
            fix_versions=wi.fix_versions,
            labels=wi.labels,
            priority=wi.priority,
            assignee=wi.assignee,
        )

    def _resolve_work_item(self, key: str) -> WorkItem:
        """Resolve a key to a WorkItem (local_key first, jira_key fallback).

        Raises KeyError if not found by either key.
        """
        wi = self._store.get_by_local_key(key)
        if wi is None:
            wi = self._store.get_by_jira_key(key)
        if wi is None:
            raise KeyError(key)
        return wi

    # -- Key generation helpers -----------------------------------------------

    def _next_staged_epic_key(self) -> str:
        """Allocate the next staged epic key: e{Name}-{seq:03d}."""
        name = developer_name()
        pid = get_project_id(self._root)
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(db, f"staged_epic_{name}", seed_fn=lambda: 0, project_id=pid)
        db.close()
        return f"e{name}-{n:03d}"

    def _next_staged_child_key(self, parent_key: str, type_prefix: str) -> str:
        """Allocate the next staged child key."""
        name = developer_name()
        pid = get_project_id(self._root)
        m_staged = re.match(r"^e[A-Za-z]+-(\d+)$", parent_key)
        if m_staged:
            parent_seq = m_staged.group(1)
            counter_name = f"staged_child_{name}_{parent_seq}_{type_prefix}"
            db = get_project_db(self._root)
            create_all(db)
            n = next_counter(db, counter_name, seed_fn=lambda: 0, project_id=pid)
            db.close()
            return f"{type_prefix}{name}-{parent_seq}.{n}"
        counter_name = f"staged_child_{name}_{type_prefix}"
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(db, counter_name, seed_fn=lambda: 0, project_id=pid)
        db.close()
        return f"{type_prefix}{name}-{n:03d}"

    def _next_story_key(self, parent_key: str) -> str:
        """Allocate the next story key for a given epic."""
        m_legacy = re.match(r"E(\d+)", parent_key)
        if m_legacy:
            epic_num = m_legacy.group(1)
            prefix = f"S{epic_num}."
            pid = get_project_id(self._root)
            db = get_project_db(self._root)
            create_all(db)
            n = next_counter(
                db,
                f"story_{epic_num}",
                seed_fn=lambda: seed_from_work_items(db, prefix),
                project_id=pid,
            )
            db.close()
            return f"S{epic_num}.{n}"
        return self._next_staged_child_key(parent_key, "s")

    def _next_generic_key(self, prefix: str, parent_key: str | None = None) -> str:
        """Allocate the next key for a custom issue type."""
        if parent_key:
            return self._next_staged_child_key(parent_key, prefix)
        pid = get_project_id(self._root)
        db = get_project_db(self._root)
        create_all(db)
        n = next_counter(
            db,
            f"type_{prefix}",
            seed_fn=lambda: seed_from_work_items(db, prefix),
            project_id=pid,
        )
        db.close()
        return f"{prefix}{n}"

    # -- Read operations ----------------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Get issue detail by key (local_key first, jira_key fallback)."""
        wi = self._resolve_work_item(key)
        return self._to_issue_detail(wi)

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        """Search issues using JQL-like syntax.

        Loads all items and filters in Python (same approach as filesystem).
        """
        all_items = self._store.list_all()
        summaries = [self._to_issue_summary(wi) for wi in all_items]
        matched = [s for s in summaries if self._match(s, query)]
        if fetch_all:
            return matched[offset:]
        return matched[offset : offset + limit]

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Get comments for an issue."""
        try:
            wi = self._resolve_work_item(key)
        except KeyError:
            return []
        raw_comments = self._store.get_comments(wi.id)
        comments = [
            Comment(
                id=c.id,
                body=c.body,
                author=c.author,
                created=c.created_at,
            )
            for c in raw_comments
        ]
        if fetch_all:
            return comments[offset:]
        return comments[offset : offset + limit]

    def health(self) -> AdapterHealth:
        """Check adapter health."""
        try:
            count = len(self._store.list_all())
            return AdapterHealth(
                name="local",
                healthy=True,
                message=f"work_items table ({count} items)",
            )
        except Exception as exc:  # noqa: BLE001
            return AdapterHealth(
                name="local",
                healthy=False,
                message=f"work_items table error: {exc}",
            )

    # -- Write operations ---------------------------------------------------

    def create_issue(self, _project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a new issue in work_items."""
        meta = issue.metadata or {}
        now = datetime.now(UTC).isoformat()
        prefix = resolve_key_prefix(self._root, issue.issue_type)
        if prefix == "e":
            key = self._next_staged_epic_key()
        elif prefix == "s":
            parent_key = issue.parent or meta.get("parent_key")
            if not parent_key:
                raise KeyError("Story creation requires parent_key")
            key = self._next_story_key(str(parent_key))
        else:
            parent_key = issue.parent or meta.get("parent_key")
            key = self._next_generic_key(
                prefix, str(parent_key) if parent_key else None
            )

        wi_type = issue_type_to_work_item_type(issue.issue_type)
        work_item = WorkItem(
            id=str(uuid.uuid4()),
            type=wi_type,  # type: ignore[arg-type]
            local_key=key,
            parent_local_key=issue.parent or meta.get("parent_key"),
            summary=issue.summary,
            status="pending",
            description=issue.description,
            labels=issue.labels,
            priority=meta.get("priority"),
            created_at=now,
            updated_at=now,
        )
        self._store.create(work_item)
        return IssueRef(key=key)

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update fields on an existing issue. Writes changelog for each change."""
        wi = self._resolve_work_item(key)
        author = developer_name()
        changes: dict[str, object] = {}
        for field_name, value in fields.items():
            canonical = _JIRA_FIELD_ALIASES.get(field_name, field_name)
            if canonical in _IMMUTABLE_FIELDS:
                continue
            # Map to updatable field names
            if canonical == "parent":
                canonical = "parent_local_key"
            if canonical in _UPDATABLE_FIELDS:
                old_value = getattr(wi, canonical, None)
                if isinstance(old_value, list):
                    old_str = str(old_value)
                    new_str = str(value)
                else:
                    old_str = str(old_value) if old_value is not None else ""
                    new_str = str(value) if value is not None else ""
                if old_str != new_str:
                    self._store.append_changelog(
                        wi.id, canonical, old_str, new_str, author
                    )
                changes[canonical] = value
        if changes:
            self._store.update_fields(wi.id, changes)
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Update issue status and write changelog."""
        wi = self._resolve_work_item(key)
        author = developer_name()
        old_status = wi.status
        self._store.append_changelog(wi.id, "status", old_status, status, author)
        self._store.update_fields(wi.id, {"status": status})
        return IssueRef(key=key)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple issues."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for key in keys:
            try:
                ref = self.transition_issue(key, status)
                succeeded.append(ref)
            except KeyError:
                failed.append(FailureDetail(key=key, error=f"{key} not found"))
        return BatchResult(succeeded=succeeded, failed=failed)

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Create multiple issues."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for spec in issues:
            try:
                ref = self.create_issue(spec.project, spec)
                succeeded.append(ref)
            except Exception as exc:  # noqa: BLE001
                failed.append(FailureDetail(key=spec.summary, error=str(exc)))
        return BatchResult(succeeded=succeeded, failed=failed)

    # -- Relationship & comment operations ----------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Set parent field on child issue."""
        wi = self._resolve_work_item(child_key)
        self._store.update_fields(wi.id, {"parent_local_key": parent_key})
        return True

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Add a link from source to target."""
        wi = self._resolve_work_item(source)
        return self._store.add_link(wi.id, target, link_type)

    def remove_link(self, link_id: str) -> None:
        """Remove a link by its ID."""
        import contextlib

        with contextlib.suppress(ValueError, TypeError):
            self._store.remove_link(int(link_id))

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Add a comment to an issue."""
        wi = self._resolve_work_item(key)
        author = developer_name()
        comment = self._store.add_comment(wi.id, body, author)
        return CommentRef(id=comment.id)

    # -- Discovery (not supported — sqlite adapter is local/offline) ---------

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    # -- Attachments (not supported) -----------------------------------------

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Not supported — sqlite adapter is local/offline."""
        raise NotImplementedError("attach() not supported by sqlite adapter")

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Not supported — sqlite adapter is local/offline."""
        return []

    def download_attachment(self, attachment_id: str) -> bytes:
        """Not supported — sqlite adapter is local/offline."""
        raise NotImplementedError(
            "download_attachment() not supported by sqlite adapter"
        )

    # -- Composite duck contract -------------------------------------------

    def promote_key(self, old_key: str, new_key: str) -> None:
        """Rename a staged key to its permanent Jira key.

        Uses direct SQL for identity columns excluded from update_fields
        whitelist (D-S3.7). Also updates parent references on children.
        """
        wi = self._store.get_by_local_key(old_key)
        if wi is None:
            raise KeyError(old_key)

        conn = self._store._conn  # pyright: ignore[reportPrivateUsage] — D-S3.7: direct SQL for identity columns excluded from update_fields
        with conn:
            conn.execute(
                "UPDATE work_items SET local_key = ?, jira_key = ? WHERE id = ?",
                (new_key, new_key, wi.id),
            )
            conn.execute(
                "UPDATE work_items SET parent_local_key = ? WHERE parent_local_key = ?",
                (new_key, old_key),
            )
            conn.execute(
                "UPDATE work_items SET parent_jira_key = ? WHERE parent_jira_key = ?",
                (new_key, old_key),
            )

    def _save_item(self, item: BacklogItem) -> None:
        """Create or update a local work_items row from a BacklogItem.

        Used by CompositeBacklogAdapter._save_local_issue_mirror to create
        a local mirror for remote-native creates (D-S3.8).
        """
        existing = self._store.get_by_local_key(item.key)
        now = datetime.now(UTC).isoformat()

        if existing is not None:
            # Update existing
            changes: dict[str, object] = {}
            if item.summary:
                changes["summary"] = item.summary
            if item.status:
                changes["status"] = item.status
            if item.description:
                changes["description"] = item.description
            if item.labels:
                changes["labels"] = item.labels
            if item.priority:
                changes["priority"] = item.priority
            if item.assignee:
                changes["assignee"] = item.assignee
            if item.parent:
                changes["parent_local_key"] = item.parent
            if changes:
                self._store.update_fields(existing.id, changes)
        else:
            # Create new
            wi_type = issue_type_to_work_item_type(item.issue_type)
            work_item = WorkItem(
                id=str(uuid.uuid4()),
                type=wi_type,  # type: ignore[arg-type]
                local_key=item.key,
                jira_key=item.key if not item.key.startswith("e") else None,
                parent_local_key=item.parent,
                summary=item.summary,
                status=item.status,
                description=item.description or "",
                labels=item.labels or [],
                priority=item.priority,
                assignee=item.assignee,
                fix_versions=item.fix_versions or [],
                created_at=item.created or now,
                updated_at=item.updated or now,
            )
            self._store.create(work_item)

    # -- Search helper (mirrors filesystem._match) ---------------------------

    @staticmethod
    def _match_in(item: IssueSummary, field: str, values_lower: list[str]) -> bool:
        """Evaluate a single ``field in (values)`` JQL clause."""
        if field in ("issuetype", "issue_type"):
            return item.issue_type.lower() in values_lower
        if field in ("fixversion", "fix_version"):
            return any(fv.lower() in values_lower for fv in item.fix_versions)
        if field == "key":
            return item.key.lower() in values_lower
        return False

    @staticmethod
    def _match_eq(item: IssueSummary, field: str, value: str) -> bool:
        """Evaluate a single ``field = value`` JQL clause."""
        if field == "status":
            return item.status.lower() == value
        if field in ("issuetype", "issue_type"):
            return item.issue_type.lower() == value
        if field == "project":
            return True  # single-project scope
        if field == "name":
            return value in item.summary.lower()
        if field == "parent":
            return (item.parent_key or "").lower() == value
        return False

    def _match(self, item: IssueSummary, query: str) -> bool:
        """Return True when *item* satisfies *query*.

        Supports compound JQL (AND/OR), parenthesized groups, field = value,
        field in (...), and bare text. Mirrors filesystem._match() exactly.
        """
        query = query.strip()
        query = re.sub(r"\s+ORDER\s+BY\s+.*$", "", query, flags=re.IGNORECASE).strip()
        if not query:
            return True
        if query.startswith("(") and query.endswith(")"):
            query = query[1:-1].strip()
        if re.search(r"\bAND\b", query, re.IGNORECASE):
            clauses = re.split(r"\bAND\b", query, flags=re.IGNORECASE)
            return all(self._match(item, c.strip()) for c in clauses if c.strip())
        if re.search(r"\bOR\b", query, re.IGNORECASE):
            clauses = re.split(r"\bOR\b", query, flags=re.IGNORECASE)
            return any(self._match(item, c.strip()) for c in clauses if c.strip())
        m_in = re.match(r"(\w+)\s+in\s*\((.+)\)", query, re.IGNORECASE)
        if m_in:
            field = m_in.group(1).lower()
            values = [v.strip().strip("\"'").lower() for v in m_in.group(2).split(",")]
            return self._match_in(item, field, values)
        m_eq = re.match(r"(\w+)\s*=\s*(.+)", query)
        if m_eq:
            return self._match_eq(
                item,
                m_eq.group(1).lower(),
                m_eq.group(2).strip().strip("\"'").lower(),
            )
        q = query.lower()
        return q in item.key.lower() or q in item.summary.lower()
