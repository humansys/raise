"""Tests for agent telemetry service layer.

DB functions are mocked — service tests verify orchestration.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from raise_server.schemas.agent import AgentEventCreate
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def _mock_session_factory() -> async_sessionmaker[AsyncSession]:
    session = AsyncMock(spec=AsyncSession)
    begin_cm = AsyncMock()
    begin_cm.__aenter__ = AsyncMock(return_value=None)
    begin_cm.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = begin_cm

    @asynccontextmanager
    async def _session_cm() -> AsyncGenerator[AsyncSession, None]:
        yield session

    factory = MagicMock(spec=async_sessionmaker)
    factory.side_effect = lambda: _session_cm()
    return factory  # type: ignore[return-value]


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


class TestRecordEvent:
    @pytest.mark.anyio
    async def test_returns_event_id(self, org_id: uuid.UUID) -> None:
        from raise_server.services.agent import record_event

        expected_id = uuid.uuid4()
        factory = _mock_session_factory()

        with patch(
            "raise_server.services.agent.insert_event",
            new_callable=AsyncMock,
            return_value=expected_id,
        ):
            body = AgentEventCreate(
                event_type="skill_executed", payload={"skill": "test"}
            )
            result = await record_event(factory, org_id, body)

        assert result.id == expected_id
        assert result.status == "ok"


class TestGetEvents:
    @pytest.mark.anyio
    async def test_returns_list(self, org_id: uuid.UUID) -> None:
        from raise_server.services.agent import get_events

        factory = _mock_session_factory()
        mock_rows = [
            {
                "id": uuid.uuid4(),
                "event_type": "ping",
                "payload": {},
                "created_at": datetime.now(tz=UTC),
            },
        ]

        with patch(
            "raise_server.services.agent.list_events",
            new_callable=AsyncMock,
            return_value=mock_rows,
        ):
            result = await get_events(factory, org_id, limit=10)

        assert result.count == 1
        assert result.events[0].event_type == "ping"

    @pytest.mark.anyio
    async def test_empty_list(self, org_id: uuid.UUID) -> None:
        from raise_server.services.agent import get_events

        factory = _mock_session_factory()

        with patch(
            "raise_server.services.agent.list_events",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await get_events(factory, org_id)

        assert result.count == 0
        assert result.events == []
