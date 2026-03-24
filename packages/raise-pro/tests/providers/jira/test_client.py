"""Tests for JIRA client with read operations and rate limiting."""

import time
from unittest.mock import Mock, patch

import pytest
from rai_pro.providers.jira.client import JiraClient, RateLimiter
from rai_pro.providers.jira.exceptions import (
    JiraAuthError,
    JiraError,
    JiraNotFoundError,
    JiraRateLimitError,
)
from rai_pro.providers.jira.models import JiraEpic, JiraStory


class TestRateLimiter:
    """Tests for RateLimiter (token bucket algorithm)."""

    def test_rate_limiter_initialization(self) -> None:
        """Test rate limiter initializes with correct defaults."""
        limiter = RateLimiter(max_requests=10, window_seconds=1.0)

        assert limiter._max_requests == 10
        assert limiter._window == 1.0
        assert len(limiter._requests) == 0

    def test_rate_limiter_allows_requests_under_limit(self) -> None:
        """Test that requests under limit are allowed without delay."""
        limiter = RateLimiter(max_requests=10, window_seconds=1.0)

        start = time.time()
        for _ in range(5):
            limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should complete almost instantly (< 0.1s)
        assert elapsed < 0.1

    def test_rate_limiter_enforces_limit(self) -> None:
        """Test that rate limiter enforces the limit by delaying."""
        limiter = RateLimiter(max_requests=5, window_seconds=1.0)

        start = time.time()
        for _ in range(7):  # Exceed limit
            limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should take at least 1 second (waited for window to clear)
        assert elapsed >= 0.9  # Allow small margin

    def test_rate_limiter_window_sliding(self) -> None:
        """Test that old requests outside window are removed."""
        limiter = RateLimiter(max_requests=3, window_seconds=0.5)

        # Fill bucket
        for _ in range(3):
            limiter.wait_if_needed()

        # Wait for window to pass
        time.sleep(0.6)

        # Should allow new requests without delay
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        assert elapsed < 0.1


