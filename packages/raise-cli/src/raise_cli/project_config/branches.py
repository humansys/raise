"""Branch resolution utilities — project_config tier (RAISE-16462).

Extracted from ``raise_cli.story.open_service`` so that both T2 service modules
and T3 domain modules can import without creating upward edges.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.project_config.manifest import ReleaseLine


def resolve_dev_branch(project: Path) -> str:
    """Development branch from explicit environment or manifest configuration.

    ``RAISE_DEVELOPMENT_BRANCH`` lets CI delta gates compare against the actual
    merge-request target. Normal CLI usage remains manifest-driven.
    """
    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override
    try:
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.development
    except FileNotFoundError:
        pass
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


def resolve_source_branch() -> str | None:
    """MR source branch from CI-supplied pipeline config.

    ``CI_MERGE_REQUEST_SOURCE_BRANCH_NAME`` is set by GitLab CI in MR
    pipelines. It is CI-supplied infrastructure config — the same trust
    category as ``RAISE_DEVELOPMENT_BRANCH`` — not an agent-controlled
    escape hatch (RAISE-16748).
    """
    value = os.environ.get("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", "").strip()
    return value or None


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


# ---------------------------------------------------------------------------
# Multi-release-line resolution (RAISE-17066)
# ---------------------------------------------------------------------------

_FEATURE_WORK_TYPES = frozenset({"story", "feature", "epic"})


def _resolve_from_lines(
    release_lines: list[ReleaseLine],
    work_type: str,
    fix_version: str | None,
) -> str:
    from raise_cli.exceptions import AmbiguousTargetError

    non_sunset = [ln for ln in release_lines if ln.status != "sunset"]

    if fix_version:
        for ln in non_sunset:
            if fix_version in ln.fix_versions:
                return ln.branch
        raise AmbiguousTargetError(
            f"fix_version '{fix_version}' not found in any active release line",
        )

    if len(non_sunset) == 1:
        return non_sunset[0].branch

    if work_type == "bugfix":
        bugfix_only = [ln for ln in non_sunset if ln.status == "bugfix-only"]
        if len(bugfix_only) == 1:
            return bugfix_only[0].branch

    # Step 5: all other work -> active line (includes bugfix when >1 bugfix-only lines)
    active = [ln for ln in release_lines if ln.status == "active"]
    if active:
        return active[0].branch

    raise AmbiguousTargetError(
        "Cannot determine target branch — no active release line found",
    )


def resolve_target(
    project: Path,
    work_type: str,
    fix_version: str | None = None,
    explicit_base: str | None = None,
) -> str:
    """Deterministic target-branch resolution chain (RAISE-17066).

    Chain: explicit_base > env > fix_version mapping > work-type default > FAIL.
    Empty ``release_lines`` triggers legacy mode (``resolve_dev_branch``).
    """
    from raise_cli.project_config.manifest import load_manifest

    if explicit_base:
        return explicit_base

    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override

    try:
        manifest = load_manifest(project)
    except FileNotFoundError:
        return "main"

    if manifest is None:
        return "main"

    lines = manifest.branches.release_lines
    if not lines:
        return manifest.branches.development

    return _resolve_from_lines(lines, work_type, fix_version)


def check_admission(
    target_branch: str,
    work_type: str,
    release_lines: list[ReleaseLine],
) -> None:
    """Reject work that violates release-line lifecycle policy."""
    from raise_cli.exceptions import AdmissionError

    for ln in release_lines:
        if ln.branch != target_branch:
            continue
        if ln.status == "sunset":
            raise AdmissionError(
                f"Branch {target_branch} is sunset — no work accepted",
            )
        if ln.status == "bugfix-only" and work_type in _FEATURE_WORK_TYPES:
            raise AdmissionError(
                f"Branch {target_branch} is bugfix-only — feature/story work rejected",
            )
        return
    # Branch not in release_lines — pass defensively (may be manually specified)
