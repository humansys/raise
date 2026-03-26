"""Tests for API key endpoints — S616.2 T3.

Verifies show-once pattern (AC2): raw key in POST, never in GET.
Hard delete (AC5): row permanently removed.

NOTE: No `from __future__ import annotations` (PAT-E-597).
"""

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.api.v1.api_keys import router as api_keys_router
from raise_server.auth import MemberContext, Plan, Role, verify_member
from raise_server.db.models import ApiKeyRow, MemberRow

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TARGET_MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
KEY_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")


def _make_ctx(
    *,
    org_id: uuid.UUID = ORG_ID,
    role: Role = "admin",
    plan: Plan = "team",
) -> MemberContext:
    return MemberContext(
        org_id=org_id,
        org_name="TestOrg",
        member_id=MEMBER_ID,
        email="admin@test.com",
        role=role,
        plan=plan,
        features=["jira"],
    )


def _mock_api_key(key_id: uuid.UUID = KEY_ID) -> ApiKeyRow:
    k = MagicMock(spec=ApiKeyRow)
    k.id = key_id
    k.member_id = TARGET_MEMBER_ID
    k.org_id = ORG_ID
    k.key_hash = "abc123hash"
    k.key_prefix = "rsk_abc12345"
    k.scopes = ["full_access"]
    k.last_used_at = None
    k.is_active = True
    k.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    return k


def _mock_session_factory(
    *,
    scalar_one_or_none_result: Any = None,
    scalars_all_result: list[Any] | None = None,
    scalar_results: list[Any] | None = None,
) -> MagicMock:
    session = AsyncMock()

    if scalar_results is not None:
        result_proxies = []
        for sr in scalar_results:
            rp = MagicMock()
            rp.scalar_one_or_none.return_value = sr
            result_proxies.append(rp)
        session.execute.side_effect = result_proxies
    else:
        result_proxy = MagicMock()
        result_proxy.scalar_one_or_none.return_value = scalar_one_or_none_result
        result_proxy.scalars.return_value.all.return_value = scalars_all_result or []
        session.execute.return_value = result_proxy

    async def _refresh(obj: Any) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        if getattr(obj, "is_active", None) is None:
            obj.is_active = True

    session.refresh.side_effect = _refresh

    ctx_manager = MagicMock()
    ctx_manager.__aenter__ = AsyncMock(return_value=session)
    ctx_manager.__aexit__ = AsyncMock(return_value=None)

    factory = MagicMock()
    factory.return_value = ctx_manager
    return factory


def _make_app(
    *,
    ctx: MemberContext | None = None,
    session_factory: MagicMock | None = None,
) -> FastAPI:
    app = FastAPI()
    if ctx is None:
        ctx = _make_ctx()

    async def _override() -> MemberContext:
        return ctx

    app.dependency_overrides[verify_member] = _override
    app.state.session_factory = session_factory or _mock_session_factory()
    app.include_router(api_keys_router)
    return app


class TestCreateApiKey:
    def test_admin_creates_key_show_once(self) -> None:
        """POST returns raw key (AC2 — shown once)."""
        member = MagicMock(spec=MemberRow)
        member.id = TARGET_MEMBER_ID
        member.org_id = ORG_ID
        factory = _mock_session_factory(scalar_results=[member])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/api-keys",
            json={"member_id": str(TARGET_MEMBER_ID)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["key"].startswith("rsk_")
        assert len(data["key"]) == 68  # rsk_ + 64 hex chars
        assert data["prefix"] == data["key"][:12]
        assert "scopes" in data

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/api-keys",
            json={"member_id": str(TARGET_MEMBER_ID)},
        )
        assert resp.status_code == 403

    def test_wrong_org_returns_403(self) -> None:
        ctx = _make_ctx(org_id=OTHER_ORG_ID)
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/api-keys",
            json={"member_id": str(TARGET_MEMBER_ID)},
        )
        assert resp.status_code == 403


class TestListApiKeys:
    def test_admin_lists_keys_no_raw(self) -> None:
        """GET never returns raw key (AC2, AC11)."""
        keys = [_mock_api_key()]
        factory = _mock_session_factory(scalars_all_result=keys)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/api-keys")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert "key" not in data[0]
        assert "key_hash" not in data[0]
        assert data[0]["prefix"] == "rsk_abc12345"

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/api-keys")
        assert resp.status_code == 403


class TestDeleteApiKey:
    def test_admin_hard_deletes_key(self) -> None:
        """DELETE permanently removes key row (AC5)."""
        key = _mock_api_key()
        factory = _mock_session_factory(scalar_one_or_none_result=key)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).delete(
            f"/api/v1/organizations/{ORG_ID}/api-keys/{KEY_ID}"
        )
        assert resp.status_code == 204

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).delete(
            f"/api/v1/organizations/{ORG_ID}/api-keys/{KEY_ID}"
        )
        assert resp.status_code == 403
