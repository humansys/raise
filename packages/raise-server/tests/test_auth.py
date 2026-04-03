"""Tests for auth module — T3.

Strategy: Test requires_plan/requires_role logic via FastAPI TestClient
with a minimal app and dependency overrides. No real DB — verify_member
is overridden to return controlled MemberContext values.

NOTE: No `from __future__ import annotations` — FastAPI needs runtime type
resolution for Annotated[] dependencies (PAT-E-597).
"""

import uuid
from typing import Annotated

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.auth import (
    PLAN_RANK,
    MemberContext,
    Plan,
    Role,
    requires_plan,
    requires_role,
    verify_member,
)


def _make_ctx(
    *,
    plan: Plan = "team",
    role: Role = "member",
    features: list[str] | None = None,
) -> MemberContext:
    return MemberContext(
        org_id=uuid.uuid4(),
        org_name="TestOrg",
        member_id=uuid.uuid4(),
        email="test@example.com",
        role=role,
        plan=plan,
        features=features or [],
    )


def _make_app(
    ctx: MemberContext,
    plan_required: str | None = None,
    role_required: str | None = None,
) -> FastAPI:
    """Build a minimal FastAPI app with auth dependencies for testing."""
    app = FastAPI()

    async def _override_verify() -> MemberContext:
        return ctx

    app.dependency_overrides[verify_member] = _override_verify

    if plan_required:
        dep = requires_plan(plan_required)

        @app.get("/test")
        async def endpoint(ctx: Annotated[MemberContext, dep]) -> dict[str, str]:  # noqa: N806
            return {"plan": ctx.plan}

    elif role_required:
        dep = requires_role(role_required)

        @app.get("/test")
        async def endpoint(ctx: Annotated[MemberContext, dep]) -> dict[str, str]:  # type: ignore[no-redef]  # noqa: N806
            return {"role": ctx.role}

    return app


class TestRequiresPlan:
    def test_sufficient_plan_passes(self) -> None:
        ctx = _make_ctx(plan="team")
        app = _make_app(ctx, plan_required="team")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 200
        assert resp.json()["plan"] == "team"

    def test_higher_plan_passes(self) -> None:
        ctx = _make_ctx(plan="enterprise")
        app = _make_app(ctx, plan_required="team")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 200

    def test_insufficient_plan_returns_403(self) -> None:
        ctx = _make_ctx(plan="pro")
        app = _make_app(ctx, plan_required="team")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 403
        detail = resp.json()["detail"]
        assert detail["required_plan"] == "team"
        assert detail["current_plan"] == "pro"
        assert "Requires 'team' plan" in detail["message"]

    def test_community_plan_blocked_from_pro(self) -> None:
        ctx = _make_ctx(plan="community")
        app = _make_app(ctx, plan_required="pro")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 403

    def test_community_plan_passes_community_endpoint(self) -> None:
        ctx = _make_ctx(plan="community")
        app = _make_app(ctx, plan_required="community")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 200


class TestRequiresRole:
    def test_admin_passes_admin_check(self) -> None:
        ctx = _make_ctx(role="admin")
        app = _make_app(ctx, role_required="admin")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_member_blocked_from_admin(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx, role_required="admin")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 403
        detail = resp.json()["detail"]
        assert detail["required_role"] == "admin"
        assert detail["current_role"] == "member"
        assert "Requires 'admin' role" in detail["message"]

    def test_member_passes_member_check(self) -> None:
        ctx = _make_ctx(role="member")
        app = _make_app(ctx, role_required="member")
        resp = TestClient(app).get("/test")
        assert resp.status_code == 200


class TestMemberContextFields:
    def test_community_plan_with_empty_features(self) -> None:
        ctx = _make_ctx(plan="community", features=[])
        assert ctx.plan == "community"
        assert ctx.features == []

    def test_team_plan_with_features(self) -> None:
        ctx = _make_ctx(plan="team", features=["jira", "confluence"])
        assert ctx.features == ["jira", "confluence"]


class TestPlanRankConsistency:
    def test_plan_rank_covers_all_context_plans(self) -> None:
        for plan in ("community", "pro", "team", "enterprise"):
            assert plan in PLAN_RANK

    def test_plan_rank_is_monotonic(self) -> None:
        plans = ["community", "pro", "team", "enterprise"]
        for i in range(len(plans) - 1):
            assert PLAN_RANK[plans[i]] < PLAN_RANK[plans[i + 1]]
