"""Project Management boundary models.

Typed inputs and outputs for the ``ProjectManagementAdapter`` protocol.

Architecture: ADR-033 (PM adapter)
"""

# drift: ignore — modelo de boundary PM tocado por muchas historias; densidad de
# story-tokens pre-existente (no accretion nueva). drift-story-accretion CAND-05.

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from raise_core.workflow.state_machine import WorkflowStateMachine

# Shared field descriptions
_DESC_ISSUE_TITLE = "Issue title"
_DESC_PARENT_KEY = "Parent issue key"
_DESC_CREATED_TS = "ISO 8601 creation timestamp"
_DESC_UPDATED_TS = "ISO 8601 last update timestamp"


# ── Field schema model (S2503.20) ───────────────────────────────────


class FieldSchema(BaseModel, frozen=True):
    """Rich field schema for auto-wrapping — type + items for arrays."""

    type: str = Field(default="string")
    items: dict[str, str] | None = Field(default=None)
    custom: bool = Field(default=False)

    @staticmethod
    def from_legacy_string(type_str: str) -> FieldSchema:
        """Build a FieldSchema from a legacy plain type string."""
        return FieldSchema(type=type_str)


# ── Named custom field models (S2503.11) ────────────────────────────


class CustomFieldContext(BaseModel, frozen=True):
    """One field context with its valid option values."""

    id: str = Field(..., description="Context ID (numeric string)")
    name: str = Field(..., description="Context display name")
    is_global: bool = Field(..., description="True if context applies to all projects")
    values: list[str] = Field(default_factory=list, description="Valid option values")


class CustomField(BaseModel, frozen=True):
    """A named custom field with its ID and per-context option values."""

    name: str = Field(..., description="Display name as shown in the PM tool")
    id: str = Field(..., description="Internal field ID (e.g. customfield_XXXXX)")
    context: str = Field(..., description="Work item type this field belongs to")
    field_contexts: list[CustomFieldContext] = Field(
        default_factory=lambda: list[CustomFieldContext](),
        description="Contexts with their valid option values",
    )
    schema_type: str = Field(
        default="string", description="Jira schema.type (S2503.17)"
    )


# ── Discovery models (S1130.2) ──────────────────────────────────────


class TransitionInfo(BaseModel):
    """A workflow transition available from a status."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Transition numeric ID")
    name: str = Field(..., description="Transition display name")
    to_status: str = Field(..., description="Target status name")


class WorkflowState(BaseModel):
    """A status in a project workflow."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default="", description="Jira status ID (numeric string)")
    name: str = Field(..., description="Status name (e.g. 'In Progress')")
    status_category: str = Field(..., description="Category: new, indeterminate, done")
    transitions: list[TransitionInfo] = Field(
        ..., description="Transitions available from this status"
    )


class FieldDefinition(BaseModel, frozen=True):
    """A Jira field available in the instance."""

    id: str = Field(..., description="Field ID (e.g. 'customfield_10001')")
    name: str = Field(..., description="Field display name (e.g. 'Story Points')")
    custom: bool = Field(..., description="Whether this is a custom field")
    allowed_values: list[str] = Field(
        default_factory=list,
        description="Valid option values for select/multi-select fields (S9939.1)",
    )
    schema_type: str = Field(
        default="",
        description="Jira schema.type (e.g. 'option', 'string', 'number') (S9939.1)",
    )
    belongs_to_issue_types: list[str] = Field(
        default_factory=list,
        description="Issue type names that include this field, from per-issue-type discovery (S9939.1)",
    )


class LinkTypeDefinition(BaseModel, frozen=True):
    """A Jira issue link type."""

    id: str = Field(..., description="Link type ID (numeric string)")
    name: str = Field(..., description="Link type name (e.g. 'Blocks')")
    inward: str = Field(..., description="Inward description (e.g. 'is blocked by')")
    outward: str = Field(..., description="Outward description (e.g. 'blocks')")


