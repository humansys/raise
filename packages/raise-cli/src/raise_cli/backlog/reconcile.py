"""Reconcile — match filesystem artifacts against Jira and sync.

Deterministic matching: jira_key in frontmatter > directory name > ID pattern.
Read-only on Jira until execute phase. Filesystem is canonical.

Story: S1700.4 (reconcile) | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

from raise_cli.adapters.models import IssueSpec
from raise_cli.backlog.scanner import ScannedItem
from raise_cli.storage.work_items import WorkItemStore

logger = logging.getLogger(__name__)

ActionType = Literal["link", "create", "review"]


@dataclass
class ReconcileAction:
    """A single reconciliation action."""

    local_id: str
    title: str
    item_type: str
    action: ActionType
    jira_key: str | None = None
    source_file: str = ""
    parent_id: str | None = None
    reason: str = ""
    error: str | None = None


@dataclass
class ReconcileResult:
    """Summary of reconciliation execution."""

    linked: int = 0
    created: int = 0
    reviewed: int = 0
    failed: int = 0
    actions: list[ReconcileAction] = field(
        default_factory=lambda: list[ReconcileAction]()
    )


def plan_reconcile(
    items: list[ScannedItem],
    jira_issues: dict[str, str],
    wi_store: WorkItemStore,
) -> list[ReconcileAction]:
    """Plan reconciliation actions.

    Args:
        items: Scanned filesystem items.
        jira_issues: {jira_key: summary} from Jira search (read-only).
        wi_store: Work item store for existing key mappings.

    Returns:
        Ordered list of actions (epics first, then stories).
    """
    # Sort parent-first: epics before stories
    sorted_items = sorted(
        items, key=lambda i: (0 if i.item_type == "epic" else 1, i.local_id)
    )

    actions: list[ReconcileAction] = []
    for item in sorted_items:
        # Already mapped → skip (already reconciled)
        if wi_store.get_jira_key(item.local_id):
            continue

        action = _classify_item(item, jira_issues)
        actions.append(action)

    return actions


def _classify_item(
    item: ScannedItem,
    jira_issues: dict[str, str],
) -> ReconcileAction:
    """Classify a single item into link/create/review."""
    # 1. Has jira_key from scanner (frontmatter, blockquote, dirname)
    if item.jira_key:
        if item.jira_key in jira_issues:
            return ReconcileAction(
                local_id=item.local_id,
                title=item.title,
                item_type=item.item_type,
                action="link",
                jira_key=item.jira_key,
                source_file=item.source_file,
                parent_id=item.parent_id,
                reason="jira_key in artifact",
            )
        return ReconcileAction(
            local_id=item.local_id,
            title=item.title,
            item_type=item.item_type,
            action="review",
            jira_key=item.jira_key,
            source_file=item.source_file,
            parent_id=item.parent_id,
            reason=f"jira_key {item.jira_key} not found in Jira",
        )

    # 2. Try match by ID pattern (E1305 → RAISE-1305)
    candidate_key = _id_to_jira_key(item.local_id)
    if candidate_key and candidate_key in jira_issues:
        return ReconcileAction(
            local_id=item.local_id,
            title=item.title,
            item_type=item.item_type,
            action="link",
            jira_key=candidate_key,
            source_file=item.source_file,
            parent_id=item.parent_id,
            reason=f"ID pattern match ({item.local_id} → {candidate_key})",
        )

    # 3. No match → create
    return ReconcileAction(
        local_id=item.local_id,
        title=item.title,
        item_type=item.item_type,
        action="create",
        source_file=item.source_file,
        parent_id=item.parent_id,
        reason="no Jira match found",
    )


def _id_to_jira_key(local_id: str) -> str | None:
    """Convert local ID to potential Jira key. E1305 → RAISE-1305."""
    if local_id.startswith("RAISE-"):
        return local_id
    if local_id.startswith("E"):
        num = local_id[1:]
        if num.isdigit():
            return f"RAISE-{int(num)}"
    return None


def fetch_jira_index(remote: Any, project_key: str) -> dict[str, str]:
    """Fetch all Jira issues as {key: summary} dict. Read-only.

    Paginates using key ranges since adapter search() has a hard limit.
    """
    result: dict[str, str] = {}
    batch_size = 100  # adapter hard limit
    last_key: str | None = None
    while True:
        try:
            if last_key:
                query = f"project = {project_key} AND key > {last_key} ORDER BY key ASC"
            else:
                query = f"project = {project_key} ORDER BY key ASC"
            issues = remote.search(query, limit=batch_size)
            if not issues:
                break
            for issue in issues:
                result[issue.key] = issue.summary
            last_key = issues[-1].key
            if len(issues) < batch_size:
                break
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("Failed to fetch Jira index (after %s): %s", last_key, exc)
            break
    return result


def execute_reconcile(
    actions: list[ReconcileAction],
    remote: Any,
    wi_store: WorkItemStore,
    project_key: str,
) -> ReconcileResult:
    """Execute reconciliation. Only writes to Jira for CREATE actions."""
    result = ReconcileResult()

    for action in actions:
        if action.action == "link":
            # Record mapping — no Jira write
            if action.jira_key:
                wi_store.upsert_jira_mapping(action.local_id, action.jira_key)
            result.linked += 1
            result.actions.append(action)

        elif action.action == "create":
            try:
                spec = IssueSpec(
                    summary=action.title,
                    issue_type="Epic" if action.item_type == "epic" else "Story",
                )
                ref = remote.create_issue(project_key, spec)
                action.jira_key = ref.key
                wi_store.upsert_jira_mapping(action.local_id, ref.key)

                # Link to parent if parent is in store
                if action.parent_id:
                    parent_key = wi_store.get_jira_key(action.parent_id)
                    if parent_key:
                        try:
                            remote.link_to_parent(ref.key, parent_key)
                        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                            logger.warning(
                                "Parent link failed for %s: %s", action.local_id, exc
                            )

                result.created += 1
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                action.error = str(exc)
                result.failed += 1
                logger.warning("Create failed for %s: %s", action.local_id, exc)

            result.actions.append(action)

        elif action.action == "review":
            result.reviewed += 1
            result.actions.append(action)

    return result
