"""Cartridge validation — schema, file integrity, dependency checks."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from raise_core.cartridges.extract import (
    ExtractorConfig,
    RelationshipSchemaError,
    load_relationship_schema,
)
from raise_core.cartridges.loader import CARTRIDGE_YAML
from raise_core.cartridges.models import CartridgeManifest

_EXPECTED_DIRS = ("schema", "extractors", "instances", "skills")


class ValidationResult(BaseModel):
    """Result of validating a cartridge."""

    valid: bool
    errors: list[str]
    warnings: list[str]


def _load_manifest(
    cartridge_dir: Path,
) -> tuple[CartridgeManifest | None, list[str]]:
    """Load and validate manifest, returning errors if any."""
    manifest_path = cartridge_dir / CARTRIDGE_YAML
    if not manifest_path.exists():
        return None, [f"CARTRIDGE.yaml not found in {cartridge_dir}"]

    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"Invalid YAML syntax: {exc}"]

    try:
        manifest = CartridgeManifest.model_validate(raw)
    except ValidationError as exc:
        return None, [f"Manifest validation failed: {exc}"]

    return manifest, []


def _check_integrity(
    cartridge_dir: Path,
    manifest: CartridgeManifest,
    installed_cartridges: list[str] | None,
) -> list[str]:
    """Check file/directory integrity and dependencies. Returns warnings."""
    warnings: list[str] = []

    for dir_name in _EXPECTED_DIRS:
        if not (cartridge_dir / dir_name).is_dir():
            warnings.append(f"Expected directory '{dir_name}/' not found")

    project_root = cartridge_dir.parents[1] if cartridge_dir.parents else cartridge_dir
    for corpus_path in manifest.corpus:
        has_wildcard = any(c in corpus_path for c in "*?[")
        if has_wildcard:
            if not list(cartridge_dir.glob(corpus_path)) and not list(
                project_root.glob(corpus_path)
            ):
                warnings.append(f"No files match corpus pattern '{corpus_path}'")
        elif (
            not (cartridge_dir / corpus_path).exists()
            and not (project_root / corpus_path).exists()
        ):
            warnings.append(f"Corpus file '{corpus_path}' not found")

    if manifest.dependencies and installed_cartridges is not None:
        for dep in manifest.dependencies:
            if dep.name not in installed_cartridges:
                warnings.append(
                    f"Dependency '{dep.name}' ({dep.version}) not installed"
                )

    return warnings


def _check_relationship_schemas(cartridge_dir: Path) -> tuple[list[str], list[str]]:
    """Parse every declared relationship schema_ref. Returns (errors, warnings).

    RAISE-15999 F4: this is the natural enforcement point — it already runs
    on every cartridge command via ``_run_integrity_check`` — so a malformed
    schema_ref fails the gate here, loudly and before any extraction or
    relate pass runs, instead of degrading into a silent zero-relationship
    no-op several steps downstream. A declared-but-absent schema file is a
    warning, not an error: the file may legitimately not exist yet, but the
    gate must still name it (R5) rather than let the run end in a silent
    "Attached 0", exit 0.
    """
    errors: list[str] = []
    warnings: list[str] = []
    config_path = cartridge_dir / "extractors" / "config.yaml"
    try:
        config = ExtractorConfig.from_yaml(config_path)
    except ValidationError as exc:
        # R3: the gate's job is structured diagnostics — a malformed
        # config.yaml must not escape as a raw pydantic traceback.
        return [f"Invalid extractor config {config_path}: {exc}"], warnings
    for spec in config.extractors:
        if spec.schema_ref is None:
            continue
        if not (cartridge_dir / spec.schema_ref).exists():
            warnings.append(
                f"Extractor '{spec.name}' declares schema_ref "
                f"'{spec.schema_ref}' but the file does not exist"
            )
            continue
        try:
            load_relationship_schema(spec, cartridge_dir)
        except RelationshipSchemaError as exc:
            errors.append(str(exc))
    return errors, warnings


def validate_cartridge(
    cartridge_dir: Path,
    installed_cartridges: list[str] | None = None,
) -> ValidationResult:
    """Validate a cartridge directory for correctness."""
    manifest, errors = _load_manifest(cartridge_dir)
    if errors or manifest is None:
        return ValidationResult(valid=False, errors=errors, warnings=[])

    errors, schema_warnings = _check_relationship_schemas(cartridge_dir)
    warnings = _check_integrity(cartridge_dir, manifest, installed_cartridges)
    warnings.extend(schema_warnings)

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
