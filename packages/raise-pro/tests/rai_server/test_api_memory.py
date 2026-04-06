"""Tests for memory pattern API routes."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from raise_server.app import create_app
from raise_server.config import ServerConfig
from raise_server.schemas.memory import MemoryPatternListResponse, MemoryPatternResponse

_DB_URL = "postgresql+asyncpg://u:p@h/db"
_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_ORG_NAME = "acme"


@contextmanager
def _override_auth(client: TestClient) -> Generator[None, None, None]:
    from raise_server.auth import MemberContext, verify_member

    async def _fake_auth() -> MemberContext:
        return MemberContext(
            org_id=_ORG_ID,
            org_name=_ORG_NAME,
            member_id=_ORG_ID,
            email="test@example.com",
            role="admin",
            plan="team",
            features=[],
        )

    client.app.dependency_overrides[verify_member] = _fake_auth  # type: ignore[union-attr]
    try:
        yield
    finally:
        client.app.dependency_overrides.clear()  # type: ignore[union-attr]


@pytest.fixture
def client() -> TestClient:
    config = ServerConfig(database_url=_DB_URL)
    app = create_app(config=config)
    app.state.session_factory = MagicMock()
    return TestClient(app)


class TestCreatePatternEndpoint:
    def test_returns_200_with_id(self, client: TestClient) -> None:
        mock_response = MemoryPatternResponse(id=uuid.uuid4())
        with (
            _override_auth(client),
            patch(
                "raise_server.api.v1.memory.add_pattern",
                new_callable=AsyncMock,
                return_value=mock_response,
            ),
        ):
            resp = client.post(
                "/api/v1/memory/patterns",
                json={"content": "Always validate inputs", "context": ["governance"]},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "id" in data

    def test_rejects_empty_content(self, client: TestClient) -> None:
        with _override_auth(client):
            resp = client.post("/api/v1/memory/patterns", json={"content": ""})
        assert resp.status_code == 422

    def test_requires_auth(self, client: TestClient) -> None:
        resp = client.post("/api/v1/memory/patterns", json={"content": "test"})
        assert resp.status_code == 401


class TestListPatternsEndpoint:
    def test_returns_200_with_patterns(self, client: TestClient) -> None:
        mock_response = MemoryPatternListResponse(patterns=[], count=0)
        with (
            _override_auth(client),
            patch(
                "raise_server.api.v1.memory.get_patterns",
                new_callable=AsyncMock,
                return_value=mock_response,
            ),
        ):
            resp = client.get("/api/v1/memory/patterns")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["patterns"] == []

    def test_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/v1/memory/patterns")
        assert resp.status_code == 401
