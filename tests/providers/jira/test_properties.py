"""Tests for JIRA entity property storage/retrieval functions.

Tests set_entity_property, get_entity_property, and has_rai_metadata with mocked client.
TDD: RED phase - tests written before implementation.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from rai_pro.providers.jira.client import JiraClient
from rai_pro.providers.jira.exceptions import JiraApiError
from rai_pro.providers.jira.models import RaiSyncMetadata
from rai_pro.providers.jira.properties import (
    PROPERTY_KEY,
    get_entity_property,
    has_rai_metadata,
    set_entity_property,
)


class TestSetEntityProperty:
    """Test set_entity_property function."""

    def test_set_entity_property_success(self) -> None:
        """Test successful entity property storage."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()
        mock_client._jira.put = Mock()

        metadata = RaiSyncMetadata(
            epic_id="E-DEMO",
            story_id="S-DEMO.4",
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        set_entity_property(mock_client, "DEMO-123", metadata)

        # Verify API call
        mock_client._jira.put.assert_called_once()
        call_args = mock_client._jira.put.call_args

        # Verify endpoint
        assert "DEMO-123" in call_args[0][0]
        assert PROPERTY_KEY in call_args[0][0]
        assert (
            call_args[0][0] == f"/rest/api/3/issue/DEMO-123/properties/{PROPERTY_KEY}"
        )

        # Verify payload structure
        payload = call_args[1]["data"]
        assert "rai_sync" in payload
        assert payload["rai_sync"]["epic_id"] == "E-DEMO"
        assert payload["rai_sync"]["story_id"] == "S-DEMO.4"

    def test_set_entity_property_handles_api_error(self) -> None:
        """Test error handling when JIRA API call fails."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()

        # Create exception with status_code attribute
        error = Exception("Forbidden")
        error.status_code = 403  # type: ignore[attr-defined]
        mock_client._jira.put = Mock(side_effect=error)

        metadata = RaiSyncMetadata(
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        with pytest.raises(JiraApiError) as exc_info:
            set_entity_property(mock_client, "DEMO-123", metadata)

        assert exc_info.value.status_code == 403


class TestGetEntityProperty:
    """Test get_entity_property function."""

    def test_get_entity_property_success(self) -> None:
        """Test successful entity property retrieval."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()

        # Mock JIRA API response (returns dict directly, not Mock)
        mock_client._jira.get = Mock(
            return_value={
                "value": {
                    "rai_sync": {
                        "epic_id": "E-DEMO",
                        "story_id": "S-DEMO.4",
                        "last_sync_at": datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                        "sync_version": "1",
                        "rai_branch": "demo/atlassian-webinar",
                        "local_path": "/home/emilio/Code/raise-commons",
                        "sync_direction": "push",
                        "last_modified_by": "rai",
                    }
                }
            }
        )

        result = get_entity_property(mock_client, "DEMO-123")

        # Verify API call
        mock_client._jira.get.assert_called_once_with(
            f"/rest/api/3/issue/DEMO-123/properties/{PROPERTY_KEY}"
        )

        # Verify result
        assert result is not None
        assert result.epic_id == "E-DEMO"
        assert result.story_id == "S-DEMO.4"
        assert result.sync_version == "1"

    def test_get_entity_property_not_found_returns_none(self) -> None:
        """Test that 404 (property not set) returns None."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()
        mock_client._jira.get = Mock(
            side_effect=JiraApiError(status_code=404, message="Property not found")
        )

        result = get_entity_property(mock_client, "DEMO-999")

        assert result is None

    def test_get_entity_property_other_error_raises(self) -> None:
        """Test that non-404 errors are raised."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()
        mock_client._jira.get = Mock(
            side_effect=JiraApiError(status_code=500, message="Internal Server Error")
        )

        with pytest.raises(JiraApiError) as exc_info:
            get_entity_property(mock_client, "DEMO-123")

        assert exc_info.value.status_code == 500

    def test_get_entity_property_strict_validation_rejects_malformed(self) -> None:
        """Test that strict validation rejects malformed data from JIRA."""
        mock_client = Mock(spec=JiraClient)

        # Mock malformed response (missing required fields)
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "rai_sync": {
                    "epic_id": "E-DEMO",
                    # Missing: last_sync_at, rai_branch, local_path
                }
            }
        }
        mock_client._jira = Mock()
        mock_client._jira.get = Mock(return_value=mock_response)

        with pytest.raises(ValidationError):
            get_entity_property(mock_client, "DEMO-123")

    def test_get_entity_property_rejects_unknown_fields(self) -> None:
        """Test that strict mode rejects unknown fields."""
        mock_client = Mock(spec=JiraClient)

        mock_response = Mock()
        mock_response.json.return_value = {
            "value": {
                "rai_sync": {
                    "epic_id": "E-DEMO",
                    "last_sync_at": datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                    "rai_branch": "demo/atlassian-webinar",
                    "local_path": "/home/emilio/Code/raise-commons",
                },
                "unknown_field": "should_fail",  # Unknown at EntityProperty level
            }
        }
        mock_client._jira = Mock()
        mock_client._jira.get = Mock(return_value=mock_response)

        with pytest.raises(ValidationError):
            get_entity_property(mock_client, "DEMO-123")


class TestHasRaiMetadata:
    """Test has_rai_metadata helper function."""

    def test_has_rai_metadata_true_when_property_exists(self) -> None:
        """Test returns True when entity property exists."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()

        # Return dict directly (not Mock)
        mock_client._jira.get = Mock(
            return_value={
                "value": {
                    "rai_sync": {
                        "epic_id": "E-DEMO",
                        "last_sync_at": datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                        "rai_branch": "demo/atlassian-webinar",
                        "local_path": "/home/emilio/Code/raise-commons",
                    }
                }
            }
        )

        result = has_rai_metadata(mock_client, "DEMO-123")

        assert result is True

    def test_has_rai_metadata_false_when_property_not_set(self) -> None:
        """Test returns False when entity property not set (404)."""
        mock_client = Mock(spec=JiraClient)
        mock_client._jira = Mock()
        mock_client._jira.get = Mock(
            side_effect=JiraApiError(status_code=404, message="Property not found")
        )

        result = has_rai_metadata(mock_client, "DEMO-999")

        assert result is False
