"""Tests for sync engine (pull, push, authorization).

Uses mocked JiraClient to test sync logic without JIRA API calls.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from rai_pro.providers.jira.models import JiraEpic, JiraStory
from rai_pro.providers.jira.sync import (
    LocalStory,
    check_authorization,
    pull_epic,
    push_stories,
)
from rai_pro.providers.jira.sync_state import SyncMapping, SyncState


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mocked JiraClient."""
    client = MagicMock()
    return client


@pytest.fixture
def empty_state() -> SyncState:
    """Create empty sync state."""
    return SyncState(cloud_id="test-cloud", project_key="DEMO")


@pytest.fixture
def state_with_epic() -> SyncState:
    """Create state with one epic mapped."""
    now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)
    return SyncState(
        cloud_id="test-cloud",
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
    )


@pytest.fixture
def state_with_stories() -> SyncState:
    """Create state with epic and stories mapped."""
    now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)
    return SyncState(
        cloud_id="test-cloud",
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
            ),
            "S-DEMO.2": SyncMapping(
                local_id="S-DEMO.2",
                jira_key="DEMO-3",
                jira_status="To Do",
                last_sync_at=now,
                sync_direction="push",
            ),
        },
    )


class TestPullEpic:
    """Tests for pull_epic function."""

    def test_pull_new_epic(
        self, mock_client: MagicMock, empty_state: SyncState
    ) -> None:
        """Pull epic not in state creates new mapping."""
        mock_client.read_epic.return_value = JiraEpic(
            key="DEMO-1",
            summary="Product Governance Initiative",
            description="Test epic",
            status="In Progress",
            labels=["governance"],
        )
        mock_client.read_stories_for_epic.return_value = []

        result = pull_epic(
            client=mock_client,
            epic_key="DEMO-1",
            epic_id="E-DEMO",
            state=empty_state,
        )

        assert result.epic_imported is True
        assert "E-DEMO" in empty_state.epics
        assert empty_state.epics["E-DEMO"].jira_key == "DEMO-1"
        assert empty_state.epics["E-DEMO"].jira_status == "In Progress"
        assert empty_state.epics["E-DEMO"].sync_direction == "pull"

    def test_pull_existing_epic_updates_status(
        self, mock_client: MagicMock, state_with_epic: SyncState
    ) -> None:
        """Pull epic already in state updates status."""
        mock_client.read_epic.return_value = JiraEpic(
            key="DEMO-1",
            summary="Product Governance Initiative",
            status="Done",
            labels=[],
        )
        mock_client.read_stories_for_epic.return_value = []

        result = pull_epic(
            client=mock_client,
            epic_key="DEMO-1",
            epic_id="E-DEMO",
            state=state_with_epic,
        )

        assert result.epic_imported is False  # Not new, just updated
        assert state_with_epic.epics["E-DEMO"].jira_status == "Done"

    def test_pull_with_stories(
        self, mock_client: MagicMock, empty_state: SyncState
    ) -> None:
        """Pull epic with stories maps all items."""
        mock_client.read_epic.return_value = JiraEpic(
            key="DEMO-1",
            summary="Test Epic",
            status="In Progress",
            labels=[],
        )
        mock_client.read_stories_for_epic.return_value = [
            JiraStory(
                key="DEMO-2",
                summary="Story One",
                status="Approved",
                epic_key="DEMO-1",
            ),
            JiraStory(
                key="DEMO-3",
                summary="Story Two",
                status="To Do",
                epic_key="DEMO-1",
            ),
        ]

        result = pull_epic(
            client=mock_client,
            epic_key="DEMO-1",
            epic_id="E-DEMO",
            state=empty_state,
        )

        assert result.stories_imported == 2
        assert result.stories_updated == 0
        assert len(empty_state.stories) == 2
        # Stories get sequential IDs
        story_ids = sorted(empty_state.stories.keys())
        assert story_ids == ["S-DEMO.1", "S-DEMO.2"]

    def test_pull_updates_existing_story_status(
        self, mock_client: MagicMock, state_with_stories: SyncState
    ) -> None:
        """Pull updates status of stories already in state."""
        mock_client.read_epic.return_value = JiraEpic(
            key="DEMO-1",
            summary="Test Epic",
            status="In Progress",
            labels=[],
        )
        mock_client.read_stories_for_epic.return_value = [
            JiraStory(
                key="DEMO-2",
                summary="Story One",
                status="In Progress",  # Changed from Approved
                epic_key="DEMO-1",
            ),
            JiraStory(
                key="DEMO-3",
                summary="Story Two",
                status="Approved",  # Changed from To Do
                epic_key="DEMO-1",
            ),
        ]

        result = pull_epic(
            client=mock_client,
            epic_key="DEMO-1",
            epic_id="E-DEMO",
            state=state_with_stories,
        )

        assert result.stories_updated == 2
        assert result.stories_imported == 0
        assert state_with_stories.stories["S-DEMO.1"].jira_status == "In Progress"
        assert state_with_stories.stories["S-DEMO.2"].jira_status == "Approved"

    def test_pull_dry_run_no_state_change(
        self, mock_client: MagicMock, empty_state: SyncState
    ) -> None:
        """Dry run doesn't modify state."""
        mock_client.read_epic.return_value = JiraEpic(
            key="DEMO-1",
            summary="Test Epic",
            status="In Progress",
            labels=[],
        )
        mock_client.read_stories_for_epic.return_value = []

        result = pull_epic(
            client=mock_client,
            epic_key="DEMO-1",
            epic_id="E-DEMO",
            state=empty_state,
            dry_run=True,
        )

        assert result.dry_run is True
        assert len(empty_state.epics) == 0  # State unchanged


