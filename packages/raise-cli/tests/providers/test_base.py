"""Tests for BacklogProvider abstract interface."""

from abc import ABC

import pytest
from rai_pro.providers.base import BacklogProvider
from rai_pro.providers.jira.client import JiraClient


def test_backlog_provider_is_abstract():
    """BacklogProvider should be an abstract base class."""
    assert issubclass(BacklogProvider, ABC)
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BacklogProvider()  # type: ignore


def test_backlog_provider_has_required_methods():
    """BacklogProvider should define required abstract methods."""
    required_methods = {"read_epic", "read_stories_for_epic", "create_story"}
    abstract_methods = BacklogProvider.__abstractmethods__  # type: ignore
    assert required_methods == set(abstract_methods)


def test_jira_client_implements_backlog_provider():
    """JiraClient should implement BacklogProvider interface."""
    assert issubclass(JiraClient, BacklogProvider)

    # Verify all abstract methods are implemented
    client = JiraClient(cloud_id="test-cloud", access_token="test-token")
    assert hasattr(client, "read_epic")
    assert callable(client.read_epic)
    assert hasattr(client, "read_stories_for_epic")
    assert callable(client.read_stories_for_epic)
    assert hasattr(client, "create_story")
    assert callable(client.create_story)
