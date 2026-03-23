"""Jira adapter via ACLI subprocess.

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to ``acli jira`` commands via ``AcliJiraBridge``.

Configuration: reads ``.raise/jira.yaml`` for project config.
Status resolution: by convention (``replace("-", " ").title()``), not config lookup.
``status_mapping`` in jira.yaml is MCP legacy — not used by this adapter.

Architecture: E494 design (D1-D4), S494.3
"""

from __future__ import annotations

import logging
import re
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

from .acli_bridge import AcliJiraBridge

logger = logging.getLogger(__name__)

# Module-level config path as test seam (PAT-E-589)
_JIRA_YAML_PATH = Path(".raise") / "jira.yaml"


_JQL_OPERATORS = re.compile(
    r"\b(AND|OR|NOT|IN|IS|ORDER BY)\b|[=!<>~]",
    re.IGNORECASE,
)
_ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")
_UNQUOTED_PROJECT = re.compile(r"(project\s*=\s*)(?![\"'])(\w+)", re.IGNORECASE)


def _quote_project_values(jql: str) -> str:
    """Quote unquoted project values to avoid JQL reserved word errors."""
    return _UNQUOTED_PROJECT.sub(r'\1"\2"', jql)


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

    def _walk(node: dict[str, object]) -> None:
        node_type = node.get("type", "")
        content = node.get("content") or []
        if node_type == "text":
            parts.append(str(node.get("text", "")))
            return
        if node_type == "listItem":
            parts.append("- ")
        for child in content:
            if isinstance(child, dict):
                _walk(child)
        if node_type in ("paragraph", "heading", "blockquote", "codeBlock", "listItem"):
            parts.append("\n")

    _walk(value)
    return "".join(parts).strip()


def to_jql(query: str) -> str:
    r"""Normalize a user query to valid JQL.

    Rules (RAISE-552):
    - ``PROJECT-NNN`` issue key → ``issue = PROJECT-NNN``
    - Query already containing JQL operators → pass through with project quoting
    - Plain text → ``text ~ "query"``
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

    Examples: "in-progress" → "In Progress", "done" → "Done".
    """
    return status.replace("-", " ").title()


