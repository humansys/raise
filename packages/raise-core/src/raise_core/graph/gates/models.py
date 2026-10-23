"""Gate configuration and result models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class GateResult(BaseModel):
    """Result of running a single validation gate."""

    gate: str
    domain: str
    passed: bool
    metrics: dict[str, Any]
    errors: list[str]
    warnings: list[str]
    duration_ms: float


class GateConfig(BaseModel):
    """Runtime configuration for gates — derived from CartridgeManifest."""

    model_config = {"arbitrary_types_allowed": True}

    node_model: type[BaseModel]
    cq_file: Path | None = None
    cq_threshold: float = 80.0
    required_types: set[str] = Field(default_factory=set)
    node_dir: Path
    domain_dir: Path | None = None
