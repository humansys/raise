"""API key authentication — FastAPI dependency.

Extracts Bearer rsk_... token, validates hash against DB,
checks is_active, returns OrgContext with org info.
"""

from __future__ import annotations

import hashlib
import uuid

from fastapi import HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from raise_server.db.models import ApiKey, Organization
from raise_server.deps import get_session_factory


class OrgContext(BaseModel):
    """Authenticated organization context injected into request handlers."""

    org_id: uuid.UUID
    org_name: str


async def verify_api_key(request: Request) -> OrgContext:
    """FastAPI dependency that validates API key and returns OrgContext.

    Expects header: Authorization: Bearer rsk_<key>
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not auth_header.startswith("Bearer rsk_"):
        raise HTTPException(status_code=401, detail="Invalid API key format. Expected: Bearer rsk_<key>")

    raw_key = auth_header.removeprefix("Bearer ")
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    session_factory = get_session_factory(request.app)
    async with session_factory() as session:
        result = await session.execute(
            select(ApiKey, Organization)
            .join(Organization, ApiKey.org_id == Organization.id)
            .where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)  # noqa: E712
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")

        _api_key, org = row
        return OrgContext(org_id=org.id, org_name=org.name)
