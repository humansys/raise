"""Session scope identity — S15456.1 (E15456, design v2).

``resolve_scope()`` is the single scope-identity function (design contract):
every write/read path that needs to know "which worktree + which agent does
this session belong to" resolves it here. S15456.1 wired it into the open
and close write paths; S15456.3 wired donor, ``rai session context`` and
``rai session measure``; history/ledger read paths follow in S15456.4.

Binding decisions:
- D3: the main checkout is represented as ``worktree_id=''`` — never NULL,
  never the literal ``'main'``.
- D1: an empty ``agent_session_id`` is NOT a matchable key — ``''`` must
  never equal ``''`` for donation or filtering purposes. Consumers treat
  ``''`` as "unknown agent", never as a criterion.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

logger = logging.getLogger(__name__)


class SessionScope(BaseModel, frozen=True):
    """Resolved scope identity for a session.

    Attributes:
        worktree_id: Registered worktree ID; ``''`` for the main checkout (D3).
        agent_session_id: Agent/runtime session ID; ``''`` when discovery
            failed (D1 — empty never matches anything).
    """

    worktree_id: str = ""
    agent_session_id: str = ""


def resolve_scope(cwd: Path, agent_session_id: str | None = None) -> SessionScope:
    """Resolve the scope identity for a session running at *cwd*.

    ``worktree_id`` comes from the worktree registry (exact resolved-path
    match); an unregistered path IS the main checkout and resolves to ``''``
    (D3).

    ``agent_session_id`` precedence (S15456.3, retro O2): an explicit value —
    including explicit ``''`` — always wins; env discovery
    (``discover_agent_session_id()``) runs only when the kwarg is ``None``.
    ``None`` = "not provided"; ``''`` = explicit empty, never a matchable key
    (D1).

    Scope resolution never raises: registry problems degrade to main scope
    with a warning, so session open/close can never be blocked by
    attribution bookkeeping.
    """
    if agent_session_id is None:
        agent_session_id = discover_agent_session_id()
    worktree_id = ""
    try:
        worktree_id = SqliteWorktreeStore(cwd).get_by_path(str(cwd)).worktree_id
    except WorktreeNotFoundError:
        pass  # not a registered worktree -> main checkout ('')
    except (OSError, sqlite3.Error) as exc:
        logger.warning("resolve_scope: worktree lookup failed for %s: %s", cwd, exc)
    return SessionScope(
        worktree_id=worktree_id,
        agent_session_id=agent_session_id or "",
    )
