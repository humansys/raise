"""ClaudePlugin — generates RaiSE graph-hints injection config for Claude Code.

Writes the UserPromptSubmit hook that injects neuro-symbolic hints as
additionalContext, plus merges the corresponding block into .claude/settings.json,
via the AgentPlugin.post_init hook called by `rai init --agent claude`.

Architecture: ADR-032 (Multi-agent skill distribution), RAISE-16289 (graph
context injection per agent).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raise_cli.config.agents import AgentConfig

# Public — imported by purge.py as the single source of truth for what
# post_init generates (D1: purge must never drift from what init writes).
USER_PROMPT_SUBMIT_PY_CONTENT = '''\
#!/usr/bin/env python3
"""UserPromptSubmit hook — injects neuro-symbolic hints as additionalContext.

Fail-open: any error → exit 0 (never block the prompt).
Guards:
    CC #17550 — empty transcript_path on first message of new session
    CC #13912 — JSON-only stdout (hookSpecificOutput format required)
    CC #17804 — data-not-instructions in additionalContext
    DD-5      — all failures exit 0, never crash
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt: str = data.get("prompt", "")

    # Guard: first message of new session may have no transcript (CC bug #17550)
    if not data.get("transcript_path"):
        sys.exit(0)

    try:
        from raise_cli.memory.hint_oracle import get_hints, triviality_gate
    except ImportError:
        sys.exit(0)

    if triviality_gate(prompt):
        sys.exit(0)

    try:
        hints = get_hints(prompt, top_k=5)
    except Exception:
        sys.exit(0)

    if not hints:
        sys.exit(0)

    # CC #13912: must print JSON hookSpecificOutput — never plain text
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": hints,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
'''

SETTINGS_USER_PROMPT_SUBMIT_BLOCK: dict[str, Any] = {
    "hooks": [
        {
            "type": "command",
            "command": (
                'REPO_ROOT="$(dirname "$(git rev-parse --git-common-dir)")" && '
                'cd "$REPO_ROOT" && '
                "uv run python .claude/hooks/user-prompt-submit.py || exit 0"
            ),
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
        """Write user-prompt-submit.py and merge the UserPromptSubmit hook.

        Idempotent: re-running does not duplicate the hook in settings.json.

        Args:
            project_root: Project root directory.
            _config: Claude agent configuration (unused — all paths are fixed).

        Returns:
            List of relative file paths created/updated.
        """
        hooks_dir = project_root / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        script_path = hooks_dir / "user-prompt-submit.py"
        script_path.write_text(USER_PROMPT_SUBMIT_PY_CONTENT, encoding="utf-8")

        settings_path = project_root / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings: dict[str, Any] = (
            json.loads(settings_path.read_text(encoding="utf-8"))
            if settings_path.is_file()
            else {}
        )
        hooks = settings.setdefault("hooks", {})
        ups_hooks = hooks.setdefault("UserPromptSubmit", [])
        already_present = any(
            "user-prompt-submit.py" in str(entry) for entry in ups_hooks
        )
        if not already_present:
            ups_hooks.append(SETTINGS_USER_PROMPT_SUBMIT_BLOCK)
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

        return [
            str(script_path.relative_to(project_root)),
            str(settings_path.relative_to(project_root)),
        ]
