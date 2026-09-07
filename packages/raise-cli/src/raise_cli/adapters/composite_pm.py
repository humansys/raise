"""Composite PM adapter — write-all, read-local.

Dual-writes to all adapters (filesystem + Jira). Reads (get_issue, search,
get_comments, health) delegate to the local adapter (first in list — filesystem).

Filesystem is canonical. Remote failures are queued as pending ops.
Result always returns the local reference.

Story: S1700.3 | Epic: E1700 Adapter Migration Path
Design decision D1: read-local (inverse of CompositeDocTarget which reads remote).
"""

from __future__ import annotations

import contextlib
import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, NamedTuple
from uuid import uuid4

from pydantic import ValidationError

from raise_cli.adapters.errors import AdapterSyncError
from raise_cli.adapters.filesystem_models import BacklogItem
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
from raise_cli.adapters.models.pm import CustomField
from raise_cli.adapters.models.sync import SyncEntry, SyncReport
from raise_cli.adapters.pending_ops import PendingOp, PendingOpsLog
from raise_cli.storage.work_items import WorkItemStore

logger = logging.getLogger(__name__)

# Type alias for remote write action: (remote_adapter, remote_key) -> None
_RemoteAction = Callable[[Any, str], None]

MAX_RETRIES = 5

_JIRA_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")


class RemoteWriteOutcome(NamedTuple):
    """Return contract for ``_write_to_remotes_keyed`` (RAISE-12598).

    Every ``return``/``break`` path in that method must produce one of
    these instead of the previous implicit ``None`` — callers need to be
    able to tell "landed on the remote" from "queued locally for later
    replay" so the signal is not lost at this choke point.
    """

    status: Literal["landed", "queued"]
    reason: Literal["no_remotes", "unmapped", "remote_error"] | None = None
    # RAISE-15818: str(exc) when reason == "remote_error" — carries the actual
    # failure (401, 500, timeout, ...) instead of the generic "remote_error"
    # label. The exception is already logged server-side; this lets it reach
    # the CLI too.
    error_detail: str | None = None


