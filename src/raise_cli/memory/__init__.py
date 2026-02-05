"""Memory module for Rai's persistent memory.

This module provides infrastructure for loading, querying, and managing
Rai's accumulated memories stored in JSONL format.

.. deprecated::
    The following classes are deprecated and will be removed in a future release:
    - MemoryGraph, MemoryGraphBuilder, MemoryCache, MemoryQuery

    Use UnifiedGraph from raise_cli.context instead:
    - For queries: `raise context query "keywords" --unified --types pattern,calibration,session`
    - For programmatic access: `UnifiedQueryEngine` from `raise_cli.context.query`

    The JSONL files (.rai/memory/*.jsonl) remain the source of truth.
    The unified graph consolidates memory with governance, skills, and work items.
"""

from __future__ import annotations

from raise_cli.memory.builder import MemoryGraph, MemoryGraphBuilder, traverse_bfs
from raise_cli.memory.cache import MemoryCache
from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryRelationship,
    MemoryRelationshipType,
    PatternSubType,
)
from raise_cli.memory.query import MemoryQuery, MemoryQueryResult
from raise_cli.memory.writer import (
    CalibrationInput,
    PatternInput,
    SessionInput,
    WriteResult,
    append_calibration,
    append_pattern,
    append_session,
)

__all__ = [
    "CalibrationInput",
    "MemoryCache",
    "MemoryConcept",
    "MemoryConceptType",
    "MemoryGraph",
    "MemoryGraphBuilder",
    "MemoryQuery",
    "MemoryQueryResult",
    "MemoryRelationship",
    "MemoryRelationshipType",
    "PatternInput",
    "PatternSubType",
    "SessionInput",
    "WriteResult",
    "append_calibration",
    "append_pattern",
    "append_session",
    "traverse_bfs",
]
