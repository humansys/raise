"""Pydantic models for memory pattern endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryPatternCreate(BaseModel):
    """Incoming learned pattern from a Rovo agent or CLI."""

    content: str = Field(min_length=1)
    context: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class MemoryPatternResponse(BaseModel):
    """Response after adding a pattern."""

    id: uuid.UUID
    status: str = "ok"


class MemoryPatternItem(BaseModel):
    """Single pattern in a list response."""

    id: uuid.UUID
    content: str
    context: list[str]
    properties: dict[str, Any]
    created_at: datetime


class MemoryPatternListResponse(BaseModel):
    """List of memory patterns."""

    patterns: list[MemoryPatternItem]
    total: int
