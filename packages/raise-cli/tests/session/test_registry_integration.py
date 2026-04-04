"""Integration tests for LocalSessionRegistry gc() against real filesystem.

These tests create realistic session directory structures and validate
cleanup behavior. Marked with @pytest.mark.integration for CI filtering.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

import pytest

from raise_cli.schemas.session_state import SessionInfo, SessionOutcome
from raise_cli.session.registry import LocalSessionRegistry


@pytest.mark.integration
class TestGcIntegration:
    """Full gc() lifecycle against real filesystem."""

    def test_full_gc_lifecycle(self, tmp_path: Path) -> None:
        """Register → close → gc cleans up everything."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)

        registry = LocalSessionRegistry(project=tmp_path)

        # Register a session
        info = SessionInfo(
            session_id="S-E-260403-1530",
            developer="Emilio",
            project=tmp_path,
            branch="release/2.4.0",
            started=datetime(2026, 4, 3, 15, 30),
        )
        registry.register(info)

        # Verify pointer exists
        pointer = personal / "active-session"
        assert pointer.exists()

        # Close the session
        outcome = SessionOutcome(summary="Test session")
        registry.close(info.session_id, outcome)

        # Pointer should be gone
        assert not pointer.exists()

        # gc should return empty (nothing stale)
        assert registry.gc() == []

    def test_gc_cleans_realistic_structure(self, tmp_path: Path) -> None:
        """GC handles a realistic personal dir with mixed content."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        sessions_dir = personal / "sessions"

        # Create 25 session dirs with varying ages
        for i in range(25):
            d = sessions_dir / f"S-E-2604{i:02d}-1200"
            d.mkdir(parents=True)
            (d / "state.yaml").write_text(f"session: {i}")
            # Backdate older dirs
            old_time = time.time() - ((25 - i) * 86400)
            os.utime(d, (old_time, old_time))

        # Create stale output file (25h old)
        output = personal / "session-output.yaml"
        output.write_text("stale: true")
        old_time = time.time() - (25 * 3600)
        os.utime(output, (old_time, old_time))

        registry = LocalSessionRegistry(project=tmp_path)
        cleaned = registry.gc()

        # Should have cleaned 5 dirs + 1 stale output
        dir_cleaned = [c for c in cleaned if c.startswith("dir:")]
        assert len(dir_cleaned) == 5
        assert "session-output.yaml" in cleaned

        # 20 dirs should remain
        remaining = [d for d in sessions_dir.iterdir() if d.is_dir()]
        assert len(remaining) == 20

        # Stale output should be gone
        assert not output.exists()

    def test_gc_is_idempotent(self, tmp_path: Path) -> None:
        """Running gc twice produces no additional changes."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        sessions_dir = personal / "sessions"

        for i in range(25):
            d = sessions_dir / f"S-E-2604{i:02d}-1200"
            d.mkdir(parents=True)

        registry = LocalSessionRegistry(project=tmp_path)
        first = registry.gc()
        second = registry.gc()

        assert len(first) == 5  # 5 dirs removed
        assert second == []  # nothing left to clean

    def test_gc_handles_empty_personal_dir(self, tmp_path: Path) -> None:
        """GC works when personal dir exists but is empty."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)

        registry = LocalSessionRegistry(project=tmp_path)
        assert registry.gc() == []
