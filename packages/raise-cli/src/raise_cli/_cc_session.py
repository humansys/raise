"""Backward compat stub — use _agent_session instead (RAISE-2779)."""

from raise_cli._agent_session import discover_agent_session_id


def discover_cc_session_id() -> str | None:
    """Deprecated: use discover_agent_session_id() instead."""
    return discover_agent_session_id()
