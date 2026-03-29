"""Filesystem-based PM adapter with YAML file store.

Open-core fallback: provides read + write PM functionality without
external services. Each issue is a YAML file at
``.raise/backlog/items/{KEY}.yaml`` validated by Pydantic on load/dump.

Architecture: S347.2 (E347 Backlog Automation)
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.filesystem_models import (
    BacklogComment,
    BacklogItem,
    BacklogLink,
)
from raise_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    FailureDetail,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)


class FilesystemPMAdapter:
    """PM adapter backed by YAML file store.

    Each issue lives at ``.raise/backlog/items/{KEY}.yaml``.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        self._items_dir = self._root / ".raise" / "backlog" / "items"

    # -- YAML I/O helpers ---------------------------------------------------

    def _item_path(self, key: str) -> Path:
        """Path to a YAML item file."""
        return self._items_dir / f"{key}.yaml"

    def _load_item(self, key: str) -> BacklogItem:
        """Load and validate a single YAML item. Raises KeyError if missing."""
        path = self._item_path(key)
        if not path.exists():
            raise KeyError(key)
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return BacklogItem.model_validate(raw)

    def _save_item(self, item: BacklogItem) -> None:
        """Dump a BacklogItem to YAML, excluding None values for clean files."""
        self._items_dir.mkdir(parents=True, exist_ok=True)
        data = item.model_dump(exclude_none=True)
        # Remove empty collections for clean YAML
        for field in ("comments", "links", "labels"):
            if field in data and not data[field]:
                del data[field]
        if "description" in data and not data["description"]:
            del data["description"]
        path = self._item_path(item.key)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def _load_all_items(self) -> list[BacklogItem]:
        """Load all YAML items from the store."""
        if not self._items_dir.is_dir():
            return []
        items: list[BacklogItem] = []
        for path in sorted(self._items_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            items.append(BacklogItem.model_validate(raw))
        return items

    # -- Key generation helpers -----------------------------------------------

    def _next_epic_key(self) -> str:
        """Scan existing E{N}.yaml files and return E{N+1}."""
        max_n = 0
        if self._items_dir.is_dir():
            for path in self._items_dir.glob("E*.yaml"):
                m = re.match(r"E(\d+)\.yaml$", path.name)
                if m:
                    max_n = max(max_n, int(m.group(1)))
        return f"E{max_n + 1}"

    def _next_story_key(self, parent_key: str) -> str:
        """Scan existing S{epic_num}.{M}.yaml and return S{epic_num}.{M+1}.

        Requires the parent epic key (e.g., 'E1') to derive the epic number.
        """
        m = re.match(r"E(\d+)", parent_key)
        if not m:
            raise ValueError(f"Cannot derive epic number from parent key: {parent_key}")
        epic_num = m.group(1)
        max_m = 0
        if self._items_dir.is_dir():
            for path in self._items_dir.glob(f"S{epic_num}.*.yaml"):
                sm = re.match(rf"S{epic_num}\.(\d+)\.yaml$", path.name)
                if sm:
                    max_m = max(max_m, int(sm.group(1)))
        return f"S{epic_num}.{max_m + 1}"

    # -- Search helper -------------------------------------------------------

    def _match(self, item: IssueSummary, query: str) -> bool:
        """Check if an item matches a search query.

        Supports:
        - Empty query: matches all
        - field = value: exact match on status, key
        - bare text: case-insensitive substring match on key + summary
        """
        query = query.strip()
        if not query:
            return True

        # Parse "field = value" syntax
        m = re.match(r"(\w+)\s*=\s*(.+)", query)
        if m:
            field, value = m.group(1).lower(), m.group(2).strip().lower()
            if field == "status":
                return item.status.lower() == value
            if field == "name":
                return value in item.summary.lower()
            if field == "priority":
                return False
            return False

        # bare text -> substring match on key + summary
        q = query.lower()
        return q in item.key.lower() or q in item.summary.lower()

    # -- Read operations ----------------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Get issue detail by key."""
        item = self._load_item(key)
        return IssueDetail(
            key=item.key,
            summary=item.summary,
            status=item.status,
            issue_type=item.issue_type,
            description=item.description,
            labels=item.labels,
            parent_key=item.parent,
            priority=item.priority,
            assignee=item.assignee,
            created=item.created,
            updated=item.updated,
        )

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search issues."""
        items = self._load_all_items()
        summaries = [
            IssueSummary(
                key=it.key,
                summary=it.summary,
                status=it.status,
                issue_type=it.issue_type,
                parent_key=it.parent,
            )
            for it in items
        ]
        matched = [s for s in summaries if self._match(s, query)]
        return matched[:limit]

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """Get comments for an issue. Returns [] if issue not found."""
        try:
            item = self._load_item(key)
        except KeyError:
            return []
        comments = [
            Comment(id=c.id, body=c.body, author=c.author, created=c.created)
            for c in item.comments
        ]
        return comments[:limit]

    def health(self) -> AdapterHealth:
        """Check adapter health."""
        if self._items_dir.is_dir():
            count = len(list(self._items_dir.glob("*.yaml")))
            return AdapterHealth(
                name="filesystem",
                healthy=True,
                message=f".raise/backlog/items/ ({count} items)",
            )
        return AdapterHealth(
            name="filesystem",
            healthy=False,
            message="YAML store not found (.raise/backlog/items/)",
        )

    # -- Write operations ---------------------------------------------------

    def create_issue(self, _project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a new issue."""
        meta = issue.metadata or {}
        now = datetime.now(UTC).isoformat()
        itype = issue.issue_type.lower()
        if itype == "epic":
            key = self._next_epic_key()
        elif itype in ("story", "subtask"):
            parent_key = meta.get("parent_key")
            if not parent_key:
                raise KeyError("Story creation requires parent_key")
            key = self._next_story_key(parent_key)
        else:
            # Default to epic-style key for Task and other types
            key = self._next_epic_key()
        new_item = BacklogItem(
            key=key,
            summary=issue.summary,
            issue_type=issue.issue_type,
            status="pending",
            parent=meta.get("parent_key"),
            description=issue.description,
            labels=issue.labels,
            priority=meta.get("priority"),
            created=now,
            updated=now,
        )
        self._save_item(new_item)
        return IssueRef(key=new_item.key)

    # Fields that must not be mutated via update_issue()
    _IMMUTABLE_FIELDS: frozenset[str] = frozenset(
        {"key", "created", "comments", "links"}
    )

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update fields on an existing issue."""
        item = self._load_item(key)
        for field_name, value in fields.items():
            if field_name in self._IMMUTABLE_FIELDS:
                continue
            if hasattr(item, field_name):
                setattr(item, field_name, value)
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Update issue status."""
        item = self._load_item(key)
        item.status = status
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)
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

    # -- Relationship & comment operations ----------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """Set parent field on child issue."""
        item = self._load_item(child_key)
        item.parent = parent_key
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        """Add a link from source to target."""
        item = self._load_item(source)
        item.links.append(BacklogLink(target=target, link_type=link_type))
        item.updated = datetime.now(UTC).isoformat()
        self._save_item(item)

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Add a comment to an issue."""
        item = self._load_item(key)
        next_n = len(item.comments) + 1
        comment_id = f"{key}-{next_n}"
        now = datetime.now(UTC).isoformat()
        item.comments.append(
            BacklogComment(id=comment_id, body=body, author="rai", created=now)
        )
        item.updated = now
        self._save_item(item)
        return CommentRef(id=comment_id)
