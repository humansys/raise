"""Session context backend for MCP tools — S1962.9.

Dual backend behind a Protocol so ``raise_session_context`` runs uniformly
under both transports:

    stdio (Claude Code local)  → FilesystemSessionContextBackend
    http  (Rovo multi-tenant)  → PostgresSessionContextBackend, scoped by JWT

Filesystem backend delegates to the existing ``_run_cli("session", "context")``
subprocess — identical behavior to pre-S1962.9.

Postgres backend (in raise-server) queries pipeline_runs, governance_scopes,
and memory_patterns per section.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SessionContextBackend(Protocol):
    """Contract for session context bundle assembly from MCP tools."""

    async def bundle(
        self, sections: list[str], session_id: str | None = None
    ) -> dict[str, Any]:
        """Assemble context bundle for the requested sections.

        Returns a dict with ``status`` and ``content`` keys.
        Content shape varies by transport:
        - stdio: ``content`` is a plain text string (formatted for AI consumption).
        - http: ``content`` is a structured dict with per-section data.

        Args:
            sections: Section names to load.
            session_id: Explicit agent session_id, already resolved in-process
                by the caller (RAISE-9886 idiom, RAISE-13146 AR F1). Threaded
                through as ``--session`` by the Filesystem backend so the
                ``ledger`` section surfaces the same session that was written,
                even when this backend's own env would resolve differently.
                Non-local backends (Api/Postgres) accept it for Protocol
                conformance; server-side parity is deferred (design §8).
        """
        ...


class FilesystemSessionContextBackend:
    """stdio-mode backend — delegates to ``rai session context`` CLI.

    Preserves the exact pre-S1962.9 behavior: subprocess call with
    ``--sections`` and ``--project`` flags, returns text output.
    """

    def __init__(self, project_path: str = ".") -> None:
        self._project_path = project_path

    async def bundle(
        self, sections: list[str], session_id: str | None = None
    ) -> dict[str, Any]:
        """Run ``rai session context`` via CLI subprocess.

        When ``session_id`` is provided, forwards it as ``--session`` so the
        subprocess surfaces the SAME session that was resolved in-process by
        the caller, instead of re-resolving from its own (possibly divergent)
        inherited env (RAISE-13146 AR F1).
        """
        sections_str = ",".join(sections)
        args = [
            "uv",
            "run",
            "rai",
            "session",
            "context",
            "--sections",
            sections_str,
            "--project",
            self._project_path,
        ]
        if session_id:
            args += ["--session", session_id]
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            return {"status": "error", "reason": "Session context timed out"}
        if result.returncode != 0:
            return {
                "status": "error",
                "reason": result.stderr.strip() or "Session context failed",
            }
        return {"status": "ok", "content": result.stdout.strip()}


# ---------------------------------------------------------------------------
# Transport-based resolver
# ---------------------------------------------------------------------------


def _is_http_request() -> bool:
    return os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http"


def get_session_context_backend(cwd: str = "") -> SessionContextBackend:
    """Resolve the right backend for the current context.

    Tri-state resolver (ADR-075):
    - RAISE_SERVER_URL set → ApiSessionContextBackend (thin HTTP client).
    - RAISE_MCP_TRANSPORT=http → PostgresSessionContextBackend (server in-process).
    - Neither → FilesystemSessionContextBackend (local CLI subprocess).

    Args:
        cwd: Working directory for project resolution (worktree support).
             Passed to FilesystemSessionContextBackend as project_path.
             Ignored for API and Postgres backends.
    """
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is not None:
        from raise_cli.session.api_context_backend import ApiSessionContextBackend

        server_url, api_key = creds
        return ApiSessionContextBackend(server_url=server_url, api_key=api_key)

    if _is_http_request():
        from mcp.server.auth.middleware.auth_context import get_access_token
        from raise_server.mcp_mount import get_mcp_session_factory
        from raise_server.session.context_backend_db import (
            PostgresSessionContextBackend,
        )

        token: Any = get_access_token()
        if token is None:
            raise RuntimeError(
                "session_context tool invoked via HTTP without valid JWT — "
                "no filesystem fallback allowed on server",
            )
        return PostgresSessionContextBackend(
            get_mcp_session_factory(),
            org_id=token.org_id,
            member_id=token.member_id,
        )

    project_path = str(Path(cwd).resolve()) if cwd else "."
    return FilesystemSessionContextBackend(project_path=project_path)
