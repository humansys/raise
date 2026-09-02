"""24h TTL cache for the update-availability check (RAISE-15660).

Wraps `check_update_available()` (open_service.py) — does not replace it.
Any read failure (missing file, corrupt JSON, wrong schema, partially
written file) degrades to a cache miss, never an exception: callers fall
back to the existing fetch-and-report behavior.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from raise_cli.config.paths import get_cache_dir

CACHE_FILENAME = "update-check.json"
DEFAULT_TTL_SECONDS = 24 * 60 * 60

# Mirrors open_service.CheckStatus — duplicated rather than imported to
# keep this module free of a dependency on open_service.
CacheStatus = Literal["ok", "warn", "blocked"]


class UpdateCacheEntry(BaseModel):
    """Persisted result of the last successful update check."""

    checked_at: float
    status: CacheStatus
    data: dict[str, Any] = {}


def get_update_cache_path() -> Path:
    """Return the default on-disk location for the update-check cache."""
    return get_cache_dir() / CACHE_FILENAME


def read_update_cache(
    *,
    path: Path | None = None,
    ttl_seconds: float = DEFAULT_TTL_SECONDS,
    now: float | None = None,
) -> UpdateCacheEntry | None:
    """Return the cached entry if present, well-formed, and within TTL.

    Returns None (cache miss) on any of: missing file, unreadable file,
    invalid JSON, schema mismatch, or an entry older than `ttl_seconds`.
    """
    cache_path = path or get_update_cache_path()
    try:
        raw = cache_path.read_text()
    except (OSError, UnicodeDecodeError):
        return None

    try:
        entry = UpdateCacheEntry.model_validate_json(raw)
    except (ValidationError, ValueError):
        return None

    current = now if now is not None else time.time()
    if current - entry.checked_at > ttl_seconds:
        return None
    return entry


def write_update_cache(
    status: CacheStatus,
    data: dict[str, Any],
    *,
    path: Path | None = None,
    now: float | None = None,
) -> None:
    """Persist the latest check result. Write failures are advisory, never raised."""
    cache_path = path or get_update_cache_path()
    entry = UpdateCacheEntry(
        checked_at=now if now is not None else time.time(), status=status, data=data
    )
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(entry.model_dump_json())
    except OSError:
        pass
