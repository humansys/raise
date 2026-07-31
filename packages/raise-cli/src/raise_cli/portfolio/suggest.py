"""Portfolio suggestion engine — level-invariant git attribution (RAISE-15255).

Given any Jira key (initiative, epic, story, or bug), derives a *draft*
portfolio characterisation from git history:

1. ``git log --grep <key>`` → commit SHAs
2. ``git diff-tree`` per commit → changed repo-relative file paths
3. Map files → component names via ``portfolio.component_paths`` in manifest
4. Query graph DB for ``is_contract=True`` symbol nodes in changed files
5. Infer ``change_mode`` (breaking / additive / evolutionary) from numstat

The result is intentionally *not* persisted — callers decide whether to
promote it to ``initiative_profiles`` or ``epic_profiles``.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from raise_cli.portfolio.component_map import resolve_component
from raise_cli.portfolio.git_attr import (
    get_changed_files_for_commits,
    get_commits_for_key,
    infer_change_mode,
)
from raise_cli.storage.connection import get_project_db_path, get_project_id


class SuggestionResult(BaseModel):
    """Draft portfolio suggestion for a Jira key (not persisted)."""

    key: str
    components_touched: list[str]
    change_mode: str  # "" when unknown (no commits, empty numstat)
    contracts_affected: list[str]
    commit_count: int
    mapped_count: int = 0
    total_count: int = 0
    unmapped_files: list[str] = []
    note: str = "draft — verify before persisting"


def _load_component_paths(project_root: Path) -> dict[str, list[str]]:
    """Load ``portfolio.component_paths`` from ``.raise/manifest.yaml``.

    Returns an empty dict when the manifest is absent or has no portfolio
    section — callers treat this as "no component map configured".
    """
    from raise_cli.onboarding.manifest import load_manifest  # noqa: PLC0415

    manifest = load_manifest(project_root)
    if manifest is None or manifest.project.portfolio is None:
        return {}
    return manifest.project.portfolio.component_paths


def _get_contract_nodes_in_files(files: list[str], project_root: Path) -> list[str]:
    """Return node IDs of contract symbol nodes whose ``source_file`` is in *files*.

    Queries ``graph_nodes`` for ``node_type='symbol'`` rows where
    ``source_file`` matches any of *files* and ``metadata_json`` contains
    ``is_contract=true``.

    Args:
        files: Repo-relative file paths (same format as ``source_file`` column).
        project_root: Absolute path to the project root (used to locate the DB
            and derive the project partition key).

    Returns:
        List of ``node_id`` strings for matching contract nodes.
        Empty list when *files* is empty, DB does not exist, or no contracts
        are found.
    """
    if not files:
        return []
    db_path = get_project_db_path(project_root)
    if not db_path.exists():
        return []
    project_id = get_project_id(project_root)
    placeholders = ",".join("?" * len(files))
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            f"SELECT node_id, metadata_json FROM graph_nodes"  # noqa: S608  # nosec B608
            f" WHERE project_id = ? AND node_type = 'symbol'"
            f" AND source_file IN ({placeholders})",
            [project_id, *files],
        ).fetchall()
    finally:
        conn.close()
    result: list[str] = []
    for row in rows:
        meta: dict[str, object] = json.loads(str(row["metadata_json"] or "{}"))
        if meta.get("is_contract"):
            result.append(str(row["node_id"]))
    return result


def suggest_for_key(key: str, project_root: Path) -> SuggestionResult:
    """Derive a draft portfolio suggestion for *key* from git history.

    Level-invariant: works for initiative, epic, story, and bug keys.
    No writes to the DB — the caller decides whether to persist the result.

    Args:
        key: Jira key (e.g. ``"RAISE-15255"``).
        project_root: Absolute path to the project root.

    Returns:
        :class:`SuggestionResult` with ``commit_count=0`` and empty fields
        when no commits reference *key*.
    """
    commits = get_commits_for_key(key, project_root)
    if not commits:
        return SuggestionResult(
            key=key,
            components_touched=[],
            change_mode="",
            contracts_affected=[],
            commit_count=0,
            note="no commits found",
        )

    changed_files = get_changed_files_for_commits(commits, project_root)
    component_paths = _load_component_paths(project_root)

    mapped: list[str] = []
    unmapped: list[str] = []
    components_set: set[str] = set()
    for f in changed_files:
        c = resolve_component(f, component_paths)
        if c is not None:
            mapped.append(f)
            components_set.add(c)
        else:
            unmapped.append(f)

    components_touched = sorted(components_set)

    contracts = _get_contract_nodes_in_files(changed_files, project_root)
    change_mode = infer_change_mode(
        commits, project_root, has_contracts=bool(contracts)
    )

    return SuggestionResult(
        key=key,
        components_touched=components_touched,
        change_mode=change_mode,
        contracts_affected=contracts,
        commit_count=len(commits),
        mapped_count=len(mapped),
        total_count=len(changed_files),
        unmapped_files=sorted(unmapped),
    )
