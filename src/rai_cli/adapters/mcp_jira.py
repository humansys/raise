"""Jira adapter via MCP bridge (mcp-atlassian server).

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to the corresponding ``mcp-atlassian`` tool call via ``McpBridge``.

Configuration: reads ``.raise/jira.yaml`` for status_mapping and project config.
Connection: lazy — no MCP server connection until first method call.

Architecture: S301.3 design, AR-S3-2, AR-S3-5
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from rai_cli.adapters.mcp_bridge import McpBridge, McpBridgeError, McpToolResult
from rai_cli.adapters.models import (
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


class McpJiraAdapter:
    """Jira adapter that delegates to mcp-atlassian via McpBridge.

    Implements ``AsyncProjectManagementAdapter`` protocol (structural typing).

    Args:
        project_root: Project root directory containing ``.raise/jira.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        config = self._load_jira_config(root)

        status_mapping = config.get("status_mapping")
        if not status_mapping:
            msg = (
                "Missing 'status_mapping' in .raise/jira.yaml. "
                "Add a status_mapping section with status names and transition IDs."
            )
            raise ValueError(msg)

        self._status_mapping: dict[str, int] = status_mapping
        self._bridge = McpBridge(server_command="mcp-atlassian")

    @staticmethod
    def _load_jira_config(root: Path) -> dict[str, Any]:
        """Read and parse .raise/jira.yaml."""
        config_path = root / ".raise" / "jira.yaml"
        if not config_path.exists():
            msg = f"Jira config not found: {config_path}"
            raise FileNotFoundError(msg)
        with open(config_path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return data

    def _resolve_transition_id(self, status: str) -> str:
        """Map status name to Jira transition ID.

        Args:
            status: Status name (e.g. "done", "in-progress").

        Returns:
            Transition ID as string.

        Raises:
            ValueError: If status is not in status_mapping.
        """
        tid = self._status_mapping.get(status)
        if tid is None:
            available = ", ".join(sorted(self._status_mapping.keys()))
            msg = f"Unknown status '{status}'. Available: {available}"
            raise ValueError(msg)
        return str(tid)

    # ----- CRUD -----

    async def create_issue(
        self, project_key: str, issue: IssueSpec
    ) -> IssueRef:
        args: dict[str, Any] = {
            "project_key": project_key,
            "summary": issue.summary,
            "issue_type": issue.issue_type,
        }
        if issue.description:
            args["description"] = issue.description
        if issue.labels:
            args["additional_fields"] = json.dumps(
                {**issue.metadata, "labels": issue.labels}
            )
        elif issue.metadata:
            args["additional_fields"] = json.dumps(issue.metadata)

        result = await self._bridge.call("jira_create_issue", args)
        return self._parse_issue_ref(result)

    async def get_issue(self, key: str) -> IssueDetail:
        result = await self._bridge.call(
            "jira_get_issue", {"issue_key": key}
        )
        return self._parse_issue_detail(result)

    async def update_issue(
        self, key: str, fields: dict[str, Any]
    ) -> IssueRef:
        result = await self._bridge.call(
            "jira_update_issue",
            {"issue_key": key, "fields": json.dumps(fields)},
        )
        return self._parse_issue_ref(result)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        tid = self._resolve_transition_id(status)
        result = await self._bridge.call(
            "jira_transition_issue",
            {"issue_key": key, "transition_id": tid},
        )
        return self._parse_issue_ref(result)

    # ----- Batch -----

    async def batch_transition(
        self, keys: list[str], status: str
    ) -> BatchResult:
        tid = self._resolve_transition_id(status)
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for key in keys:
            try:
                result = await self._bridge.call(
                    "jira_transition_issue",
                    {"issue_key": key, "transition_id": tid},
                )
                succeeded.append(self._parse_issue_ref(result))
            except (McpBridgeError, Exception) as exc:
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ----- Relationships -----

    async def link_to_parent(
        self, child_key: str, parent_key: str
    ) -> None:
        """Link child to parent via jira_update_issue (AR-S3-2)."""
        await self._bridge.call(
            "jira_update_issue",
            {
                "issue_key": child_key,
                "additional_fields": json.dumps({"parent": parent_key}),
            },
        )

    async def link_issues(
        self, source: str, target: str, link_type: str
    ) -> None:
        await self._bridge.call(
            "jira_create_issue_link",
            {
                "inward_issue_key": source,
                "outward_issue_key": target,
                "link_type": link_type,
            },
        )

    # ----- Comments -----

    async def add_comment(self, key: str, body: str) -> CommentRef:
        result = await self._bridge.call(
            "jira_add_comment",
            {"issue_key": key, "body": body},
        )
        comment_id = result.data.get("id", "")
        url = result.data.get("self", "")
        return CommentRef(id=str(comment_id), url=str(url))

    async def get_comments(
        self, key: str, limit: int = 10
    ) -> list[Comment]:
        """Get comments via jira_get_issue with comment_limit (AR-S3-5)."""
        result = await self._bridge.call(
            "jira_get_issue",
            {"issue_key": key, "comment_limit": limit},
        )
        return self._parse_comments(result)

    # ----- Query -----

    async def search(
        self, query: str, limit: int = 50
    ) -> list[IssueSummary]:
        result = await self._bridge.call(
            "jira_search",
            {"jql": query, "limit": limit},
        )
        return self._parse_search_results(result)

    # ----- Health -----

    async def health(self) -> AdapterHealth:
        start = time.monotonic()
        try:
            await self._bridge.call(
                "jira_search",
                {"jql": "project is not EMPTY", "limit": 1},
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira",
                healthy=True,
                message="OK",
                latency_ms=elapsed_ms,
            )
        except (McpBridgeError, Exception) as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira",
                healthy=False,
                message=str(exc),
                latency_ms=elapsed_ms,
            )

    # ----- Response parsers -----

    @staticmethod
    def _parse_issue_ref(result: McpToolResult) -> IssueRef:
        """Parse McpToolResult into IssueRef."""
        key = result.data.get("key", "")
        url = result.data.get("self", "")
        return IssueRef(key=key, url=str(url))

    @staticmethod
    def _parse_issue_detail(result: McpToolResult) -> IssueDetail:
        """Parse McpToolResult into IssueDetail."""
        data = result.data
        fields = data.get("fields", {})
        parent = fields.get("parent")
        assignee = fields.get("assignee")
        priority = fields.get("priority")

        return IssueDetail(
            key=data.get("key", ""),
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            status=fields.get("status", {}).get("name", ""),
            issue_type=fields.get("issuetype", {}).get("name", ""),
            parent_key=parent.get("key") if parent else None,
            labels=fields.get("labels", []),
            assignee=assignee.get("displayName") if assignee else None,
            priority=priority.get("name") if priority else None,
            created=fields.get("created", ""),
            updated=fields.get("updated", ""),
        )

    @staticmethod
    def _parse_comments(result: McpToolResult) -> list[Comment]:
        """Parse comments from jira_get_issue response."""
        fields = result.data.get("fields", {})
        comment_data = fields.get("comment", {})
        comments_list = comment_data.get("comments", [])

        return [
            Comment(
                id=str(c.get("id", "")),
                body=c.get("body", ""),
                author=c.get("author", {}).get("displayName", ""),
                created=c.get("created", ""),
            )
            for c in comments_list
        ]

    @staticmethod
    def _parse_search_results(result: McpToolResult) -> list[IssueSummary]:
        """Parse search results into IssueSummary list."""
        issues = result.data.get("issues", [])
        return [
            IssueSummary(
                key=issue.get("key", ""),
                summary=issue.get("fields", {}).get("summary", ""),
                status=issue.get("fields", {}).get("status", {}).get("name", ""),
                issue_type=issue.get("fields", {}).get("issuetype", {}).get("name", ""),
                parent_key=(
                    issue.get("fields", {}).get("parent", {}).get("key")
                    if issue.get("fields", {}).get("parent")
                    else None
                ),
            )
            for issue in issues
        ]
