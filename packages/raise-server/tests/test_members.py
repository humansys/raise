"""Tests for member endpoints — S616.2 T2.

Verifies member CRUD, seat enforcement, auto-key creation, soft delete,
role gating, and org scoping via mocked session + auth overrides.

NOTE: No `from __future__ import annotations` — FastAPI needs runtime type
resolution for dependency overrides (PAT-E-597).
"""

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.api.v1.members import router as member_router
from raise_server.auth import MemberContext, Plan, Role, verify_member
from raise_server.db.models import LicenseRow, MemberRow

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TARGET_MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")


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


def _mock_member(
    member_id: uuid.UUID = TARGET_MEMBER_ID,
    org_id: uuid.UUID = ORG_ID,
) -> MemberRow:
    """Create a mock MemberRow."""
    m = MagicMock(spec=MemberRow)
    m.id = member_id
    m.org_id = org_id
    m.email = "fernando@test.com"
    m.name = "Fernando"
    m.role = "member"
    m.is_active = True
    m.deleted_at = None
    m.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    m.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    return m


def _mock_license(seats: int = 10) -> LicenseRow:
    """Create a mock LicenseRow."""
    lic = MagicMock(spec=LicenseRow)
    lic.seats = seats
    return lic


def _mock_session_factory(
    *,
    scalar_one_or_none_result: Any = None,
    scalars_all_result: list[Any] | None = None,
    scalar_results: list[Any] | None = None,
) -> MagicMock:
    """Build a mock async session factory."""
    session = AsyncMock()

    if scalar_results is not None:
        # Multiple execute() calls return different results
        result_proxies = []
        for sr in scalar_results:
            rp = MagicMock()
            rp.scalar_one_or_none.return_value = sr
            rp.scalar.return_value = sr
            result_proxies.append(rp)
        session.execute.side_effect = result_proxies
    else:
        result_proxy = MagicMock()
        result_proxy.scalar_one_or_none.return_value = scalar_one_or_none_result
        result_proxy.scalars.return_value.all.return_value = scalars_all_result or []
        session.execute.return_value = result_proxy

    async def _refresh(obj: Any) -> None:
        # Simulate server defaults that DB would set
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = datetime.now(UTC)
        if getattr(obj, "is_active", None) is None:
            obj.is_active = True
        if getattr(obj, "role", None) is None:
            obj.role = "member"

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

    async def _override_verify() -> MemberContext:
        return ctx

    app.dependency_overrides[verify_member] = _override_verify
    app.state.session_factory = session_factory or _mock_session_factory()
    app.include_router(member_router)
    return app


class TestCreateMember:
    def test_admin_creates_member_with_key(self) -> None:
        """POST /members returns member + auto-created API key (AR-Q2)."""
        # scalar_results: [dup check=None, license, seat count=2]
        lic = _mock_license(seats=10)
        factory = _mock_session_factory(scalar_results=[None, lic, 2])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/members",
            json={"email": "new@test.com", "name": "New User"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@test.com"
        assert data["name"] == "New User"
        assert data["role"] == "member"
        assert "api_key" in data
        assert data["api_key"].startswith("rsk_")

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/members",
            json={"email": "new@test.com", "name": "New"},
        )
        assert resp.status_code == 403

    def test_wrong_org_returns_403(self) -> None:
        ctx = _make_ctx(org_id=OTHER_ORG_ID)
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/members",
            json={"email": "new@test.com", "name": "New"},
        )
        assert resp.status_code == 403

    def test_seat_limit_returns_409(self) -> None:
        """Seat enforcement: 409 when at limit (AC3)."""
        lic = _mock_license(seats=5)
        # scalar_results: [dup check=None, license, seat count=5 (full)]
        factory = _mock_session_factory(scalar_results=[None, lic, 5])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/members",
            json={"email": "new@test.com", "name": "New"},
        )
        assert resp.status_code == 409
        assert "Seat limit" in resp.json()["detail"]

    def test_duplicate_email_returns_409(self) -> None:
        existing = _mock_member()
        factory = _mock_session_factory(scalar_results=[existing])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/members",
            json={"email": "fernando@test.com", "name": "Duplicate"},
        )
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]


class TestListMembers:
    def test_admin_lists_members(self) -> None:
        members = [_mock_member()]
        factory = _mock_session_factory(scalars_all_result=members)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/members")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["email"] == "fernando@test.com"

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/members")
        assert resp.status_code == 403


class TestPatchMember:
    def test_admin_patches_role(self) -> None:
        member = _mock_member()
        factory = _mock_session_factory(scalar_one_or_none_result=member)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).patch(
            f"/api/v1/organizations/{ORG_ID}/members/{TARGET_MEMBER_ID}",
            json={"role": "admin"},
        )
        assert resp.status_code == 200

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).patch(
            f"/api/v1/organizations/{ORG_ID}/members/{TARGET_MEMBER_ID}",
            json={"role": "admin"},
        )
        assert resp.status_code == 403


class TestDeleteMember:
    def test_admin_soft_deletes_member(self) -> None:
        member = _mock_member()
        factory = _mock_session_factory(scalar_one_or_none_result=member)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).delete(
            f"/api/v1/organizations/{ORG_ID}/members/{TARGET_MEMBER_ID}"
        )
        assert resp.status_code == 204

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).delete(
            f"/api/v1/organizations/{ORG_ID}/members/{TARGET_MEMBER_ID}"
        )
        assert resp.status_code == 403