class TestPushStories:
    """Tests for push_stories function."""

    def test_push_new_stories(
        self, mock_client: MagicMock, state_with_epic: SyncState
    ) -> None:
        """Push new stories creates JIRA issues."""
        mock_client.create_story.side_effect = [
            JiraStory(
                key="DEMO-2", summary="Story One", status="To Do", epic_key="DEMO-1"
            ),
            JiraStory(
                key="DEMO-3", summary="Story Two", status="To Do", epic_key="DEMO-1"
            ),
        ]

        stories = [
            LocalStory(story_id="S-DEMO.1", title="Story One"),
            LocalStory(story_id="S-DEMO.2", title="Story Two"),
        ]

        result = push_stories(
            client=mock_client,
            epic_id="E-DEMO",
            stories=stories,
            state=state_with_epic,
        )

        assert result.created == 2
        assert result.skipped == 0
        assert "S-DEMO.1" in state_with_epic.stories
        assert "S-DEMO.2" in state_with_epic.stories
        assert state_with_epic.stories["S-DEMO.1"].jira_key == "DEMO-2"
        assert mock_client.create_story.call_count == 2

    def test_push_existing_stories_skipped(
        self, mock_client: MagicMock, state_with_stories: SyncState
    ) -> None:
        """Push stories already in state are skipped (idempotent)."""
        stories = [
            LocalStory(story_id="S-DEMO.1", title="Story One"),
            LocalStory(story_id="S-DEMO.2", title="Story Two"),
        ]

        result = push_stories(
            client=mock_client,
            epic_id="E-DEMO",
            stories=stories,
            state=state_with_stories,
        )

        assert result.created == 0
        assert result.skipped == 2
        mock_client.create_story.assert_not_called()

    def test_push_sets_entity_properties(
        self, mock_client: MagicMock, state_with_epic: SyncState
    ) -> None:
        """Push sets entity properties on created stories."""
        mock_client.create_story.return_value = JiraStory(
            key="DEMO-2", summary="Story One", status="To Do", epic_key="DEMO-1"
        )

        stories = [LocalStory(story_id="S-DEMO.1", title="Story One")]

        with patch("rai_pro.providers.jira.sync.set_entity_property") as mock_set:
            push_stories(
                client=mock_client,
                epic_id="E-DEMO",
                stories=stories,
                state=state_with_epic,
            )
            mock_set.assert_called_once()
            call_args = mock_set.call_args
            metadata = call_args[0][2]  # Third positional arg
            assert metadata.epic_id == "E-DEMO"
            assert metadata.story_id == "S-DEMO.1"
            assert metadata.sync_direction == "push"

    def test_push_without_epic_mapping_raises(
        self, mock_client: MagicMock, empty_state: SyncState
    ) -> None:
        """Push for unmapped epic raises error."""
        stories = [LocalStory(story_id="S-DEMO.1", title="Story One")]

        with pytest.raises(ValueError, match="not mapped"):
            push_stories(
                client=mock_client,
                epic_id="E-DEMO",
                stories=stories,
                state=empty_state,
            )

    def test_push_dry_run_no_jira_calls(
        self, mock_client: MagicMock, state_with_epic: SyncState
    ) -> None:
        """Dry run doesn't call JIRA API or modify state."""
        stories = [LocalStory(story_id="S-DEMO.1", title="Story One")]

        result = push_stories(
            client=mock_client,
            epic_id="E-DEMO",
            stories=stories,
            state=state_with_epic,
            dry_run=True,
        )

        assert result.dry_run is True
        assert result.created == 0
        mock_client.create_story.assert_not_called()
        assert "S-DEMO.1" not in state_with_epic.stories

    def test_push_mixed_new_and_existing(
        self, mock_client: MagicMock, state_with_stories: SyncState
    ) -> None:
        """Push with mix of new and existing stories."""
        mock_client.create_story.return_value = JiraStory(
            key="DEMO-10", summary="New Story", status="To Do", epic_key="DEMO-1"
        )

        stories = [
            LocalStory(story_id="S-DEMO.1", title="Existing"),  # Already in state
            LocalStory(story_id="S-DEMO.3", title="New Story"),  # Not in state
        ]

        result = push_stories(
            client=mock_client,
            epic_id="E-DEMO",
            stories=stories,
            state=state_with_stories,
        )

        assert result.created == 1
        assert result.skipped == 1
        assert mock_client.create_story.call_count == 1


