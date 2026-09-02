"""Shared key generation and local adapter utilities.

Extracted from ``filesystem.py`` so both ``FilesystemPMAdapter`` and
``SQLitePMAdapter`` share identical key-prefix resolution, developer-name
lookup, and seed logic without duplication.

Story: RAISE-16623 (S16533.3), design decision D-S3.5
"""

from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path
from typing import Any

from raise_cli.adapters.backlog_config import (
    get_configured_adapters,
    load_backlog_config,
)
from raise_cli.adapters.models.pm import BacklogAdapterConfig
from raise_cli.developer_profile.profile import load_developer_profile


def developer_name() -> str:
    """Return the developer's local staging prefix from developer.yaml.

    Uses local_prefix if set, otherwise name. Falls back to 'Local' if
    developer.yaml is absent or unreadable.
    """
    profile = load_developer_profile()
    if profile is None:
        return "Local"
    return profile.local_prefix or profile.name


def issue_type_to_work_item_type(issue_type: str) -> str:
    """Map an issue_type string to a WorkItem type (lowercase).

    D8 (S16533.4): promoted from ``sqlite_pm._issue_type_to_work_item_type``
    (RAISE-16623) to a shared, public helper — both ``SQLitePMAdapter`` and
    the migration CLI need identical lossy-mapping behavior. Anything
    outside the V72 CHECK enum (``Mission``, ``Historia``, ``Error``, ...)
    falls back to ``"story"``; callers that must not silently lose the
    original value are responsible for preserving it elsewhere (migration
    stores it in ``custom_fields["source_issue_type"]``).
    """
    lower = issue_type.lower()
    valid = {"theme", "initiative", "epic", "story", "task", "bug"}
    if lower in valid:
        return lower
    return "story"  # default fallback


def seed_from_work_items(conn: sqlite3.Connection, prefix: str) -> int:
    """Return the max numeric suffix of work_items.local_key starting with prefix.

    Used to seed the SQLite counter on first use (replaces Ledger.bootstrap_seed).
    """
    rows = conn.execute(
        "SELECT local_key FROM work_items WHERE local_key LIKE ?",
        (f"{prefix}%",),
    ).fetchall()
    max_n = 0
    for row in rows:
        key: str = row[0]
        suffix = key[len(prefix) :]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return max_n


def resolve_key_prefix(project_root: Path, issue_type: str) -> str:
    """Resolve issue_type -> key prefix using backlog.yaml config.

    Applies alias resolution first (e.g. Historia -> Story),
    then looks up issue_type_prefixes. Falls back to first char lowercase.
    """
    if not issue_type:
        return "x"
    try:
        config = load_backlog_config(project_root, "filesystem")
        canonical = config.issue_type_aliases.get(issue_type, issue_type)
        return config.issue_type_prefixes.get(canonical, canonical[0].lower())
    except (FileNotFoundError, KeyError):
        return issue_type[0].lower()


def _status_category_adapter_names(project_root: Path) -> list[str]:
    """Configured adapter sections that may carry workflow metadata."""
    adapter_names = ["filesystem"]
    with contextlib.suppress(FileNotFoundError, OSError):
        adapter_names.extend(
            name
            for name in sorted(get_configured_adapters(project_root))
            if name != "filesystem"
        )
    return adapter_names


def _workflow_states_for_issue_type(
    config: BacklogAdapterConfig, issue_type: str
) -> list[dict[str, Any]]:
    """Return workflow states for an issue type, with case-insensitive fallback."""
    workflow = config.workflow.get(issue_type)
    if workflow is None:
        for configured_type, candidate in config.workflow.items():
            if configured_type.casefold() == issue_type.casefold():
                workflow = candidate
                break
    return [] if workflow is None else workflow.states


def status_category_for(project_root: Path, issue_type: str, status: str) -> str:
    """Resolve a stored status name to its workflow category when configured.

    Searches all configured adapter sections in backlog.yaml for a matching
    workflow state with the given issue_type and status (case-insensitive).
    Returns empty string if no match is found.
    """
    if not issue_type or not status:
        return ""

    for adapter_name in _status_category_adapter_names(project_root):
        try:
            config = load_backlog_config(project_root, adapter_name)
        except (FileNotFoundError, KeyError, ValueError):
            continue

        for state in _workflow_states_for_issue_type(config, issue_type):
            if str(state.get("name", "")).casefold() == status.casefold():
                return str(state.get("status_category", ""))

    return ""
