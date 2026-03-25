"""Tests for router auth integration — T4.

Verifies that all 3 routers (graph, memory, agent) use requires_plan("team")
by testing with controlled MemberContext via dependency overrides.

NOTE: No `from __future__ import annotations` — FastAPI needs runtime type
resolution for dependency overrides (PAT-E-597).
"""

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from raise_server.api.v1.agent import router as agent_router
from raise_server.api.v1.graph import router as graph_router
from raise_server.api.v1.memory import router as memory_router
from raise_server.auth import MemberContext, Plan, verify_member


def _make_ctx(*, plan: Plan = "team") -> MemberContext:
    return MemberContext(
        org_id=uuid.uuid4(),
        org_name="TestOrg",
        member_id=uuid.uuid4(),
        email="test@example.com",
        role="member",
        plan=plan,
        features=["jira"] if plan != "community" else [],
    )


def _make_app(plan: Plan = "team") -> FastAPI:
    """Build app with all routers and overridden auth."""
    app = FastAPI()
    ctx = _make_ctx(plan=plan)

    async def _override_verify() -> MemberContext:
        return ctx

    app.dependency_overrides[verify_member] = _override_verify

    # Mock session_factory — routers need it but we don't call DB
    app.state.session_factory = None  # type: ignore[assignment]
    app.state.engine = None  # type: ignore[assignment]

    app.include_router(graph_router)
    app.include_router(memory_router)
    app.include_router(agent_router)

    return app


class TestGraphRouterAuth:
    def test_team_plan_passes_auth(self) -> None:
        app = _make_app(plan="team")
        resp = TestClient(app, raise_server_exceptions=False).get(
            "/api/v1/graph/query?q=test"
        )
        # 500 = auth passed, service failed (no DB). Not 401/403.
        assert resp.status_code == 500

    def test_community_plan_blocked(self) -> None:
        app = _make_app(plan="community")
        resp = TestClient(app).get("/api/v1/graph/query?q=test")
        assert resp.status_code == 403


class TestMemoryRouterAuth:
    def test_team_plan_passes_auth(self) -> None:
        app = _make_app(plan="team")
        resp = TestClient(app, raise_server_exceptions=False).get(
            "/api/v1/memory/patterns"
        )
        assert resp.status_code == 500

    def test_community_plan_blocked(self) -> None:
        app = _make_app(plan="community")
        resp = TestClient(app).get("/api/v1/memory/patterns")
        assert resp.status_code == 403


class TestAgentRouterAuth:
    def test_team_plan_passes_auth(self) -> None:
        app = _make_app(plan="team")
        resp = TestClient(app, raise_server_exceptions=False).get(
            "/api/v1/agent/events"
        )
        assert resp.status_code == 500

    def test_community_plan_blocked(self) -> None:
        app = _make_app(plan="community")
        resp = TestClient(app).get("/api/v1/agent/events")
        assert resp.status_code == 403

    def test_pro_plan_blocked(self) -> None:
        app = _make_app(plan="pro")
        resp = TestClient(app).get("/api/v1/agent/events")
        assert resp.status_code == 403

    def test_enterprise_plan_passes_auth(self) -> None:
        app = _make_app(plan="enterprise")
        resp = TestClient(app, raise_server_exceptions=False).get(
            "/api/v1/agent/events"
        )
        assert resp.status_code == 500