class AcliJiraAdapter:
    """Jira adapter that delegates to ACLI via AcliJiraBridge.

    Implements ``AsyncProjectManagementAdapter`` protocol (structural typing).

    Args:
        project_root: Project root containing ``.raise/jira.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        config = self._load_config(root)
        self._instances: dict[str, dict[str, Any]] = self._require(
            config, "instances", "jira.yaml missing required 'instances' section"
        )
        default_name: str = self._require(
            config, "default_instance", "jira.yaml missing required 'default_instance'"
        )
        if default_name not in self._instances:
            msg = (
                f"default_instance '{default_name}' not found in instances "
                f"(available: {', '.join(self._instances)})"
            )
            raise ValueError(msg)
        self._default_site: str = self._instances[default_name]["site"]
        self._projects: dict[str, dict[str, Any]] = config.get("projects", {})
        self._validate_projects()
        self._bridge = AcliJiraBridge()

    @staticmethod
    def _require(config: dict[str, Any], key: str, msg: str) -> Any:
        """Return config[key] or raise ValueError."""
        value = config.get(key)
        if not value:
            raise ValueError(msg)
        return value

    def _validate_projects(self) -> None:
        """Validate project→instance mapping and cross-check instance.projects."""
        for project_key, project in self._projects.items():
            instance_name = project.get("instance")
            if not instance_name:
                msg = f"Project '{project_key}' missing required 'instance' field"
                raise ValueError(msg)
            instance = self._instances.get(instance_name, {})
            instance_projects: list[str] = instance.get("projects", [])
            if project_key not in instance_projects:
                logger.warning(
                    "Project %s declares instance '%s' but is not in "
                    "instances.%s.projects",
                    project_key,
                    instance_name,
                    instance_name,
                )

    @staticmethod
    def _load_config(root: Path) -> dict[str, Any]:
        """Read and parse .raise/jira.yaml."""
        config_path = root / _JIRA_YAML_PATH
        if not config_path.exists():
            msg = f"Jira config not found: {config_path}"
            raise FileNotFoundError(msg)
        with open(config_path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return data

    def build_url(self, key: str) -> str:
        """Construct web browse URL from project instance site + issue key.

        Returns empty string if project is unknown (no instance configured).
        """
        project_key = key.split("-")[0] if "-" in key else ""
        project = self._projects.get(project_key, {})
        instance_name = project.get("instance", "")
        if not instance_name:
            return ""
        instance = self._instances.get(instance_name, {})
        site = instance.get("site", "")
        if not site:
            return ""
        return f"https://{site}/browse/{key}"

    # ----- Site resolution -----

    _PROJECT_IN_JQL = re.compile(r"project\s*=\s*[\"']?(\w+)[\"']?")

    def _resolve_site(self, project_key: str) -> str:
        """Resolve project key → instance → site. Default on unknown."""
        project = self._projects.get(project_key)
        if not project:
            logger.warning("Unknown project '%s', using default instance", project_key)
            return self._default_site
        instance_name = project.get("instance", "")
        instance = self._instances.get(instance_name, {})
        return instance.get("site", self._default_site)

    def _resolve_site_from_key(self, issue_key: str) -> str:
        """Extract project key from issue key and resolve site."""
        if "-" not in issue_key:
            return self._default_site
        project_key = issue_key.split("-")[0]
        return self._resolve_site(project_key)

    def _resolve_site_from_jql(self, jql: str) -> str:
        """Extract project from JQL query and resolve site. Default on miss."""
        match = self._PROJECT_IN_JQL.search(jql)
        if match:
            return self._resolve_site(match.group(1))
        return self._default_site

    # ----- Response parsers -----

    @staticmethod
    def _extract_issue_fields(data: dict[str, Any]) -> dict[str, Any]:
        """Extract common fields from nested Jira API format.

        ACLI always returns nested format (``fields.summary``, ``fields.status.name``).
        No ``is_flat`` parameter — D1 from architecture review.
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
        """Parse single nested issue → IssueDetail."""
        common = self._extract_issue_fields(data)
        fields: dict[str, Any] = data.get("fields") or {}
        assignee: dict[str, Any] | None = fields.get("assignee")
        priority: dict[str, Any] | None = fields.get("priority")

        return IssueDetail(
            **common,
            url=self.build_url(common["key"]),
            description=_adf_to_text(fields.get("description", "")),
            labels=fields.get("labels", []),
            assignee=assignee.get("displayName") if assignee else None,
            priority=priority.get("name") if priority else None,
            created=fields.get("created", ""),
            updated=fields.get("updated", ""),
        )

    def _parse_result_envelope(self, data: dict[str, Any]) -> IssueRef:
        """Parse ACLI result envelope into IssueRef.

        Envelope format: ``{results: [{status, message, id}], totalCount, successCount}``
        The ``id`` field contains the issue key (e.g. "RAISE-99").
        """
        results = data.get("results", [])
        key = results[0]["id"] if results else ""
        return IssueRef(key=key, url=self.build_url(key))

    # ----- CRUD -----

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create a Jira issue via ``acli jira workitem create``."""
        site = self._resolve_site(project_key)
        flags: dict[str, str] = {
            "--project": project_key,
            "--summary": issue.summary,
            "--type": issue.issue_type,
        }
        if issue.description:
            flags["--description"] = issue.description
        if issue.labels:
            flags["--label"] = ",".join(issue.labels)

        result = await self._bridge.call(["workitem", "create"], flags, site=site)
        # ACLI create returns the full issue ({key, fields}), not an envelope
        key = result.get("key", "")
        return IssueRef(key=key, url=self.build_url(key))

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update issue fields via ``acli jira workitem edit``."""
        site = self._resolve_site_from_key(key)
        flags: dict[str, str] = {"--key": key}
        for field, value in fields.items():
            flags[f"--{field}"] = str(value)

        result = await self._bridge.call(["workitem", "edit"], flags, site=site)
        return self._parse_result_envelope(result)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition issue status via ``acli jira workitem transition``."""
        site = self._resolve_site_from_key(key)
        jira_status = normalize_status(status)
        flags = {"--key": key, "--status": jira_status}

        result = await self._bridge.call(["workitem", "transition"], flags, site=site)
        return self._parse_result_envelope(result)

    async def get_issue(self, key: str) -> IssueDetail:
        """Get full issue detail via ``acli jira workitem view``."""
        site = self._resolve_site_from_key(key)
        result = await self._bridge.call(
            ["workitem", "view", key], {"--fields": "*all"}, site=site
        )
        return self._parse_issue_detail(result)

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search issues via ``acli jira workitem search``.

        ACLI returns a top-level array, not ``{issues: [...]}``.
        """
        jql = to_jql(query)
        site = self._resolve_site_from_jql(jql)
        result = await self._bridge.call(
            ["workitem", "search"],
            {"--jql": jql, "--limit": str(limit)},
            site=site,
        )
        issues = (
            cast("list[dict[str, Any]]", result) if isinstance(result, list) else []
        )
        return [IssueSummary(**self._extract_issue_fields(i)) for i in issues]

    # ----- Batch -----

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition multiple issues, isolating failures per key."""
        jira_status = normalize_status(status)
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for key in keys:
            site = self._resolve_site_from_key(key)
            try:
                result = await self._bridge.call(
                    ["workitem", "transition"],
                    {"--key": key, "--status": jira_status},
                    site=site,
                )
                succeeded.append(self._parse_result_envelope(result))
            except Exception as exc:
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ----- Relationships -----

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        """Set parent via ``acli jira workitem edit``."""
        site = self._resolve_site_from_key(child_key)
        await self._bridge.call(
            ["workitem", "edit"],
            {"--key": child_key, "--parent": parent_key},
            site=site,
        )

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        """Create link via ``acli jira workitem link create``."""
        site = self._resolve_site_from_key(source)
        await self._bridge.call(
            ["workitem", "link", "create"],
            {"--out": source, "--in": target, "--type": link_type},
            site=site,
            json_output=False,
        )

    # ----- Comments -----

    async def add_comment(self, key: str, body: str) -> CommentRef:
        """Add comment via ``acli jira workitem comment create``."""
        site = self._resolve_site_from_key(key)
        result = await self._bridge.call(
            ["workitem", "comment", "create"],
            {"--key": key, "--body": body},
            site=site,
        )
        envelope = self._parse_result_envelope(result)
        return CommentRef(id=envelope.key, url="")

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        """Get comments via ``acli jira workitem comment list``.

        ACLI comment format: ``{comments: [{id, author, body}]}``.
        ``created`` is missing — set to empty string (D3).
        """
        site = self._resolve_site_from_key(key)
        result = await self._bridge.call(
            ["workitem", "comment", "list"],
            {"--key": key, "--limit": str(limit)},
            site=site,
        )
        comments_data: list[dict[str, Any]] = result.get("comments", [])
        return [
            Comment(
                id=str(c.get("id", "")),
                body=c.get("body", ""),
                author=c.get("author", ""),
                created="",
            )
            for c in comments_data
        ]

    # ----- Health -----

    async def health(self) -> AdapterHealth:
        """Delegate health check to AcliJiraBridge."""
        return await self._bridge.health(site=self._default_site)
