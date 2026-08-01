"""Composite documentation target — delegates to multiple targets.

Publishes to ALL targets (e.g. filesystem + Confluence). Reads (get_page,
search, health) delegate to the remote target (last in list — typically Confluence).

Filesystem is first for durability: local copy always saved.
Result prefers last successful publish (remote URL over local path).
If remote fails, returns success with warning (local copy is the guarantee).

S1700.6 — Retrofit with PendingOpsLog:
- On remote failure with filesystem success, append pending op (queue for replay).
- Before each publish, attempt best-effort flush of existing pending ops.
- `pending_ops=None` preserves pre-S1700.6 behavior (backward compat).

RAISE-5618 — Docs sync state in SQLite:
- After each successful remote publish, persist local_path → remote_id/url/updated_at in SQLite.
- Lazy migration imports existing .raise/sync/docs-manifest.yaml entries on first write.
- `project_root=None` skips sync state write (backward compat).

RAISE-1051 (S1051.7) | RAISE-1795 (S1700.6) | RAISE-3414 (S20.2)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.errors import AdapterSyncError
from raise_cli.adapters.models.docs import (
    AttachmentSummary,
    CommentSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.adapters.models.sync import SyncEntry, SyncReport
from raise_cli.adapters.pending_ops import PendingOpsLog

logger = logging.getLogger(__name__)


def migrate_docs_yaml_to_sqlite(project_root: Path) -> None:
    """Lazy one-time migration: import valid YAML entries to SQLite, skip stale paths.

    No-op when the YAML manifest does not exist or SQLite already has entries.
    """
    manifest_path = project_root / ".raise" / "sync" / "docs-manifest.yaml"
    if not manifest_path.exists():
        return
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    db = get_project_db(project_root)
    create_all(db)
    pid = get_project_id(project_root)
    count = db.execute(
        "SELECT COUNT(*) FROM docs_sync WHERE project_id = ?", (pid,)
    ).fetchone()[0]
    if count > 0:
        db.close()
        return
    try:
        data: dict[str, Any] = (
            yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        db.close()
        return
    for key, meta in data.items():
        if not isinstance(meta, dict):
            continue
        if not Path(key).exists():
            continue
        db.execute(
            "INSERT OR IGNORE INTO docs_sync"
            " (local_path, remote_id, url, updated_at, project_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                key,
                str(meta.get("remote_id", "")),
                str(meta.get("url", "")),
                str(meta.get("updated_at", "")),
                pid,
            ),
        )
    db.commit()
    db.close()


class CompositeDocTarget:
    """Delegates to multiple DocumentationTargets.

    - publish: calls all targets; returns last successful result (remote preferred)
    - get_page / search / health: delegate to remote (last) target
    - Filesystem first for durability, Confluence last for the URL
    - Optional pending_ops queues failed remote publishes for later replay (S1700.6)
    - require_local=True: filesystem failure aborts immediately without calling remotes (RAISE-3939)
    """

    def __init__(
        self,
        targets: list[Any],
        pending_ops: PendingOpsLog | None = None,
        project_root: Path | None = None,
        require_local: bool = False,
        server_first: bool = False,
    ) -> None:
        self._targets = targets
        self._remote = targets[-1]  # last target = remote (Confluence)
        self._pending_ops = pending_ops
        self._project_root = project_root
        self._require_local = require_local
        self._server_first = server_first

    def can_publish(self, doc_type: str | None, metadata: dict[str, Any]) -> bool:
        """True if any wrapped target can publish."""
        return any(t.can_publish(doc_type, metadata) for t in self._targets)

    def publish(
        self, doc_type: str | None, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish to all accepting targets. Return best result.

        Prefers last successful result (remote URL). If remote fails but
        local succeeded, returns success with sync-pending warning.

        When `pending_ops` is configured (S1700.6):
        - Before publishing, attempt best-effort flush of queued ops.
        - On remote failure with filesystem success, append a pending op.
        """
        # S1700.6: best-effort flush of pending ops (non-blocking)
        self._flush_pending()

        # RAISE-5894: inject remote_id from docs_sync so remote adapter can PUT by ID
        local_path = metadata.get("path")
        if local_path:
            stored_id = self._load_remote_id(str(local_path))
            if stored_id:
                metadata = {**metadata, "remote_id": stored_id}

        results, failures, fs_result, remote_failed = self._publish_to_targets(
            doc_type, content, metadata
        )

        # S-AQG.3: server-first mode — fail loud on remote failure
        if self._server_first and remote_failed:
            raise AdapterSyncError(f"Remote publish failed: {'; '.join(failures)}")

        # RAISE-5618: persist sync state to SQLite when remote publish succeeded
        if not remote_failed and results:
            remote_result = results[-1]
            local_path = metadata.get("path")
            if remote_result.success and local_path:
                try:
                    self._save_docs_sync(str(local_path), remote_result)
                except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                    logger.warning("Failed to save docs sync state", exc_info=True)

        # S-AQG.3: read-back verify in server-first mode
        if self._server_first and not remote_failed and results:
            self._verify_remote_publish(results[-1])

        # S1700.6: queue pending op when filesystem (canonical) succeeded but remote failed
        if (
            self._pending_ops is not None
            and remote_failed
            and fs_result is not None
            and fs_result.success
        ):
            self._pending_ops.append(
                op="publish",
                key=str(metadata.get("key") or metadata.get("title") or doc_type),
                args={"doc_type": doc_type, "content": content, "metadata": metadata},
            )

        return self._reduce_results(results, failures)

    def _publish_to_targets(
        self, doc_type: str | None, content: str, metadata: dict[str, Any]
    ) -> tuple[list[PublishResult], list[str], PublishResult | None, bool]:
        """Publish to each accepting target, tracking results, failures, and remote status."""
        results: list[PublishResult] = []
        failures: list[str] = []
        fs_result: PublishResult | None = None
        remote_failed = False
        last_idx = len(self._targets) - 1

        for idx, target in enumerate(self._targets):
            if not target.can_publish(doc_type, metadata):
                continue
            try:
                result: PublishResult = target.publish(doc_type, content, metadata)
                results.append(result)
                if idx == 0:
                    fs_result = result
                    if self._require_local and not result.success:
                        failures.append(result.message)
                        return results, failures, fs_result, False
                if not result.success:
                    failures.append(result.message)
                    if idx == last_idx:
                        remote_failed = True
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning(
                    "Composite publish failed on %s: %s",
                    type(target).__name__,
                    exc,
                )
                failures.append(str(exc))
                if idx == last_idx:
                    remote_failed = True

        return results, failures, fs_result, remote_failed

    def _verify_remote_publish(self, remote_result: PublishResult) -> None:
        """Verify page exists after successful remote publish (server-first only)."""
        if not remote_result.success or not remote_result.remote_id:
            return
        try:
            self._remote.get_page(remote_result.remote_id)
        except Exception as exc:
            raise AdapterSyncError(
                f"Page not found post-publish: remote_id={remote_result.remote_id}"
            ) from exc

    @staticmethod
    def _reduce_results(
        results: list[PublishResult], failures: list[str]
    ) -> PublishResult:
        """Reduce per-target results into a single PublishResult."""
        if not results:
            return PublishResult(
                success=False, message="No target accepted this doc_type"
            )
        successful = [r for r in results if r.success]
        if not successful:
            return results[0]
        best = successful[-1]  # last success = remote if available
        if failures:
            return PublishResult(
                success=True,
                url=best.url,
                message=f"{best.message} (sync pending: {'; '.join(failures)})",
                sync_pending=True,
            )
        return best

    def _load_remote_id(self, local_path: str) -> str | None:
        """Return remote_id from docs_sync for local_path, or None if not found."""
        if self._project_root is None:
            return None
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        db = get_project_db(self._project_root)
        create_all(db)
        pid = get_project_id(self._project_root)
        row = db.execute(
            "SELECT remote_id FROM docs_sync WHERE local_path = ? AND project_id = ?",
            (local_path, pid),
        ).fetchone()
        db.close()
        return row[0] if row and row[0] else None

    def _save_docs_sync(self, local_path: str, remote_result: PublishResult) -> None:
        """Persist docs sync state to SQLite after a successful remote publish."""
        if self._project_root is None:
            return
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        self._migrate_yaml_to_sqlite()
        db = get_project_db(self._project_root)
        create_all(db)
        pid = get_project_id(self._project_root)
        db.execute(
            "INSERT INTO docs_sync (local_path, remote_id, url, updated_at, project_id)"
            " VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(local_path, project_id) DO UPDATE SET"
            "   remote_id = excluded.remote_id,"
            "   url = excluded.url,"
            "   updated_at = excluded.updated_at",
            (
                local_path,
                remote_result.remote_id or "",
                remote_result.url or "",
                datetime.now(UTC).replace(microsecond=0).isoformat(),
                pid,
            ),
        )
        db.commit()
        db.close()

    def _migrate_yaml_to_sqlite(self) -> None:
        """Lazy one-time migration: import valid YAML entries to SQLite, skip stale paths."""
        if self._project_root is not None:
            migrate_docs_yaml_to_sqlite(self._project_root)

    def _flush_pending(self) -> None:
        """Attempt to replay pending ops against remote. Best-effort, never raises."""
        if self._pending_ops is None:
            return
        try:
            for op in list(self._pending_ops.iter()):
                args = op.args
                doc_type = str(args.get("doc_type", ""))
                content = str(args.get("content", ""))
                metadata: dict[str, Any] = args.get("metadata") or {}
                try:
                    replay_result = self._remote.publish(doc_type, content, metadata)
                    if (
                        isinstance(replay_result, PublishResult)
                        and replay_result.success
                    ):
                        self._pending_ops.mark_done(op.id)
                    else:
                        msg = getattr(
                            replay_result, "message", "publish returned failure"
                        )
                        self._pending_ops.update_last_error(op.id, str(msg)[:200])
                        count = self._pending_ops.increment_attempt(op.id)
                        if count >= 5:
                            self._pending_ops.move_to_dead_letter(op.id)
                except Exception as exc:  # noqa: BLE001 — replay failure = keep queued
                    logger.warning(
                        "Pending op %s replay raised: %s", op.id, exc, exc_info=True
                    )
                    self._pending_ops.update_last_error(op.id, str(exc)[:200])
                    count = self._pending_ops.increment_attempt(op.id)
                    if count >= 5:
                        self._pending_ops.move_to_dead_letter(op.id)
        except Exception:  # noqa: BLE001 — flush errors never block new publish
            logger.exception("Pending ops flush failed")

    # -------------------------------------------------------------------
    # SyncVerifiable implementation (S-AQG.4)
    # -------------------------------------------------------------------

    @property
    def is_server_first(self) -> bool:
        """True when running in connected mode (RAISE_SERVER_URL + RAISE_API_KEY set)."""
        return self._server_first

    def verify_sync(self, keys: frozenset[str] | None = None) -> SyncReport:
        """Verify docs_sync entries exist on Confluence via GET requests.

        keys=None: verify all entries (--all mode).
        keys: verify entries where local_path or remote_id is in keys (R2 dual match).
        Pending/dead-letter counts are ALWAYS global for docs — op.key is
        metadata title/type, not local_path, so scoping is unreliable (QR-C2).
        """
        sync_entries = self._load_docs_sync_all()
        if keys is not None:
            sync_entries = {
                lp: rid for lp, rid in sync_entries.items() if lp in keys or rid in keys
            }

        entries: list[SyncEntry] = []
        for local_path, remote_id in sync_entries.items():
            try:
                page = self._remote.get_page(remote_id)
                entries.append(
                    SyncEntry(
                        local_key=local_path,
                        remote_key=remote_id,
                        exists=bool(page),
                        detail=f"title={page.title}" if page else "empty response",
                    )
                )
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                entries.append(
                    SyncEntry(
                        local_key=local_path,
                        remote_key=remote_id,
                        exists=False,
                        detail=str(exc)[:200],
                    )
                )

        pending = sum(1 for _ in self._pending_ops.iter()) if self._pending_ops else 0
        dead = (
            sum(1 for _ in self._pending_ops.iter_dead_letter())
            if self._pending_ops
            else 0
        )
        return SyncReport(
            domain="docs",
            entries=tuple(entries),
            pending_count=pending,
            dead_letter_count=dead,
        )

    def _load_docs_sync_all(self) -> dict[str, str]:
        """Return all {local_path: remote_id} entries from docs_sync SQLite."""
        if self._project_root is None:
            return {}
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        db = get_project_db(self._project_root)
        create_all(db)
        pid = get_project_id(self._project_root)
        rows = db.execute(
            "SELECT local_path, remote_id FROM docs_sync WHERE project_id = ?",
            (pid,),
        ).fetchall()
        db.close()
        return {row[0]: row[1] for row in rows if row[1]}

    def get_page(self, identifier: str) -> PageContent:
        """Delegate to remote (last) target."""
        return self._remote.get_page(identifier)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Delegate to remote (last) target."""
        return self._remote.search(query, limit=limit)

    def health(self) -> AdapterHealth:
        """Delegate to remote (last) target."""
        return self._remote.health()

    def add_label(self, page_id: str, name: str) -> None:
        """Delegate to remote (last) target."""
        self._remote.add_label(page_id, name)

    def get_labels(self, page_id: str) -> list[str]:
        """Delegate to remote (last) target."""
        return self._remote.get_labels(page_id)

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        """Delegate to remote (last) target."""
        return self._remote.get_page_children(page_id)

    def delete_page(self, page_id: str) -> None:
        """Delegate to remote (last) target."""
        self._remote.delete_page(page_id)

    def add_comment(self, page_id: str, body: str) -> None:
        """Delegate to remote (last) target."""
        self._remote.add_comment(page_id, body)

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        """Delegate to remote (last) target."""
        return self._remote.get_comments(page_id)

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str:
        """Delegate to remote (last) target."""
        return self._remote.upload_attachment(page_id, file_path, comment)

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        """Delegate to remote (last) target."""
        return self._remote.get_attachments(page_id)

    def embed_attachment(self, page_id: str, filename: str) -> PageContent:
        """Delegate to remote (last) target."""
        return self._remote.embed_attachment(page_id, filename)
