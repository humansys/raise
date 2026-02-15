"""Sync state management for JIRA bidirectional sync.

Manages persistent sync state between RaiSE local IDs and JIRA keys.
State lives in .raise/rai/sync/state.json, separate from the knowledge graph.

Functions:
    load_state: Load sync state from file (returns None if missing)
    save_state: Save sync state to file (creates directory if needed)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SyncMapping(BaseModel):
    """Mapping between a local RaiSE ID and a JIRA issue key.

    Tracks the sync relationship for a single epic or story.

    Attributes:
        local_id: RaiSE internal ID (e.g., "E-DEMO", "S-DEMO.1")
        jira_key: JIRA issue key (e.g., "DEMO-1", "DEMO-2")
        jira_status: Current JIRA status (e.g., "In Progress", "Approved")
        last_sync_at: When this mapping was last synced
        sync_direction: Whether this was pulled or pushed
    """

    local_id: str = Field(description="RaiSE internal ID")
    jira_key: str = Field(description="JIRA issue key")
    jira_status: str = Field(description="Current JIRA status")
    last_sync_at: datetime = Field(description="Last sync timestamp (UTC)")
    sync_direction: Literal["pull", "push"] = Field(description="Sync direction")


class SyncState(BaseModel):
    """Persistent sync state between RaiSE and JIRA.

    Stored in .raise/rai/sync/state.json. Separate from knowledge graph.

    Attributes:
        provider: Provider name (always "jira" for now)
        cloud_id: Atlassian cloud ID
        project_key: JIRA project key (e.g., "DEMO")
        epics: Epic mappings (local_id → SyncMapping)
        stories: Story mappings (local_id → SyncMapping)
        last_sync_at: Global last sync timestamp
    """

    provider: str = Field(default="jira", description="Provider name")
    cloud_id: str = Field(description="Atlassian cloud ID")
    project_key: str = Field(description="JIRA project key")
    epics: dict[str, SyncMapping] = Field(
        default_factory=dict, description="Epic mappings"
    )
    stories: dict[str, SyncMapping] = Field(
        default_factory=dict, description="Story mappings"
    )
    last_sync_at: datetime | None = Field(
        None, description="Global last sync timestamp"
    )

    model_config = ConfigDict(extra="forbid")


def load_state(sync_dir: Path) -> SyncState | None:
    """Load sync state from file.

    Args:
        sync_dir: Path to sync directory (e.g., .raise/rai/sync/)

    Returns:
        SyncState if state.json exists and is valid, None otherwise
    """
    state_file = sync_dir / "state.json"
    if not state_file.exists():
        return None

    data = json.loads(state_file.read_text(encoding="utf-8"))
    return SyncState.model_validate(data)


def save_state(state: SyncState, sync_dir: Path) -> None:
    """Save sync state to file.

    Creates sync directory if it doesn't exist.

    Args:
        state: Sync state to save
        sync_dir: Path to sync directory (e.g., .raise/rai/sync/)
    """
    sync_dir.mkdir(parents=True, exist_ok=True)
    state_file = sync_dir / "state.json"
    state_file.write_text(
        state.model_dump_json(indent=2),
        encoding="utf-8",
    )
