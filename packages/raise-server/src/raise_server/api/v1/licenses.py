"""License management endpoints — S616.2.

2 endpoints: POST (create/replace), GET (current active).
One active license per org (D7). POST deactivates existing before creating new.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from raise_server.auth import MemberContext, requires_org_role
from raise_server.db.models import LicenseRow
from raise_server.deps import get_session_factory
from raise_server.schemas.admin import CreateLicenseRequest, LicenseResponse

router = APIRouter(
    prefix="/api/v1/organizations/{org_id}/license",
    tags=["licenses"],
)

OrgAdmin = Annotated[MemberContext, requires_org_role("admin")]
OrgMember = Annotated[MemberContext, requires_org_role()]


@router.post("", status_code=201, response_model=LicenseResponse)
async def create_license(
    request: Request,
    org_id: uuid.UUID,
    body: CreateLicenseRequest,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> LicenseResponse:
    """Create or replace license. Deactivates existing active license (D7)."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        # Deactivate existing active license if any
        existing_result = await session.execute(
            select(LicenseRow).where(
                LicenseRow.org_id == org_id,
                LicenseRow.status == "active",
            ).limit(1)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.status = "replaced"

        # Create new license
        lic = LicenseRow(
            org_id=org_id,
            plan=body.plan,
            features=body.features,
            seats=body.seats,
            status="active",
            expires_at=body.expires_at,
        )
        session.add(lic)
        await session.commit()
        await session.refresh(lic)
        return LicenseResponse.model_validate(lic, from_attributes=True)


@router.get("", response_model=LicenseResponse)
async def get_license(
    request: Request,
    org_id: uuid.UUID,
    ctx: OrgMember,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> LicenseResponse:
    """Get current active license. Any org member."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(LicenseRow).where(
                LicenseRow.org_id == org_id,
                LicenseRow.status == "active",
            ).limit(1)
        )
        lic = result.scalar_one_or_none()
        if not lic:
            raise HTTPException(
                status_code=404,
                detail="No active license for this organization",
            )
        return LicenseResponse.model_validate(lic, from_attributes=True)
