"""Launch sequence for cockpit agent exec (S14777.3, RAISE-15086).

Wraps os.chdir + env sanitization + os.execvpe in a clean launch flow.
Includes session-detection lease management (ADR-094 cockpit layer).
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from raise_cli.cockpit.agent import DetectedAgent
from raise_cli.cockpit.env import build_exec_env
from raise_cli.storage.leases import Lease, SqliteLeaseStore


class ActiveWorktreeError(Exception):
    """Raised when a live agent session already occupies the target worktree."""

    def __init__(self, holder: Lease) -> None:
        self.holder = holder
        super().__init__(
            f"Worktree '{holder.worktree_id}' has an active session "
            f"'{holder.session_id}' (pid {holder.pid})"
        )


@dataclass
class PreparedLaunch:
    """Result of prepare_agent_launch — carries identity for exec."""

    launch_id: str
    lease_acquired: bool


def prepare_agent_launch(
    store: SqliteLeaseStore,
    worktree_id: str,
    agent: DetectedAgent,
    *,
    allow_conflict: bool = False,
) -> PreparedLaunch:
    """Reserve a worktree lease for the upcoming agent launch.

    Reaps dead-PID holders automatically.  When a live holder exists and
    allow_conflict is False, raises ActiveWorktreeError.  With
    allow_conflict=True the launch proceeds without a lease (the existing
    holder keeps its lease).
    """
    launch_id = f"cockpit:{agent.cmd}:{uuid4().hex}"
    holder = store.get_live_or_reap(worktree_id)

    if holder is not None:
        if not allow_conflict:
            raise ActiveWorktreeError(holder)
        return PreparedLaunch(launch_id=launch_id, lease_acquired=False)

    store.acquire(worktree_id, session_id=launch_id, pid=os.getpid())
    return PreparedLaunch(launch_id=launch_id, lease_acquired=True)


def exec_agent(
    worktree_path: Path,
    agent: DetectedAgent,
    *,
    launch_id: str = "",
    config_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> None:
    """Print warm launch sequence, then os.execvp(e). No return on success.

    Stops the calling process via os.execvpe (Unix) or subprocess (Windows).

    Args:
        worktree_path: Absolute path to the target worktree.
        agent: The selected DetectedAgent to launch.
        launch_id: Session identity from prepare_agent_launch (injected into env).
        config_args: Extra CLI args from stored agent config (model, permissions).
        extra_env: Additional env vars to inject AFTER stripping (RAISE-15050 AC4).
            Used by the cockpit recovery flow to set RAISE_RECOVERY_RUN_ID so
            the child agent's SessionStart hook receives the run ID to restore.
            These vars bypass the strip pass — callers are responsible for only
            passing intent-specific, session-scoped vars (no secrets).
    """
    env = build_exec_env(
        worktree_path,
        agent_session_id=launch_id,
        agent_runtime=agent.cmd,
    )
    if extra_env:
        env.update(extra_env)
    os.chdir(worktree_path)

    print(f"→ worktree  {worktree_path}")
    print(f"→ agent     {agent.name}")
    print("✓ env sanitized")
    print(f"✓ exec {agent.cmd}")

    argv = [agent.cmd, *agent.args, *(config_args or [])]

    if sys.platform == "win32":
        subprocess.run(argv, env=env, check=False)
    else:
        os.execvpe(agent.cmd, argv, env)  # noqa: S606
