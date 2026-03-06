"""Pydantic models for memory concepts.

This module defines the core data structures for representing Rai's
memories loaded from JSONL files.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MemoryScope(StrEnum):
    """Scope/tier for memory data.

    Determines where memory data is stored and its visibility:
    - GLOBAL: ~/.rai/ - Cross-repo, universal patterns
    - PROJECT: .raise/rai/memory/ - Shared, committed to repo
    - PERSONAL: .raise/rai/personal/ - Developer-specific, gitignored

    Precedence for same-ID concepts: PERSONAL > PROJECT > GLOBAL
    """

    GLOBAL = "global"
    PROJECT = "project"
    PERSONAL = "personal"

    def __str__(self) -> str:
        """Return value for string interpolation."""
        return self.value


class MemoryConceptType(StrEnum):
    """Types of memory concepts.

    Attributes:
        PATTERN: Learned patterns (from patterns.jsonl).
        CALIBRATION: Velocity/estimation data (from calibration.jsonl).
        SESSION: Session records (from sessions/index.jsonl).
    """

    PATTERN = "pattern"
    CALIBRATION = "calibration"
    SESSION = "session"


class PatternSubType(StrEnum):
    """Sub-types for pattern concepts.

    Attributes:
        CODEBASE: Code-level patterns.
        PROCESS: Process/workflow patterns.
        ARCHITECTURE: Architectural patterns.
        TECHNICAL: Technical discoveries.
    """

    CODEBASE = "codebase"
    PROCESS = "process"
    ARCHITECTURE = "architecture"
    TECHNICAL = "technical"


class MemoryRelationshipType(StrEnum):
    """Types of relationships between memory concepts.

    Attributes:
        LEARNED_FROM: Pattern/calibration was learned from a session.
        RELATED_TO: Concepts share context keywords.
        VALIDATES: Calibration data validates a pattern.
        APPLIES_TO: Pattern applies to a context domain.
    """

    LEARNED_FROM = "learned_from"
    RELATED_TO = "related_to"
    VALIDATES = "validates"
    APPLIES_TO = "applies_to"


class MemoryConcept(BaseModel):
    """A memory concept extracted from JSONL files.

    Represents a single unit of Rai's memory (pattern, calibration record,
    or session record) with its metadata.

    Attributes:
        id: Unique identifier (e.g., 'PAT-001', 'CAL-001', 'SES-001').
        type: Type of memory concept.
        content: Main content or summary.
        context: Context keywords for retrieval.
        created: Date when memory was created.
        metadata: Type-specific metadata.

    Examples:
        >>> concept = MemoryConcept(
        ...     id="PAT-001",
        ...     type=MemoryConceptType.PATTERN,
        ...     content="Singleton with get/set/configure",
        ...     context=["testing", "module-design"],
        ...     created=date(2026, 1, 31),
        ...     metadata={"sub_type": "codebase", "learned_from": "F1.4"}
        ... )
        >>> concept.id
        'PAT-001'
    """

    id: str = Field(..., description="Unique identifier (e.g., 'PAT-001')")
    type: MemoryConceptType = Field(..., description="Memory concept type")
    content: str = Field(..., description="Main content or summary")
    context: list[str] = Field(default_factory=list, description="Context keywords")
    created: date = Field(..., description="Date when memory was created")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific metadata"
    )

    @property
    def token_estimate(self) -> int:
        """Estimate tokens for this concept.

        Returns:
            Estimated token count (content length // 4).
        """
        return len(self.content) // 4


class MemoryRelationship(BaseModel):
    """A relationship between two memory concepts.

    Attributes:
        source: Source concept ID.
        target: Target concept ID.
        type: Relationship type.
        metadata: Additional relationship metadata.

    Examples:
        >>> rel = MemoryRelationship(
        ...     source="PAT-001",
        ...     target="SES-001",
        ...     type=MemoryRelationshipType.LEARNED_FROM,
        ...     metadata={"confidence": 1.0}
        ... )
        >>> rel.type
        <MemoryRelationshipType.LEARNED_FROM: 'learned_from'>
    """

    source: str = Field(..., description="Source concept ID")
    target: str = Field(..., description="Target concept ID")
    type: MemoryRelationshipType = Field(..., description="Relationship type")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class MemoryLoadResult(BaseModel):
    """Result of loading memory from JSONL files.

    Attributes:
        concepts: List of loaded memory concepts.
        total: Total number of concepts loaded.
        files_processed: Number of files successfully processed.
        errors: List of error messages.
    """

    concepts: list[MemoryConcept] = Field(default_factory=lambda: list[MemoryConcept]())
    total: int = Field(default=0, description="Total concepts loaded")
    files_processed: int = Field(default=0, description="Files processed")
    errors: list[str] = Field(default_factory=lambda: list[str]())
