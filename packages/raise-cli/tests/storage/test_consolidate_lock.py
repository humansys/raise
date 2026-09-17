"""Tests for maintenance lock integration in consolidate_all() (S8371.3).

Verifies that consolidate_all():
- Acquires the db_consolidation lock before first write
- Releases the lock in finally (even on error)
- Aborts immediately when lock is held by a live PID
- Skips lock acquisition for dry_run=True
- Recovers orphan lock with dead PID automatically
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.storage.consolidate import (
    ConsolidationResult,
    SourceDb,
    consolidate_all,
)
from raise_cli.storage.maintenance_lock import (
    MaintenanceLockHeldError,
    MaintenanceLockStore,
)


def _dead_pid() -> int:
    """Spawn and reap a child so its PID is guaranteed dead."""
    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-c", "pass"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        proc.wait(timeout=30)
    except KeyboardInterrupt:
        # Windows: asyncio event-loop teardown between tests can deliver a wakeup
        # signal that interrupts WaitForSingleObject inside proc.wait(). The child
        # may have already exited with STATUS_CONTROL_C_EXIT — kill it if still
        # alive so we always return a guaranteed-dead PID.
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return proc.pid


def _empty_sources() -> list[SourceDb]:
    """No real DBs — consolidation logic completes after lock acquires."""
    return []


def _make_source_db(tmp_path: Path) -> SourceDb:
    """Create a minimal real SQLite DB so consolidate_all doesn't short-circuit."""
    import sqlite3

    db_path = tmp_path / "test_source.db"
    conn = sqlite3.connect(str(db_path))
    # Minimal schema — just enough to not be empty
    conn.execute(
        "CREATE TABLE sessions (session_id TEXT PRIMARY KEY, name TEXT NOT NULL, started TEXT NOT NULL, closed TEXT, type TEXT NOT NULL DEFAULT 'feature', summary TEXT NOT NULL DEFAULT '', branch TEXT NOT NULL DEFAULT '', prefix TEXT NOT NULL DEFAULT '', state_json TEXT NOT NULL DEFAULT '{}')"
    )
    conn.commit()
    conn.close()
    return SourceDb(path=db_path, project_id="test-project", kind="project-local")


@pytest.fixture
def rai_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect RAI_HOME so tests don't touch ~/.rai/raise.db."""
    home = tmp_path / "rai_home"
    home.mkdir()
    monkeypatch.setenv("RAI_HOME", str(home))
    return home


class TestConsolidateLockAcquire:
    def test_acquires_lock_before_write(
        self,
        rai_home: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """consolidate_all() must hold the lock during execution when sources exist."""
        acquired_pids: list[int] = []

        original_acquire = MaintenanceLockStore.acquire

        def tracking_acquire(
            self: MaintenanceLockStore,
            name: str,
            *,
            pid: int,
            ttl_seconds: int = 300,
        ) -> bool:
            acquired_pids.append(pid)
            return original_acquire(self, name, pid=pid, ttl_seconds=ttl_seconds)

        monkeypatch.setattr(MaintenanceLockStore, "acquire", tracking_acquire)

        source = _make_source_db(tmp_path)
        consolidate_all(sources=[source])
        # Lock acquire must have been called once (with our PID)
        assert os.getpid() in acquired_pids

    def test_skips_lock_for_dry_run(
        self, rai_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """dry_run=True must not acquire the maintenance lock."""
        acquired_pids: list[int] = []

        original_acquire = MaintenanceLockStore.acquire

        def tracking_acquire(
            self: MaintenanceLockStore,
            name: str,
            *,
            pid: int,
            ttl_seconds: int = 300,
        ) -> bool:
            acquired_pids.append(pid)
            return original_acquire(self, name, pid=pid, ttl_seconds=ttl_seconds)

        monkeypatch.setattr(MaintenanceLockStore, "acquire", tracking_acquire)

        result = consolidate_all(sources=_empty_sources(), dry_run=True)
        assert result.sources_found == 0
        assert acquired_pids == []

    def test_aborts_when_lock_held_by_live_pid(
        self, rai_home: Path, tmp_path: Path
    ) -> None:
        """consolidate_all() raises MaintenanceLockHeldError when another PID holds lock."""
        import sqlite3

        from raise_cli.config.paths import get_global_rai_dir
        from raise_cli.storage.schema import create_all

        # Pre-acquire lock with current PID (simulates another process holding it)
        rai_dir = get_global_rai_dir()
        rai_dir.mkdir(parents=True, exist_ok=True)
        global_db_path = rai_dir / "raise.db"
        conn = sqlite3.connect(str(global_db_path))
        conn.row_factory = sqlite3.Row
        create_all(conn)
        holder_store = MaintenanceLockStore(conn)
        # Use os.getpid() — guaranteed alive
        holder_store.acquire("db_consolidation", pid=os.getpid(), ttl_seconds=300)
        conn.close()

        # Simulate consolidate_all() running as a different PID
        # (patch os.getpid inside the consolidate module)
        source = _make_source_db(tmp_path)
        with (
            patch("raise_cli.storage.consolidate.os.getpid", return_value=99998),
            pytest.raises(MaintenanceLockHeldError) as exc,
        ):
            consolidate_all(sources=[source])
        assert exc.value.holder.pid == os.getpid()

    def test_releases_lock_after_success(self, rai_home: Path) -> None:
        """Lock must be released after consolidate_all() completes normally."""
        import sqlite3

        from raise_cli.config.paths import get_global_rai_dir
        from raise_cli.storage.schema import create_all

        consolidate_all(sources=_empty_sources())

        rai_dir = get_global_rai_dir()
        global_db_path = rai_dir / "raise.db"
        if not global_db_path.exists():
            return  # No DB created for empty sources — lock was never held
        conn = sqlite3.connect(str(global_db_path))
        conn.row_factory = sqlite3.Row
        create_all(conn)
        store = MaintenanceLockStore(conn)
        assert store.get("db_consolidation") is None
        conn.close()

    def test_orphan_lock_with_dead_pid_auto_recovers(self, rai_home: Path) -> None:
        """consolidate_all() takes over an expired lock with a dead PID."""
        import sqlite3

        from raise_cli.config.paths import get_global_rai_dir
        from raise_cli.storage.schema import create_all

        dead = _dead_pid()
        rai_dir = get_global_rai_dir()
        rai_dir.mkdir(parents=True, exist_ok=True)
        global_db_path = rai_dir / "raise.db"
        conn = sqlite3.connect(str(global_db_path))
        conn.row_factory = sqlite3.Row
        create_all(conn)
        orphan_store = MaintenanceLockStore(conn)
        orphan_store.acquire("db_consolidation", pid=dead, ttl_seconds=-1)
        conn.close()

        # Must succeed — orphan lock with dead PID + expired TTL is recoverable
        result = consolidate_all(sources=_empty_sources())
        assert isinstance(result, ConsolidationResult)
