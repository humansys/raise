"""Repo-id wire-identity binding in the manifest (RAISE-14662, ADR-133).

A project records the server-issued repo_id it registered so pushes can send
it instead of a free-text project_id, letting the server derive the write's
org from the repo binding rather than from the api_key (the invariant that
closes the cross-org contamination class, ADR-133).

These helpers do **surgical** YAML read/modify/write — same technique as
``org_binding.py`` (RAISE-9823) — they must NOT round-trip through
``ProjectManifest``: ``save_manifest`` uses ``model_dump`` and would drop any
key the model does not declare. Preserving every key (including the sibling
``org:`` block) is the whole point.

The ``repo_id`` here is the WIRE identity — distinct from the LOCAL
``project_id`` that keys ``~/.rai/raise.db`` (never re-key it, RAISE-13467).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir

__all__ = ["bind_repo", "get_bound_repo"]


def get_bound_repo(project_root: Path) -> tuple[str, str] | None:
    """Return ``(slug, repo_id)`` the project is bound to, or None.

    None when there is no manifest, no ``repo`` block, or no ``id`` — the
    match key is ``id`` (UUID); without it there is nothing to enforce.
    """
    path = get_raise_dir(project_root) / MANIFEST_FILE
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    repo = data.get("repo")
    if not isinstance(repo, dict):
        return None
    repo_id = str(repo.get("id") or "").strip()
    if not repo_id:
        return None
    slug = str(repo.get("slug") or "").strip()
    return (slug, repo_id)


def bind_repo(project_root: Path, *, repo_id: str, slug: str) -> bool:
    """Persist the ``repo`` block surgically, preserving all other keys.

    Returns True when the manifest was written, False when there is no
    manifest to bind (run ``rai init`` first) or it is unreadable. All
    non-``repo`` keys (including the sibling ``org:`` block and anything the
    Pydantic model does not declare) are preserved verbatim.
    """
    path = get_raise_dir(project_root) / MANIFEST_FILE
    if not path.exists():
        return False
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return False
    if not isinstance(data, dict):
        return False
    data["repo"] = {"slug": slug, "id": repo_id}
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return True
