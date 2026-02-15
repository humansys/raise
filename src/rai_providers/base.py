"""Abstract base classes for provider interfaces.

This module defines the contracts that provider implementations (JIRA, GitLab,
Odoo, Local) must satisfy for bidirectional sync operations.
"""

from abc import ABC, abstractmethod
from typing import Any


class BacklogProvider(ABC):
    """Abstract interface for backlog providers (JIRA, GitLab, Odoo, Local).

    This interface defines the contract for bidirectional sync operations.
    Implementations should handle provider-specific details (auth, API calls,
    rate limiting, error handling, etc.).

    Design Principles:
    - Provider-agnostic: Methods work with Any to allow provider-specific models
    - Minimal: Only the operations required for epic-story sync
    - Extensible: Easy to add new providers without changing consumers
    """

    @abstractmethod
    def read_epic(self, key: str) -> Any:
        """Read an epic from the provider.

        Args:
            key: Provider-specific epic identifier (e.g., "DEMO-123" for JIRA)

        Returns:
            Epic data (provider-specific model, e.g., JiraEpic)

        Raises:
            Provider-specific exceptions for auth, not found, rate limiting, etc.
        """
        pass

    @abstractmethod
    def read_stories_for_epic(self, epic_key: str) -> list[Any]:
        """Read all stories under an epic.

        Args:
            epic_key: Parent epic identifier

        Returns:
            List of story data (provider-specific models, e.g., JiraStory)

        Raises:
            Provider-specific exceptions for auth, not found, rate limiting, etc.
        """
        pass

    @abstractmethod
    def create_story(self, epic_key: str, story: Any) -> Any:
        """Create a story under a parent epic.

        Args:
            epic_key: Parent epic identifier
            story: Story data (provider-specific input model, e.g., StoryCreate)

        Returns:
            Created story data (provider-specific model, e.g., JiraStory)

        Raises:
            Provider-specific exceptions for auth, not found, rate limiting, etc.
        """
        pass
