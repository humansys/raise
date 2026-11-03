"""EvidenceItem model for ISO 27001 compliance evidence.

Shared across all evidence extractors (git, gate, session).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EvidenceItem(BaseModel):
    """A single piece of ISO 27001 compliance evidence.

    Attributes:
        control_id: ISO 27001 control identifier (e.g., "A.8.32").
        control_name: Short control name.
        evidence_type: Source category of this evidence.
        title: Brief summary of the evidence item.
        description: Detailed description of what this evidence demonstrates.
        timestamp: When the evidence was created/recorded.
        source_ref: Unique reference within the source (e.g., commit hash, gate ID).
        url: Optional URL linking to the evidence source.
    """

    model_config = ConfigDict(frozen=True)

    control_id: str
    control_name: str
    evidence_type: Literal["git", "gate", "session"]
    title: str
    description: str
    timestamp: datetime
    source_ref: str
    url: str | None = None
