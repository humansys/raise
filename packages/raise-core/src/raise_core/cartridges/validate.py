"""Cartridge validation — schema, file integrity, dependency checks."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

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


def validate_cartridge(
    cartridge_dir: Path,
    installed_cartridges: list[str] | None = None,
) -> ValidationResult:
    """Validate a cartridge directory for correctness."""
    manifest, errors = _load_manifest(cartridge_dir)
    if errors or manifest is None:
        return ValidationResult(valid=False, errors=errors, warnings=[])

    warnings = _check_integrity(cartridge_dir, manifest, installed_cartridges)

    return ValidationResult(valid=True, errors=[], warnings=warnings)
