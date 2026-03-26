"""Pydantic request/response schemas for admin endpoints (S616.2).

Organizations, members, API keys, and licenses — all in one file.
~15 schemas, not enough to justify per-resource files (D2).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# --- Organizations ---


class CreateOrganizationRequest(BaseModel):
    """POST /organizations request body."""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=63, pattern=r"^[a-z0-9-]+$")


class PatchOrganizationRequest(BaseModel):
    """PATCH /organizations/{id} request body."""

    name: str | None = Field(None, min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    """Organization in API responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime


# --- Members ---


class CreateMemberRequest(BaseModel):
    """POST /organizations/{id}/members request body."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    role: Literal["admin", "member"] = "member"


class PatchMemberRequest(BaseModel):
    """PATCH /organizations/{id}/members/{mid} request body."""

    role: Literal["admin", "member"]


class MemberResponse(BaseModel):
    """Member in API responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime


class MemberCreatedResponse(MemberResponse):
    """POST /members response — includes auto-created API key (shown once)."""

    api_key: str


# --- API Keys ---


class CreateApiKeyRequest(BaseModel):
    """POST /organizations/{id}/api-keys request body."""

    member_id: uuid.UUID
    scopes: list[str] = Field(default_factory=lambda: ["full_access"])


class ApiKeyCreatedResponse(BaseModel):
    """POST /api-keys response — raw key shown once."""

    id: uuid.UUID
    key: str
    prefix: str
    scopes: list[str]
    created_at: datetime


class ApiKeyResponse(BaseModel):
    """GET /api-keys response — no raw key, ever."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    member_id: uuid.UUID
    prefix: str
    scopes: list[str]
    last_used_at: datetime | None
    is_active: bool
    created_at: datetime


# --- Licenses ---


class CreateLicenseRequest(BaseModel):
    """POST /organizations/{id}/license request body."""

    plan: Literal["pro", "team", "enterprise"]
    features: list[str]
    seats: int = Field(ge=1)
    expires_at: datetime


class LicenseResponse(BaseModel):
    """License in API responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    org_id: uuid.UUID
    plan: str
    features: list[str]
    seats: int
    status: str
    expires_at: datetime
    created_at: datetime
