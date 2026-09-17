"""DefaultProvisioningVerifier — implements ProvisioningVerifier (ADR §1, RAISE-15764).

`verify()` is a pure read of filesystem/env/registry state — no writes, no
lease acquisition, no settings.json mutation (ADR §1: "no I/O side
effects"). Two independent check registries (D10):

- session_governance: non-empty PreToolUse/PostToolUse/UserPromptSubmit/
  SessionStart hook arrays + the ADR-098 cwd-binding hook. BLOCKING only
  when checked against the fleet DIRECTOR's own session
  (`verify_director_session`, D10.1). Reported but ADVISORY when checked
  per-story worktree (`verify`) — in-band fleet subagents inherit the
  director's session, not the target worktree's settings.json (F12), so
  gating dispatch on the worktree's file would be governance theater.
- workspace_integrity: the resolved worktree is a real git checkout on its
  registered branch, has a worktree-scoped MCP venv (ADR-129), and its
  lease is acquirable. ALWAYS blocking wherever reported.

Registry is intentionally extensible: RAISE-15766 (D8.b) added
`session_governance.hooks.git_commit_block`, checking for the presence of
its PreToolUse `git commit` block hook (raise_cli.hooks.git_commit_block)
the same way `session_governance.hooks.cwd_binding` checks for ADR-098's.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from raise_cli.storage.leases import SqliteLeaseStore, pid_alive
from raise_cli.storage.worktrees import (
    SqliteWorktreeStore,
    Worktree,
    WorktreeNotFoundError,
)
from raise_core.fleet.protocols import ProvisioningCheck, ProvisioningReport

logger = logging.getLogger(__name__)

#: Maps a Claude Code hook event name to its check's dotted name suffix.
_HOOK_EVENT_CHECK_NAMES: dict[str, str] = {
    "PreToolUse": "hooks.pre_tool_use",
    "PostToolUse": "hooks.post_tool_use",
    "UserPromptSubmit": "hooks.user_prompt_submit",
    "SessionStart": "hooks.session_start",
}

#: Substrings that identify the ADR-098 cwd-binding hook wiring in a
#: PreToolUse command string. The repo's live convention invokes the
#: `raise_cli.hooks.pretooluse` module (which internally calls
#: `evaluate_pretooluse` unconditionally) rather than referencing a
#: standalone `cwd-binding-pre-tool-use.py` script by name — check for
#: either so both conventions are recognized.
_CWD_BINDING_HOOK_MARKERS: tuple[str, ...] = (
    "raise_cli.hooks.pretooluse",
    "cwd-binding-pre-tool-use",
    "cwd_binding",
)

#: Substrings that identify the RAISE-15766 (D8.b) git-commit-block
#: PreToolUse hook wiring in a PreToolUse command string. Mirrors
#: `_CWD_BINDING_HOOK_MARKERS`'s pattern — checks for either the module
#: invocation or a standalone-script name.
_GIT_COMMIT_BLOCK_HOOK_MARKERS: tuple[str, ...] = (
    "raise_cli.hooks.git_commit_block",
    "git-commit-block",
)


def _load_settings(settings_path: Path) -> dict[str, Any]:
    """Read `.claude/settings.json`.

    Returns {} when absent/unreadable — that absence itself is surfaced by
    the hook-array checks below, not here.
    """
    if not settings_path.is_file():
        return {}
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _hook_command_contains(entries: Any, markers: tuple[str, ...]) -> bool:
    """Check whether a hook command in `entries` contains one of `markers`.

    `entries` follows the settings.json hook-array shape:
    [{"matcher": ..., "hooks": [{"command": "..."}]}].
    """
    if not isinstance(entries, list):
        return False
    for entry in entries:
        sub_hooks = entry.get("hooks") if isinstance(entry, dict) else None
        if not isinstance(sub_hooks, list):
            continue
        for sub in sub_hooks:
            command = sub.get("command", "") if isinstance(sub, dict) else ""
            if isinstance(command, str) and any(m in command for m in markers):
                return True
    return False


def _check_session_governance(session_path: str) -> tuple[ProvisioningCheck, ...]:
    """ADR §1 minimum checks (non-empty hook arrays) + ADR-098 cwd-binding hook.

    `session_path` is the root whose `.claude/settings.json` is read — the
    fleet DIRECTOR's own cwd for the D10.1 gate, or a story's resolved
    worktree_path for the (advisory, per D10) per-story report.
    """
    settings_path = Path(session_path) / ".claude" / "settings.json"
    settings = _load_settings(settings_path)
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}

    checks: list[ProvisioningCheck] = []
    for event, suffix in _HOOK_EVENT_CHECK_NAMES.items():
        entries = hooks.get(event)
        satisfied = isinstance(entries, list) and len(entries) > 0
        checks.append(
            ProvisioningCheck(
                name=f"session_governance.{suffix}",
                satisfied=satisfied,
                detail=(
                    ""
                    if satisfied
                    else f"{settings_path} has no {event} hooks configured"
                ),
            )
        )

    cwd_binding_present = _hook_command_contains(
        hooks.get("PreToolUse"), _CWD_BINDING_HOOK_MARKERS
    )
    checks.append(
        ProvisioningCheck(
            name="session_governance.hooks.cwd_binding",
            satisfied=cwd_binding_present,
            detail=(
                ""
                if cwd_binding_present
                else f"{settings_path} PreToolUse is missing the ADR-098 cwd-binding hook"
            ),
        )
    )
    # RAISE-15766 (D8.b): the PreToolUse array is checked above for
    # non-emptiness only — that does not prove THIS specific hook is
    # present, so it gets its own named check, same pattern as cwd_binding.
    git_commit_block_present = _hook_command_contains(
        hooks.get("PreToolUse"), _GIT_COMMIT_BLOCK_HOOK_MARKERS
    )
    checks.append(
        ProvisioningCheck(
            name="session_governance.hooks.git_commit_block",
            satisfied=git_commit_block_present,
            detail=(
                ""
                if git_commit_block_present
                else f"{settings_path} PreToolUse is missing the D8.b "
                "git-commit-block hook"
            ),
        )
    )
    return tuple(checks)


def _load_registered_worktree(worktree_path: str) -> Worktree | None:
    """Read-only lookup of the worktree registry row for `worktree_path`.

    Returns None (not an exception) when unregistered or unreachable —
    callers turn that into an unsatisfied ProvisioningCheck with detail,
    per D2.a's fail-closed convention.
    """
    try:
        store = SqliteWorktreeStore(Path(worktree_path))
        return store.get_by_path(worktree_path)
    except (WorktreeNotFoundError, OSError) as exc:
        logger.debug(
            "provisioning: worktree lookup failed for %s: %s", worktree_path, exc
        )
        return None


def _check_git_worktree(path: Path) -> ProvisioningCheck:
    name = "workspace_integrity.git_worktree"
    is_git = path.is_dir() and (path / ".git").exists()
    return ProvisioningCheck(
        name=name,
        satisfied=is_git,
        detail="" if is_git else f"{path} is not a git checkout (missing .git)",
    )


def _check_expected_branch(
    path: Path, registered: Worktree | None
) -> ProvisioningCheck:
    name = "workspace_integrity.git_branch"
    if registered is None:
        return ProvisioningCheck(
            name=name, satisfied=False, detail=f"{path} is not a registered worktree"
        )
    try:
        # symbolic-ref (not rev-parse --abbrev-ref) so a freshly-provisioned
        # worktree with zero commits — HEAD is unborn, rev-parse fails with
        # "ambiguous argument 'HEAD'" — still resolves its branch name.
        result = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ProvisioningCheck(
            name=name, satisfied=False, detail=f"git branch lookup failed: {exc}"
        )

    if result.returncode != 0:
        return ProvisioningCheck(
            name=name,
            satisfied=False,
            detail=f"git branch lookup failed: {result.stderr.strip()}",
        )

    current = result.stdout.strip()
    if current != registered.branch:
        return ProvisioningCheck(
            name=name,
            satisfied=False,
            detail=f"{path} is on branch '{current}', registry expects '{registered.branch}'",
        )
    return ProvisioningCheck(name=name, satisfied=True)


def _check_mcp_venv_scope(path: Path) -> ProvisioningCheck:
    name = "workspace_integrity.mcp_venv_scope"
    venv_dir = path / ".venv-mcp"
    satisfied = venv_dir.is_dir()
    return ProvisioningCheck(
        name=name,
        satisfied=satisfied,
        detail="" if satisfied else f"no worktree-scoped .venv-mcp at {path} (ADR-129)",
    )


def _check_lease_acquirable(
    worktree_path: str, registered: Worktree | None
) -> ProvisioningCheck:
    name = "workspace_integrity.lease_acquirable"
    if registered is None:
        return ProvisioningCheck(
            name=name,
            satisfied=False,
            detail=f"{worktree_path} is not a registered worktree",
        )
    try:
        lease_store = SqliteLeaseStore(Path(worktree_path))
        lease = lease_store.get(registered.worktree_id)
    except OSError as exc:
        return ProvisioningCheck(
            name=name, satisfied=False, detail=f"lease lookup failed: {exc}"
        )

    if lease is None or not pid_alive(lease.pid):
        return ProvisioningCheck(name=name, satisfied=True)
    return ProvisioningCheck(
        name=name,
        satisfied=False,
        detail=f"worktree leased by session {lease.session_id} (pid {lease.pid})",
    )


def _check_workspace_integrity(worktree_path: str) -> tuple[ProvisioningCheck, ...]:
    path = Path(worktree_path)
    registered = _load_registered_worktree(worktree_path)
    return (
        _check_git_worktree(path),
        _check_expected_branch(path, registered),
        _check_mcp_venv_scope(path),
        _check_lease_acquirable(worktree_path, registered),
    )


class DefaultProvisioningVerifier:
    """Implements `ProvisioningVerifier` — ADR §1, split registry per D10.

    `verify()` is the Protocol method: workspace_integrity (blocking) +
    session_governance (advisory here) for a resolved story worktree.
    `verify_director_session()` is the D10.1 pre-loop gate: session_
    governance ONLY, checked once against the fleet director's own cwd —
    it is not part of the ADR §1 Protocol signature (which takes
    worktree_path + work_id) and is called directly by fleet_dispatch.
    """

    def verify(self, worktree_path: str, work_id: str) -> ProvisioningReport:
        """Check `worktree_path`'s workspace_integrity + session_governance."""
        return ProvisioningReport(
            work_id=work_id,
            session_governance=_check_session_governance(worktree_path),
            workspace_integrity=_check_workspace_integrity(worktree_path),
        )

    def verify_director_session(self, director_cwd: str) -> ProvisioningReport:
        """Check ONLY session_governance for the fleet director's own cwd (D10.1)."""
        return ProvisioningReport(
            work_id="__director__",
            session_governance=_check_session_governance(director_cwd),
            workspace_integrity=(),
        )