class ProjectInfo(BaseModel):
    """Summary of a Jira project for discovery."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(..., description="Project key (e.g. 'RAISE')")
    name: str = Field(..., description="Project display name")
    project_type_key: str = Field(
        ..., description="Project type (e.g. 'software', 'business')"
    )


class ProjectVersion(BaseModel):
    """A project release/fixVersion in a PM tool."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default="", description="Version ID in the PM tool")
    name: str = Field(..., description="Version name (e.g. '3.1.0b1')")
    project_key: str = Field(default="", description="Project key (e.g. 'RAISE')")
    released: bool = Field(default=False, description="Whether the version is released")
    archived: bool = Field(default=False, description="Whether the version is archived")
    start_date: str = Field(default="", description="ISO 8601 start date if available")
    release_date: str = Field(
        default="", description="ISO 8601 release date if available"
    )
    description: str = Field(default="", description="Version description")
    created: bool = Field(
        default=False,
        description="True when returned from a create call that created it now",
    )


class IssueTypeInfo(BaseModel):
    """An issue type available in a project."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Issue type ID")
    name: str = Field(..., description="Issue type name (e.g. 'Story', 'Bug')")
    subtask: bool = Field(..., description="Whether this is a subtask type")


# ── Issue CRUD models ───────────────────────────────────────────────


class IssueSpec(BaseModel):
    """Specification for creating a PM issue."""

    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    project: str = Field(default="", description="Project key (e.g. 'RAISE')")
    description: str = Field(default="", description="Issue body (markdown)")
    issue_type: str = Field(default="Task", description="Issue type name")
    labels: list[str] = Field(default_factory=list)
    parent: str | None = Field(default=None, description=_DESC_PARENT_KEY)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="PM-specific fields"
    )


class IssueLink(BaseModel, frozen=True):
    """Dependency link between two issues — ADR-106 D1.

    Distinct from BacklogLink (filesystem_models.py) which is a file-system
    artefact. IssueLink is a boundary model for PM adapter output.
    """

    target: str = Field(..., description="Linked issue key (e.g. 'RAISE-8401')")
    link_type: str = Field(
        ..., description="Relationship (e.g. 'is blocked by', 'blocks')"
    )


class IssueRef(BaseModel):
    """Reference to an existing PM issue."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    url: str = Field(default="", description="Web URL to the issue")
    metadata: dict[str, Any] = Field(default_factory=dict)
    remote_synced: bool | None = Field(
        default=None,
        description=(
            "Whether a write landed on the remote (True) or was only queued "
            "locally for later replay (False). None means this call site "
            "does not report the signal (RAISE-12598)."
        ),
    )


class IssueDetail(IssueRef):
    """Full issue details — extends IssueRef (inherits key, url, metadata).

    Timestamps use ISO 8601 format (e.g. ``2026-02-27T10:30:00Z``).
    Empty string means timestamp not available.
    """

    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    description: str = Field(default="", description="Issue body (markdown)")
    status: str = Field(..., description="Current status name")
    status_category: str = Field(
        default="",
        description=(
            "Workflow status category: 'new', 'indeterminate', or 'done'. "
            "Empty when the adapter cannot resolve a category (RAISE-11770 — "
            "read-back verification needs this to confirm a Done transition "
            "actually landed, not just the status display name)."
        ),
    )
    issue_type: str = Field(..., description="Issue type (e.g., 'Story', 'Bug')")
    parent_key: str | None = Field(default=None, description=_DESC_PARENT_KEY)
    labels: list[str] = Field(default_factory=list)
    assignee: str | None = Field(default=None, description="Assignee identifier")
    priority: str | None = Field(default=None, description="Priority name")
    created: str = Field(default="", description=_DESC_CREATED_TS)
    updated: str = Field(default="", description=_DESC_UPDATED_TS)
    comment_count: int = Field(default=0, description="Total number of comments")
    links: list[IssueLink] = Field(
        default_factory=list, description="Dependency links (e.g. 'is blocked by')"
    )
    fix_versions: list[str] = Field(
        default_factory=list,
        description=(
            "Assigned fixVersion names. Populated on read so callers can "
            "confirm a fixVersion assignment actually landed (RAISE-11770)."
        ),
    )


