"""Kimi Code CLI project configuration for RaiSE.

Kimi supports project-scoped MCP configuration at ``.kimi-code/mcp.json``.
This plugin keeps RaiSE's native instructions and skills unchanged and adds
only the project-local MCP projection needed by Kimi.
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
_KIMI_MCP_RELATIVE_PATH = Path(".kimi-code") / "mcp.json"


def _managed_mcp_servers(project_root: Path) -> dict[str, dict[str, object]]:
    """Build Kimi entries for the RaiSE workspace server.

    Uses workspace_server_entry from the builder module (S15457.3 AC1, D5):
    - No _portable_project_args / _RAI_WORKSPACE_ARGS / portability-marker "." logic.
    - Absolute project_root assertion (AC2/AC3 — never emits ".").
    - Always uses WORKSPACE_COMMAND: the registry's stored command may point to
      a stale worktree binary and must not be projected into the Kimi config.
    """
    return {
        WORKSPACE_SERVER_NAME: dict(
            workspace_server_entry(command=WORKSPACE_COMMAND, project_root=project_root)
        ),
    }


def _load_existing(path: Path) -> dict[str, object]:
    """Load an existing Kimi mapping, recovering cleanly from malformed JSON."""
    if not path.exists():
        return {}
    try:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _log.warning("Replacing malformed Kimi MCP config %s: %s", path, exc)
        return {}
    if not isinstance(parsed, dict):
        _log.warning("Replacing non-object Kimi MCP config %s", path)
        return {}
    return dict(parsed)


class KimiPlugin:
    """Generate RaiSE's project-scoped Kimi MCP configuration."""

    def transform_instructions(self, content: str, _config: AgentConfig) -> str:
        """Return instructions unchanged; ``AGENTS.md`` is native to Kimi."""
        return content

    def transform_skill(
        self,
        frontmatter: dict[str, Any],
        body: str,
        _config: AgentConfig,
    ) -> tuple[dict[str, Any], str]:
        """Return skills unchanged; RaiSE skills use Kimi's native format."""
        return dict(frontmatter), body

    def post_init(self, project_root: Path, _config: AgentConfig) -> list[str]:
        """Upsert RaiSE MCP entries into Kimi's project configuration."""
        config_path = project_root / _KIMI_MCP_RELATIVE_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)

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
        return [str(_KIMI_MCP_RELATIVE_PATH)]
