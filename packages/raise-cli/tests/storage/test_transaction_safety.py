"""RAISE-15605: write paths must never leave an orphaned write transaction.

Every ``.execute()`` + ``.commit()`` pair in a store is a latent lock: when the
statement raises, the exception propagates *past* ``commit()`` while sqlite3's
implicit ``BEGIN`` is still open, so the connection holds the WAL write lock for
the life of the process. ``~/.rai/raise.db`` is shared by every project and every
long-lived ``rai-mcp-pipeline`` process on the machine, so one orphaned
transaction locks out all writers indefinitely (not slowly — ``busy_timeout``
never expires because the holder never finishes).

Two assertions per write path:

1. the exception still propagates (AC5 behaviour is unchanged), and
2. **a second connection can write immediately afterwards** — the assertion that
   actually proves the lock is gone.

Failures are forced with a TEMP ``RAISE(ABORT)`` trigger so the same shape covers
paths that have no natural constraint to violate (``INSERT OR IGNORE``, plain
``UPDATE``). Verified empirically: the trigger fires even under ``OR IGNORE``.
"""

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest

from raise_cli.artifacts.models import (
    AcceptanceCriterion,
    ComponentRef,
    Decision,
    DesignArtifact,
)
from raise_cli.artifacts.store import ArtifactStore
from raise_cli.storage.connection import get_project_db, get_project_db_path
from raise_cli.storage.schema import create_all
from raise_cli.storage.work_items import WorkItem, WorkItemStore
from raise_cli.storage.worktrees import SqliteWorktreeStore

_BUSY_TIMEOUT_MS = 1000


def _abort_trigger(conn: sqlite3.Connection, table: str, event: str) -> None:
    """Make the next `event` on `table` fail, then leave the connection clean."""
    conn.execute(
        f"CREATE TEMP TRIGGER abort_{table}_{event} BEFORE {event} ON {table} "  # noqa: S608 — test-local identifiers, not user input
        "BEGIN SELECT RAISE(ABORT, 'forced failure (RAISE-15605)'); END"
    )
    conn.commit()
    assert not conn.in_transaction


def _assert_another_connection_can_write(project: Path) -> None:
    """The lock assertion: a *different* connection must write without waiting.

    ``busy_timeout`` is deliberately short — the pre-fix behaviour is an
    indefinite lock, so 1s is plenty to tell "gone" from "still held".
    """
    other = sqlite3.connect(str(get_project_db_path(project)))
    try:
        other.execute(f"PRAGMA busy_timeout={_BUSY_TIMEOUT_MS}")
        try:
            other.execute(
                "INSERT INTO work_items "
                "(id, type, local_key, created_at, updated_at) "
                "VALUES (?, 'story', ?, '2026-01-01T00:00:00Z', "
                "'2026-01-01T00:00:00Z')",
                (uuid.uuid4().hex, f"probe-{uuid.uuid4().hex}"),
            )
            other.commit()
        except sqlite3.OperationalError as exc:  # pragma: no cover — the defect
            pytest.fail(f"write lock still held by the failed store connection: {exc}")
    finally:
        other.close()


