"""Member management endpoints — S616.2.

4 endpoints: POST (with auto-key), GET list, PATCH role, DELETE (soft).
POST auto-creates first API key per AR-Q2 (value stream).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import func, select

from raise_server.auth import MemberContext, requires_org_role
from raise_server.db.models import ApiKeyRow, LicenseRow, MemberRow
from raise_server.deps import get_session_factory
from raise_server.schemas.admin import (
    CreateMemberRequest,
    MemberCreatedResponse,
    MemberResponse,
    PatchMemberRequest,
)

router = APIRouter(
    prefix="/api/v1/organizations/{org_id}/members",
    tags=["members"],
)

OrgAdmin = Annotated[MemberContext, requires_org_role("admin")]


@router.post("", status_code=201, response_model=MemberCreatedResponse)
async def create_member(
    request: Request,
    org_id: uuid.UUID,
    body: CreateMemberRequest,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> MemberCreatedResponse:
    """Create member + auto-create first API key (AR-Q2). Enforces seat limit."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        # Check duplicate email in org
        dup_result = await session.execute(
            select(MemberRow).where(
                MemberRow.org_id == org_id,
                MemberRow.email == body.email,
                MemberRow.deleted_at.is_(None),
            )
        )
        if dup_result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Member with email '{body.email}' already exists in this organization",
            )

        # Seat enforcement: count active members vs license seats
        lic_result = await session.execute(
            select(LicenseRow).where(
                LicenseRow.org_id == org_id,
                LicenseRow.status == "active",
            ).limit(1)
        )
        lic = lic_result.scalar_one_or_none()
        if lic:
            count_result = await session.execute(
                select(func.count()).select_from(MemberRow).where(
                    MemberRow.org_id == org_id,
                    MemberRow.is_active == True,  # noqa: E712
                    MemberRow.deleted_at.is_(None),
                )
            )
            active_count = count_result.scalar()
            if active_count is not None and active_count >= lic.seats:
                raise HTTPException(
                    status_code=409,
                    detail=f"Seat limit reached. License allows {lic.seats} seats, {active_count} active members exist.",
                )

        # Create member
        member = MemberRow(
            org_id=org_id,
            email=body.email,
            name=body.name,
            role=body.role,
        )
        session.add(member)
        await session.flush()

        # Auto-create first API key (AR-Q2)
        raw_key = "rsk_" + secrets.token_hex(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:12]
        api_key = ApiKeyRow(
            member_id=member.id,
            org_id=org_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
        )
        session.add(api_key)

        await session.commit()
        await session.refresh(member)

        return MemberCreatedResponse(
            id=member.id,
            email=member.email,
            name=member.name,
            role=member.role,
            is_active=member.is_active,
            created_at=member.created_at,
            api_key=raw_key,
        )


@router.get("", response_model=list[MemberResponse])
async def list_members(
    request: Request,
    org_id: uuid.UUID,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> list[MemberResponse]:
    """List active members of organization. Admin only."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(MemberRow).where(
                MemberRow.org_id == org_id,
                MemberRow.deleted_at.is_(None),
            )
        )
        members = result.scalars().all()
        return [
            MemberResponse.model_validate(m, from_attributes=True)
            for m in members
        ]


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    request: Request,
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    body: PatchMemberRequest,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> MemberResponse:
    """Update member role. Admin only."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(MemberRow).where(
                MemberRow.id == member_id,
                MemberRow.org_id == org_id,
                MemberRow.deleted_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        member.role = body.role
        await session.commit()
        await session.refresh(member)
        return MemberResponse.model_validate(member, from_attributes=True)


@router.delete("/{member_id}", status_code=204)
async def delete_member(
    request: Request,
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> Response:
    """Soft delete member (AC4). Sets deleted_at and is_active=false."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(MemberRow).where(
                MemberRow.id == member_id,
                MemberRow.org_id == org_id,
                MemberRow.deleted_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        member.is_active = False
        member.deleted_at = func.now()  # type: ignore[assignment]  # SQL expression, not datetime
        await session.commit()
        return Response(status_code=204)
