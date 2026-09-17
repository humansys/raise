"""Inject Claude-Session git trailer into commit messages — S11126.2 (RAISE-11141).

Single responsibility: string manipulation only.
No I/O, no side effects, no Pydantic schemas.

Design decisions in effect:
- D1: Session ID is raw UUID from discover_agent_session_id(), NOT a URL
- D3: Graceful degradation — no session → message unchanged, no error
- D4: New module (SRP, not in emit_work.py)
- D5: Trailer appended after Co-Authored-By as last line
"""

from __future__ import annotations

import re

_TRAILER_RE = re.compile(r"^Claude-Session:\s+\S+$", re.MULTILINE)


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
        return _TRAILER_RE.sub(new_trailer, message)

    # Append as last line (no trailing newline)
    return message.rstrip("\n") + f"\n{new_trailer}"
