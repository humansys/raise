"""Tests for raise_cli.storage.connection — DB factory functions."""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest

from raise_cli.storage.connection import (
    get_global_db,
    get_project_db,
    get_project_id,
    get_server_slug,
)


def _init_git_repo(path: Path, remote_url: str | None = None) -> None:
    """Initialize a git repo at path, optionally with a remote."""
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    if remote_url:
        subprocess.run(
            ["git", "remote", "add", "origin", remote_url],
            cwd=str(path),
            capture_output=True,
            check=True,
        )


class TestGetProjectDb:
    def test_returns_connection(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_wal_mode_enabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"
        conn.close()

    def test_busy_timeout_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        assert timeout == 5000
        conn.close()

    def test_foreign_keys_enabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1
        conn.close()

    def test_auto_vacuum_incremental(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        av = conn.execute("PRAGMA auto_vacuum").fetchone()[0]
        assert av == 2  # 2 = INCREMENTAL
        conn.close()

    def test_row_factory_is_row(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        assert conn.row_factory is sqlite3.Row
        conn.close()

    def test_db_at_global_location(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        conn.close()
        assert (rai_home / "raise.db").exists()

    def test_all_projects_share_global_db(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        repo_a = tmp_path / "repo_a"
        repo_b = tmp_path / "repo_b"
        _init_git_repo(repo_a, "git@gitlab.com:org/repo-a.git")
        _init_git_repo(repo_b, "git@gitlab.com:org/repo-b.git")
        conn_a = get_project_db(repo_a)
        conn_b = get_project_db(repo_b)
        path_a = conn_a.execute("PRAGMA database_list").fetchone()[2]
        path_b = conn_b.execute("PRAGMA database_list").fetchone()[2]
        assert path_a == path_b
        conn_a.close()
        conn_b.close()

    def test_creates_parent_dirs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        _init_git_repo(tmp_path / "repo")
        conn = get_project_db(tmp_path / "repo")
        conn.close()
        assert (rai_home / "raise.db").exists()


class TestGetGlobalDb:
    def test_returns_connection(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path))
        conn = get_global_db()
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_wal_mode_enabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path))
        conn = get_global_db()
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"
        conn.close()

    def test_creates_parent_dirs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rai_home = tmp_path / "custom_rai"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        conn = get_global_db()
        db_path = rai_home / "raise.db"
        assert db_path.exists()
        conn.close()

    def test_db_at_expected_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path))
        conn = get_global_db()
        db_path = tmp_path / "raise.db"
        assert db_path.exists()
        conn.close()


