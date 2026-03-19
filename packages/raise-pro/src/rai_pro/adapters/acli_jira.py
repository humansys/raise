"""Jira adapter via ACLI subprocess.

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to ``acli jira`` commands via ``AcliJiraBridge``.

Configuration: reads ``.raise/jira.yaml`` for project config.
Status resolution: by convention (``replace("-", " ").title()``), not config lookup.
``status_mapping`` in jira.yaml is MCP legacy — not used by this adapter.

Architecture: E494 design (D1-D4), S494.3
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    FailureDetail,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)

from .acli_bridge import AcliJiraBridge

# Module-level config path as test seam (PAT-E-589)
_JIRA_YAML_PATH = Path(".raise") / "jira.yaml"


_JQL_OPERATORS = re.compile(
    r"\b(AND|OR|NOT|IN|IS|ORDER BY)\b|[=!<>~]",
    re.IGNORECASE,
)
_ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")


def to_jql(query: str) -> str:
    r"""Normalize a user query to valid JQL.

    Rules (RAISE-552):
    - ``PROJECT-NNN`` issue key → ``issue = PROJECT-NNN``
    - Query already containing JQL operators → pass through unchanged
    - Plain text → ``text ~ "query"``
    - Escaped operators (``\!``) are unescaped before processing
    """
    clean = query.replace("\\!", "!")
    if _ISSUE_KEY.match(clean):
        return f"issue = {clean}"
    if _JQL_OPERATORS.search(clean):
        return clean
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
        self._projects: dict[str, dict[str, Any]] = config.get("projects", {})
        self._bridge = AcliJiraBridge()

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
        """Construct web browse URL from project site + issue key.

        Returns empty string if project is unknown (no site configured).
        """
        project_key = key.split("-")[0] if "-" in key else ""
        project = self._projects.get(project_key, {})
        site = project.get("site", "")
        if not site:
            return ""
        return f"https://{site}/browse/{key}"

    # ----- Response parsers -----

    @staticmethod
    def _extract_issue_fields(data: dict[str, Any]) -> dict[str, Any]:
        """Extract common fields from nested Jira API format.

        ACLI always returns nested format (``fields.summary``, ``fields.status.name``).
        No ``is_flat`` parameter — D1 from architecture review.
        """
        fields = data.get("fields", {})
        parent = fields.get("parent")
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
        fields = data.get("fields", {})
        assignee = fields.get("assignee")
        priority = fields.get("priority")

        return IssueDetail(
            **common,
            url=self.build_url(common["key"]),
            description=str(fields.get("description", "")),
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
        flags: dict[str, str] = {
            "--project": project_key,
            "--summary": issue.summary,
            "--type": issue.issue_type,
        }
        if issue.description:
            flags["--description"] = issue.description
        if issue.labels:
            flags["--label"] = ",".join(issue.labels)

        result = await self._bridge.call(["workitem", "create"], flags)
        return self._parse_result_envelope(result)

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update issue fields via ``acli jira workitem edit``."""
        flags: dict[str, str] = {"--key": key}
        for field, value in fields.items():
            flags[f"--{field}"] = str(value)

        result = await self._bridge.call(["workitem", "edit"], flags)
        return self._parse_result_envelope(result)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition issue status via ``acli jira workitem transition``."""
        jira_status = normalize_status(status)
        flags = {"--key": key, "--status": jira_status}

        result = await self._bridge.call(["workitem", "transition"], flags)
        return self._parse_result_envelope(result)

    async def get_issue(self, key: str) -> IssueDetail:
        """Get full issue detail via ``acli jira workitem view``."""
        result = await self._bridge.call(["workitem", "view"], {"--key": key})
        return self._parse_issue_detail(result)

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        """Search issues via ``acli jira workitem search``.

        ACLI returns a top-level array, not ``{issues: [...]}``.
        """
        jql = to_jql(query)
        result = await self._bridge.call(
            ["workitem", "search"],
            {"--jql": jql, "--limit": str(limit)},
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
            try:
                result = await self._bridge.call(
                    ["workitem", "transition"],
                    {"--key": key, "--status": jira_status},
                )
                succeeded.append(self._parse_result_envelope(result))
            except Exception as exc:
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ----- Health -----

    async def health(self) -> AdapterHealth:
        """Delegate health check to AcliJiraBridge."""
        return await self._bridge.health()
