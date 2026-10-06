"""Session identity — timestamp-based ID generation.

Session IDs use the format S-{prefix}-{YYMMDD}-{HHMM}-{XXXX} where:
- prefix: developer prefix from ~/.rai/developer.yaml (e.g., "E")
- timestamp: session start time, minute resolution
- XXXX: 4 uppercase hex chars of random entropy (65536 values per minute)

The timestamp keeps ids lexicographically sortable and human-meaningful;
the entropy suffix makes collisions practically impossible (RAISE-15482:
minute-resolution-only ids collided whenever one developer started two
sessions in the same minute, and the second clobbered the first row in
the sessions table, whose PK is session_id). No coordination (counter,
lock, or git pull) is required across worktrees, branches, or machines.
"""

from __future__ import annotations

import secrets
from datetime import datetime


def generate_session_id(
    prefix: str,
    *,
    now: datetime | None = None,
    entropy: str | None = None,
) -> str:
    """Generate a timestamp-based session ID.

    Args:
        prefix: Developer prefix (e.g., "E", "EO").
        now: Timestamp to use. Defaults to current time.
        entropy: 4-char suffix to use. Defaults to random uppercase hex.
            Inject for deterministic tests only.

    Returns:
        Session ID in format ``S-{prefix}-{YYMMDD}-{HHMM}-{XXXX}``.

    Example:
        >>> generate_session_id("E", now=datetime(2026, 3, 22, 14, 30), entropy="AB12")
        'S-E-260322-1430-AB12'
    """
    ts = now or datetime.now()
    suffix = entropy or secrets.token_hex(2).upper()
    return f"S-{prefix}-{ts.strftime('%y%m%d-%H%M')}-{suffix}"
