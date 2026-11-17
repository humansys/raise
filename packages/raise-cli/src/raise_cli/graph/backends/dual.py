"""Dual-write graph backend — local + remote with best-effort sync.

Writes to both FilesystemGraphBackend (local, always succeeds) and
ApiGraphBackend (remote, best-effort). Loads from local only.

Architecture: ADR-036 (KnowledgeGraphBackend)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import (
    GraphBackendMetadata,
    KnowledgeGraphBackend,
)
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

__all__ = ["DualWriteBackend", "REMOTE_SYNC_NODE_TYPES"]

REMOTE_SYNC_NODE_TYPES: frozenset[str] = frozenset(
    {
        "pattern",
        "decision",
        "guardrail",
        "term",
        "principle",
        "module",
        "bounded_context",
        "layer",
        "epic",
        "story",
        "skill",
        "requirement",
        "outcome",
        "project",
        "initiative",
        "release",
        "artifact",
        "document",
        # Cartridge node types (E-KC.3 — ADR-089)
        "knowledge",
        "concept",
        "workflow",
        "command",
        "practice",
        "event",
        "symptom",
        # Cartridge-originated custom types
        "governance",
        "architecture",
        # Code structure (symbols + components form cluster edges)
        "symbol",
        "component",
        # Backlog cartridge types (RAISE-10133)
        "backlog.custom_field",
        "backlog.business_rule",
        "backlog.workflow_state",
        "backlog.issue_type",
        # Backlog issue-instance types — any backlog.* not already listed
        # is caught by prefix match in _filter_for_remote (RAISE-16727).
        # Graph-discovered types (RAISE-10133)
        "calibration",
        "tool",
        "value",
        "session",
        "convention",
        "policy",
    }
)


class DualWriteBackend:
    """Dual-write backend — local always, remote best-effort.

    Local is source of truth. Remote failures are logged as warnings,
    never raised as exceptions. When raise_dir is provided, a pending_sync
    marker is written to raise.db on remote failure and cleared on success.

    Args:
        local: Local backend (FilesystemGraphBackend).
        remote: Remote backend (ApiGraphBackend).
        raise_dir: Path to .raise/ directory. Used to locate raise.db.
            If None, marker behavior is skipped.
    """

    def __init__(
        self,
        local: KnowledgeGraphBackend,
        remote: KnowledgeGraphBackend,
        raise_dir: Path | None = None,
    ) -> None:
        self.local = local
        self.remote = remote
        self._db_path: Path | None = (
            raise_dir / "rai" / "raise.db" if raise_dir is not None else None
        )

    def persist(self, graph: Graph, *, prune: bool = False) -> None:
        """Persist to local first, then sync graph to remote (best-effort).

        Local receives the full graph. Remote receives only nodes in
        REMOTE_SYNC_NODE_TYPES, which includes code structure (symbol,
        component) so cluster edges (calls, implements_symbol) survive on
        the server. This expands the remote payload substantially — see
        RAISE-8443 / ADR-096 for the capacity/tier-boundary decision.
        If embeddings are available from cartridge instances, they are
        attached to the remote sync payload.

        Local failure raises (critical). Remote failure logs warning
        and writes a pending_sync marker to raise.db if raise_dir is configured.

        `prune` is accepted for signature compatibility but is NOT forwarded
        to the remote backend (RAISE-15607). The server keyspace is still
        repo-wide — keyed by `server_slug`, with no checkout discriminator —
        so a prune driven by one checkout sends only ITS nodes as
        `keep_node_ids` and the server deletes every other checkout's nodes.
        That is the same last-writer-wins defect this bug fixed locally,
        surviving on the remote side.

        Suppressing the forward trades active corruption (other checkouts'
        nodes deleted) for a benign leak (orphan nodes accumulate on the
        server). The local backend was never pruned — local is source of
        truth — so local behaviour is unchanged.

        KNOWN GAP: server-side checkout scoping is deferred. Until it lands,
        orphan nodes on the server are not reclaimed by any path.

        Args:
            graph: The graph to persist.
            prune: Accepted but ignored — see above. Has no effect on either
                backend.
        """
        self.local.persist(graph)
        filtered = self._filter_for_remote(graph)
        if hasattr(self.remote, "set_embeddings"):
            embeddings = self._load_embeddings(graph)
            if embeddings:
                self.remote.set_embeddings(embeddings)  # type: ignore[union-attr]
                logger.info("Attached %d embeddings to remote sync", len(embeddings))
        try:
            if prune:
                logger.info(
                    "Remote prune suppressed (RAISE-15607): server keyspace is "
                    "repo-wide, so pruning from one checkout would delete other "
                    "checkouts' nodes. Orphans accumulate until server-side "
                    "checkout scoping lands."
                )
            self.remote.persist(filtered)
        except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            detail = ""
            try:
                import httpx

                if isinstance(e, httpx.HTTPStatusError):
                    detail = f" Response: {e.response.text[:200]}"
            except ImportError:
                pass
            logger.warning(
                "Remote sync failed: %s.%s Graph saved locally only.", e, detail
            )
            self._write_marker(filtered, str(e))
            return

        # Remote succeeded — clear any pending marker
        self._clear_marker()

    def _load_embeddings(self, graph: Graph) -> dict[str, list[float]]:
        """Load embeddings from cartridge instances directories."""
        import json

        import numpy as np

        result: dict[str, list[float]] = {}
        if self._db_path is None:
            return result
        raise_dir = self._db_path.parent.parent
        cartridges_dir = raise_dir / "cartridges"
        if not cartridges_dir.exists():
            return result
        for cart_dir in cartridges_dir.iterdir():
            instances_dir = cart_dir / "instances"
            npy_path = instances_dir / "embeddings.npy"
            index_path = instances_dir / "embedding_index.json"
            if not npy_path.exists() or not index_path.exists():
                continue
            try:
                matrix = np.load(npy_path)
                index: dict[str, int] = json.loads(
                    index_path.read_text(encoding="utf-8")
                )
                for node_id, idx in index.items():
                    if idx < len(matrix):
                        result[node_id] = matrix[idx].tolist()
            except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("Failed to load embeddings from %s: %s", cart_dir, e)
        return result

    @staticmethod
    def _filter_for_remote(graph: Graph) -> Graph:
        """Build a subgraph containing only nodes in the sync allowlist."""
        filtered = Graph()
        included_ids: set[str] = set()
        for node in graph.iter_concepts():
            if node.type in REMOTE_SYNC_NODE_TYPES or node.type.startswith("backlog."):
                filtered.add_concept(node)
                included_ids.add(node.id)
        for edge in graph.iter_relationships():
            if edge.type == "related_to":
                continue
            if edge.source in included_ids and edge.target in included_ids:
                filtered.add_relationship(edge)
        return filtered

    def _write_marker(self, graph: Graph, error: str) -> None:
        """Write pending_sync row to raise.db on remote failure."""
        if self._db_path is None:
            return
        from raise_cli.graph.backends.pending import (
            PendingSyncMarker,
            write_pending_marker,
        )

        marker = PendingSyncMarker(
            timestamp=datetime.now(tz=UTC),
            graph_path=str(getattr(self.local, "path", "unknown")),
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            error=error,
        )
        write_pending_marker(self._db_path, marker)

    def _clear_marker(self) -> None:
        """Clear pending_sync row from raise.db on remote success."""
        if self._db_path is None:
            return
        from raise_cli.graph.backends.pending import clear_pending_marker

        clear_pending_marker(self._db_path)

    # -- Protocol delegation ------------------------------------------------
    # DualWriteBackend is a transparent read-proxy for self.local.  Every
    # protocol method that the local backend (SQLiteGraphBackend) implements
    # must be explicitly defined here so @runtime_checkable isinstance()
    # checks pass.  Write goes to both; reads go to local only.

    # -- GraphBackendMetadata --
    def backend_name(self) -> str:  # noqa: D102
        return "dual"

    def storage_location(self) -> str:  # noqa: D102
        if isinstance(self.local, GraphBackendMetadata):
            return self.local.storage_location()
        return str(getattr(self.local, "path", "unknown"))

    # -- KnowledgeGraphBackend --
    def load(self) -> Graph:  # noqa: D102
        return self.local.load()

    # -- GraphBundleQueryBackend --
    def get_foundational_patterns(self) -> list[GraphNode]:  # noqa: D102
        return self.local.get_foundational_patterns()  # type: ignore[union-attr]

    def get_always_on_nodes(self) -> list[GraphNode]:  # noqa: D102
        return self.local.get_always_on_nodes()  # type: ignore[union-attr]

    def find_release_for_epic(self, epic_node_id: str) -> GraphNode | None:  # noqa: D102
        return self.local.find_release_for_epic(epic_node_id)  # type: ignore[union-attr]

    def get_backlog_item_nodes(self) -> list[GraphNode]:  # noqa: D102
        return self.local.get_backlog_item_nodes()  # type: ignore[union-attr]

    # -- GraphTraversalBackend --
    def get_module_ids(self) -> list[str]:  # noqa: D102
        return self.local.get_module_ids()  # type: ignore[union-attr]

    def ego_subgraph(self, node_id: str, depth: int = 2) -> Graph:  # noqa: D102
        return self.local.ego_subgraph(node_id, depth=depth)  # type: ignore[union-attr]

    def neighbors(  # noqa: D102
        self, node_id: str, direction: str = "outgoing"
    ) -> list[tuple[str, str]]:
        return self.local.neighbors(node_id, direction=direction)  # type: ignore[union-attr]

    def path(self, src: str, dst: str) -> list[str] | None:  # noqa: D102
        return self.local.path(src, dst)  # type: ignore[union-attr]

    # -- Durable annotations (RAISE-16596, local-only) --
    # Not part of KnowledgeGraphBackend yet — only SQLiteGraphBackend
    # implements the annotations table. Delegated here anyway (RAISE-16610)
    # so callers that resolve the backend via get_active_backend() (which
    # returns DualWriteBackend whenever server credentials are configured —
    # the common case) don't silently fall back to the destructive
    # persist() path just because the outer backend object doesn't happen
    # to be a bare SQLiteGraphBackend. Annotations are local-only, same as
    # every other local-only capability delegated above.
    def upsert_annotations(
        self,
        namespace: str,
        payloads: dict[str, dict[str, object]],
        *,
        checkout_id: str | None = None,
    ) -> None:
        """Delegate to local — see `local` backend's own docstring."""
        self.local.upsert_annotations(  # type: ignore[union-attr]
            namespace, payloads, checkout_id=checkout_id
        )

    def load_annotations(self, namespace: str) -> dict[str, dict[str, object]]:  # noqa: D102
        return self.local.load_annotations(namespace)  # type: ignore[union-attr]

    # -- RAISE-16852: BC assignments (local-only, REPO_WIDE partition) --
    def upsert_bc_assignments(self, graph: Graph) -> None:
        """Delegate BC assignment persistence to local — see SQLiteGraphBackend.

        BC-* nodes and belongs_to→BC-* edges are local-only (same as
        annotations): they require the REPO_WIDE durability mechanism only
        available in SQLiteGraphBackend.  Remote sync is intentionally omitted
        until the server has checkout-scoped keyspace (RAISE-15607 gap).
        """
        self.local.upsert_bc_assignments(graph)  # type: ignore[union-attr]

    def health(self) -> BackendHealth:
        """Aggregate health from both backends.

        Returns:
            BackendHealth with combined status:
            - healthy: both healthy
            - degraded: local healthy, remote not
            - unavailable: local not healthy
        """
        local_health = self.local.health()
        remote_health = self.remote.health()

        if local_health.status != "healthy":
            status = "unavailable"
        elif remote_health.status != "healthy":
            status = "degraded"
        else:
            status = "healthy"

        return BackendHealth(
            status=status,
            message=f"local: {local_health.status}, remote: {remote_health.status}",
            metadata={
                "backend": "dual",
                "local": local_health.status,
                "remote": remote_health.status,
            },
        )
