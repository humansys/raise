"""Regenerate backlog cartridge items.json from the shared work_items DB.

RAISE-16901: items.json for dynamic backlog cartridges is a git-tracked file
that diverges per worktree (25 distinct hashes across 48 worktrees in the
RAISE repo). This module supersedes E16887's "items.json = durable portable
source" decision: ``work_items`` in ``~/.rai/raise.db`` is the
worktree-agnostic source of truth; items.json is a regenerable projection.

Design: work/bugs/RAISE-16901/plan.md (Task 2).

CRAFT-003 (domain purity): DB access lives here in raise_cli.storage, not
in raise_core.cartridges.backlog_items which must remain a pure function.
``build_backlog_item_node`` (raise_core) is called from here — that is the
allowed direction (raise_cli → raise_core).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class _WorkItemIssueProxy:
    """Duck-typed adapter: WorkItem → issue shape for ``build_backlog_item_node``.

    ``WorkItem.type`` is a normalized ``WorkItemType`` (``"story"``,
    ``"bug"``, ``"epic"``, ``"task"``).  Custom Jira types that collapsed to
    ``"story"`` via ``issue_type_to_work_item_type`` (e.g. "Research Item")
    lose their original name here — nodes become ``backlog.story.*`` instead of
    ``backlog.research-item.*``.  Pre-existing limitation of work_items schema;
    content-based search is unaffected.  ``status_category`` defaults to ``""``.
    """

    def __init__(self, wi: Any) -> None:  # WorkItem, avoid circular import
        self.key: str = wi.jira_key or wi.local_key
        self.summary: str = wi.summary or ""
        self.status: str = wi.status or ""
        self.issue_type: str = wi.type or "story"
        self.priority: str | None = wi.priority
        self.labels: list[str] = list(wi.labels or [])
        self.assignee: str | None = wi.assignee
        self.fix_versions: list[str] = list(wi.fix_versions or [])
        # parent field aliases — build_backlog_item_node checks both
        self.parent_key: str | None = wi.parent_jira_key
        self.parent: str | None = wi.parent_jira_key
        # status_category not stored in work_items; default to empty string
        self.status_category: str = ""
        # custom_fields used for metadata; preserve what was stored
        self.metadata: dict[str, Any] = dict(wi.custom_fields or {})
        # updated field aliases — build_backlog_item_node checks both
        self.updated: str | None = wi.updated_at
        self.updated_at: str | None = wi.updated_at


def regenerate_backlog_cartridge_items(
    cartridge_dir: Path,
    project_key: str,
    project_root: Path,
) -> int:
    """Rebuild ``instances/items.json`` from the shared work_items DB.

    Reads all work_items whose ``jira_key`` matches ``{project_key}-*`` from
    ``~/.rai/raise.db`` (scoped to ``project_root``'s project_id), converts
    each to a backlog-item node via ``build_backlog_item_node``, and writes
    the result to ``cartridge_dir/instances/items.json``.

    Returns the number of nodes written (0 means DB is empty for this project
    key — items.json is NOT touched so any existing file is preserved).

    Best-effort: never raises; logs at DEBUG on failure.

    Args:
        cartridge_dir: The backlog-* cartridge directory
            (contains ``CARTRIDGE.yaml``).
        project_key: Jira project key prefix (e.g. ``"RAISE"``).
        project_root: Project root used to resolve project_id and DB path.

    Returns:
        Count of nodes written to items.json, or 0 if DB returned no items.
    """
    try:
        return _regenerate(cartridge_dir, project_key, project_root)
    except Exception:  # noqa: BLE001 — best-effort, must not block graph build
        logger.debug(
            "cartridge_projection: regeneration failed for %s/%s",
            project_key,
            cartridge_dir,
            exc_info=True,
        )
        return 0


def _regenerate(
    cartridge_dir: Path,
    project_key: str,
    project_root: Path,
) -> int:
    """Inner (raises freely — caller catches in best-effort wrapper)."""
    from raise_cli.storage.work_items import WorkItemStore

    store = WorkItemStore(project_root)
    items = store.list_by_jira_project(project_key)
    if not items:
        return 0

    # C1 fix (RAISE-16901): filter out registration stubs before projecting.
    # A stub row has jira_key set (from seed_jira_keys / upsert_jira_mapping
    # registration) but summary == '' or None — it carries no real content.
    # With 2225 stubs in the RAISE DB, projecting them wholesale would
    # overwrite 1555 rich nodes in items.json with empty garbage.
    hydrated = [wi for wi in items if wi.jira_key and wi.summary]
    if not hydrated:
        # All DB rows for this project are stubs — leave items.json untouched
        # so any existing rich content (from a previous sync or git checkout)
        # is preserved.
        return 0

    from raise_core.cartridges.backlog_items import build_backlog_item_node

    cartridge_name = cartridge_dir.name
    new_nodes_by_key: dict[str, dict[str, Any]] = {}
    for wi in hydrated:
        node = build_backlog_item_node(
            _WorkItemIssueProxy(wi),
            cartridge_name=cartridge_name,
        )
        if wi.jira_key is None:  # pragma: no cover — guaranteed by the hydrated filter
            continue
        new_nodes_by_key[wi.jira_key] = node

    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(parents=True, exist_ok=True)
    items_path = instances_dir / "items.json"

    # Merge hydrated rows OVER existing nodes rather than replacing wholesale.
    # Existing rich nodes that are not in the hydrated set (e.g. items from a
    # previous sync that were not returned this run) survive untouched.
    existing_nodes: list[Any] = []
    if items_path.exists():
        try:
            raw = json.loads(items_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                existing_nodes = raw
        except (json.JSONDecodeError, OSError):
            existing_nodes = []

    merged: dict[str, dict[str, Any]] = {
        node["metadata"]["key"]: node
        for node in existing_nodes
        if isinstance(node, dict)
        and isinstance(node.get("metadata"), dict)
        and node["metadata"].get("key")
    }
    merged.update(new_nodes_by_key)
    final_nodes = list(merged.values())

    items_path.write_text(
        json.dumps(final_nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.debug(
        "cartridge_projection: wrote %d nodes to %s (%d hydrated from DB, %d preserved)",
        len(final_nodes),
        items_path,
        len(new_nodes_by_key),
        len(final_nodes) - len(new_nodes_by_key),
    )
    return len(final_nodes)
