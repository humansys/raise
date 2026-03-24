"""Tests for memory pattern DB query functions.

Mock AsyncSession to verify SQL construction without a real DB.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


def _mock_session() -> AsyncSession:
    """Create a mock AsyncSession with execute support."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


class TestInsertPattern:
    """insert_pattern inserts a memory pattern and returns its UUID."""

    @pytest.mark.anyio
    async def test_returns_uuid(self, org_id: uuid.UUID) -> None:
        from raise_server.db.memory_queries import insert_pattern

        session = _mock_session()
        expected_id = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_id
        session.execute.return_value = mock_result

        result = await insert_pattern(
            session, org_id, "Always validate", ["governance"], {"confidence": 0.8}
        )
        assert result == expected_id
        session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_empty_context_and_properties(self, org_id: uuid.UUID) -> None:
        from raise_server.db.memory_queries import insert_pattern

        session = _mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = uuid.uuid4()
        session.execute.return_value = mock_result

        result = await insert_pattern(session, org_id, "Simple pattern", [], {})
        assert isinstance(result, uuid.UUID)


class TestListPatterns:
    """list_patterns returns dicts ordered by created_at desc."""

    @pytest.mark.anyio
    async def test_returns_list_of_dicts(self, org_id: uuid.UUID) -> None:
        from raise_server.db.memory_queries import list_patterns

        session = _mock_session()
        mock_mappings = MagicMock()
        mock_mappings.all.return_value = [
            {
                "id": uuid.uuid4(),
                "content": "pat",
                "context": [],
                "properties": {},
                "created_at": "2026-01-01",
            },
        ]
        mock_result = MagicMock()
        mock_result.mappings.return_value = mock_mappings
        session.execute.return_value = mock_result

        result = await list_patterns(session, org_id)
        assert len(result) == 1
        assert result[0]["content"] == "pat"

    @pytest.mark.anyio
    async def test_empty_result(self, org_id: uuid.UUID) -> None:
        from raise_server.db.memory_queries import list_patterns

        session = _mock_session()
        mock_mappings = MagicMock()
        mock_mappings.all.return_value = []
        mock_result = MagicMock()
        mock_result.mappings.return_value = mock_mappings
        session.execute.return_value = mock_result

        result = await list_patterns(session, org_id)
        assert result == []
