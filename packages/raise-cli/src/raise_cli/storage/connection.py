"""SQLite connection factory with WAL mode and production PRAGMAs."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
import subprocess
from functools import lru_cache
from pathlib import Path

from raise_cli.config.paths import get_global_rai_dir

logger = logging.getLogger(__name__)

DB_FILE = "raise.db"


def _configure(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


@lru_cache(maxsize=32)
def get_project_hash(project_root: str) -> str:
    """Compute a stable hash for a project, based on git remote URL or path.

    Legacy — used only by the hash→slug migration to compute old partition keys.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            identity = result.stdout.strip()
            return hashlib.sha256(identity.encode()).hexdigest()[:12]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    identity = str(Path(project_root).resolve())
    return hashlib.sha256(identity.encode()).hexdigest()[:12]


def _read_manifest_project(project_root: str) -> dict[str, object]:
    """Read the `project` dict from .raise/manifest.yaml.

    Returns {} when the manifest is absent, unreadable, or malformed.
    Shared by `_get_project_slug` and `_get_server_slug` so the yaml-load
    guard exists in exactly one place (RAISE-13467 arch-review refinement).
    """
    manifest = Path(project_root) / ".raise" / "manifest.yaml"
    if not manifest.is_file():
        return {}
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        project = (data or {}).get("project", {})
        return project if isinstance(project, dict) else {}
    except Exception:  # noqa: BLE001, S110
        return {}


@lru_cache(maxsize=32)
def _get_project_slug(project_root: str) -> str:
    """Derive a human-readable project slug — the LOCAL identity.

    This is the key for every row in ~/.rai/raise.db (sessions, missions,
    graph, patterns, signals). It MUST remain stable regardless of
    `server_slug` — for the wire-facing id sent to raise-server, use
    `get_server_slug()` instead. Collapsing the two here (RAISE-13298)
    silently re-keyed all local history when `server_slug` diverged from
    `name` (RAISE-13467).

    Resolution order:
    1. .raise/manifest.yaml → project.name
    2. git remote basename (strip .git)
    3. directory name
    """
    project = _read_manifest_project(project_root)
    name = project.get("name", "")
    if name:
        return str(name)

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            basename = url.rstrip("/").rsplit("/", 1)[-1]
            basename = basename.removesuffix(".git")
            if basename:
                return basename
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return Path(project_root).resolve().name


def get_project_id(project_root: Path) -> str:
    """Return the stable LOCAL project identifier — keys ~/.rai/raise.db.

    NEVER use this for raise-server API calls — use get_server_slug()
    instead (RAISE-13467).
    """
    return _get_project_slug(str(project_root))


@lru_cache(maxsize=32)
def _get_server_slug(project_root: str) -> str:
    """Derive the WIRE-facing project slug for raise-server API calls.

    Resolution order:
    1. .raise/manifest.yaml → project.server_slug (RAISE-11083, server-confirmed)
    2. _get_project_slug(project_root) (local slug, if no server_slug set)
    """
    project = _read_manifest_project(project_root)
    server_slug = project.get("server_slug", "")
    if server_slug:
        return str(server_slug)
    return _get_project_slug(project_root)


def get_server_slug(project_root: Path) -> str:
    """Return the wire-facing project slug for raise-server API calls.

    Resolution order:
    1. .raise/manifest.yaml → project.server_slug (RAISE-11083, server-confirmed)
    2. get_project_id(project_root) (local slug, if no server_slug set)

    NEVER use this for local ~/.rai/raise.db keying — use get_project_id()
    instead (RAISE-13467: collapsing these two caused silent re-keying of
    all local data).
    """
    return _get_server_slug(str(project_root))


def get_project_db_path(_project_root: Path | None = None) -> Path:
    """Resolve the global DB path at ~/.rai/raise.db."""
    return get_global_rai_dir() / DB_FILE


def get_project_db(project_root: Path) -> sqlite3.Connection:
    """Return a configured SQLite connection for the global DB (~/.rai/raise.db).

    All projects share the same database; use get_project_id(project_root)
    to obtain the project_id for query discrimination.
    """
    db_path = get_project_db_path(project_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    if conn.execute("PRAGMA auto_vacuum").fetchone()[0] != 2:
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL")
    conn = _configure(conn)

    return conn


def get_global_db() -> sqlite3.Connection:
    """Return a configured SQLite connection for global cross-project data."""
    global_dir = get_global_rai_dir()
    db_path = global_dir / DB_FILE
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    if conn.execute("PRAGMA auto_vacuum").fetchone()[0] != 2:
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL")
    return _configure(conn)