class TestCheckAuthorization:
    """Tests for check_authorization function."""

    def test_authorized_story(self, state_with_stories: SyncState) -> None:
        """Story with 'Approved' status is authorized."""
        result = check_authorization(state_with_stories, "S-DEMO.1")
        assert result.authorized is True
        assert result.jira_status == "Approved"

    def test_unauthorized_story(self, state_with_stories: SyncState) -> None:
        """Story with 'To Do' status is not authorized."""
        result = check_authorization(state_with_stories, "S-DEMO.2")
        assert result.authorized is False
        assert result.jira_status == "To Do"

    def test_unsynced_story(self, empty_state: SyncState) -> None:
        """Story not in state has no JIRA mapping — no gate."""
        result = check_authorization(empty_state, "S-DEMO.99")
        assert result.authorized is True  # No JIRA mapping = no gate
        assert result.jira_status is None

    def test_custom_authorized_statuses(self, state_with_stories: SyncState) -> None:
        """Custom status list overrides default."""
        # "To Do" is not in default authorized list, but we add it
        result = check_authorization(
            state_with_stories,
            "S-DEMO.2",
            authorized_statuses=["To Do", "Approved"],
        )
        assert result.authorized is True

    def test_in_progress_is_authorized(self) -> None:
        """'In Progress' is authorized by default."""
        now = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)
        state = SyncState(
            cloud_id="test",
            project_key="DEMO",
            stories={
                "S-DEMO.1": SyncMapping(
                    local_id="S-DEMO.1",
                    jira_key="DEMO-2",
                    jira_status="In Progress",
                    last_sync_at=now,
                    sync_direction="push",
                )
            },
        )
        result = check_authorization(state, "S-DEMO.1")
        assert result.authorized is True
