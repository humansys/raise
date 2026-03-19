"""Jira adapter via MCP bridge (mcp-atlassian server).

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to the corresponding ``mcp-atlassian`` tool call via ``McpBridge``.

Configuration: reads ``.raise/jira.yaml`` for status_mapping and project config.
Connection: lazy — no MCP server connection until first method call.

Architecture: S301.3 design, AR-S3-2, AR-S3-5
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, cast

import yaml

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
from raise_cli.mcp.bridge import McpBridge, McpBridgeError, McpToolResult


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

        workflow = config.get("workflow", {})
        status_mapping = workflow.get("status_mapping")
        if not status_mapping:
            msg = (
                "Missing 'status_mapping' in .raise/jira.yaml. "
                "Add a status_mapping section with status names and transition IDs."
            )
            raise ValueError(msg)

        self._status_mapping: dict[str, int] = status_mapping
        self._bridge = self._create_bridge()

    @staticmethod
    def _create_bridge() -> McpBridge:
        """Create McpBridge with server args from environment variables.

        Reads JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN (or JIRA_TOKEN)
        from environment and passes them as CLI args to mcp-atlassian.
        """
        server_args: list[str] = ["mcp-atlassian"]
        jira_url = os.environ.get("JIRA_URL")
        if jira_url:
            server_args.extend(["--jira-url", jira_url])
        jira_username = os.environ.get("JIRA_USERNAME")
        if jira_username:
            server_args.extend(["--jira-username", jira_username])
        jira_token = os.environ.get("JIRA_API_TOKEN") or os.environ.get("JIRA_TOKEN")
        if jira_token:
            server_args.extend(["--jira-token", jira_token])
        return McpBridge(server_command="uvx", server_args=server_args)

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
        tid = self._status_mapping.get(status.lower())
        if tid is None:
            available = ", ".join(sorted(self._status_mapping.keys()))
            msg = f"Unknown status '{status}'. Available: {available}"
            raise ValueError(msg)
        return str(tid)

    # ----- CRUD -----

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
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
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return self._parse_issue_ref(result)

    async def get_issue(self, key: str) -> IssueDetail:
        result = await self._bridge.call(
            "jira_get_issue", {"issue_key": key, "fields": "*all"}
        )
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return self._parse_issue_detail(result)

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        result = await self._bridge.call(
            "jira_update_issue",
            {"issue_key": key, "fields": json.dumps(fields)},
        )
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return self._parse_issue_ref(result)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        tid = self._resolve_transition_id(status)
        result = await self._bridge.call(
            "jira_transition_issue",
            {"issue_key": key, "transition_id": tid},
        )
        if result.is_error:
            raise McpBridgeError(result.error_message)
        ref = self._parse_issue_ref(result)
        # MCP transition tool returns no data — use the key we already have
        if not ref.key:
            ref = IssueRef(key=key, url=ref.url)
        return ref

    # ----- Batch -----

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        tid = self._resolve_transition_id(status)
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for key in keys:
            try:
                result = await self._bridge.call(
                    "jira_transition_issue",
                    {"issue_key": key, "transition_id": tid},
                )
                ref = self._parse_issue_ref(result)
                if not ref.key:
                    ref = IssueRef(key=key, url=ref.url)
                succeeded.append(ref)
            except Exception as exc:
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ----- Relationships -----

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """Link child to parent via jira_update_issue (AR-S3-2)."""
        await self._bridge.call(
            "jira_update_issue",
            {
                "issue_key": child_key,
                "additional_fields": json.dumps({"parent": parent_key}),
            },
        )

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
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
        if result.is_error:
            raise McpBridgeError(result.error_message)
        comment_id = result.data.get("id", "")
        url = result.data.get("self", "")
        return CommentRef(id=str(comment_id), url=str(url))

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """Get comments via jira_get_issue with comment_limit (AR-S3-5)."""
        result = await self._bridge.call(
            "jira_get_issue",
            {"issue_key": key, "comment_limit": limit},
        )
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return self._parse_comments(result)

    # ----- Query -----

    @staticmethod
    def _to_jql(query: str) -> str:
        """Normalize a user query to valid JQL.

        Rules (RAISE-552):
        - ``PROJECT-NNN`` issue key → ``issue = PROJECT-NNN``
        - Query already containing JQL operators → pass through unchanged
        - Plain text → ``text ~ "query"``
        """
        _JQL_OPERATORS = re.compile(
            r"\b(AND|OR|NOT|IN|IS|ORDER BY)\b|[=!<>~]",
            re.IGNORECASE,
        )
        _ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")

        if _ISSUE_KEY.match(query):
            return f"issue = {query}"
        if _JQL_OPERATORS.search(query):
            return query
        return f'text ~ "{query}"'

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        # Sanitize shell-escaped operators (Claude Code Bash escapes ! to \!)
        clean_query = self._to_jql(query.replace("\\!", "!"))
        result = await self._bridge.call(
            "jira_search",
            {"jql": clean_query, "limit": limit},
        )
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return self._parse_search_results(result)

    # ----- Lifecycle -----

    async def aclose(self) -> None:
        """Close the underlying MCP bridge — prevents asyncgen finalizer tracebacks."""
        await self._bridge.aclose()

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
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira",
                healthy=False,
                message=str(exc),
                latency_ms=elapsed_ms,
            )

    # ----- Response parsers -----

    @staticmethod
    def _extract_type_name(raw: Any) -> str:
        """Extract issue type name from raw response field."""
        if isinstance(raw, dict):
            name: str = str(raw.get("name", ""))  # type: ignore[union-attr]
            return name
        return str(raw) if raw else ""

    @staticmethod
    def _extract_issue_fields(data: dict[str, Any], *, is_flat: bool) -> dict[str, Any]:
        """Extract common issue fields from flat (sooperset) or nested (raw Jira) format.

        Shared by ``_parse_issue_detail`` and ``_parse_search_results`` to avoid
        duplicating the flat/nested branching logic.

        Args:
            data: Raw issue data dict (single issue, not the search wrapper).
            is_flat: True for sooperset format (top-level fields),
                False for raw Jira API format (nested under ``fields``).

        Returns:
            Dict with normalized keys: key, summary, status, issue_type, parent_key.
        """
        if is_flat:
            parent = data.get("parent")
            return {
                "key": data.get("key", ""),
                "summary": data.get("summary", ""),
                "status": data.get("status", {}).get("name", ""),
                "issue_type": McpJiraAdapter._extract_type_name(data.get("issue_type")),
                "parent_key": parent.get("key") if parent else None,
            }

        fields = data.get("fields", {})
        parent = fields.get("parent")
        return {
            "key": data.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "parent_key": parent.get("key") if parent else None,
        }

    @staticmethod
    def _parse_issue_ref(result: McpToolResult) -> IssueRef:
        """Parse McpToolResult into IssueRef.

        Handles both flat format (key at top level) and wrapped format
        (key nested under ``issue`` — used by create_issue, update_issue).
        """
        data = result.data
        # Wrapped format: {"message": "...", "issue": {"key": "..."}}
        if "issue" in data and isinstance(data["issue"], dict):
            data = cast("dict[str, Any]", data["issue"])
        key = data.get("key", "")
        url = data.get("url", data.get("self", ""))
        return IssueRef(key=key, url=str(url))

    @staticmethod
    def _parse_issue_detail(result: McpToolResult) -> IssueDetail:
        """Parse McpToolResult into IssueDetail.

        Supports both sooperset mcp-atlassian format (top-level fields,
        ``issue_type``, ``display_name``) and raw Jira API format
        (nested ``fields``, ``issuetype``, ``displayName``).
        """
        data = result.data
        is_flat = "summary" in data and "fields" not in data
        common = McpJiraAdapter._extract_issue_fields(data, is_flat=is_flat)

        # Detail-specific fields differ by format
        if is_flat:
            src = data
            assignee = data.get("assignee")
            assignee_name = (
                str(assignee.get("display_name", assignee.get("displayName", "")))
                if assignee
                else None
            )
        else:
            src = data.get("fields", {})
            assignee = src.get("assignee")
            assignee_name = assignee.get("displayName") if assignee else None

        priority = src.get("priority")
        return IssueDetail(
            **common,
            url=data.get("url", ""),
            description=src.get("description", ""),
            labels=src.get("labels", []),
            assignee=assignee_name,
            priority=priority.get("name") if priority else None,
            created=src.get("created", ""),
            updated=src.get("updated", ""),
        )

    @staticmethod
    def _parse_comments(result: McpToolResult) -> list[Comment]:
        """Parse comments from jira_get_issue response.

        Sooperset: ``data.comments`` list.
        Raw Jira: ``data.fields.comment.comments`` list.
        """
        data = result.data
        # Sooperset format: top-level comments list
        comments_list = data.get("comments", [])
        if not comments_list:
            # Raw Jira API format
            fields = data.get("fields", {})
            comment_data = fields.get("comment", {})
            comments_list = comment_data.get("comments", [])

        return [
            Comment(
                id=str(c.get("id", "")),
                body=c.get("body", ""),
                author=c.get("author", {}).get(
                    "display_name", c.get("author", {}).get("displayName", "")
                ),
                created=c.get("created", ""),
            )
            for c in comments_list
        ]

    @staticmethod
    def _parse_search_results(result: McpToolResult) -> list[IssueSummary]:
        """Parse search results into IssueSummary list.

        Sooperset: issues have top-level fields (``summary``, ``status.name``).
        Raw Jira: issues have nested ``fields`` dict.
        """
        issues = result.data.get("issues", [])
        summaries: list[IssueSummary] = []
        for issue in issues:
            is_flat = "summary" in issue and "fields" not in issue
            common = McpJiraAdapter._extract_issue_fields(issue, is_flat=is_flat)
            summaries.append(IssueSummary(**common))
        return summaries