class TestJiraClient:
    """Tests for JiraClient read operations."""

    @pytest.fixture
    def mock_jira(self) -> Mock:
        """Create a mock Jira instance."""
        mock = Mock()
        return mock

    @pytest.fixture
    def client(self, mock_jira: Mock) -> JiraClient:
        """Create a JiraClient with mocked Jira instance."""
        with patch("rai_pro.providers.jira.client.Jira", return_value=mock_jira):
            client = JiraClient(cloud_id="test-cloud-id", access_token="test-token")
            client._jira = mock_jira
        return client

    def test_client_initialization(self) -> None:
        """Test JiraClient initializes correctly."""
        with patch("rai_pro.providers.jira.client.Jira") as mock_jira_class:
            client = JiraClient(cloud_id="test-cloud", access_token="test-token")

            mock_jira_class.assert_called_once()
            assert client._rate_limiter is not None
            assert client._rate_limiter._max_requests == 10
            assert client._rate_limiter._window == 1.0

    def test_read_epic_success(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test reading an epic successfully."""
        mock_jira.issue.return_value = {
            "key": "DEMO-123",
            "fields": {
                "summary": "Product Governance Initiative",
                "description": "Epic description here",
                "status": {"name": "In Progress"},
                "labels": ["governance", "mvp"],
            },
        }

        epic = client.read_epic("DEMO-123")

        assert isinstance(epic, JiraEpic)
        assert epic.key == "DEMO-123"
        assert epic.summary == "Product Governance Initiative"
        assert epic.description == "Epic description here"
        assert epic.status == "In Progress"
        assert epic.labels == ["governance", "mvp"]

        # Verify fields parameter used (field filtering)
        mock_jira.issue.assert_called_once_with(
            "DEMO-123", fields="key,summary,description,status,labels"
        )

    def test_read_epic_not_found(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test reading non-existent epic raises JiraNotFoundError."""
        mock_jira.issue.side_effect = Exception("Issue Does Not Exist")

        with pytest.raises(JiraNotFoundError) as exc_info:
            client.read_epic("INVALID-999")

        assert "INVALID-999" in str(exc_info.value)

    def test_read_epic_auth_error(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test authentication error raises JiraAuthError."""
        mock_jira.issue.side_effect = Exception("401 Unauthorized")

        with pytest.raises(JiraAuthError):
            client.read_epic("DEMO-123")

    def test_read_stories_for_epic_success(
        self, client: JiraClient, mock_jira: Mock
    ) -> None:
        """Test reading stories for an epic successfully."""
        mock_jira.jql.return_value = {
            "issues": [
                {
                    "key": "DEMO-124",
                    "fields": {
                        "summary": "Define governance principles",
                        "description": "Story description",
                        "status": {"name": "To Do"},
                        "labels": ["governance"],
                        "parent": {"key": "DEMO-123"},
                    },
                },
                {
                    "key": "DEMO-125",
                    "fields": {
                        "summary": "Create compliance checklist",
                        "description": None,
                        "status": {"name": "In Progress"},
                        "labels": [],
                        "parent": {"key": "DEMO-123"},
                    },
                },
            ]
        }

        stories = client.read_stories_for_epic("DEMO-123")

        assert len(stories) == 2
        assert isinstance(stories[0], JiraStory)
        assert stories[0].key == "DEMO-124"
        assert stories[0].summary == "Define governance principles"
        assert stories[0].epic_key == "DEMO-123"
        assert stories[1].key == "DEMO-125"
        assert stories[1].description is None

        # Verify JQL query used
        mock_jira.jql.assert_called_once()
        call_args = mock_jira.jql.call_args
        assert "parent = DEMO-123" in call_args[0][0]
        assert call_args[1]["fields"] == "key,summary,description,status,labels,parent"

    def test_read_stories_for_epic_empty(
        self, client: JiraClient, mock_jira: Mock
    ) -> None:
        """Test reading stories when epic has no stories."""
        mock_jira.jql.return_value = {"issues": []}

        stories = client.read_stories_for_epic("DEMO-999")

        assert stories == []

    def test_read_epic_status(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test reading epic status."""
        mock_jira.issue.return_value = {
            "key": "DEMO-123",
            "fields": {
                "summary": "Test Epic",
                "status": {"name": "Done"},
                "labels": [],
            },
        }

        status = client.read_epic_status("DEMO-123")

        assert status == "Done"

    def test_read_story_status(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test reading story status."""
        mock_jira.issue.return_value = {
            "key": "DEMO-124",
            "fields": {
                "summary": "Test Story",
                "status": {"name": "In Progress"},
                "labels": [],
            },
        }

        status = client.read_story_status("DEMO-124")

        assert status == "In Progress"

    def test_rate_limiting_applied(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test that rate limiter is called for each API operation."""
        mock_jira.issue.return_value = {
            "key": "DEMO-123",
            "fields": {
                "summary": "Test",
                "status": {"name": "To Do"},
                "labels": [],
            },
        }

        with patch.object(client._rate_limiter, "wait_if_needed") as mock_wait:
            client.read_epic("DEMO-123")
            mock_wait.assert_called_once()

    def test_error_mapping_404(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test that 404 errors map to JiraNotFoundError."""
        mock_jira.issue.side_effect = Exception("404 Not Found")

        with pytest.raises(JiraNotFoundError):
            client.read_epic("DEMO-999")

    def test_error_mapping_429(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test that 429 errors map to JiraRateLimitError."""
        mock_jira.issue.side_effect = Exception("429 Too Many Requests")

        with pytest.raises(JiraRateLimitError):
            client.read_epic("DEMO-123")

    def test_error_mapping_generic(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test that unknown errors map to generic JiraError."""
        mock_jira.issue.side_effect = Exception("500 Internal Server Error")

        with pytest.raises(JiraError) as exc_info:
            client.read_epic("DEMO-123")

        # Should be generic JiraError, not a subclass
        assert isinstance(exc_info.value, JiraError)
        assert not isinstance(
            exc_info.value, (JiraAuthError, JiraNotFoundError, JiraRateLimitError)
        )


class TestJiraClientWriteOperations:
    """Tests for JiraClient write operations (create story)."""

    @pytest.fixture
    def mock_jira(self) -> Mock:
        """Create a mock Jira instance."""
        mock = Mock()
        return mock

    @pytest.fixture
    def client(self, mock_jira: Mock) -> JiraClient:
        """Create a JiraClient with mocked Jira instance."""
        with patch("rai_pro.providers.jira.client.Jira", return_value=mock_jira):
            client = JiraClient(cloud_id="test-cloud-id", access_token="test-token")
            client._jira = mock_jira
        return client

    def test_create_story_success(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test creating a story under an epic successfully."""
        from rai_pro.providers.jira.models import StoryCreate

        # Mock response from JIRA
        mock_jira.create_issue.return_value = {
            "key": "DEMO-124",
            "fields": {
                "summary": "Implement value metrics",
                "description": "Design and implement value measurement framework",
                "status": {"name": "To Do"},
                "labels": ["governance", "metrics"],
            },
        }

        story_data = StoryCreate(
            summary="Implement value metrics",
            description="Design and implement value measurement framework",
            labels=["governance", "metrics"],
        )

        created_story = client.create_story("DEMO-123", story_data)

        assert isinstance(created_story, JiraStory)
        assert created_story.key == "DEMO-124"
        assert created_story.summary == "Implement value metrics"
        assert (
            created_story.description
            == "Design and implement value measurement framework"
        )
        assert created_story.status == "To Do"
        assert created_story.labels == ["governance", "metrics"]
        assert created_story.epic_key == "DEMO-123"

        # Verify API call structure
        mock_jira.create_issue.assert_called_once()
        call_args = mock_jira.create_issue.call_args
        fields = call_args[1]["fields"]

        assert fields["summary"] == "Implement value metrics"
        assert fields["issuetype"]["name"] == "Story"
        assert fields["parent"]["key"] == "DEMO-123"
        assert fields["labels"] == ["governance", "metrics"]

    def test_create_story_minimal(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test creating a story with minimal fields (summary only)."""
        from rai_pro.providers.jira.models import StoryCreate

        mock_jira.create_issue.return_value = {
            "key": "DEMO-125",
            "fields": {
                "summary": "Minimal story",
                "description": None,
                "status": {"name": "To Do"},
                "labels": [],
            },
        }

        story_data = StoryCreate(summary="Minimal story")
        created_story = client.create_story("DEMO-123", story_data)

        assert created_story.key == "DEMO-125"
        assert created_story.summary == "Minimal story"
        assert created_story.description is None
        assert created_story.labels == []

    def test_create_story_extracts_project_key(
        self, client: JiraClient, mock_jira: Mock
    ) -> None:
        """Test that project key is correctly extracted from epic key."""
        from rai_pro.providers.jira.models import StoryCreate

        mock_jira.create_issue.return_value = {
            "key": "PROJ-999",
            "fields": {
                "summary": "Test",
                "status": {"name": "To Do"},
                "labels": [],
            },
        }

        story_data = StoryCreate(summary="Test story")
        client.create_story("PROJ-456", story_data)

        # Verify project key extracted correctly
        call_args = mock_jira.create_issue.call_args
        fields = call_args[1]["fields"]
        assert fields["project"]["key"] == "PROJ"

    def test_create_story_epic_not_found(
        self, client: JiraClient, mock_jira: Mock
    ) -> None:
        """Test creating story with non-existent epic raises JiraNotFoundError."""
        from rai_pro.providers.jira.models import StoryCreate

        mock_jira.create_issue.side_effect = Exception("Parent does not exist")

        story_data = StoryCreate(summary="Test story")

        with pytest.raises(JiraNotFoundError):
            client.create_story("INVALID-999", story_data)

    def test_create_story_auth_error(self, client: JiraClient, mock_jira: Mock) -> None:
        """Test creating story with auth error raises JiraAuthError."""
        from rai_pro.providers.jira.models import StoryCreate

        mock_jira.create_issue.side_effect = Exception("401 Unauthorized")

        story_data = StoryCreate(summary="Test story")

        with pytest.raises(JiraAuthError):
            client.create_story("DEMO-123", story_data)

    def test_create_story_rate_limiting_applied(
        self, client: JiraClient, mock_jira: Mock
    ) -> None:
        """Test that rate limiter is called for create operation."""
        from rai_pro.providers.jira.models import StoryCreate

        mock_jira.create_issue.return_value = {
            "key": "DEMO-124",
            "fields": {
                "summary": "Test",
                "status": {"name": "To Do"},
                "labels": [],
            },
        }

        story_data = StoryCreate(summary="Test story")

        with patch.object(client._rate_limiter, "wait_if_needed") as mock_wait:
            client.create_story("DEMO-123", story_data)
            mock_wait.assert_called_once()
