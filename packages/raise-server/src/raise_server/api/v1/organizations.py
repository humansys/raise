"""Organization management endpoints — S616.2.

4 endpoints: POST, GET list, GET one, PATCH.
No DELETE — deferred per AR-Q3 (YAGNI, 1 org in MVP).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from raise_server.auth import MemberContext, requires_org_role, requires_role
from raise_server.db.models import Organization
from raise_server.deps import get_session_factory
from raise_server.schemas.admin import (
    CreateOrganizationRequest,
    OrganizationResponse,
    PatchOrganizationRequest,
)

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])

AdminCtx = Annotated[MemberContext, requires_role("admin")]
OrgMember = Annotated[MemberContext, requires_org_role()]
OrgAdmin = Annotated[MemberContext, requires_org_role("admin")]


@router.post("", status_code=201, response_model=OrganizationResponse)
async def create_organization(
    request: Request,
    body: CreateOrganizationRequest,
    ctx: AdminCtx,  # noqa: ARG001 — triggers auth dependency
) -> OrganizationResponse:
    """Create a new organization. Admin only (D1: admin=superadmin for MVP)."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        # Check slug uniqueness
        result = await session.execute(
            select(Organization).where(Organization.slug == body.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Organization with slug '{body.slug}' already exists",
            )

        org = Organization(name=body.name, slug=body.slug)
        session.add(org)
        await session.commit()
        await session.refresh(org)
        return OrganizationResponse.model_validate(org, from_attributes=True)


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    request: Request,
    ctx: AdminCtx,  # noqa: ARG001 — triggers auth dependency
) -> list[OrganizationResponse]:
    """List all organizations. Admin only."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(select(Organization))
        orgs = result.scalars().all()
        return [
            OrganizationResponse.model_validate(org, from_attributes=True)
            for org in orgs
        ]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    request: Request,
    org_id: uuid.UUID,
    ctx: OrgMember,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> OrganizationResponse:
    """Get organization details. Any member of this org."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return OrganizationResponse.model_validate(org, from_attributes=True)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    request: Request,
    org_id: uuid.UUID,
    body: PatchOrganizationRequest,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> OrganizationResponse:
    """Update organization. Admin of this org only."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        if body.name is not None:
            org.name = body.name

        await session.commit()
        await session.refresh(org)
        return OrganizationResponse.model_validate(org, from_attributes=True)
