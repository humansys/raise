"""Sync engine for bidirectional JIRA synchronization.

Orchestrates pull (JIRA → local state) and push (local → JIRA) operations.
State is tracked in .raise/rai/sync/state.json, separate from knowledge graph.

Functions:
    pull_epic: Pull epic and stories from JIRA to local sync state
    push_stories: Push local stories to JIRA under mapped epic
    check_authorization: Check if story is authorized (offline, reads state only)
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from rai_providers.jira.client import JiraClient
from rai_providers.jira.models import RaiSyncMetadata, StoryCreate
from rai_providers.jira.properties import set_entity_property
from rai_providers.jira.sync_state import SyncMapping, SyncState

# Default JIRA statuses that indicate authorization to work
DEFAULT_AUTHORIZED_STATUSES: list[str] = ["Approved", "Ready", "In Progress"]


class LocalStory(BaseModel):
    """Local story data for push to JIRA."""

    story_id: str = Field(description="RaiSE story ID (e.g., S-DEMO.1)")
    title: str = Field(description="Story title")
    description: str = Field(default="", description="Story description")
    labels: list[str] = Field(default_factory=list, description="Story labels")


class PullResult(BaseModel):
    """Result of a pull operation."""

    epic_key: str = Field(description="JIRA epic key pulled")
    epic_id: str = Field(description="Local epic ID")
    epic_imported: bool = Field(description="True if epic was newly imported")
    epic_summary: str = Field(default="", description="Epic title from JIRA")
    epic_status: str = Field(default="", description="Epic status from JIRA")
    stories_imported: int = Field(default=0, description="New stories imported")
    stories_updated: int = Field(default=0, description="Existing stories updated")
    story_details: list[dict[str, str]] = Field(
        default_factory=lambda: list[dict[str, str]](),
        description="Story sync details",
    )
    dry_run: bool = Field(default=False, description="Was this a dry run?")


class PushResult(BaseModel):
    """Result of a push operation."""

    epic_id: str = Field(description="Local epic ID")
    jira_epic_key: str = Field(description="JIRA epic key")
    created: int = Field(default=0, description="Stories created in JIRA")
    skipped: int = Field(default=0, description="Stories skipped (already synced)")
    created_details: list[dict[str, str]] = Field(
        default_factory=lambda: list[dict[str, str]](),
        description="Created story details",
    )
    skipped_details: list[str] = Field(
        default_factory=list, description="Skipped story IDs"
    )
    dry_run: bool = Field(default=False, description="Was this a dry run?")


class AuthResult(BaseModel):
    """Result of an authorization check."""

    story_id: str = Field(description="Story ID checked")
    authorized: bool = Field(description="Whether story is authorized")
    jira_key: str | None = Field(None, description="JIRA key if mapped")
    jira_status: str | None = Field(None, description="Current JIRA status")
    message: str = Field(default="", description="Human-readable message")


def pull_epic(
    client: JiraClient,
    epic_key: str,
    epic_id: str,
    state: SyncState,
    dry_run: bool = False,
    branch: str = "",
    local_path: str = "",
) -> PullResult:
    """Pull epic and stories from JIRA, update sync state.

    Args:
        client: Authenticated JIRA client
        epic_key: JIRA epic key (e.g., "DEMO-1")
        epic_id: Local epic ID to assign (e.g., "E-DEMO")
        state: Sync state (mutated in place unless dry_run)
        dry_run: If True, preview without modifying state
        branch: Git branch name (for entity properties)
        local_path: Local project path (for entity properties)

    Returns:
        PullResult with import summary
    """
    now = datetime.now(UTC)

    # Read epic from JIRA
    jira_epic = client.read_epic(epic_key)

    # Check if epic already mapped
    is_new = epic_id not in state.epics

    if dry_run:
        # Read stories for preview
        jira_stories = client.read_stories_for_epic(epic_key)
        story_details = [
            {"jira_key": s.key, "summary": s.summary, "status": s.status}
            for s in jira_stories
        ]
        return PullResult(
            epic_key=epic_key,
            epic_id=epic_id,
            epic_imported=is_new,
            epic_summary=jira_epic.summary,
            epic_status=jira_epic.status,
            stories_imported=len(jira_stories) if is_new else 0,
            stories_updated=len(jira_stories) if not is_new else 0,
            story_details=story_details,
            dry_run=True,
        )

    # Update or create epic mapping
    state.epics[epic_id] = SyncMapping(
        local_id=epic_id,
        jira_key=epic_key,
        jira_status=jira_epic.status,
        last_sync_at=now,
        sync_direction="pull",
    )

    # Set entity property on JIRA epic
    _set_sync_metadata(
        client=client,
        issue_key=epic_key,
        epic_id=epic_id,
        direction="pull",
        branch=branch,
        local_path=local_path,
    )

    # Read and map stories
    jira_stories = client.read_stories_for_epic(epic_key)
    stories_imported = 0
    stories_updated = 0
    story_details: list[dict[str, str]] = []

    # Build reverse lookup: jira_key → local_id
    jira_to_local: dict[str, str] = {
        m.jira_key: m.local_id for m in state.stories.values()
    }

    for idx, jira_story in enumerate(jira_stories, 1):
        existing_local_id = jira_to_local.get(jira_story.key)

        if existing_local_id:
            # Update existing story status
            state.stories[existing_local_id].jira_status = jira_story.status
            state.stories[existing_local_id].last_sync_at = now
            stories_updated += 1
            story_details.append(
                {
                    "local_id": existing_local_id,
                    "jira_key": jira_story.key,
                    "summary": jira_story.summary,
                    "status": jira_story.status,
                    "action": "updated",
                }
            )
        else:
            # Create new story mapping
            story_local_id = f"S-{epic_id.removeprefix('E-')}.{idx}"
            state.stories[story_local_id] = SyncMapping(
                local_id=story_local_id,
                jira_key=jira_story.key,
                jira_status=jira_story.status,
                last_sync_at=now,
                sync_direction="pull",
            )
            stories_imported += 1
            story_details.append(
                {
                    "local_id": story_local_id,
                    "jira_key": jira_story.key,
                    "summary": jira_story.summary,
                    "status": jira_story.status,
                    "action": "imported",
                }
            )

    state.last_sync_at = now

    return PullResult(
        epic_key=epic_key,
        epic_id=epic_id,
        epic_imported=is_new,
        epic_summary=jira_epic.summary,
        epic_status=jira_epic.status,
        stories_imported=stories_imported,
        stories_updated=stories_updated,
        story_details=story_details,
    )


def push_stories(
    client: JiraClient,
    epic_id: str,
    stories: list[LocalStory],
    state: SyncState,
    dry_run: bool = False,
    branch: str = "",
    local_path: str = "",
) -> PushResult:
    """Push local stories to JIRA under mapped epic.

    Args:
        client: Authenticated JIRA client
        epic_id: Local epic ID (e.g., "E-DEMO")
        stories: Local stories to push
        state: Sync state (mutated in place unless dry_run)
        dry_run: If True, preview without creating JIRA issues
        branch: Git branch name (for entity properties)
        local_path: Local project path (for entity properties)

    Returns:
        PushResult with creation summary

    Raises:
        ValueError: If epic_id is not mapped in state
    """
    now = datetime.now(UTC)

    # Verify epic is mapped
    if epic_id not in state.epics:
        msg = f"Epic {epic_id} not mapped in sync state. Run pull first."
        raise ValueError(msg)

    jira_epic_key = state.epics[epic_id].jira_key

    if dry_run:
        # Preview: count what would be created vs skipped
        would_create = [s for s in stories if s.story_id not in state.stories]
        would_skip = [s for s in stories if s.story_id in state.stories]
        return PushResult(
            epic_id=epic_id,
            jira_epic_key=jira_epic_key,
            created=0,
            skipped=len(would_skip),
            created_details=[
                {"story_id": s.story_id, "title": s.title} for s in would_create
            ],
            skipped_details=[s.story_id for s in would_skip],
            dry_run=True,
        )

    created = 0
    skipped = 0
    created_details: list[dict[str, str]] = []
    skipped_details: list[str] = []

    for story in stories:
        # Idempotency: skip if already in state
        if story.story_id in state.stories:
            skipped += 1
            skipped_details.append(story.story_id)
            continue

        # Create JIRA story
        story_create = StoryCreate(
            summary=story.title,
            description=story.description or None,
            labels=story.labels,
        )
        jira_story = client.create_story(
            epic_key=jira_epic_key, story=story_create
        )

        # Set entity property
        _set_sync_metadata(
            client=client,
            issue_key=jira_story.key,
            epic_id=epic_id,
            story_id=story.story_id,
            direction="push",
            branch=branch,
            local_path=local_path,
        )

        # Update state
        state.stories[story.story_id] = SyncMapping(
            local_id=story.story_id,
            jira_key=jira_story.key,
            jira_status=jira_story.status,
            last_sync_at=now,
            sync_direction="push",
        )

        created += 1
        created_details.append(
            {
                "story_id": story.story_id,
                "jira_key": jira_story.key,
                "title": story.title,
            }
        )

    state.last_sync_at = now

    return PushResult(
        epic_id=epic_id,
        jira_epic_key=jira_epic_key,
        created=created,
        skipped=skipped,
        created_details=created_details,
        skipped_details=skipped_details,
    )


def check_authorization(
    state: SyncState,
    story_id: str,
    authorized_statuses: list[str] | None = None,
) -> AuthResult:
    """Check if story is authorized to work on (offline, reads state only).

    Args:
        state: Current sync state
        story_id: Local story ID (e.g., "S-DEMO.1")
        authorized_statuses: JIRA statuses that mean "authorized"
                            Default: ["Approved", "Ready", "In Progress"]

    Returns:
        AuthResult with authorization status and message
    """
    if authorized_statuses is None:
        authorized_statuses = DEFAULT_AUTHORIZED_STATUSES

    # Story not in state = no JIRA mapping = no gate
    if story_id not in state.stories:
        return AuthResult(
            story_id=story_id,
            authorized=True,
            jira_key=None,
            jira_status=None,
            message=f"Story {story_id} has no JIRA mapping — no authorization gate.",
        )

    mapping = state.stories[story_id]
    is_authorized = mapping.jira_status in authorized_statuses

    if is_authorized:
        message = (
            f"Story {story_id} authorized "
            f"(JIRA: {mapping.jira_key}, status: {mapping.jira_status})"
        )
    else:
        message = (
            f"Story {story_id} NOT authorized in JIRA "
            f"(status: {mapping.jira_status})\n"
            f"  JIRA key: {mapping.jira_key}\n"
            f"  Required: one of {authorized_statuses}\n"
            f"  Run: rai backlog pull --source jira to refresh status."
        )

    return AuthResult(
        story_id=story_id,
        authorized=is_authorized,
        jira_key=mapping.jira_key,
        jira_status=mapping.jira_status,
        message=message,
    )


def _set_sync_metadata(
    client: JiraClient,
    issue_key: str,
    epic_id: str,
    direction: Literal["pull", "push"],
    story_id: str | None = None,
    branch: str = "",
    local_path: str = "",
) -> None:
    """Set entity property on JIRA issue with sync metadata.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key
        epic_id: Local epic ID
        direction: Sync direction
        story_id: Local story ID (optional, for stories)
        branch: Git branch name
        local_path: Local project path
    """
    metadata = RaiSyncMetadata(
        epic_id=epic_id,
        story_id=story_id,
        task_id=None,
        last_sync_at=datetime.now(UTC),
        sync_version="1",
        rai_branch=branch or "unknown",
        local_path=local_path or "unknown",
        task_status=None,
        task_blocked=None,
        estimated_sp=None,
        sync_direction=direction,
        last_modified_by="rai",
    )
    set_entity_property(client, issue_key, metadata)
