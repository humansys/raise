"""Tests for session state schema."""

from __future__ import annotations

from datetime import date

from raise_cli.schemas.session_state import (
    CurrentWork,
    EpicProgress,
    LastSession,
    PendingItems,
    SessionState,
)


class TestCurrentWork:
    """Tests for CurrentWork model."""

    def test_defaults_to_empty_strings(self) -> None:
        """CurrentWork accepts no arguments (all default to empty)."""
        work = CurrentWork()
        assert work.epic == ""
        assert work.story == ""
        assert work.phase == ""
        assert work.branch == ""

    def test_none_coerced_to_empty(self) -> None:
        """CurrentWork coerces None values to empty string (YAML null fix)."""
        work = CurrentWork(epic=None, story=None, phase="design", branch="main")  # type: ignore[arg-type]
        assert work.epic == ""
        assert work.story == ""
        assert work.phase == "design"
        assert work.branch == "main"

    def test_from_yaml_dict_with_nulls(self) -> None:
        """CurrentWork validates from dict with null values (as YAML produces)."""
        data = {"epic": None, "story": None, "phase": "onboarding-complete", "branch": "test/raise-v2"}
        work = CurrentWork.model_validate(data)
        assert work.epic == ""
        assert work.story == ""
        assert work.phase == "onboarding-complete"


class TestEpicProgress:
    """Tests for EpicProgress model."""

    def test_create_progress(self) -> None:
        """EpicProgress holds epic progress data."""
        progress = EpicProgress(
            epic="E15",
            stories_done=5,
            stories_total=8,
            sp_done=16,
            sp_total=25,
        )
        assert progress.epic == "E15"
        assert progress.stories_done == 5
        assert progress.stories_total == 8
        assert progress.sp_done == 16
        assert progress.sp_total == 25

    def test_progress_serialization(self) -> None:
        """EpicProgress round-trips through dict."""
        progress = EpicProgress(
            epic="E15",
            stories_done=3,
            stories_total=7,
            sp_done=9,
            sp_total=22,
        )
        data = progress.model_dump()
        restored = EpicProgress.model_validate(data)
        assert restored == progress


class TestSessionState:
    """Tests for SessionState model."""

    def _make_minimal(self) -> SessionState:
        return SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.8", phase="implement", branch="epic/e15"
            ),
            last_session=LastSession(
                id="SES-003",
                date=date(2026, 2, 8),
                developer="Emilio",
                summary="Task 1 done",
            ),
        )

    def test_progress_default_none(self) -> None:
        """Progress defaults to None."""
        state = self._make_minimal()
        assert state.progress is None

    def test_completed_epics_default_empty(self) -> None:
        """Completed epics defaults to empty list."""
        state = self._make_minimal()
        assert state.completed_epics == []

    def test_with_progress(self) -> None:
        """SessionState accepts progress field."""
        state = self._make_minimal()
        state.progress = EpicProgress(
            epic="E15",
            stories_done=6,
            stories_total=8,
            sp_done=19,
            sp_total=25,
        )
        assert state.progress is not None
        assert state.progress.sp_done == 19

    def test_with_completed_epics(self) -> None:
        """SessionState accepts completed_epics list."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.8", phase="implement", branch="epic/e15"
            ),
            last_session=LastSession(
                id="SES-003",
                date=date(2026, 2, 8),
                developer="Emilio",
                summary="done",
            ),
            completed_epics=["E1", "E2", "E3"],
        )
        assert state.completed_epics == ["E1", "E2", "E3"]

    def test_round_trip_with_new_fields(self) -> None:
        """SessionState with progress and completed_epics round-trips."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.8", phase="implement", branch="epic/e15"
            ),
            last_session=LastSession(
                id="SES-003",
                date=date(2026, 2, 8),
                developer="Emilio",
                summary="done",
            ),
            progress=EpicProgress(
                epic="E15",
                stories_done=5,
                stories_total=8,
                sp_done=16,
                sp_total=25,
            ),
            completed_epics=["E1", "E2"],
        )
        data = state.model_dump()
        restored = SessionState.model_validate(data)
        assert restored.progress is not None
        assert restored.progress.epic == "E15"
        assert restored.completed_epics == ["E1", "E2"]

    def test_backward_compat_no_progress_in_yaml(self) -> None:
        """SessionState loads from dict without progress (backward compat)."""
        data = {
            "current_work": {
                "epic": "E15",
                "story": "S15.7",
                "phase": "design",
                "branch": "main",
            },
            "last_session": {
                "id": "SES-001",
                "date": "2026-02-08",
                "developer": "Test",
                "summary": "test",
            },
        }
        state = SessionState.model_validate(data)
        assert state.progress is None
        assert state.completed_epics == []
