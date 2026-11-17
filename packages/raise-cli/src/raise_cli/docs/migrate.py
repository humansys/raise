"""Bulk migration of filesystem docs to a documentation target (Confluence).

`plan_migration` discovers migratable docs from `manifest.graph.document_sources`
and infers doc_type + title from path/frontmatter.

`execute_migration` iterates items, calls `target.publish()` for each, and
classifies outcomes into published / queued (pending-op on remote fail) /
failed / skipped.

No SyncLedger — Confluence title upsert makes re-runs idempotent (S1700.6 D2).

Story: S1700.6.1 | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from raise_cli.adapters.models.docs import PublishResult
from raise_cli.adapters.protocols import DocumentationTarget
from raise_cli.context.loaders.documents import load_documents

logger = logging.getLogger(__name__)

# CompositeDocTarget returns success=True with this marker text when remote
# failed but filesystem succeeded (see composite_docs.py:137).
_SYNC_PENDING_MARKER = "sync pending"


class PublishOutcome(str, Enum):
    """Classification of a single publish attempt during migration."""

    PUBLISHED = "published"
    QUEUED = "queued"  # remote failed, op queued for replay
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class MigrationItem:
    """A discovered doc eligible for migration.

    Content is NOT captured here — it's read from disk at execute time to
    avoid stale snapshots if the file changes between plan and execute
    (AR-P1 decision B: filesystem is canonical).
    """

    path: Path
    doc_type: str
    title: str


@dataclass
class MigrationResult:
    """Aggregated result of a migration run."""

    total: int = 0
    published: int = 0
    queued: int = 0
    failed: int = 0
    skipped: int = 0
    items: list[tuple[MigrationItem, PublishOutcome, PublishResult]] = field(
        default_factory=lambda: []
    )


def plan_migration(
    project_root: Path,
    doc_type_filter: str | None = None,
) -> list[MigrationItem]:
    """Discover migratable docs from manifest.graph.document_sources.

    Skips files whose doc_type resolves to the generic "document" sentinel
    (i.e., path doesn't match any doc_type map entry like sops/rfcs/...).
    These files have no routing and would fail at publish anyway.

    Args:
        project_root: Project root directory.
        doc_type_filter: Optional doc_type to filter to (e.g., "sop").

    Returns:
        List of MigrationItem objects ready to publish.
    """
    from raise_cli.onboarding.manifest import load_manifest

    manifest = load_manifest(project_root)
    if manifest is None or manifest.graph is None:
        return []

    nodes = load_documents(project_root, manifest.graph.document_sources)
    items: list[MigrationItem] = []
    for node in nodes:
        doc_type = str(node.metadata.get("doc_type", ""))
        # Skip the generic "document" fallback — no routing, not migratable
        if doc_type == "document" or not doc_type:
            continue
        if doc_type_filter is not None and doc_type != doc_type_filter:
            continue
        if node.source_file is None:
            continue
        items.append(
            MigrationItem(
                path=project_root / node.source_file,
                doc_type=doc_type,
                title=str(node.metadata.get("title", node.id)),
            )
        )
    return items


def execute_migration(
    items: list[MigrationItem], target: DocumentationTarget
) -> MigrationResult:
    """Publish each item to target, aggregate outcomes.

    Args:
        items: Items to publish (from plan_migration).
        target: DocumentationTarget (typically CompositeDocTarget).

    Returns:
        MigrationResult with per-item outcomes and aggregate counts.
    """
    result = MigrationResult(total=len(items))

    for item in items:
        # Re-read from disk at execute time (AR-P1 decision B): the filesystem
        # is canonical, so we must publish what's on disk NOW, not a snapshot
        # taken during plan. Missing/unreadable files are skipped.
        try:
            content = item.path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s — skipping", item.path, exc)
            publish_result = PublishResult(success=False, message=f"unreadable: {exc}")
            result.items.append((item, PublishOutcome.SKIPPED, publish_result))
            _increment(result, PublishOutcome.SKIPPED)
            continue

        metadata = {"title": item.title, "path": str(item.path)}
        try:
            publish_result = target.publish(item.doc_type, content, metadata)
        except Exception as exc:  # noqa: BLE001 — surface as failed, keep going
            logger.warning("Publish failed for %s: %s", item.path, exc, exc_info=True)
            publish_result = PublishResult(success=False, message=str(exc))

        outcome = _classify(publish_result)
        result.items.append((item, outcome, publish_result))
        _increment(result, outcome)

    return result


def _classify(publish_result: PublishResult) -> PublishOutcome:
    """Classify a PublishResult into a migration outcome."""
    if not publish_result.success:
        return PublishOutcome.FAILED
    if _SYNC_PENDING_MARKER in (publish_result.message or ""):
        return PublishOutcome.QUEUED
    return PublishOutcome.PUBLISHED


def _increment(result: MigrationResult, outcome: PublishOutcome) -> None:
    """Update the aggregate counter for the given outcome."""
    if outcome == PublishOutcome.PUBLISHED:
        result.published += 1
    elif outcome == PublishOutcome.QUEUED:
        result.queued += 1
    elif outcome == PublishOutcome.FAILED:
        result.failed += 1
    else:
        result.skipped += 1
