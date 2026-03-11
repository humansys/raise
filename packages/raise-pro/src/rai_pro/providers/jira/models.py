"""Pydantic models for JIRA entities.

These models define the data structures for JIRA epics, stories, and story creation.
Only essential fields are included (field filtering for API efficiency).

Entity property models (RaiSyncMetadata, EntityProperty) implement ADR-028 schema
for JIRA entity properties used in bidirectional sync.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class JiraEpic(BaseModel):
    """JIRA Epic with filtered fields only.

    Attributes:
        key: Epic key (e.g., DEMO-123)
        summary: Epic title
        description: Epic description (optional)
        status: Status name (e.g., 'In Progress', 'Done')
        labels: Epic labels for categorization
    """

    key: str = Field(..., description="Epic key (e.g., DEMO-123)")
    summary: str = Field(..., description="Epic title")
    description: str | None = Field(None, description="Epic description")
    status: str = Field(..., description="Status name (e.g., 'In Progress')")
    labels: list[str] = Field(default_factory=list, description="Epic labels")


class JiraStory(BaseModel):
    """JIRA Story/Issue with filtered fields only.

    Attributes:
        key: Story key (e.g., DEMO-124)
        summary: Story title
        description: Story description (optional)
        status: Status name (e.g., 'To Do', 'In Progress', 'Done')
        labels: Story labels for categorization
        epic_key: Parent epic key (optional, None if not linked to epic)
    """

    key: str = Field(..., description="Story key (e.g., DEMO-124)")
    summary: str = Field(..., description="Story title")
    description: str | None = Field(None, description="Story description")
    status: str = Field(..., description="Status name (e.g., 'To Do')")
    labels: list[str] = Field(default_factory=list, description="Story labels")
    epic_key: str | None = Field(None, description="Parent epic key")


class StoryCreate(BaseModel):
    """Data required to create a JIRA story.

    Attributes:
        summary: Story title (1-255 characters)
        description: Story description (optional)
        labels: Story labels for categorization
    """

    summary: str = Field(..., min_length=1, max_length=255, description="Story title")
    description: str | None = Field(None, description="Story description")
    labels: list[str] = Field(default_factory=list, description="Story labels")


class RaiSyncMetadata(BaseModel):
    """RaiSE sync metadata for JIRA entity properties (ADR-028).

    This model defines the sync state stored on JIRA issues via entity properties.
    Used for tracking what's been synced, when, and by whom.

    Attributes:
        epic_id: RaiSE epic ID (e.g., E-DEMO) - stable cross-project identifier
        story_id: RaiSE story ID (e.g., S-DEMO.4)
        task_id: RaiSE task ID (e.g., T-DEMO.4.1) - for subtasks only
        last_sync_at: Last sync timestamp (ISO 8601 UTC)
        sync_version: Schema version for evolution (default: "1")
        rai_branch: Git branch (e.g., demo/atlassian-webinar)
        local_path: Local project path (e.g., /path/to/project)
        task_status: Task workflow state (for subtasks)
        task_blocked: Is task blocked? (for subtasks)
        estimated_sp: Story points estimate (for subtasks)
        sync_direction: Sync direction (push/pull/bidirectional)
        last_modified_by: Who last modified (rai or jira) - for conflict detection
    """

    # Internal IDs (stable cross-project)
    epic_id: str | None = Field(None, description="RaiSE epic ID (e.g., E-DEMO)")
    story_id: str | None = Field(None, description="RaiSE story ID (e.g., S-DEMO.4)")
    task_id: str | None = Field(None, description="RaiSE task ID (e.g., T-DEMO.4.1)")

    # Sync tracking (required)
    last_sync_at: datetime = Field(description="Last sync timestamp (ISO 8601 UTC)")
    sync_version: str = Field(default="1", description="Schema version for evolution")
    rai_branch: str = Field(description="Git branch (e.g., demo/atlassian-webinar)")
    local_path: str = Field(description="Local project path")

    # Task-specific metadata (optional, for subtasks)
    task_status: Literal["pending", "in_progress", "done"] | None = Field(
        None, description="Task workflow state"
    )
    task_blocked: bool | None = Field(None, description="Is task blocked?")
    estimated_sp: float | None = Field(None, description="Story points estimate")

    # Forge-ready fields (V3)
    sync_direction: Literal["push", "pull", "bidirectional"] = Field(
        default="push", description="Sync direction"
    )
    last_modified_by: Literal["rai", "jira"] = Field(
        default="rai", description="Who last modified (conflict detection)"
    )

    model_config = ConfigDict(
        strict=True,  # Fail fast on invalid data (design decision)
        extra="forbid",  # Reject unknown fields (strict validation)
    )


class EntityProperty(BaseModel):
    """JIRA entity property wrapper for RaiSE sync metadata (ADR-028).

    Wraps RaiSyncMetadata in the structure expected by JIRA entity properties API.
    Property key: com.humansys.raise.sync

    Attributes:
        rai_sync: RaiSE sync metadata
    """

    rai_sync: RaiSyncMetadata = Field(description="RaiSE sync metadata")

    model_config = ConfigDict(
        strict=True,  # Fail fast on invalid data (design decision)
        extra="forbid",  # Reject unknown fields (strict validation)
    )
