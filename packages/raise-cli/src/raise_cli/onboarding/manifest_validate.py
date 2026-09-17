"""Manifest project.* key validation — thin re-export shim (RAISE-16419 S4).

Canonical implementation moved to project_config/manifest_validate.py.
This shim preserves backward compatibility for T1/T2 callers.
"""

from __future__ import annotations

from raise_cli.project_config.manifest_validate import (
    KNOWN_PROJECT_KEY_PATHS,
    validate_manifest_project_keys,
    walk_project_keys,
)

__all__ = [
    "KNOWN_PROJECT_KEY_PATHS",
    "validate_manifest_project_keys",
    "walk_project_keys",
]
