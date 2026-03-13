"""Tests for JIRA entity property Pydantic models.

Tests RaiSyncMetadata and EntityProperty models with strict validation.
TDD: RED phase - tests written before implementation.
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from rai_pro.providers.jira.models import EntityProperty, RaiSyncMetadata


class TestRaiSyncMetadata:
    """Test RaiSyncMetadata model validation."""

    def test_valid_metadata_minimal_fields(self) -> None:
        """Test valid metadata with only required fields."""
        metadata = RaiSyncMetadata(
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        assert metadata.last_sync_at == datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC)
        assert metadata.rai_branch == "demo/atlassian-webinar"
        assert metadata.local_path == "/home/emilio/Code/raise-commons"
        assert metadata.sync_version == "1"  # Default
        assert metadata.sync_direction == "push"  # Default
        assert metadata.last_modified_by == "rai"  # Default

    def test_valid_metadata_with_epic_story_ids(self) -> None:
        """Test metadata with epic and story IDs."""
        metadata = RaiSyncMetadata(
            epic_id="E-DEMO",
            story_id="S-DEMO.4",
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        assert metadata.epic_id == "E-DEMO"
        assert metadata.story_id == "S-DEMO.4"
        assert metadata.task_id is None  # Optional

    def test_valid_metadata_with_task_fields(self) -> None:
        """Test metadata with task-specific fields."""
        metadata = RaiSyncMetadata(
            task_id="T-DEMO.4.1",
            task_status="in_progress",
            task_blocked=False,
            estimated_sp=0.5,
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        assert metadata.task_id == "T-DEMO.4.1"
        assert metadata.task_status == "in_progress"
        assert metadata.task_blocked is False
        assert metadata.estimated_sp == 0.5

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSyncMetadata(
                rai_branch="demo/atlassian-webinar",
                # Missing: last_sync_at, local_path
            )

        errors = exc_info.value.errors()
        assert len(errors) == 2
        field_names = {error["loc"][0] for error in errors}
        assert "last_sync_at" in field_names
        assert "local_path" in field_names

    def test_invalid_task_status_raises_validation_error(self) -> None:
        """Test that invalid task_status literal raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSyncMetadata(
                task_status="invalid_status",  # type: ignore[arg-type]
                last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                rai_branch="demo/atlassian-webinar",
                local_path="/home/emilio/Code/raise-commons",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("task_status",)
        # Verify error mentions valid literal values
        assert "pending" in str(errors[0]["msg"]).lower() or "in_progress" in str(
            errors[0]["msg"]
        )

    def test_invalid_sync_direction_raises_validation_error(self) -> None:
        """Test that invalid sync_direction literal raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSyncMetadata(
                sync_direction="invalid",  # type: ignore[arg-type]
                last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                rai_branch="demo/atlassian-webinar",
                local_path="/home/emilio/Code/raise-commons",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("sync_direction",)

    def test_strict_mode_rejects_unknown_fields(self) -> None:
        """Test that strict mode rejects unknown fields (extra='forbid')."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSyncMetadata(
                last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
                rai_branch="demo/atlassian-webinar",
                local_path="/home/emilio/Code/raise-commons",
                unknown_field="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "unknown_field" in str(errors[0])

    def test_serialization_to_dict(self) -> None:
        """Test model_dump() serialization."""
        metadata = RaiSyncMetadata(
            epic_id="E-DEMO",
            story_id="S-DEMO.4",
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        data = metadata.model_dump(mode="json")

        assert data["epic_id"] == "E-DEMO"
        assert data["story_id"] == "S-DEMO.4"
        assert data["last_sync_at"] == "2026-02-14T10:00:00Z"
        assert data["sync_version"] == "1"


class TestEntityProperty:
    """Test EntityProperty wrapper model."""

    def test_valid_entity_property(self) -> None:
        """Test valid EntityProperty wrapping RaiSyncMetadata."""
        metadata = RaiSyncMetadata(
            epic_id="E-DEMO",
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )

        entity_prop = EntityProperty(rai_sync=metadata)

        assert entity_prop.rai_sync.epic_id == "E-DEMO"
        assert entity_prop.rai_sync.sync_version == "1"

    def test_entity_property_serialization(self) -> None:
        """Test EntityProperty serialization matches JIRA API format."""
        metadata = RaiSyncMetadata(
            epic_id="E-DEMO",
            story_id="S-DEMO.4",
            last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
            rai_branch="demo/atlassian-webinar",
            local_path="/home/emilio/Code/raise-commons",
        )
        entity_prop = EntityProperty(rai_sync=metadata)

        data = entity_prop.model_dump(mode="json")

        # Verify nested structure
        assert "rai_sync" in data
        assert data["rai_sync"]["epic_id"] == "E-DEMO"
        assert data["rai_sync"]["story_id"] == "S-DEMO.4"
        assert data["rai_sync"]["sync_version"] == "1"

    def test_entity_property_deserialization_from_jira_response(self) -> None:
        """Test EntityProperty.model_validate() from JIRA API response."""
        jira_response: dict[str, Any] = {
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

        entity_prop = EntityProperty.model_validate(jira_response)

        assert entity_prop.rai_sync.epic_id == "E-DEMO"
        assert entity_prop.rai_sync.story_id == "S-DEMO.4"
        assert entity_prop.rai_sync.sync_version == "1"

    def test_entity_property_deserialization_from_jira_json_string(self) -> None:
        """Test EntityProperty.model_validate_json() from raw JIRA JSON response."""
        jira_json_response = """{
            "rai_sync": {
                "epic_id": "E-DEMO",
                "story_id": "S-DEMO.4",
                "last_sync_at": "2026-02-14T10:00:00Z",
                "sync_version": "1",
                "rai_branch": "demo/atlassian-webinar",
                "local_path": "/home/emilio/Code/raise-commons",
                "sync_direction": "push",
                "last_modified_by": "rai"
            }
        }"""

        entity_prop = EntityProperty.model_validate_json(jira_json_response)

        assert entity_prop.rai_sync.epic_id == "E-DEMO"
        assert entity_prop.rai_sync.story_id == "S-DEMO.4"
        assert entity_prop.rai_sync.last_sync_at == datetime(
            2026, 2, 14, 10, 0, 0, tzinfo=UTC
        )

    def test_entity_property_strict_validation_rejects_malformed_data(self) -> None:
        """Test strict validation rejects malformed JIRA response."""
        malformed_response: dict[str, Any] = {
            "rai_sync": {
                "epic_id": "E-DEMO",
                # Missing required fields: last_sync_at, rai_branch, local_path
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityProperty.model_validate(malformed_response)

        errors = exc_info.value.errors()
        assert len(errors) >= 3  # At least 3 missing required fields

    def test_entity_property_rejects_unknown_fields(self) -> None:
        """Test EntityProperty rejects unknown fields (strict mode)."""
        response_with_unknown: dict[str, Any] = {
            "rai_sync": {
                "epic_id": "E-DEMO",
                "last_sync_at": "2026-02-14T10:00:00Z",
                "rai_branch": "demo/atlassian-webinar",
                "local_path": "/home/emilio/Code/raise-commons",
            },
            "unknown_top_level": "should_fail",  # Unknown field at EntityProperty level
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityProperty.model_validate(response_with_unknown)

        errors = exc_info.value.errors()
        assert any("unknown_top_level" in str(error) for error in errors)