class TestGetProjectId:
    def test_returns_manifest_slug_when_available(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RAISE-6143: get_project_id must return manifest project.name, not hash."""
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo, "git@gitlab.com:org/my-project.git")
        manifest = repo / ".raise" / "manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "version: '1.0'\nproject:\n  name: my-project\n", encoding="utf-8"
        )
        pid = get_project_id(repo)
        assert pid == "my-project"

    def test_same_remote_same_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        remote = "git@gitlab.com:org/repo.git"
        repo_a = tmp_path / "repo_a"
        repo_b = tmp_path / "repo_b"
        _init_git_repo(repo_a, remote)
        _init_git_repo(repo_b, remote)
        assert get_project_id(repo_a) == get_project_id(repo_b)

    def test_different_remotes_different_ids(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo_a = tmp_path / "repo_a"
        repo_b = tmp_path / "repo_b"
        _init_git_repo(repo_a, "git@gitlab.com:org/repo-a.git")
        _init_git_repo(repo_b, "git@gitlab.com:org/repo-b.git")
        assert get_project_id(repo_a) != get_project_id(repo_b)

    def test_no_manifest_falls_back_to_remote_basename(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RAISE-6143: without manifest, derive slug from git remote basename."""
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo, "git@gitlab.com:org/cool-repo.git")
        pid = get_project_id(repo)
        assert pid == "cool-repo"

    def test_no_remote_falls_back_to_dir_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RAISE-6143: without remote, use directory name."""
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "my-local-repo"
        _init_git_repo(repo)
        pid = get_project_id(repo)
        assert pid == "my-local-repo"


class TestGetServerSlug:
    """RAISE-11083 / RAISE-13467: server_slug is the WIRE identity, not the local one.

    get_server_slug() (not get_project_id()) is what should read server_slug —
    it is a separate accessor from the local resolver.
    """

    def test_prefers_server_slug_over_mismatched_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo)
        manifest = repo / ".raise" / "manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: Raw Directory Name\n"
            "  server_slug: confirmed-slug\n",
            encoding="utf-8",
        )
        slug = get_server_slug(repo)
        assert slug == "confirmed-slug"

    def test_falls_back_to_name_when_server_slug_absent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo)
        manifest = repo / ".raise" / "manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "version: '1.0'\nproject:\n  name: my-project\n", encoding="utf-8"
        )
        slug = get_server_slug(repo)
        assert slug == "my-project"


class TestGetProjectIdIgnoresServerSlug:
    """RAISE-13467: get_project_id() (LOCAL identity) must ignore server_slug.

    Regression prevention for RAISE-13298's original bug — server_slug leaking
    into get_project_id() silently re-keyed all local ~/.rai/raise.db history.
    """

    def test_project_id_ignores_server_slug(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo)
        manifest = repo / ".raise" / "manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "version: '1.0'\nproject:\n  name: raise-commons\n  server_slug: raise\n",
            encoding="utf-8",
        )
        pid = get_project_id(repo)
        assert pid == "raise-commons"

    def test_project_id_stable_when_server_slug_added_later(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Same repo path reused deliberately to exercise the resolution logic
        # itself (not just cache reuse) — the lru_cache is cleared between
        # reads so a regression in the resolution order actually surfaces
        # here. cache_clear() on the module-private cached resolver is
        # legitimately necessary: there is no public cache-invalidation API.
        from raise_cli.storage.connection import (
            _get_project_slug,  # pyright: ignore[reportPrivateUsage]
        )

        monkeypatch.setenv("RAI_HOME", str(tmp_path / "rai_home"))
        repo = tmp_path / "repo"
        _init_git_repo(repo)
        manifest = repo / ".raise" / "manifest.yaml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            "version: '1.0'\nproject:\n  name: raise-commons\n", encoding="utf-8"
        )
        pid_before = get_project_id(repo)

        manifest.write_text(
            "version: '1.0'\nproject:\n  name: raise-commons\n  server_slug: raise\n",
            encoding="utf-8",
        )
        _get_project_slug.cache_clear()
        pid_after = get_project_id(repo)

        assert pid_before == pid_after == "raise-commons"


class TestMultiProjectIsolation:
    """Integration tests verifying two projects in the same global DB don't interfere."""

    def test_sessions_isolated_by_project_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.storage.schema import create_all

        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        repo_a = tmp_path / "repo_a"
        repo_b = tmp_path / "repo_b"
        _init_git_repo(repo_a, "git@gitlab.com:org/repo-a.git")
        _init_git_repo(repo_b, "git@gitlab.com:org/repo-b.git")

        pid_a = get_project_id(repo_a)
        pid_b = get_project_id(repo_b)
        assert pid_a != pid_b

        conn = get_project_db(repo_a)
        create_all(conn)

        conn.execute(
            "INSERT INTO sessions (project_id, session_id, name, started, type, summary, branch, prefix, state_json, outcomes)"
            " VALUES (?, 'sess-a-1', 'test-a', '2026-01-01', 'feature', '', '', '', '{}', '[]')",
            (pid_a,),
        )
        conn.execute(
            "INSERT INTO sessions (project_id, session_id, name, started, type, summary, branch, prefix, state_json, outcomes)"
            " VALUES (?, 'sess-b-1', 'test-b', '2026-01-01', 'feature', '', '', '', '{}', '[]')",
            (pid_b,),
        )
        conn.commit()

        rows_a = conn.execute(
            "SELECT name FROM sessions WHERE project_id = ?", (pid_a,)
        ).fetchall()
        rows_b = conn.execute(
            "SELECT name FROM sessions WHERE project_id = ?", (pid_b,)
        ).fetchall()
        assert len(rows_a) == 1
        assert rows_a[0]["name"] == "test-a"
        assert len(rows_b) == 1
        assert rows_b[0]["name"] == "test-b"

        all_rows = conn.execute("SELECT * FROM sessions").fetchall()
        assert len(all_rows) == 2
        conn.close()

    def test_unscoped_global_tables_no_project_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.storage.schema import create_all

        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        repo = tmp_path / "repo"
        _init_git_repo(repo, "git@gitlab.com:org/repo.git")

        conn = get_project_db(repo)
        create_all(conn)

        for table in ("issue_cache", "sync_outbox", "sync_state"):
            cols = {
                r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()
            }
            assert "project_id" not in cols
        conn.close()

    def test_missions_are_scoped_by_project_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.storage.schema import create_all

        rai_home = tmp_path / "rai_home"
        monkeypatch.setenv("RAI_HOME", str(rai_home))
        repo = tmp_path / "repo"
        _init_git_repo(repo, "git@gitlab.com:org/repo.git")
        pid = get_project_id(repo)

        conn = get_project_db(repo)
        create_all(conn)

        conn.execute(
            "INSERT INTO missions (project_id, mission_id, name, status, objectives, linked_epics, sessions, learned_patterns, scratch, close_note, retrospective_path, created_at, last_used_at)"
            " VALUES (?, 'm1', 'test', 'active', '[]', '[]', '[]', '[]', 0, '', '', '2026-01-01', '2026-01-01')",
            (pid,),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM missions WHERE project_id = ? AND mission_id = 'm1'",
            (pid,),
        ).fetchone()
        assert row is not None
        assert row["name"] == "test"

        cols = {r[1] for r in conn.execute("PRAGMA table_info(missions)").fetchall()}
        assert "project_id" in cols
        conn.close()
