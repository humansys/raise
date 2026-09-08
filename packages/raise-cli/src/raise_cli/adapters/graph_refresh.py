"""GraphRefreshAdapter — refreshes the backlog items cartridge after mutations.

Wraps any ProjectManagementAdapter. After a successful create_issue/update_issue/
transition_issue, refreshes the single corresponding node in the backlog items
cartridge (`.raise/cartridges/backlog-{org}-{project}/instances/items.json`).

Best-effort by design: refresh failures log a warning and never block the
mutation (the mutation result from the delegate is always returned unchanged).

Mirrors the LedgerAwareAdapter pattern (plain class, explicit delegation, no
inheritance, no `__getattr__` magic — see design DS-1).

Story: S16397.3 (RAISE-16403) | Epic: RAISE-16397
Design: work/stories/s16397.3-graph-refresh-adapter/design.md
"""

from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.models import (
    AdapterHealth,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    CustomField,
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
from raise_cli.adapters.protocols import SyncVerifiable
from raise_cli.config.paths import checkout_scope_id
from raise_cli.storage.connection import get_project_db_path, get_project_id
from raise_core.cartridges.backlog_items import build_backlog_item_node

logger = logging.getLogger(__name__)


def _warn_refresh_failed(key: str, exc: Exception, *, store: str = "graph") -> None:
    """Surface a swallowed refresh failure on stderr (RAISE-16938, D4).

    The refresh is best-effort by design (DS-5) and must never block the
    mutation — but routing the only signal to `logger.warning` made silent
    divergence indistinguishable from success. RAISE-16938 sat with zero graph
    nodes in any checkout and nothing ever said so. The mutation still
    succeeds; this only makes the degraded outcome legible.
    """
    print(
        f"\n⚠ GRAPH_REFRESH_FAILED\n"
        f"  Item: {key}\n"
        f"  Store: {store}\n"
        f"  Reason: {type(exc).__name__}: {exc}\n"
        f"  Effect: the write to the tracker succeeded; the local graph is\n"
        f"          now stale for this item.\n"
        f"  Action: run `rai graph build` to reconcile.",
        file=sys.stderr,
    )


def _find_cartridge(project_root: Path, key: str) -> Path | None:
    """Locate the backlog-items cartridge dir owning `key` (DS-3).

    Globs `{project_root}/.raise/cartridges/backlog-*/CARTRIDGE.yaml`, parses
    `project_id`, and matches it (case-insensitively) against the issue key's
    project prefix. Returns None (logging DEBUG) if no cartridges dir exists,
    no manifest matches, or a manifest is unparseable — the graph is simply
    not initialized yet for that project (S16397.4's `rai backlog sync`
    bootstraps it); this is never an error condition for the hot path.
    """
    cartridges_root = project_root / ".raise" / "cartridges"
    if not cartridges_root.is_dir():
        logger.debug("No cartridges dir at %s; skipping graph refresh", cartridges_root)
        return None

    prefix = key.split("-")[0].upper()
    for manifest_path in sorted(cartridges_root.glob("backlog-*/CARTRIDGE.yaml")):
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError):
            logger.debug(
                "Unparseable cartridge manifest %s; skipping",
                manifest_path,
                exc_info=True,
            )
            continue
        project_id = manifest.get("project_id")
        if isinstance(project_id, str) and project_id.upper() == prefix:
            return manifest_path.parent

    logger.debug(
        "No backlog-items cartridge matches key %s; skipping graph refresh", key
    )
    return None


