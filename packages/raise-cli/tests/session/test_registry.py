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


class TestGcPlaceholder:
    """GC is implemented in T2 — verify it exists and returns empty for now."""

    def test_gc_returns_list(self, tmp_path: Path) -> None:
        _setup_personal_dir(tmp_path)
        registry = LocalSessionRegistry(project=tmp_path)
        result = registry.gc()
        assert isinstance(result, list)


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
) -> SessionInfo:
    return SessionInfo(
        session_id=session_id,
        developer=developer,
        project=project,
        branch=branch,
        started=datetime(2026, 4, 3, 15, 30),
    )
