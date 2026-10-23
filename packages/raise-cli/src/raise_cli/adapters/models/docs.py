"""Documentation Target boundary models.

Typed inputs and outputs for the ``DocumentationTarget`` protocol.

Architecture: ADR-033 (Docs adapter), ADR-014 (Atlassian transport)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PublishResult(BaseModel):
    """Result of publishing documentation."""

    success: bool = Field(..., description="Whether publish succeeded")
    url: str = Field(default="", description="URL of published content")
    message: str = Field(default="", description="Status or error message")
    remote_id: str = Field(
        default="", description="Remote page ID (set by remote adapters)"
    )
    sync_pending: bool = Field(
        default=False,
        description=(
            "True when the local write succeeded but the remote (Confluence) "
            "publish failed and was queued for replay — success is True but the "
            "URL is local, not remote (RAISE-10714)."
        ),
    )


class PageContent(BaseModel):
    """Full page content from documentation target."""

    id: str = Field(..., description="Page ID")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Page content (markdown)")
    url: str = Field(default="", description="Web URL to the page")
    space_key: str = Field(default="", description="Space key (e.g., 'DEV')")
    version: int = Field(default=1, description="Page version number")
    parent_id: str | None = Field(default=None, description="Immediate parent page ID")
    parent_title: str | None = Field(
        default=None, description="Immediate parent page title"
    )


class PageSummary(BaseModel):
    """Compact page for search results. Timestamps use ISO 8601 format."""

    id: str = Field(..., description="Page ID")
    title: str = Field(..., description="Page title")
    url: str = Field(default="", description="Web URL to the page")
    space_key: str = Field(default="", description="Space key")
    updated: str = Field(default="", description="ISO 8601 last update timestamp")


class SpaceInfo(BaseModel):
    """Confluence space metadata from discovery."""

    key: str = Field(..., description="Space key (e.g., 'raidoc')")
    name: str = Field(..., description="Space display name")
    url: str = Field(default="", description="Web URL to the space")
    type: str = Field(default="global", description="Space type (global, personal)")


class CommentSummary(BaseModel):
    """Comment on a documentation page."""

    id: str = Field(..., description="Comment ID")
    body: str = Field(..., description="Comment body (storage format)")


class AttachmentSummary(BaseModel):
    """Attachment on a documentation page."""

    id: str = Field(..., description="Attachment ID")
    filename: str = Field(..., description="Attachment filename")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="Download URL")
    media_type: str = Field(default="", description="MIME type")
