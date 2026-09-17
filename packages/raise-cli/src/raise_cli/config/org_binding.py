"""Project↔organization binding in the manifest (RAISE-9823).

A project records the org it belongs to so server-write commands can refuse to
land data in a different org after ``server.json`` switches between operations
(the cross-org contamination incident RAISE-11075).

These helpers do **surgical** YAML read/modify/write — they must NOT round-trip
through ``ProjectManifest``: ``save_manifest`` uses ``model_dump`` and would drop
any key the model does not declare (e.g. ``fleet``). Preserving every key is the
whole point, so we edit the parsed mapping in place.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir

__all__ = ["bind_org", "get_bound_org"]


def get_bound_org(project_root: Path) -> tuple[str, str] | None:
    """Return ``(org_name, org_id)`` the project is bound to, or None.

    None when there is no manifest, no ``org`` block, or no ``id`` — the match
    key is ``id`` (UUID); without it there is nothing to enforce.
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
    org = data.get("org")
    if not isinstance(org, dict):
        return None
    org_id = str(org.get("id") or "").strip()
    if not org_id:
        return None
    org_name = str(org.get("name") or "").strip()
    return (org_name, org_id)


def bind_org(project_root: Path, org_name: str, org_id: str) -> bool:
    """Persist the ``org`` block surgically, preserving all other keys.

    Returns True when the manifest was written, False when there is no manifest
    to bind (run ``rai init`` first) or it is unreadable. All non-``org`` keys
    (including ones the Pydantic model does not declare) are preserved verbatim.
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
    data["org"] = {"name": org_name, "id": org_id}
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return True
