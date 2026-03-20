"""Tests for health endpoint — GET /health (public, no auth)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from raise_server.app import create_app
from raise_server.config import ServerConfig


@pytest.fixture
def client() -> TestClient:
    """Create test client with explicit config (no env vars needed)."""
    config = ServerConfig(database_url="postgresql+asyncpg://u:p@h/db")
    app = create_app(config=config)
    return TestClient(app)


class TestHealthEndpoint:
    """GET /health returns server status and DB connectivity."""

    def test_health_returns_200(self, client: TestClient) -> None:
        with patch(
            "raise_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body_when_db_connected(self, client: TestClient) -> None:
        with patch(
            "raise_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = client.get("/health")
        body = resp.json()
        assert body["status"] == "ok"
        assert body["database"] == "connected"
        assert "version" in body

    def test_health_body_when_db_disconnected(self, client: TestClient) -> None:
        with patch(
            "raise_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=False,
        ):
            resp = client.get("/health")
        body = resp.json()
        assert resp.status_code == 200
        assert body["database"] == "disconnected"
