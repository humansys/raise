"""Caller-checkout context for checkout-scoped MCP tools — S15457.2 (E15457).

The MCP server process has NO checkout context of its own: no boot-time
``os.chdir`` (deleted in ``mcp_server.py``), and the process CWD is arbitrary
spawn state. Every checkout-scoped tool resolves from the caller's explicit
``cwd`` parameter — omitting it in community stdio mode is a loud structured
error, never a silent fallback to the server CWD (PAT-E-9604/9605/1474).

Mode awareness (D1): the guard fires only when resolution would be local —
stdio transport AND no server credentials. Under ``RAISE_MCP_TRANSPORT=http``
(JWT-scoped Postgres backends) or configured server credentials (API
backends) the backend carries the context and the guard is inert.

Boot identity assertion (D4): ``--project`` argv (else ``RAISE_PROJECT_ROOT``
env) is an identity ASSERTION consumed only by
``_check_mcp_worktree_identity`` — never a resolution source.

Test seam: ``tests/conftest.py`` patches ``require_caller_cwd`` /
``resolve_run_cwd`` with legacy (inert) semantics so the pre-S15457.2 suite
keeps its server-CWD fallback; the guard's own tests re-install the real
implementations. Tools must therefore call the guard through this module
(``_caller_context.require_caller_cwd(...)``), not a direct name import.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool classification inventory (AC2/AC8) — single source of truth.
# The parametrized guard test iterates CHECKOUT_SCOPED_TOOLS; the inventory
# test asserts every registered tool appears in exactly one list.
# ---------------------------------------------------------------------------

CHECKOUT_SCOPED_TOOLS: tuple[str, ...] = (
    # artifact store
    "raise_artifact_emit",
    "raise_artifact_query",
    # knowledge graph
    "raise_graph_query",
    "raise_graph_context",
    # patterns
    "raise_pattern_query",
    "raise_pattern_add",
    "raise_pattern_reinforce",
    # session
    "raise_signal_emit",
    "raise_session_context",
    "raise_session_history",
    "raise_session_bind",
    "raise_ledger_add",
    "raise_session_open",
    "raise_session_close_full",
    # pipeline (stateful tools use resolve_run_cwd's start_cwd chain, D5)
    "pipeline_list",
    "pipeline_start",
    "pipeline_advance",
    # story bookends
    "raise_story_open",
    "raise_story_close_full",
    # backlog
    "raise_backlog_context",
    "raise_backlog_transition",
    "raise_backlog_create",
    "raise_backlog_update",
    "raise_epic_story_create",
    # docs
    "raise_docs_write",
    "raise_docs_search",
    "raise_docs_get",
    # fleet
    "fleet_dispatch",
    "fleet_approve",
    "fleet_signal",
)

EXEMPT_TOOLS: tuple[str, ...] = (
    # run_id-addressed: shared run state, not checkout state
    "pipeline_status",
    "pipeline_runs",
    "pipeline_pause",
    "pipeline_cancel",
    "pipeline_decision",
    "pipeline_restore",  # cwd = optional; used for lease enrichment + identity check (S15457.4)
    # in-process FleetState; cwd reserved/unused
    "fleet_status",
    # session-id-addressed via env chain; writes global JSONL/server
    "raise_session_topic",
)

# Already fail-loud before S15457.2 — the guard contract was copied from
# these. They keep their original error payloads (caller compatibility).
REFERENCE_GUARDED_TOOLS: tuple[str, ...] = (
    "raise_gate_check",
    "raise_task_complete",
)


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


def _resolution_is_local() -> bool:
    """True when tool state would resolve against the local filesystem.

    Community stdio mode: no HTTP transport, no server credentials. Only
    then does an omitted ``cwd`` constitute a silent-fallback hazard.
    """
    if os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http":
        return False
    from raise_cli.config.server import get_server_credentials

    return get_server_credentials() is None


# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------


# RAISE-15817: platform-specific fallback paths for git resolution.
# When the MCP server is spawned as a stdio subprocess, the child process
# may inherit a minimal environment without the user's PATH.
_GIT_FALLBACK_PATHS: list[Path] = (
    [
        Path(r"C:\Program Files\Git\cmd\git.exe"),
        Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
        Path(os.environ.get("LOCALAPPDATA", ""), "Programs", "Git", "cmd", "git.exe"),
    ]
    if sys.platform == "win32"
    else [
        Path("/usr/bin/git"),
        Path("/usr/local/bin/git"),
        Path("/opt/homebrew/bin/git"),
    ]
)


def _resolve_git() -> str | None:
    """Resolve the git executable, resilient to minimal PATH environments.

    RAISE-15817: when the MCP server is launched as a stdio subprocess,
    PATH inheritance is not guaranteed. ``shutil.which`` alone fails in
    that scenario; platform-specific fallback paths cover the gap.
    """
    found = shutil.which("git")
    if found:
        return found
    for candidate in _GIT_FALLBACK_PATHS:
        if candidate.is_file():
            return str(candidate)
    return None


def _checkout_root(path: Path) -> Path | None:
    """Return the git checkout root containing ``path``, or None.

    Uses ``git rev-parse`` (authoritative) rather than a ``.git`` filesystem
    walk — a stray ``.git`` entry in an ancestor directory (e.g. ``/tmp/.git``)
    does not make the tree below it a checkout.
    """
    import subprocess

    git = _resolve_git()
    if git is None:
        return None

    try:
        result = subprocess.run(
            [git, "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "git rev-parse --show-toplevel timed out in %s — "
            "likely inherited stdin from a live parent pipe",
            path,
        )
        return None
    except OSError:
        return None
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    return Path(top).resolve() if top else None


def _git_common_dir(path: Path) -> Path | None:
    """Return the git common dir for ``path`` (shared across all worktrees).

    ``git rev-parse --git-common-dir`` resolves to the SAME path for the main
    checkout and every linked worktree of that repository — the authoritative
    "same repo" test independent of ``--show-toplevel`` (which differs per
    worktree, RAISE-15912).
    """
    import subprocess

    git = _resolve_git()
    if git is None:
        return None

    try:
        result = subprocess.run(
            [git, "rev-parse", "--git-common-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "git rev-parse --git-common-dir timed out in %s — "
            "likely inherited stdin from a live parent pipe",
            path,
        )
        return None
    except OSError:
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    common = Path(raw)
    if not common.is_absolute():
        common = (path / common).resolve()
    return common.resolve()


def _cwd_error(reason: str, tool: str, message: str) -> dict[str, str]:
    return {"status": "error", "reason": reason, "tool": tool, "message": message}


def require_caller_cwd(cwd: str, tool: str) -> Path | dict[str, str]:
    """Validate the caller-supplied ``cwd`` for a checkout-scoped tool.

    Returns the resolved checkout root Path on success, or a structured
    error dict (JSON-serialize it verbatim as the tool response):

    - ``cwd_required`` — empty cwd in community stdio mode (AC2/AC7)
    - ``cwd_not_absolute`` — relative cwd in ANY mode (PAT-E-9605, RAISE-13024)
    - ``git_not_found`` — git executable not resolvable (RAISE-15817)
    - ``cwd_not_checkout`` — path not inside a git checkout (D2)

    Inert under HTTP transport / server creds: returns ``Path(cwd).resolve()``
    when cwd is given, else ``Path.cwd()`` (legacy behavior, AC10).
    """
    if not cwd:
        if not _resolution_is_local():
            return Path.cwd()
        return _cwd_error(
            "cwd_required",
            tool,
            "The MCP server has no checkout context. Pass the caller's "
            f"absolute checkout path as `cwd` when calling {tool}.",
        )

    raw = Path(cwd)
    if not raw.is_absolute():
        return _cwd_error(
            "cwd_not_absolute",
            tool,
            f"cwd '{cwd}' is not absolute — a relative cwd would silently "
            "anchor against the MCP server process CWD.",
        )
    resolved = raw.resolve()
    if not _resolution_is_local():
        return resolved
    if _resolve_git() is None:
        return _cwd_error(
            "git_not_found",
            tool,
            "git executable not found in PATH or known platform locations — "
            "install git or ensure it is accessible to the MCP server process.",
        )
    root = _checkout_root(resolved)
    if root is None:
        return _cwd_error(
            "cwd_not_checkout",
            tool,
            f"cwd '{cwd}' is not inside a git checkout — pass the absolute "
            "path of the caller's project checkout or worktree.",
        )
    return root


def _worktree_aware_start_cwd(start_cwd: str) -> str:
    """Prefer the caller's current worktree over a stale ``start_cwd`` (RAISE-15912).

    ``start_cwd`` is pinned once at ``pipeline_start``. When the actual work
    later moves to a secondary worktree of the SAME repository — e.g. a story
    branch checked out after the run began — an omitted ``cwd`` on subsequent
    calls must not resolve artifacts against the now-stale main checkout.

    ``Path.cwd()`` is the only signal available when ``cwd`` is omitted; it is
    trusted here only as a fallback preference between two checkouts already
    known to share ``git rev-parse --git-common-dir`` with ``start_cwd`` (the
    RAISE-8470 "same repo" test) — never as an identity assertion.
    """
    current_root = _checkout_root(Path.cwd())
    if current_root is None:
        return start_cwd

    start_root = _checkout_root(Path(start_cwd))
    if current_root == start_root:
        return start_cwd

    current_common = _git_common_dir(current_root)
    start_common = _git_common_dir(Path(start_cwd))
    if current_common is not None and current_common == start_common:
        return str(current_root)
    return start_cwd


def resolve_run_cwd(cwd: str, start_cwd: str, tool: str) -> Path | dict[str, str]:
    """Fallback chain for stateful run-addressed tools (D5, PAT-E-9604).

    explicit ``cwd`` → run-metadata ``start_cwd`` (worktree-aware, RAISE-15912)
    → structured ``cwd_required`` error (community stdio). Inert modes fall
    back to ``Path.cwd()`` when both are empty (legacy behavior).
    """
    if cwd:
        return require_caller_cwd(cwd, tool)
    if start_cwd:
        resolved_start = (
            _worktree_aware_start_cwd(start_cwd)
            if _resolution_is_local()
            else start_cwd
        )
        return require_caller_cwd(resolved_start, tool)
    if not _resolution_is_local():
        return Path.cwd()
    return _cwd_error(
        "cwd_required",
        tool,
        "The MCP server has no checkout context and the run carries no "
        f"start_cwd. Pass the caller's absolute checkout path as `cwd` when "
        f"calling {tool}.",
    )


# ---------------------------------------------------------------------------
# Boot identity assertion (D4) — --project argv, else RAISE_PROJECT_ROOT env.
# The server process CWD is NEVER an assertion source.
# ---------------------------------------------------------------------------


class _Assertion:
    """Mutable holder for the boot identity assertion (avoids `global`)."""

    root: Path | None = None


_assertion = _Assertion()


def set_asserted_root(root: Path | None) -> None:
    """Record the boot-time identity assertion (from parsed ``--project``)."""
    _assertion.root = root


def get_asserted_root() -> Path | None:
    """Return the identity assertion root, or None when the server is unbound."""
    if _assertion.root is not None:
        return _assertion.root
    env = os.environ.get("RAISE_PROJECT_ROOT", "").strip()
    return Path(env) if env else None


def parse_boot_argv(argv: list[str]) -> str:
    """Parse server argv; return the ``--project`` assertion ("" when absent).

    ``--project`` is an identity assertion only — never a resolution source.
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="rai-mcp-pipeline",
        description=(
            "RaiSE Workspace MCP server (stateless — per-call cwd resolves state)."
        ),
    )
    parser.add_argument(
        "--project",
        default="",
        help=(
            "Identity assertion: the checkout this server was provisioned for. "
            "Calls whose cwd resolves elsewhere are rejected (worktree_mismatch). "
            "Never used as a resolution source — per-call `cwd` is."
        ),
    )
    args = parser.parse_args(argv)
    return str(args.project)


def validate_asserted_root(raw: str) -> Path:
    """Validate a ``--project`` assertion: must exist and be a git checkout."""
    import sys

    path = Path(raw).expanduser().resolve()
    if not path.is_dir() or _checkout_root(path) is None:
        sys.stderr.write(
            f"FATAL: --project '{raw}' is not a git checkout — the identity "
            "assertion must name the checkout this server was provisioned for.\n"
        )
        sys.exit(2)
    return path
