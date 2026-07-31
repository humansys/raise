"""Continuity donor resolution for session start."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from raise_cli.schemas.session_state import SessionState
from raise_cli.session.scope import SessionScope, resolve_scope
from raise_cli.session.state import load_session_state
from raise_cli.storage.worktrees import Worktree


class DonorSource(str, Enum):
    """Source selected for session-start continuity."""

    WORKTREE = "worktree"
    LAST_CLOSED = "last_closed"
    FLAT = "flat"
    NONE = "none"


class DonorMismatch(BaseModel):
    """Retained for bundle_data backward-compat serialisation — always None post-S7."""

    worktree_session_id: str
    mission_session_id: str


class ContinuityDonorDecision(BaseModel):
    """Resolved continuity donor for session start."""

    source: DonorSource
    selected_session_id: str | None = None
    state: SessionState | None = None
    worktree_session_id: str | None = None
    mission_session_id: str | None = (
        None  # always None post-S7 (kept for bundle compat)
    )
    mismatch: DonorMismatch | None = (
        None  # always None post-S7 (kept for bundle compat)
    )
    skipped_session_ids: list[str] = Field(default_factory=list[str])


class StateLoader(Protocol):
    """Load session state for a specific session ID or flat fallback."""

    def __call__(
        self, project_path: Path, session_id: str | None = None
    ) -> SessionState | None:
        """Return persisted session state for ``session_id`` or flat fallback."""
        ...


class ScopedClosedLookup(Protocol):
    """Find the latest closed session within the caller's scope."""

    def __call__(
        self, prefix: str, scope: SessionScope, *, project_root: Path
    ) -> str | None:
        """Return the latest closed in-scope session ID, if one exists."""
        ...


def _find_scoped_closed_session(
    prefix: str, scope: SessionScope, *, project_root: Path
) -> str | None:
    from raise_cli.session.index import find_last_closed_in_scope

    return find_last_closed_in_scope(prefix, scope, project_root=project_root)


def _candidate_state(
    *,
    project_path: Path,
    session_id: str,
    load_state: StateLoader,
    skipped_session_ids: list[str],
) -> SessionState | None:
    state = load_state(project_path, session_id=session_id)
    if state is None:
        skipped_session_ids.append(session_id)
    return state


def resolve_continuity_donor(
    *,
    project_path: Path,
    developer_prefix: str,
    agent_session_id: str | None = None,
    active_worktree: Worktree | None = None,
    load_state: StateLoader = load_session_state,
    find_scoped_closed: ScopedClosedLookup = _find_scoped_closed_session,
) -> ContinuityDonorDecision:
    """Resolve the best continuity donor for ``rai session start``.

    Precedence (E15456 design v2, post-S7 ADR-130 mission dissolution):
    worktree-local session (pointer), latest closed session IN SCOPE
    (same worktree; non-empty agent id as tiebreaker; '' never matches;
    unattributable rows excluded), legacy flat state, then no donor.
    Continuity never crosses scope boundaries — absence of an in-scope
    donor yields a clean bundle.
    """
    project_path = project_path.resolve()
    skipped_session_ids: list[str] = []
    worktree_session_id = (
        active_worktree.last_session_id
        if active_worktree is not None and active_worktree.status == "open"
        else None
    )

    if worktree_session_id is not None:
        state = _candidate_state(
            project_path=project_path,
            session_id=worktree_session_id,
            load_state=load_state,
            skipped_session_ids=skipped_session_ids,
        )
        if state is not None:
            return ContinuityDonorDecision(
                source=DonorSource.WORKTREE,
                selected_session_id=worktree_session_id,
                state=state,
                worktree_session_id=worktree_session_id,
                skipped_session_ids=skipped_session_ids,
            )

    scope = resolve_scope(project_path, agent_session_id)
    scoped_closed_id = find_scoped_closed(
        developer_prefix, scope, project_root=project_path
    )
    if scoped_closed_id is not None:
        state = _candidate_state(
            project_path=project_path,
            session_id=scoped_closed_id,
            load_state=load_state,
            skipped_session_ids=skipped_session_ids,
        )
        if state is not None:
            return ContinuityDonorDecision(
                source=DonorSource.LAST_CLOSED,  # last closed within scope
                selected_session_id=scoped_closed_id,
                state=state,
                worktree_session_id=worktree_session_id,
                skipped_session_ids=skipped_session_ids,
            )

    flat_state = load_state(project_path)
    if flat_state is not None:
        return ContinuityDonorDecision(
            source=DonorSource.FLAT,
            state=flat_state,
            worktree_session_id=worktree_session_id,
            skipped_session_ids=skipped_session_ids,
        )

    return ContinuityDonorDecision(
        source=DonorSource.NONE,
        worktree_session_id=worktree_session_id,
        skipped_session_ids=skipped_session_ids,
    )
