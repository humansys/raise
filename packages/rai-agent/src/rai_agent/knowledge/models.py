"""Knowledge domain models — GateResult, GateConfig, DomainManifest."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 — Pydantic needs Path at runtime
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


class SchemaRef(BaseModel):
    """Reference to a Pydantic model class for node validation."""

    module: str
    class_name: str


class PromptingConfig(BaseModel):
    """LLM prompting instructions for a knowledge domain."""

    system_context: str = ""
    response_format: str = ""


class RetrievalConfig(BaseModel):
    """Retrieval adapter and builder references for a knowledge domain."""

    adapter: SchemaRef
    builder: SchemaRef


class DomainManifest(BaseModel):
    """Manifest describing a knowledge domain — parsed from domain.yaml."""

    model_config = {"populate_by_name": True}

    name: str
    display_name: str
    node_schema: SchemaRef = Field(validation_alias="schema")
    corpus: list[str] = Field(default_factory=list)
    competency_questions: str | None = None
    thresholds: dict[str, float] = Field(default_factory=lambda: {"cq_coverage": 80.0})
    required_types: set[str] = Field(default_factory=set)
    retrieval: RetrievalConfig | None = None
    prompting: PromptingConfig | None = None


class GateConfig(BaseModel):
    """Runtime configuration for gates — derived from DomainManifest."""

    model_config = {"arbitrary_types_allowed": True}

    node_model: type[BaseModel]
    cq_file: Path | None = None
    cq_threshold: float = 80.0
    required_types: set[str] = Field(default_factory=set)
    node_dir: Path
    domain_dir: Path | None = None
