"""CWD binding adapters for raise-cli (S8395.1 + S8395.2).

LocalCoordinationStore — SQLite backend for raise_core.cwd_binding.
evaluate_pretooluse — CC PreToolUse hook evaluator.

Usage:
    from raise_cli.cwd_binding import LocalCoordinationStore, evaluate_pretooluse
    store = LocalCoordinationStore(project=Path(project_root))
    exit_code = evaluate_pretooluse(stdin_data, os.environ, store)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from raise_cli.storage.leases import SqliteLeaseStore
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

_log = logging.getLogger(__name__)


class LocalCoordinationStore:
    """CoordinationStore backed by the project SQLite DB (existing tables).

    Delegates the session → lease read to ``SqliteLeaseStore`` (ADR-094
    capability ``worktree-lease``: no second lease DAO) and resolves
    ``worktree_id`` → path through ``SqliteWorktreeStore``.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._leases = SqliteLeaseStore(project)
        self._worktrees = SqliteWorktreeStore(project)

    def get_session_worktree_path(self, session_id: str) -> str | None:
        """Return the worktree path leased by *session_id*, or None.

        When a session holds several leases (parent + an ``isolation:
        worktree`` subagent sharing its session id and pid), the one with
        the most recent heartbeat wins — RAISE-17602. An orphan lease,
        whose worktree row is gone, answers None so the hook fails open.
        """
        lease = self._leases.get_latest_for_session(session_id)
        if lease is None:
            return None
        try:
            return str(self._worktrees.get_by_name(lease.worktree_id).path)
        except WorktreeNotFoundError:
            return None

    def get_repo_root(self) -> str:
        """Return the project root as the repo boundary."""
        return str(self._project)


def evaluate_pretooluse(
    data: dict[str, object],
    env: dict[str, str],
    store: object,
) -> int:
    """Evaluate a CC PreToolUse event against CWD binding rules.

    Returns 0 (allow) or 2 (block). Fail-open on any unresolvable state.

    Args:
        data: Parsed JSON from CC PreToolUse stdin.
        env: Environment variables dict (typically os.environ).
        store: A CoordinationStore instance (LocalCoordinationStore or stub).
    """
    from raise_core.cwd_binding import (
        CwdBindingDecision,
        check_write,
        extract_target_path,
    )

    tool_name = str(data.get("tool_name") or "")
    raw_input = data.get("tool_input")
    tool_input: dict[str, object] = raw_input if isinstance(raw_input, dict) else {}
    cwd = str(data.get("cwd") or "")
    session_id = str(data.get("session_id") or env.get("RAISE_CC_SESSION_ID") or "")

    target_path = extract_target_path(tool_name, tool_input)
    if target_path is None:
        return 0

    decision = check_write(session_id, cwd, target_path, store)  # type: ignore[arg-type]

    if decision == CwdBindingDecision.rejected:
        _log.warning(
            "[cwd-binding] BLOCKED session=%s target=%s", session_id, target_path
        )
        print(
            f"[cwd-binding] BLOCKED: write to {target_path} rejected.\n"
            f"  Session '{session_id}' is leased to a different worktree.\n"
            f"  Only writes inside your leased worktree are allowed.",
            file=sys.stderr,
        )
        return 2

    if decision == CwdBindingDecision.warning:
        no_lease = False
        try:
            no_lease = store.get_session_worktree_path(session_id) is None  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 — fail-open, fall back to generic message
            no_lease = False

        if no_lease:
            print(
                f"[cwd-binding] WARNING: no active worktree lease for this session"
                f" — writing content ({target_path}) from the main checkout.\n"
                f"  Consider opening a dedicated worktree "
                f"(/rai-worktree-open) for this work.",
                file=sys.stderr,
            )
        else:
            print(
                f"[cwd-binding] WARNING: check inconclusive — proceeding fail-open."
                f" target={target_path}",
                file=sys.stderr,
            )
    return 0
