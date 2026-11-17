"""Cartridge loading, discovery, and scaffolding."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel, ValidationError

from raise_core.cartridges.models import CartridgeManifest, GateConfig

if TYPE_CHECKING:
    from raise_core.cartridges.models import SchemaRef

logger = logging.getLogger(__name__)

CARTRIDGE_YAML = "CARTRIDGE.yaml"


class CartridgeConfigError(Exception):
    """Raised when a cartridge configuration is invalid."""


def load_cartridge(cartridge_dir: Path) -> tuple[CartridgeManifest, GateConfig]:
    """Load a cartridge manifest and build a GateConfig from it.

    Raises:
        CartridgeConfigError: If CARTRIDGE.yaml is missing, schema can't load, etc.
    """
    manifest_path = cartridge_dir / CARTRIDGE_YAML
    if not manifest_path.exists():
        msg = f"CARTRIDGE.yaml not found in {cartridge_dir}"
        raise CartridgeConfigError(msg)

    raw: Any = yaml.safe_load(manifest_path.read_text())
    try:
        manifest = CartridgeManifest.model_validate(raw)
    except ValidationError as exc:
        msg = f"Invalid CARTRIDGE.yaml in {cartridge_dir}: {exc}"
        raise CartridgeConfigError(msg) from exc

    model_cls = _resolve_schema(manifest)
    node_dir = _resolve_node_dir(cartridge_dir)

    cq_file: Path | None = None
    if manifest.competency_questions:
        cq_path = cartridge_dir / manifest.competency_questions
        if cq_path.exists():
            cq_file = cq_path

    config = GateConfig(
        node_model=model_cls,
        cq_file=cq_file,
        cq_threshold=manifest.thresholds.get("cq_coverage", 80.0),
        required_types=manifest.required_types,
        node_dir=node_dir,
        domain_dir=cartridge_dir,
    )
    return manifest, config


def discover_cartridges(
    base_dir: Path,
) -> list[tuple[CartridgeManifest, GateConfig]]:
    """Discover all valid cartridges under base_dir.

    Skips directories that don't have a valid CARTRIDGE.yaml.
    """
    if not base_dir.exists():
        return []

    results: list[tuple[CartridgeManifest, GateConfig]] = []
    for entry in sorted(base_dir.iterdir()):
        if not entry.is_dir():
            continue
        try:
            pair = load_cartridge(entry)
            results.append(pair)
        except CartridgeConfigError:
            logger.debug("Skipping %s: invalid cartridge", entry.name)
    return results


def scaffold_cartridge(
    base_dir: Path,
    cartridge_name: str,
    corpus_paths: list[str] | None = None,
    node_schema: tuple[str, str] | None = None,
) -> Path:
    """Create a new cartridge directory with ADR-083 structure.

    ``node_schema`` is an optional ``(module, class_name)`` for the manifest
    schema. When omitted it defaults to the canonical ``GraphNode`` model so
    ``build``/``extract`` work immediately with no manual manifest edit
    (RAISE-11617); callers needing a custom schema pass ``node_schema`` to
    override it.

    Raises:
        CartridgeConfigError: If cartridge directory already exists with a manifest.
    """
    cartridge_dir = base_dir / cartridge_name

    if cartridge_dir.exists() and (cartridge_dir / CARTRIDGE_YAML).exists():
        msg = f"Cartridge '{cartridge_name}' already exists at {cartridge_dir}"
        raise CartridgeConfigError(msg)

    cartridge_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ("schema", "extractors", "instances", "skills"):
        (cartridge_dir / subdir).mkdir(exist_ok=True)

    schema_module, schema_class = node_schema or (
        "raise_core.graph.models",
        "GraphNode",
    )
    manifest = {
        "name": cartridge_name,
        "display_name": cartridge_name.replace("-", " ").replace("_", " ").title(),
        "version": "0.1.0",
        "author": "",
        "license": "",
        "tier": "open",
        "namespace": cartridge_name,
        "description": "",
        "source": {
            "type": "curated",
            "authority": "local",
        },
        "schema": {
            "module": schema_module,
            "class_name": schema_class,
        },
        "corpus": corpus_paths or [],
        "competency_questions": None,
        "thresholds": {"cq_coverage": 80.0},
        "required_types": [],
    }

    (cartridge_dir / CARTRIDGE_YAML).write_text(
        yaml.dump(
            manifest, default_flow_style=False, sort_keys=False, allow_unicode=True
        )
    )

    return cartridge_dir


def resolve_adapter(manifest: CartridgeManifest) -> Any:
    """Resolve and instantiate the retrieval adapter for a manifest.

    Raises:
        CartridgeConfigError: If no retrieval config or import fails.
    """
    if manifest.retrieval is None:
        msg = f"No retrieval config for cartridge '{manifest.name}'"
        raise CartridgeConfigError(msg)

    cls = _resolve_class(manifest.retrieval.adapter, manifest.name, "adapter")
    try:
        return cls()
    except Exception as exc:
        msg = (
            f"Cannot instantiate adapter '{manifest.retrieval.adapter.class_name}' "
            f"for cartridge '{manifest.name}': {exc}"
        )
        raise CartridgeConfigError(msg) from exc


def resolve_builder(manifest: CartridgeManifest) -> Any:
    """Resolve and instantiate the GraphBuilder for a manifest.

    Raises:
        CartridgeConfigError: If no retrieval config or import fails.
    """
    if manifest.retrieval is None:
        msg = f"No retrieval config for cartridge '{manifest.name}'"
        raise CartridgeConfigError(msg)

    cls = _resolve_class(manifest.retrieval.builder, manifest.name, "builder")
    try:
        return cls()
    except Exception as exc:
        msg = (
            f"Cannot instantiate builder '{manifest.retrieval.builder.class_name}' "
            f"for cartridge '{manifest.name}': {exc}"
        )
        raise CartridgeConfigError(msg) from exc


def _resolve_class(ref: SchemaRef, cartridge_name: str, role: str) -> Any:
    """Dynamically import a class from a SchemaRef."""
    try:
        mod = importlib.import_module(ref.module)
    except ImportError as exc:
        msg = (
            f"Cannot import {role} module '{ref.module}' "
            f"for cartridge '{cartridge_name}': {exc}"
        )
        raise CartridgeConfigError(msg) from exc

    cls: Any = getattr(mod, ref.class_name, None)
    if cls is None:
        msg = (
            f"Class '{ref.class_name}' not found "
            f"in module '{ref.module}' (role: {role})"
        )
        raise CartridgeConfigError(msg)

    return cls


def _resolve_schema(manifest: CartridgeManifest) -> type[BaseModel]:
    """Import the schema model class from the manifest reference."""
    schema_ref = manifest.node_schema
    try:
        mod = importlib.import_module(schema_ref.module)
    except ImportError as exc:
        msg = (
            f"Cannot import schema module '{schema_ref.module}' "
            f"for cartridge '{manifest.name}': {exc}"
        )
        raise CartridgeConfigError(msg) from exc

    cls: Any = getattr(mod, schema_ref.class_name, None)
    if cls is None:
        msg = (
            f"Class '{schema_ref.class_name}' not found in module '{schema_ref.module}'"
        )
        raise CartridgeConfigError(msg)

    if not (isinstance(cls, type) and issubclass(cls, BaseModel)):
        msg = (
            f"'{schema_ref.class_name}' in '{schema_ref.module}' "
            f"is not a Pydantic BaseModel (got {type(cls).__name__})"
        )
        raise CartridgeConfigError(msg)

    return cls


def _resolve_node_dir(cartridge_dir: Path) -> Path:
    """Determine the node directory: instances/ (preferred), curated/, or extracted/."""
    instances = cartridge_dir / "instances"
    curated = cartridge_dir / "curated"
    extracted = cartridge_dir / "extracted"

    if instances.exists() and any(instances.rglob("*.yaml")):
        return instances
    if curated.exists() and any(curated.rglob("*.yaml")):
        return curated
    if extracted.exists():
        return extracted
    return instances


__all__ = [
    "CARTRIDGE_YAML",
    "CartridgeConfigError",
    "discover_cartridges",
    "load_cartridge",
    "resolve_adapter",
    "resolve_builder",
    "scaffold_cartridge",
]
