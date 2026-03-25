"""Tests for SQLAlchemy models and Pydantic schemas — T1 RED phase.

Pure unit tests: instantiate models/schemas directly, verify fields and defaults.
No DB connection needed.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from raise_server.db.models import ApiKeyRow, LicenseRow, MemberRow


class TestMemberRow:
    def test_instantiation_with_required_fields(self, org_id: uuid.UUID) -> None:
        member = MemberRow(
            id=uuid.uuid4(),
            org_id=org_id,
            email="emilio@humansys.ai",
            name="Emilio",
        )
        assert member.email == "emilio@humansys.ai"
        assert member.name == "Emilio"
        assert member.org_id == org_id

    def test_role_accepts_valid_values(self, org_id: uuid.UUID) -> None:
        admin = MemberRow(
            id=uuid.uuid4(),
            org_id=org_id,
            email="admin@humansys.ai",
            name="Admin",
            role="admin",
        )
        assert admin.role == "admin"

    def test_is_active_settable(self, org_id: uuid.UUID) -> None:
        inactive = MemberRow(
            id=uuid.uuid4(),
            org_id=org_id,
            email="gone@humansys.ai",
            name="Gone",
            is_active=False,
        )
        assert inactive.is_active is False

    def test_deleted_at_nullable(self, org_id: uuid.UUID) -> None:
        member = MemberRow(
            id=uuid.uuid4(),
            org_id=org_id,
            email="dev@humansys.ai",
            name="Dev",
        )
        assert member.deleted_at is None


class TestApiKeyRow:
    def test_instantiation_with_required_fields(
        self, org_id: uuid.UUID, member_id: uuid.UUID
    ) -> None:
        key = ApiKeyRow(
            id=uuid.uuid4(),
            member_id=member_id,
            org_id=org_id,
            key_hash="a" * 64,
            key_prefix="rsk_abc12345",
        )
        assert key.member_id == member_id
        assert key.org_id == org_id
        assert key.key_hash == "a" * 64
        assert key.key_prefix == "rsk_abc12345"

    def test_last_used_at_nullable(
        self, org_id: uuid.UUID, member_id: uuid.UUID
    ) -> None:
        key = ApiKeyRow(
            id=uuid.uuid4(),
            member_id=member_id,
            org_id=org_id,
            key_hash="b" * 64,
            key_prefix="rsk_xyz98765",
        )
        assert key.last_used_at is None


class TestLicenseRow:
    def test_instantiation_with_required_fields(self, org_id: uuid.UUID) -> None:
        now = datetime.now(UTC)
        lic = LicenseRow(
            id=uuid.uuid4(),
            org_id=org_id,
            plan="team",
            features=["jira", "confluence"],
            seats=5,
            status="active",
            expires_at=now,
        )
        assert lic.plan == "team"
        assert lic.features == ["jira", "confluence"]
        assert lic.seats == 5
        assert lic.status == "active"

    def test_license_plans(self, org_id: uuid.UUID) -> None:
        now = datetime.now(UTC)
        for plan in ("pro", "team", "enterprise"):
            lic = LicenseRow(
                id=uuid.uuid4(),
                org_id=org_id,
                plan=plan,
                features=[],
                seats=1,
                status="active",
                expires_at=now,
            )
            assert lic.plan == plan

    def test_license_statuses(self, org_id: uuid.UUID) -> None:
        now = datetime.now(UTC)
        for status in ("active", "expired", "revoked"):
            lic = LicenseRow(
                id=uuid.uuid4(),
                org_id=org_id,
                plan="pro",
                features=[],
                seats=1,
                status=status,
                expires_at=now,
            )
            assert lic.status == status


class TestMemberContext:
    def test_construction(self) -> None:
        from raise_server.auth import MemberContext

        ctx = MemberContext(
            org_id=uuid.uuid4(),
            org_name="HumanSys",
            member_id=uuid.uuid4(),
            email="emilio@humansys.ai",
            role="admin",
            plan="team",
            features=["jira", "confluence"],
        )
        assert ctx.org_name == "HumanSys"
        assert ctx.role == "admin"
        assert ctx.plan == "team"
        assert ctx.features == ["jira", "confluence"]

    def test_community_plan_empty_features(self) -> None:
        from raise_server.auth import MemberContext

        ctx = MemberContext(
            org_id=uuid.uuid4(),
            org_name="FreeCo",
            member_id=uuid.uuid4(),
            email="dev@freeco.io",
            role="member",
            plan="community",
            features=[],
        )
        assert ctx.plan == "community"
        assert ctx.features == []


class TestPlanRank:
    def test_ordering(self) -> None:
        from raise_server.auth import PLAN_RANK

        assert PLAN_RANK["community"] < PLAN_RANK["pro"]
        assert PLAN_RANK["pro"] < PLAN_RANK["team"]
        assert PLAN_RANK["team"] < PLAN_RANK["enterprise"]

    def test_all_plans_present(self) -> None:
        from raise_server.auth import PLAN_RANK

        assert set(PLAN_RANK.keys()) == {"community", "pro", "team", "enterprise"}
