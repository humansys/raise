"""Canonical domain model schema + path resolver.

RAISE-16801: Single source of truth for .raise/domain-model.yaml location.

Producer (ddd discover) and all consumers (graph assign-bcs, clustering)
must use `get_domain_model_path()` rather than hardcoding a path.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

from raise_cli.ddd.tactical import TacticalType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

CANONICAL_PATH = ".raise/domain-model.yaml"
DRAFT_PATH = ".raise/domain-model.draft.yaml"
LEGACY_PATH = "governance/architecture/domain-model.yaml"

# ---------------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------------


class BoundedContext(BaseModel):
    """A single Bounded Context definition in domain-model.yaml.

    ``terms`` is a list of term objects from the domain vocabulary; each entry
    is a dict with at least a ``name`` key and optionally ``definition`` and
    ``aliases``.  Using ``dict[str, Any]`` preserves the YAML schema used in
    existing domain-model.yaml files.
    """

    name: str
    description: str = ""
    modules: list[str] = []
    terms: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# RAISE-16851: DDD convergence block (D1, ADR-148)
# ---------------------------------------------------------------------------


class DDDModuleDecision(BaseModel):
    """A human DDD decision for an entire module.

    ``layer`` must be ``"D"`` (Domain) or ``"I"`` (Infrastructure).
    Unknown values fail at load time so YAML drift is caught early.
    """

    module: str
    layer: Literal["D", "I"]
    reasoning: str = ""


class DDDSymbolRatification(BaseModel):
    """A human ratification of a single symbol's DDD classification.

    Ratified symbols are never reclassified by LLM (authority = ratified,
    rank 50 in the authority ladder — see RAISE-16850 / ADR-148 D3).

    RAISE-16917 (D4): ``tactical_type`` is optional — existing YAML files without
    this field continue to parse correctly (Pydantic sets it to None).
    """

    symbol: str
    layer: Literal["D", "I"]
    tactical_type: TacticalType | None = None  # RAISE-16917 D4
    ratified_by: str
    ratified_at: str  # ISO date YYYY-MM-DD


class DDDBlock(BaseModel):
    """Container for human DDD decisions stored in domain-model.yaml.

    Both ``modules`` and ``ratified`` default to empty lists so that
    domain-model.yaml files without a ``ddd:`` key remain valid (backward
    compatibility).
    """

    modules: list[DDDModuleDecision] = Field(default_factory=list)
    ratified: list[DDDSymbolRatification] = Field(default_factory=list)


class DomainModel(BaseModel):
    """Root schema for domain-model.yaml."""

    version: str = "1"
    bounded_contexts: list[BoundedContext]
    ratified_by: str = ""
    ratified_at: str = ""
    ddd: DDDBlock = Field(default_factory=DDDBlock)


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


def get_domain_model_path(project_root: Path) -> Path:
    """Return the path to domain-model.yaml for *project_root*.

    Resolution order:
    1. ``<project_root>/.raise/domain-model.yaml`` (canonical) — returned if it
       exists, or returned as the non-existent default so callers get a
       consistent ``FileNotFoundError`` on read.
    2. ``<project_root>/governance/architecture/domain-model.yaml`` (legacy) —
       returned with a ``WARNING`` when canonical is absent.  Move the file to
       the canonical path to silence the warning.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        Path to the domain-model.yaml file (may not exist — check with
        ``path.exists()`` before reading when presence is not guaranteed).
    """
    project_root = project_root.resolve()
    canonical = project_root / CANONICAL_PATH
    if canonical.exists():
        return canonical

    legacy = project_root / LEGACY_PATH
    if legacy.exists():
        logger.warning(
            "domain-model.yaml found at legacy path %s; move to %s to silence this warning",
            legacy,
            canonical,
        )
        return legacy

    # Neither exists — return canonical so callers see a consistent path
    return canonical


def get_domain_model_draft_path(project_root: Path) -> Path:
    """Return the draft output path for ``rai ddd discover``.

    RAISE-16895: ``rai ddd discover`` writes to this path by default so that
    it never silently overwrites a human-authored BC catalog at the canonical
    path.  The draft can be promoted to canonical manually or via
    ``--out .raise/domain-model.yaml``.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        ``<project_root>/.raise/domain-model.draft.yaml`` (may not exist).
    """
    return project_root.resolve() / DRAFT_PATH


# ---------------------------------------------------------------------------
# RAISE-16788: Loader + prompt serialiser
# ---------------------------------------------------------------------------


def load_domain_model(path: Path) -> DomainModel:
    """Load and validate domain-model.yaml at *path*.

    Args:
        path: Absolute path to the domain-model.yaml file.

    Returns:
        A validated :class:`DomainModel` instance.

    Raises:
        SystemExit or click.exceptions.Exit: Via
            :func:`raise_cli.cli.error_handler.cli_error` on FileNotFoundError,
            YAML parse error, Pydantic ValidationError, or empty
            ``bounded_contexts``.
    """
    # Import here to avoid circular import at module load (graph.py imports
    # domain_model.py at the top level; error_handler imports nothing from ddd).
    from raise_cli.cli.error_handler import cli_error

    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        cli_error(
            f"domain-model.yaml not found: {path}",
            hint="Run 'rai ddd discover' to generate a domain model first",
            exit_code=2,
        )
        raise  # unreachable — cli_error raises SystemExit; satisfies pyright

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        cli_error(
            f"Invalid YAML in domain-model.yaml: {exc}",
            hint="Fix the YAML syntax in the domain-model file",
            exit_code=2,
        )
        raise

    try:
        model = DomainModel.model_validate(data)
    except ValidationError as exc:
        cli_error(
            f"domain-model.yaml does not match schema: {exc}",
            hint="Ensure bounded_contexts is a valid list of BC objects",
            exit_code=2,
        )
        raise

    if not model.bounded_contexts:
        cli_error(
            "domain-model.yaml has no bounded_contexts",
            hint="Add at least one bounded context before using --context in classify",
            exit_code=2,
        )
        raise SystemExit(2)  # unreachable; satisfies pyright

    return model


# ---------------------------------------------------------------------------
# RAISE-16881: BC catalog coverage check
# ---------------------------------------------------------------------------


class CoverageResult(BaseModel):
    """Result of a BC catalog coverage check against graph modules.

    Attributes:
        ratio: Fraction of graph modules covered by the BC catalog (0.0–1.0).
        covered: Module names present in both the catalog and the graph.
        uncovered: Module names present in the graph but absent from the catalog.
        modules_in_graph: All unique module names found in the graph symbols.
    """

    ratio: float
    covered: set[str]
    uncovered: set[str]
    modules_in_graph: set[str]


def compute_catalog_coverage(
    symbols: list[Any],
    domain_model: DomainModel,
) -> CoverageResult:
    """Compute how well the BC catalog covers the modules present in the graph.

    Args:
        symbols: List of SymbolNode objects (duck-typed: ``metadata`` dict with
            optional ``"module"`` key).
        domain_model: Validated :class:`DomainModel` instance.

    Returns:
        :class:`CoverageResult` with ratio, covered, uncovered, and
        modules_in_graph sets.

    The ratio is ``|covered| / |modules_in_graph|``.  When the graph has no
    modules (empty *symbols* or all symbols lack a ``"module"`` key), ratio
    is ``1.0`` — there is nothing to cover, so the check passes trivially.
    """
    modules_in_catalog: set[str] = {
        mod for bc in domain_model.bounded_contexts for mod in bc.modules
    }
    modules_in_graph: set[str] = {
        mod for sym in symbols if (mod := sym.metadata.get("module", ""))
    }

    if not modules_in_graph:
        return CoverageResult(
            ratio=1.0,
            covered=set(),
            uncovered=set(),
            modules_in_graph=set(),
        )

    covered = modules_in_catalog & modules_in_graph
    uncovered = modules_in_graph - modules_in_catalog
    ratio = len(covered) / len(modules_in_graph)

    return CoverageResult(
        ratio=ratio,
        covered=covered,
        uncovered=uncovered,
        modules_in_graph=modules_in_graph,
    )


def domain_model_to_prompt_context(model: DomainModel) -> str:
    """Serialise BC → module hints as a prompt-injection string for Pass 1.

    Each module in each BC produces one line::

        - Module `{mod}` belongs to bounded context `{bc.name}` — {bc.description}

    The description suffix (`` — {desc}``) is omitted when ``bc.description``
    is empty.  BCs with no modules are skipped.  Model order is preserved so
    output is deterministic.

    Args:
        model: Validated :class:`DomainModel` instance.

    Returns:
        A newline-joined hint string, or ``""`` when no BC has any modules.
    """
    lines: list[str] = []
    for bc in model.bounded_contexts:
        if not bc.modules:
            continue
        suffix = f" — {bc.description}" if bc.description else ""
        for mod in bc.modules:
            lines.append(
                f"- Module `{mod}` belongs to bounded context `{bc.name}`{suffix}"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# RAISE-16851: save_domain_model
# ---------------------------------------------------------------------------


def save_domain_model(model: DomainModel, path: Path) -> None:
    """Serialize *model* back to YAML at *path*.

    Writes a valid YAML file that round-trips through :func:`load_domain_model`.
    Empty ``ddd:`` blocks are omitted from the output to keep files readable.

    Args:
        model: Validated :class:`DomainModel` instance to serialize.
        path: Output path (parent directory must exist).
    """
    data: dict[str, Any] = {}

    if model.version and model.version != "1":
        data["version"] = model.version

    if model.ratified_by:
        data["ratified_by"] = model.ratified_by
    if model.ratified_at:
        data["ratified_at"] = model.ratified_at

    data["bounded_contexts"] = [_bc_to_dict(bc) for bc in model.bounded_contexts]

    # Write ddd: block only when non-empty
    if model.ddd.modules or model.ddd.ratified:
        data["ddd"] = _ddd_block_to_dict(model.ddd)

    path.write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _bc_to_dict(bc: BoundedContext) -> dict[str, Any]:
    """Convert a BoundedContext to a plain dict for YAML serialization."""
    d: dict[str, Any] = {"name": bc.name}
    if bc.description:
        d["description"] = bc.description
    if bc.modules:
        d["modules"] = list(bc.modules)
    if bc.terms:
        d["terms"] = [dict(t) for t in bc.terms]
    return d


def _ddd_block_to_dict(block: DDDBlock) -> dict[str, Any]:
    """Convert a DDDBlock to a plain dict for YAML serialization."""
    d: dict[str, Any] = {}
    if block.modules:
        d["modules"] = [
            {
                "module": m.module,
                "layer": m.layer,
                **({"reasoning": m.reasoning} if m.reasoning else {}),
            }
            for m in block.modules
        ]
    if block.ratified:
        ratified_entries: list[dict[str, Any]] = []
        for r in block.ratified:
            entry: dict[str, Any] = {
                "symbol": r.symbol,
                "layer": r.layer,
            }
            if r.tactical_type is not None:
                entry["tactical_type"] = str(r.tactical_type)
            entry["ratified_by"] = r.ratified_by
            entry["ratified_at"] = r.ratified_at
            ratified_entries.append(entry)
        d["ratified"] = ratified_entries
    return d
