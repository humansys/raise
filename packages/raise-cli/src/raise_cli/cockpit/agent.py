"""Agent detection for the cockpit agent picker (S14777.3).

Detects available agents by presence of marker files/directories in a worktree.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DetectedAgent:
    """A detected agent available for launching from the cockpit."""

    key: str
    """Single-char hotkey: c, o, h, s."""

    name: str
    """Display name: 'Claude Code', 'Codex CLI', etc."""

    description: str
    """Brief description shown in the picker overlay."""

    cmd: str
    """Launch command: 'claude', 'codex', 'hermes', 'bash'."""

    args: list[str]
    """Default args passed to the command."""

    available: bool = True
    """False if cmd not found in PATH (still shown, but not launchable)."""


def detect_agents(worktree_path: Path) -> list[DetectedAgent]:
    """Return agents detected by presence of marker files in worktree_path.

    Detection rules (checked in order):
    - claude: .claude/ dir or CLAUDE.md → key='c', cmd='claude'
    - codex:  .codex/ dir or AGENTS.md  → key='o', cmd='codex'
    - hermes: .hermes/ dir              → key='h', cmd='hermes'
    - shell:  always available          → key='s', cmd='bash'

    Args:
        worktree_path: Path to the worktree to inspect.

    Returns:
        List of detected agents, shell always last.
    """
    agents: list[DetectedAgent] = []

    # claude
    if (worktree_path / ".claude").exists() or (worktree_path / "CLAUDE.md").exists():
        available = shutil.which("claude") is not None
        agents.append(
            DetectedAgent(
                key="c",
                name="Claude Code",
                description="interactive session",
                cmd="claude",
                args=[],
                available=available,
            )
        )

    # codex
    if (worktree_path / ".codex").exists() or (worktree_path / "AGENTS.md").exists():
        available = shutil.which("codex") is not None
        agents.append(
            DetectedAgent(
                key="o",
                name="Codex CLI",
                description="sandboxed autonomous",
                cmd="codex",
                args=[],
                available=available,
            )
        )

    # hermes
    if (worktree_path / ".hermes").exists():
        available = shutil.which("hermes") is not None
        agents.append(
            DetectedAgent(
                key="h",
                name="Hermes",
                description="declarative config",
                cmd="hermes",
                args=[],
                available=available,
            )
        )

    # shell — always present
    agents.append(
        DetectedAgent(
            key="s",
            name="Shell",
            description="terminal only",
            cmd="bash",
            args=[],
            available=True,
        )
    )

    return agents
