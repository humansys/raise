"""Session management for the Rai daemon.

SessionState tracks per-connection state.
SessionManager is a Protocol — InMemorySessionManager is the S2.2 implementation.
Migration path: SQLiteSessionManager in S2.4 when CronTrigger introduces the DB.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


@dataclass
class SessionState:
    """Per-connection session state."""

    session_key: str
    connected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    seq: int = 0  # next event sequence number (monotonic)
    agent_session_id: str | None = None  # assigned by ClaudeRuntime in S2.3


class SessionManager(Protocol):
    """Protocol for session storage backends.

    Implementations: InMemorySessionManager (S2.2), SQLiteSessionManager (S2.4).
    connection.py depends only on this Protocol — backend is injected.
    """

    def create(self, session_key: str) -> SessionState: ...
    def get(self, session_key: str) -> SessionState | None: ...
    def remove(self, session_key: str) -> None: ...
    def next_seq(self, session_key: str) -> int: ...


class InMemorySessionManager:
    """In-memory SessionManager. No persistence across daemon restarts."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create(self, session_key: str) -> SessionState:
        state = SessionState(session_key=session_key)
        self._sessions[session_key] = state
        return state

    def get(self, session_key: str) -> SessionState | None:
        return self._sessions.get(session_key)

    def remove(self, session_key: str) -> None:
        self._sessions.pop(session_key, None)

    def next_seq(self, session_key: str) -> int:
        """Increment and return the next sequence number. Raises KeyError if unknown."""
        state = self._sessions[session_key]
        state.seq += 1
        return state.seq

    def __len__(self) -> int:
        """Number of active sessions."""
        return len(self._sessions)
