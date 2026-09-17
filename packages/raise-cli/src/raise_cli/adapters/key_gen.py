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

from raise_cli.adapters.backlog_config import (
    get_configured_adapters,
    load_backlog_config,
)
from raise_cli.adapters.models.pm import BacklogAdapterConfig, WorkflowState
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


# Built-in fallback so status_category is always populated even when no
# backlog.yaml config exists (RAISE-16941 fixed FilesystemPMAdapter;
# RAISE-16968 brings the same fix to the shared key_gen path used by SQLite).
_CANONICAL_STATUS_CATEGORIES: dict[str, str] = {
    "pending": "new",
    "backlog": "new",
    "new": "new",
    "design": "indeterminate",
    "implement": "indeterminate",
    "in progress": "indeterminate",
    "in_progress": "indeterminate",
    "review": "indeterminate",
    "done": "done",
    "complete": "done",
    "cancelled": "done",
    "canceled": "done",
}


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
) -> list[WorkflowState]:
    """Return workflow states for an issue type, with case-insensitive fallback."""
    workflow = config.workflow.get(issue_type)
    if workflow is None:
        for configured_type, candidate in config.workflow.items():
            if configured_type.casefold() == issue_type.casefold():
                workflow = candidate
                break
    return [] if workflow is None else workflow.states


def status_category_for(project_root: Path, issue_type: str, status: str) -> str:
    """Resolve a stored status name to its workflow category.

    Checks the built-in canonical mapping first so status_category is always
    populated regardless of external config presence (RAISE-16941/RAISE-16968),
    then falls through to any configured adapter workflow for project-specific
    overrides. Returns empty string only for blank inputs.
    """
    if not issue_type or not status:
        return ""

    canonical = _CANONICAL_STATUS_CATEGORIES.get(status.casefold())
    if canonical is not None:
        return canonical

    for adapter_name in _status_category_adapter_names(project_root):
        try:
            config = load_backlog_config(project_root, adapter_name)
        except (FileNotFoundError, KeyError, ValueError):
            continue

        for state in _workflow_states_for_issue_type(config, issue_type):
            if state.name.casefold() == status.casefold():
                return state.status_category

    return ""
