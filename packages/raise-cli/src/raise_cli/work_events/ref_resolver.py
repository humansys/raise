r"""Resolve local work IDs to Jira keys via the work_items store.

Passthrough policy: IDs already matching the Jira regex (``[A-Z]+-\d+``) are
returned as-is without touching the store. Otherwise the store is queried
(cached in-memory per db path) and consulted. Misses return None; the caller
is responsible for dropping the corresponding signal and logging.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from raise_cli.storage.connection import get_project_db_path
from raise_cli.storage.schema import create_all

_JIRA_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")

_cache: dict[Path, dict[str, str]] = {}


def _load_ledger(db_path: Path) -> dict[str, str]:
    if db_path in _cache:
        return _cache[db_path]
    if not db_path.exists():
        _cache[db_path] = {}
        return _cache[db_path]
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        create_all(conn)
        rows = conn.execute(
            "SELECT local_key, jira_key FROM work_items WHERE jira_key IS NOT NULL"
        ).fetchall()
        result = {row["local_key"]: row["jira_key"] for row in rows}
    finally:
        conn.close()
    _cache[db_path] = result
    return result


def clear_cache() -> None:
    """Clear the in-memory ledger cache (test hook / SIGHUP-style refresh)."""
    _cache.clear()


def resolve(work_id: str, *, db_path: Path | None = None) -> str | None:
    """Resolve a local work id to a Jira key. Returns None on miss.

    Jira-shaped IDs (e.g. "RAISE-1713") pass through without consulting the
    ledger. Local IDs (e.g. "E1691", "S2.1") trigger a cached ledger lookup.
    """
    if not work_id:
        return None
    if _JIRA_KEY_RE.match(work_id):
        return work_id
    path = db_path or get_project_db_path(Path.cwd())
    return _load_ledger(path).get(work_id)
