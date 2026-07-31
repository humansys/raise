"""CWD binding enforcement core — ADR-098 Tier 1 (S8395.1, E-FLEET-1).

Single entry point: check_write(session_id, cwd, target_path, store).

Design decisions:
- Protocol + logic in raise-core (no SQLite dep) so any runtime can import.
- store injected as parameter (PAT-E-1303: no import-time bindings).
- Fail-open (warning) on: empty session_id, internal error, and — as of
  RAISE-11106 — no active lease + main checkout + a content-path (work/,
  packages/) write. Everything else with no lease stays allowed.
- realpath applied to both paths before comparison (symlink neutralisation).
- .git/ writes are allowed — not content contamination.
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable

_log = logging.getLogger(__name__)


class CwdBindingDecision(str, Enum):
    """Outcome of a per-write CWD binding check."""

    allowed = "allowed"
    rejected = "rejected"
    warning = "warning"  # fail-open — allow but log


@runtime_checkable
class CoordinationStore(Protocol):
    """Read-only view of the coordination data needed to evaluate check_write."""

    def get_session_worktree_path(self, session_id: str) -> str | None:
        """Return the absolute path of the worktree this session has leased.

        Returns None when the session holds no active lease.
        """
        ...

    def get_repo_root(self) -> str:
        """Return the absolute path of the git repository root."""
        ...


def check_write(
    session_id: str,
    cwd: str,  # noqa: ARG001 — provided by adapters; repo root comes from store
    target_path: str,
    store: CoordinationStore,
) -> CwdBindingDecision:
    """Decide whether writing to *target_path* is valid for *session_id*.

    Boundary semantics (ADR-098 §Tier 1):
    1. session_id empty/blank → warning (fail-open, ADR-094 §6).
    2. Session holds no lease:
       a. main checkout + content-path write (work/, packages/) → warning
          (RAISE-11106 — nudge toward a dedicated worktree).
       b. anything else → allowed (not bound to any worktree).
    3. Session leased to worktree P:
       a. target inside P              → allowed
       b. target inside repo, outside P → rejected (incl. main checkout)
       c. target outside repo tree     → allowed
    4. Any internal exception          → warning (fail-open).
    """
    if not session_id.strip():
        _log.warning(
            "check_write: empty session_id — RAISE_AGENT_SESSION_ID not set? "
            "Proceeding fail-open. target=%s",
            target_path,
        )
        return CwdBindingDecision.warning

    try:
        return _check(session_id, target_path, store)
    except Exception:  # noqa: BLE001 — fail-open by design (ADR-094 §6)
        _log.warning(
            "check_write: internal error — proceeding fail-open. target=%s",
            target_path,
            exc_info=True,
        )
        return CwdBindingDecision.warning


def _check(
    session_id: str,
    target_path: str,
    store: CoordinationStore,
) -> CwdBindingDecision:
    repo_root = Path(store.get_repo_root()).resolve()
    target = Path(target_path).resolve()

    worktree_raw = store.get_session_worktree_path(session_id)
    if worktree_raw is None:
        if _is_main_checkout(repo_root) and _is_content_path_write(repo_root, target):
            _log.warning(
                "check_write: no active worktree lease for a content-path write "
                "in the main checkout. session=%s target=%s",
                session_id,
                target,
            )
            return CwdBindingDecision.warning
        return CwdBindingDecision.allowed

    worktree = Path(worktree_raw).resolve()

    target_str = str(target)
    worktree_str = str(worktree)
    repo_str = str(repo_root)

    # Inside the leased worktree — always allowed.
    if _is_under(target_str, worktree_str):
        return CwdBindingDecision.allowed

    # .git/ writes are infrastructure, not content — not a cross-checkout risk.
    git_dir = repo_str + "/.git"
    if _is_under(target_str, git_dir):
        return CwdBindingDecision.allowed

    # Inside repo but outside the leased worktree → cross-checkout contamination.
    if _is_under(target_str, repo_str):
        _log.warning(
            "check_write: REJECTED cross-checkout write. "
            "session=%s worktree=%s target=%s",
            session_id,
            worktree_str,
            target_str,
        )
        return CwdBindingDecision.rejected

    # Outside the repo tree entirely (e.g. /tmp, $HOME) — allowed.
    return CwdBindingDecision.allowed


def _is_under(path: str, parent: str) -> bool:
    """True when *path* is *parent* itself or a descendant of *parent*."""
    parent_with_sep = parent if parent.endswith("/") else parent + "/"
    return path == parent or path.startswith(parent_with_sep)


# Content roots where an unleased write in the main checkout is worth a nudge.
# MVP set — promote to config if it grows beyond a couple of entries.
_CONTENT_ROOTS = ("work", "packages")


def _is_main_checkout(repo_root: Path) -> bool:
    """True when *repo_root* is the primary checkout, not a linked worktree.

    Heuristic: linked worktrees in this codebase are created under one of
    three root conventions — `.worktree/` (see `rai worktree open`; test
    fixtures mirror this as `repo/.worktree/s1`), `.claude/worktrees/` (see
    `_agent_session.py`), or `.rai-worktrees/` (see `pipeline/worktree.py`).
    A repo_root matching none of these is treated as the main checkout.
    This is a naming-convention check, not a git fact — accepted per
    architecture-review Q1 as proportional for this scope; a
    `git rev-parse --git-dir` vs `--git-common-dir` comparison would be more
    robust but adds a subprocess call to a hot path (fires on every write)
    and would require extending CoordinationStore, which is out of scope.
    """
    parts = repo_root.parts
    if ".worktree" in parts or ".rai-worktrees" in parts:
        return False
    return not any(
        parts[i] == ".claude" and parts[i + 1] == "worktrees"
        for i in range(len(parts) - 1)
    )


def _is_content_path_write(repo_root: Path, target: Path) -> bool:
    """True when *target* falls under a content root of *repo_root*.

    Content roots are work/ and packages/ — the paths this nudge cares
    about, as opposed to repo-root config files or unrelated trees.
    """
    try:
        relative = target.relative_to(repo_root)
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] in _CONTENT_ROOTS


def extract_target_path(tool_name: str, tool_input: dict[str, object]) -> str | None:
    """Extract the write-target file path from a CC/Hermes/Codex tool call.

    Returns None for tools with no reliable write target (fail-open).

    CC tools with file_path: Edit, Write.
    Codex tools (shell_command, exec_command, apply_patch): no reliable file_path
    in v1 — fail-open (ADR-098 §Limitaciones, E-FLEET-1).
    """
    match tool_name:
        case "Edit" | "Write":
            raw = tool_input.get("file_path")
            return str(raw) if raw else None
        case "shell_command" | "exec_command" | "apply_patch":
            # Codex v1: file path embedded in shell command string — unparseable reliably.
            return None
        case _:
            return None
