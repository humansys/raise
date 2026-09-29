"""Cartridge models — GateResult, GateConfig, CartridgeManifest.

GateResult and GateConfig re-exported from raise-core gates (S2674.6).
Cartridge-specific models (SchemaRef, CartridgeManifest, etc.) defined here.
ADR-083 fields added in S5875.1.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from raise_core.graph.gates.models import GateConfig, GateResult
from raise_core.graph.retrieval.engine import W_DOMAIN, W_SA

SourceType = Literal["curated", "derived"]
SourceAuthority = Literal["local", "remote"]
RefreshStrategy = Literal["manual", "signal", "cron"]


class SourceConfig(BaseModel):
    """Source type and authority for a cartridge (ADR-088)."""

    type: SourceType = "curated"
    authority: SourceAuthority = "local"
    generator: str | None = None
    refresh: RefreshStrategy = "manual"


class TemporalMetadata(BaseModel):
    """Temporal versioning for cartridge nodes (ADR-088)."""

    valid_from: datetime
    superseded_at: datetime | None = None
    superseded_by: str | None = None
    source_version: str | None = None


class SchemaRef(BaseModel):
    """Reference to a Pydantic model class for node validation."""

    module: str = "raise_core.graph.models"
    class_name: str = "GraphNode"


class PromptingConfig(BaseModel):
    """LLM prompting instructions for a cartridge."""

    system_context: str = ""
    response_format: str = ""


# Eval-only sem_alpha profile (S10230.3 landed α path). Renamed from
# RetrievalProfile to deconflict with the production-reaching B′
# RetrievalProfile(BaseModel) below — both named the same across two parallel
# S10230.3 implementations. This Literal tunes the eval HybridSemanticScorer
# blend only (never reaches production retrieval).
SemAlphaProfile = Literal["conceptual", "taxonomic", "technical"]

PROFILE_ALPHA: dict[SemAlphaProfile, float] = {
    "conceptual": 0.15,
    "taxonomic": 0.30,
    "technical": 0.50,
}


class RetrievalConfig(BaseModel):
    """Retrieval adapter, builder, and scoring profile for a cartridge."""

    adapter: SchemaRef = Field(default_factory=SchemaRef)
    builder: SchemaRef = Field(default_factory=SchemaRef)
    profile: SemAlphaProfile | None = None
    sem_alpha: float | None = Field(default=None, ge=0.0, le=1.0)

    def resolve_alpha(self) -> float | None:
        """Return explicit sem_alpha, or profile-mapped alpha, or None."""
        if self.sem_alpha is not None:
            return self.sem_alpha
        if self.profile is not None:
            return PROFILE_ALPHA[self.profile]
        return None


class CartridgeDependency(BaseModel):
    """Dependency on another cartridge (ADR-083)."""

    name: str
    version: str = "*"


class CartridgeRequires(BaseModel):
    """Runtime requirements for a cartridge (ADR-083)."""

    llm: str = "any"
    graph: str | None = None


class AIDisclosure(BaseModel):
    """AI generation disclosure per layer (ADR-083 legal framework)."""

    schema_pct: int = 0
    extractors_pct: int = 0
    instances_pct: int = 0
    human_review: bool = False


CartridgeTier = Literal["open", "community", "verified", "enterprise"]


class RetrievalProfile(BaseModel):
    """Per-cartridge composite weight override for retrieve() (S10230.3 B′).

    Declares per-domain tuning of the lexical/dense balance.
    Fields absent from CARTRIDGE.yaml default to the global engine constants.
    Floats validated to [0.0, 1.0]; out-of-range raises ValidationError.
    """

    w_attr: float = Field(..., ge=0.0, le=1.0, description="Attribute (lexical) weight")
    w_sem: float = Field(..., ge=0.0, le=1.0, description="Semantic (dense) weight")
    w_sa: float = Field(
        default=W_SA, ge=0.0, le=1.0, description="Structural-adjacency weight"
    )
    w_domain: float = Field(
        default=W_DOMAIN, ge=0.0, le=1.0, description="Domain-graph weight"
    )

    def to_weights(self) -> tuple[float, float, float, float]:
        """Composite weights tuple in retrieve()/composite_score order.

        Order matches ``composite_score`` and the engine default
        ``(W_SA, W_ATTR, W_DOMAIN, W_SEM)``. Canonical builder shared by every
        call site so the tuple order lives in exactly one place.
        """
        return (self.w_sa, self.w_attr, self.w_domain, self.w_sem)


class ReferenceConfig(BaseModel):
    """Config per-cartridge para materialización de reference edges (DA-6, S10328.1).

    Controla el threshold de calidad de nombres usados como targets en
    ``materialize_reference_edges``. Defaults conservadores compatibles con
    cartridges existentes que no declaran reference_config.
    """

    min_name_tokens: int = Field(default=2, ge=1)
    min_char_length: int = Field(default=5, ge=1)


class CartridgeManifest(BaseModel):
    """Manifest describing a knowledge cartridge — parsed from CARTRIDGE.yaml."""

    model_config = {"populate_by_name": True}

    # --- Original fields ---
    name: str
    display_name: str
    node_schema: SchemaRef = Field(default_factory=SchemaRef, validation_alias="schema")
    corpus: list[str] = Field(default_factory=list)
    competency_questions: str | None = None
    thresholds: dict[str, float] = Field(default_factory=lambda: {"cq_coverage": 80.0})
    required_types: set[str] = Field(default_factory=set)
    retrieval: RetrievalConfig | None = None
    prompting: PromptingConfig | None = None

    # --- ADR-088 fields ---
    source: SourceConfig = Field(default_factory=SourceConfig)

    # --- RAISE-13378: self-snapshot marker (consumer directive, not provenance) ---
    # A distinct top-level bool, not `source.type`: `source.type == "derived"` is
    # shared by governance/management-ontology/backlog cartridges, which must keep
    # being ingested. `snapshot` narrowly means "this cartridge is a snapshot of
    # the build graph itself — never re-ingest it".
    snapshot: bool = False

    # --- ADR-083 fields ---
    version: str = "0.0.0"
    author: str = ""
    license: str = ""
    tier: CartridgeTier = "open"
    namespace: str | None = None
    description: str = ""
    dependencies: list[CartridgeDependency] = Field(default_factory=list)
    requires: CartridgeRequires | None = None
    ai_disclosure: AIDisclosure | None = None

    # --- ADR-111 backlog cartridge fields ---
    org_id: str | None = None
    project_id: str | None = None
    schema_version: str | None = None
    valid_from: datetime | None = None
    superseded_at: datetime | None = None

    # --- S10230.3 B′ per-cartridge retrieval profile ---
    retrieval_profile: RetrievalProfile | None = None

    # --- S10328.1: configurable reference edge materialization (DA-6) ---
    reference_config: ReferenceConfig | None = None

    # --- RAISE-16241: --depth used for the build this snapshot came from,
    # so the collapse guard can tell a depth change from a real collapse ---
    symbol_depth: str | None = None


__all__ = [
    "AIDisclosure",
    "CartridgeDependency",
    "CartridgeManifest",
    "CartridgeRequires",
    "CartridgeTier",
    "GateConfig",
    "GateResult",
    "PROFILE_ALPHA",
    "PromptingConfig",
    "ReferenceConfig",
    "RetrievalConfig",
    "RetrievalProfile",
    "SchemaRef",
    "SourceConfig",
    "TemporalMetadata",
]