class IssueSummary(BaseModel):
    """Compact issue for search results and listings."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    status: str = Field(..., description="Current status name")
    issue_type: str = Field(..., description="Issue type name")
    parent_key: str | None = Field(default=None, description=_DESC_PARENT_KEY)
    assignee: str | None = Field(default=None, description="Assignee identifier")
    priority: str | None = Field(default=None, description="Priority name")
    labels: list[str] = Field(default_factory=list)
    fix_versions: list[str] = Field(
        default_factory=list,
        description="Assigned fixVersion names (mirrors IssueDetail.fix_versions — RAISE-15325).",
    )
    status_category: str = Field(
        default="",
        description=(
            "Workflow status category: 'new', 'indeterminate', or 'done'. "
            "Empty when the adapter cannot resolve a category (mirrors "
            "IssueDetail.status_category — RAISE-16888)."
        ),
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Raw customfield_* passthrough (mirrors IssueDetail.metadata, "
            "inherited from IssueRef — RAISE-16888)."
        ),
    )


class SprintRef(BaseModel, frozen=True):
    """A Jira sprint (Scrum-specific)."""

    id: int = Field(..., description="Sprint ID")
    name: str = Field(..., description="Sprint display name")
    state: str = Field(..., description="Sprint state: active, future, or closed")
    start_date: str = Field(default="", description="ISO 8601 start date")
    end_date: str = Field(default="", description="ISO 8601 end date")


class Comment(BaseModel):
    """Issue comment. Timestamps use ISO 8601 format."""

    id: str = Field(..., description="Comment ID")
    body: str = Field(..., description="Comment body (markdown)")
    author: str = Field(..., description="Author identifier")
    created: str = Field(..., description=_DESC_CREATED_TS)


class CommentRef(BaseModel):
    """Reference to a created comment."""

    id: str = Field(..., description="Comment ID")
    url: str = Field(default="", description="Web URL to the comment")


class FailureDetail(BaseModel):
    """A single failure in a batch operation."""

    key: str = Field(..., description="Issue key that failed")
    error: str = Field(..., description="Error description")


class BatchResult(BaseModel):
    """Result of a batch operation."""

    succeeded: list[IssueRef] = Field(default_factory=lambda: list[IssueRef]())
    failed: list[FailureDetail] = Field(default_factory=lambda: list[FailureDetail]())


# ── Backlog adapter config models (S2503.12) ────────────────────────────


class OrganizationConfig(BaseModel):
    """A named connection to a PM tool instance.

    extra="allow" preserves Jira-specific fields (category, board_type, etc.) from
    migrated jira.yaml.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    url: str = Field(..., description="Tool endpoint (e.g. humansys.atlassian.net)")
    email: str = Field(default="", description="Auth email — falls back to env")
    projects: list[str] = Field(
        default_factory=list, description="Project keys on this org"
    )


class ProjectConfig(BaseModel):
    """A work container within an organization."""

    model_config = ConfigDict(extra="allow", frozen=True)

    org: str = Field(
        ..., description="Organization key (references organizations dict)"
    )
    name: str = Field(default="", description="Human-readable project name")
    issue_types: list[str] = Field(default_factory=list, description="Issue type names")


class WorkflowConfig(BaseModel, frozen=True):
    """Workflow states and status mapping for an adapter."""

    states: list[dict[str, Any]] = Field(default_factory=lambda: list[dict[str, Any]]())
    status_mapping: list[str] = Field(default_factory=list)


class UnknownProjectKeyError(ValueError):
    """Raised by resolve_org when project_key is not registered in backlog.yaml:projects."""

    def __init__(self, project_key: str) -> None:
        super().__init__(
            f"Unknown project key '{project_key}'. "
            f"Register it under 'projects:' in .raise/backlog.yaml."
        )
        self.project_key = project_key