class CompositeBacklogAdapter:
    """Write-all, read-local PM adapter with sync state.

    - Write ops (7): delegate to all adapters; remote failures → pending ops
    - Read ops (4): delegate to local (filesystem) only
    - health: delegates to local — composite is healthy if filesystem works
    """

    def __init__(
        self,
        adapters: list[Any],
        wi_store: WorkItemStore,
        pending: PendingOpsLog,
        *,
        server_first: bool = False,
    ) -> None:
        self._local = adapters[0]
        self._remotes = adapters[1:]
        self._wi_store = wi_store
        self._pending = pending
        self._server_first = server_first

    @property
    def remotes(self) -> list[Any]:
        """Remote adapters in write order."""
        return list(self._remotes)

    # -------------------------------------------------------------------
    # Locality probe (RAISE-1877)
    # -------------------------------------------------------------------

    def _local_has_key(self, key: str) -> bool:
        """Does filesystem have an artifact for this key?

        Distinguishes:
          * Local-canonical keys (have a filesystem artifact; composite
            writes both arms and uses the ledger for translation)
          * Remote-native keys (no filesystem artifact; composite writes
            only to remotes, passing the key through as-is)

        A remote-native key is any identifier the filesystem does not
        recognize — typically a Jira key that predates the ledger retrofit
        or was created directly in the remote. The composite must not
        force filesystem KeyErrors on these; the user still expects the
        write to land (online) or queue (offline).
        """
        try:
            self._local.get_issue(key)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return False
        return True

    _SQLITE_FIELD_MAP: dict[str, str] = {
        "parent": "parent_jira_key",
    }
    _SQLITE_UPDATABLE: frozenset[str] = frozenset(
        {
            "summary",
            "status",
            "description",
            "labels",
            "priority",
            "assignee",
            "fix_versions",
            "custom_fields",
            "parent_local_key",
            "parent_jira_key",
        }
    )

    def _update_work_item_fields(self, key: str, changes: dict[str, Any]) -> None:
        """Best-effort update of SQLite work_items after a successful write (RAISE-16729)."""
        wi = self._wi_store.get_by_jira_key(key) or self._wi_store.get_by_local_key(key)
        if wi is None:
            return
        mapped: dict[str, Any] = {}
        for k, v in changes.items():
            col = self._SQLITE_FIELD_MAP.get(k, k)
            if col in self._SQLITE_UPDATABLE:
                mapped[col] = v
        if mapped:
            with contextlib.suppress(Exception):
                self._wi_store.update_fields(wi.id, mapped)

    def _write_through_to_local(
        self,
        key: str,
        *,
        fields: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> None:
        """Best-effort write-through to local after a remote write lands.

        Calls ``_save_item`` on the local adapter (upsert semantics):
        existing items get only non-empty fields updated; new items are
        created with available data.
        """
        save_item = getattr(self._local, "_save_item", None)
        if not callable(save_item):
            return
        merged: dict[str, Any] = {}
        if fields:
            merged.update(fields)
        if status:
            merged["status"] = status
        now = datetime.now(UTC).isoformat()
        _wi_row = self._wi_store.get_by_jira_key(
            key
        ) or self._wi_store.get_by_local_key(key)
        _stored_type = (_wi_row.type[0].upper() + _wi_row.type[1:]) if _wi_row else None
        with contextlib.suppress(Exception):
            save_item(
                BacklogItem(
                    key=key,
                    summary=merged.get("summary", ""),
                    issue_type=merged.get("issue_type", _stored_type or "Task"),
                    status=merged.get("status", ""),
                    parent=merged.get("parent"),
                    description=merged.get("description", ""),
                    labels=merged.get("labels", []),
                    priority=merged.get("priority"),
                    updated=now,
                )
            )

    def _save_local_issue_mirror(self, key: str, issue: IssueSpec) -> None:
        """Best-effort local artifact for remote-native child creation."""
        save_item = getattr(self._local, "_save_item", None)
        if not callable(save_item):
            return
        meta = issue.metadata or {}
        now = datetime.now(UTC).isoformat()
        save_item(
            BacklogItem(
                key=key,
                summary=issue.summary,
                issue_type=issue.issue_type,
                status="pending",
                parent=issue.parent or meta.get("parent_key"),
                description=issue.description,
                labels=issue.labels,
                priority=meta.get("priority"),
                created=now,
                updated=now,
            )
        )

    def _queue_remote_first_create_placeholder(
        self,
        project_key: str,
        issue: IssueSpec,
        completed_remotes: list[int] | None = None,
    ) -> IssueRef:
        """Persist intent locally when remote-native create cannot complete now."""
        placeholder_key = f"TMP-{uuid4().hex[:8].upper()}"
        self._save_local_issue_mirror(placeholder_key, issue)
        self._pending.append(
            "create_issue",
            placeholder_key,
            {"project_key": project_key, **issue.model_dump()},
            completed_remotes=completed_remotes or [],
        )
        return IssueRef(key=placeholder_key)

    def _should_create_remote_first(self, issue: IssueSpec) -> bool:
        """Use remote as canonical ID source when external adapters exist."""
        return bool(self._remotes)

    # -------------------------------------------------------------------
    # Write ops — delegate to all, remote failures → pending
    # -------------------------------------------------------------------

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Remote-first when external adapters exist; local-only otherwise.

        Remote-first: Jira provides the canonical key, local stores a mirror.
        If remote fails, a TMP-xxx placeholder is queued for retry.
        Local-only (no remotes): local adapter assigns the key directly.
        """
        self._flush_pending()
        if self._should_create_remote_first(issue):
            primary_remote_ref: IssueRef | None = None
            completed: list[int] = []
            for i, remote in enumerate(self._remotes):
                try:
                    remote_ref: IssueRef = remote.create_issue(project_key, issue)
                    if primary_remote_ref is None:
                        primary_remote_ref = remote_ref
                        self._save_local_issue_mirror(remote_ref.key, issue)
                        # RAISE-16938: seed the row from the spec we already
                        # hold — a bare self-map births a stub that every
                        # local-first read then serves as truth.
                        self._wi_store.upsert_jira_mapping(
                            remote_ref.key,
                            remote_ref.key,
                            summary=issue.summary,
                            issue_type=issue.issue_type,
                            description=issue.description,
                            labels=issue.labels,
                            parent_jira_key=issue.parent,
                        )
                    completed.append(i)
                except Exception as exc:
                    logger.warning("Remote-first create failed: %s", exc)
                    if self._server_first:
                        raise AdapterSyncError(f"Remote create failed: {exc}") from exc
                    if primary_remote_ref is not None:
                        self._pending.append(
                            "create_issue",
                            primary_remote_ref.key,
                            {
                                "project_key": project_key,
                                "__skip_ledger_update__": True,
                                **issue.model_dump(),
                            },
                            completed_remotes=completed,
                        )
                        return primary_remote_ref
                    return self._queue_remote_first_create_placeholder(
                        project_key, issue, completed_remotes=completed
                    )
            if primary_remote_ref is None:
                return self._queue_remote_first_create_placeholder(project_key, issue)
            return primary_remote_ref
        local_ref: IssueRef = self._local.create_issue(project_key, issue)
        completed: list[int] = []
        for i, remote in enumerate(self._remotes):
            try:
                remote_ref: IssueRef = remote.create_issue(project_key, issue)
                self._wi_store.upsert_jira_mapping(
                    local_ref.key,
                    remote_ref.key,
                    summary=issue.summary,
                    issue_type=issue.issue_type,
                    description=issue.description,
                    labels=issue.labels,
                    parent_jira_key=issue.parent,
                )
                completed.append(i)
                local_ref = self._maybe_promote(local_ref.key, remote_ref.key)
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                self._pending.append(
                    "create_issue",
                    local_ref.key,
                    {"project_key": project_key, **issue.model_dump()},
                    completed_remotes=completed,
                )
                logger.warning("Remote create failed: %s", exc)
                break
        return local_ref

    def _maybe_promote(self, staging_key: str, jira_key: str) -> IssueRef:
        """Call promote_key on local adapter if supported; remove ledger entry.

        Returns IssueRef with jira_key on success, staging_key on any failure.
        """
        promote = getattr(self._local, "promote_key", None)
        if promote is None:
            return IssueRef(key=staging_key)
        try:
            promote(staging_key, jira_key)
            self._wi_store.remove_jira_mapping(staging_key)
            # Self-map: jira_key → jira_key so _write_to_remotes_keyed treats it as
            # remote-native (not a local-canonical unsynced key).
            self._wi_store.upsert_jira_mapping(jira_key, jira_key)
            return IssueRef(key=jira_key)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "promote_key(%s → %s) failed: %s", staging_key, jira_key, exc
            )
            return IssueRef(key=staging_key)

    def _apply_write_outcome(
        self, ref: IssueRef, outcome: RemoteWriteOutcome
    ) -> IssueRef:
        """Stamp a RemoteWriteOutcome onto an IssueRef (RAISE-12598).

        ``remote_synced`` carries the typed landed/queued signal; the reason
        (when queued) rides along in ``metadata`` so CLI callers can render a
        specific message without a new schema field.
        """
        metadata = dict(ref.metadata)
        if outcome.reason is not None:
            metadata["remote_sync_reason"] = outcome.reason
        if outcome.error_detail is not None:
            metadata["remote_sync_error_detail"] = outcome.error_detail
        return ref.model_copy(
            update={
                "remote_synced": outcome.status == "landed",
                "metadata": metadata,
            }
        )

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update locally (when local-canonical), then best-effort on remotes."""
        self._flush_pending()
        local_known = self._local_has_key(key)
        if local_known:
            local_ref: IssueRef = self._local.update_issue(key, fields)
        else:
            local_ref = IssueRef(key=key)  # remote-native; no local artifact

        def _do_update(remote: Any, rk: str) -> None:
            remote.update_issue(rk, fields)

        outcome = self._write_to_remotes_keyed(
            "update_issue",
            key,
            {"fields": fields},
            _do_update,
            propagate_errors=self._server_first,
        )
        if outcome.status == "landed" and not local_known:
            self._write_through_to_local(key, fields=fields)
        self._update_work_item_fields(key, fields)
        return self._apply_write_outcome(local_ref, outcome)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition locally (when local-canonical), then propagate on remotes.

        Remote-native keys (no local artifact, e.g. RAISE-xxx) call the remote
        directly and propagate errors — queuing a failed transition for replay
        makes no sense because transitions are context-dependent (RAISE-4140).

        Local-canonical keys also propagate remote errors (RAISE-4186): if Jira
        rejects the transition, the local state is rolled back (best-effort) and
        the exception is re-raised so the caller sees a real failure instead of
        a false-positive success.
        """
        self._flush_pending()
        if self._local_has_key(key):
            prev_status = self._local.get_issue(key).status
            local_ref: IssueRef = self._local.transition_issue(key, status)

            def _do_transition(remote: Any, rk: str) -> None:
                remote.transition_issue(rk, status)

            try:
                outcome = self._write_to_remotes_keyed(
                    "transition_issue",
                    key,
                    {"status": status},
                    _do_transition,
                    propagate_errors=True,
                )
            except Exception:
                with contextlib.suppress(Exception):
                    self._local.transition_issue(key, prev_status)
                raise
            self._update_work_item_fields(key, {"status": status})
            return self._apply_write_outcome(local_ref, outcome)

        # Remote-native: call directly so errors propagate to the caller.
        remote_key = self._wi_store.get_jira_key(key) or key
        for remote in self._remotes:
            remote.transition_issue(remote_key, status)
        if self._server_first and self._remotes:
            actual = self._remotes[0].get_issue(remote_key)
            if actual.status.lower() != status.lower():
                raise AdapterSyncError(
                    f"Transition status mismatch: expected '{status}', "
                    f"got '{actual.status}'"
                )
        self._write_through_to_local(key, status=status)
        self._update_work_item_fields(key, {"status": status})
        return IssueRef(key=key, remote_synced=True)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Batch transition: local-canonical via filesystem, remote-native direct to remote."""
        self._flush_pending()
        local_canonical = [k for k in keys if self._local_has_key(k)]
        remote_native = [k for k in keys if not self._local_has_key(k)]

        merged: BatchResult = (
            self._local.batch_transition(local_canonical, status)
            if local_canonical
            else BatchResult()
        )

        # remote_native: pass through as-is; local_canonical: resolve via ledger
        remote_keys: list[str] = list(remote_native)
        for k in local_canonical:
            rk = self._wi_store.get_jira_key(k)
            if rk is not None:
                remote_keys.append(rk)
            else:
                self._pending.append("transition_issue", k, {"status": status})

        if not remote_keys:
            return merged

        remote_native_set = set(remote_native)
        for remote in self._remotes:
            try:
                remote_result = remote.batch_transition(remote_keys, status)
                merged = BatchResult(
                    succeeded=merged.succeeded
                    + [
                        r for r in remote_result.succeeded if r.key in remote_native_set
                    ],
                    failed=merged.failed
                    + [f for f in remote_result.failed if f.key in remote_native_set],
                )
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                self._pending.append(
                    "batch_transition",
                    ",".join(keys),
                    {"status": status},
                )
                logger.warning("Remote batch_transition failed: %s", exc)
        return merged

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Create multiple issues with per-item fault isolation."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []
        for spec in issues:
            try:
                ref = self.create_issue(spec.project, spec)
                succeeded.append(ref)
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("batch_create failed for %r: %s", spec.summary, exc)
                failed.append(FailureDetail(key=spec.summary, error=str(exc)))
        return BatchResult(succeeded=succeeded, failed=failed)

    def remove_link(self, link_id: str) -> None:
        """Remove an issue link by ID — delegates to remote only (IDs are remote-native)."""
        for remote in self._remotes:
            remote.remove_link(link_id)

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Link locally (when local-canonical), then best-effort on remotes.

        Returns True if the link was created on all remotes, False if any
        remote failed (or the key was unmapped) and the operation was queued
        for later replay.
        """
        self._flush_pending()
        if self._local_has_key(child_key) and self._local_has_key(parent_key):
            self._local.link_to_parent(child_key, parent_key)
        # Resolve remote keys: ledger first, fall back to pass-through for
        # remote-native identifiers (RAISE-1877).
        remote_child = self._wi_store.get_jira_key(child_key) or (
            child_key if not self._local_has_key(child_key) else None
        )
        remote_parent = self._wi_store.get_jira_key(parent_key) or (
            parent_key if not self._local_has_key(parent_key) else None
        )
        if remote_child and remote_parent:
            queued = False
            for remote in self._remotes:
                try:
                    remote.link_to_parent(remote_child, remote_parent)
                except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                    self._pending.append(
                        "link_to_parent",
                        child_key,
                        {"parent_key": parent_key},
                    )
                    logger.warning("Remote link_to_parent failed: %s", exc)
                    queued = True
            return not queued
        # Either side unmapped and local-canonical → queue for later
        self._pending.append("link_to_parent", child_key, {"parent_key": parent_key})
        return False

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Link locally (when local-canonical), then best-effort on remotes.

        Returns True if the link was created on all remotes, False if any
        remote failed and the operation was queued for later replay.
        """
        self._flush_pending()
        if self._local_has_key(source) and self._local_has_key(target):
            self._local.link_issues(source, target, link_type)
        remote_source = self._wi_store.get_jira_key(source) or (
            source if not self._local_has_key(source) else None
        )
        remote_target = self._wi_store.get_jira_key(target) or (
            target if not self._local_has_key(target) else None
        )
        if remote_source and remote_target:
            queued = False
            for remote in self._remotes:
                try:
                    remote.link_issues(remote_source, remote_target, link_type)
                except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                    self._pending.append(
                        "link_issues",
                        source,
                        {"target": target, "link_type": link_type},
                    )
                    logger.warning("Remote link_issues failed: %s", exc)
                    queued = True
            return not queued
        self._pending.append(
            "link_issues",
            source,
            {"target": target, "link_type": link_type},
        )
        return False

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Comment locally (when local-canonical), then best-effort on remotes."""
        self._flush_pending()
        if self._local_has_key(key):
            local_ref: CommentRef = self._local.add_comment(key, body)
        else:
            local_ref = CommentRef(id="")  # remote-native

        def _do_comment(remote: Any, rk: str) -> None:
            remote.add_comment(rk, body)

        self._write_to_remotes_keyed("add_comment", key, {"body": body}, _do_comment)
        return local_ref

    # -------------------------------------------------------------------
    # Read ops — local only
    # -------------------------------------------------------------------

    def _reconcile_local_mirror(
        self, local_key: str, remote_key: str, remote: Any
    ) -> IssueDetail:
        """Pull the full remote record and fold it into the local mirror.

        One-time reconciliation: after this, the local record's status is no
        longer "pending", so it will not fire again for the same record
        (D1-compatible — see s1700.3-design.md D1 + RAISE-11897 analysis).
        Truly external writes on already-confirmed records are intentionally
        NOT covered here; that remains `rai backlog reconcile`'s job.

        Within this reconciled field set, the remote read-back is treated as
        authoritative even when it returns None/empty (e.g. priority=None,
        labels=[]) — bounded to records composite itself just created
        remote-first, where remote is canonical by design (D1), not silent
        loss of user-authored data (AR Q1, RAISE-11897).
        """
        remote_detail = remote.get_issue(remote_key)
        fields = {
            "status": remote_detail.status,
            "summary": remote_detail.summary,
            "description": remote_detail.description,
            "labels": remote_detail.labels,
            "priority": remote_detail.priority,
            "assignee": remote_detail.assignee,
            "parent": remote_detail.parent_key,  # BacklogItem attr is "parent", not "parent_key"
            "fix_versions": remote_detail.fix_versions,
        }
        self._local.update_issue(local_key, fields)
        return remote_detail

    def get_issue(self, key: str) -> IssueDetail:
        """Read from local; fallback to remote for remote-native keys."""
        try:
            detail: IssueDetail = self._local.get_issue(key)
        except (KeyError, FileNotFoundError, ValidationError):
            # RAISE-14593: ValidationError means the local YAML mirror is corrupt
            # (or absent). Degrade to remote instead of hard-crashing the read.
            if self._remotes:
                logger.debug(
                    "get_issue fallback to remote for remote-native key %r", key
                )
                return self._remotes[0].get_issue(key)  # type: ignore[no-any-return]
            raise
        if detail.status == "pending" and self._remotes:
            with contextlib.suppress(Exception):
                remote_detail = self._reconcile_local_mirror(key, key, self._remotes[0])
                return remote_detail.model_copy(update={"key": detail.key})
        return detail

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Try local first; fall back to remote for remote-native keys not in filesystem."""
        result = self._local.get_comments(
            key, limit=limit, offset=offset, fetch_all=fetch_all
        )
        if not result and self._remotes:
            return self._remotes[0].get_comments(
                key, limit=limit, offset=offset, fetch_all=fetch_all
            )  # type: ignore[no-any-return]
        return result

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        """Search local first; fall back to remote if local returns no results."""
        result = self._local.search(
            query, limit=limit, offset=offset, fetch_all=fetch_all
        )
        if not result and self._remotes:
            logger.debug("search fallback to remote for query %r", query)
            return self._remotes[0].search(
                query, limit=limit, offset=offset, fetch_all=fetch_all
            )  # type: ignore[no-any-return]
        return result

    def health(self) -> AdapterHealth:
        """Healthy if local (filesystem) is healthy."""
        return self._local.health()  # type: ignore[no-any-return]

    # -------------------------------------------------------------------
    # Discovery — delegate to primary remote (S2503.16)
    # -------------------------------------------------------------------

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].discover_fields(project_key)  # type: ignore[no-any-return]

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].discover_statuses(project_key, issue_type=issue_type)  # type: ignore[no-any-return]

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].discover_link_types()  # type: ignore[no-any-return]

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].discover_issue_types(project_key)  # type: ignore[no-any-return]

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].discover_named_fields(
            names=names, issue_type=issue_type, project_key=project_key
        )  # type: ignore[no-any-return]

    # ── Project versions / fixVersions — delegate to primary remote ──

    def _remote_version_op(self, operation: str) -> Callable[..., Any]:
        """Return a supported project-version operation from the primary remote."""
        if not self._remotes:
            raise NotImplementedError("No remote adapter supports project versions")
        method = getattr(self._remotes[0], operation, None)
        if not callable(method):
            raise NotImplementedError(
                f"Primary remote adapter does not support {operation}()"
            )
        return method

    def list_versions(self, project_key: str) -> list[ProjectVersion]:
        """Delegate project version discovery to the primary remote."""
        return self._remote_version_op("list_versions")(project_key)  # type: ignore[no-any-return]

    def create_version(self, project_key: str, name: str) -> ProjectVersion:
        """Delegate project version creation to the primary remote."""
        return self._remote_version_op("create_version")(project_key, name)  # type: ignore[no-any-return]

    # ── Attachments (S2503.7) ────────────────────────────────────────

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Delegate to primary remote; raise if no remotes."""
        if not self._remotes:
            raise RuntimeError("No remote adapters available for attach()")
        return self._remotes[0].attach(key, path, mime_type)  # type: ignore[no-any-return]

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Delegate to primary remote; return [] if no remotes."""
        if not self._remotes:
            return []
        return self._remotes[0].get_attachments(key)  # type: ignore[no-any-return]

    # ── Sprint (Jira-specific) — delegate to primary remote ──────────

    def get_sprints(self, project_key: str, state: str | None = None) -> list[Any]:
        """Delegate to primary remote; raise if no remotes."""
        if not self._remotes:
            raise RuntimeError("No remote adapters available for get_sprints()")
        return self._remotes[0].get_sprints(project_key, state=state)  # type: ignore[no-any-return]

    def assign_to_sprint(self, issue_key: str, sprint_id: int) -> None:
        """Delegate to primary remote; raise if no remotes."""
        if not self._remotes:
            raise RuntimeError("No remote adapters available for assign_to_sprint()")
        self._remotes[0].assign_to_sprint(issue_key, sprint_id)  # type: ignore[no-any-return]

    def download_attachment(self, attachment_id: str) -> bytes:
        """Delegate to primary remote; raise if no remotes."""
        if not self._remotes:
            raise RuntimeError("No remote adapters available for download_attachment()")
        return self._remotes[0].download_attachment(attachment_id)  # type: ignore[no-any-return]

    # -------------------------------------------------------------------
    # Drain — replay queued pending ops (S1700.7.1)
    # -------------------------------------------------------------------

    def _flush_pending(self) -> None:
        """Attempt to replay pending ops against remotes. Best-effort, never raises.

        Called at the top of every write method. Mirrors
        ``CompositeDocTarget._flush_pending`` (S1700.6). Successful replays
        are marked done; failures increment attempt_count and are moved to
        dead-letter after MAX_RETRIES consecutive failures.
        """
        dead_letter_moved = 0
        try:
            for op in list(self._pending.iter()):
                try:
                    if self._replay_one(op):
                        self._pending.mark_done(op.id)
                    else:
                        self._pending.update_last_error(
                            op.id,
                            "replay returned False (ledger unmapped or remote unreachable)",
                        )
                        count = self._pending.increment_attempt(op.id)
                        if count >= MAX_RETRIES:
                            self._pending.move_to_dead_letter(op.id)
                            dead_letter_moved += 1
                except Exception as exc:  # noqa: BLE001 — replay failure = keep queued
                    logger.debug(
                        "Pending op %s (%s) replay raised: %s", op.id, op.op, exc
                    )
                    self._pending.update_last_error(op.id, str(exc)[:200])
                    count = self._pending.increment_attempt(op.id)
                    if count >= MAX_RETRIES:
                        self._pending.move_to_dead_letter(op.id)
                        dead_letter_moved += 1
        except Exception:
            logger.exception("Pending ops flush failed")
        if dead_letter_moved:
            logger.warning(
                "%d op(s) moved to dead-letter"
                " (run `rai backlog pending-ops list --dead` to inspect)",
                dead_letter_moved,
            )

    def _replay_one(self, op: PendingOp) -> bool:
        """Dispatch a single pending op to its replay handler. Returns True if drained."""
        dispatch: dict[str, Callable[[PendingOp], bool]] = {
            "create_issue": self._replay_create_issue,
            "update_issue": self._replay_update_issue,
            "transition_issue": self._replay_transition_issue,
            "batch_transition": self._replay_batch_transition,
            "link_to_parent": self._replay_link_to_parent,
            "link_issues": self._replay_link_issues,
            "add_comment": self._replay_add_comment,
        }
        handler = dispatch.get(op.op)
        if handler is None:
            logger.warning("Unknown pending op type %r; keeping queued", op.op)
            return False
        return handler(op)

    def _replay_create_issue(self, op: PendingOp) -> bool:
        """Replay a queued create_issue on every remote; update ledger on success."""
        args = dict(op.args)
        skip_ledger_update = bool(args.pop("__skip_ledger_update__", False))
        project_key = args.pop("project_key", None)
        if project_key is None:
            logger.warning("Pending create_issue %s missing project_key", op.id)
            return False
        try:
            spec = IssueSpec.model_validate(args)
        except Exception as exc:  # noqa: BLE001 — bad payload = keep queued
            logger.warning("Pending create_issue %s payload invalid: %s", op.id, exc)
            return False
        all_ok = True
        completed = list(op.completed_remotes)
        for i, remote in enumerate(self._remotes):
            if i in completed:
                continue
            try:
                remote_ref: IssueRef = remote.create_issue(project_key, spec)
                if not skip_ledger_update:
                    self._wi_store.upsert_jira_mapping(op.key, remote_ref.key)
                completed.append(i)
                promoted_ref = self._maybe_promote(op.key, remote_ref.key)
                with contextlib.suppress(Exception):
                    self._reconcile_local_mirror(
                        promoted_ref.key, remote_ref.key, remote
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Replay create_issue %s failed on remote[%d]: %s", op.key, i, exc
                )
                all_ok = False
        if completed != list(op.completed_remotes):
            self._pending.update_completed(op.id, completed)
        return all_ok

    def _replay_update_issue(self, op: PendingOp) -> bool:
        fields = op.args.get("fields")
        if not isinstance(fields, dict):
            return False
        return self._replay_keyed(
            op, lambda remote, rk: remote.update_issue(rk, fields)
        )

    def _replay_transition_issue(self, op: PendingOp) -> bool:
        status = op.args.get("status")
        if not isinstance(status, str):
            return False
        return self._replay_keyed(
            op, lambda remote, rk: remote.transition_issue(rk, status)
        )

    def _replay_batch_transition(self, op: PendingOp) -> bool:
        """Replay batch_transition. Requires ALL keys to resolve (QR-C2).

        Partial resolution would silently drop unresolvable keys if we
        marked the op done — the unresolved transitions would never reach
        the remote. Keep the op queued until every key has a ledger entry;
        the next drain will retry.
        """
        status = op.args.get("status")
        if not isinstance(status, str):
            return False
        local_keys = op.key.split(",") if op.key else []
        if not local_keys:
            return False
        # remote-native keys (not in ledger, not local) resolve as pass-through
        resolved = [
            self._wi_store.get_jira_key(k)
            or (k if not self._local_has_key(k) else None)
            for k in local_keys
        ]
        if any(rk is None for rk in resolved):
            # local-canonical key still unmapped — wait for ledger entry
            return False
        all_ok = True
        completed = list(op.completed_remotes)
        for i, remote in enumerate(self._remotes):
            if i in completed:
                continue
            try:
                remote.batch_transition(resolved, status)  # type: ignore[arg-type]
                completed.append(i)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Replay batch_transition %s failed on remote[%d]: %s",
                    op.key,
                    i,
                    exc,
                )
                all_ok = False
        if completed != list(op.completed_remotes):
            self._pending.update_completed(op.id, completed)
        return all_ok

    def _replay_link_to_parent(self, op: PendingOp) -> bool:
        parent_local = op.args.get("parent_key")
        if not isinstance(parent_local, str):
            return False
        remote_child = self._wi_store.get_jira_key(op.key)
        remote_parent = self._wi_store.get_jira_key(parent_local)
        if not (remote_child and remote_parent):
            return False
        all_ok = True
        completed = list(op.completed_remotes)
        for i, remote in enumerate(self._remotes):
            if i in completed:
                continue
            try:
                remote.link_to_parent(remote_child, remote_parent)
                completed.append(i)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Replay link_to_parent %s failed on remote[%d]: %s", op.key, i, exc
                )
                all_ok = False
        if completed != list(op.completed_remotes):
            self._pending.update_completed(op.id, completed)
        return all_ok

    def _replay_link_issues(self, op: PendingOp) -> bool:
        target_local = op.args.get("target")
        link_type = op.args.get("link_type")
        if not (isinstance(target_local, str) and isinstance(link_type, str)):
            return False
        remote_source = self._wi_store.get_jira_key(op.key)
        remote_target = self._wi_store.get_jira_key(target_local)
        if not (remote_source and remote_target):
            return False
        all_ok = True
        completed = list(op.completed_remotes)
        for i, remote in enumerate(self._remotes):
            if i in completed:
                continue
            try:
                remote.link_issues(remote_source, remote_target, link_type)
                completed.append(i)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Replay link_issues %s failed on remote[%d]: %s", op.key, i, exc
                )
                all_ok = False
        if completed != list(op.completed_remotes):
            self._pending.update_completed(op.id, completed)
        return all_ok

    def _replay_add_comment(self, op: PendingOp) -> bool:
        """Replay an add_comment op.

        **Retry-safety caveat (QR-C1):** ``add_comment`` is NOT idempotent on
        Jira — each call creates a new comment. Under the current single-remote
        reality this is safe: if the only remote succeeds, mark_done removes
        the op; if it fails, no comment was created so retry is fine.

        When a second PM remote is added (RAISE-1859 follow-up), per-remote
        bookkeeping will be needed to avoid duplicate comments when one remote
        accepts and another fails. Do NOT add a non-idempotent op to
        ``_replay_keyed`` until that bookkeeping exists.
        """
        body = op.args.get("body")
        if not isinstance(body, str):
            return False
        return self._replay_keyed(op, lambda remote, rk: remote.add_comment(rk, body))

    def _replay_keyed(
        self,
        op: PendingOp,
        action: _RemoteAction,
    ) -> bool:
        """Shared replay path: resolve via ledger, call action on each remote.

        **Contract:** ``action`` MUST be idempotent on each remote. Current
        callers (update_issue, transition_issue, add_comment) satisfy this
        under single-remote reality. For multi-remote + non-idempotent ops
        (notably add_comment), per-remote bookkeeping is required — see
        QR-C1 note on ``_replay_add_comment``.

        Key resolution (RAISE-1877): ledger first; if unmapped, check
        filesystem — if filesystem does not know the key, treat it as
        remote-native (key IS the remote identifier) and pass through.
        """
        remote_key = self._wi_store.get_jira_key(op.key)
        if remote_key is None:
            if self._local_has_key(op.key):
                # Local-canonical but not yet synced — keep queued until the
                # key gets mapped (e.g. via reconcile)
                return False
            # Remote-native — pass through
            remote_key = op.key
        if not self._remotes:
            return False  # no remote arm to drain to
        all_ok = True
        completed = list(op.completed_remotes)
        for i, remote in enumerate(self._remotes):
            if i in completed:
                continue
            try:
                action(remote, remote_key)
                completed.append(i)
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    "Replay %s %s failed on remote[%d]: %s", op.op, op.key, i, exc
                )
                all_ok = False
        if completed != list(op.completed_remotes):
            self._pending.update_completed(op.id, completed)
        return all_ok

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    def _write_to_remotes_keyed(
        self,
        op_name: str,
        local_key: str,
        args: dict[str, Any],
        action: _RemoteAction,
        *,
        propagate_errors: bool = False,
    ) -> RemoteWriteOutcome:
        """Execute a keyed write op on all remotes using ledger for key translation.

        ``args`` carries the op's replayable payload (e.g. ``{"fields": ...}``
        for update_issue, ``{"status": ...}`` for transition_issue,
        ``{"body": ...}`` for add_comment). It is persisted into the pending
        queue on failure so that a later ``_flush_pending`` pass can replay
        the op with full fidelity.

        Key resolution (RAISE-1877):
          * ledger has mapping → use translated remote key
          * no ledger mapping and filesystem knows the key → queue for
            later migration (local-canonical, unmapped)
          * no ledger mapping and filesystem does NOT know the key →
            pass through (remote-native; the key IS the remote identifier)

        Remote reachability (RAISE-1877): if no remote arms are configured
        (e.g. jira.yaml absent at composite construction), the op is queued
        for later replay when a remote becomes available — never silently
        dropped.

        Returns a :class:`RemoteWriteOutcome` (RAISE-12598) so callers can
        distinguish "landed on the remote" from "queued locally" instead of
        the previous implicit ``None`` that erased the signal at this choke
        point. Every return path below sets the outcome explicitly.
        """
        if not self._remotes:
            # No remote arms in the composite — queue for future drain
            self._pending.append(op_name, local_key, args)
            return RemoteWriteOutcome("queued", "no_remotes")
        remote_key = self._wi_store.get_jira_key(local_key)
        if remote_key is None:
            if self._local_has_key(local_key):
                if _JIRA_KEY_RE.match(local_key):
                    # Auto-heal: local key IS a remote key (migrated/imported
                    # item with NULL jira_key). Self-map and pass through.
                    remote_key = local_key
                    self._wi_store.upsert_jira_mapping(local_key, local_key)
                else:
                    # Local-canonical key not yet synced to remote — queue it
                    self._pending.append(op_name, local_key, args)
                    return RemoteWriteOutcome("queued", "unmapped")
            else:
                # Remote-native key — pass through
                remote_key = local_key
        completed: list[int] = []
        for i, remote in enumerate(self._remotes):
            try:
                action(remote, remote_key)
                completed.append(i)
            except Exception as exc:
                logger.warning("Remote %s failed: %s", op_name, exc)
                if propagate_errors:
                    raise
                self._pending.append(
                    op_name,
                    local_key,
                    args,
                    completed_remotes=completed,
                )
                return RemoteWriteOutcome(
                    "queued", "remote_error", error_detail=str(exc)
                )
        return RemoteWriteOutcome("landed")

    # -------------------------------------------------------------------
    # SyncVerifiable implementation (S-AQG.4)
    # -------------------------------------------------------------------

    @property
    def is_server_first(self) -> bool:
        """True when running in connected mode (RAISE_SERVER_URL + RAISE_API_KEY set)."""
        return self._server_first

    def verify_sync(self, keys: frozenset[str] | None = None) -> SyncReport:
        """Verify ledger entries exist on the remote via GET requests.

        keys=None: verify all ledger entries (--all mode, counts global).
        keys: verify only entries where local_key or remote_key is in keys,
              counts scoped to matching op.key values (C2).
        """
        ledger = self._wi_store.all_jira_mappings()
        if keys is not None:
            ledger = {lk: rk for lk, rk in ledger.items() if lk in keys or rk in keys}

        remote = self._remotes[0] if self._remotes else None
        entries: list[SyncEntry] = []
        for local_key, remote_key in ledger.items():
            if remote is None:
                entries.append(
                    SyncEntry(
                        local_key=local_key,
                        remote_key=remote_key,
                        exists=False,
                        detail="no remote configured",
                    )
                )
                continue
            try:
                detail = remote.get_issue(remote_key)
                entries.append(
                    SyncEntry(
                        local_key=local_key,
                        remote_key=remote_key,
                        exists=True,
                        detail=f"status={detail.status}",
                    )
                )
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                entries.append(
                    SyncEntry(
                        local_key=local_key,
                        remote_key=remote_key,
                        exists=False,
                        detail=str(exc)[:200],
                    )
                )

        pending = self._count_ops(self._pending.iter(), keys)
        dead = self._count_ops(self._pending.iter_dead_letter(), keys)

        return SyncReport(
            domain="backlog",
            entries=tuple(entries),
            pending_count=pending,
            dead_letter_count=dead,
        )

    @staticmethod
    def _count_ops(ops: Any, keys: frozenset[str] | None) -> int:
        """Count ops; scoped by op.key when keys given, global when None."""
        if keys is None:
            return sum(1 for _ in ops)
        return sum(1 for op in ops if op.key in keys)
