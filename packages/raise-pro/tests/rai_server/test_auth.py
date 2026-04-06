"""Tests for member authentication middleware."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from raise_server.auth import MemberContext, verify_member


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture
def member_id() -> uuid.UUID:
    return uuid.UUID("22345678-1234-1234-1234-123456789abc")


@pytest.fixture
def raw_key() -> str:
    return "rsk_testkey123456"


@pytest.fixture
def key_hash(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def _make_client(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    key_hash: str,
    is_active: bool = True,
    key_exists: bool = True,
) -> TestClient:
    """Build a TestClient with mocked DB for auth tests."""
    from raise_server.db.models import ApiKeyRow, LicenseRow, MemberRow, Organization

    app = FastAPI()

    @app.get("/api/v1/protected")
    async def protected(ctx: MemberContext = Depends(verify_member)) -> dict[str, str]:  # noqa: B008
        return {"org_id": str(ctx.org_id), "org_name": ctx.org_name, "email": ctx.email}

    # Mock the DB objects
    mock_org = MagicMock(spec=Organization)
    mock_org.id = org_id
    mock_org.name = "Test Org"

    mock_member = MagicMock(spec=MemberRow)
    mock_member.id = member_id
    mock_member.org_id = org_id
    mock_member.email = "test@example.com"
    mock_member.role = "admin"
    mock_member.is_active = True
    mock_member.deleted_at = None

    mock_api_key = MagicMock(spec=ApiKeyRow)
    mock_api_key.key_hash = key_hash
    mock_api_key.is_active = is_active
    mock_api_key.member_id = member_id
    mock_api_key.last_used_at = None

    mock_license = MagicMock(spec=LicenseRow)
    mock_license.plan = "team"
    mock_license.features = []
    mock_license.status = "active"

    if key_exists and is_active:
        # First query: api_key JOIN member JOIN org
        mock_result = MagicMock()
        mock_result.first.return_value = (mock_api_key, mock_member, mock_org)
        # Second query: license lookup
        mock_lic_result = MagicMock()
        mock_lic_result.scalar_one_or_none.return_value = mock_license
    else:
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_lic_result = MagicMock()
        mock_lic_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.execute.side_effect = [mock_result, mock_lic_result]
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_factory = MagicMock()
    mock_factory.return_value = mock_session

    app.state.session_factory = mock_factory

    return TestClient(app)


class TestAuthMissingHeader:
    """Requests without Authorization header get 401."""

    def test_no_header_returns_401(self, org_id: uuid.UUID, member_id: uuid.UUID, key_hash: str) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get("/api/v1/protected")
        assert resp.status_code == 401

    def test_no_header_error_message(self, org_id: uuid.UUID, member_id: uuid.UUID, key_hash: str) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get("/api/v1/protected")
        assert "Missing Authorization" in resp.json()["detail"]


class TestAuthInvalidFormat:
    """Requests with wrong key format get 401."""

    def test_no_bearer_prefix(self, org_id: uuid.UUID, member_id: uuid.UUID, key_hash: str) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get(
            "/api/v1/protected", headers={"Authorization": "rsk_testkey123456"}
        )
        assert resp.status_code == 401

    def test_wrong_prefix(self, org_id: uuid.UUID, member_id: uuid.UUID, key_hash: str) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get(
            "/api/v1/protected", headers={"Authorization": "Bearer bad_key123"}
        )
        assert resp.status_code == 401


class TestAuthValidKey:
    """Requests with valid active API key get MemberContext."""

    def test_valid_key_returns_200(
        self, org_id: uuid.UUID, member_id: uuid.UUID, raw_key: str, key_hash: str
    ) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert resp.status_code == 200

    def test_valid_key_returns_member_context(
        self, org_id: uuid.UUID, member_id: uuid.UUID, raw_key: str, key_hash: str
    ) -> None:
        client = _make_client(org_id, member_id, key_hash)
        resp = client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {raw_key}"}
        )
        body = resp.json()
        assert body["org_id"] == str(org_id)
        assert body["org_name"] == "Test Org"
        assert body["email"] == "test@example.com"


class TestAuthInactiveKey:
    """Inactive keys get 401."""

    def test_inactive_key_returns_401(
        self, org_id: uuid.UUID, member_id: uuid.UUID, raw_key: str, key_hash: str
    ) -> None:
        client = _make_client(org_id, member_id, key_hash, is_active=False)
        resp = client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {raw_key}"}
        )
        assert resp.status_code == 401


class TestAuthNonexistentKey:
    """Unknown keys get 401."""

    def test_unknown_key_returns_401(self, org_id: uuid.UUID, member_id: uuid.UUID, key_hash: str) -> None:
        client = _make_client(org_id, member_id, key_hash, key_exists=False)
        resp = client.get(
            "/api/v1/protected",
            headers={"Authorization": "Bearer rsk_doesnotexist"},
        )
        assert resp.status_code == 401