class BacklogAdapterConfig(BaseModel, frozen=True):
    """Generic per-adapter config section in backlog.yaml.

    Extra fields (team, issue_types, etc.) pass through via extra='allow'.
    """

    model_config = ConfigDict(extra="allow")

    default_org: str = Field(..., description="Default organization key")
    organizations: dict[str, OrganizationConfig] = Field(
        ..., description="Named organizations"
    )
    projects: dict[str, ProjectConfig] = Field(default_factory=dict)
    custom_fields: dict[str, list[CustomField]] = Field(
        default_factory=dict,
        description="Custom fields keyed by issue type context",
    )
    workflow: dict[str, WorkflowConfig] = Field(
        default_factory=dict,
        description="Workflow states keyed by issue type (e.g. 'Bug', 'Story')",
    )
    status_aliases: dict[str, int] = Field(
        default_factory=dict,
        description="CLI alias → Jira state ID lifted from flat workflow.status_mapping (RAISE-7078)",
    )
    relation_types: list[dict[str, Any]] = Field(
        default_factory=lambda: list[dict[str, Any]](),
        description="Issue relation/link types",
    )
    field_types: dict[str, str | FieldSchema] = Field(
        default_factory=dict,
        description="field_id → schema mapping (FieldSchema | legacy string) for offline-first wrapping",
    )
    issue_type_aliases: dict[str, str] = Field(
        default_factory=dict,
        description="Localized name → canonical name (e.g. Historia → Story) for CLI alias resolution",
    )
    issue_type_prefixes: dict[str, str] = Field(
        default_factory=dict,
        description="Issue type → key prefix (e.g. Epic → e, Story → s). Populated by issue-types discover.",
    )

    @model_validator(mode="before")
    @classmethod
    def _migrate_flat_workflow(cls, data: Any) -> Any:
        """Strip legacy flat workflow keys and migrate per-type status_mapping dict→list.

        1. Strips top-level flat keys (states, status_mapping).
        2. Migrates per-issue-type status_mapping from dict to list of canonical names.
           Dict values become list items; slug keys are dropped (always re-derivable).

        Note: lifecycle_mapping was removed from _legacy_keys in RAISE-15038.
        The key was obsolete since RAISE-7078 and no longer needs a migration shim.
        """
        _legacy_keys: frozenset[str] = frozenset({"states", "status_mapping"})
        if not isinstance(data, dict):
            return data
        raw_wf = data.get("workflow")  # type: ignore[reportUnknownVariableType]
        if not isinstance(raw_wf, dict):
            return data  # type: ignore[reportUnknownVariableType]
        wf: dict[str, Any] = raw_wf  # type: ignore[reportUnknownVariableType]
        # Lift flat status_mapping (alias→int) to status_aliases before stripping (RAISE-7078)
        flat_sm = wf.get("status_mapping")
        if isinstance(flat_sm, dict) and all(
            isinstance(v, int) for v in flat_sm.values()
        ):
            existing: dict[str, int] = cast(
                "dict[str, int]", data.get("status_aliases", {})
            )
            data = {
                **data,
                "status_aliases": {**existing, **cast("dict[str, int]", flat_sm)},
            }
        # Strip legacy flat keys
        cleaned: dict[str, Any] = {k: v for k, v in wf.items() if k not in _legacy_keys}
        # Migrate per-type status_mapping dict → list
        for itype, itype_config in cleaned.items():
            if not isinstance(itype_config, dict):
                continue
            sm: Any = cast("dict[str, Any]", itype_config).get("status_mapping")
            if isinstance(sm, dict):
                cleaned[itype] = {
                    **cast("dict[str, Any]", itype_config),
                    "status_mapping": list(cast("dict[str, Any]", sm).values()),
                }
        return {**data, "workflow": cleaned}  # type: ignore[reportUnknownVariableType]

    @model_validator(mode="before")
    @classmethod
    def _normalize_custom_fields_casing(cls, data: Any) -> Any:
        """Merge custom_fields entries that differ only by issue-type key casing.

        `fields discover --issue-type bug` and `--issue-type Bug` are
        independent write-path calls that verbatim-key the dict by
        operator-typed casing, so a stale on-disk config (or one written
        before the write-path fix) can still carry sibling keys like
        `bug` and `Bug`. This validator groups keys case-insensitively
        (`key.casefold()`), MERGES each group's field lists, and dedupes
        by ``CustomField.id`` (stable; ``name`` may be localized) so a
        lookup on any casing sees the full set. The emitted key is the
        FIXED_PREFIXES canonical casing (Epic/Story/Bug) when the group
        matches one of those, else the first-seen casing (RAISE-10285).
        """
        if not isinstance(data, dict):
            return data
        raw_cf = data.get("custom_fields")  # type: ignore[reportUnknownVariableType]
        if not isinstance(raw_cf, dict) or not raw_cf:
            return data  # type: ignore[reportUnknownVariableType]
        cf: dict[str, Any] = raw_cf  # type: ignore[reportUnknownVariableType]

        merged = merge_custom_fields_entries(cf.items())
        return {**data, "custom_fields": merged}  # type: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def _validate_org_references(self) -> BacklogAdapterConfig:
        if self.default_org not in self.organizations:
            msg = (
                f"default_org '{self.default_org}' not found in organizations "
                f"(available: {', '.join(self.organizations)})"
            )
            raise ValueError(msg)
        for key, project in self.projects.items():
            if project.org not in self.organizations:
                msg = (
                    f"Project '{key}' references org '{project.org}' "
                    f"not found in organizations (available: {', '.join(self.organizations)})"
                )
                raise ValueError(msg)
        return self

    def resolve_org(self, project_key: str) -> OrganizationConfig:
        """Return OrganizationConfig for project_key.

        Raises UnknownProjectKeyError if project_key is not in projects dict.
        Use config.organizations[config.default_org] for an explicit default.
        """
        if project_key not in self.projects:
            raise UnknownProjectKeyError(project_key)
        org_name = self.projects[project_key].org
        return self.organizations[org_name]


