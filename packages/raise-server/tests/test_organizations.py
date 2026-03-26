"""Tests for organization endpoints — S616.2 T1.

Strategy: Override verify_member to control MemberContext. For endpoints that
need DB (POST, GET list, PATCH), override session_factory with async mock.
For GET one (org_id path), verify_org_access returns controlled org.

NOTE: No `from __future__ import annotations` — FastAPI needs runtime type
resolution for dependency overrides (PAT-E-597).
"""

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.api.v1.organizations import router as org_router
from raise_server.auth import MemberContext, Plan, Role, verify_member
from raise_server.db.models import Organization

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


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


def _mock_org(org_id: uuid.UUID = ORG_ID) -> Organization:
    """Create a mock Organization with expected attributes."""
    org = MagicMock(spec=Organization)
    org.id = org_id
    org.name = "TestOrg"
    org.slug = "testorg"
    org.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    return org


def _mock_session_factory(
    *,
    execute_results: list[Any] | None = None,
    scalar_one_or_none_result: Any = None,
    scalars_all_result: list[Any] | None = None,
) -> MagicMock:
    """Build a mock async session factory for testing without real DB.

    Returns a MagicMock that, when called, returns an async context manager
    yielding an AsyncMock session. Mirrors async_sessionmaker behavior.
    """
    session = AsyncMock()

    # Default: execute returns a result proxy
    result_proxy = MagicMock()
    result_proxy.scalar_one_or_none.return_value = scalar_one_or_none_result
    result_proxy.scalars.return_value.all.return_value = scalars_all_result or []
    session.execute.return_value = result_proxy

    # session.refresh populates server-generated fields
    async def _refresh(obj: Any) -> None:
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = uuid.uuid4()
        if not hasattr(obj, "created_at") or obj.created_at is None:
            obj.created_at = datetime.now(UTC)

    session.refresh.side_effect = _refresh

    # Build async context manager that factory() returns
    ctx_manager = MagicMock()
    ctx_manager.__aenter__ = AsyncMock(return_value=session)
    ctx_manager.__aexit__ = AsyncMock(return_value=None)

    # factory() returns the context manager (synchronous call, like async_sessionmaker)
    factory = MagicMock()
    factory.return_value = ctx_manager

    return factory


def _make_app(
    *,
    ctx: MemberContext | None = None,
    session_factory: AsyncMock | None = None,
) -> FastAPI:
    """Build app with org router and overridden auth."""
    app = FastAPI()

    if ctx is None:
        ctx = _make_ctx()

    async def _override_verify() -> MemberContext:
        return ctx

    app.dependency_overrides[verify_member] = _override_verify
    app.state.session_factory = session_factory or _mock_session_factory()
    app.include_router(org_router)

    return app


class TestCreateOrganization:
    def test_admin_creates_org(self) -> None:
        factory = _mock_session_factory(scalar_one_or_none_result=None)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            "/api/v1/organizations",
            json={"name": "Acme", "slug": "acme"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Acme"
        assert data["slug"] == "acme"
        assert "id" in data

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).post(
            "/api/v1/organizations",
            json={"name": "Acme", "slug": "acme"},
        )
        assert resp.status_code == 403

    def test_duplicate_slug_returns_409(self) -> None:
        existing_org = _mock_org()
        factory = _mock_session_factory(scalar_one_or_none_result=existing_org)
        app = _make_app(session_factory=factory)
        resp = TestClient(app).post(
            "/api/v1/organizations",
            json={"name": "Acme", "slug": "testorg"},
        )
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_invalid_slug_returns_422(self) -> None:
        app = _make_app()
        resp = TestClient(app).post(
            "/api/v1/organizations",
            json={"name": "Acme", "slug": "INVALID SLUG!"},
        )
        assert resp.status_code == 422


class TestListOrganizations:
    def test_admin_lists_orgs(self) -> None:
        org = _mock_org()
        factory = _mock_session_factory(scalars_all_result=[org])
        app = _make_app(session_factory=factory)
        resp = TestClient(app).get("/api/v1/organizations")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["slug"] == "testorg"

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).get("/api/v1/organizations")
        assert resp.status_code == 403


class TestGetOrganization:
    def test_own_org_returns_200(self) -> None:
        org = _mock_org(org_id=ORG_ID)
        factory = _mock_session_factory(scalar_one_or_none_result=org)
        ctx = _make_ctx(org_id=ORG_ID)
        app = _make_app(ctx=ctx, session_factory=factory)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "testorg"

    def test_wrong_org_returns_403(self) -> None:
        ctx = _make_ctx(org_id=OTHER_ORG_ID)
        app = _make_app(ctx=ctx)
        resp = TestClient(app).get(f"/api/v1/organizations/{ORG_ID}")
        assert resp.status_code == 403
        assert "Access denied" in resp.json()["detail"]


class TestPatchOrganization:
    def test_admin_patches_own_org(self) -> None:
        org = _mock_org(org_id=ORG_ID)
        factory = _mock_session_factory(scalar_one_or_none_result=org)
        ctx = _make_ctx(org_id=ORG_ID, role="admin")
        app = _make_app(ctx=ctx, session_factory=factory)
        resp = TestClient(app).patch(
            f"/api/v1/organizations/{ORG_ID}",
            json={"name": "NewName"},
        )
        assert resp.status_code == 200

    def test_member_role_rejected(self) -> None:
        ctx = _make_ctx(org_id=ORG_ID, role="member")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).patch(
            f"/api/v1/organizations/{ORG_ID}",
            json={"name": "NewName"},
        )
        assert resp.status_code == 403

    def test_wrong_org_returns_403(self) -> None:
        ctx = _make_ctx(org_id=OTHER_ORG_ID, role="admin")
        app = _make_app(ctx=ctx)
        resp = TestClient(app).patch(
            f"/api/v1/organizations/{ORG_ID}",
            json={"name": "NewName"},
        )
        assert resp.status_code == 403
