"""ClaudePlugin — generates RaiSE graph-hints injection config for Claude Code.

Merges the UserPromptSubmit hook block into .claude/settings.json via
AgentPlugin.post_init, called by `rai init --agent claude`.

The hook invokes `rai hook user-prompt-submit` directly — no external Python
script required (RAISE-17307: eliminates uv-run implicit sync and raise_cli
import failure when rai is distributed as a binary).

Architecture: ADR-032 (Multi-agent skill distribution), RAISE-16289 (graph
context injection per agent).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from raise_cli.config.agents import AgentConfig

_HOOK_COMMAND_POSIX = (
    'REPO_ROOT="$(dirname "$(git rev-parse --git-common-dir)")" && '
    'cd "$REPO_ROOT" && '
    "rai hook user-prompt-submit || exit 0"
)

_HOOK_COMMAND_WINDOWS = (
    'set REPO_ROOT="$(dirname "$(git rev-parse --git-common-dir)")" && '
    "cd %REPO_ROOT% && "
    "rai hook user-prompt-submit"
)

SETTINGS_USER_PROMPT_SUBMIT_BLOCK: dict[str, Any] = {
    "hooks": [
        {
            "type": "command",
            "command": _HOOK_COMMAND_POSIX,
        }
    ]
}

# Expected settings.json for a project with no pre-existing hooks — the
# shape purge.py compares against to detect a fully rai-owned, unmodified
# file (D1/D2, same pattern as MCP_JSON_CONTENT in purge.py).
SETTINGS_JSON_CONTENT: dict[str, Any] = {
    "hooks": {"UserPromptSubmit": [SETTINGS_USER_PROMPT_SUBMIT_BLOCK]}
}


class ClaudePlugin:
    """Generate RaiSE graph-hints injection config for Claude Code.

    Pass-through for skill/instructions transforms — CLAUDE.md and SKILL.md
    are native Claude Code formats that need no transformation.
    """

    def transform_instructions(self, content: str, _config: AgentConfig) -> str:
        """Return instructions unchanged — CLAUDE.md is native Claude Code format."""
        return content

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, _config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Return skill unchanged — SKILL.md is native Claude Code format."""
        return dict(frontmatter), body

    def post_init(self, project_root: Path, _config: AgentConfig) -> list[str]:
        """Merge the UserPromptSubmit hook block into .claude/settings.json.

        Idempotent: re-running does not duplicate the hook in settings.json.
        No external Python script is written — the hook invokes the rai binary
        directly via `rai hook user-prompt-submit` (RAISE-17307).

        Args:
            project_root: Project root directory.
            _config: Claude agent configuration (unused — all paths are fixed).

        Returns:
            List of relative file paths created/updated.
        """
        command = (
            _HOOK_COMMAND_WINDOWS if sys.platform == "win32" else _HOOK_COMMAND_POSIX
        )
        hook_block: dict[str, Any] = {
            "hooks": [{"type": "command", "command": command}]
        }

        settings_path = project_root / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings: dict[str, Any] = (
            json.loads(settings_path.read_text(encoding="utf-8"))
            if settings_path.is_file()
            else {}
        )
        hooks = settings.setdefault("hooks", {})
        ups_hooks = hooks.setdefault("UserPromptSubmit", [])
        if any("rai hook user-prompt-submit" in str(e) for e in ups_hooks):
            pass  # already migrated — idempotent no-op
        elif any("user-prompt-submit.py" in str(e) for e in ups_hooks):
            # Migrate: replace old uv-run entry in-place (RAISE-17307)
            for i, e in enumerate(ups_hooks):
                if "user-prompt-submit.py" in str(e):
                    ups_hooks[i] = hook_block
                    break
        else:
            ups_hooks.append(hook_block)
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

        return [str(settings_path.relative_to(project_root))]
