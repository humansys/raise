"""Tests for JIRA Pydantic models."""

import pytest
from pydantic import ValidationError
from rai_pro.providers.jira.models import JiraEpic, JiraStory, StoryCreate


class TestJiraEpic:
    """Tests for JiraEpic model."""

    def test_valid_epic(self) -> None:
        """Test creating a valid epic with all fields."""
        epic = JiraEpic(
            key="DEMO-123",
            summary="Product Governance Initiative",
            description="Full epic description here",
            status="In Progress",
            labels=["governance", "mvp"],
        )

        assert epic.key == "DEMO-123"
        assert epic.summary == "Product Governance Initiative"
        assert epic.description == "Full epic description here"
        assert epic.status == "In Progress"
        assert epic.labels == ["governance", "mvp"]

    def test_epic_minimal_fields(self) -> None:
        """Test epic with only required fields (description and labels optional)."""
        epic = JiraEpic(
            key="DEMO-456",
            summary="Minimal Epic",
            status="To Do",
        )

        assert epic.key == "DEMO-456"
        assert epic.summary == "Minimal Epic"
        assert epic.description is None
        assert epic.status == "To Do"
        assert epic.labels == []

    def test_epic_missing_required_field(self) -> None:
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            JiraEpic(
                key="DEMO-789",
                # Missing summary (required)
                status="Done",
            )

        assert "summary" in str(exc_info.value)


class TestJiraStory:
    """Tests for JiraStory model."""

    def test_valid_story(self) -> None:
        """Test creating a valid story with all fields."""
        story = JiraStory(
            key="DEMO-124",
            summary="Define governance principles",
            description="Story description here",
            status="To Do",
            labels=["governance"],
            epic_key="DEMO-123",
        )

        assert story.key == "DEMO-124"
        assert story.summary == "Define governance principles"
        assert story.description == "Story description here"
        assert story.status == "To Do"
        assert story.labels == ["governance"]
        assert story.epic_key == "DEMO-123"

    def test_story_minimal_fields(self) -> None:
        """Test story with only required fields."""
        story = JiraStory(
            key="DEMO-125",
            summary="Minimal Story",
            status="In Progress",
        )

        assert story.key == "DEMO-125"
        assert story.summary == "Minimal Story"
        assert story.description is None
        assert story.status == "In Progress"
        assert story.labels == []
        assert story.epic_key is None

    def test_story_missing_required_field(self) -> None:
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            JiraStory(
                key="DEMO-126",
                summary="Test Story",
                # Missing status (required)
            )

        assert "status" in str(exc_info.value)


class TestStoryCreate:
    """Tests for StoryCreate model (input for story creation)."""

    def test_valid_story_create(self) -> None:
        """Test creating a valid StoryCreate with all fields."""
        story = StoryCreate(
            summary="Implement value metrics",
            description="Design and implement value measurement framework",
            labels=["governance", "metrics"],
        )

        assert story.summary == "Implement value metrics"
        assert story.description == "Design and implement value measurement framework"
        assert story.labels == ["governance", "metrics"]

    def test_story_create_minimal(self) -> None:
        """Test StoryCreate with only required field (summary)."""
        story = StoryCreate(summary="Minimal story")

        assert story.summary == "Minimal story"
        assert story.description is None
        assert story.labels == []

    def test_story_create_summary_too_short(self) -> None:
        """Test that empty summary raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StoryCreate(summary="")

        # Pydantic uses "string_too_short" error type
        assert "string_too_short" in str(exc_info.value).lower()

    def test_story_create_summary_too_long(self) -> None:
        """Test that summary > 255 chars raises validation error."""
        long_summary = "x" * 256

        with pytest.raises(ValidationError) as exc_info:
            StoryCreate(summary=long_summary)

        # Pydantic uses "string_too_long" error type
        assert "string_too_long" in str(exc_info.value).lower()

    def test_story_create_missing_summary(self) -> None:
        """Test that missing summary raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StoryCreate()  # type: ignore

        assert "summary" in str(exc_info.value)
