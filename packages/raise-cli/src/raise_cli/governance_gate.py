"""Governance gate — block content-path writes without an active session (RAISE-15129).

PreToolUse check: Edit/Write to work/ or packages/ requires an active
governance session (created by /rai-session-start → raise_session_open).
Fail-open on: empty session ID, DB errors, non-content paths.

This is a HARD gate (exit 2 blocks the tool call), not an advisory message.
"""

from __future__ import annotations

import sys
from pathlib import Path

from raise_core.cwd_binding import extract_target_path

_CONTENT_ROOTS = ("work", "packages")
_ALLOWLISTED_ROOTS = (".raise", ".claude")


def check_governance_gate(
    *,
    tool_name: str,
    tool_input: dict[str, object],
    env: dict[str, str],
    project: Path,
) -> int:
    """Check if a governance session is active before allowing content writes.

    Returns 0 (allow) or 2 (block).
    """
    target_path = extract_target_path(tool_name, tool_input)
    if target_path is None:
        return 0

    resolved = Path(target_path).resolve()
    project_resolved = project.resolve()

    try:
        relative = resolved.relative_to(project_resolved)
    except ValueError:
        return 0

    if not relative.parts:
        return 0

    first = relative.parts[0]

    if first in _ALLOWLISTED_ROOTS:
        return 0

    if first not in _CONTENT_ROOTS:
        return 0

    cc_session_id = env.get("RAISE_CC_SESSION_ID", "").strip()
    if not cc_session_id:
        return 0

    try:
        if _has_active_session(project_resolved, cc_session_id):
            return 0
    except Exception:  # noqa: BLE001 — fail-open (ADR-094 §6)
        return 0

    print(
        f"[governance] BLOCKED: no active governance session for this agent.\n"
        f"  Run /rai-session-start before writing to {first}/.\n"
        f"  Target: {target_path}",
        file=sys.stderr,
    )
    return 2


def _has_active_session(project: Path, cc_session_id: str) -> bool:
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    conn = get_project_db(project)
    create_all(conn)
    pid = get_project_id(project)
    row = conn.execute(
        "SELECT 1 FROM active_sessions"
        " WHERE project_id = ? AND cc_session_id = ?"
        " LIMIT 1",
        (pid, cc_session_id),
    ).fetchone()
    return row is not None
