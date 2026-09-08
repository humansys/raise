"""Backlog sync: query remote adapter, format markdown, write atomically.

Generates ``governance/backlog.md`` from a remote PM adapter (e.g., Jira).
The filesystem adapter is detected and rejected (it IS the source of truth).

Architecture: S347.6 (E347 Backlog Automation)
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel, Field

from raise_cli.adapters.models import IssueSummary

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from raise_cli.adapters.protocols import ProjectManagementAdapter


class SyncResult(BaseModel):
    """Result of a backlog sync operation."""

    adapter_name: str = Field(..., description="Name of source adapter")
    epic_count: int = Field(..., description="Number of epics synced")
    timestamp: str = Field(..., description="ISO 8601 sync timestamp")
    output_path: str = Field(..., description="Path to generated file")


class ItemsSyncResult(BaseModel):
    """Result of a backlog-items cartridge sync operation (RAISE-16428 DS4-1)."""

    project_key: str = Field(..., description="Project key filter used for the fetch")
    org_id: str = Field(..., description="Organisation identifier for the cartridge")
    item_count: int = Field(..., description="Number of issues fetched and written")
    cartridge_dir: str = Field(
        ..., description="Path to the generated cartridge directory"
    )
    timestamp: str = Field(..., description="ISO 8601 sync timestamp")
    fetch_mode: str = Field("full", description="full or incremental")


def _require_jira_compatible(adapter: ProjectManagementAdapter) -> None:
    """Reject adapters that cannot process JQL queries (MUST-ARCH-003)."""
    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.ledger_aware import LedgerAwareAdapter
    from raise_cli.adapters.sync import SyncPMAdapter

    if isinstance(adapter, FilesystemPMAdapter):
        raise ValueError("Filesystem adapter is source of truth — nothing to sync.")
    inner = adapter.remote if isinstance(adapter, LedgerAwareAdapter) else adapter
    if not isinstance(inner, SyncPMAdapter):
        raise ValueError(
            "Backlog sync currently supports Jira adapters only. "
            "Configure Jira with /rai-backlog-setup."
        )


def sync_backlog(
    adapter: ProjectManagementAdapter,
    adapter_name: str,
    project_filter: str | None,
    output_path: Path,
) -> SyncResult:
    """Query adapter, format markdown, write atomically.

    Raises:
        ValueError: If adapter is not a Jira-compatible adapter.
        RuntimeError: If adapter query fails (file left untouched).
    """
    _require_jira_compatible(adapter)

    # Build query
    query = "issuetype = Epic ORDER BY key ASC"
    if project_filter:
        query = f'project = "{project_filter}" AND issuetype = Epic ORDER BY key ASC'

    # Fetch from adapter — let exceptions propagate (file untouched)
    try:
        results = adapter.search(query, limit=200)
    except Exception as exc:
        raise RuntimeError(f"Adapter '{adapter_name}' failed: {exc}") from exc

    # Format and write
    timestamp = datetime.now(UTC).isoformat()
    from raise_cli.core.files import atomic_write

    content = _format_markdown(results, adapter_name, timestamp)
    atomic_write(output_path, content)

    return SyncResult(
        adapter_name=adapter_name,
        epic_count=len(results),
        timestamp=timestamp,
        output_path=str(output_path),
    )


_INACTIVE_STATUSES = ("Done", "Cancelled")


def _read_watermark(cartridge_dir: Path) -> str | None:
    """Read the last_fetch_at watermark from an existing CARTRIDGE.yaml."""
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    if not manifest_path.exists():
        return None
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    generation = raw.get("generation")
    if not isinstance(generation, dict):
        return None
    wm = generation.get("last_fetch_at")
    return str(wm) if wm is not None else None


def _format_watermark_for_jql(watermark: str) -> str:
    """Convert ISO 8601 watermark to Jira JQL date format (``yyyy-MM-dd HH:mm``)."""
    dt = datetime.fromisoformat(watermark)
    return dt.strftime("%Y-%m-%d %H:%M")


def _build_items_query(
    project_key: str,
    *,
    active_only: bool,
    watermark: str | None,
) -> str:
    """Build the JQL query for backlog items fetch."""
    clauses = [f'project = "{project_key}"']
    if active_only:
        statuses = ", ".join(f'"{s}"' for s in _INACTIVE_STATUSES)
        clauses.append(f"status NOT IN ({statuses})")
    if watermark:
        jql_date = _format_watermark_for_jql(watermark)
        clauses.append(f'updated >= "{jql_date}"')
    return " AND ".join(clauses) + " ORDER BY key ASC"


def sync_backlog_items(
    adapter: ProjectManagementAdapter,
    project_key: str,
    org_id: str,
    cartridges_dir: Path,
    *,
    cartridge_name: str | None = None,
    limit: int | None = None,
    active_only: bool = True,
    full: bool = False,
    project_root: Path | None = None,
) -> ItemsSyncResult:
    """Fetch backlog issues for a project and (re)generate the items cartridge.

    By default fetches only active issues (status NOT IN Done, Cancelled) and
    uses the watermark from the previous sync for incremental fetch
    (RAISE-16444). ``limit`` truncates to the first N issues.

    Args:
        adapter: Remote PM adapter to query.
        project_key: Jira project key (e.g. "RAISE").
        org_id: Organisation identifier for the cartridge.
        cartridges_dir: Parent directory for cartridge output.
        cartridge_name: Override the default cartridge directory name.
        limit: Truncate fetch to first N issues (ordered by key).
        active_only: Exclude Done/Cancelled issues from the query (default True).
            Pass False (CLI ``--all``) to fetch the complete history.
        full: Ignore the watermark and do a complete fetch (CLI ``--full``).
        project_root: When provided, upsert fetched issues into work_items
            SQLite (RTEST-46).

    Raises:
        ValueError: If adapter is not a Jira-compatible adapter.
        RuntimeError: If the adapter query fails (existing cartridge untouched
            — the fetch completes in full before the cartridge is written).
    """
    _require_jira_compatible(adapter)

    name = cartridge_name or f"backlog-{org_id}-{project_key}".lower()
    watermark: str | None = None
    if not full and limit is None:
        watermark = _read_watermark(cartridges_dir / name)

    query = _build_items_query(
        project_key, active_only=active_only, watermark=watermark
    )
    incremental = watermark is not None

    try:
        if limit is not None:
            issues = adapter.search(query, limit=limit, fetch_all=False)
        else:
            issues = adapter.search(query, fetch_all=True)
    except Exception as exc:
        raise RuntimeError(f"Adapter query for '{project_key}' failed: {exc}") from exc

    from raise_core.cartridges.backlog_items import generate_backlog_items_cartridge

    cartridge_dir = generate_backlog_items_cartridge(
        issues,
        cartridges_dir,
        org_id=org_id,
        project_key=project_key,
        cartridge_name=cartridge_name,
        merge_existing=incremental,
    )

    if incremental:
        _warn_on_stale_stubs(cartridge_dir)

    if project_root is not None:
        _upsert_issues_to_work_items(issues, project_root)

    return ItemsSyncResult(
        project_key=project_key,
        org_id=org_id,
        item_count=len(issues),
        cartridge_dir=str(cartridge_dir),
        timestamp=datetime.now(UTC).isoformat(),
        fetch_mode="incremental" if incremental else "full",
    )


def _warn_on_stale_stubs(cartridge_dir: Path) -> None:
    """Warn when the merged items.json still has pre-S1 nodes (RAISE-16888 D-S1.5).

    Incremental sync only rewrites nodes matched by the watermark-filtered
    query — nodes untouched since before this story's metadata enrichment
    landed keep missing ``status_category`` forever unless a full sync runs.
    Minimum viable signal: one read + one counter, no new schema.
    """
    items_path = cartridge_dir / "instances" / "items.json"
    if not items_path.exists():
        return
    try:
        nodes = json.loads(items_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(nodes, list):
        return
    stale_count = sum(
        1
        for n in nodes
        if isinstance(n, dict) and "status_category" not in (n.get("metadata") or {})
    )
    if stale_count > 0:
        logger.warning(
            "%d backlog node(s) in %s lack the status_category metadata key "
            "(written before RAISE-16888) — run `rai backlog sync --full` to "
            "fully hydrate them.",
            stale_count,
            cartridge_dir.name,
        )


def _upsert_issues_to_work_items(
    issues: list[IssueSummary], project_root: Path
) -> None:
    """Write fetched issues into the work_items SQLite table (RTEST-46)."""
    import logging

    from raise_cli.storage.work_items import WorkItemStore

    _log = logging.getLogger(__name__)
    store = WorkItemStore(project_root)
    failed = 0
    for issue in issues:
        try:
            store.upsert_jira_mapping(
                local_key=issue.key,
                jira_key=issue.key,
                summary=issue.summary,
                status=issue.status,
                issue_type=issue.issue_type,
                priority=issue.priority,
                labels=issue.labels,
                assignee=issue.assignee,
                fix_versions=issue.fix_versions,
                parent_jira_key=issue.parent_key,
            )
        except Exception:  # noqa: BLE001 — per-item isolation
            failed += 1
            _log.debug("work_items upsert failed for %s", issue.key, exc_info=True)
    if failed:
        _log.warning(
            "work_items upsert: %d of %d items failed — see debug log",
            failed,
            len(issues),
        )


class _SyncDiscoveryShim:
    """Wrap sync adapter discovery methods as async for BacklogDiscoveryAdapter."""

    def __init__(self, adapter: ProjectManagementAdapter) -> None:
        self._adapter = adapter

    async def discover_issue_types(self, project_key: str) -> list[Any]:
        return self._adapter.discover_issue_types(project_key)

    async def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[Any]:
        return self._adapter.discover_statuses(project_key, issue_type=issue_type)

    async def discover_fields(self, project_key: str) -> list[Any]:
        return self._adapter.discover_fields(project_key)

    async def discover_fields_for_issue_type(
        self, project_key: str, issue_type_name: str
    ) -> list[Any]:
        if hasattr(self._adapter, "discover_fields_for_issue_type"):
            return self._adapter.discover_fields_for_issue_type(  # type: ignore[union-attr]
                project_key, issue_type_name
            )
        return []


def sync_backlog_model(
    adapter: ProjectManagementAdapter,
    project_key: str,
    org_id: str,
    cartridges_dir: Path,
    *,
    cartridge_name: str | None = None,
) -> str:
    """Regenerate the MODEL cartridge (issue types, workflow states, custom fields).

    Wraps the async ``generate_backlog_model_cartridge`` for use from the
    synchronous sync pipeline (RAISE-16436).

    Args:
        adapter: Remote PM adapter with discovery methods.
        project_key: Jira project key (e.g. "RAISE").
        org_id: Organisation identifier for the cartridge.
        cartridges_dir: Parent directory for cartridge output.
        cartridge_name: Override the default cartridge directory name.

    Returns:
        Path to the cartridge directory (as string).

    Raises:
        ValueError: If adapter is not a Jira-compatible adapter.
        RuntimeError: If discovery fails.
    """
    import asyncio

    _require_jira_compatible(adapter)

    from raise_core.cartridges.backlog_model import generate_backlog_model_cartridge

    shim = _SyncDiscoveryShim(adapter)
    try:
        cartridge_dir = asyncio.run(
            generate_backlog_model_cartridge(
                shim,
                project_key,
                cartridges_dir,
                org_id=org_id,
                cartridge_name=cartridge_name,
            )
        )
    except Exception as exc:
        raise RuntimeError(
            f"MODEL cartridge generation for '{project_key}' failed: {exc}"
        ) from exc

    return str(cartridge_dir)


def _escape_pipe(value: str) -> str:
    """Escape pipe characters in markdown table cell values."""
    return value.replace("|", "\\|")


def _format_markdown(
    epics: list[IssueSummary], adapter_name: str, timestamp: str
) -> str:
    """Generate markdown table from IssueSummary list."""
    lines: list[str] = [
        f"<!-- Generated by `rai backlog sync` at {timestamp} from adapter: {adapter_name} -->",
        "<!-- Do not edit manually. Re-run `rai backlog sync` to refresh. -->",
        "",
        "# Backlog",
        "",
        "## Epics Overview",
        "",
        "| Key | Epic | Status | Type |",
        "|-----|------|--------|------|",
    ]
    for epic in epics:
        summary = _escape_pipe(epic.summary)
        status = _escape_pipe(epic.status)
        issue_type = _escape_pipe(epic.issue_type)
        lines.append(f"| {epic.key} | {summary} | {status} | {issue_type} |")
    lines.append("")  # trailing newline
    return "\n".join(lines)
