"""Pydantic models for JIRA entities.

These models define the data structures for JIRA epics, stories, and story creation.
Only essential fields are included (field filtering for API efficiency).
"""

from pydantic import BaseModel, Field


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
