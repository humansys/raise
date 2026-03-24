"""Session identity — timestamp-based ID generation.

Session IDs use the format S-{prefix}-{YYMMDD}-{HHMM} where:
- prefix: developer prefix from ~/.rai/developer.yaml (e.g., "E")
- timestamp: session start time, minute resolution

This format requires no coordination (counter, lock, or git pull)
and never collides across worktrees, branches, or machines.
"""

from __future__ import annotations

from datetime import datetime


def generate_session_id(prefix: str, *, now: datetime | None = None) -> str:
    """Generate a timestamp-based session ID.

    Args:
        prefix: Developer prefix (e.g., "E", "EO").
        now: Timestamp to use. Defaults to current time.

    Returns:
        Session ID in format ``S-{prefix}-{YYMMDD}-{HHMM}``.

    Example:
        >>> generate_session_id("E", now=datetime(2026, 3, 22, 14, 30))
        'S-E-260322-1430'
    """
    ts = now or datetime.now()
    return f"S-{prefix}-{ts.strftime('%y%m%d-%H%M')}"
