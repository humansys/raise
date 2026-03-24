"""Unified session registry for the Rai daemon.

SessionKey is a structured identifier for sessions across all providers.
SessionRegistry provides async CRUD backed by SQLite (aiosqlite).
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any, Literal, NamedTuple

import aiosqlite
from pydantic import BaseModel, Field

__all__ = [
    "Session",
    "SessionKey",
    "SessionLimitError",
    "SessionRegistry",
    "SessionStatus",
]

# ── Types ───────────────────────────────────────────────────────────────────

SessionStatus = Literal["open", "closed"]


class SessionKey(NamedTuple):
    """Structured session identifier: ``{provider}:{account}:{scope}:{channel_id}``.

    Immutable and hashable — safe as dict keys (used by SessionDispatcher in S5.3).
    """

    provider: str
    account: str
    scope: str
    channel_id: str

    @classmethod
    def parse(cls, raw: str) -> SessionKey:
        """Parse a colon-separated session key string.

        Uses ``maxsplit=3`` so that ``channel_id`` may contain colons
        (e.g., ``gchat:default:group:spaces/ABC:extra``).

        Raises:
            ValueError: If fewer than 4 parts are present.
        """
        parts = raw.split(":", 3)
        if len(parts) < 4:  # noqa: PLR2004
            msg = (
                f"Expected at least 4 colon-separated parts, got {len(parts)}: {raw!r}"
            )
            raise ValueError(msg)
        return cls(
            provider=parts[0],
            account=parts[1],
            scope=parts[2],
            channel_id=parts[3],
        )

    def __str__(self) -> str:
        return f"{self.provider}:{self.account}:{self.scope}:{self.channel_id}"


# ── Exceptions ────────────────────────────────────────────────────────────


class SessionLimitError(Exception):
    """Raised when max sessions per chat is reached."""


# ── Session model ──────────────────────────────────────────────────────────


class Session(BaseModel):
    """Persistent session state, maps to SQLite ``sessions`` table."""

    id: int
    session_key: str
    name: str
    provider: str
    account: str
    scope: str
    channel_id: str
    sdk_session_id: str | None = None
    cwd: str
    status: SessionStatus = "open"
    is_current: bool = False
    origin: str = "telegram"
    created_at: datetime
    last_active_at: datetime
    last_input_tokens: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── SessionRegistry ────────────────────────────────────────────────────────

_CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key     TEXT NOT NULL,
    name            TEXT NOT NULL,
    provider        TEXT NOT NULL,
    account         TEXT NOT NULL,
    scope           TEXT NOT NULL,
    channel_id      TEXT NOT NULL,
    sdk_session_id  TEXT,
    cwd             TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open',
    is_current      BOOLEAN NOT NULL DEFAULT 0,
    origin          TEXT NOT NULL DEFAULT 'telegram',
    created_at      TEXT NOT NULL,
    last_active_at  TEXT NOT NULL,
    last_input_tokens INTEGER DEFAULT 0,
    metadata        TEXT NOT NULL DEFAULT '{}',
    UNIQUE(session_key, name)
)"""

_CREATE_IDX_PROVIDER = (
    "CREATE INDEX IF NOT EXISTS idx_sessions_provider_status "
    "ON sessions(provider, status)"
)
_CREATE_IDX_ACTIVE = (
    "CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active_at)"
)
_CREATE_IDX_CURRENT = (
    "CREATE INDEX IF NOT EXISTS idx_sessions_current "
    "ON sessions(session_key, is_current) WHERE is_current = 1"
)

_COLUMN_LIST = [
    "id",
    "session_key",
    "name",
    "provider",
    "account",
    "scope",
    "channel_id",
    "sdk_session_id",
    "cwd",
    "status",
    "is_current",
    "origin",
    "created_at",
    "last_active_at",
    "last_input_tokens",
    "metadata",
]
_COLUMNS = ", ".join(_COLUMN_LIST)
_INSERT_COLUMNS = ", ".join(c for c in _COLUMN_LIST if c != "id")

_AUTO_NAME_RE = re.compile(r"^Session (\d+)$")


def _row_to_session(row: aiosqlite.Row) -> Session:
    """Convert a SQLite row to a Session model."""
    return Session(
        id=row[0],
        session_key=row[1],
        name=row[2],
        provider=row[3],
        account=row[4],
        scope=row[5],
        channel_id=row[6],
        sdk_session_id=row[7],
        cwd=row[8],
        status=row[9],
        is_current=bool(row[10]),
        origin=row[11],
        created_at=datetime.fromisoformat(row[12]),
        last_active_at=datetime.fromisoformat(row[13]),
        last_input_tokens=row[14],
        metadata=json.loads(row[15]),
    )


