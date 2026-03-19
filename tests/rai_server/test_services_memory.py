"""Tests for memory pattern service layer.

DB functions are mocked — service tests verify orchestration.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from raise_server.schemas.memory import MemoryPatternCreate
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


class TestAddPattern:
    @pytest.mark.anyio
    async def test_returns_pattern_id(self, org_id: uuid.UUID) -> None:
        from raise_server.services.memory import add_pattern

        expected_id = uuid.uuid4()
        factory = _mock_session_factory()

        with patch(
            "raise_server.services.memory.insert_pattern",
            new_callable=AsyncMock,
            return_value=expected_id,
        ):
            body = MemoryPatternCreate(
                content="Always validate", context=["governance"]
            )
            result = await add_pattern(factory, org_id, body)

        assert result.id == expected_id
        assert result.status == "ok"


class TestGetPatterns:
    @pytest.mark.anyio
    async def test_returns_list(self, org_id: uuid.UUID) -> None:
        from raise_server.services.memory import get_patterns

        factory = _mock_session_factory()
        mock_rows = [
            {
                "id": uuid.uuid4(),
                "content": "pat",
                "context": ["testing"],
                "properties": {},
                "created_at": datetime.now(tz=UTC),
            },
        ]

        with patch(
            "raise_server.services.memory.list_patterns",
            new_callable=AsyncMock,
            return_value=mock_rows,
        ):
            result = await get_patterns(factory, org_id)

        assert result.count == 1
        assert result.patterns[0].content == "pat"

    @pytest.mark.anyio
    async def test_empty_list(self, org_id: uuid.UUID) -> None:
        from raise_server.services.memory import get_patterns

        factory = _mock_session_factory()

        with patch(
            "raise_server.services.memory.list_patterns",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await get_patterns(factory, org_id)

        assert result.count == 0
        assert result.patterns == []
