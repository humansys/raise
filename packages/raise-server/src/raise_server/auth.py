"""Member authentication and plan/role enforcement — FastAPI dependencies.

Auth chain: Bearer rsk_... → SHA-256 → api_keys JOIN members JOIN organizations
→ license lookup → MemberContext. Plan and role checks as composable dependencies.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Literal, cast

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func, select

from raise_server.db.models import ApiKeyRow, LicenseRow, MemberRow, Organization
from raise_server.deps import get_session_factory

Role = Literal["admin", "member"]
Plan = Literal["community", "pro", "team", "enterprise"]

PLAN_RANK: dict[str, int] = {"community": 0, "pro": 1, "team": 2, "enterprise": 3}


class MemberContext(BaseModel):
    """Authenticated member context injected into request handlers."""

    org_id: uuid.UUID
    org_name: str
    member_id: uuid.UUID
    email: str
    role: Role
    plan: Plan
    features: list[str]


async def verify_member(request: Request) -> MemberContext:
    """FastAPI dependency: validate API key, resolve member + org + license.

    Expects header: Authorization: Bearer rsk_<key>
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not auth_header.startswith("Bearer rsk_"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format. Expected: Bearer rsk_<key>",
        )

    raw_key = auth_header.removeprefix("Bearer ")
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        # Joined query: api_key → member → organization
        result = await session.execute(
            select(ApiKeyRow, MemberRow, Organization)
            .join(MemberRow, ApiKeyRow.member_id == MemberRow.id)
            .join(Organization, MemberRow.org_id == Organization.id)
            .where(
                ApiKeyRow.key_hash == key_hash,
                ApiKeyRow.is_active == True,  # noqa: E712
                MemberRow.is_active == True,  # noqa: E712
                MemberRow.deleted_at.is_(None),
            )
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")

        api_key, member, org = row

        # License lookup (separate query — optional, may not exist)
        lic_result = await session.execute(
            select(LicenseRow)
            .where(
                LicenseRow.org_id == org.id,
                LicenseRow.status == "active",
            )
            .limit(1)
        )
        lic = lic_result.scalar_one_or_none()

        plan = lic.plan if lic else "community"
        features: list[str] = lic.features if lic else []

        # Update last_used_at — telemetry, must not break auth on failure
        try:
            api_key.last_used_at = func.now()  # type: ignore[assignment]  # SQL expression, not datetime
            await session.commit()
        except Exception:  # noqa: BLE001
            await session.rollback()

        return MemberContext(
            org_id=org.id,
            org_name=org.name,
            member_id=member.id,
            email=member.email,
            role=cast("Role", member.role),
            plan=cast("Plan", plan),
            features=features,
        )


def requires_plan(minimum: str) -> Depends:  # type: ignore[type-arg]
    """FastAPI dependency factory — returns 403 if plan insufficient."""

    async def check(ctx: MemberContext = Depends(verify_member)) -> MemberContext:  # noqa: B008
        if PLAN_RANK.get(ctx.plan, 0) < PLAN_RANK.get(minimum, 0):
            raise HTTPException(
                status_code=403,
                detail={
                    "message": f"Requires '{minimum}' plan. Current: '{ctx.plan}'.",
                    "required_plan": minimum,
                    "current_plan": ctx.plan,
                },
            )
        return ctx

    return Depends(check)


def requires_role(role: str) -> Depends:  # type: ignore[type-arg]
    """FastAPI dependency factory — returns 403 if role insufficient."""

    async def check(ctx: MemberContext = Depends(verify_member)) -> MemberContext:  # noqa: B008
        if ctx.role != role:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": f"Requires '{role}' role. Current: '{ctx.role}'.",
                    "required_role": role,
                    "current_role": ctx.role,
                },
            )
        return ctx

    return Depends(check)


def requires_org_role(role: str | None = None) -> Depends:  # type: ignore[type-arg]
    """FastAPI dependency factory — verify org access from path + optional role check.

    Combines org-scoping (ctx.org_id == path org_id) with role gating in a single
    dependency. Impossible to bypass (Jidoka). See AR-Q1.

    Usage:
        OrgMember = Annotated[MemberContext, requires_org_role()]
        OrgAdmin = Annotated[MemberContext, requires_org_role("admin")]
    """

    async def check(
        org_id: uuid.UUID,
        ctx: MemberContext = Depends(verify_member),  # noqa: B008
    ) -> MemberContext:
        if ctx.org_id != org_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this organization",
            )
        if role and ctx.role != role:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": f"Requires '{role}' role. Current: '{ctx.role}'.",
                    "required_role": role,
                    "current_role": ctx.role,
                },
            )
        return ctx

    return Depends(check)