class SessionRegistry:
    """Async session CRUD backed by SQLite via aiosqlite.

    All methods accept ``SessionKey`` (not raw strings).
    WAL mode is enabled on init for concurrent read safety.
    """

    def __init__(
        self,
        db_path: str = "daemon.db",
        *,
        max_sessions: int = 10,
    ) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None
        self._max_sessions = max_sessions

    def _conn(self) -> aiosqlite.Connection:
        """Return the active connection or raise if not initialized."""
        if self._db is None:
            msg = "SessionRegistry not initialized — call init() first"
            raise RuntimeError(msg)
        return self._db

    async def init(self) -> None:
        """Open connection, create table, enable WAL mode.

        Detects old schema (no ``id`` column) and migrates by dropping
        the old table and creating the new one (D1: drop + recreate).
        """
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.execute("PRAGMA journal_mode=WAL")

        # Migration: detect old schema by checking for 'id' column
        async with self._db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'",
        ) as cursor:
            table_exists = await cursor.fetchone() is not None

        if table_exists:
            async with self._db.execute(
                "PRAGMA table_info(sessions)",
            ) as cursor:
                cols = await cursor.fetchall()
            col_names = {c[1] for c in cols}
            if "id" not in col_names:
                # Old schema detected — drop and recreate
                await self._db.execute("DROP TABLE sessions")

        await self._db.execute(_CREATE_TABLE)
        await self._db.execute(_CREATE_IDX_PROVIDER)
        await self._db.execute(_CREATE_IDX_ACTIVE)
        await self._db.execute(_CREATE_IDX_CURRENT)
        await self._db.commit()

    # ── Named session CRUD ─────────────────────────────────────────────

    async def create_named(
        self,
        key: SessionKey,
        *,
        name: str | None = None,
        cwd: str,
    ) -> Session:
        """Create a new named session, optionally auto-naming.

        If ``name`` is None, auto-generates "Session N" where N is
        max existing auto-name + 1 (no gap fill per D4).

        Marks the new session as ``is_current=1`` and clears
        ``is_current`` on all other sessions for this key.

        Raises:
            SessionLimitError: If open session count >= max_sessions.
            aiosqlite.IntegrityError: If duplicate (session_key, name).
        """
        db = self._conn()
        sk = str(key)

        # Validate name length
        max_name_len = 100
        if name is not None and len(name) > max_name_len:
            msg = f"Session name too long ({len(name)} > {max_name_len})"
            raise ValueError(msg)

        # Check session limit
        async with db.execute(
            "SELECT COUNT(*) FROM sessions WHERE session_key = ? AND status = 'open'",
            (sk,),
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
        if count >= self._max_sessions:
            msg = f"Session limit reached ({self._max_sessions}) for key {key}"
            raise SessionLimitError(msg)

        # Auto-name if not provided
        if name is None:
            async with db.execute(
                "SELECT name FROM sessions WHERE session_key = ?",
                (sk,),
            ) as cursor:
                existing_names = [r[0] for r in await cursor.fetchall()]
            max_n = 0
            for n in existing_names:
                m = _AUTO_NAME_RE.match(n)
                if m:
                    max_n = max(max_n, int(m.group(1)))
            name = f"Session {max_n + 1}"

        now_iso = datetime.now(UTC).isoformat()

        # Clear is_current on all existing sessions for this key
        await db.execute(
            "UPDATE sessions SET is_current = 0 WHERE session_key = ?",
            (sk,),
        )

        # Insert new session
        await db.execute(
            f"INSERT INTO sessions ({_INSERT_COLUMNS}) "  # noqa: S608
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sk,
                name,
                key.provider,
                key.account,
                key.scope,
                key.channel_id,
                None,  # sdk_session_id
                cwd,
                "open",
                1,  # is_current
                key.provider,  # origin
                now_iso,
                now_iso,
                0,
                "{}",
            ),
        )
        await db.commit()

        # Read back
        async with db.execute(
            f"SELECT {_COLUMNS} FROM sessions "  # noqa: S608
            "WHERE session_key = ? AND name = ?",
            (sk, name),
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            return _row_to_session(row)

    async def get_current(self, key: SessionKey) -> Session | None:
        """Get the current (is_current=1) session for a key, or None."""
        db = self._conn()
        async with db.execute(
            f"SELECT {_COLUMNS} FROM sessions "  # noqa: S608
            "WHERE session_key = ? AND is_current = 1",
            (str(key),),
        ) as cursor:
            row = await cursor.fetchone()
            return _row_to_session(row) if row else None

    async def list_named(self, key: SessionKey) -> list[Session]:
        """List open sessions for a key, ordered by last_active_at DESC."""
        db = self._conn()
        async with db.execute(
            f"SELECT {_COLUMNS} FROM sessions "  # noqa: S608
            "WHERE session_key = ? AND status = 'open' "
            "ORDER BY last_active_at DESC",
            (str(key),),
        ) as cursor:
            rows = await cursor.fetchall()
            return [_row_to_session(row) for row in rows]

    async def switch_to(
        self,
        key: SessionKey,
        *,
        name: str | None = None,
        index: int | None = None,
    ) -> Session:
        """Switch current session by name or 1-based index.

        Raises:
            KeyError: If target session not found.
        """
        target = await self._lookup(key, name=name, index=index)
        db = self._conn()
        sk = str(key)

        # Clear current
        await db.execute(
            "UPDATE sessions SET is_current = 0 WHERE session_key = ?",
            (sk,),
        )
        # Set new current and update last_active_at
        now_iso = datetime.now(UTC).isoformat()
        await db.execute(
            "UPDATE sessions SET is_current = 1, last_active_at = ? WHERE id = ?",
            (now_iso, target.id),
        )
        await db.commit()

        result = await self.get_current(key)
        assert result is not None  # just set is_current=1
        return result

    async def close_named(
        self,
        key: SessionKey,
        *,
        name: str | None = None,
    ) -> None:
        """Close a session (set status='closed', clear is_current).

        If no name given, closes the current session.

        Raises:
            KeyError: If session not found.
        """
        db = self._conn()
        if name is None:
            current = await self.get_current(key)
            if current is None:
                msg = f"No current session for key {key}"
                raise KeyError(msg)
            target_id = current.id
        else:
            target = await self._lookup(key, name=name)
            target_id = target.id

        await db.execute(
            "UPDATE sessions SET status = 'closed', is_current = 0 WHERE id = ?",
            (target_id,),
        )
        await db.commit()

    async def delete_named(
        self,
        key: SessionKey,
        *,
        name: str | None = None,
        index: int | None = None,
    ) -> None:
        """Hard-delete a session by name or 1-based index.

        Raises:
            ValueError: If trying to delete the current active session.
            KeyError: If session not found.
        """
        target = await self._lookup(key, name=name, index=index)
        if target.is_current:
            msg = "Cannot delete the current active session"
            raise ValueError(msg)
        db = self._conn()
        await db.execute("DELETE FROM sessions WHERE id = ?", (target.id,))
        await db.commit()

    async def update(
        self,
        key: SessionKey,
        *,
        sdk_session_id: str | None = None,
        input_tokens: int | None = None,
    ) -> Session:
        """Update the current session's fields after an SDK interaction.

        Raises:
            KeyError: If no current session exists for the key.
        """
        db = self._conn()
        now_iso = datetime.now(UTC).isoformat()
        sets: list[str] = ["last_active_at = ?"]
        params: list[Any] = [now_iso]

        if sdk_session_id is not None:
            sets.append("sdk_session_id = ?")
            params.append(sdk_session_id)
        if input_tokens is not None:
            sets.append("last_input_tokens = ?")
            params.append(input_tokens)

        sk = str(key)
        params.append(sk)
        cursor = await db.execute(
            f"UPDATE sessions SET {', '.join(sets)} "  # noqa: S608
            "WHERE session_key = ? AND is_current = 1",
            tuple(params),
        )
        if cursor.rowcount == 0:
            msg = f"No current session for key {key}"
            raise KeyError(msg)
        await db.commit()

        result = await self.get_current(key)
        assert result is not None
        return result

    async def close(self) -> None:
        """Close the database connection."""
        if self._db is not None:
            await self._db.close()
            self._db = None

    # ── Internal helpers ───────────────────────────────────────────────

    async def _lookup(
        self,
        key: SessionKey,
        *,
        name: str | None = None,
        index: int | None = None,
    ) -> Session:
        """Find a session by name or 1-based index from list_named.

        Raises:
            KeyError: If session not found.
        """
        if name is not None:
            db = self._conn()
            async with db.execute(
                f"SELECT {_COLUMNS} FROM sessions "  # noqa: S608
                "WHERE session_key = ? AND name = ? AND status = 'open'",
                (str(key), name),
            ) as cursor:
                row = await cursor.fetchone()
            if row is None:
                msg = f"No session named {name!r} for key {key}"
                raise KeyError(msg)
            return _row_to_session(row)

        if index is not None:
            sessions = await self.list_named(key)
            if index < 1 or index > len(sessions):
                msg = f"Session index {index} out of range (1-{len(sessions)})"
                raise KeyError(msg)
            return sessions[index - 1]

        msg = "Either name or index must be provided"
        raise KeyError(msg)
