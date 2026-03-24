"""Tests for memory pattern Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError


class TestMemoryPatternCreate:
    """MemoryPatternCreate validates incoming patterns."""

    def test_minimal_valid(self) -> None:
        from raise_server.schemas.memory import MemoryPatternCreate

        pattern = MemoryPatternCreate(content="Always validate inputs")
        assert pattern.content == "Always validate inputs"
        assert pattern.context == []
        assert pattern.properties == {}

    def test_with_context_and_properties(self) -> None:
        from raise_server.schemas.memory import MemoryPatternCreate

        pattern = MemoryPatternCreate(
            content="Use TDD for all features",
            context=["governance", "testing"],
            properties={"confidence": 0.9},
        )
        assert pattern.context == ["governance", "testing"]
        assert pattern.properties["confidence"] == 0.9

    def test_empty_content_rejected(self) -> None:
        from raise_server.schemas.memory import MemoryPatternCreate

        with pytest.raises(ValidationError):
            MemoryPatternCreate(content="")

    def test_content_max_length(self) -> None:
        from raise_server.schemas.memory import MemoryPatternCreate

        with pytest.raises(ValidationError):
            MemoryPatternCreate(content="x" * 10001)


class TestMemoryPatternResponse:
    """MemoryPatternResponse returns id and status."""

    def test_defaults(self) -> None:
        from raise_server.schemas.memory import MemoryPatternResponse

        resp = MemoryPatternResponse(id=uuid.uuid4())
        assert resp.status == "ok"


class TestMemoryPatternItem:
    """MemoryPatternItem represents a single pattern in list response."""

    def test_all_fields(self) -> None:
        from raise_server.schemas.memory import MemoryPatternItem

        item = MemoryPatternItem(
            id=uuid.uuid4(),
            content="Test pattern",
            context=["testing"],
            properties={"source": "rovo"},
            created_at=datetime.now(tz=UTC),
        )
        assert item.content == "Test pattern"


class TestMemoryPatternListResponse:
    """MemoryPatternListResponse wraps pattern list with count."""

    def test_empty_list(self) -> None:
        from raise_server.schemas.memory import MemoryPatternListResponse

        resp = MemoryPatternListResponse(patterns=[], count=0)
        assert resp.patterns == []
        assert resp.count == 0
