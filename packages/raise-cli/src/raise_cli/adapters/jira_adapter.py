"""Jira adapter via atlassian-python-api.

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to ``JiraClient`` operations with response parsing to Pydantic boundary models.

Configuration: reads ``.raise/jira.yaml`` via ``load_jira_config``.
Status resolution: convention (``normalize_status``) + live transition lookup.

Architecture: E1052 design (S1052.3)
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any, cast

from raise_cli.adapters.jira_client import JiraClient
from raise_cli.adapters.jira_config import JiraConfig, load_jira_config
from raise_cli.adapters.jira_exceptions import JiraApiError
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

logger = logging.getLogger(__name__)

# ── JQL normalization (ported from acli_jira.py) ────────────────────

_JQL_OPERATORS = re.compile(
    r"\b(AND|OR|NOT|IN|IS|ORDER BY)\b|[=!<>~]",
    re.IGNORECASE,
)
_ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")
_UNQUOTED_PROJECT = re.compile(r"(project\s*=\s*)(?![\"'])(\w+)", re.IGNORECASE)


def _quote_project_values(jql: str) -> str:
    """Quote unquoted project values to avoid JQL reserved word errors."""
    return _UNQUOTED_PROJECT.sub(r'\1"\2"', jql)


def to_jql(query: str) -> str:
    r"""Normalize a user query to valid JQL.

    Rules (RAISE-552):
    - ``PROJECT-NNN`` issue key -> ``issue = PROJECT-NNN``
    - Query already containing JQL operators -> pass through with project quoting
    - Plain text -> ``text ~ "query"``
    - Escaped operators (``\!``) are unescaped before processing
    """
    clean = query.replace("\\!", "!")
    if _ISSUE_KEY.match(clean):
        return f"issue = {clean}"
    if _JQL_OPERATORS.search(clean):
        return _quote_project_values(clean)
    return f'text ~ "{clean}"'


def normalize_status(status: str) -> str:
    """Convert CLI slug to Jira status name by convention.

    Examples: "in-progress" -> "In Progress", "done" -> "Done".
    """
    return status.replace("-", " ").title()


# ── ADF conversion (ported from acli_jira.py) ───────────────────────


def _adf_to_text(value: object) -> str:
    """Convert an ADF (Atlassian Document Format) dict to plain text.

    Passes plain strings through unchanged. Returns empty string for None/falsy.
    Handles: paragraph, heading, text, bulletList, orderedList, listItem,
    codeBlock, blockquote.
    """
    if not value:
        return ""
    if not isinstance(value, dict):
        return str(value)

    parts: list[str] = []

    def _walk(node: dict[str, Any]) -> None:
        node_type = node.get("type", "")
        raw_content: Any = node.get("content")
        content: list[Any] = cast("list[Any]", raw_content) if isinstance(raw_content, list) else []
        if node_type == "text":
            parts.append(str(node.get("text", "")))
            return
        if node_type == "listItem":
            parts.append("- ")
        for child in content:
            _walk(child)
        if node_type in ("paragraph", "heading", "blockquote", "codeBlock", "listItem"):
            parts.append("\n")

    _walk(cast("dict[str, Any]", value))
    return "".join(parts).strip()


# ── Adapter ─────────────────────────────────────────────────────────


class PythonApiJiraAdapter:
    """Jira adapter via atlassian-python-api.

    Implements ``AsyncProjectManagementAdapter`` protocol (structural typing).
    Delegates to ``JiraClient`` for all Jira REST API operations.

    Args:
        project_root: Project root containing ``.raise/jira.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        self._config: JiraConfig = load_jira_config(root)
        self._clients: dict[str, JiraClient] = {}

    # ── Client resolution ───────────────────────────────────────────

    def _client_for(self, project_key: str) -> JiraClient:
        """Lazy client resolution: project_key -> instance -> cached client.

        Cache key is the instance site (unique per Jira instance).
        Falls back to default instance for unknown projects.
        """
        instance = self._config.resolve_instance(project_key)
        cache_key = instance.site
        if cache_key not in self._clients:
            # Find instance name for from_config
            instance_name: str | None = None
            for name, inst in self._config.instances.items():
                if inst.site == instance.site:
                    instance_name = name
                    break
            self._clients[cache_key] = JiraClient.from_config(
                self._config, instance=instance_name
            )
        return self._clients[cache_key]

    def _project_key_from_issue(self, issue_key: str) -> str:
        """Extract project key from issue key (e.g., RAISE-123 -> RAISE)."""
        return issue_key.split("-")[0] if "-" in issue_key else issue_key

    # ── URL builder ─────────────────────────────────────────────────

    def _build_url(self, key: str) -> str:
        """Construct web browse URL from config instance site + issue key."""
        project_key = self._project_key_from_issue(key)
        instance = self._config.resolve_instance(project_key)
        return f"https://{instance.site}/browse/{key}"

    # ── Response parsers ────────────────────────────────────────────

    @staticmethod
    def _extract_issue_fields(data: dict[str, Any]) -> dict[str, Any]:
        """Extract common fields from nested Jira API format.

        Format: ``fields.summary``, ``fields.status.name``, etc.
        """
        fields: dict[str, Any] = data.get("fields") or {}
        parent: dict[str, Any] | None = fields.get("parent")
        return {
            "key": data.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "parent_key": parent.get("key") if parent else None,
        }

    def _parse_issue_detail(self, data: dict[str, Any]) -> IssueDetail:
        """Parse single nested issue -> IssueDetail."""
        common = self._extract_issue_fields(data)
        fields: dict[str, Any] = data.get("fields") or {}
        assignee: dict[str, Any] | None = fields.get("assignee")
        priority: dict[str, Any] | None = fields.get("priority")

        return IssueDetail(
            **common,
            url=self._build_url(common["key"]),
            description=_adf_to_text(fields.get("description", "")),
            labels=fields.get("labels", []),
            assignee=assignee.get("displayName") if assignee else None,
            priority=priority.get("name") if priority else None,
            created=fields.get("created", ""),
            updated=fields.get("updated", ""),
        )

    # ── CRUD ────────────────────────────────────────────────────────

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a Jira issue via REST API."""
        client = self._client_for(project_key)
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": issue.summary,
            "issuetype": {"name": issue.issue_type},
        }
        if issue.description:
            fields["description"] = issue.description
        if issue.labels:
            fields["labels"] = issue.labels
        if issue.metadata.get("parent"):
            fields["parent"] = {"key": issue.metadata["parent"]}

        result = client.create_issue(fields)
        key = result.get("key", "")
        return IssueRef(key=key, url=self._build_url(key))

    async def get_issue(self, key: str) -> IssueDetail:
        """Get full issue detail via REST API."""
        client = self._client_for(self._project_key_from_issue(key))
        result = client.get_issue(key)
        return self._parse_issue_detail(result)

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update issue fields via REST API."""
        client = self._client_for(self._project_key_from_issue(key))
        normalized = dict(fields)
        assignee = normalized.get("assignee")
        if isinstance(assignee, str):
            users = client.search_users(assignee)
            if not users:
                raise JiraApiError(f"No Jira user found for '{assignee}'")
            normalized["assignee"] = {"accountId": users[0]["accountId"]}
        client.update_issue(key, normalized)
        return IssueRef(key=key, url=self._build_url(key))

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition issue status via live transition lookup.

        Receives a CLI slug (e.g., "in-progress"), normalizes to Jira
        display name ("In Progress"), queries available transitions,
        matches by name (case-insensitive), then executes.
        """
        client = self._client_for(self._project_key_from_issue(key))
        jira_status = normalize_status(status)
        transitions = client.get_transitions(key)

        match = next(
            (t for t in transitions if t["name"].lower() == jira_status.lower()),
            None,
        )
        if not match:
            available = [t["name"] for t in transitions]
            raise JiraApiError(
                f"No transition to '{jira_status}' for {key}. "
                f"Available: {available}"
            )

        client.transition_issue(key, match["id"])
        return IssueRef(key=key, url=self._build_url(key))

    # ── Batch ───────────────────────────────────────────────────────

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple issues, isolating failures per key."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for key in keys:
            try:
                ref = await self.transition_issue(key, status)
                succeeded.append(ref)
            except Exception as exc:
                logger.warning("batch_transition failed for %s: %s", key, exc)
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ── Search ──────────────────────────────────────────────────────

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search issues via JQL with query normalization."""
        jql = to_jql(query)
        # Resolve client from JQL or use default
        project_key = self._extract_project_from_jql(jql)
        client = self._client_for(project_key)
        issues = client.jql(jql, limit=limit)
        return [IssueSummary(**self._extract_issue_fields(i)) for i in issues]

    _PROJECT_IN_JQL = re.compile(r"project\s*=\s*[\"']?(\w+)[\"']?")

    def _extract_project_from_jql(self, jql: str) -> str:
        """Extract project key from JQL for client routing. Default on miss."""
        match = self._PROJECT_IN_JQL.search(jql)
        if match:
            return match.group(1)
        # Try to extract from issue key pattern
        issue_match = re.search(r"issue\s*=\s*([A-Z][A-Z0-9_]+)-\d+", jql)
        if issue_match:
            return issue_match.group(1)
        return self._config.default_instance

    # ── Relationships ───────────────────────────────────────────────

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """Set parent via update_issue with parent field."""
        client = self._client_for(self._project_key_from_issue(child_key))
        client.set_parent(child_key, parent_key)

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        """Create issue link between two issues."""
        client = self._client_for(self._project_key_from_issue(source))
        client.create_link(source, target, link_type)

    # ── Comments ────────────────────────────────────────────────────

    async def add_comment(self, key: str, body: str) -> CommentRef:
        """Add comment to an issue."""
        client = self._client_for(self._project_key_from_issue(key))
        result = client.add_comment(key, body)
        comment_id = str(result.get("id", ""))
        return CommentRef(id=comment_id, url="")

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """Get comments on an issue.

        Jira comment format: ``{id, body, author: {displayName}, created}``.
        Body may be ADF dict or plain string.
        """
        client = self._client_for(self._project_key_from_issue(key))
        comments_data = client.get_comments(key, limit=limit)
        return [
            Comment(
                id=str(c.get("id", "")),
                body=_adf_to_text(c.get("body", "")),
                author=c.get("author", {}).get("displayName", ""),
                created=c.get("created", ""),
            )
            for c in comments_data
        ]

    # ── Health ──────────────────────────────────────────────────────

    async def health(self) -> AdapterHealth:
        """Check Jira connectivity via server_info."""
        try:
            # Use default instance for health check
            client = self._client_for(self._config.default_instance)
            start = time.monotonic()
            client.server_info()
            latency = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira",
                healthy=True,
                message="OK",
                latency_ms=latency,
            )
        except Exception as exc:
            logger.warning("Jira health check failed: %s", exc)
            return AdapterHealth(
                name="jira",
                healthy=False,
                message=str(exc),
            )
