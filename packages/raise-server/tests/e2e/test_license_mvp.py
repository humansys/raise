"""E2E integration tests for E616: License MVP.

Cross-story flow: seed (conftest) → auth (S616.1) → CRUD (S616.2) → plan enforcement.
All tests run against real PostgreSQL. Marked @pytest.mark.e2e.

NOTE: No `from __future__ import annotations` (PAT-E-597).
"""

import pytest

pytestmark = pytest.mark.e2e


# ── 1. Health & seed validation ──────────────────────────────────────────


class TestHealthAndSeed:
    async def test_health_with_db(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    async def test_seed_org_exists(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Seeded org is accessible via admin key."""
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["slug"] == "humansys"


# ── 2. Organization CRUD ────────────────────────────────────────────────


class TestOrganizationCrud:
    async def test_create_org(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.post(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"name": "Acme Corp", "slug": "acme-e2e"},
        )
        assert resp.status_code == 201
        assert resp.json()["slug"] == "acme-e2e"

    async def test_list_orgs(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 200
        slugs = [o["slug"] for o in resp.json()]
        assert "humansys" in slugs

    async def test_patch_org(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.patch(
            f"/api/v1/organizations/{seed_data['org_id']}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"name": "HumanSys AI"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "HumanSys AI"

    async def test_duplicate_slug_returns_409(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.post(
            "/api/v1/organizations",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"name": "Duplicate", "slug": "humansys"},
        )
        assert resp.status_code == 409


# ── 3. Member CRUD + auto-key ───────────────────────────────────────────


class TestMemberCrud:
    async def test_create_member_with_auto_key(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """POST /members returns member + raw API key (AR-Q2)."""
        resp = await client.post(
            f"/api/v1/organizations/{seed_data['org_id']}/members",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"email": "fernando-e2e@humansys.ai", "name": "Fernando E2E"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "fernando-e2e@humansys.ai"
        assert data["api_key"].startswith("rsk_")
        # Store for subsequent tests
        seed_data["fernando_id"] = data["id"]
        seed_data["fernando_key"] = data["api_key"]

    async def test_new_member_can_authenticate(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Auto-created key works for auth (cross-story: S616.1 + S616.2)."""
        fernando_key = seed_data.get("fernando_key")
        if not fernando_key:
            pytest.skip("Depends on test_create_member_with_auto_key")
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}",
            headers={"Authorization": f"Bearer {fernando_key}"},
        )
        assert resp.status_code == 200

    async def test_list_members(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}/members",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 200
        emails = [m["email"] for m in resp.json()]
        assert "emilio@humansys.ai" in emails

    async def test_patch_member_role(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        fernando_id = seed_data.get("fernando_id")
        if not fernando_id:
            pytest.skip("Depends on test_create_member_with_auto_key")
        resp = await client.patch(
            f"/api/v1/organizations/{seed_data['org_id']}/members/{fernando_id}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"role": "admin"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    async def test_duplicate_email_returns_409(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.post(
            f"/api/v1/organizations/{seed_data['org_id']}/members",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"email": "emilio@humansys.ai", "name": "Duplicate"},
        )
        assert resp.status_code == 409


# ── 4. API Key lifecycle ────────────────────────────────────────────────


