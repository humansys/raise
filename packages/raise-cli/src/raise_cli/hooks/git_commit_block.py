"""CC PreToolUse hook — blocks raw `git commit` in a fleet-governed worktree.

While a pipeline run is active for the story bound to it.

RAISE-15766, D8.b: defense-in-depth per ADR-2026-08-05 §2, amended —
"A PreToolUse hook blocking raw `git commit` ... is defense-in-depth, not
the primary enforcement." The primary enforcement is the missing
`advance_token`: a fleet subagent that never received it gets
AUTHORITY_DENIED from `pipeline_advance` (F3, live defense). This hook is a
second, independent layer.

Invoked as: uv run python -m raise_cli.hooks.git_commit_block

Scope note (design.md D10/session_governance): this — like the whole
session_governance check set — only matters for an agent whose OWN project
root is the fleet worktree (e.g. a `claude -p` launch rooted there). In-band
fleet subagents are `Agent()`/Task calls INSIDE the director's session
(F12) and inherit the DIRECTOR's `.claude/settings.json`, never a story
worktree's own — so this hook only fires when actually wired into that
worktree's PreToolUse array (checked by
`ProvisioningVerifier`'s `session_governance.hooks.git_commit_block`,
provisioning.py). It is opt-in per worktree, not globally active.

Fail-open on every unresolved case (ADR-094 §6): raise-cli not installed,
worktree unregistered, no story bound, no active run, or any internal
exception. This hook only ever narrows what is otherwise allowed — it must
never be the reason a legitimate commit outside a bound fleet run is lost.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

#: Matches a `git commit` invocation as its own shell command — anchored so
#: it doesn't false-positive on substrings like "digital commit" but still
#: catches it after a `;`/`&&`/`|`/newline chain separator (multi-line Bash
#: tool calls, e.g. "git add .\ngit commit -m x", are the ordinary shape
#: agents emit — RAISE-15766 quality-review R2).
_GIT_COMMIT_RE = re.compile(r"(?:^|[;&|\n]\s*)git\s+commit\b")


def _is_raw_git_commit(command: str) -> bool:
    """True when `command` invokes `git commit` as a standalone shell command."""
    return bool(_GIT_COMMIT_RE.search(command))


async def _has_active_run_for_stories(stories: list[str]) -> bool:
    """True iff the run store has a non-terminal run for any of `stories`."""
    from raise_cli.fleet.subagent_dispatcher import is_active_run_status
    from raise_cli.pipeline.run_store import get_run_store

    store = get_run_store()
    runs = await store.list_runs()
    return any(
        run.get("issue_id") in stories and is_active_run_status(run.get("status"))
        for run in runs
    )


def main() -> int:  # noqa: D103
    try:
        data: dict[str, object] = json.loads(sys.stdin.read() or "{}")
        tool_name = str(data.get("tool_name") or "")
        if tool_name != "Bash":
            return 0

        raw_input = data.get("tool_input")
        tool_input: dict[str, object] = raw_input if isinstance(raw_input, dict) else {}
        command = str(tool_input.get("command") or "")
        if not _is_raw_git_commit(command):
            return 0

        cwd = str(data.get("cwd") or os.getcwd())

        from raise_cli.storage.worktrees import (
            SqliteWorktreeStore,
            WorktreeNotFoundError,
        )

        try:
            worktree = SqliteWorktreeStore(Path(cwd)).get_by_path(cwd)
        except (WorktreeNotFoundError, OSError):
            # Unregistered worktree — nothing to enforce against. Fail-open.
            return 0

        if not worktree.stories:
            return 0

        if asyncio.run(_has_active_run_for_stories(worktree.stories)):
            print(
                "[git-commit-block] BLOCKED: an active fleet pipeline run exists "
                f"for this worktree's story/stories ({', '.join(worktree.stories)}). "
                "Complete the current phase via raise_task_complete / "
                'fleet_signal(event="phase_complete") so the director can advance '
                "it, instead of a raw `git commit` (RAISE-15766, D8.b, "
                "defense-in-depth).",
                file=sys.stderr,
            )
            return 2

        return 0
    except ImportError:
        print(
            "[git-commit-block] WARNING: raise-cli not available — proceeding fail-open",
            file=sys.stderr,
        )
        return 0
    except Exception as exc:  # noqa: BLE001 — fail-open by design
        print(
            f"[git-commit-block] ERROR: internal failure — proceeding fail-open: {exc}",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
