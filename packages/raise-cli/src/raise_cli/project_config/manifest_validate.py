"""Manifest project.* key validation — ADR-071 known-key set.

Validates the project.* section of .raise/manifest.yaml against the locked set
of keys defined in ADR-071. Unknown keys are reported as errors so typos are
caught before they silently degrade tier-2 fallbacks or tier-3 gates.

Design: walk the raw YAML dict (not Pydantic model_validate) so validation is
independent of the normal load path, which uses extra='ignore' to stay resilient.

Moved from onboarding/manifest_validate.py in RAISE-16419 S4.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import yaml

from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir

_ProjectDict = Mapping[str, object]

# Locked set of valid dotted paths in the project.* section.
# Includes both existing ProjectInfo flat keys and ADR-071 tier-2/tier-3 keys.
KNOWN_PROJECT_KEY_PATHS: frozenset[str] = frozenset(
    {
        # Existing ProjectInfo flat keys
        "name",
        "project_type",
        "language",
        "test_command",
        "lint_command",
        "type_check_command",
        "format_command",
        "code_file_count",
        "detected_at",
        "apps",
        # ADR-071 Tier 2 — fallback-on-missing
        "code.root_glob",
        "schema.file",
        "learnings_dir",
        # ADR-071 Tier 3 — skip-on-absence
        "docs.product.primary_dir",
        "docs.product.translations_dir",
        "docs.product.parity_check",
        "docs.developer.modules_dir",
        "governance.drift_catalog",
        "governance.drift_hotspots",
        "governance.adrs_dir",
        # Portfolio — opaque map (RAISE-15251)
        "portfolio.component_paths",
    }
)

# Dotted paths whose dict values must NOT be recursed into.
# The path itself is the leaf — its nested keys are schema-defined sub-structure,
# not arbitrary project.* extension points (RAISE-15251).
_OPAQUE_MAP_PATHS: frozenset[str] = frozenset({"portfolio.component_paths"})


def walk_project_keys(d: _ProjectDict, prefix: str = "") -> list[str]:
    """DFS walk of a dict, returning all dotted leaf-key paths.

    Lists are treated as leaves (not recursed into) — their parent key is the
    leaf path. Dict values at paths in ``_OPAQUE_MAP_PATHS`` are also treated
    as leaves — the dict IS the value, not a namespace to recurse into.
    This matches the validation contract: we validate key paths, not
    the schema of list items or opaque sub-maps (Pydantic handles that on
    model_validate).
    """
    paths: list[str] = []
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and path not in _OPAQUE_MAP_PATHS:
            paths.extend(walk_project_keys(v, path))  # type: ignore[arg-type]
        else:
            paths.append(path)
    return paths


def validate_manifest_project_keys(
    project_root: Path,
) -> tuple[list[str], int, str | None]:
    """Validate project.* keys in the manifest against the ADR-071 known set.

    Returns (unknown_paths, total_count, parse_error) in a single YAML read:
    - unknown_paths: dotted key paths not in KNOWN_PROJECT_KEY_PATHS ([] = clean)
    - total_count: total project.* leaf paths found (0 = no project section)
    - parse_error: human-readable message when YAML cannot be parsed, else None

    Returns ([], 0, None) when manifest is absent or has no project section.
    Returns ([], 0, "<msg>") when the manifest exists but cannot be parsed.
    """
    manifest_path = get_raise_dir(project_root) / MANIFEST_FILE
    if not manifest_path.exists():
        return [], 0, None

    try:
        data: object = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [], 0, str(exc)

    if not isinstance(data, dict):
        return [], 0, None

    raw: _ProjectDict = data  # type: ignore[assignment]
    project_section = raw.get("project")
    if not isinstance(project_section, dict):
        return [], 0, None

    project_dict: _ProjectDict = project_section  # type: ignore[assignment]
    all_paths = walk_project_keys(project_dict)
    unknown = [p for p in all_paths if p not in KNOWN_PROJECT_KEY_PATHS]
    return unknown, len(all_paths), None
