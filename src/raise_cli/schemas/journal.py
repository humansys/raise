"""Journal entry schema for incremental session memory.

Journal entries are append-only records of decisions, insights, and
task completions that persist across context compaction events.
Stored in .raise/rai/personal/sessions/{session_id}/journal.jsonl.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class JournalEntryType(StrEnum):
    """Types of journal entries.

    Attributes:
        DECISION: A design or implementation decision with rationale.
        INSIGHT: An observation or learning worth preserving.
        TASK_DONE: A completed task (can be auto-generated).
        NOTE: Free-form note for context preservation.
    """

    DECISION = "decision"
    INSIGHT = "insight"
    TASK_DONE = "task_done"
    NOTE = "note"


class JournalEntry(BaseModel):
    """A single journal entry for incremental session memory.

    Attributes:
        id: Auto-generated entry ID (e.g., 'JRN-001').
        timestamp: When the entry was created.
        entry_type: Category of entry.
        content: The actual content to preserve.
        tags: Optional context tags for filtering.
    """

    id: str = Field(..., description="Entry ID (e.g., 'JRN-001')")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When entry was created"
    )
    entry_type: JournalEntryType = Field(..., description="Category of entry")
    content: str = Field(..., description="Content to preserve")
    tags: list[str] = Field(default_factory=list, description="Context tags")
