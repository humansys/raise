"""Pydantic models for ISO 27001 control mapping configuration.

Defines the schema for mapping ISO 27001:2022 Annex A controls
to RaiSE evidence sources (git, gate, session).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class EvidenceSourceConfig(BaseModel):
    """Configuration for a single evidence source.

    Attributes:
        type: Evidence source category (git, gate, or session).
        extractor: Specific extractor within the source type.
        description: Human-readable description of what this source provides.
    """

    model_config = ConfigDict(frozen=True)

    type: Literal["git", "gate", "session"]
    extractor: str
    description: str


class ControlConfig(BaseModel):
    """Configuration for a single ISO 27001 control.

    Attributes:
        id: Control identifier (e.g., "A.8.32").
        name: Short control name.
        description: Full control description.
        evidence_sources: List of evidence sources mapped to this control.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str
    evidence_sources: list[EvidenceSourceConfig]


class ControlMapping(BaseModel):
    """Top-level mapping of ISO 27001 controls to evidence sources.

    Attributes:
        version: Schema version string.
        standard: Standard identifier (e.g., "ISO 27001:2022").
        controls: List of control configurations.
    """

    model_config = ConfigDict(frozen=True)

    version: str
    standard: str
    controls: list[ControlConfig]
