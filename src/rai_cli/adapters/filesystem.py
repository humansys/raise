"""Filesystem-based PM adapter with YAML file store.

Open-core fallback: provides read + write PM functionality without
external services. Each issue is a YAML file at
``.raise/backlog/items/{KEY}.yaml`` validated by Pydantic on load/dump.

Legacy mode: falls back to parsing ``governance/backlog.md`` markdown
table when no YAML store is present (to be removed in T7).

Architecture: S347.2 (E347 Backlog Automation)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from rai_cli.adapters.models import (
    AdapterHealth,
    BacklogItem,
    BatchResult,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)
from rai_cli.governance.parsers.backlog import extract_epics


class FilesystemPMAdapter:
    """PM adapter backed by YAML file store.

    Primary: ``.raise/backlog/items/{KEY}.yaml`` (one file per issue).
    Fallback: ``governance/backlog.md`` markdown table (legacy, read-only-ish).
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        self._items_dir = self._root / ".raise" / "backlog" / "items"
        # Legacy fallback
        self._backlog_path = self._root / "governance" / "backlog.md"

    @property
    def _use_yaml(self) -> bool:
        """True when YAML store directory exists."""
        return self._items_dir.is_dir()

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

    # -- Legacy markdown helpers (fallback) ----------------------------------

    def _parse_epics(self) -> list[IssueSummary]:
        """Parse backlog.md into IssueSummary list."""
        if not self._backlog_path.exists():
            return []

        concepts = extract_epics(self._backlog_path, self._root)
        results: list[IssueSummary] = []
        for c in concepts:
            meta = c.metadata or {}
            results.append(
                IssueSummary(
                    key=meta.get("epic_id", c.id),
                    summary=meta.get("name", ""),
                    status=meta.get("status", "pending"),
                    issue_type="Epic",
                )
            )
        return results

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

        # field = value
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

        # bare text → substring match on key + summary
        q = query.lower()
        return q in item.key.lower() or q in item.summary.lower()

    # -- Read operations ----------------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Get issue detail by key."""
        if self._use_yaml:
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
        # Legacy fallback
        epics = self._parse_epics()
        for e in epics:
            if e.key == key:
                return IssueDetail(
                    key=e.key,
                    summary=e.summary,
                    status=e.status,
                    issue_type="Epic",
                    description="",
                    labels=[],
                )
        raise KeyError(key)

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search issues."""
        if self._use_yaml:
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
        # Legacy fallback
        epics = self._parse_epics()
        matched = [e for e in epics if self._match(e, query)]
        return matched[:limit]

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """Get comments for an issue. Returns [] if issue not found."""
        if self._use_yaml:
            try:
                item = self._load_item(key)
            except KeyError:
                return []
            comments = [
                Comment(id=c.id, body=c.body, author=c.author, created=c.created)
                for c in item.comments
            ]
            return comments[:limit]
        return []

    def health(self) -> AdapterHealth:
        """Check adapter health."""
        if self._use_yaml:
            count = len(list(self._items_dir.glob("*.yaml")))
            return AdapterHealth(
                name="filesystem",
                healthy=True,
                message=f".raise/backlog/items/ ({count} items)",
            )
        if not self._items_dir.is_dir() and not self._backlog_path.exists():
            return AdapterHealth(
                name="filesystem",
                healthy=False,
                message="YAML store and backlog.md not found",
            )
        # Legacy fallback
        if not self._backlog_path.exists():
            return AdapterHealth(
                name="filesystem",
                healthy=False,
                message="governance/backlog.md not found",
            )
        epics = self._parse_epics()
        return AdapterHealth(
            name="filesystem",
            healthy=True,
            message=f"governance/backlog.md ({len(epics)} epics)",
        )

    # -- Write helpers (legacy markdown) ------------------------------------

    _STATUS_TO_DISPLAY: dict[str, str] = {
        "complete": "✅ Complete",
        "in_progress": "🚀 In Progress",
        "pending": "📋 Backlog",
        "backlog": "📋 Backlog",
        "draft": "📋 DRAFT",
        "deferred": "→ Deferred",
        "planning": "📋 Planning",
    }

    def _next_epic_id(self) -> str:
        """Find max E{N} in table and return E{N+1}."""
        epics = self._parse_epics()
        max_n = 0
        for e in epics:
            m = re.match(r"E(\d+)", e.key)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"E{max_n + 1}"

    def _find_table_end(self, lines: list[str]) -> int:
        """Find the line index after the last table row in Epics Overview."""
        in_table = False
        last_row = -1
        for i, line in enumerate(lines):
            if re.match(r"^\|\s*-+", line):
                in_table = True
                continue
            if in_table and line.startswith("|"):
                last_row = i
            elif in_table and not line.startswith("|"):
                break
        return last_row + 1 if last_row >= 0 else -1

    def _format_row(
        self,
        epic_id: str,
        name: str,
        status_display: str,
        scope_doc: str | None,
        priority: str | None,
    ) -> str:
        scope = f"`{scope_doc}`" if scope_doc else "—"
        prio = priority or "—"
        return f"| {epic_id} | **{name}** | {status_display} | {scope} | {prio} |"

    def _find_epic_row(self, lines: list[str], key: str) -> int:
        """Find the line index of a specific epic row. Returns -1 if not found."""
        esc = re.escape(key)
        pattern = re.compile(
            rf"^\|\s*(?:{esc}|\[{esc}\]\([^)]+\))\s*\|"
        )
        for i, line in enumerate(lines):
            if pattern.match(line):
                return i
        return -1

    def _parse_row(self, line: str) -> dict[str, str]:
        """Parse a table row into named fields."""
        inner = [c.strip() for c in line.strip("|").split("|")]
        if len(inner) < 5:
            return {}
        name = inner[1].strip()
        name = re.sub(r"^\*\*(.+)\*\*$", r"\1", name)
        return {
            "id": inner[0].strip(),
            "name": name,
            "status_display": inner[2].strip(),
            "scope_doc": inner[3].strip(),
            "priority": inner[4].strip(),
        }

    def _extract_scope_priority(
        self, parsed: dict[str, str]
    ) -> tuple[str | None, str | None]:
        """Extract scope_doc and priority values from parsed row."""
        scope_raw = parsed.get("scope_doc", "—")
        scope_match = re.match(r"`(.+)`", scope_raw)
        scope_doc = scope_match.group(1) if scope_match else None
        priority_raw = parsed.get("priority", "—")
        priority = priority_raw if priority_raw != "—" else None
        return scope_doc, priority

    def _write_lines(self, lines: list[str]) -> None:
        self._backlog_path.write_text("\n".join(lines), encoding="utf-8")

    # -- Write operations ---------------------------------------------------

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a new issue."""
        if self._use_yaml:
            from datetime import UTC, datetime

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

        # Legacy fallback
        text = self._backlog_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        epic_id = self._next_epic_id()
        status_display = self._STATUS_TO_DISPLAY.get("pending", "📋 Backlog")
        meta = issue.metadata or {}
        row = self._format_row(
            epic_id,
            issue.summary,
            status_display,
            meta.get("scope_doc"),
            meta.get("priority"),
        )
        insert_at = self._find_table_end(lines)
        if insert_at < 0:
            raise ValueError("Cannot find epic table in backlog.md")
        lines.insert(insert_at, row)
        self._write_lines(lines)
        return IssueRef(key=epic_id)

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update fields on an existing issue."""
        if self._use_yaml:
            from datetime import UTC, datetime

            item = self._load_item(key)
            for field_name, value in fields.items():
                if hasattr(item, field_name):
                    setattr(item, field_name, value)
            item.updated = datetime.now(UTC).isoformat()
            self._save_item(item)
            return IssueRef(key=key)

        # Legacy fallback
        text = self._backlog_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        row_idx = self._find_epic_row(lines, key)
        if row_idx < 0:
            raise KeyError(key)
        parsed = self._parse_row(lines[row_idx])
        raw_id = parsed.get("id", key)
        name = fields.get("summary", parsed.get("name", ""))
        status_display = parsed.get("status_display", "📋 Backlog")
        scope_doc, priority = self._extract_scope_priority(parsed)
        if "priority" in fields:
            priority = fields["priority"]
        if "scope_doc" in fields:
            scope_doc = fields["scope_doc"]
        lines[row_idx] = self._format_row(raw_id, name, status_display, scope_doc, priority)
        self._write_lines(lines)
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Update issue status."""
        if self._use_yaml:
            from datetime import UTC, datetime

            item = self._load_item(key)
            item.status = status
            item.updated = datetime.now(UTC).isoformat()
            self._save_item(item)
            return IssueRef(key=key)

        # Legacy fallback
        text = self._backlog_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        row_idx = self._find_epic_row(lines, key)
        if row_idx < 0:
            raise KeyError(key)
        parsed = self._parse_row(lines[row_idx])
        raw_id = parsed.get("id", key)
        status_display = self._STATUS_TO_DISPLAY.get(
            status.lower(), f"📋 {status.title()}"
        )
        name = parsed.get("name", "")
        scope_doc, priority = self._extract_scope_priority(parsed)
        lines[row_idx] = self._format_row(raw_id, name, status_display, scope_doc, priority)
        self._write_lines(lines)
        return IssueRef(key=key)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple issues."""
        from rai_cli.adapters.models import FailureDetail

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
        if self._use_yaml:
            from datetime import UTC, datetime

            item = self._load_item(child_key)
            item.parent = parent_key
            item.updated = datetime.now(UTC).isoformat()
            self._save_item(item)
            return
        # Legacy: no-op

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        """Add a link from source to target."""
        if self._use_yaml:
            from datetime import UTC, datetime

            from rai_cli.adapters.models import BacklogLink

            item = self._load_item(source)
            item.links.append(BacklogLink(target=target, link_type=link_type))
            item.updated = datetime.now(UTC).isoformat()
            self._save_item(item)
            return
        # Legacy: no-op

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Add a comment to an issue."""
        if self._use_yaml:
            from datetime import UTC, datetime

            from rai_cli.adapters.models import BacklogComment

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

        return CommentRef(id="", url="")
