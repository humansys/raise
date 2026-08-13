"""Startup health checks for the RaiSE MCP server.

Extracted from mcp_server.py to keep the entrypoint ≤70 non-blank lines.
Each check is non-blocking and swallows all exceptions silently (local-first).
"""

from __future__ import annotations

import importlib.util
import logging
import time
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

_STAMP_PATH: Path = Path.home() / ".rai" / "mcp_server_stamp"


def _resolve_source_files() -> list[Path]:
    spec = importlib.util.find_spec("raise_cli.pipeline.mcp_server")
    if spec and spec.origin:
        parent = Path(spec.origin).parent
        return sorted(parent.glob("mcp_*.py"))
    return []


_SOURCE_FILES: list[Path] = _resolve_source_files()


def check_server_version() -> None:
    """Warn when raise-server version skews from CLI version (RAISE-8388).

    Never blocks startup — local-first. Swallows all exceptions silently.
    """
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is None:
        return
    server_url, _api_key = creds
    try:
        import raise_cli

        resp = httpx.get(f"{server_url}/health", timeout=3.0)
        srv_ver: str = resp.json().get("version", "")
        cli_ver: str = raise_cli.__version__
        srv_parts = srv_ver.split(".")
        cli_parts = cli_ver.split(".")
        if (
            len(srv_parts) >= 2
            and len(cli_parts) >= 2
            and srv_parts[:2] != cli_parts[:2]
        ):
            logger.warning(
                "Version skew detected: cli=%s server=%s — MCP tools may fail on "
                "mismatched endpoints. Resolve with: rai connect",
                cli_ver,
                srv_ver,
            )
    except Exception:  # noqa: BLE001 S110 — intentional: local-first, never block startup
        pass


def check_staleness() -> None:
    """Warn when pipeline source files changed since last MCP server start (RAISE-8491).

    Compares the max mtime of key pipeline source files against a stamp written
    at the previous startup. A newer mtime means a git merge or reinstall occurred
    while the server was running — tools in that session may have been stale.

    Never blocks startup — swallows all exceptions silently.
    """
    try:
        if not _STAMP_PATH.exists():
            return
        stamp_mtime = float(_STAMP_PATH.read_text().strip())
        max_src_mtime = max(
            (f.stat().st_mtime for f in _SOURCE_FILES if f.exists()),
            default=0.0,
        )
        if max_src_mtime > stamp_mtime:
            logger.warning(
                "Pipeline source files changed since last MCP server start — "
                "tools in the previous session may have been stale. "
                "If tools behave unexpectedly, restart with: claude mcp restart rai-workspace",
            )
    except Exception:  # noqa: BLE001 S110 — intentional: local-first, never block startup
        pass
    finally:
        try:
            _STAMP_PATH.parent.mkdir(parents=True, exist_ok=True)
            _STAMP_PATH.write_text(str(time.time()))
        except Exception:  # noqa: BLE001 S110
            pass
