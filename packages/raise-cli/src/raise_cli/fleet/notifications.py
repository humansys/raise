"""Fleet notification formatting — SIGNAL_EMOJI dict and format_notification().

Extracted from mcp_tools_fleet._SIGNAL_EMOJI and _format_signal so they can be
tested and reused independently of the MCP layer.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIGNAL_EMOJI: dict[str, str] = {
    "phase_complete": "✅",
    "blocked": "🔴",
    "hitl": "⏸",
    "complete": "🏁",
}

_FALLBACK_EMOJI = "📡"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def format_notification(
    event: str,
    story_key: str,
    payload: dict[str, object] | None = None,
    next_action: str | None = None,
) -> str:
    """Format a fleet notification message.

    Args:
        event: Signal event type (e.g. "phase_complete", "blocked").
        story_key: Jira key of the emitting story (e.g. "RAISE-9508").
        payload: Optional event details rendered on line 2.
        next_action: Optional next-step hint rendered on line 3.

    Returns:
        Multi-line string:
            Line 1: ``{emoji} {story_key} · {event}``
            Line 2 (if payload): ``   {k1: v1, k2: v2, ...}``
            Line 3 (if next_action): ``   → next: {next_action}``
    """
    emoji = SIGNAL_EMOJI.get(event, _FALLBACK_EMOJI)
    lines = [f"{emoji} {story_key} · {event}"]

    if payload:
        detail = ", ".join(f"{k}: {v}" for k, v in payload.items())
        lines.append(f"   {detail}")

    if next_action:
        lines.append(f"   → next: {next_action}")

    return "\n".join(lines)
