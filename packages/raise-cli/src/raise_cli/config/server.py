"""Server credential resolution — single source of truth.

Every CLI subsystem that talks to raise-server must resolve credentials
through ``get_server_credentials()``. Resolution order:

1. RAISE_SERVER_URL + RAISE_API_KEY env vars
2. ~/.rai/server.json (written by ``rai connect``)

Reading env vars directly skips the ``rai connect`` onboarding path and
breaks new developers whose only configuration is server.json.
"""

from __future__ import annotations

import json
import os
from typing import NamedTuple

from raise_cli.config.paths import get_global_rai_dir

__all__ = ["ServerTarget", "get_server_credentials", "get_server_target"]


class ServerTarget(NamedTuple):
    """Full server write target: credentials plus org identity (RAISE-9821).

    ``org_name``/``org_id`` come from ~/.rai/server.json (written by
    ``rai connect``) and are empty strings when only env vars configure the
    connection — callers must tolerate empties.
    """

    server_url: str
    api_key: str
    org_name: str
    org_id: str


def get_server_credentials() -> tuple[str, str] | None:
    """Return (server_url, api_key) or None when not configured.

    Never raises — a malformed server.json degrades to None.
    """
    url = os.environ.get("RAISE_SERVER_URL", "").strip().rstrip("/")
    key = os.environ.get("RAISE_API_KEY", "").strip()
    if url and key:
        return url, key

    path = get_global_rai_dir() / "server.json"
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            json_url = str(data.get("server_url", "")).strip().rstrip("/")
            json_key = str(data.get("api_key", "")).strip()
            url = url or json_url
            key = key or json_key
            if url and key:
                return url, key
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return None


def get_server_target() -> ServerTarget | None:
    """Return the full write target (creds + org identity), or None if unconfigured.

    Builds on ``get_server_credentials`` (the canonical resolver) and enriches it
    with org_name/org_id from server.json so write commands can echo where the
    data is going before sending it (RAISE-9821).
    """
    creds = get_server_credentials()
    if creds is None:
        return None
    url, key = creds
    org_name = ""
    org_id = ""
    path = get_global_rai_dir() / "server.json"
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            org_name = str(data.get("org_name") or "").strip()
            org_id = str(data.get("org_id") or "").strip()
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return ServerTarget(url, key, org_name, org_id)
