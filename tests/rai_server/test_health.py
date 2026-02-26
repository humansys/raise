"""Tests for health endpoint — GET /health (public, no auth)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create test client with minimal config."""
    monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
    from rai_server.app import create_app

    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """GET /health returns server status and DB connectivity."""

    def test_health_returns_200(self, client: TestClient) -> None:
        with patch(
            "rai_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body_when_db_connected(self, client: TestClient) -> None:
        with patch(
            "rai_server.api.v1.health._check_db",
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
            "rai_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=False,
        ):
            resp = client.get("/health")
        body = resp.json()
        assert resp.status_code == 200
        assert body["database"] == "disconnected"

    def test_health_no_auth_required(self, client: TestClient) -> None:
        """Health is public — no Authorization header needed."""
        with patch(
            "rai_server.api.v1.health._check_db",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = client.get("/health")
        assert resp.status_code == 200
