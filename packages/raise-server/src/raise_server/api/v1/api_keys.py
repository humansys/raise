"""API key management endpoints — S616.2.

3 endpoints: POST (show-once), GET list (metadata only), DELETE (hard).
Raw key shown ONCE in POST response, never stored or returned in GET (AC2, AC11).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import select

from raise_server.auth import MemberContext, requires_org_role
from raise_server.db.models import ApiKeyRow, MemberRow
from raise_server.deps import get_session_factory
from raise_server.schemas.admin import (
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    CreateApiKeyRequest,
)

router = APIRouter(
    prefix="/api/v1/organizations/{org_id}/api-keys",
    tags=["api-keys"],
)

OrgAdmin = Annotated[MemberContext, requires_org_role("admin")]


@router.post("", status_code=201, response_model=ApiKeyCreatedResponse)
async def create_api_key(
    request: Request,
    org_id: uuid.UUID,
    body: CreateApiKeyRequest,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> ApiKeyCreatedResponse:
    """Create API key. Raw key shown ONCE in response (D5)."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        # Verify member exists in this org
        result = await session.execute(
            select(MemberRow).where(
                MemberRow.id == body.member_id,
                MemberRow.org_id == org_id,
                MemberRow.deleted_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found in this organization")

        # Generate key
        raw_key = "rsk_" + secrets.token_hex(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:12]

        api_key = ApiKeyRow(
            member_id=body.member_id,
            org_id=org_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=body.scopes,
        )
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)

        return ApiKeyCreatedResponse(
            id=api_key.id,
            key=raw_key,
            prefix=key_prefix,
            scopes=api_key.scopes,
            created_at=api_key.created_at,
        )


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    request: Request,
    org_id: uuid.UUID,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> list[ApiKeyResponse]:
    """List API key metadata. NEVER returns raw key (AC2, AC11)."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(ApiKeyRow).where(
                ApiKeyRow.org_id == org_id,
                ApiKeyRow.is_active == True,  # noqa: E712
            )
        )
        keys = result.scalars().all()
        return [
            ApiKeyResponse.model_validate(k, from_attributes=True)
            for k in keys
        ]


@router.delete("/{key_id}", status_code=204)
async def delete_api_key(
    request: Request,
    org_id: uuid.UUID,
    key_id: uuid.UUID,
    ctx: OrgAdmin,  # noqa: ARG001 — triggers auth + org-scoping dependency
) -> Response:
    """Hard delete API key — row permanently removed (AC5, D5)."""
    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(ApiKeyRow).where(
                ApiKeyRow.id == key_id,
                ApiKeyRow.org_id == org_id,
            )
        )
        key = result.scalar_one_or_none()
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")

        await session.delete(key)
        await session.commit()
        return Response(status_code=204)
