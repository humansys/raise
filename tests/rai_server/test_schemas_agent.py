"""Tests for agent telemetry Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError


class TestAgentEventCreate:
    """AgentEventCreate validates incoming telemetry events."""

    def test_minimal_valid(self) -> None:
        from raise_server.schemas.agent import AgentEventCreate

        event = AgentEventCreate(event_type="skill_executed")
        assert event.event_type == "skill_executed"
        assert event.payload == {}

    def test_with_payload(self) -> None:
        from raise_server.schemas.agent import AgentEventCreate

        event = AgentEventCreate(
            event_type="skill_executed",
            payload={"skill": "lean-business-case", "success": True},
        )
        assert event.payload["skill"] == "lean-business-case"

    def test_empty_event_type_rejected(self) -> None:
        from raise_server.schemas.agent import AgentEventCreate

        with pytest.raises(ValidationError):
            AgentEventCreate(event_type="")

    def test_event_type_max_length(self) -> None:
        from raise_server.schemas.agent import AgentEventCreate

        with pytest.raises(ValidationError):
            AgentEventCreate(event_type="x" * 101)

    def test_payload_size_limit(self) -> None:
        from raise_server.schemas.agent import AgentEventCreate

        big_payload = {"data": "x" * 200_000}
        with pytest.raises(ValidationError):
            AgentEventCreate(event_type="test", payload=big_payload)


class TestAgentEventResponse:
    """AgentEventResponse returns id and status."""

    def test_defaults(self) -> None:
        from raise_server.schemas.agent import AgentEventResponse

        resp = AgentEventResponse(id=uuid.uuid4())
        assert resp.status == "ok"


class TestAgentEventItem:
    """AgentEventItem represents a single event in list response."""

    def test_all_fields(self) -> None:
        from raise_server.schemas.agent import AgentEventItem

        item = AgentEventItem(
            id=uuid.uuid4(),
            event_type="skill_executed",
            payload={"skill": "test"},
            created_at=datetime.now(tz=UTC),
        )
        assert item.event_type == "skill_executed"


class TestAgentEventListResponse:
    """AgentEventListResponse wraps event list with count."""

    def test_empty_list(self) -> None:
        from raise_server.schemas.agent import AgentEventListResponse

        resp = AgentEventListResponse(events=[], count=0)
        assert resp.events == []
        assert resp.count == 0
