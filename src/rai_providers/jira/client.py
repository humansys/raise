"""JIRA client for bidirectional sync operations.

This module provides a clean wrapper over atlassian-python-api with:
- Rate limiting (10 req/sec for JIRA Cloud)
- Field filtering (minimize API response size)
- OAuth token integration
- Type-safe models (Pydantic)
"""

import time
from collections import deque

from atlassian import Jira

from rai_providers.base import BacklogProvider
from rai_providers.jira.exceptions import (
    JiraAuthError,
    JiraError,
    JiraNotFoundError,
    JiraRateLimitError,
)
from rai_providers.jira.models import JiraEpic, JiraStory, StoryCreate


class RateLimiter:
    """Token bucket rate limiter for API calls.

    Enforces maximum request rate to comply with JIRA Cloud limits (10 req/sec).
    Uses sliding window algorithm to track requests and delays when limit exceeded.

    Attributes:
        _max_requests: Maximum requests allowed per window
        _window: Time window in seconds
        _requests: Deque of request timestamps
    """

    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window (default: 10)
            window_seconds: Time window in seconds (default: 1.0)
        """
        self._max_requests = max_requests
        self._window = window_seconds
        self._requests: deque[float] = deque()

    def wait_if_needed(self) -> None:
        """Block if rate limit would be exceeded.

        Removes requests outside the current window, then checks if at limit.
        If at limit, sleeps until oldest request exits the window.
        """
        now = time.time()

        # Remove requests outside window (sliding window)
        while self._requests and self._requests[0] < now - self._window:
            self._requests.popleft()

        # If at limit, wait until oldest request exits window
        if len(self._requests) >= self._max_requests:
            sleep_time = self._window - (now - self._requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                now = time.time()

        # Record this request
        self._requests.append(now)


class JiraClient(BacklogProvider):
    """JIRA implementation of BacklogProvider interface.

    Provides type-safe methods for reading epics and stories, with:
    - Rate limiting (10 req/sec)
    - Field filtering (only required fields)
    - OAuth token integration
    - Error handling with custom exceptions

    Implements BacklogProvider contract for bidirectional epic-story sync.

    Attributes:
        _jira: Underlying atlassian-python-api client
        _rate_limiter: Rate limiter instance
    """

    def __init__(self, cloud_id: str, access_token: str) -> None:
        """Initialize JIRA client.

        Args:
            cloud_id: Atlassian cloud ID (from OAuth)
            access_token: OAuth access token
        """
        url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        self._jira = Jira(url=url, token=access_token)
        self._rate_limiter = RateLimiter(max_requests=10, window_seconds=1.0)

    def read_epic(self, key: str) -> JiraEpic:
        """Read an epic from JIRA with filtered fields.

        Args:
            key: Epic key (e.g., "DEMO-123")

        Returns:
            JiraEpic with filtered fields

        Raises:
            JiraNotFoundError: Epic doesn't exist or no permission
            JiraAuthError: Authentication failed
            JiraError: Other errors
        """
        self._rate_limiter.wait_if_needed()

        try:
            # Field filtering: only request required fields
            fields = "key,summary,description,status,labels"
            response = self._jira.issue(key, fields=fields)  # type: ignore[no-untyped-call]

            return JiraEpic(
                key=response["key"],  # type: ignore[index,call-overload]
                summary=response["fields"]["summary"],  # type: ignore[index,call-overload]
                description=response["fields"].get("description"),  # type: ignore[union-attr]
                status=response["fields"]["status"]["name"],  # type: ignore[index]
                labels=response["fields"].get("labels", []),  # type: ignore[union-attr]
            )
        except Exception as e:
            raise self._map_error(e, key) from e

    def read_stories_for_epic(self, epic_key: str) -> list[JiraStory]:
        """Read all stories under an epic.

        Args:
            epic_key: Parent epic key (e.g., "DEMO-123")

        Returns:
            List of JiraStory objects (empty if no stories)

        Raises:
            JiraAuthError: Authentication failed
            JiraError: Other errors
        """
        self._rate_limiter.wait_if_needed()

        try:
            # JQL query for stories under epic
            jql = f"parent = {epic_key}"
            fields = "key,summary,description,status,labels,parent"
            response = self._jira.jql(jql, fields=fields)  # type: ignore[no-untyped-call]

            stories: list[JiraStory] = []
            for issue in response.get("issues", []):  # type: ignore[union-attr]
                stories.append(
                    JiraStory(
                        key=issue["key"],  # type: ignore[index,call-overload]
                        summary=issue["fields"]["summary"],  # type: ignore[index,call-overload]
                        description=issue["fields"].get("description"),  # type: ignore[union-attr]
                        status=issue["fields"]["status"]["name"],  # type: ignore[index]
                        labels=issue["fields"].get("labels", []),  # type: ignore[union-attr]
                        epic_key=issue["fields"]["parent"]["key"],  # type: ignore[index]
                    )
                )

            return stories
        except Exception as e:
            raise self._map_error(e, epic_key) from e

    def read_epic_status(self, key: str) -> str:
        """Get epic status.

        Args:
            key: Epic key (e.g., "DEMO-123")

        Returns:
            Status name (e.g., "In Progress", "Done")

        Raises:
            JiraNotFoundError: Epic doesn't exist
            JiraAuthError: Authentication failed
            JiraError: Other errors
        """
        epic = self.read_epic(key)
        return epic.status

    def read_story_status(self, key: str) -> str:
        """Get story status.

        Args:
            key: Story key (e.g., "DEMO-124")

        Returns:
            Status name (e.g., "To Do", "In Progress", "Done")

        Raises:
            JiraNotFoundError: Story doesn't exist
            JiraAuthError: Authentication failed
            JiraError: Other errors
        """
        self._rate_limiter.wait_if_needed()

        try:
            fields = "key,summary,status,labels"
            response = self._jira.issue(key, fields=fields)  # type: ignore[no-untyped-call]
            return response["fields"]["status"]["name"]  # type: ignore[index,return-value]
        except Exception as e:
            raise self._map_error(e, key) from e

    def create_story(self, epic_key: str, story: StoryCreate) -> JiraStory:
        """Create a JIRA story under a parent epic.

        Args:
            epic_key: Parent epic key (e.g., "DEMO-123")
            story: Story data to create

        Returns:
            Created JiraStory with JIRA-assigned key

        Raises:
            JiraNotFoundError: Epic doesn't exist or no permission
            JiraAuthError: Authentication failed
            JiraError: Other errors
        """
        self._rate_limiter.wait_if_needed()

        try:
            # Extract project key from epic key (DEMO-123 → DEMO)
            project_key = self._extract_project_key(epic_key)

            # Build create payload with field filtering
            fields = {
                "project": {"key": project_key},
                "summary": story.summary,
                "issuetype": {"name": "Story"},
                "parent": {"key": epic_key},
            }

            # Add optional fields only if provided
            if story.description:
                fields["description"] = story.description

            if story.labels:
                fields["labels"] = story.labels

            # Create story via API
            response = self._jira.create_issue(fields=fields)  # type: ignore[no-untyped-call]

            # Return created story
            return JiraStory(
                key=response["key"],  # type: ignore[index,call-overload]
                summary=story.summary,
                description=story.description,
                status=response["fields"]["status"]["name"],  # type: ignore[index]
                labels=story.labels,
                epic_key=epic_key,
            )
        except Exception as e:
            raise self._map_error(e, epic_key) from e

    def _extract_project_key(self, issue_key: str) -> str:
        """Extract project key from issue key.

        Args:
            issue_key: Issue key (e.g., "DEMO-123")

        Returns:
            Project key (e.g., "DEMO")
        """
        return issue_key.split("-")[0]

    def _map_error(self, error: Exception, context: str = "") -> JiraError:
        """Map atlassian-python-api errors to custom exceptions.

        Args:
            error: Original exception
            context: Additional context (e.g., issue key)

        Returns:
            Appropriate JiraError subclass
        """
        error_msg = str(error).lower()

        if "401" in error_msg or "unauthorized" in error_msg or "403" in error_msg:
            return JiraAuthError(f"Authentication failed: {error}")

        if "404" in error_msg or "does not exist" in error_msg:
            return JiraNotFoundError(f"{context} not found or no permission: {error}")

        if "429" in error_msg or "too many requests" in error_msg:
            return JiraRateLimitError(f"Rate limit exceeded: {error}")

        # Generic error
        return JiraError(f"JIRA API error: {error}")
