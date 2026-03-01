"""Filesystem-based PM adapter over governance/backlog.md.

Open-core fallback: provides read + write PM functionality without
external services. Parses the epic table in backlog.md using the
existing BacklogParser infrastructure.

Architecture: S301.9 (E301 Agent Tool Abstraction)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from rai_cli.adapters.models import (
    AdapterHealth,
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
    """PM adapter backed by governance/backlog.md.

    Reads: search, get_issue, get_comments, health.
    Writes: create_issue, update_issue, transition_issue, batch_transition.
    No-ops: add_comment, link_to_parent, link_issues (no md structure).
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        self._backlog_path = self._root / "governance" / "backlog.md"

    # -- Internal helpers ---------------------------------------------------

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

    def _match(self, epic: IssueSummary, query: str) -> bool:
        """Check if an epic matches a search query.

        Supports:
        - Empty query: matches all
        - field = value: exact match on status, name, priority
        - bare text: case-insensitive substring match on summary
        """
        query = query.strip()
        if not query:
            return True

        # field = value
        m = re.match(r"(\w+)\s*=\s*(.+)", query)
        if m:
            field, value = m.group(1).lower(), m.group(2).strip().lower()
            if field == "status":
                return epic.status.lower() == value
            if field == "name":
                return value in epic.summary.lower()
            if field == "priority":
                # priority not in IssueSummary, skip
                return False
            return False

        # bare text → name match
        return query.lower() in epic.summary.lower()

    # -- Read operations ----------------------------------------------------

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search epics in backlog.md."""
        epics = self._parse_epics()
        matched = [e for e in epics if self._match(e, query)]
        return matched[:limit]

    def get_issue(self, key: str) -> IssueDetail:
        """Get epic detail by ID (e.g., 'E1')."""
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

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """No comment storage in markdown — always empty."""
        return []

    def health(self) -> AdapterHealth:
        """Check if backlog.md exists and count epics."""
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

    # -- Write helpers ------------------------------------------------------

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
        """Find the line index of a specific epic row. Returns -1 if not found.

        Matches both simple (E1) and Jira link ([RAISE-301](url)) formats.
        """
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
        # Remove bold markers
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
        """Append a new epic row to the backlog table."""
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
        """Update fields in an existing epic row."""
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
        """Update status column in epic row."""
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
        """Transition multiple epics."""
        from rai_cli.adapters.models import FailureDetail

        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for key in keys:
            try:
                ref = self.transition_issue(key, status)
                succeeded.append(ref)
            except KeyError:
                failed.append(FailureDetail(key=key, error=f"Epic {key} not found"))
        return BatchResult(succeeded=succeeded, failed=failed)

    # -- No-ops (no md structure for these) ---------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """No-op: no link structure in markdown table."""

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        """No-op: no link structure in markdown table."""

    def add_comment(self, key: str, body: str) -> CommentRef:
        """No-op: no comment storage in markdown."""
        return CommentRef(id="", url="")
