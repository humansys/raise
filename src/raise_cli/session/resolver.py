"""Session ID resolution logic.

Resolves session ID from --session flag or RAI_SESSION_ID env var
following priority order: flag > env var > error (or None for optional).
"""

from __future__ import annotations

from raise_cli.exceptions import RaiSessionNotFoundError


def _normalize_session_id(session_id: str) -> str:
    """Normalize session ID to standard format.

    Accepts:
    - "SES-E-20260322T1430" (new timestamp-based format)
    - "SES-177" (legacy sequential format)
    - "ses-177" (lowercase prefix)
    - "177" (numeric only — legacy shorthand)

    Rejects values containing path traversal components (CWE-23) since
    session IDs are used to construct file paths.

    Returns:
        Normalized session ID (uppercased if starts with SES-).

    Raises:
        ValueError: If session_id contains '..' or path separator characters.
    """
    session_id = session_id.strip()

    if not session_id:
        return session_id  # Empty string, caller will handle

    # CWE-23: Reject path traversal components before any path construction.
    # Session IDs flow from env vars (RAI_SESSION_ID) into get_session_dir().
    if ".." in session_id or "/" in session_id or "\\" in session_id:
        raise ValueError(
            f"Invalid session ID — path traversal characters detected: {session_id!r}"
        )

    # Already normalized (case-insensitive check)
    if session_id.upper().startswith("SES-"):
        return session_id.upper()

    # Numeric only — add prefix
    if session_id.isdigit():
        return f"SES-{session_id}"

    # Unknown format — return as-is (let caller handle invalid formats)
    return session_id


def resolve_session_id(
    session_flag: str | None,
    env_var: str | None,
) -> str:
    """Resolve session ID from flag or environment variable.

    Resolution priority:
    1. --session flag (explicit, per-command)
    2. RAI_SESSION_ID env var (per-terminal/process)
    3. RaiSessionNotFoundError (no session context)

    Normalization:
    - "177" → "SES-177"
    - "ses-177" → "SES-177"
    - "SES-177" → "SES-177" (no change)

    Args:
        session_flag: Value from --session CLI flag.
        env_var: Value from RAI_SESSION_ID environment variable.

    Returns:
        Normalized session ID (e.g., "SES-177").

    Raises:
        RaiSessionNotFoundError: When neither flag nor env var is provided.

    Example:
        >>> resolve_session_id(session_flag="177", env_var=None)
        'SES-177'
        >>> resolve_session_id(session_flag=None, env_var="SES-178")
        'SES-178'
    """
    # Priority 1: --session flag
    if session_flag and session_flag.strip():
        return _normalize_session_id(session_flag)

    # Priority 2: RAI_SESSION_ID env var
    if env_var and env_var.strip():
        return _normalize_session_id(env_var)

    # Priority 3: Error
    raise RaiSessionNotFoundError(
        "No session ID provided",
        hint="Pass --session SES-NNN or set RAI_SESSION_ID environment variable",
    )


def resolve_session_id_optional(
    session_flag: str | None,
    env_var: str | None,
) -> str | None:
    """Resolve session ID, returning None when neither source is provided.

    Same resolution priority as resolve_session_id but returns None instead
    of raising when no session context exists. Use for commands where
    --session is optional (e.g., telemetry emit commands).

    Args:
        session_flag: Value from --session CLI flag.
        env_var: Value from RAI_SESSION_ID environment variable.

    Returns:
        Normalized session ID, or None if neither source provided.
    """
    # Priority 1: --session flag
    if session_flag and session_flag.strip():
        return _normalize_session_id(session_flag)

    # Priority 2: RAI_SESSION_ID env var
    if env_var and env_var.strip():
        return _normalize_session_id(env_var)

    # Priority 3: None (no session context — that's OK)
    return None
