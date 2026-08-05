"""Execution environment builder for cockpit agent launch (E14777).

Strips ephemeral session vars so the child agent starts clean.
"""

from __future__ import annotations

import os
from pathlib import Path

# Env vars that must not leak into the child agent process.
# These are session-scoped identifiers from the current Claude Code session.
_STRIP_PREFIXES: tuple[str, ...] = (
    "RAISE_CC_SESSION_ID",
    "RAISE_AGENT_SESSION_ID",
    "RAISE_AGENT_RUNTIME",  # stripped then re-injected only when explicitly provided
    "RAISE_CC_HOOK_",
    "RAISE_PIPELINE_LEASE_",
    # RAISE-15050 (AC4): recovery env vars must not propagate to sub-subagents.
    # The cockpit sets RAISE_RECOVERY_RUN_ID when launching a recovery agent;
    # that agent reads it via SessionStart hook and then acts on it. It must not
    # further pass it to any spawned subagents (would re-trigger recovery).
    "RAISE_RECOVERY_",
)


def build_exec_env(
    worktree_path: Path,  # noqa: ARG001
    *,
    agent_session_id: str = "",
    agent_runtime: str = "",
) -> dict[str, str]:
    """Return a copy of os.environ with ephemeral session vars removed.

    After stripping inherited identity, injects fresh launch identity
    when ``agent_session_id`` is provided.

    Args:
        worktree_path: The target worktree path (reserved for future use).
        agent_session_id: Launch identity from prepare_agent_launch.
        agent_runtime: Agent command name (claude/codex/hermes/bash).

    Returns:
        A clean env dict safe to pass to os.execvpe / subprocess.
    """
    env = os.environ.copy()
    for key in list(env):
        if any(key.startswith(prefix) for prefix in _STRIP_PREFIXES):
            del env[key]
    if agent_session_id:
        env["RAISE_AGENT_SESSION_ID"] = agent_session_id
    if agent_runtime:
        env["RAISE_AGENT_RUNTIME"] = agent_runtime
    return env
