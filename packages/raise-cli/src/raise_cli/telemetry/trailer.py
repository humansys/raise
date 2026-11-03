"""Inject Claude-Session git trailer into commit messages — S11126.2 (RAISE-11141).

Single responsibility: string manipulation only.
No I/O, no side effects, no Pydantic schemas.

Design decisions in effect:
- D1: Session ID is raw UUID from discover_agent_session_id(), NOT a URL
- D3: Graceful degradation — no session → message unchanged, no error
- D4: New module (SRP, not in emit_work.py)
- D5: Trailer appended after Co-Authored-By as last line
- D6: URL in existing Claude-Session is preserved — never downgraded to a bare
  UUID (RAISE-19207). A URL always carries more traceability than a UUID alone.
- D7: Claude-Parent-Session emitted from RAISE_PARENT_SESSION_ID env var when
  present — CLI parity with MCP path (RAISE-19207).
"""

from __future__ import annotations

import os
import re

_TRAILER_RE = re.compile(r"^Claude-Session:\s+\S+$", re.MULTILINE)
_PARENT_TRAILER_RE = re.compile(r"^Claude-Parent-Session:\s+\S+$", re.MULTILINE)


def resolve_session_id() -> str | None:
    """Resolve session ID from agent session discovery chain.

    Returns None when no session is active (CI, human commits, etc.).
    Delegates to discover_agent_session_id() — lazy import to avoid
    circular imports at module load time.

    Swallows all exceptions so a broken discovery chain never blocks a
    commit (D3 graceful degradation).
    """
    try:
        from raise_cli._agent_session import discover_agent_session_id

        return discover_agent_session_id()
    except Exception:  # noqa: BLE001 — D3: discovery failure must not block commits
        return None


def with_session_trailer(message: str, session_id: str | None) -> str:
    """Append or replace Claude-Session trailer idempotently.

    - No-op when session_id is None or empty (graceful degradation, D3).
    - Replaces any existing Claude-Session line with the new value (idempotent).
    - Appends after Co-Authored-By as last line (D5).

    Args:
        message: The git commit message to modify.
        session_id: The session UUID to inject, or None/empty to skip.

    Returns:
        The message with Claude-Session trailer appended/replaced,
        or the original message unchanged if session_id is falsy.
    """
    if not session_id:
        return message

    new_trailer = f"Claude-Session: {session_id}"

    # Replace existing trailer (handles idempotency + different-sid replacement)
    if _TRAILER_RE.search(message):
        existing_match = _TRAILER_RE.search(message)
        if existing_match is not None and "://" in existing_match.group():
            # D6: existing value is a URL — preserve it, never downgrade to a UUID
            return message
        return _TRAILER_RE.sub(new_trailer, message)

    # Append as last line (no trailing newline)
    return message.rstrip("\n") + f"\n{new_trailer}"


def with_parent_session_trailer(message: str) -> str:
    """Append Claude-Parent-Session trailer from RAISE_PARENT_SESSION_ID env var.

    - No-op when the env var is absent or empty (D3 graceful degradation, D7).
    - Appends as last line, after Claude-Session when both are present.

    Args:
        message: The git commit message to modify.

    Returns:
        The message with Claude-Parent-Session trailer appended, or the original
        message unchanged when RAISE_PARENT_SESSION_ID is falsy.
    """
    parent_sid = os.environ.get("RAISE_PARENT_SESSION_ID", "").strip()
    if not parent_sid:
        return message
    if _PARENT_TRAILER_RE.search(message):
        return message
    return message.rstrip("\n") + f"\nClaude-Parent-Session: {parent_sid}"
