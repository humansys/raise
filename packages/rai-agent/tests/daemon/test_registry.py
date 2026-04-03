"""Tests for SessionRegistry — SessionKey, Session model, and CRUD operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from rai_agent.daemon.registry import (
    Session,
    SessionKey,
    SessionLimitError,
    SessionRegistry,
    SessionStatus,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path


class TestSessionKey:
    def test_str_formats_four_parts(self) -> None:
        key = SessionKey(provider="tg", account="default", scope="dm", channel_id="123")
        assert str(key) == "tg:default:dm:123"

    def test_parse_round_trip(self) -> None:
        raw = "tg:rai-main:dm:123456"
        key = SessionKey.parse(raw)
        assert key == SessionKey(
            provider="tg", account="rai-main", scope="dm", channel_id="123456"
        )
        assert str(key) == raw

    def test_parse_channel_id_with_colons(self) -> None:
        """channel_id can contain colons (Q2 resolution: maxsplit=3)."""
        raw = "gchat:default:group:spaces/ABC:extra"
        key = SessionKey.parse(raw)
        assert key.provider == "gchat"
        assert key.account == "default"
        assert key.scope == "group"
        assert key.channel_id == "spaces/ABC:extra"
        assert str(key) == raw

    def test_parse_too_few_parts_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected at least 4"):
            SessionKey.parse("tg:default:dm")

    def test_parse_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected at least 4"):
            SessionKey.parse("")

    def test_hashable_as_dict_key(self) -> None:
        key = SessionKey(provider="tg", account="default", scope="dm", channel_id="1")
        d: dict[SessionKey, str] = {key: "value"}
        assert d[key] == "value"

    def test_equality(self) -> None:
        a = SessionKey.parse("ws:default:session:uuid-abc")
        b = SessionKey(
            provider="ws",
            account="default",
            scope="session",
            channel_id="uuid-abc",
        )
        assert a == b

    def test_immutable(self) -> None:
        key = SessionKey(provider="tg", account="default", scope="dm", channel_id="1")
        with pytest.raises(AttributeError):
            key.provider = "gchat"  # type: ignore[misc]


# ── Fixtures ────────────────────────────────────────────────────────────────

KEY = SessionKey(
    provider="tg",
    account="default",
    scope="dm",
    channel_id="123",
)


@pytest.fixture
async def registry() -> AsyncGenerator[SessionRegistry]:
    """In-memory SessionRegistry, initialized and ready."""
    reg = SessionRegistry(db_path=":memory:")
    await reg.init()
    yield reg
    await reg.close()


# ── T1: Schema + Session model + migration ────────────────────────────────


class TestNewSchema:
    """T1: Verify the new schema columns exist."""

    async def test_schema_has_id_column(
        self,
        registry: SessionRegistry,
    ) -> None:
        """New schema has autoincrement id column."""
        db = registry._conn()
        async with db.execute("PRAGMA table_info(sessions)") as cursor:
            rows = await cursor.fetchall()
        col_names = [r[1] for r in rows]
        assert "id" in col_names

    async def test_schema_has_name_column(
        self,
        registry: SessionRegistry,
    ) -> None:
        db = registry._conn()
        async with db.execute("PRAGMA table_info(sessions)") as cursor:
            rows = await cursor.fetchall()
        col_names = [r[1] for r in rows]
        assert "name" in col_names

    async def test_schema_has_is_current_column(
        self,
        registry: SessionRegistry,
    ) -> None:
        db = registry._conn()
        async with db.execute("PRAGMA table_info(sessions)") as cursor:
            rows = await cursor.fetchall()
        col_names = [r[1] for r in rows]
        assert "is_current" in col_names

    async def test_schema_has_origin_column(
        self,
        registry: SessionRegistry,
    ) -> None:
        db = registry._conn()
        async with db.execute("PRAGMA table_info(sessions)") as cursor:
            rows = await cursor.fetchall()
        col_names = [r[1] for r in rows]
        assert "origin" in col_names

    async def test_sessions_table_exists(
        self,
        registry: SessionRegistry,
    ) -> None:
        db = registry._conn()
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'",
        ) as cursor:
            rows = await cursor.fetchall()
        assert len(rows) == 1


class TestMigration:
    """AR: Verify old schema is dropped and new schema created on init()."""

    async def test_old_schema_migrated_on_init(self, tmp_path: Path) -> None:
        """If old schema exists (no id column), init() drops and recreates."""
        import aiosqlite

        db_path = str(tmp_path / "migrate.db")

        # Create old-schema table (session_key as PK, no id column)
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "CREATE TABLE sessions ("
                "  session_key TEXT PRIMARY KEY,"
                "  provider TEXT NOT NULL,"
                "  account TEXT NOT NULL,"
                "  scope TEXT NOT NULL,"
                "  channel_id TEXT NOT NULL,"
                "  sdk_session_id TEXT,"
                "  cwd TEXT NOT NULL,"
                "  status TEXT NOT NULL DEFAULT 'active',"
                "  created_at TEXT NOT NULL,"
                "  last_active_at TEXT NOT NULL,"
                "  last_input_tokens INTEGER DEFAULT 0,"
                "  metadata TEXT NOT NULL DEFAULT '{}'"
                ")"
            )
            await db.commit()

        # init() should detect old schema and recreate
        reg = SessionRegistry(db_path=db_path)
        await reg.init()

        # Verify new schema has id column
        db = reg._conn()
        async with db.execute("PRAGMA table_info(sessions)") as cursor:
            rows = await cursor.fetchall()
        col_names = [r[1] for r in rows]
        assert "id" in col_names
        assert "name" in col_names
        assert "is_current" in col_names
        assert "origin" in col_names

        await reg.close()


class TestSessionModel:
    """T1: Verify the updated Session model."""

    def test_session_accepts_new_fields(self) -> None:
        from datetime import UTC, datetime

        s = Session(
            id=1,
            session_key="tg:default:dm:123",
            name="Session 1",
            provider="tg",
            account="default",
            scope="dm",
            channel_id="123",
            cwd="/tmp",
            is_current=True,
            origin="telegram",
            created_at=datetime.now(UTC),
            last_active_at=datetime.now(UTC),
        )
        assert s.id == 1
        assert s.name == "Session 1"
        assert s.is_current is True
        assert s.origin == "telegram"

    def test_session_status_is_open_closed(self) -> None:
        """SessionStatus should be Literal['open', 'closed']."""
        from typing import get_args

        args = get_args(SessionStatus)
        assert set(args) == {"open", "closed"}

    def test_session_default_status_is_open(self) -> None:
        from datetime import UTC, datetime

        s = Session(
            id=1,
            session_key="tg:default:dm:123",
            name="Session 1",
            provider="tg",
            account="default",
            scope="dm",
            channel_id="123",
            cwd="/tmp",
            created_at=datetime.now(UTC),
            last_active_at=datetime.now(UTC),
        )
        assert s.status == "open"


class TestMaxSessions:
    """T1: Verify max_sessions is stored on registry."""

    def test_max_sessions_default(self) -> None:
        reg = SessionRegistry(db_path=":memory:")
        assert reg._max_sessions == 10

    def test_max_sessions_custom(self) -> None:
        reg = SessionRegistry(db_path=":memory:", max_sessions=5)
        assert reg._max_sessions == 5


class TestRegistryInit:
    async def test_not_initialized_raises(self) -> None:
        """_conn() raises RuntimeError, not AttributeError."""
        reg = SessionRegistry(db_path=":memory:")
        with pytest.raises(RuntimeError, match="not initialized"):
            reg._conn()

    async def test_wal_mode_enabled(self, tmp_path: Path) -> None:
        """WAL only works with file-based DBs (not :memory:)."""
        db_path = str(tmp_path / "test.db")
        reg = SessionRegistry(db_path=db_path)
        await reg.init()
        try:
            db = reg._conn()
            async with db.execute("PRAGMA journal_mode") as cursor:
                rows = await cursor.fetchall()
            assert rows[0][0] == "wal"
        finally:
            await reg.close()


# ── T2: create_named() ───────────────────────────────────────────────────


class TestCreateNamed:
    """T2: create_named() with auto-naming and max sessions."""

    async def test_creates_with_explicit_name(
        self,
        registry: SessionRegistry,
    ) -> None:
        session = await registry.create_named(KEY, name="my-chat", cwd="/tmp")
        assert isinstance(session, Session)
        assert session.name == "my-chat"
        assert session.status == "open"
        assert session.is_current is True
        assert session.cwd == "/tmp"

    async def test_auto_names_session_1(
        self,
        registry: SessionRegistry,
    ) -> None:
        """First auto-named session is 'Session 1'."""
        session = await registry.create_named(KEY, cwd="/tmp")
        assert session.name == "Session 1"

    async def test_auto_names_session_2(
        self,
        registry: SessionRegistry,
    ) -> None:
        """Second auto-named session is 'Session 2'."""
        await registry.create_named(KEY, cwd="/tmp")
        session = await registry.create_named(KEY, cwd="/tmp")
        assert session.name == "Session 2"

    async def test_no_gap_fill(
        self,
        registry: SessionRegistry,
    ) -> None:
        """Deleting 'Session 2' doesn't fill the gap -- next is 'Session 3'."""
        await registry.create_named(KEY, cwd="/tmp")
        s2 = await registry.create_named(KEY, cwd="/tmp")
        _s3 = await registry.create_named(KEY, cwd="/tmp")
        # Delete Session 2 (not current, s3 is current)
        await registry.delete_named(KEY, name=s2.name)
        s4 = await registry.create_named(KEY, cwd="/tmp")
        assert s4.name == "Session 4"

    async def test_new_session_is_current(
        self,
        registry: SessionRegistry,
    ) -> None:
        """New session gets is_current=True, previous gets False."""
        s1 = await registry.create_named(KEY, cwd="/tmp")
        assert s1.is_current is True
        s2 = await registry.create_named(KEY, cwd="/tmp")
        assert s2.is_current is True
        # s1 should no longer be current
        db = registry._conn()
        async with db.execute(
            "SELECT is_current FROM sessions WHERE id = ?",
            (s1.id,),
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == 0

    async def test_limit_error(self) -> None:
        """Raises SessionLimitError when max sessions reached."""
        reg = SessionRegistry(db_path=":memory:", max_sessions=2)
        await reg.init()
        try:
            await reg.create_named(KEY, cwd="/tmp")
            await reg.create_named(KEY, cwd="/tmp")
            with pytest.raises(SessionLimitError):
                await reg.create_named(KEY, cwd="/tmp")
        finally:
            await reg.close()

    async def test_duplicate_name_raises(
        self,
        registry: SessionRegistry,
    ) -> None:
        """Duplicate (session_key, name) raises IntegrityError."""
        import aiosqlite

        await registry.create_named(KEY, name="dupe", cwd="/tmp")
        with pytest.raises(aiosqlite.IntegrityError):
            await registry.create_named(KEY, name="dupe", cwd="/tmp")


# ── T3: get_current() and list_named() ───────────────────────────────────


class TestGetCurrent:
    """T3: get_current() returns the is_current=1 session."""

    async def test_returns_none_when_no_sessions(
        self,
        registry: SessionRegistry,
    ) -> None:
        result = await registry.get_current(KEY)
        assert result is None

    async def test_returns_current_after_create(
        self,
        registry: SessionRegistry,
    ) -> None:
        created = await registry.create_named(KEY, cwd="/tmp")
        result = await registry.get_current(KEY)
        assert result is not None
        assert result.id == created.id
        assert result.is_current is True


class TestListNamed:
    """T3: list_named() returns open sessions ordered by last_active_at."""

    async def test_empty_when_no_sessions(
        self,
        registry: SessionRegistry,
    ) -> None:
        result = await registry.list_named(KEY)
        assert result == []

    async def test_returns_sessions_ordered(
        self,
        registry: SessionRegistry,
    ) -> None:
        """Sessions ordered by last_active_at DESC (most recent first)."""
        import asyncio

        s1 = await registry.create_named(KEY, name="first", cwd="/tmp")
        await asyncio.sleep(0.01)
        s2 = await registry.create_named(KEY, name="second", cwd="/tmp")
        result = await registry.list_named(KEY)
        assert len(result) == 2
        # Most recent first
        assert result[0].id == s2.id
        assert result[1].id == s1.id

    async def test_excludes_closed_sessions(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, name="keep", cwd="/tmp")
        s2 = await registry.create_named(KEY, name="close-me", cwd="/tmp")
        await registry.close_named(KEY, name=s2.name)
        result = await registry.list_named(KEY)
        assert len(result) == 1
        assert result[0].name == "keep"


# ── T4: switch_to(), close_named(), delete_named() ──────────────────────


class TestSwitchTo:
    """T4: switch_to() changes the current session."""

    async def test_switch_by_name(
        self,
        registry: SessionRegistry,
    ) -> None:
        s1 = await registry.create_named(KEY, name="first", cwd="/tmp")
        await registry.create_named(KEY, name="second", cwd="/tmp")
        result = await registry.switch_to(KEY, name="first")
        assert result.id == s1.id
        assert result.is_current is True

    async def test_switch_by_index(
        self,
        registry: SessionRegistry,
    ) -> None:
        """1-based index from list_named order (last_active DESC)."""
        import asyncio

        await registry.create_named(KEY, name="older", cwd="/tmp")
        await asyncio.sleep(0.01)
        s2 = await registry.create_named(KEY, name="newer", cwd="/tmp")
        # list_named: [newer, older] -> index 1 = newer
        result = await registry.switch_to(KEY, index=1)
        assert result.id == s2.id

    async def test_switch_unknown_raises(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, cwd="/tmp")
        with pytest.raises(KeyError):
            await registry.switch_to(KEY, name="nonexistent")


class TestCloseNamed:
    """T4: close_named() sets status='closed' and clears is_current."""

    async def test_close_current(
        self,
        registry: SessionRegistry,
    ) -> None:
        """No name = close the current session."""
        s = await registry.create_named(KEY, cwd="/tmp")
        await registry.close_named(KEY)
        db = registry._conn()
        async with db.execute(
            "SELECT status, is_current FROM sessions WHERE id = ?",
            (s.id,),
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "closed"
        assert row[1] == 0

    async def test_close_by_name(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, name="a", cwd="/tmp")
        s2 = await registry.create_named(KEY, name="b", cwd="/tmp")
        # Close "a" (not current)
        await registry.close_named(KEY, name="a")
        db = registry._conn()
        async with db.execute(
            "SELECT status FROM sessions WHERE name = 'a' AND session_key = ?",
            (str(KEY),),
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "closed"
        # "b" is still current
        current = await registry.get_current(KEY)
        assert current is not None
        assert current.id == s2.id

    async def test_close_not_found_raises(
        self,
        registry: SessionRegistry,
    ) -> None:
        with pytest.raises(KeyError):
            await registry.close_named(KEY)


class TestDeleteNamed:
    """T4: delete_named() hard-deletes a session."""

    async def test_delete_removes_session(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, name="a", cwd="/tmp")
        s2 = await registry.create_named(KEY, name="b", cwd="/tmp")
        # Delete "a" (not current)
        await registry.delete_named(KEY, name="a")
        sessions = await registry.list_named(KEY)
        assert len(sessions) == 1
        assert sessions[0].id == s2.id

    async def test_delete_current_raises_value_error(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, cwd="/tmp")
        with pytest.raises(ValueError, match="current active"):
            await registry.delete_named(KEY, name="Session 1")

    async def test_delete_by_index(
        self,
        registry: SessionRegistry,
    ) -> None:
        """1-based index from list_named order."""
        import asyncio

        await registry.create_named(KEY, name="older", cwd="/tmp")
        await asyncio.sleep(0.01)
        await registry.create_named(KEY, name="newer", cwd="/tmp")
        # list_named: [newer (current), older] -> index 2 = older
        await registry.delete_named(KEY, index=2)
        sessions = await registry.list_named(KEY)
        assert len(sessions) == 1
        assert sessions[0].name == "newer"

    async def test_delete_not_found_raises(
        self,
        registry: SessionRegistry,
    ) -> None:
        with pytest.raises(KeyError):
            await registry.delete_named(KEY, name="ghost")


# ── T5: update() ──────────────────────────────────────────────────────────


class TestUpdate:
    """T5: update() works on the current session (is_current=1)."""

    async def test_updates_sdk_session_id(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, cwd="/tmp")
        updated = await registry.update(KEY, sdk_session_id="sdk-abc")
        assert updated.sdk_session_id == "sdk-abc"

    async def test_updates_input_tokens(
        self,
        registry: SessionRegistry,
    ) -> None:
        await registry.create_named(KEY, cwd="/tmp")
        updated = await registry.update(KEY, input_tokens=1500)
        assert updated.last_input_tokens == 1500

    async def test_updates_last_active_at(
        self,
        registry: SessionRegistry,
    ) -> None:
        import asyncio

        session = await registry.create_named(KEY, cwd="/tmp")
        first_active = session.last_active_at
        await asyncio.sleep(0.01)
        updated = await registry.update(KEY, sdk_session_id="x")
        assert updated.last_active_at > first_active

    async def test_update_no_current_raises(
        self,
        registry: SessionRegistry,
    ) -> None:
        with pytest.raises(KeyError):
            await registry.update(KEY, sdk_session_id="x")
