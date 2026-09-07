"""Pydantic schemas mirroring the server AgentEventCreate contract (ADR-046).

Bridge fields (`event_id`, `schema_version`) are CLI-side additions per ADR-048
for idempotent replay (S2.3 retry, S2.6 backfill) and forward compatibility.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = 1

# Mirror of raise_server.schemas.agent._MAX_PAYLOAD_BYTES (100 KiB = 102_400).
# Kept literal-coupled: if the server relaxes/tightens the limit, update here
# in the same change. S2.7 contract test will assert both stay in lockstep.
MAX_PAYLOAD_BYTES = 102_400

WorkEventType = Literal[
    "pipeline_phase_completed",
    "session_started",
    "session_closed",
    "session_topic",
    "artifact_created",
    "gate_checked",
    "story_started",
    "story_closed",
    "work_lifecycle",
    "token_usage",
    "token_usage_daily",
    "story_cost_summary",  # S6456.2 — aggregated cost per story at close
    "phase_finish",  # S9115.3 — per-phase telemetry at advance
    "tool_cost",  # S16430.2 — multi-tool cost ingestion (Copilot, Cursor, ...)
    "governance_audit",  # RAISE-16691 S16430.3 — gate/HITL decision audit trail
]


class AgentEventCreate(BaseModel):
    """Server-bound work event. Mirrors `raise_server.schemas.agent.AgentEventCreate`."""

    event_type: WorkEventType
    payload: dict[str, Any] = Field(default_factory=dict)
    work_item_ref: str | None = Field(default=None, max_length=255)
    event_id: str = Field(min_length=16, max_length=16)
    session_id: str | None = Field(default=None, max_length=64)
    schema_version: int = Field(default=SCHEMA_VERSION, ge=1)

    @model_validator(mode="after")
    def _check_payload_size(self) -> AgentEventCreate:
        if len(json.dumps(self.payload)) > MAX_PAYLOAD_BYTES:
            msg = f"payload exceeds {MAX_PAYLOAD_BYTES} bytes"
            raise ValueError(msg)
        return self


class AgentEventResponse(BaseModel):
    """Parsed server response. Mirrors `raise_server.schemas.agent.AgentEventResponse`.

    `status` is intentionally unconstrained to match the server exactly —
    tight bounds would flag any future server-added status as false drift.
    """

    id: uuid.UUID
    status: str = "ok"


def make_event_id(
    *,
    event_type: str,
    work_item_ref: str | None,
    iso_timestamp: str,
    source_id: str,
) -> str:
    """Return a 16-hex deterministic event id (sha256 prefix).

    Same inputs produce the same id, enabling idempotent replay for backfill
    (S2.6) and retry (S2.3) without server-side duplicate rows.
    """
    raw = f"{event_type}|{work_item_ref or ''}|{iso_timestamp}|{source_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
