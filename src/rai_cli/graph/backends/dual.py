"""Dual-write graph backend — local + remote with best-effort sync.

Writes to both FilesystemGraphBackend (local, always succeeds) and
ApiGraphBackend (remote, best-effort). Loads from local only.

Architecture: ADR-036 (KnowledgeGraphBackend)
"""

from __future__ import annotations

import logging

from rai_core.graph.backends.models import BackendHealth
from rai_core.graph.backends.protocol import KnowledgeGraphBackend
from rai_core.graph.engine import Graph

logger = logging.getLogger(__name__)

__all__ = ["DualWriteBackend"]


class DualWriteBackend:
    """Dual-write backend — local always, remote best-effort.

    Local is source of truth. Remote failures are logged as warnings,
    never raised as exceptions.

    Args:
        local: Local backend (FilesystemGraphBackend).
        remote: Remote backend (ApiGraphBackend).
    """

    def __init__(
        self, local: KnowledgeGraphBackend, remote: KnowledgeGraphBackend
    ) -> None:
        self.local = local
        self.remote = remote

    def persist(self, graph: Graph) -> None:
        """Persist to local first, then sync to remote (best-effort).

        Local failure raises (critical). Remote failure logs warning.

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
