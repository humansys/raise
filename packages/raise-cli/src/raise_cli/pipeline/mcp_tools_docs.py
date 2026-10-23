"""Docs MCP tools — raise_docs_write, raise_docs_search, raise_docs_get.

Dual-write: local filesystem + remote docs target (Confluence).
Local write is skipped when RAISE_MCP_TRANSPORT=http (server context).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_instance import mcp

_logger = logging.getLogger(__name__)


def _is_server_context() -> bool:
    return os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http"


def _resolve_docs_target_safe(
    target_name: str | None = None, project_root: Path | None = None
) -> Any | None:
    """Resolve DocumentationTarget without calling sys.exit().

    Returns None when no target is available (missing config, no
    adapters installed, instantiation failure). The MCP tool treats
    remote publish as best-effort — local write is the primary output.

    ``project_root`` anchors docs.yaml resolution to the caller's checkout
    (S15457.2); None preserves the legacy process-CWD resolution.
    """
    try:
        from raise_cli.cli.commands._resolve import resolve_docs_target

        return resolve_docs_target(
            target_name, require_local=True, project_root=project_root
        )
    except SystemExit:
        _logger.debug("Docs target resolution triggered sys.exit — skipping remote")
        return None
    except Exception:  # noqa: BLE001
        _logger.debug("Docs target resolution failed", exc_info=True)
        return None


def _resolve_local_path(output_path: str, cwd: str = "") -> Path:
    """Resolve docs output path against caller-provided cwd when relative."""
    local_path = Path(output_path)
    if cwd and not local_path.is_absolute():
        return Path(cwd).resolve() / local_path
    return local_path


def _display_path(local_path: Path, cwd: str) -> str:
    """Build a human-friendly display path for the response."""
    try:
        return str(local_path.relative_to(Path(cwd).resolve()) if cwd else local_path)
    except ValueError:
        return str(local_path)


@mcp.tool()
async def raise_docs_search(
    query: str,
    limit: int = 10,
    target: str = "",
    cwd: str = "",
) -> str:
    """Search documentation pages on the remote target.

    Args:
        query: Search query.
        limit: Max results to return (default 10).
        target: Optional docs target name (e.g., "confluence"). Empty = default.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_docs_search")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        doc_target = _resolve_docs_target_safe(target or None, _root if cwd else None)
        if doc_target is None:
            return json.dumps({"status": "error", "reason": "No docs target available"})
        try:
            results = doc_target.search(query, limit=limit)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        return json.dumps({"status": "ok", "items": [r.model_dump() for r in results]})

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_docs_get(
    identifier: str,
    target: str = "",
    cwd: str = "",
) -> str:
    """Retrieve a page from the documentation target.

    Args:
        identifier: Page ID on the remote target.
        target: Optional docs target name (e.g., "confluence"). Empty = default.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_docs_get")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        doc_target = _resolve_docs_target_safe(target or None, _root if cwd else None)
        if doc_target is None:
            return json.dumps({"status": "error", "reason": "No docs target available"})
        try:
            page = doc_target.get_page(identifier)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        return json.dumps({"status": "ok", **page.model_dump()})

    return await asyncio.to_thread(_run)


def _publish_remote(
    doc_type: str,
    content: str,
    metadata: dict[str, str],
    project_root: Path | None = None,
    format: str = "markdown",
) -> tuple[str, str]:
    """Attempt remote publish. Returns (url, error) — both empty on skip."""
    doc_target = _resolve_docs_target_safe(project_root=project_root)
    if doc_target is None:
        return "", ""
    try:
        result = doc_target.publish(
            doc_type=doc_type,
            content=content,
            metadata=metadata,
            format=format,
        )
        if not result.success:
            return "", result.message or "publish failed"
        if result.sync_pending:
            return "", result.message or "remote publish pending"
        return result.url, ""
    except Exception as exc:  # noqa: BLE001
        return "", str(exc)


@mcp.tool()
async def raise_docs_write(
    doc_type: str,
    title: str,
    content: str,
    output_path: str,
    parent: str = "",
    cwd: str = "",
    format: str = "markdown",
    local_only: bool = False,
) -> str:
    """Write a governance artifact locally and publish to remote docs target.

    Local write is skipped when RAISE_MCP_TRANSPORT=http (server context).

    Args:
        doc_type: Artifact type (e.g., "epic-scope", "story-design", "adr").
        title: Document title.
        content: Content to write -- Markdown by default; pass format="html"
            for a self-contained HTML companion (RAISE-16870).
        output_path: Local file path (relative to project root).
        parent: Optional parent page title for remote target.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
        format: Content format, "markdown" (default) or "html". Routes
            Markdown to Confluence/filesystem and HTML to the platform
            target (RAISE-16870) -- does not itself decide when to
            publish HTML by default; that remains RAISE-16647's scope.
        local_only: When True, skip remote publication entirely
            (RAISE-16909). Use for internal governance artifacts (scope,
            design, plan) that should not be pushed to Confluence.
    """
    _raw = _caller_context.require_caller_cwd(cwd, "raise_docs_write")
    if isinstance(_raw, dict):
        return json.dumps(_raw)
    _root: Path = _raw  # narrowed — Pyright can see Path in the closure below

    def _run() -> str:
        is_server = _is_server_context()

        local_path = _resolve_local_path(output_path, str(_root) if cwd else "")

        if not is_server and not local_path.is_absolute():
            # output_path was relative and no usable cwd was provided, so
            # local_path was never anchored. Writing it now would resolve
            # against the MCP server process's os.getcwd() — silently
            # wrong in a multi-worktree setup (RAISE-13024). Fail loud
            # instead of guessing.
            return json.dumps(
                {
                    "status": "error",
                    "reason": (
                        f"output_path '{output_path}' is relative and no "
                        "`cwd` was provided. Pass the caller's working "
                        "directory explicitly as `cwd` — omitting it would "
                        "silently resolve the write against the MCP "
                        "server process's CWD, which is wrong whenever "
                        "the server runs from a different checkout/"
                        "worktree than the caller (RAISE-13024)."
                    ),
                }
            )

        if not is_server:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(content, encoding="utf-8")

        response: dict[str, Any] = {"status": "ok"}
        if not is_server:
            response["output_path"] = _display_path(local_path, cwd)

        if not local_only:
            metadata: dict[str, str] = {"title": title, "path": str(local_path)}
            if parent:
                metadata["parent"] = parent
            remote_url, remote_error = _publish_remote(
                doc_type, content, metadata, _root if cwd else None, format
            )
            if remote_url:
                response["remote_url"] = remote_url
            if remote_error:
                response["remote_warning"] = remote_error

        return compact_response(response)

    return await asyncio.to_thread(_run)