# ── Attachment models (S2503.7) ─────────────────────────────────────────


class AttachmentRef(BaseModel, frozen=True):
    """Returned by attach() after a successful upload."""

    id: str = Field(..., description="Attachment ID as assigned by the PM tool")
    filename: str = Field(..., description="Filename as stored in the PM tool")
    content_url: str = Field(..., description="URL to fetch attachment content")


class AttachmentDetail(BaseModel, frozen=True):
    """One entry in the list returned by get_attachments()."""

    id: str = Field(..., description="Attachment ID")
    filename: str = Field(..., description="Filename as stored in the PM tool")
    mime_type: str = Field(..., description="MIME type (e.g. 'image/png')")
    size: int = Field(..., description="File size in bytes")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    content_url: str = Field(..., description="URL to fetch attachment content")
    content: bytes | None = Field(
        default=None,
        description="Binary content — populated only when explicitly fetched",
    )


# ── Prefix utilities (S3382.7) ──────────────────────────────────────────

FIXED_PREFIXES: dict[str, str] = {"Epic": "e", "Story": "s", "Bug": "b"}


def canonicalize_issue_type_key(issue_type: str) -> str:
    """Return the canonical casing for an issue-type dict key (RAISE-10285).

    Case-insensitively maps to a FIXED_PREFIXES entry (Epic/Story/Bug) when
    one matches (e.g. 'bug' -> 'Bug'); otherwise returns issue_type
    unchanged. Used at both the write path (`rai backlog fields discover`)
    and the load-time validator (`BacklogAdapterConfig`) so
    `custom_fields` keys never re-split across repeated calls with
    different operator-typed casing.
    """
    fold = issue_type.casefold()
    for canonical in FIXED_PREFIXES:
        if canonical.casefold() == fold:
            return canonical
    return issue_type


def merge_custom_fields_entries(
    entries: Iterable[tuple[str, Any]],
) -> dict[str, list[Any]]:
    """Merge ``custom_fields`` (issue_type_key, field_list) pairs (RAISE-10285).

    Groups pairs case-insensitively on the issue-type key
    (``key.casefold()`` — so ``bug`` ≡ ``Bug`` ≡ ``BUG``), concatenates the
    field lists of each group, and dedupes by ``CustomField.id`` (the stable
    identity; ``name`` may be localized). On an id collision the LAST
    occurrence wins, so a fresh ``fields discover`` refreshes a previously
    stored field's values rather than dropping the update. The emitted key
    is the FIXED_PREFIXES canonical casing (Epic/Story/Bug) when the group
    matches one of those, else the first-seen casing.

    Accepts an iterable of pairs (not a dict) so callers can feed duplicate
    keys — e.g. an existing on-disk ``{"Bug": [...]}`` chained with an
    incoming ``{"Bug": [...]}`` — and have both lists merged into one bucket
    instead of one silently replacing the other. Field items may be plain
    dicts (loaded from YAML) or ``CustomField`` objects.
    """
    canonical_by_fold: dict[str, str] = {}
    merged: dict[str, list[Any]] = {}
    id_index: dict[str, dict[str, int]] = {}

    for key, fields in entries:
        fold = key.casefold()
        canonical = canonicalize_issue_type_key(key)
        if fold not in canonical_by_fold:
            canonical_by_fold[fold] = canonical
            merged[canonical] = []
            id_index[canonical] = {}
        bucket = canonical_by_fold[fold]
        field_list: list[Any] = fields if isinstance(fields, list) else []
        for f in field_list:
            fid: Any = f.get("id") if isinstance(f, dict) else getattr(f, "id", None)
            if fid is not None and fid in id_index[bucket]:
                merged[bucket][id_index[bucket][fid]] = f  # keep-last: refresh
                continue
            if fid is not None:
                id_index[bucket][fid] = len(merged[bucket])
            merged[bucket].append(f)

    return merged


