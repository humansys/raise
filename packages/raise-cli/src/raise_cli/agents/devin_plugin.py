"""Devin project configuration for RaiSE.

Devin (CLI + Desktop) reads project-scoped MCP servers from
``.devin/config.json`` and lifecycle hooks from ``.devin/hooks.v1.json``.
This plugin keeps RaiSE's native instructions and skills unchanged and adds
only the project-local MCP and hooks projections needed by Devin.

P0 finding (RAISE-15531, validated against devin v3000.2.17):
``.devin/hooks.v1.json`` uses TOP-LEVEL events — the file IS the hooks
object. Nesting events under a ``"hooks"`` wrapper key fails silently.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from raise_cli.config.agents import AgentConfig
from raise_cli.mcp.workspace_config import (
    WORKSPACE_COMMAND,
    WORKSPACE_SERVER_NAME,
    workspace_server_entry,
)

_log = logging.getLogger(__name__)
_DEVIN_CONFIG_RELATIVE_PATH = Path(".devin") / "config.json"
_DEVIN_HOOKS_RELATIVE_PATH = Path(".devin") / "hooks.v1.json"

# Minimal SessionStart context injection (< 30 LOC of config by design):
# a single command hook that reminds the agent to read AGENTS.md and where
# the RaiSE skills live. Devin injects SessionStart stdout as context.
_SESSION_START_HOOK: dict[str, Any] = {
    "type": "command",
    "command": (
        "printf '## RaiSE Context\\n"
        "This repository is governed by RaiSE. Read AGENTS.md first and "
        "invoke rai-* skills by name (they live in .agents/skills/).\\n'"
    ),
}


def _managed_mcp_servers(project_root: Path) -> dict[str, dict[str, object]]:
    """Build Devin entries for the RaiSE workspace server.

    Uses workspace_server_entry from the builder module (S15457.3 AC1, D5):
    no hand-composed command/args literals; absolute project_root only
    (AC2/AC3 — never emits ".").
    """
    return {
        WORKSPACE_SERVER_NAME: dict(
            workspace_server_entry(command=WORKSPACE_COMMAND, project_root=project_root)
        ),
    }


def _load_existing(path: Path) -> dict[str, Any]:
    """Load an existing JSON mapping, recovering cleanly from malformed JSON."""
    if not path.exists():
        return {}
    try:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _log.warning("Replacing malformed Devin config %s: %s", path, exc)
        return {}
    if not isinstance(parsed, dict):
        _log.warning("Replacing non-object Devin config %s", path)
        return {}
    return dict(parsed)


def _entry_commands(entry: object) -> set[str]:
    """Extract hook command strings from a hooks event entry."""
    if not isinstance(entry, dict):
        return set()
    hooks = entry.get("hooks", [])
    if not isinstance(hooks, list):
        return set()
    return {
        hook["command"]
        for hook in hooks
        if isinstance(hook, dict) and isinstance(hook.get("command"), str)
    }


def _merge_hooks(existing: dict[str, Any]) -> dict[str, Any]:
    """Upsert the RaiSE SessionStart hook without clobbering user hooks.

    Other events and foreign entries are preserved; the RaiSE hook is
    appended only when its command is not already present (idempotent).
    """
    merged = dict(existing)
    event = "SessionStart"
    managed_entry: dict[str, Any] = {"hooks": [dict(_SESSION_START_HOOK)]}
    managed_commands = _entry_commands(managed_entry)

    current = merged.get(event)
    if not isinstance(current, list):
        merged[event] = [managed_entry]
        return merged

    existing_commands: set[str] = set()
    for entry in current:
        existing_commands |= _entry_commands(entry)
    if not managed_commands <= existing_commands:
        current.append(managed_entry)
    return merged


class DevinPlugin:
    """Generate RaiSE's project-scoped Devin MCP and hooks configuration."""

    def transform_instructions(self, content: str, _config: AgentConfig) -> str:
        """Return instructions unchanged; ``AGENTS.md`` is native to Devin."""
        return content

    def transform_skill(
        self,
        frontmatter: dict[str, Any],
        body: str,
        _config: AgentConfig,
    ) -> tuple[dict[str, Any], str]:
        """Return skills unchanged; RaiSE skills use Devin's native format."""
        return dict(frontmatter), body

    def post_init(self, project_root: Path, _config: AgentConfig) -> list[str]:
        """Upsert RaiSE MCP and SessionStart hook into Devin's project config."""
        devin_dir = project_root / ".devin"
        devin_dir.mkdir(parents=True, exist_ok=True)

        config_path = project_root / _DEVIN_CONFIG_RELATIVE_PATH
        data = _load_existing(config_path)
        existing_servers = data.get("mcpServers", {})
        mcp_servers = (
            dict(existing_servers) if isinstance(existing_servers, dict) else {}
        )
        mcp_servers.update(_managed_mcp_servers(project_root))
        data["mcpServers"] = mcp_servers
        config_path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )

        hooks_path = project_root / _DEVIN_HOOKS_RELATIVE_PATH
        hooks = _merge_hooks(_load_existing(hooks_path))
        hooks_path.write_text(
            json.dumps(hooks, indent=2) + "\n",
            encoding="utf-8",
        )

        return [
            str(_DEVIN_CONFIG_RELATIVE_PATH),
            str(_DEVIN_HOOKS_RELATIVE_PATH),
        ]
