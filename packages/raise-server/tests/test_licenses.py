"""Tests for license endpoints — S616.2 T4.

NOTE: No `from __future__ import annotations` (PAT-E-597).
"""

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.api.v1.licenses import router as license_router
from raise_server.auth import MemberContext, Plan, Role, verify_member
from raise_server.db.models import LicenseRow

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
LICENSE_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")


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


def _mock_license(license_id: uuid.UUID = LICENSE_ID) -> LicenseRow:
    lic = MagicMock(spec=LicenseRow)
    lic.id = license_id
    lic.org_id = ORG_ID
    lic.plan = "team"
    lic.features = ["jira", "confluence"]
    lic.seats = 10
    lic.status = "active"
    lic.expires_at = datetime(2027, 1, 1, tzinfo=UTC)
    lic.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    lic.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    return lic


def _mock_session_factory(
    *,
    scalar_one_or_none_result: Any = None,
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
        session.execute.return_value = result_proxy

    async def _refresh(obj: Any) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = datetime.now(UTC)
        if getattr(obj, "status", None) is None:
            obj.status = "active"

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
    app.include_router(license_router)
    return app


class TestCreateLicense:
    def test_admin_creates_license(self) -> None:
        # scalar_results: [existing license=None (no active)]
        factory = _mock_session_factory(scalar_results=[None])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/license",
            json={
                "plan": "team",
                "features": ["jira", "confluence"],
                "seats": 10,
                "expires_at": "2027-01-01T00:00:00Z",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["plan"] == "team"
        assert data["seats"] == 10
        assert data["status"] == "active"

    def test_replaces_existing_license(self) -> None:
        """POST deactivates existing active license before creating new."""
        existing = _mock_license()
        factory = _mock_session_factory(scalar_results=[existing])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/license",
            json={
                "plan": "enterprise",
                "features": ["jira", "confluence", "odoo"],
                "seats": 50,
                "expires_at": "2028-01-01T00:00:00Z",
            },
        )
        assert resp.status_code == 201
        # Verify old license was deactivated
        assert existing.status == "replaced"

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            f"/api/v1/organizations/{ORG_ID}/license",
            json={
                "plan": "team",
                "features": [],
                "seats": 5,
                "expires_at": "2027-01-01T00:00:00Z",
            },
        )
        assert resp.status_code == 403


class TestGetLicense:
    def test_member_gets_active_license(self) -> None:
        """Any org member can view the license."""
        lic = _mock_license()
        factory = _mock_session_factory(scalar_one_or_none_result=lic)
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx, session_factory=factory)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/license")
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "team"

    def test_no_license_returns_404(self) -> None:
        factory = _mock_session_factory(scalar_one_or_none_result=None)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/license")
        assert resp.status_code == 404

    def test_wrong_org_returns_403(self) -> None:
        ctx = _make_ctx(org_id=OTHER_ORG_ID)
        app = _make_app(ctx=ctx)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}/license")
        assert resp.status_code == 403
