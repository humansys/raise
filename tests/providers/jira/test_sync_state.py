"""Tests for sync state management.

Tests for SyncMapping, SyncState models and file I/O operations.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError
from rai_pro.providers.jira.sync_state import (
    SyncMapping,
    SyncState,
    load_state,
    save_state,
)


class TestSyncMapping:
    """Tests for SyncMapping model."""

    def test_create_mapping(self) -> None:
        """Create a valid sync mapping."""
        mapping = SyncMapping(
            local_id="E-DEMO",
            jira_key="DEMO-1",
            jira_status="In Progress",
            last_sync_at=datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC),
            sync_direction="pull",
        )
        assert mapping.local_id == "E-DEMO"
        assert mapping.jira_key == "DEMO-1"
        assert mapping.jira_status == "In Progress"
        assert mapping.sync_direction == "pull"

    def test_mapping_requires_fields(self) -> None:
        """Missing required fields raises validation error."""
        with pytest.raises(ValidationError):
            SyncMapping(local_id="E-DEMO")  # type: ignore[call-arg]


class TestSyncState:
    """Tests for SyncState model."""

    def test_empty_state(self) -> None:
        """Create empty state with defaults."""
        state = SyncState(
            cloud_id="abc-123",
            project_key="DEMO",
        )
        assert state.provider == "jira"
        assert state.epics == {}
        assert state.stories == {}
        assert state.last_sync_at is None

    def test_state_with_mappings(self) -> None:
        """Create state with epic and story mappings."""
        now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)
        epic_mapping = SyncMapping(
            local_id="E-DEMO",
            jira_key="DEMO-1",
            jira_status="In Progress",
            last_sync_at=now,
            sync_direction="pull",
        )
        story_mapping = SyncMapping(
            local_id="S-DEMO.1",
            jira_key="DEMO-2",
            jira_status="Approved",
            last_sync_at=now,
            sync_direction="push",
        )
        state = SyncState(
            cloud_id="abc-123",
            project_key="DEMO",
            epics={"E-DEMO": epic_mapping},
            stories={"S-DEMO.1": story_mapping},
            last_sync_at=now,
        )
        assert "E-DEMO" in state.epics
        assert "S-DEMO.1" in state.stories
        assert state.epics["E-DEMO"].jira_key == "DEMO-1"

    def test_state_rejects_extra_fields(self) -> None:
        """Extra fields rejected (strict mode)."""
        with pytest.raises(ValidationError):
            SyncState(
                cloud_id="abc",
                project_key="DEMO",
                unknown_field="value",  # type: ignore[call-arg]
            )


class TestLoadState:
    """Tests for load_state function."""

    def test_load_nonexistent_returns_none(self, tmp_path: Path) -> None:
        """Load from missing file returns None."""
        result = load_state(tmp_path / "sync")
        assert result is None

    def test_load_empty_dir_returns_none(self, tmp_path: Path) -> None:
        """Load from directory without state.json returns None."""
        sync_dir = tmp_path / "sync"
        sync_dir.mkdir()
        result = load_state(sync_dir)
        assert result is None


class TestSaveState:
    """Tests for save_state function."""

    def test_save_creates_directory(self, tmp_path: Path) -> None:
        """Save creates sync directory if missing."""
        sync_dir = tmp_path / ".raise" / "rai" / "sync"
        state = SyncState(cloud_id="abc-123", project_key="DEMO")
        save_state(state, sync_dir)
        assert (sync_dir / "state.json").exists()

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        """Save then load produces identical state."""
        sync_dir = tmp_path / "sync"
        now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)
        state = SyncState(
            cloud_id="abc-123",
            project_key="DEMO",
            epics={
                "E-DEMO": SyncMapping(
                    local_id="E-DEMO",
                    jira_key="DEMO-1",
                    jira_status="In Progress",
                    last_sync_at=now,
                    sync_direction="pull",
                )
            },
            stories={
                "S-DEMO.1": SyncMapping(
                    local_id="S-DEMO.1",
                    jira_key="DEMO-2",
                    jira_status="Approved",
                    last_sync_at=now,
                    sync_direction="push",
                )
            },
            last_sync_at=now,
        )

        save_state(state, sync_dir)
        loaded = load_state(sync_dir)

        assert loaded is not None
        assert loaded.cloud_id == state.cloud_id
        assert loaded.project_key == state.project_key
        assert loaded.epics["E-DEMO"].jira_key == "DEMO-1"
        assert loaded.stories["S-DEMO.1"].jira_status == "Approved"
        assert loaded.last_sync_at == now

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        """Save overwrites existing state file."""
        sync_dir = tmp_path / "sync"
        now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)

        state1 = SyncState(cloud_id="abc-123", project_key="DEMO")
        save_state(state1, sync_dir)

        state2 = SyncState(
            cloud_id="abc-123",
            project_key="DEMO",
            epics={
                "E-DEMO": SyncMapping(
                    local_id="E-DEMO",
                    jira_key="DEMO-1",
                    jira_status="Done",
                    last_sync_at=now,
                    sync_direction="pull",
                )
            },
        )
        save_state(state2, sync_dir)

        loaded = load_state(sync_dir)
        assert loaded is not None
        assert "E-DEMO" in loaded.epics
