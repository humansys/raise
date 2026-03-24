"""Domain loading, discovery, and scaffolding."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path  # noqa: TC003 — used at runtime
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel, ValidationError

from rai_agent.knowledge.models import DomainManifest, GateConfig

if TYPE_CHECKING:
    from rai_agent.knowledge.models import SchemaRef

logger = logging.getLogger(__name__)

DOMAIN_YAML = "domain.yaml"


class DomainConfigError(Exception):
    """Raised when a domain configuration is invalid."""


def load_domain(domain_dir: Path) -> tuple[DomainManifest, GateConfig]:
    """Load a domain manifest and build a GateConfig from it.

    Raises:
        DomainConfigError: If domain.yaml is missing, schema can't load, etc.
    """
    manifest_path = domain_dir / DOMAIN_YAML
    if not manifest_path.exists():
        msg = f"domain.yaml not found in {domain_dir}"
        raise DomainConfigError(msg)

    raw: Any = yaml.safe_load(manifest_path.read_text())
    try:
        manifest = DomainManifest.model_validate(raw)
    except ValidationError as exc:
        msg = f"Invalid domain.yaml in {domain_dir}: {exc}"
        raise DomainConfigError(msg) from exc

    # Dynamic import of schema model
    model_cls = _resolve_schema(manifest)

    # Determine node directory: prefer curated/ if it has files, else extracted/
    node_dir = _resolve_node_dir(domain_dir)

    # Build CQ file path
    cq_file: Path | None = None
    if manifest.competency_questions:
        cq_path = domain_dir / manifest.competency_questions
        if cq_path.exists():
            cq_file = cq_path

    config = GateConfig(
        node_model=model_cls,
        cq_file=cq_file,
        cq_threshold=manifest.thresholds.get("cq_coverage", 80.0),
        required_types=manifest.required_types,
        node_dir=node_dir,
        domain_dir=domain_dir,
    )
    return manifest, config


def discover_domains(
    base_dir: Path,
) -> list[tuple[DomainManifest, GateConfig]]:
    """Discover all valid domains under base_dir.

    Skips directories that don't have a valid domain.yaml.
    """
    if not base_dir.exists():
        return []

    results: list[tuple[DomainManifest, GateConfig]] = []
    for entry in sorted(base_dir.iterdir()):
        if not entry.is_dir():
            continue
        try:
            pair = load_domain(entry)
            results.append(pair)
        except DomainConfigError:
            logger.debug("Skipping %s: invalid domain", entry.name)
    return results


def scaffold_domain(
    base_dir: Path,
    domain_name: str,
    corpus_paths: list[str] | None = None,
) -> Path:
    """Create a new domain directory with template domain.yaml.

    Raises:
        DomainConfigError: If domain directory already exists with a manifest.
    """
    domain_dir = base_dir / domain_name

    if domain_dir.exists() and (domain_dir / DOMAIN_YAML).exists():
        msg = f"Domain '{domain_name}' already exists at {domain_dir}"
        raise DomainConfigError(msg)

    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "extracted").mkdir(exist_ok=True)
    (domain_dir / "curated").mkdir(exist_ok=True)

    manifest = {
        "name": domain_name,
        "display_name": domain_name.replace("-", " ").replace("_", " ").title(),
        "schema": {
            "module": "TODO",
            "class_name": "TODO",
        },
        "corpus": corpus_paths or [],
        "competency_questions": None,
        "thresholds": {"cq_coverage": 80.0},
        "required_types": [],
    }

    (domain_dir / DOMAIN_YAML).write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False,
                  allow_unicode=True)
    )

    return domain_dir


def _resolve_class(ref: SchemaRef, domain_name: str, role: str) -> Any:
    """Dynamically import a class from a SchemaRef.

    Args:
        ref: Module + class_name reference.
        domain_name: Domain name for error messages.
        role: Role description for error messages (e.g., 'adapter', 'builder').

    Returns:
        The imported class (not instantiated).

    Raises:
        DomainConfigError: If module or class cannot be found.
    """
    try:
        mod = importlib.import_module(ref.module)
    except ImportError as exc:
        msg = (
            f"Cannot import {role} module '{ref.module}' "
            f"for domain '{domain_name}': {exc}"
        )
        raise DomainConfigError(msg) from exc

    cls: Any = getattr(mod, ref.class_name, None)
    if cls is None:
        msg = (
            f"Class '{ref.class_name}' not found "
            f"in module '{ref.module}' (role: {role})"
        )
        raise DomainConfigError(msg)

    return cls


def resolve_adapter(manifest: DomainManifest) -> Any:
    """Resolve and instantiate the DomainAdapter for a manifest.

    Raises:
        DomainConfigError: If no retrieval config or import fails.
    """
    if manifest.retrieval is None:
        msg = f"No retrieval config for domain '{manifest.name}'"
        raise DomainConfigError(msg)

    cls = _resolve_class(manifest.retrieval.adapter, manifest.name, "adapter")
    return cls()


def resolve_builder(manifest: DomainManifest) -> Any:
    """Resolve and instantiate the GraphBuilder for a manifest.

    Raises:
        DomainConfigError: If no retrieval config or import fails.
    """
    if manifest.retrieval is None:
        msg = f"No retrieval config for domain '{manifest.name}'"
        raise DomainConfigError(msg)

    cls = _resolve_class(manifest.retrieval.builder, manifest.name, "builder")
    return cls()


def _resolve_schema(manifest: DomainManifest) -> type[BaseModel]:
    """Import the schema model class from the manifest reference."""
    schema_ref = manifest.node_schema
    try:
        mod = importlib.import_module(schema_ref.module)
    except ImportError as exc:
        msg = (
            f"Cannot import schema module '{schema_ref.module}' "
            f"for domain '{manifest.name}': {exc}"
        )
        raise DomainConfigError(msg) from exc

    cls: Any = getattr(mod, schema_ref.class_name, None)
    if cls is None:
        msg = (
            f"Class '{schema_ref.class_name}' not found "
            f"in module '{schema_ref.module}'"
        )
        raise DomainConfigError(msg)

    if not (isinstance(cls, type) and issubclass(cls, BaseModel)):
        msg = (
            f"'{schema_ref.class_name}' in '{schema_ref.module}' "
            f"is not a Pydantic BaseModel (got {type(cls).__name__})"  # type: ignore[union-attr]
        )
        raise DomainConfigError(msg)

    return cls  # type: ignore[return-value]


def _resolve_node_dir(domain_dir: Path) -> Path:
    """Determine the node directory: curated/ if it has files, else extracted/."""
    curated = domain_dir / "curated"
    extracted = domain_dir / "extracted"

    if curated.exists() and any(curated.rglob("*.yaml")):
        return curated
    if extracted.exists():
        return extracted
    return curated  # default to curated even if empty
