"""Tests for raise_cli.storage.maintenance_lock — MaintenanceLockStore (S8371.3)."""

from __future__ import annotations

import sqlite3
import subprocess
import sys

import pytest

from raise_cli.storage.maintenance_lock import (
    MaintenanceLock,
    MaintenanceLockHeldError,
    MaintenanceLockStore,
)
from raise_cli.storage.schema import SCHEMA_VERSION, create_all

_LOCK_NAME = "db_consolidation"


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    create_all(conn)
    return conn


def _dead_pid() -> int:
    """Spawn and reap a child process so its PID is guaranteed dead."""
    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-c", "pass"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    proc.wait(timeout=30)
    return proc.pid


@pytest.fixture
def conn() -> sqlite3.Connection:
    return _make_conn()


@pytest.fixture
def store(conn: sqlite3.Connection) -> MaintenanceLockStore:
    return MaintenanceLockStore(conn)


class TestSchemaV43:
    def test_schema_version_is_43(self) -> None:
        assert SCHEMA_VERSION >= 43

    def test_v43_creates_maintenance_locks_table(self) -> None:
        conn = _make_conn()
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "maintenance_locks" in tables

    def test_v43_migration_is_idempotent(self) -> None:
        conn = _make_conn()
        # Running create_all a second time must not raise
        create_all(conn)
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "maintenance_locks" in tables

    def test_maintenance_locks_columns(self) -> None:
        conn = _make_conn()
        cols = {
            r[1]
            for r in conn.execute("PRAGMA table_info(maintenance_locks)").fetchall()
        }
        assert cols == {"name", "pid", "acquired_at", "expires_at"}


class TestAcquire:
    def test_acquire_free_lock_returns_true(self, store: MaintenanceLockStore) -> None:
        result = store.acquire(_LOCK_NAME, pid=12345, ttl_seconds=300)
        assert result is True

    def test_acquire_held_by_live_pid_raises(self, store: MaintenanceLockStore) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        with pytest.raises(MaintenanceLockHeldError) as exc:
            store.acquire(_LOCK_NAME, pid=99999, ttl_seconds=300)
        assert exc.value.holder.pid == os.getpid()
        assert exc.value.holder.name == _LOCK_NAME

    def test_acquire_held_error_has_expires_at(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        with pytest.raises(MaintenanceLockHeldError) as exc:
            store.acquire(_LOCK_NAME, pid=99999, ttl_seconds=300)
        assert exc.value.holder.expires_at != ""

    def test_acquire_takeover_expired_lock_with_dead_pid(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        dead = _dead_pid()
        store.acquire(_LOCK_NAME, pid=dead, ttl_seconds=-1)
        result = store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        assert result is True
        lock = store.get(_LOCK_NAME)
        assert lock is not None
        assert lock.pid == os.getpid()

    def test_acquire_same_pid_renews_idempotently(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        first_lock = store.get(_LOCK_NAME)
        result = store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        assert result is True
        second_lock = store.get(_LOCK_NAME)
        assert second_lock is not None
        assert first_lock is not None
        # expires_at should be refreshed (>= first)
        assert second_lock.expires_at >= first_lock.expires_at

    def test_acquire_default_ttl_is_300s(self, store: MaintenanceLockStore) -> None:
        import os
        from datetime import datetime

        store.acquire(_LOCK_NAME, pid=os.getpid())
        lock = store.get(_LOCK_NAME)
        assert lock is not None
        acquired = datetime.fromisoformat(lock.acquired_at)
        expires = datetime.fromisoformat(lock.expires_at)
        diff = (expires - acquired).total_seconds()
        assert 295 <= diff <= 305  # 300s ± 5s tolerance


class TestRelease:
    def test_release_by_caller_pid_clears_lock(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        store.release(_LOCK_NAME, pid=os.getpid())
        assert store.get(_LOCK_NAME) is None

    def test_release_wrong_pid_does_not_clear(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        store.release(_LOCK_NAME, pid=99999)
        assert store.get(_LOCK_NAME) is not None

    def test_release_nonexistent_lock_is_noop(
        self, store: MaintenanceLockStore
    ) -> None:
        # Must not raise
        store.release(_LOCK_NAME, pid=12345)


class TestGet:
    def test_get_returns_none_when_free(self, store: MaintenanceLockStore) -> None:
        assert store.get(_LOCK_NAME) is None

    def test_get_returns_lock_when_held(self, store: MaintenanceLockStore) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        lock = store.get(_LOCK_NAME)
        assert isinstance(lock, MaintenanceLock)
        assert lock.pid == os.getpid()
        assert lock.name == _LOCK_NAME


class TestIsExpiredAndDead:
    def test_live_pid_not_expired_returns_false(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        lock = store.get(_LOCK_NAME)
        assert lock is not None
        assert store.is_expired_and_dead(lock) is False

    def test_expired_and_dead_pid_returns_true(
        self, store: MaintenanceLockStore
    ) -> None:
        dead = _dead_pid()
        store.acquire(_LOCK_NAME, pid=dead, ttl_seconds=-1)
        lock = store.get(_LOCK_NAME)
        assert lock is not None
        assert store.is_expired_and_dead(lock) is True

    def test_expired_but_live_pid_returns_false(
        self, store: MaintenanceLockStore
    ) -> None:
        import os

        store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=-1)
        lock = store.get(_LOCK_NAME)
        assert lock is not None
        assert store.is_expired_and_dead(lock) is False