def _work_item(**overrides: object) -> WorkItem:
    fields: dict[str, object] = {
        "id": uuid.uuid4().hex,
        "type": "story",
        "local_key": "S1",
        "jira_key": "RAISE-1",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    fields.update(overrides)
    return WorkItem.model_validate(fields)


class TestWorkItemStoreTransactions:
    """4 write paths: create, upsert_jira_mapping, remove_jira_mapping, seed_jira_keys."""

    def test_create_unique_violation_releases_write_lock(self, tmp_path: Path) -> None:
        """THE acceptance test — the exact production trigger (RAISE-15605).

        A duplicate ``local_key`` raises ``IntegrityError`` from
        ``raise_epic_story_create``'s placeholder insert. The exception must
        still propagate, and the connection must be left clean.

        (RAISE-16845: a duplicate ``jira_key`` no longer raises here — it is
        upserted, since the MCP server races ``create()`` with a ghost row on
        the same ``jira_key``. ``local_key`` duplication is unrelated to that
        race and must still raise — see ``TestCreateUpsertsGhostRow`` in
        ``test_work_item_store.py``.)
        """
        store = WorkItemStore(tmp_path)
        store.create(_work_item(local_key="S1", jira_key="RAISE-1"))

        with pytest.raises(sqlite3.IntegrityError):
            store.create(_work_item(local_key="S1", jira_key="RAISE-2"))

        assert not store._conn.in_transaction  # noqa: SLF001 — asserting connection state is the point
        _assert_another_connection_can_write(tmp_path)

    def test_upsert_jira_mapping_failure_releases_write_lock(
        self, tmp_path: Path
    ) -> None:
        store = WorkItemStore(tmp_path)
        # RAISE-17037: duplicate jira_key no longer raises (DO NOTHING arm).
        # Force failure via trigger so the lock-release invariant is still verified.
        _abort_trigger(store._conn, "work_items", "INSERT")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.upsert_jira_mapping("S1", "RAISE-1")

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_remove_jira_mapping_failure_releases_write_lock(
        self, tmp_path: Path
    ) -> None:
        store = WorkItemStore(tmp_path)
        store.create(_work_item(local_key="S1", jira_key="RAISE-1"))
        _abort_trigger(store._conn, "work_items", "UPDATE")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.remove_jira_mapping("S1")

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_seed_jira_keys_failure_releases_write_lock(self, tmp_path: Path) -> None:
        store = WorkItemStore(tmp_path)
        _abort_trigger(store._conn, "work_items", "INSERT")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.seed_jira_keys(["RAISE-1", "RAISE-2"])

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_seed_jira_keys_still_commits_on_success(self, tmp_path: Path) -> None:
        store = WorkItemStore(tmp_path)
        inserted, skipped = store.seed_jira_keys(["RAISE-1", "RAISE-2"])
        assert (inserted, skipped) == (2, 0)
        assert not store._conn.in_transaction  # noqa: SLF001
        assert set(WorkItemStore(tmp_path).all_jira_mappings()) == {
            "RAISE-1",
            "RAISE-2",
        }

    def test_seed_jira_keys_dry_run_writes_nothing(self, tmp_path: Path) -> None:
        store = WorkItemStore(tmp_path)
        inserted, skipped = store.seed_jira_keys(["RAISE-1"], dry_run=True)
        assert (inserted, skipped) == (1, 0)
        assert WorkItemStore(tmp_path).all_jira_mappings() == {}


class TestWorktreeStoreTransactions:
    """3 write paths: register (INSERT), register (UPDATE), complete, set_last_session."""

    def _register(self, store: SqliteWorktreeStore, name: str = "wt-1") -> None:
        store.register(name, str(Path.cwd()), "branch", "main")

    def test_register_insert_failure_releases_write_lock(self, tmp_path: Path) -> None:
        store = SqliteWorktreeStore(tmp_path)
        _abort_trigger(store._conn, "worktrees", "INSERT")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            self._register(store)

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_register_update_failure_releases_write_lock(self, tmp_path: Path) -> None:
        store = SqliteWorktreeStore(tmp_path)
        self._register(store)
        _abort_trigger(store._conn, "worktrees", "UPDATE")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.register("wt-1", str(Path.cwd()), "other", "main", update=True)

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_complete_failure_releases_write_lock(self, tmp_path: Path) -> None:
        store = SqliteWorktreeStore(tmp_path)
        self._register(store)
        _abort_trigger(store._conn, "worktrees", "UPDATE")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.complete("wt-1")

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)

    def test_set_last_session_failure_releases_write_lock(self, tmp_path: Path) -> None:
        store = SqliteWorktreeStore(tmp_path)
        self._register(store)
        _abort_trigger(store._conn, "worktrees", "UPDATE")  # noqa: SLF001

        with pytest.raises(sqlite3.IntegrityError):
            store.set_last_session("wt-1", "sess-1")

        assert not store._conn.in_transaction  # noqa: SLF001
        _assert_another_connection_can_write(tmp_path)


class TestArtifactStoreTransactions:
    """1 write path: save (INSERT branch and UPDATE branch)."""

    @staticmethod
    def _design() -> DesignArtifact:
        return DesignArtifact(
            problem="p",
            value="v",
            approach="a",
            components=[ComponentRef(name="f.py", change="create", purpose="x")],
            decisions=[Decision(id="D1", title="t", rationale="r")],
            acceptance_criteria=[AcceptanceCriterion(id="AC1", description="d")],
        )

    def test_save_insert_failure_releases_write_lock(self, tmp_path: Path) -> None:
        conn = get_project_db(tmp_path)
        create_all(conn)
        store = ArtifactStore(conn, "proj")
        _abort_trigger(conn, "artifacts", "INSERT")

        with pytest.raises(sqlite3.IntegrityError):
            store.save("S1", "design", self._design())

        assert not conn.in_transaction
        _assert_another_connection_can_write(tmp_path)

    def test_save_update_failure_releases_write_lock(self, tmp_path: Path) -> None:
        conn = get_project_db(tmp_path)
        create_all(conn)
        store = ArtifactStore(conn, "proj")
        store.save("S1", "design", self._design())
        _abort_trigger(conn, "artifacts", "UPDATE")

        with pytest.raises(sqlite3.IntegrityError):
            store.save("S1", "design", self._design())

        assert not conn.in_transaction
        _assert_another_connection_can_write(tmp_path)
