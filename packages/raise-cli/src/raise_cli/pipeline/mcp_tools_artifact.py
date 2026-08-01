"""Artifact MCP tools — raise_artifact_emit, raise_artifact_query."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from raise_cli.artifacts.models import ARTIFACT_TYPES
from raise_cli.artifacts.store import ArtifactStore
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_instance import mcp
from raise_cli.storage.schema import create_all

_log = logging.getLogger(__name__)


def _get_conn_and_pid(root: Path) -> tuple[sqlite3.Connection, str]:
    """Resolve the project DB connection and project_id for the caller's root."""
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id

    checkout = resolve_checkout_root(root)
    conn = get_project_db(checkout)
    create_all(conn)
    return conn, get_project_id(checkout)


@mcp.tool()
def raise_artifact_emit(
    artifact_type: str,
    story_id: str,
    content: str,
    session_id: str = "",
    cwd: str = "",
) -> str:
    """Validate and persist a structured story artifact.

    Args:
        artifact_type: One of "design", "plan", "implement", "review", "retro".
        story_id: Story identifier (e.g., "s15.2").
        content: JSON string with artifact fields. Schema depends on artifact_type.
        session_id: Optional session ID for traceability.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_artifact_emit")
    if isinstance(_root, dict):
        return json.dumps(_root)
    if artifact_type not in ARTIFACT_TYPES:
        return json.dumps(
            {
                "status": "error",
                "reason": f"Unknown artifact type '{artifact_type}'. Valid: {sorted(ARTIFACT_TYPES)}",
            }
        )

    model_cls = ARTIFACT_TYPES[artifact_type]

    try:
        parsed: dict[str, Any] = json.loads(content)
    except json.JSONDecodeError as exc:
        return json.dumps({"status": "error", "reason": f"Invalid JSON: {exc}"})

    try:
        validated = model_cls.model_validate(parsed)
    except ValidationError as exc:
        details = [
            {"field": ".".join(str(p) for p in e["loc"]), "error": e["msg"]}
            for e in exc.errors()
        ]
        return json.dumps(
            {"status": "error", "reason": "Validation failed", "details": details}
        )

    conn, pid = _get_conn_and_pid(_root)
    store = ArtifactStore(conn, project_id=pid)
    artifact_id = store.save(
        story_id,
        artifact_type,
        validated,
        session_id=session_id or None,
    )

    return compact_response({"status": "ok", "artifact_id": artifact_id})


@mcp.tool()
def raise_artifact_query(
    story_id: str,
    artifact_type: str = "",
    review_type: str | None = None,
    cwd: str = "",
) -> str:
    """Query artifacts by story and optionally by type.

    Args:
        story_id: Story identifier (e.g., "s15.2").
        artifact_type: Filter by type. If empty, returns all artifacts for the story.
        review_type: Optional review discriminator ("architecture" or "quality").
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_artifact_query")
    if isinstance(_root, dict):
        return json.dumps(_root)
    conn, pid = _get_conn_and_pid(_root)
    store = ArtifactStore(conn, project_id=pid)

    if artifact_type:
        if artifact_type == "review" and review_type is None:
            artifacts = store.list(story_id, artifact_type="review")
            return json.dumps({"status": "ok", "artifacts": artifacts})
        artifact = store.get(story_id, artifact_type, review_type=review_type)
        return json.dumps({"status": "ok", "artifact": artifact})

    artifacts = store.list(story_id)
    return json.dumps({"status": "ok", "artifacts": artifacts})
