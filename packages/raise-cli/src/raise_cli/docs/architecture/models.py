"""Pydantic models for the Layer 2 architecture doc synthesis pipeline.

``SynthesisBundle`` is deliberately an **allowlist by construction**: its
field set IS the fingerprint allowlist (D-S5). Volatile graph fields such
as ``created``/``updated_at``/``rank``/``score``/``execution_time_ms`` are
never copied onto this model, so they cannot leak into the fingerprint —
a new volatile field added upstream fails closed (invisible here) rather
than silently re-triggering synthesis on every ``rai graph build``.

Architecture: ADR-146, S15884.2 design D-S3/D-S5.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SymbolSummary(BaseModel):
    """A single public-API symbol surfaced to the synthesis bundle.

    Deliberately narrow — name/kind/file only. Line numbers, signatures,
    and other churny detail are not part of the allowlist. ``name`` MUST
    be a bare identifier (e.g. ``"FilesystemGraphBackend"``), never the
    full signature a graph ``symbol`` node's ``content`` field actually
    carries in production (``raise_core.discovery.symbols`` sets
    ``content = signature or name``) — R4: bundle.py derives this from
    the node's ``id`` tail (``_bare_symbol_name``), not ``content``,
    specifically so a signature's ``[``/``]`` generics never leak in.
    """

    name: str
    kind: str = ""
    file: str = ""


class SynthesisBundle(BaseModel):
    """The complete, deterministic LLM input for one module doc.

    Every field here is allowlisted (D-S5): this model's schema *is* the
    fingerprint allowlist. Do not add ``created``, ``updated_at``, ``rank``,
    ``score``, ``execution_time_ms``, or absolute ``source_file`` paths —
    doing so would make ``fingerprint()`` unstable across `rai graph build`
    runs (AC5) and break idempotence (AC1).
    """

    module_id: str
    name: str
    purpose: str = ""
    depends_on: list[str] = Field(default_factory=list)
    depended_by: list[str] = Field(default_factory=list)
    public_api: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    code_imports: list[str] = Field(default_factory=list)
    code_exports: list[str] = Field(default_factory=list)
    code_components: int = 0
    symbols: list[SymbolSummary] = Field(default_factory=list)
    fingerprint: str = ""


class Region(BaseModel):
    """A parsed ``rai:auto`` region — one begin/end marker pair.

    Byte offsets are into the *original* document text and are used by the
    writer to splice in place (ADR-146 preservation guarantee) rather than
    re-serializing the whole document.
    """

    id: str
    generator: str = ""
    src: str = ""
    hash: str = ""
    begin_start: int
    begin_end: int
    end_start: int
    end_end: int
    body: str = ""


class RegionWriteResult(BaseModel):
    """Outcome of a single ``regions.write_region`` call.

    ``preview`` carries the would-be region block (begin marker + body +
    end marker) when the call was made with ``dry_run=True`` — the
    human-reviewable diff content for the ADR-025 HITL gate to inspect
    before a subsequent non-dry-run call commits it to disk (C3). Empty
    on a real (non-dry-run) write, and on an ``"unchanged"`` outcome
    either way (nothing would be written).
    """

    changed: bool
    action: str  # "inserted" | "replaced" | "unchanged"
    region_id: str
    path: str
    hash: str = ""
    message: str = ""
    preview: str = ""


class FreshnessVerdict(BaseModel):
    """Per-doc/per-region staleness verdict (D-S4, AC6)."""

    doc_path: str
    region_id: str
    fresh: bool
    stored_src: str = ""
    computed_src: str = ""
    message: str = ""
