"""Additive merge of detected project conventions into the manifest.

Conventions are applied non-destructively: only fields that are currently None
in the manifest are populated. Existing values are never overwritten (ADR-071 D7).
"""

from __future__ import annotations

from pathlib import Path

from raise_cli.onboarding.manifest import (
    ProjectCodeConfig,
    ProjectManifest,
    save_manifest,
)


def merge_project_conventions(
    manifest: ProjectManifest,
    conventions: dict[str, object],
    project_root: Path,
) -> bool:
    """Merge detected conventions into manifest non-destructively.

    Only adds keys where the manifest currently has None. Never overwrites
    existing values. Saves the updated manifest if any change was made.

    Args:
        manifest: Current project manifest.
        conventions: Dict from detect_project_conventions() — e.g.
            {"code": {"root_glob": "packages/*/src/"}}.
        project_root: Project root (for save_manifest).

    Returns:
        True if the manifest was modified and saved, False otherwise.
    """
    changed = False
    project = manifest.project

    code_conventions = conventions.get("code")
    if isinstance(code_conventions, dict):
        raw_root_glob: object = code_conventions.get("root_glob")
        root_glob = raw_root_glob if isinstance(raw_root_glob, str) else None
        if root_glob is not None and project.code is None:
            project = project.model_copy(
                update={"code": ProjectCodeConfig(root_glob=root_glob)}
            )
            changed = True

    if changed:
        updated = manifest.model_copy(update={"project": project})
        save_manifest(updated, project_root)

    return changed