def _upsert_items_json(items_path: Path, node: dict[str, Any], key: str) -> None:
    """Upsert `node` into `items_path` by key, atomically (DS-5 step 3).

    Any existing node whose `metadata.key == key` is removed first (a
    type change moves the node id, e.g. `backlog.task.X` -> `backlog.story.X`)
    before the new node is appended. Missing file is treated as an empty list.
    Written via a uniquely-named temp file + `os.replace` to prevent torn
    writes AND to survive concurrent refreshes: a shared fixed temp name
    (e.g. `items.json.tmp`) would let two concurrent writers interleave on
    the same temp file before either calls `os.replace` (quality review F2).
    """
    if items_path.exists():
        nodes: list[dict[str, Any]] = json.loads(items_path.read_text(encoding="utf-8"))
    else:
        nodes = []

    # Match on both field names: a cartridge written before the jira_key→key
    # rename (RAISE-16940) still carries `jira_key`, and matching only the new
    # name would leave the stale entry behind and append a duplicate.
    def _node_key(n: dict[str, Any]) -> object:
        meta = n.get("metadata", {})
        return meta.get("key") or meta.get("jira_key")

    nodes = [n for n in nodes if _node_key(n) != key]
    nodes.append(node)

    items_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=items_path.parent, prefix=items_path.name + ".", suffix=".tmp"
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(nodes, indent=2, ensure_ascii=False))
        os.replace(tmp_path, items_path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


class GraphRefreshAdapter:
    """Transparent wrapper: refreshes the backlog items cartridge after mutations.

    Best-effort — refresh failures log a warning and never block the mutation.
    """

    def __init__(self, delegate: Any, project_root: Path) -> None:
        self._delegate = delegate
        self._project_root = project_root
        # Gemba finding beyond design.md §3.1: gate-sync does
        # `isinstance(resolve_pm_adapter(...), SyncVerifiable)` directly on
        # the result. runtime_checkable Protocol isinstance uses
        # inspect.getattr_static, which does NOT invoke descriptors — so a
        # `@property is_server_first` defined unconditionally on this class
        # would make isinstance() always True regardless of delegate support
        # (verified empirically). Snapshotting as plain instance attributes
        # here, only when the delegate is actually SyncVerifiable, makes
        # both isinstance() and attribute access correctly reflect delegate
        # capability (no `__getattr__` magic — DS-1).
        if isinstance(delegate, SyncVerifiable):
            self.is_server_first = delegate.is_server_first
            self.verify_sync = delegate.verify_sync

    @property
    def delegate(self) -> Any:
        """Wrapped delegate adapter (parity with LedgerAwareAdapter.remote)."""
        return self._delegate

    # -- Intercepted mutations (real protocol signatures) --------------------

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create on delegate, then refresh the cartridge node from the result key."""
        ref = self._delegate.create_issue(project_key, issue)
        self._refresh_node(ref.key)
        return ref  # type: ignore[no-any-return]

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Update on delegate, then refresh the cartridge node from the result key."""
        ref = self._delegate.update_issue(key, fields)
        self._refresh_node(ref.key or key)
        return ref  # type: ignore[no-any-return]

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Transition on delegate, then refresh the cartridge node from the result key."""
        ref = self._delegate.transition_issue(key, status)
        self._refresh_node(ref.key or key)
        return ref  # type: ignore[no-any-return]

    # -- Intercepted batch ops (RAISE-16438) ------------------------------------

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Transition on delegate, then refresh each succeeded key."""
        result: BatchResult = self._delegate.batch_transition(keys, status)
        for ref in result.succeeded:
            self._refresh_node(ref.key)
        return result

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Create on delegate, then refresh each succeeded key (RAISE-16938).

        Was a pass-through ("deferred to S16397.6"), which left every
        batch-created issue absent from the graph until the next full
        `rai graph build` — while single `create_issue` refreshed immediately.
        Mirrors `batch_transition`.
        """
        result: BatchResult = self._delegate.batch_create(issues)
        for ref in result.succeeded:
            self._refresh_node(ref.key)
        return result

    # -- Pass-through: relationships -----------------------------------------

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Link on delegate, then refresh the child node (RAISE-16938).

        `parent` is part of the node: `build_backlog_item_node` writes it into
        both `metadata.parent` and `content`. Leaving this a pass-through meant
        a reparented issue kept advertising its old parent until the next full
        build. Only the child is refreshed — the parent's own node carries no
        list of children.

        The `child_of` EDGE is deliberately not written here: edges are
        checkout-scoped by ADR-145 D5 ("no puede existir una arista con
        checkout_id = ''") while backlog nodes are repo-wide, so a hot-path
        edge write would cross partitions. Edge materialisation stays with
        `rai graph build`.
        """
        result: bool = self._delegate.link_to_parent(child_key, parent_key)
        self._refresh_node(child_key)
        return result

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Link on delegate, then refresh source and target nodes (RAISE-16438)."""
        result: bool = self._delegate.link_issues(source, target, link_type)
        self._refresh_node(source)
        self._refresh_node(target)
        return result

    def remove_link(self, link_id: str) -> None:
        """Delegate untouched — `link_id` alone cannot be resolved to issues.

        The adapter surface exposes no link_id -> (source, target) lookup, so
        there is no key to refresh. Deliberate gap, not an oversight: link
        removal is picked up by the next `rai graph build`.
        """
        self._delegate.remove_link(link_id)

    # -- Pass-through: comments -----------------------------------------------

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Delegate untouched — comments are not part of the node.

        `build_backlog_item_node` derives content and metadata from
        key/status/type/summary/priority/labels/parent/assignee only, so a
        comment cannot change the node. Refreshing here would be a wasted
        round-trip.
        """
        return self._delegate.add_comment(key, body)  # type: ignore[no-any-return]

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Delegate untouched."""
        return self._delegate.get_comments(  # type: ignore[no-any-return]
            key, limit=limit, offset=offset, fetch_all=fetch_all
        )

    # -- Pass-through: read ops -------------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Delegate untouched."""
        return self._delegate.get_issue(key)  # type: ignore[no-any-return]

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        """Delegate untouched."""
        return self._delegate.search(  # type: ignore[no-any-return]
            query, limit=limit, offset=offset, fetch_all=fetch_all
        )

    def health(self) -> AdapterHealth:
        """Delegate untouched."""
        return self._delegate.health()  # type: ignore[no-any-return]

    # -- Pass-through: discovery -------------------------------------------------

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Delegate untouched."""
        return self._delegate.discover_fields(project_key)  # type: ignore[no-any-return]

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Delegate untouched."""
        return self._delegate.discover_statuses(project_key, issue_type=issue_type)  # type: ignore[no-any-return]

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Delegate untouched."""
        return self._delegate.discover_link_types()  # type: ignore[no-any-return]

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Delegate untouched."""
        return self._delegate.discover_issue_types(project_key)  # type: ignore[no-any-return]

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        """Delegate untouched."""
        return self._delegate.discover_named_fields(  # type: ignore[no-any-return]
            names, issue_type, project_key=project_key
        )

    # -- Pass-through: attachments (S2503.7) -------------------------------------

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Delegate untouched."""
        return self._delegate.attach(key, path, mime_type=mime_type)  # type: ignore[no-any-return]

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Delegate untouched."""
        return self._delegate.get_attachments(key)  # type: ignore[no-any-return]

    def download_attachment(self, attachment_id: str) -> bytes:
        """Delegate untouched."""
        return self._delegate.download_attachment(attachment_id)  # type: ignore[no-any-return]

    # -- Optional capabilities (getattr-guard, ledger pattern §1.4) --------------

    def _delegate_op(self, operation: str) -> Callable[..., Any]:
        """Return a supported optional operation from the wrapped delegate."""
        method = getattr(self._delegate, operation, None)
        if not callable(method):
            raise NotImplementedError(
                f"Wrapped delegate adapter does not support {operation}()"
            )
        return method

    def list_versions(self, project_key: str) -> list[ProjectVersion]:
        """Delegate to wrapped adapter if it supports project versions."""
        return self._delegate_op("list_versions")(project_key)  # type: ignore[no-any-return]

    def create_version(self, project_key: str, name: str) -> ProjectVersion:
        """Delegate to wrapped adapter if it supports project versions."""
        return self._delegate_op("create_version")(project_key, name)  # type: ignore[no-any-return]

    def get_sprints(self, project_key: str, state: str | None = None) -> list[Any]:
        """Delegate to wrapped adapter if it supports sprints (Jira-specific)."""
        return self._delegate_op("get_sprints")(project_key, state=state)  # type: ignore[no-any-return]

    def assign_to_sprint(self, issue_key: str, sprint_id: int) -> None:
        """Delegate to wrapped adapter if it supports sprints (Jira-specific)."""
        self._delegate_op("assign_to_sprint")(issue_key, sprint_id)

    # SyncVerifiable (is_server_first, verify_sync) is forwarded conditionally
    # in __init__ (see comment there) rather than as unconditional
    # methods/properties here — runtime_checkable Protocol isinstance() uses
    # inspect.getattr_static, which does not invoke descriptors, so a
    # `@property` defined here would make isinstance() always True regardless
    # of delegate support (gemba finding beyond design.md §3.1).

    # -- Graph refresh (best-effort, DS-5) ---------------------------------------

    def _refresh_node(self, key: str) -> None:
        """Refresh the single backlog-items cartridge node for `key` (DS-5).

        Best-effort: any failure (missing cartridge aside — that's a normal
        skip, not a failure) is caught, logged as a warning, and swallowed —
        the mutation result from the delegate is never altered or blocked.
        """
        try:
            cartridge_dir = self._find_cartridge(key)
            if cartridge_dir is None:
                return
            detail = self._delegate.get_issue(key)
            node = build_backlog_item_node(detail, cartridge_name=cartridge_dir.name)
            _upsert_items_json(cartridge_dir / "instances" / "items.json", node, key)
            self._ingest_to_sqlite(node)
            # RAISE-16901: also write to the shared work_items store so all
            # worktrees sharing this RAI_HOME see the mutation immediately.
            self._upsert_to_work_items(detail)
        except Exception as exc:  # noqa: BLE001 — best-effort by design (DS-5)
            logger.warning(
                "Graph refresh failed for %s (mutation unaffected)", key, exc_info=True
            )
            _warn_refresh_failed(key, exc)

    def _ingest_to_sqlite(self, node: dict[str, Any]) -> None:
        """Ingest a single node into the SQLite graph backend (RAISE-16443).

        Best-effort: failures are logged and swallowed so the hot-path
        mutation is never blocked. Skips silently when the DB doesn't exist
        (graph not yet built).
        """
        try:
            db_path = get_project_db_path(self._project_root)
            if not db_path.exists():
                # Normal state, not a failure: the graph has never been built
                # for this project. Logged so a silent no-op is still traceable.
                logger.debug(
                    "No graph DB at %s; skipping SQLite ingest for %s",
                    db_path,
                    node.get("id", "?"),
                )
                return
            from raise_cli.graph.backends.sqlite import (
                SQLiteGraphBackend,
            )
            from raise_core.graph.engine import Graph
            from raise_core.graph.models import GraphNode

            graph_node = GraphNode(**node)

            mini_graph = Graph()
            mini_graph.add_concept(graph_node)
            backend = SQLiteGraphBackend(
                project_id=get_project_id(self._project_root),
                db_path=db_path,
                checkout_id=checkout_scope_id(self._project_root),
            )
            backlog_key = node.get("metadata", {}).get("key")
            if backlog_key:
                backend.replace_node_by_backlog_key(str(backlog_key), mini_graph)
            else:
                backend.upsert_nodes(mini_graph)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "SQLite ingest failed for node %s (items.json unaffected)",
                node.get("id", "?"),
                exc_info=True,
            )
            _warn_refresh_failed(str(node.get("id", "?")), exc, store="graph_nodes")

    def _upsert_to_work_items(self, detail: IssueDetail) -> None:
        """Write the mutated issue into the shared work_items store (RAISE-16901).

        Best-effort: failures are logged at DEBUG and swallowed so the
        hot-path mutation is never blocked.  The shared store (~/.rai/raise.db)
        is worktree-agnostic, so every worktree that next calls load_cartridges
        will regenerate items.json from an up-to-date DB.
        """
        try:
            from raise_cli.storage.work_items import WorkItemStore

            store = WorkItemStore(self._project_root)
            store.upsert_jira_mapping(
                local_key=detail.key,
                jira_key=detail.key,
                summary=detail.summary,
                status=detail.status,
                issue_type=detail.issue_type,
                priority=detail.priority,
                labels=list(detail.labels),
                assignee=detail.assignee,
                fix_versions=list(detail.fix_versions),
                parent_jira_key=detail.parent_key,
            )
        except Exception:  # noqa: BLE001 — best-effort, must not block mutation
            logger.debug(
                "work_items upsert failed for %s (mutation unaffected)",
                detail.key,
                exc_info=True,
            )

    def _find_cartridge(self, key: str) -> Path | None:
        """Instance-bound convenience wrapper around the module-level finder."""
        return _find_cartridge(self._project_root, key)
