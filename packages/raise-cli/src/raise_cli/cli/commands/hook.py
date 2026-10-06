"""CLI commands for Claude Code hook handlers.

Provides subcommands that Claude Code hooks invoke directly via the rai binary,
eliminating the need for an external Python script or `uv run`.

Commands:
- user-prompt-submit: UserPromptSubmit hook — injects neuro-symbolic hints as
  additionalContext. Reads JSON from stdin, always exits 0 on any error (fail-open).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

hook_app = typer.Typer(
    name="hook",
    help="Claude Code hook handlers (invoked by .claude/settings.json hooks)",
    no_args_is_help=True,
)


@hook_app.callback()
def _hook_group() -> None:  # pyright: ignore[reportUnusedFunction]
    """Claude Code hook handlers (invoked by .claude/settings.json hooks)."""


@hook_app.command("user-prompt-submit")
def user_prompt_submit() -> None:
    """UserPromptSubmit hook — injects neuro-symbolic hints as additionalContext.

    Reads a JSON object from stdin (fields: prompt, transcript_path, cwd).
    Prints a hookSpecificOutput JSON object to stdout when hints are available.
    Exits 0 in all cases — never blocks a prompt (DD-5 fail-open).

    Guards:
        CC #17550 — empty transcript_path on first message of new session
        CC #13912 — JSON-only stdout (hookSpecificOutput format required)
        CC #17804 — data-not-instructions in additionalContext
        DD-5      — all failures exit 0, never crash
    """
    try:
        data = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        raise typer.Exit(0) from None

    prompt: str = data.get("prompt", "")

    # Guard: first message of new session may have no transcript (CC bug #17550)
    if not data.get("transcript_path"):
        raise typer.Exit(0)

    try:
        from raise_cli.memory.hint_oracle import (  # noqa: PLC0415
            get_hints,
            triviality_gate,
        )
    except ImportError:
        raise typer.Exit(0) from None

    if triviality_gate(prompt):
        raise typer.Exit(0)

    # RAISE-16731: pass project_root so hint_oracle queries the right graph
    cwd = data.get("cwd")
    project_root: Path | None = Path(cwd) if cwd else None

    try:
        hints = get_hints(prompt, top_k=5, project_root=project_root)
    except Exception:  # noqa: BLE001
        raise typer.Exit(0) from None

    if not hints:
        raise typer.Exit(0)

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
    raise typer.Exit(0)
