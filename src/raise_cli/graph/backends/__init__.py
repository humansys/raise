"""Graph backend implementations — CLI layer with env-var-based selection.

The factory `get_active_backend()` checks RAI_SERVER_URL + RAI_API_KEY
and returns DualWriteBackend when both are set, else FilesystemGraphBackend.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from raise_core.graph.backends.filesystem import FilesystemGraphBackend
from raise_core.graph.backends.protocol import KnowledgeGraphBackend

logger = logging.getLogger(__name__)

__all__ = ["get_active_backend"]


def get_active_backend(path: Path) -> KnowledgeGraphBackend:
    """Resolve the active graph backend based on environment.

    Returns DualWriteBackend when RAI_SERVER_URL and RAI_API_KEY are both
    set. Falls back to FilesystemGraphBackend otherwise.

    Args:
        path: Path to the graph JSON file (for local backend).
    """
    server_url = os.environ.get("RAI_SERVER_URL", "").strip()
    api_key = os.environ.get("RAI_API_KEY", "").strip()

    if server_url and api_key:
        from raise_cli.graph.backends.api import ApiGraphBackend
        from raise_cli.graph.backends.dual import DualWriteBackend

        project_id = Path.cwd().name
        raise_dir = Path.cwd() / ".raise"
        local = FilesystemGraphBackend(path=path)
        remote = ApiGraphBackend(
            server_url=server_url,
            api_key=api_key,
            project_id=project_id,
        )
        return DualWriteBackend(
            local=local,
            remote=remote,
            raise_dir=raise_dir if raise_dir.exists() else None,
        )

    if server_url and not api_key:
        logger.warning(
            "RAI_SERVER_URL is set but RAI_API_KEY is missing. "
            "Using local filesystem backend only."
        )

    return FilesystemGraphBackend(path=path)
