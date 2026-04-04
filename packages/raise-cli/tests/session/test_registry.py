"""Tests for LocalSessionRegistry — session lifecycle facade."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from raise_cli.schemas.session_state import SessionInfo
from raise_cli.session.protocols import SessionRegistry
from raise_cli.session.registry import LocalSessionRegistry


class TestProtocolCompliance:
    """LocalSessionRegistry satisfies SessionRegistry protocol."""

    def test_satisfies_protocol(self, tmp_path: Path) -> None:
        registry = LocalSessionRegistry(project=tmp_path)
        assert isinstance(registry, SessionRegistry)


class TestRegister:
    """Test session registration."""

    def test_register_writes_active_session_pointer(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)

        registry.register(info)

        pointer_path = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert pointer_path.exists()
        data = json.loads(pointer_path.read_text())
        assert data["id"] == info.session_id

    def test_register_is_idempotent(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)

        registry.register(info)
        registry.register(info)  # should not raise

        pointer_path = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert pointer_path.exists()


class TestActive:
    """Test active session listing."""

    def test_returns_registered_session(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)
        registry.register(info)

        active = registry.active()
        assert len(active) == 1
        assert active[0].session_id == info.session_id

    def test_returns_empty_when_no_session(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)

        active = registry.active()
        assert active == []

    def test_filters_by_project(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)
        registry.register(info)

        # Same project — returns session
        active = registry.active(project=tmp_path)
        assert len(active) == 1

        # Different project — returns empty
        other = tmp_path / "other-project"
        active = registry.active(project=other)
        assert active == []


class TestClose:
    """Test session close."""

    def test_close_clears_active_pointer(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)
        registry.register(info)

        from raise_cli.schemas.session_state import SessionOutcome

        outcome = SessionOutcome(summary="Done")
        registry.close(info.session_id, outcome)

        pointer_path = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert not pointer_path.exists()

    def test_close_on_nonexistent_session_is_noop(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)

        from raise_cli.schemas.session_state import SessionOutcome

        outcome = SessionOutcome(summary="Done")
        registry.close("S-X-999999-9999", outcome)  # should not raise


class TestGcZombieReaping:
    """GC reaps zombie active-session pointers."""

    def test_reaps_stale_pointer(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)

        # Register a session 72 hours ago
        old_info = _make_session_info(
            tmp_path,
            started=datetime(2026, 4, 1, 0, 0),  # 72h before "now"
        )
        registry.register(old_info)

        cleaned = registry.gc(max_age_hours=48)
        assert old_info.session_id in cleaned

        # Pointer should be gone
        pointer_path = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert not pointer_path.exists()

    def test_keeps_fresh_pointer(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        info = _make_session_info(tmp_path)
        registry.register(info)

        # gc with a very generous threshold — should not reap
        cleaned = registry.gc(max_age_hours=999999)
        assert cleaned == []

        # Pointer should still exist
        pointer_path = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert pointer_path.exists()

    def test_no_pointer_is_noop(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        cleaned = registry.gc()
        assert cleaned == []


class TestGcDirRetention:
    """GC enforces session directory retention."""

    def test_removes_old_dirs_beyond_limit(self, tmp_path: Path) -> None:
        personal = _setup_personal_dir(tmp_path)
        sessions_dir = personal / "sessions"

        # Create 25 session dirs (limit is 20)
        for i in range(25):
            d = sessions_dir / f"S-E-260{i:03d}-0000"
            d.mkdir(parents=True)
            (d / "state.yaml").write_text("test")

        registry = LocalSessionRegistry(project=tmp_path)
        cleaned = registry.gc()

        # Should have removed 5 oldest
        remaining = [d for d in sessions_dir.iterdir() if d.is_dir()]
        assert len(remaining) == 20
        assert len([c for c in cleaned if c.startswith("dir:")]) == 5

    def test_keeps_all_when_under_limit(self, tmp_path: Path) -> None:
        personal = _setup_personal_dir(tmp_path)
        sessions_dir = personal / "sessions"

        for i in range(5):
            d = sessions_dir / f"S-E-260{i:03d}-0000"
            d.mkdir(parents=True)

        registry = LocalSessionRegistry(project=tmp_path)
        registry.gc()

        remaining = [d for d in sessions_dir.iterdir() if d.is_dir()]
        assert len(remaining) == 5


class TestGcStaleOutput:
    """GC removes stale session-output.yaml."""

    def test_removes_stale_output(self, tmp_path: Path) -> None:
        import os
        import time

        personal = _setup_personal_dir(tmp_path)
        output = personal / "session-output.yaml"
        output.write_text("stale: true")

        # Backdate the file by 25 hours
        old_time = time.time() - (25 * 3600)
        os.utime(output, (old_time, old_time))

        registry = LocalSessionRegistry(project=tmp_path)
        cleaned = registry.gc()

        assert not output.exists()
        assert "session-output.yaml" in cleaned

    def test_keeps_fresh_output(self, tmp_path: Path) -> None:
        personal = _setup_personal_dir(tmp_path)
        output = personal / "session-output.yaml"
        output.write_text("fresh: true")
        # File is brand new — should be kept

        registry = LocalSessionRegistry(project=tmp_path)
        cleaned = registry.gc()

        assert output.exists()
        assert "session-output.yaml" not in cleaned


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_personal_dir(tmp_path: Path) -> Path:
    """Create the .raise/rai/personal/ directory structure."""
    personal = tmp_path / ".raise" / "rai" / "personal"
    personal.mkdir(parents=True, exist_ok=True)
    return personal


def _make_session_info(
    project: Path,
    session_id: str = "S-E-260403-1530",
    developer: str = "Emilio",
    branch: str = "release/2.4.0",
    started: datetime | None = None,
) -> SessionInfo:
    return SessionInfo(
        session_id=session_id,
        developer=developer,
        project=project,
        branch=branch,
        started=started or datetime(2026, 4, 3, 15, 30),
    )
