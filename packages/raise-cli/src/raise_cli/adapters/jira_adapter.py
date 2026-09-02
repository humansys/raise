"""Jira adapter via atlassian-python-api.

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to ``JiraClient`` operations with response parsing to Pydantic boundary models.

Configuration: reads ``.raise/backlog.yaml``[jira] via ``load_backlog_config``.
Status resolution: convention (``normalize_status``) + live transition lookup.

Architecture: E1052 design (S1052.3)
"""

from __future__ import annotations

import contextlib
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from raise_cli.adapters.backlog_config import load_backlog_config, save_backlog_config
from raise_cli.adapters.jira_adf import adf_to_markdown, markdown_to_adf
from raise_cli.adapters.jira_client import JiraClient
from raise_cli.adapters.jira_exceptions import JiraApiError
from raise_cli.adapters.models import (
    AdapterHealth,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    FailureDetail,
    FieldDefinition,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    IssueTypeInfo,
    LinkTypeDefinition,
    ProjectVersion,
    WorkflowState,
)
from raise_cli.adapters.models.pm import (
    BacklogAdapterConfig,
    CustomField,
    CustomFieldContext,
    FieldSchema,
    IssueLink,
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


def _normalize_link_type(
    link_type: str, relation_types: list[dict[str, Any]]
) -> tuple[str, bool]:
    """Resolve a link_type label to the canonical Jira TYPE NAME.

    Matches case-insensitively against name, outward, and inward fields.
    If relation_types is empty (not configured), passes link_type through with a warning.
    Raises ValueError if relation_types is configured but no match is found.

    Returns:
        (canonical_name, is_inward): canonical_name is the Jira link type name
        (e.g. "Blocks"); is_inward is True when the input matched the inward
        label (e.g. "is blocked by"), False otherwise.
    """
    if not relation_types:
        logger.warning(
            "relation_types not configured in backlog.yaml — passing link_type '%s' raw. "
            "Run 'rai backlog link-types discover' to populate available types.",
            link_type,
        )
        return link_type, False
    needle = link_type.lower()
    for rt in relation_types:
        if str(rt.get("inward", "")).lower() == needle:
            return str(rt["name"]), True
        if str(rt.get("name", "")).lower() == needle:
            return str(rt["name"]), False
        if str(rt.get("outward", "")).lower() == needle:
            return str(rt["name"]), False
    valid = [str(rt.get("name", "")) for rt in relation_types if rt.get("name")]
    raise ValueError(
        f"Unknown link type: '{link_type}'. Valid types: {valid}. "
        "If types are missing, run 'rai backlog link-types discover' to populate them."
    )


# ── Adapter ─────────────────────────────────────────────────────────


class PythonApiJiraAdapter:
    """Jira adapter via atlassian-python-api.

    Implements ``AsyncProjectManagementAdapter`` protocol (structural typing).
    Delegates to ``JiraClient`` for all Jira REST API operations.

    Args:
        project_root: Project root containing ``.raise/backlog.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        self._project_root: Path | None = root
        self._config: BacklogAdapterConfig = load_backlog_config(root, "jira")
        self._clients: dict[str, JiraClient] = {}
        self._field_schemas: dict[str, str | FieldSchema] = {}
        # RAISE-6248: RAISE_BACKLOG_ORG overrides default_org for multi-org routing.
        # Hermes sets this per-session so each subprocess uses the correct Jira instance.
        if override := os.environ.get("RAISE_BACKLOG_ORG"):
            if override in self._config.organizations:
                self._config = self._config.model_copy(update={"default_org": override})
            else:
                logger.warning(
                    "RAISE_BACKLOG_ORG=%s not in organizations — ignored", override
                )

    # ── Client resolution ───────────────────────────────────────────

    def _client_for_org(self, org_name: str) -> JiraClient:
        """Lazy client resolution: org_name -> cached client.

        Use this when you have an org name (from config.default_org or
        config.projects[key].org), not a project key.
        Cache key is the org URL (unique per Jira instance).
        """
        org = self._config.organizations[org_name]
        cache_key = org.url
        if cache_key not in self._clients:
            self._clients[cache_key] = JiraClient.from_org(org_name, org.url, org.email)
        return self._clients[cache_key]

    def _client_for(self, project_key: str) -> JiraClient:
        """Lazy client resolution: project_key -> org -> cached client.

        Cache key is the org URL (unique per Jira instance).
        Raises UnknownProjectKeyError for unknown project keys.
        Use _client_for_org(config.default_org) for the default org client.
        """
        org = self._config.resolve_org(project_key)
        org_name = self._config.projects[project_key].org
        cache_key = org.url
        if cache_key not in self._clients:
            self._clients[cache_key] = JiraClient.from_org(org_name, org.url, org.email)
        return self._clients[cache_key]

    def client_for(self, project_key: str) -> JiraClient:
        """Return the Jira client for a project key.

        Raises UnknownProjectKeyError if the project key is not registered.
        Pass an org name (e.g. config.default_org) to client_for_org instead.
        """
        return self._client_for(project_key)

    def client_for_org(self, org_name: str) -> JiraClient:
        """Return the Jira client for an org name (e.g. config.default_org).

        Use when you have an org name, not a project key — this does NOT route
        through resolve_org, so it never raises UnknownProjectKeyError.
        """
        return self._client_for_org(org_name)

    def _project_key_from_issue(self, issue_key: str) -> str:
        """Extract project key from issue key (e.g., RAISE-123 -> RAISE)."""
        return issue_key.split("-")[0] if "-" in issue_key else issue_key

    # ── URL builder ─────────────────────────────────────────────────

    def _build_url(self, key: str) -> str:
        """Construct web browse URL from config org url + issue key.

        Raises UnknownProjectKeyError if the project key is not registered.
        """
        project_key = self._project_key_from_issue(key)
        org = self._config.resolve_org(project_key)
        return f"https://{org.url}/browse/{key}"

    # ── Response parsers ────────────────────────────────────────────

    @staticmethod
    def _extract_issue_fields(data: dict[str, Any]) -> dict[str, Any]:
        """Extract common fields from nested Jira API format.

        Format: ``fields.summary``, ``fields.status.name``, etc.
        """
        fields: dict[str, Any] = data.get("fields") or {}
        parent: dict[str, Any] | None = fields.get("parent")
        assignee: dict[str, Any] | None = fields.get("assignee")
        priority: dict[str, Any] | None = fields.get("priority")
        return {
            "key": data.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "parent_key": parent.get("key") if parent else None,
            "assignee": assignee.get("displayName") if assignee else None,
            "priority": priority.get("name") if priority else None,
            "labels": fields.get("labels", []),
            "fix_versions": [
                str(v.get("name", ""))
                for v in fields.get("fixVersions") or []
                if v.get("name")
            ],
            "status_category": str(
                (fields.get("status", {}).get("statusCategory") or {}).get("key", "")
            ),
            "metadata": PythonApiJiraAdapter._extract_custom_fields(fields),
        }

    def _parse_issue_detail(self, data: dict[str, Any]) -> IssueDetail:
        """Parse single nested issue -> IssueDetail."""
        common = self._extract_issue_fields(data)
        fields: dict[str, Any] = data.get("fields") or {}
        comment_field: dict[str, Any] = fields.get("comment") or {}

        raw_links: list[dict[str, Any]] = fields.get("issuelinks") or []
        links: list[IssueLink] = []
        for link in raw_links:
            link_type_info: dict[str, Any] = link.get("type") or {}
            inward = link.get("inwardIssue") or {}
            if inward_key := inward.get("key"):
                links.append(
                    IssueLink(
                        target=inward_key,
                        link_type=link_type_info.get("inward", "is blocked by"),
                    )
                )
            outward = link.get("outwardIssue") or {}
            if outward_key := outward.get("key"):
                links.append(
                    IssueLink(
                        target=outward_key,
                        link_type=link_type_info.get("outward", "blocks"),
                    )
                )

        return IssueDetail(
            **common,
            url=self._build_url(common["key"]),
            description=adf_to_markdown(fields.get("description", "")),
            created=fields.get("created", ""),
            updated=fields.get("updated", ""),
            comment_count=int(comment_field.get("total", 0)),
            links=links,
        )

    @staticmethod
    def _extract_custom_fields(fields: dict[str, Any]) -> dict[str, Any]:
        """Surface raw ``customfield_*`` values through ``IssueDetail.metadata``.

        ``IssueDetail`` only models the common Jira system fields; tool-specific
        custom fields (Origin, Bug Type, Severity, …) were previously dropped on
        the read path. Callers that need them (e.g. the quality lens reading
        ``customfield_13269``) read them back from ``metadata`` keyed by raw
        field id. Values are passed through verbatim — Jira returns custom-field
        values in heterogeneous shapes (``{"value": ...}`` for selects, scalars
        for text/number), so normalization is the caller's concern.
        """
        return {k: v for k, v in fields.items() if k.startswith("customfield_")}

    # ── Field schema ─────────────────────────────────────────────────

    def _get_field_schemas(self, client: JiraClient) -> dict[str, str | FieldSchema]:
        """Fetch field metadata (lazy, cached). Returns {field_id: schema}.

        Offline-first, 3-tier resolution (S2503.17, S2503.20):
        1. config.field_types when populated (previously discovered/cached).
        2. Live get_fields() API call when field_types is empty — extracts
           rich FieldSchema (type + items) per field and auto-persists the
           customfield_* entries to .raise/backlog.yaml so subsequent
           sessions read tier 1 instead of hitting the API again.
        """
        if not self._field_schemas:
            if self._config.field_types:
                self._field_schemas = dict(self._config.field_types)
                # System fields (priority, issuetype, …) are absent from field_types
                # cache (which only stores custom fields from `fields discover`).
                # Seed them offline so _wrap_field_value wraps them correctly.
                for sys_field in self._NAME_OBJECT_TYPES:
                    self._field_schemas.setdefault(sys_field, sys_field)
            else:
                for f in client.get_fields():
                    field_id = f["id"]
                    schema = f.get("schema", {})
                    items_raw = schema.get("items")
                    if isinstance(items_raw, str):
                        items: dict[str, str] | None = {"type": items_raw}
                    elif isinstance(items_raw, dict):
                        items = items_raw
                    else:
                        items = None
                    self._field_schemas[field_id] = FieldSchema(
                        type=schema.get("type", "string"),
                        items=items,
                        custom=field_id.startswith("customfield_"),
                    )
                self._auto_cache_field_types(self._field_schemas)
        return self._field_schemas

    def _auto_cache_field_types(self, schemas: dict[str, str | FieldSchema]) -> None:
        """Persist live-fetched customfield_* schemas to .raise/backlog.yaml.

        Only customfield_* entries are written — system fields (priority,
        issuetype, …) are seeded offline at read time via _NAME_OBJECT_TYPES,
        so caching them would be redundant. Skips entirely when project_root
        is unknown (nowhere safe to write) or there's nothing to persist.
        """
        if self._project_root is None:
            return
        persistable: dict[str, Any] = {
            field_id: (
                schema.model_dump(exclude_defaults=True)
                if isinstance(schema, FieldSchema)
                else schema
            )
            for field_id, schema in schemas.items()
            if field_id.startswith("customfield_")
        }
        if not persistable:
            return
        with contextlib.suppress(OSError):
            save_backlog_config(
                self._project_root, "jira", {"field_types": persistable}
            )

    # Schema types that Jira expects as {"name": value} objects.
    _NAME_OBJECT_TYPES = frozenset(
        {"priority", "issuetype", "resolution", "version", "component", "group"}
    )

    # Field IDs (not schema types) that Jira expects as {"key": value} objects —
    # relational system fields whose wire shape is fixed regardless of what a
    # given Jira instance reports as the field's schema type (RAISE-14071).
    _KEY_OBJECT_FIELDS = frozenset({"parent"})

    # Field IDs (not schema types) that Jira expects as a LIST of {"name": value}
    # objects — array-of-version system fields (RAISE-14071).
    _ARRAY_NAME_OBJECT_FIELDS = frozenset({"fixVersions"})

    @staticmethod
    def _normalize_field_schema(raw: str | FieldSchema) -> FieldSchema:
        if isinstance(raw, str):
            return FieldSchema.from_legacy_string(raw)
        return raw

    def _wrap_user_field(self, value: str, client: JiraClient) -> dict[str, Any]:
        users = client.search_users(value)
        if not users:
            raise JiraApiError(f"No Jira user found for '{value}'")
        return {"accountId": users[0]["accountId"]}

    def _wrap_array_field(
        self, value: str, items: dict[str, str] | None, client: JiraClient
    ) -> list[Any]:
        values = [v.strip() for v in value.split(",")]
        if not items:
            return values
        item_type = items.get("type", "string")
        if item_type == "user":
            return [self._wrap_user_field(v, client) for v in values]
        if item_type == "option":
            return [{"value": v} for v in values]
        return values

    @staticmethod
    def _validate_date(value: str) -> None:
        import datetime as dt

        try:
            dt.date.fromisoformat(value)
        except ValueError:
            raise JiraApiError(
                f"Date field must be ISO format YYYY-MM-DD, got '{value}'"
            ) from None

    @staticmethod
    def _validate_datetime(value: str) -> None:
        import datetime as dt

        normalized = value.replace(" ", "T")
        try:
            if "T" not in normalized:
                raise ValueError("datetime must include time component")
            dt.datetime.fromisoformat(normalized.replace("+0000", "+00:00"))
        except ValueError:
            raise JiraApiError(
                f"Datetime field must be ISO 8601 format (e.g., 2026-07-30T10:00:00), got '{value}'"
            ) from None

    def _wrap_field_value(
        self,
        field_id: str,
        value: Any,
        schemas: dict[str, str | FieldSchema],
        client: JiraClient,
    ) -> Any:
        """Wrap value based on Jira field schema — universal dispatch (S2503.20)."""
        if field_id in self._KEY_OBJECT_FIELDS:
            return {"key": value} if isinstance(value, str) else value
        if field_id in self._ARRAY_NAME_OBJECT_FIELDS:
            return [{"name": value}] if isinstance(value, str) else value
        if not isinstance(value, str):
            return value

        schema = self._normalize_field_schema(schemas.get(field_id, "string"))
        return self._wrap_typed_value(value, schema, client)

    def _wrap_typed_value(
        self, value: str, schema: FieldSchema, client: JiraClient
    ) -> Any:
        """Dispatch string value wrapping by schema type (S2503.20)."""
        if schema.type == "user":
            return self._wrap_user_field(value, client)
        if schema.type == "array":
            return self._wrap_array_field(value, schema.items, client)
        if schema.type in self._NAME_OBJECT_TYPES:
            return {"name": value}
        if schema.type in ("option", "option-with-child"):
            return {"value": value}
        if schema.type == "number":
            with contextlib.suppress(ValueError):
                return float(value)
            return value
        if schema.type == "date":
            self._validate_date(value)
            return value
        if schema.type == "datetime":
            self._validate_datetime(value)
            return value
        return value

    def _wrap_fields(
        self, fields: dict[str, Any], client: JiraClient
    ) -> dict[str, Any]:
        """Wrap field values based on Jira schema type (all fields, including assignee)."""
        if "assignee" in fields and isinstance(fields["assignee"], str):
            fields["assignee"] = self._wrap_user_field(fields["assignee"], client)
        schemas = self._get_field_schemas(client)
        for key, value in fields.items():
            if key != "assignee":
                fields[key] = self._wrap_field_value(key, value, schemas, client)
        return fields

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
            fields["description"] = markdown_to_adf(issue.description)
        if issue.labels:
            fields["labels"] = issue.labels
        fields.update(issue.metadata or {})
        if issue.parent:
            fields["parent"] = {"key": issue.parent}

        self._wrap_fields(fields, client)
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
        self._wrap_fields(normalized, client)
        client.update_issue(key, normalized)
        return IssueRef(key=key, url=self._build_url(key))

    # ── Project versions / fixVersions ──────────────────────────────

    @staticmethod
    def _parse_project_version(
        raw: dict[str, Any], project_key: str, *, created: bool = False
    ) -> ProjectVersion:
        """Normalize a Jira project-version payload."""
        return ProjectVersion(
            id=str(raw.get("id", "")),
            name=str(raw.get("name", "")),
            project_key=project_key,
            released=bool(raw.get("released", False)),
            archived=bool(raw.get("archived", False)),
            start_date=str(raw.get("startDate", "") or ""),
            release_date=str(raw.get("releaseDate", "") or ""),
            description=str(raw.get("description", "") or ""),
            created=created,
        )

    async def list_versions(self, project_key: str) -> list[ProjectVersion]:
        """List project versions/fixVersions for a Jira project."""
        client = self._client_for(project_key)
        raw_versions = client.get_project_versions(project_key)
        return [
            self._parse_project_version(raw, project_key)
            for raw in raw_versions
            if raw.get("name")
        ]

    async def create_version(self, project_key: str, name: str) -> ProjectVersion:
        """Create a project version by name, returning existing versions idempotently."""
        clean_name = name.strip()
        if not clean_name:
            raise JiraApiError("Version name must not be empty")

        client = self._client_for(project_key)
        for raw in client.get_project_versions(project_key):
            if str(raw.get("name", "")) == clean_name:
                return self._parse_project_version(raw, project_key, created=False)

        raw = client.create_project_version(project_key, clean_name)
        return self._parse_project_version(raw, project_key, created=True)

    def _merged_status_mapping(self) -> dict[str, str]:
        """Build merged slug→canonical_name map from all configured issue types."""
        merged: dict[str, str] = {}
        for wf in self._config.workflow.values():
            merged.update(
                {name.lower().replace(" ", "-"): name for name in wf.status_mapping}
            )
        return merged

    def _merged_status_id_mapping(self) -> dict[str, str]:
        """Build merged slug→status_id map from all configured states.

        Uses state IDs (locale-independent) instead of display names so that
        slugs like "en-curso" resolve to the same status as "in-progress"
        when they map to the same Jira status ID (RAISE-4140).
        """
        merged: dict[str, str] = {}
        for wf in self._config.workflow.values():
            for state in wf.states:
                name = str(state.get("name", ""))
                sid = str(state.get("id", ""))
                if name and sid:
                    merged[name.lower().replace(" ", "-")] = str(sid)
        return merged

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition issue status — ID-based match with name-based fallback.

        Primary: resolves slug→status_id from discover states, then matches
        transitions by to_id (locale-independent — works for localized Jira
        instances and custom status names regardless of transition name).
        Fallback: canonical name match for instances without to_id in the
        transitions response.
        """
        client = self._client_for(self._project_key_from_issue(key))
        transitions = client.get_transitions(key)

        # Step 0: explicit alias→state_id from status_aliases (RAISE-7078)
        match = None
        alias_id = self._config.status_aliases.get(status)
        if alias_id is not None:
            match = next(
                (t for t in transitions if t.get("to_id") == str(alias_id)), None
            )

        # Primary: ID-based match (locale-independent)
        if not match:
            id_map = self._merged_status_id_mapping()
            target_id = id_map.get(status)
            if target_id:
                match = next(
                    (t for t in transitions if t.get("to_id") == target_id), None
                )

        # Fallback: name-based match (existing behavior)
        if not match:
            canonical_map = self._merged_status_mapping()
            target_name = canonical_map.get(status) or normalize_status(status)
            match = next(
                (t for t in transitions if t["name"].lower() == target_name.lower()),
                None,
            )
            if not match:
                available = [t["name"] for t in transitions]
                raise JiraApiError(
                    f"No transition to '{target_name}' for {key}. Available: {available}"
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
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("batch_transition failed for %s: %s", key, exc)
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    async def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Create multiple issues, isolating failures per item."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for spec in issues:
            try:
                ref = await self.create_issue(spec.project, spec)
                succeeded.append(ref)
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("batch_create failed for %r: %s", spec.summary, exc)
                failed.append(FailureDetail(key=spec.summary, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ── Search ──────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        fetch_all: bool = False,
    ) -> list[IssueSummary]:
        """Search issues via JQL with query normalization."""
        jql = to_jql(query)
        project_key = self._extract_project_from_jql(jql)
        client = (
            self._client_for(project_key)
            if project_key is not None
            else self._client_for_org(self._config.default_org)
        )
        if fetch_all:
            all_raw = client.jql_all(jql)
            return [IssueSummary(**self._extract_issue_fields(i)) for i in all_raw]
        # Jira Cloud caps a single jql page at maxResults=100. When the requested
        # window reaches past the first page, page-walk via jql_all() (bounded by
        # cap) and truncate, instead of silently returning only 100 (RAISE-10763).
        if offset + limit > self._MAX_SINGLE_PAGE:
            all_raw = client.jql_all(jql, cap=offset + limit)
            window = all_raw[offset : offset + limit]
            return [IssueSummary(**self._extract_issue_fields(i)) for i in window]
        issues = client.jql(jql, limit=limit, start=offset)
        return [IssueSummary(**self._extract_issue_fields(i)) for i in issues]

    # Jira Cloud caps a single jql/enhanced_jql page at maxResults=100.
    _MAX_SINGLE_PAGE = 100

    _PROJECT_IN_JQL = re.compile(r"project\s*=\s*[\"']?(\w+)[\"']?", re.IGNORECASE)

    def _extract_project_from_jql(self, jql: str) -> str | None:
        """Extract project key from JQL for client routing. None on miss.

        Caller must route via _client_for_org(config.default_org) when this
        returns None — the JQL has no project scope, so it runs cross-project
        against the default org's Jira instance (RAISE-14116).
        """
        match = self._PROJECT_IN_JQL.search(jql)
        if match:
            return match.group(1)
        # Try to extract from issue key pattern
        issue_match = re.search(r"issue\s*=\s*([A-Z][A-Z0-9_]+)-\d+", jql)
        if issue_match:
            return issue_match.group(1)
        return None

    # ── Relationships ───────────────────────────────────────────────

    async def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Set parent via update_issue with parent field."""
        client = self._client_for(self._project_key_from_issue(child_key))
        client.set_parent(child_key, parent_key)
        return True

    async def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Create issue link between two issues."""
        client = self._client_for(self._project_key_from_issue(source))
        canonical, is_inward = _normalize_link_type(
            link_type, self._config.relation_types
        )
        client.create_link(source, target, canonical, inward=is_inward)
        return True

    async def remove_link(self, link_id: str) -> None:
        """Delete an issue link by ID."""
        client = self._client_for_org(self._config.default_org)
        client.delete_issue_link(link_id)

    # ── Comments ────────────────────────────────────────────────────

    async def add_comment(self, key: str, body: str) -> CommentRef:
        """Add comment to an issue."""
        client = self._client_for(self._project_key_from_issue(key))
        result = client.add_comment(key, markdown_to_adf(body))
        comment_id = str(result.get("id", ""))
        return CommentRef(id=comment_id, url="")

    async def get_comments(
        self,
        key: str,
        limit: int = 10,
        offset: int = 0,
        fetch_all: bool = False,
    ) -> list[Comment]:
        """Get comments on an issue.

        Jira comment format: ``{id, body, author: {displayName}, created}``.
        Body may be ADF dict or plain string.
        """
        client = self._client_for(self._project_key_from_issue(key))
        comments_data = client.get_comments(
            key, limit=limit, offset=offset, fetch_all=fetch_all
        )
        return [
            Comment(
                id=str(c.get("id", "")),
                body=adf_to_markdown(c.get("body", "")),
                author=c.get("author", {}).get("displayName", ""),
                created=c.get("created", ""),
            )
            for c in comments_data
        ]

    # ── Field Discovery (S2503.1 / S2503.6) ─────────────────────────

    async def discover_named_fields(
        self,
        names: list[str],
        issue_type: str,
        project_key: str | None = None,
    ) -> list[CustomField]:
        """Discover custom fields by display name via createmeta (RAISE-15667).

        Delegates to ``discover_fields_for_issue_type`` (createmeta endpoint),
        which requires only ``read:jira-work``. Previously this called
        ``get_field_contexts`` / ``get_field_context_options`` (the field-context
        admin endpoints), which require ``manage:jira-configuration`` — a scope
        normal Jira users don't have, so the command failed for anyone but an
        admin. ``project_key`` is required because createmeta is scoped per
        project + issue type.
        """
        if not project_key:
            raise JiraApiError(
                "discover_named_fields requires project_key — configure at "
                "least one project under the adapter's 'projects' section in "
                ".raise/backlog.yaml (RAISE-15667)"
            )
        field_defs = await self.discover_fields_for_issue_type(project_key, issue_type)
        name_to_field = {fd.name: fd for fd in field_defs}

        results: list[CustomField] = []
        for name in names:
            if name not in name_to_field:
                raise JiraApiError(f"Field '{name}' not found on this instance")
            field_def = name_to_field[name]
            field_contexts = (
                [
                    CustomFieldContext(
                        id=issue_type,
                        name=issue_type,
                        is_global=False,
                        values=field_def.allowed_values,
                    )
                ]
                if field_def.allowed_values
                else []
            )
            results.append(
                CustomField(
                    name=field_def.name,
                    id=field_def.id,
                    context=issue_type,
                    field_contexts=field_contexts,
                    schema_type=field_def.schema_type or "string",
                )
            )
        return results

    async def discover_fields_for_issue_type(
        self, project_key: str, issue_type_name: str
    ) -> list[FieldDefinition]:
        """Return fields with allowedValues for a specific issue type (S9939.1).

        Uses createmeta endpoint — returns [] on any failure (best-effort).
        """
        client = self._client_for(project_key)
        raw = client.get_fields_for_issue_type(project_key, issue_type_name)
        return [
            FieldDefinition(
                id=f["id"],
                name=f["name"],
                custom=str(f.get("id", "")).startswith("customfield_"),
                allowed_values=[
                    v["value"] if "value" in v else v["name"]
                    for v in f.get("allowedValues", [])
                    if isinstance(v, dict) and ("value" in v or "name" in v)
                ],
                schema_type=f.get("schema", {}).get("type", ""),
            )
            for f in raw
        ]

    async def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Return all fields for an instance (project_key selects the instance — fields are instance-wide within it).

        Returns both system fields (priority, assignee, status) and custom fields.
        Use FieldDefinition.custom to distinguish them.
        """
        client = self._client_for(project_key)
        all_fields = client.get_fields()
        return [
            FieldDefinition(
                id=f["id"],
                name=f["name"],
                custom=str(f.get("id", "")).startswith("customfield_"),
            )
            for f in all_fields
        ]

    async def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Return workflow statuses for a project filtered by issue type."""
        client = self._client_for(project_key)
        return client.get_project_workflows(project_key, issue_type=issue_type)

    async def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Return all issue link types available in the instance."""
        client = self._client_for_org(self._config.default_org)
        raw = client.get_link_types()
        return [
            LinkTypeDefinition(
                id=str(lt["id"]),
                name=str(lt["name"]),
                inward=str(lt["inward"]),
                outward=str(lt["outward"]),
            )
            for lt in raw
        ]

    async def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Return issue types available for a project."""
        client = self._client_for(project_key)
        return client.get_issue_types(project_key)

    # ── Attachments (S2503.7) ────────────────────────────────────────

    async def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Upload a file to a Jira issue.

        MIME type is inferred via mimetypes.guess_type when not provided.
        Falls back to application/octet-stream for unknown extensions.
        """
        import mimetypes

        resolved_mime = (
            mime_type
            or mimetypes.guess_type(str(path))[0]
            or "application/octet-stream"
        )
        client = self._client_for(self._project_key_from_issue(key))
        raw = client.attach(key, path, resolved_mime)
        return AttachmentRef(
            id=str(raw["id"]),
            filename=str(raw["filename"]),
            content_url=str(raw.get("content", "")),
        )

    async def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Return metadata for all attachments on a Jira issue."""
        client = self._client_for(self._project_key_from_issue(key))
        raws = client.get_attachments(key)
        return [
            AttachmentDetail(
                id=str(r["id"]),
                filename=str(r["filename"]),
                mime_type=str(r.get("mimeType", "application/octet-stream")),
                size=int(r.get("size", 0)),
                created_at=str(r.get("created", "")),
                content_url=str(r.get("content", "")),
            )
            for r in raws
        ]

    async def download_attachment(self, attachment_id: str) -> bytes:
        """Download attachment binary content by ID.

        Attachment IDs are global in Jira — uses default_org client.
        """
        client = self._client_for_org(self._config.default_org)
        return client.download_attachment(attachment_id)

    # ── Sprint (Jira-specific) ───────────────────────────────────────

    def get_sprints(self, project_key: str, state: str | None = None) -> list[Any]:
        """Return sprints for the board associated with project_key."""
        client = self._client_for(project_key)
        board_id = client.get_board_for_project(project_key)
        return client.get_sprints(board_id, state=state)

    def assign_to_sprint(self, issue_key: str, sprint_id: int) -> None:
        """Assign issue_key to sprint_id."""
        project_key = self._project_key_from_issue(issue_key)
        client = self._client_for(project_key)
        client.assign_to_sprint(sprint_id, issue_key)

    # ── Health ──────────────────────────────────────────────────────

    async def health(self) -> AdapterHealth:
        """Check Jira connectivity via server_info."""
        try:
            # Use default instance for health check
            client = self._client_for_org(self._config.default_org)
            start = time.monotonic()
            client.server_info()
            latency = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira",
                healthy=True,
                message="OK",
                latency_ms=latency,
            )
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("Jira health check failed: %s", exc)
            return AdapterHealth(
                name="jira",
                healthy=False,
                message=str(exc),
            )

    @classmethod
    def from_client(
        cls, client: JiraClient, project_root: Path | None = None
    ) -> PythonApiJiraAdapter:
        """Create a JiraAdapter with a pre-configured JiraClient (Carril B, ADR-112).

        Seeds the client cache with *client* so that all subsequent calls use the
        Bearer-authenticated client instead of resolving from env vars.
        """
        from urllib.parse import urlparse

        adapter = cls(project_root)
        hostname = urlparse(client._url).netloc or client._url  # pyright: ignore[reportPrivateUsage]
        adapter._clients[hostname] = client
        return adapter

    @classmethod
    def from_oauth_client(
        cls, client: JiraClient, project_root: Path | None = None
    ) -> PythonApiJiraAdapter:
        """Create a JiraAdapter mapping every configured org to one Bearer client.

        Server-side delegated flow (S10418.6, Carril B, ADR-112): a single
        OAuth Bearer-authenticated *client* stands in for all configured
        organizations, so every ``org.url`` cache key resolves to it instead
        of a per-org basic-auth client.
        """
        adapter = cls.from_client(client, project_root=project_root)
        for org in adapter._config.organizations.values():
            adapter._clients[org.url] = client
        return adapter
