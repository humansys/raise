"""CodexPlugin — generates RaiSE governance config for Codex CLI.

Creates project hooks/config plus a self-contained, installable Codex plugin
package via the AgentPlugin.post_init hook called by `rai init --agent codex`.

Architecture: ADR-032 (Multi-agent skill distribution), ADR-033 (Open-Core Adapter).
"""

from __future__ import annotations

import json
import shutil
import stat
from pathlib import Path
from typing import Any

from raise_cli.config.agents import AgentConfig
from raise_cli.mcp.workspace_config import (
    detect_mcp_pipeline_command,
    render_codex_config_toml,
)

_HOOKS_JSON: dict[str, Any] = {
    "hooks": {
        "SessionStart": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ".codex-plugin/hooks/session_start.sh",
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ".codex-plugin/hooks/pre_tool_use.sh",
                    }
                ]
            },
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "uv run python .codex-plugin/hooks/cwd_binding.py",
                    }
                ]
            },
        ],
        "PostToolUse": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ".codex-plugin/hooks/post_tool_use.sh",
                    }
                ]
            }
        ],
    }
}

_PLUGIN_JSON: dict[str, Any] = {
    "name": "raise-governance",
    "version": "1.0.0",
    "description": "RaiSE AI governance — pipelines, gates, patterns",
    "skills": "./skills/",
}

