"""Integration tests for JIRA entity properties.

Manual execution against live JIRA Cloud instance.
Requires environment variables:
- JIRA_CLOUD_ID: Cloud ID from OAuth setup
- JIRA_API_TOKEN: OAuth access token
- JIRA_TEST_ISSUE_KEY: Test issue key (e.g., "DEMO-123")

Run with:
    export JIRA_CLOUD_ID="your-cloud-id"
    export JIRA_API_TOKEN="your-token"
    export JIRA_TEST_ISSUE_KEY="DEMO-123"
    pytest tests/providers/jira/test_properties_integration.py -v -s
"""

import os
from datetime import UTC, datetime

import pytest
from rai_pro.providers.jira.client import JiraClient
from rai_pro.providers.jira.models import RaiSyncMetadata
from rai_pro.providers.jira.properties import (
    get_entity_property,
    has_rai_metadata,
    set_entity_property,
)


@pytest.fixture
def jira_client() -> JiraClient:
    """Create JIRA client from environment variables."""
    cloud_id = os.getenv("JIRA_CLOUD_ID")
    token = os.getenv("JIRA_API_TOKEN")

    if not cloud_id or not token:
        pytest.skip("JIRA_CLOUD_ID and JIRA_API_TOKEN environment variables required")

    return JiraClient(cloud_id=cloud_id, access_token=token)


@pytest.fixture
def test_issue_key() -> str:
    """Get test issue key from environment."""
    issue_key = os.getenv("JIRA_TEST_ISSUE_KEY")
    if not issue_key:
        pytest.skip("JIRA_TEST_ISSUE_KEY environment variable required")
    return issue_key


@pytest.mark.integration
def test_roundtrip_entity_property(
    jira_client: JiraClient, test_issue_key: str
) -> None:
    """Test: Create metadata, set property, get property, verify match."""
    # Create test metadata
    original_metadata = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        sync_version="1",
        sync_direction="push",
        last_modified_by="rai",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )

    # Set entity property
    set_entity_property(jira_client, test_issue_key, original_metadata)

    # Get entity property
    retrieved_metadata = get_entity_property(jira_client, test_issue_key)

    # Verify match
    assert retrieved_metadata is not None
    assert retrieved_metadata.epic_id == original_metadata.epic_id
    assert retrieved_metadata.story_id == original_metadata.story_id
    assert retrieved_metadata.rai_branch == original_metadata.rai_branch
    assert retrieved_metadata.local_path == original_metadata.local_path
    assert retrieved_metadata.sync_version == original_metadata.sync_version
    assert retrieved_metadata.sync_direction == original_metadata.sync_direction
    assert retrieved_metadata.last_modified_by == original_metadata.last_modified_by
    # Timestamps may have slight precision differences, so compare as strings
    assert (
        retrieved_metadata.last_sync_at.isoformat()
        == original_metadata.last_sync_at.isoformat()
    )


@pytest.mark.integration
def test_404_handling(jira_client: JiraClient) -> None:
    """Test: Query property from issue without metadata returns None."""
    # Use a non-existent issue key pattern
    # Note: This may fail if the issue exists. Adjust key as needed.
    nonexistent_issue = "DEMO-999999"

    # Should return None, not raise exception
    result = get_entity_property(jira_client, nonexistent_issue)
    assert result is None


@pytest.mark.integration
def test_has_rai_metadata_true(jira_client: JiraClient, test_issue_key: str) -> None:
    """Test: has_rai_metadata returns True for synced issue."""
    # First ensure metadata exists
    metadata = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )
    set_entity_property(jira_client, test_issue_key, metadata)

    # Now check
    assert has_rai_metadata(jira_client, test_issue_key) is True


@pytest.mark.integration
def test_has_rai_metadata_false(jira_client: JiraClient) -> None:
    """Test: has_rai_metadata returns False for unsynced issue."""
    # Use a non-existent issue key
    nonexistent_issue = "DEMO-999999"

    # Should return False
    assert has_rai_metadata(jira_client, nonexistent_issue) is False


@pytest.mark.integration
def test_idempotency(jira_client: JiraClient, test_issue_key: str) -> None:
    """Test: Setting property multiple times is idempotent."""
    metadata_v1 = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )

    # Set first time
    set_entity_property(jira_client, test_issue_key, metadata_v1)
    result_1 = get_entity_property(jira_client, test_issue_key)

    # Set second time with updated timestamp
    metadata_v2 = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        task_id=None,
        last_sync_at=datetime.now(UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/home/emilio/Code/raise-commons",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
    )
    set_entity_property(jira_client, test_issue_key, metadata_v2)
    result_2 = get_entity_property(jira_client, test_issue_key)

    # Both should succeed
    assert result_1 is not None
    assert result_2 is not None
    # Second write should have updated the timestamp
    assert result_2.last_sync_at >= result_1.last_sync_at
