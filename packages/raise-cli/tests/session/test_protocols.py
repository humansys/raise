"""Tests for session protocol contracts and supporting models."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from raise_cli.schemas.session_state import (
    ActivityEntry,
    CurrentWork,
    Improvement,
    SessionInfo,
    SessionInsights,
    SessionOutcome,
)
from raise_cli.session.protocols import (
    SessionRegistry,
    StateDeriver,
    WorkstreamMonitor,
)

# ---------------------------------------------------------------------------
# Model construction tests
# ---------------------------------------------------------------------------


class TestActivityEntry:
    def test_construction(self) -> None:
        entry = ActivityEntry(
            commit_hash="abc1234",
            subject="fix: something",
            author="Emilio",
            timestamp=datetime(2026, 4, 3, 12, 0),
            story_id="S1248.1",
            epic_id="E1248",
        )
        assert entry.commit_hash == "abc1234"
        assert entry.story_id == "S1248.1"
        assert entry.epic_id == "E1248"

    def test_optional_ids(self) -> None:
        entry = ActivityEntry(
            commit_hash="abc1234",
            subject="chore: update deps",
            author="Emilio",
            timestamp=datetime(2026, 4, 3, 12, 0),
        )
        assert entry.story_id == ""
        assert entry.epic_id == ""


class TestSessionInfo:
    def test_construction(self) -> None:
        info = SessionInfo(
            session_id="S-E-260403-1530",
            developer="Emilio",
            project=Path("/home/emilio/Code/raise-commons"),
            branch="release/2.4.0",
            started=datetime(2026, 4, 3, 15, 30),
        )
        assert info.session_id == "S-E-260403-1530"
        assert info.branch == "release/2.4.0"


class TestSessionOutcome:
    def test_construction(self) -> None:
        outcome = SessionOutcome(
            summary="Implemented protocols",
            patterns_captured=["PAT-E-700"],
            stories_completed=["S1248.1"],
        )
        assert outcome.summary == "Implemented protocols"
        assert len(outcome.patterns_captured) == 1


class TestSessionInsights:
    def test_construction(self) -> None:
        insights = SessionInsights(
            session_id="S-E-260403-1530",
            commit_count=5,
            test_commit_ratio=0.6,
            revert_count=0,
            duration_minutes=120,
        )
        assert insights.commit_count == 5
        assert insights.test_commit_ratio == pytest.approx(0.6)


class TestImprovement:
    def test_construction(self) -> None:
        imp = Improvement(
            category="tdd",
            description="First commit took >30min in 3 of 5 sessions",
            suggestion="Consider smaller first tasks",
        )
        assert imp.category == "tdd"


# ---------------------------------------------------------------------------
# Protocol runtime_checkable tests
# ---------------------------------------------------------------------------


class TestProtocolsAreRuntimeCheckable:
    """Verify protocols can be used with isinstance()."""

    def test_state_deriver_is_runtime_checkable(self) -> None:
        class _FakeDeriver:
            def current_work(self, project: Path) -> CurrentWork:
                return CurrentWork()

            def recent_activity(
                self, project: Path, limit: int = 10
            ) -> list[ActivityEntry]:
                return []

        assert isinstance(_FakeDeriver(), StateDeriver)

    def test_session_registry_is_runtime_checkable(self) -> None:
        class _FakeRegistry:
            def register(self, session: SessionInfo) -> None: ...
            def active(
                self, project: Path | None = None
            ) -> list[SessionInfo]: ...
            def close(
                self, session_id: str, outcome: SessionOutcome
            ) -> None: ...
            def gc(self, max_age_hours: int = 48) -> list[str]: ...

        assert isinstance(_FakeRegistry(), SessionRegistry)

    def test_workstream_monitor_is_runtime_checkable(self) -> None:
        class _FakeMonitor:
            def analyze_session(self, session_id: str) -> SessionInsights:
                return SessionInsights(
                    session_id=session_id,
                    commit_count=0,
                    test_commit_ratio=0.0,
                    revert_count=0,
                    duration_minutes=0,
                )

            def suggest_improvements(
                self, last_n: int = 5
            ) -> list[Improvement]:
                return []

        assert isinstance(_FakeMonitor(), WorkstreamMonitor)

    def test_non_conforming_class_fails(self) -> None:
        class _NotADeriver:
            pass

        assert not isinstance(_NotADeriver(), StateDeriver)
