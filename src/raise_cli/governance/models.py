"""Pydantic models for governance concept extraction.

This module defines the core data structures for representing semantic
concepts extracted from governance markdown files.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, Field, model_validator


class ConceptType(StrEnum):
    """Types of concepts extracted from governance documents.

    Attributes:
        REQUIREMENT: Functional requirements from PRD (RF-XX format).
        OUTCOME: Desired outcomes from Vision document.
        PRINCIPLE: Core principles from Constitution (§N format).
        PATTERN: Design patterns from technical design (future).
        PRACTICE: Process practices from katas (future).
        PROJECT: Project from backlog (governance/backlog.md).
        EPIC: Epic from backlog or epic scope documents.
        STORY: Story from epic scope documents.
        DECISION: Architecture decision records (ADR-XXX format).
        GUARDRAIL: Code standards and quality rules.
        TERM: Glossary definitions for canonical terminology.
    """

    REQUIREMENT = "requirement"
    OUTCOME = "outcome"
    PRINCIPLE = "principle"
    PATTERN = "pattern"
    PRACTICE = "practice"
    # Work tracking types (E8)
    PROJECT = "project"
    EPIC = "epic"
    STORY = "story"
    # Knowledge graph completion types (E12)
    DECISION = "decision"
    GUARDRAIL = "guardrail"
    TERM = "term"
    # Release ontology
    RELEASE = "release"


class Concept(BaseModel):
    """A semantic concept extracted from governance markdown.

    Represents a single extractable unit of governance information
    (e.g., a requirement, outcome, or principle) with its location
    and metadata.

    Attributes:
        id: Unique identifier (e.g., 'req-rf-05', 'outcome-context-generation').
        type: Type of concept (requirement, outcome, principle, etc.).
        file: Source file relative path from project root.
        section: Section heading where concept was found.
        lines: Tuple of (start_line, end_line) in source file.
        content: Extracted content, truncated if >500 chars.
        metadata: Type-specific metadata (e.g., requirement_id, title).

    Examples:
        >>> concept = Concept(
        ...     id="req-rf-05",
        ...     type=ConceptType.REQUIREMENT,
        ...     file="governance/prd.md",
        ...     section="RF-05: Golden Context Generation",
        ...     lines=(206, 214),
        ...     content="The system MUST generate CLAUDE.md...",
        ...     metadata={"requirement_id": "RF-05", "title": "Golden Context Generation"}
        ... )
        >>> concept.id
        'req-rf-05'
        >>> concept.type
        <ConceptType.REQUIREMENT: 'requirement'>
    """

    id: str = Field(..., description="Unique identifier (e.g., 'req-rf-05')")
    type: ConceptType = Field(..., description="Concept type")
    file: str = Field(..., description="Source file relative path")
    section: str = Field(..., description="Section heading")
    lines: tuple[int, int] = Field(..., description="Line range (start, end)")
    content: str = Field(..., description="Extracted content (truncated if long)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific metadata"
    )

    @model_validator(mode="after")
    def validate_line_range(self) -> Self:
        """Validate that line range is valid (start <= end).

        Returns:
            Self if valid.

        Raises:
            ValueError: If line range is invalid (start > end).
        """
        if self.lines[0] > self.lines[1]:
            raise ValueError(
                f"Invalid line range: start ({self.lines[0]}) > end ({self.lines[1]})"
            )
        return self


class ExtractionResult(BaseModel):
    """Result of a concept extraction operation.

    Contains the extracted concepts along with metadata about the
    extraction process (files processed, errors encountered).

    Attributes:
        concepts: List of extracted concepts.
        total: Total number of concepts extracted.
        files_processed: Number of files successfully parsed.
        errors: List of error messages from failed extractions.

    Examples:
        >>> result = ExtractionResult(
        ...     concepts=[concept1, concept2],
        ...     total=2,
        ...     files_processed=1,
        ...     errors=[]
        ... )
        >>> result.total
        2
    """

    concepts: list[Concept] = Field(default_factory=lambda: list[Concept]())
    total: int = Field(..., description="Total concepts extracted")
    files_processed: int = Field(..., description="Number of files parsed")
    errors: list[str] = Field(default_factory=list)
