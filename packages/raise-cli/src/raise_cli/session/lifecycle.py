"""Session lifecycle types — RAISE-17550 (E17495 S1).

Types (SessionMeta, SessionOpenError) and helpers live here (session layer / Layer 2).
ensure_session_lifecycle() lives in raise_cli.pipeline.lifecycle (Layer 1) where it
can import raise_cli.onboarding and raise_cli.hooks (Layer 1 siblings).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SessionOpenError(Exception):
    """Session open cannot proceed: no profile or bad state."""


class SessionMeta(BaseModel, frozen=True):
    """Structured outcome of ensure_session_lifecycle()."""

    session_id: str
    started: datetime
    worktree_id: str = ""
    donor_state: Any | None = None
    stale_sessions: list[Any] = []
    upgraded: list[str] = []
    agent_session_id: str | None = None
    warnings: list[str] = []
