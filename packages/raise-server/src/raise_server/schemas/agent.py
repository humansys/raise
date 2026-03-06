"""Pydantic models for agent telemetry endpoints."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

_MAX_PAYLOAD_BYTES = 102_400  # 100 KB


class AgentEventCreate(BaseModel):
    """Incoming telemetry event from a Rovo agent or CLI."""

    event_type: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_payload_size(self) -> AgentEventCreate:
        if len(json.dumps(self.payload)) > _MAX_PAYLOAD_BYTES:
            msg = f"payload exceeds {_MAX_PAYLOAD_BYTES} bytes"
            raise ValueError(msg)
        return self


class AgentEventResponse(BaseModel):
    """Response after recording an event."""

    id: uuid.UUID
    status: str = "ok"


class AgentEventItem(BaseModel):
    """Single event in a list response."""

    id: uuid.UUID
    event_type: str
    payload: dict[str, Any]
    created_at: datetime


class AgentEventListResponse(BaseModel):
    """Paginated list of telemetry events."""

    events: list[AgentEventItem]
    count: int
