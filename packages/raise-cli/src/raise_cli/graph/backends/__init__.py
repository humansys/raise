"""Graph backend implementations — CLI layer with env-var-based selection.

The factory `get_active_backend()` checks RAISE_SERVER_URL + RAISE_API_KEY
and returns DualWriteBackend when both are set, falls back to
~/.rai/server.json, else SQLiteGraphBackend.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from raise_cli.config.paths import (
    checkout_scope_id,
    resolve_checkout_root,
    resolve_repo_root,
)
from raise_cli.config.server import get_server_credentials
from raise_cli.storage.connection import (
    get_project_db_path,
    get_project_id,
    get_server_slug,
)
from raise_core.graph.backends.filesystem import (
    FilesystemGraphBackend,  # explicit --index only
)
from raise_core.graph.backends.protocol import KnowledgeGraphBackend

logger = logging.getLogger(__name__)

__all__ = ["get_active_backend"]


def get_active_backend(
    path: Path,
    db_path: Path | None = None,
    *,
    explicit_path: bool = False,
    project_root: Path | None = None,
) -> KnowledgeGraphBackend:
    """Resolve the active graph backend based on environment.

    Resolution order:
    1. RAISE_SERVER_URL + RAISE_API_KEY env vars
    2. ~/.rai/server.json (written by ``rai connect``)
    3. Local SQLite (Community mode)

    Args:
        path: Path to the legacy graph JSON file (used as migration source).
        db_path: Optional explicit path to raise.db. Auto-derived when None.
        explicit_path: True when path was supplied via --index flag (uses FilesystemBackend).
        project_root: Optional CHECKOUT root. Since RAISE-15607 this is an
            IDENTITY KEY, not just a lookup hint: it becomes the backend's
            ``checkout_id``, i.e. which graph partition is read and written.
            Defaults to ``resolve_checkout_root()`` — the calling worktree, not
            the repository. Passing a *repository* root from inside a worktree
            selects the main checkout's partition, which is almost never what
            the caller wants. See ADR-145.
    """
    creds = get_server_credentials()

    if creds is not None:
        server_url, api_key = creds
        from raise_cli.graph.backends.api import ApiGraphBackend
        from raise_cli.graph.backends.dual import DualWriteBackend
        from raise_cli.graph.backends.sqlite import SQLiteGraphBackend

        # LOCAL id (RAISE-13319): the current checkout, never the main repo.
        local_root = project_root or resolve_checkout_root()
        raise_dir = local_root / ".raise"
        if db_path is None:
            db_path = get_project_db_path(local_root)
        # Local backend is SQLite canonical storage; remote API remains best-effort.
        local = SQLiteGraphBackend(
            project_id=get_project_id(local_root),
            db_path=db_path,
            # RAISE-15607: project_id is repo-wide (git-tracked manifest name) and
            # therefore identical in every worktree/clone. checkout_id is what
            # separates their indices. resolve_checkout_root() already computes
            # it here; it used to be discarded.
            checkout_id=checkout_scope_id(local_root),
        )
        # WIRE id (RAISE-13467): main-checkout manifest resolution stays in
        # scope here — flipping it is RAISE-13298 territory, not this bug.
        wire_root = project_root or resolve_repo_root() or Path.cwd()
        remote = ApiGraphBackend(
            server_url=server_url,
            api_key=api_key,
            project_id=get_server_slug(wire_root),
        )
        return DualWriteBackend(
            local=local,
            remote=remote,
            raise_dir=raise_dir if raise_dir.exists() else None,
        )

    if os.environ.get("RAISE_SERVER_URL", "").strip():
        logger.warning(
            "RAISE_SERVER_URL is set but no API key was resolved. "
            "Using local SQLite backend only."
        )

    local_root = project_root or resolve_checkout_root()
    if db_path is None:
        db_path = get_project_db_path(local_root)

    # Explicit JSON path (--index flag) -> FilesystemGraphBackend for that file,
    # including missing files so explicit user input keeps strict file errors.
    # Default path (interactive session) -> SQLite canonical graph store.
    if explicit_path and path.suffix == ".json":
        return FilesystemGraphBackend(path=path)

    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend

    # SQLite is the Community default. Missing graph rows remain explicit:
    # callers receive an empty graph rather than hidden seed/backfill content.
    return SQLiteGraphBackend(
        project_id=get_project_id(local_root),
        db_path=db_path,
        checkout_id=checkout_scope_id(local_root),  # RAISE-15607, see above
    )