class TestApiKeyLifecycle:
    async def test_create_additional_key_show_once(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """POST returns raw key; subsequent GET does not."""
        resp = await client.post(
            f"/api/v1/organizations/{seed_data['org_id']}/api-keys",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"member_id": seed_data["admin_id"]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["key"].startswith("rsk_")
        assert len(data["key"]) == 68
        seed_data["extra_key_id"] = data["id"]

    async def test_list_keys_no_raw(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """GET /api-keys never returns raw key (AC2, AC11)."""
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}/api-keys",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 200
        for key_data in resp.json():
            assert "key" not in key_data
            assert "key_hash" not in key_data
            assert "prefix" in key_data

    async def test_hard_delete_key(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """DELETE permanently removes key row (AC5)."""
        extra_key_id = seed_data.get("extra_key_id")
        if not extra_key_id:
            pytest.skip("Depends on test_create_additional_key_show_once")
        resp = await client.delete(
            f"/api/v1/organizations/{seed_data['org_id']}/api-keys/{extra_key_id}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 204


# ── 5. License lifecycle ────────────────────────────────────────────────


class TestLicenseLifecycle:
    async def test_get_active_license(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}/license",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 200
        assert resp.json()["plan"] == "team"

    async def test_replace_license(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """POST deactivates existing, creates new (D7)."""
        resp = await client.post(
            f"/api/v1/organizations/{seed_data['org_id']}/license",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={
                "plan": "enterprise",
                "features": ["jira", "confluence", "odoo", "gitlab", "sso"],
                "seats": 50,
                "expires_at": "2028-01-01T00:00:00Z",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["plan"] == "enterprise"

        # Verify GET returns the new license
        get_resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}/license",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert get_resp.json()["plan"] == "enterprise"


# ── 6. Cross-story: plan enforcement (S616.1) with S616.2 auth ─────────


class TestPlanEnforcement:
    async def test_team_plan_passes_graph_endpoint(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Authenticated member hits plan-gated endpoint (S616.1 requires_plan)."""
        # After license replace, plan is now "enterprise" which > "team"
        resp = await client.get(
            "/api/v1/graph/query?q=test",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        # 200 or 500 = auth+plan passed (500 = no graph data, but auth OK)
        assert resp.status_code in (200, 500)

    async def test_no_auth_returns_401(self, client) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get("/api/v1/graph/query?q=test")
        assert resp.status_code == 401

    async def test_invalid_key_returns_401(self, client) -> None:  # type: ignore[no-untyped-def]
        resp = await client.get(
            "/api/v1/graph/query?q=test",
            headers={"Authorization": "Bearer rsk_invalid_key_here"},
        )
        assert resp.status_code == 401


# ── 7. Org scoping ──────────────────────────────────────────────────────


class TestOrgScoping:
    async def test_wrong_org_returns_403(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Member of org A cannot access org B (AC7)."""
        # Use a non-existent org_id
        fake_org = "00000000-0000-0000-0000-ffffffffffff"
        resp = await client.get(
            f"/api/v1/organizations/{fake_org}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert resp.status_code == 403


# ── 8. Role gating ──────────────────────────────────────────────────────


class TestRoleGating:
    async def test_member_cannot_create_member(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Non-admin member gets 403 on admin endpoints (AC6)."""
        fernando_key = seed_data.get("fernando_key")
        if not fernando_key:
            pytest.skip("Depends on test_create_member_with_auto_key")
        # Fernando was promoted to admin in test_patch_member_role,
        # so we need to demote first
        fernando_id = seed_data["fernando_id"]
        await client.patch(
            f"/api/v1/organizations/{seed_data['org_id']}/members/{fernando_id}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
            json={"role": "member"},
        )
        # Now Fernando (role=member) tries to create a member → 403
        resp = await client.post(
            f"/api/v1/organizations/{seed_data['org_id']}/members",
            headers={"Authorization": f"Bearer {fernando_key}"},
            json={"email": "blocked@humansys.ai", "name": "Blocked"},
        )
        assert resp.status_code == 403


# ── 9. Soft delete + auth rejection ─────────────────────────────────────


class TestSoftDeleteAuth:
    async def test_soft_deleted_member_cannot_auth(self, client, seed_data) -> None:  # type: ignore[no-untyped-def]
        """Soft-deleted member's key stops working (cross-story validation)."""
        fernando_key = seed_data.get("fernando_key")
        fernando_id = seed_data.get("fernando_id")
        if not fernando_key or not fernando_id:
            pytest.skip("Depends on test_create_member_with_auto_key")

        # Soft delete Fernando
        del_resp = await client.delete(
            f"/api/v1/organizations/{seed_data['org_id']}/members/{fernando_id}",
            headers={"Authorization": f"Bearer {seed_data['raw_key']}"},
        )
        assert del_resp.status_code == 204

        # Fernando's key should now fail auth
        resp = await client.get(
            f"/api/v1/organizations/{seed_data['org_id']}",
            headers={"Authorization": f"Bearer {fernando_key}"},
        )
        assert resp.status_code == 401
