"""Branch resolution utilities — project_config tier (RAISE-16462).

Extracted from ``raise_cli.story.open_service`` so that both T2 service modules
and T3 domain modules can import without creating upward edges.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path


def resolve_dev_branch(project: Path) -> str:
    """Development branch from explicit environment or manifest configuration.

    ``RAISE_DEVELOPMENT_BRANCH`` lets CI delta gates compare against the actual
    merge-request target. Normal CLI usage remains manifest-driven.
    """
    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override
    with suppress(Exception):
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.development
    return "main"


def resolve_scm(project: Path) -> str | None:
    """SCM provider from explicit environment or manifest configuration.

    Same override chain as ``resolve_dev_branch``: env → manifest → default.
    Unlike the dev branch, the default is ``None`` — absence of a detected
    or configured SCM is not a guess (RAISE-16561).
    """
    override = os.environ.get("RAISE_SCM", "").strip()
    if override:
        return override
    with suppress(Exception):
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.scm
    return None


def resolve_merge_strategy(project: Path) -> str | None:
    """Merge strategy from explicit environment or manifest configuration.

    Same override chain as ``resolve_dev_branch``: env → manifest → default.
    Unlike the dev branch, the default is ``None`` — absence of a detected
    or configured merge strategy is not a guess (RAISE-16561).
    """
    override = os.environ.get("RAISE_MERGE_STRATEGY", "").strip()
    if override:
        return override
    with suppress(Exception):
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.merge_strategy
    return None
