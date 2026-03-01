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

    # -- Write operations ---------------------------------------------------

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Append a new epic row to the backlog table."""
        raise NotImplementedError  # T2

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update fields in an existing epic row."""
        raise NotImplementedError  # T2

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Update status column in epic row."""
        raise NotImplementedError  # T2

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple epics."""
        raise NotImplementedError  # T2

    # -- No-ops (no md structure for these) ---------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """No-op: no link structure in markdown table."""

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        """No-op: no link structure in markdown table."""

    def add_comment(self, key: str, body: str) -> CommentRef:
        """No-op: no comment storage in markdown."""
        return CommentRef(id="", url="")
