"""PostToolUse hook — MCP server staleness detection on git merge.

Detects when a git merge/pull/rebase introduces changes to MCP server
source files and warns the developer to reconnect with ``/mcp``.

Closes the gap between RAISE-8491 (startup-only staleness warning) and
the merge boundary where staleness is actually introduced.

Fail-open on ALL error paths — this hook must never break git operations.

Architecture: S8371.4 (E8371 Control-Plane Resilience)
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Paths under packages/raise-cli/src/raise_cli/ that are part of the
# in-process MCP server. Changes to these files mean the running server
# is executing stale code.
MCP_SOURCE_PREFIXES: tuple[str, ...] = (
    "packages/raise-cli/src/raise_cli/pipeline/",
    "packages/raise-cli/src/raise_cli/task/",
    "packages/raise-cli/src/raise_cli/hooks/",
)

# Regex patterns for git commands that introduce external commits.
# We check individual segments after splitting on && and ; to avoid
# false positives from compound commands like "git status && ls".
_MERGE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgit\s+merge(?!-)(?!.*--abort)"),
    re.compile(r"\bgit\s+pull\b"),
    re.compile(r"\bgit\s+rebase(?!-)(?!.*--abort)"),
)


@dataclass(frozen=True)
class StalenessCheckResult:
    """Result of a post-merge staleness check."""

    is_merge: bool
    changed_server_files: list[str] = field(default_factory=list)
    warning: str | None = None


def is_git_merge_command(command: str) -> bool:
    """Return True if *command* contains a git merge, pull, or rebase.

    Handles compound commands (``&&``, ``;``, ``||``).  Ignores
    ``--abort`` variants which undo a merge rather than completing one.
    """
    if not command:
        return False

    # Split compound commands and check each segment.
    segments = re.split(r"[;&|]+", command)
    return any(
        pattern.search(segment) for segment in segments for pattern in _MERGE_PATTERNS
    )


def get_changed_server_files(changed_files: list[str]) -> list[str]:
    """Filter *changed_files* to those matching MCP server source prefixes."""
    return [
        f
        for f in changed_files
        if any(f.startswith(prefix) for prefix in MCP_SOURCE_PREFIXES)
    ]


def format_warning(server_files: list[str]) -> str | None:
    """Format a human-readable warning for changed server files.

    Returns ``None`` if *server_files* is empty.
    """
    if not server_files:
        return None

    file_list = "\n".join(f"  {f}" for f in sorted(server_files))
    return (
        f"WARNING: MCP server source files changed by this merge:\n"
        f"{file_list}\n"
        f"The rai-workspace MCP server may be running stale code.\n"
        f"Run /mcp to reconnect and reload."
    )


def _git_diff_changed_files(cwd: str | None = None) -> list[str]:
    """Run ``git diff --name-only HEAD@{{1}}..HEAD`` and return changed paths.

    Raises on subprocess failure so the caller can handle it fail-open.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD@{1}..HEAD"],  # noqa: S603 S607
        capture_output=True,
        text=True,
        timeout=5,
        cwd=cwd,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.strip().splitlines() if line]


def evaluate_post_tool_use(
    data: dict[str, object],
    *,
    cwd: str | None = None,
) -> StalenessCheckResult:
    """Evaluate a PostToolUse event for MCP server staleness.

    Args:
        data: JSON payload from Claude Code PostToolUse hook (stdin).
        cwd: Working directory for git commands (defaults to process CWD).

    Returns:
        A :class:`StalenessCheckResult` — always safe, never raises.
    """
    tool_name = str(data.get("tool_name") or "")
    if tool_name != "Bash":
        return StalenessCheckResult(is_merge=False)

    raw_input = data.get("tool_input")
    tool_input: dict[str, object] = raw_input if isinstance(raw_input, dict) else {}
    command = str(tool_input.get("command") or "")

    if not is_git_merge_command(command):
        return StalenessCheckResult(is_merge=False)

    # It's a merge — check what changed.
    try:
        changed_files = _git_diff_changed_files(cwd)
    except Exception:  # noqa: BLE001 — fail-open by design
        logger.debug("[mcp-staleness] git diff failed — proceeding fail-open")
        return StalenessCheckResult(is_merge=True)

    server_files = get_changed_server_files(changed_files)
    warning = format_warning(server_files)

    return StalenessCheckResult(
        is_merge=True,
        changed_server_files=server_files,
        warning=warning,
    )
