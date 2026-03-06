"""Memory module for Rai's persistent memory.

This module provides infrastructure for loading, querying, and managing
Rai's accumulated memories stored in JSONL format.

For queries, use the Graph from rai_cli.context:
- CLI: `raise context query "keywords" --types pattern,calibration,session`
- Programmatic: `QueryEngine` from `rai_cli.context.query`

The JSONL files (.raise/rai/memory/*.jsonl) remain the source of truth.
The unified graph consolidates memory with governance, skills, and work items.
"""

from __future__ import annotations

from rai_cli.memory.migration import (
    MigrationResult,
    migrate_to_personal,
    needs_migration,
)
from rai_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryRelationship,
    MemoryRelationshipType,
    MemoryScope,
    PatternSubType,
)
from rai_cli.memory.writer import (
    PatternInput,
    ReinforceResult,
    SessionInput,
    WriteResult,
    append_pattern,
    append_session,
    get_memory_dir_for_scope,
    reinforce_pattern,
)

__all__ = [
    "MemoryConcept",
    "MemoryConceptType",
    "MemoryRelationship",
    "MemoryRelationshipType",
    "MemoryScope",
    "MigrationResult",
    "PatternInput",
    "PatternSubType",
    "ReinforceResult",
    "SessionInput",
    "WriteResult",
    "append_pattern",
    "append_session",
    "get_memory_dir_for_scope",
    "migrate_to_personal",
    "needs_migration",
    "reinforce_pattern",
]