_MARKETPLACE_JSON: dict[str, Any] = {
    "name": "raise-governance",
    "interface": {"displayName": "RaiSE Governance"},
    "plugins": [
        {
            "name": "raise-governance",
            "source": {
                "source": "local",
                "path": "./plugins/raise-governance",
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            "category": "Developer Tools",
        }
    ],
}

_SESSION_START_SH = """\
#!/usr/bin/env bash
# Injects RaiSE constitutional context at session start.
# Codex CLI injects stdout from SessionStart hooks as system context.
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cwd','.'))" 2>/dev/null || echo ".")
cd "$CWD" 2>/dev/null || exit 0
command -v rai &>/dev/null || exit 0

# --- Identity ---
printf "## RaiSE Context\\n\\n"
printf "You are Rai, the RaiSE AI governance agent. "
printf "RaiSE (Reliable AI Software Engineering) is a methodology and CLI framework "
printf "that adds governance, pipelines, gates, and patterns to AI-assisted development.\\n\\n"

# --- Developer profile (parse YAML with grep — no deps) ---
PROFILE_FILE="${RAI_HOME:-$HOME/.rai}/developer.yaml"
if [ -f "$PROFILE_FILE" ]; then
    DEV_NAME=$(grep "^name:" "$PROFILE_FILE" | head -1 | sed 's/name: *//')
    DEV_LEVEL=$(grep "^experience_level:" "$PROFILE_FILE" | head -1 | sed 's/experience_level: *//')
    DEV_LANG=$(grep "^  language:" "$PROFILE_FILE" | head -1 | sed 's/ *language: *//')
    [ -n "$DEV_NAME" ] && printf "Developer: %s | Level: %s | Language: %s\\n\\n" "$DEV_NAME" "${DEV_LEVEL:-ha}" "${DEV_LANG:-en}"
fi

# --- Active story + phase ---
STORY=$(rai session state --field active_story 2>/dev/null || true)
PHASE=$(rai session state --field phase 2>/dev/null || true)
[ -n "$STORY" ] && printf "Active story: %s (phase: %s)\\n\\n" "$STORY" "${PHASE:-unknown}"

# --- Skills ---
printf "Skills available: ask Codex to use any rai-* skill by name (e.g. rai-session-start, rai-story-implement).\\n"
printf "Skills location: .agent/skills/\\n"

# --- Graph hints ---
rai session context --sections graph_hints 2>/dev/null || true

exit 0
"""

_PRE_TOOL_USE_SH = """\
#!/usr/bin/env bash
# Blocks tool execution when a RaiSE HITL gate is pending approval.
# Exits 2 (block) with reason on stderr; exits 0 (allow) otherwise.
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cwd','.'))" 2>/dev/null || echo ".")
cd "$CWD" 2>/dev/null || exit 0
command -v rai &>/dev/null || exit 0
GATE=$(rai pipeline gate-check --quiet 2>/dev/null || true)
if [ -n "$GATE" ]; then
    printf "Gate pending: %s — approve with: rai pipeline approve\\n" "$GATE" >&2
    exit 2
fi
exit 0
"""

_CWD_BINDING_PY = """\
#!/usr/bin/env python3
\"\"\"Codex PreToolUse hook — CWD binding enforcement (ADR-098 Tier 1, E-FLEET-1).

Precondición: session_id llega en el JSON stdin de Codex (campo 'session_id').
No hay env var equivalente a RAISE_CC_SESSION_ID en Codex v1.

Limitación v1: Todos los tools de Codex (shell_command, exec_command, apply_patch)
devuelven None de extract_target_path → fail-open. La infrastructure queda
instalada para cuando Codex exponga tools con file_path extraíble (ADR-098 §Lim).
\"\"\"
import json
import os
import sys
from pathlib import Path


def main() -> int:
    try:
        data: dict[str, object] = json.loads(sys.stdin.read() or "{}")
        cwd = str(data.get("cwd") or os.getcwd())
        from raise_cli.cwd_binding import LocalCoordinationStore, evaluate_pretooluse

        store = LocalCoordinationStore(project=Path(cwd))
        return evaluate_pretooluse(data, dict(os.environ), store)
    except ImportError:
        print(
            "[cwd-binding] WARNING: raise-cli not available — fail-open",
            file=sys.stderr,
        )
        return 0
    except Exception as exc:  # noqa: BLE001 — fail-open by design
        print(
            f"[cwd-binding] ERROR: internal failure — fail-open: {exc}",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
"""

_POST_TOOL_USE_SH = """\
#!/usr/bin/env bash
# PostToolUse — governance trail signal + MCP staleness detection.
# Fire-and-forget on all paths: never blocks the agent.
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cwd','.'))" 2>/dev/null || echo ".")
TOOL=$(echo "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || true)
cd "$CWD" 2>/dev/null || exit 0
command -v rai &>/dev/null || exit 0

# 1. Emit governance signal.
rai signal emit tool_use --tool "$TOOL" --quiet 2>/dev/null || true

# 2. MCP staleness check (same logic as Claude Code's PostToolUse/Bash hook).
# Warns when a git merge/pull/rebase changes MCP server source files and the
# running server is now stale. RAISE_CC_SESSION_ID is unavailable in Codex v1
# but the staleness module is session-agnostic and works without it.
echo "$INPUT" | uv run python -m raise_cli.hooks.posttooluse 2>/dev/null || true

exit 0
"""


class CodexPlugin:
    """Generate RaiSE governance config files for Codex CLI.

    Pass-through for skill/instructions transforms — agentskills.io SKILL.md
    and AGENTS.md are native Codex formats that need no transformation.
    """

    def transform_instructions(self, content: str, _config: AgentConfig) -> str:
        """Return instructions unchanged — AGENTS.md is native Codex format."""
        return content

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, _config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Return skill unchanged — agentskills.io SKILL.md is native Codex format."""
        return dict(frontmatter), body

    def post_init(self, project_root: Path, _config: AgentConfig) -> list[str]:
        """Generate Codex CLI governance config files.

        Creates:
          .agents/plugins/marketplace.json — exposes the package as a Codex marketplace
          .codex/hooks.json          — wires 3 RaiSE hook scripts
          .codex/config.toml         — rai-workspace MCP server entry
          plugins/raise-governance/  — portable plugin package + RaiSE skills
          .codex-plugin/hooks/session_start.sh
          .codex-plugin/hooks/pre_tool_use.sh
          .codex-plugin/hooks/post_tool_use.sh

        Args:
            project_root: Project root directory.
            _config: Codex agent configuration (unused — all paths are fixed).

        Returns:
            List of relative file paths created.
        """
        codex_dir = project_root / ".codex"
        hooks_dir = project_root / ".codex-plugin" / "hooks"
        plugin_dir = project_root / "plugins" / "raise-governance"
        plugin_manifest_dir = plugin_dir / ".codex-plugin"
        plugin_skills_dir = plugin_dir / "skills"
        marketplace_dir = project_root / ".agents" / "plugins"

        codex_dir.mkdir(parents=True, exist_ok=True)
        hooks_dir.mkdir(parents=True, exist_ok=True)
        plugin_manifest_dir.mkdir(parents=True, exist_ok=True)
        marketplace_dir.mkdir(parents=True, exist_ok=True)

        created: list[str] = []

        hooks_json_path = codex_dir / "hooks.json"
        hooks_json_path.write_text(json.dumps(_HOOKS_JSON, indent=2), encoding="utf-8")
        created.append(str(hooks_json_path.relative_to(project_root)))

        mcp_cmd = detect_mcp_pipeline_command(project_root)
        config_toml_path = codex_dir / "config.toml"
        config_toml_path.write_text(
            render_codex_config_toml(
                command=mcp_cmd,
                project_root=project_root,
            ),
            encoding="utf-8",
        )
        created.append(str(config_toml_path.relative_to(project_root)))

        source_skills_dir = project_root / ".agent" / "skills"
        if source_skills_dir.is_dir():
            shutil.copytree(source_skills_dir, plugin_skills_dir, dirs_exist_ok=True)
        else:
            plugin_skills_dir.mkdir(parents=True, exist_ok=True)

        plugin_json_path = plugin_manifest_dir / "plugin.json"
        plugin_json_path.write_text(
            json.dumps(_PLUGIN_JSON, indent=2), encoding="utf-8"
        )
        created.append(str(plugin_json_path.relative_to(project_root)))

        # The project-scoped .codex/config.toml is the sole MCP owner. Remove
        # stale plugin-local manifests left by earlier rai init versions.
        mcp_manifest_path = plugin_dir / ".mcp.json"
        mcp_manifest_path.unlink(missing_ok=True)

        marketplace_path = marketplace_dir / "marketplace.json"
        marketplace_path.write_text(
            json.dumps(_MARKETPLACE_JSON, indent=2), encoding="utf-8"
        )
        created.append(str(marketplace_path.relative_to(project_root)))

        for name, content, executable in [
            ("session_start.sh", _SESSION_START_SH, True),
            ("pre_tool_use.sh", _PRE_TOOL_USE_SH, True),
            ("post_tool_use.sh", _POST_TOOL_USE_SH, True),
            ("cwd_binding.py", _CWD_BINDING_PY, True),
        ]:
            script_path = hooks_dir / name
            script_path.write_text(content, encoding="utf-8")
            if executable:
                script_path.chmod(
                    script_path.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )
            created.append(str(script_path.relative_to(project_root)))

        return created
