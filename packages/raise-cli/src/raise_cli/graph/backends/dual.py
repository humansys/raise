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
from raise_core.graph.backends.protocol import KnowledgeGraphBackend
from raise_core.graph.engine import Graph

logger = logging.getLogger(__name__)

__all__ = ["DualWriteBackend"]


class DualWriteBackend:
    """Dual-write backend — local always, remote best-effort.

    Local is source of truth. Remote failures are logged as warnings,
    never raised as exceptions. When raise_dir is provided, a pending_sync
    marker is created on remote failure and cleared on success.

    Args:
        local: Local backend (FilesystemGraphBackend).
        remote: Remote backend (ApiGraphBackend).
        raise_dir: Path to .raise/ directory for pending_sync marker.
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
        self._raise_dir = raise_dir

    def persist(self, graph: Graph) -> None:
        """Persist to local first, then sync to remote (best-effort).

        Local failure raises (critical). Remote failure logs warning
        and creates a pending_sync marker if raise_dir is configured.

        Args:
            graph: The graph to persist.
        """
        self.local.persist(graph)
        try:
            self.remote.persist(graph)
        except Exception as e:
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
            self._write_marker(graph, str(e))
            return

        # Remote succeeded — clear any pending marker
        self._clear_marker()

    def _write_marker(self, graph: Graph, error: str) -> None:
        """Create pending_sync marker on remote failure."""
        if self._raise_dir is None:
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
        write_pending_marker(self._raise_dir, marker)

    def _clear_marker(self) -> None:
        """Clear pending_sync marker on remote success."""
        if self._raise_dir is None:
            return
        from raise_cli.graph.backends.pending import clear_pending_marker

        clear_pending_marker(self._raise_dir)

    def load(self) -> Graph:
        """Load from local backend (source of truth).

        Returns:
            Graph loaded from local filesystem.
        """
        return self.local.load()

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
