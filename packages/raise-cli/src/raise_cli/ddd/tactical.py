"""DDD tactical type schema — TacticalType enum and TacticalClassification model.

Defines the seven DDD tactical patterns used in Pass 3 (tactical classification).
This module is the output schema for the prompt; persistence concerns belong to
the Pass 3 runner story (out of scope here).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, field_validator


class TacticalType(StrEnum):
    """The seven DDD tactical patterns.

    Uses StrEnum (consistent with RunStatus, DelegationLevel, DiscoveryStatus)
    so that JSON serialization uses the string value directly without .value.
    """

    entity = "entity"
    value_object = "value_object"
    domain_service = "domain_service"
    domain_event = "domain_event"
    aggregate_root = "aggregate_root"
    factory = "factory"
    repository_interface = "repository_interface"


class TacticalClassification(BaseModel):
    """Output schema for a single tactical DDD classification result.

    Produced by the Pass 3 tactical classification prompt.
    Does NOT include ddd_source or ddd_content_hash — those are persistence
    layer concerns handled in a later story.
    """

    symbol_id: str
    tactical_type: TacticalType
    confidence: float
    rationale: str

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: float) -> float:
        """Clamp confidence to [0.0, 1.0] (mirrors ClassificationResult pattern)."""
        return max(0.0, min(1.0, v))