# ── Pipeline workflow state machine config (S2 RAISE-15029) ────────────────


class StateMapping(BaseModel, frozen=True):
    """Maps a workflow state slug to its Jira/adapter representation.

    Used by PipelineWorkflowConfig to declare states for the state machine builder.
    """

    slug: str
    """Normalized slug (lowercase, hyphenated) used as the machine key."""

    name: str
    """Display name as-is from config or adapter."""

    native_id: str | None = None
    """Jira transition ID or adapter-specific ID (optional)."""


class PipelineWorkflowConfig(BaseModel, frozen=True):
    """Workflow configuration for the pipeline state machine builder.

    Loaded from the ``pipeline_workflow`` section of ``.raise/backlog_config.yaml``.
    Maps pipeline phases to concrete backlog states and declares legal transitions.

    Note: This is distinct from ``WorkflowConfig`` (per-issue-type adapter config
    in BacklogAdapterConfig.workflow). This model is used by the pipeline engine.

    Story: S2 (RAISE-15029) — State Machine Builder
    """

    states: list[StateMapping] = Field(default_factory=list)
    """Known workflow states — slug → display name mapping."""

    transitions: dict[str, list[str]] = Field(default_factory=dict)
    """Legal transitions: from_slug → [to_slug, ...].
    Use ``"*"`` as a to_slug to expand to all other states.
    Empty dict means fail-open: all transitions considered legal."""

    unmanaged_states: list[str] = Field(default_factory=list)
    """State slugs not governed by the pipeline (advisory mode only)."""

    def to_state_machine(self) -> WorkflowStateMachine:
        """Build WorkflowStateMachine from this config.

        Fail-open: empty transitions → all transitions are legal.
        Wildcard ``"*"`` in to_slugs expands to all other states.
        """
        from raise_core.workflow.state_machine import StateSpec, WorkflowStateMachine

        state_map = {
            s.slug: StateSpec(slug=s.slug, name=s.name, native_id=s.native_id)
            for s in self.states
        }

        all_slugs = frozenset(state_map.keys())

        if not self.transitions:
            # Fail-open: no transitions declared → all transitions legal
            trans: dict[str, frozenset[str]] = {
                slug: all_slugs - {slug} for slug in all_slugs
            }
        else:
            trans = {}
            for from_slug, to_slugs in self.transitions.items():
                expanded: set[str] = set()
                for to_slug in to_slugs:
                    if to_slug == "*":
                        expanded |= all_slugs - {from_slug}
                    else:
                        expanded.add(to_slug)
                trans[from_slug] = frozenset(expanded)

        return WorkflowStateMachine(
            states=state_map,
            transitions=trans,
            unmanaged_states=frozenset(self.unmanaged_states),
        )


def assign_prefix(issue_type: str, existing: dict[str, str]) -> str:
    """Return the shortest prefix for issue_type that doesn't collide with existing.values().

    Fixed types (Epic/Story/Bug) always return their canonical prefix.
    Custom types get the shortest unique lowercase prefix starting from 1 char.
    existing is never mutated.
    """
    if not issue_type:
        return "x"
    if issue_type in FIXED_PREFIXES:
        return FIXED_PREFIXES[issue_type]
    lower = issue_type.lower()
    taken = set(existing.values())
    for length in range(1, len(lower) + 1):
        candidate = lower[:length]
        if candidate not in taken:
            return candidate
    return lower
