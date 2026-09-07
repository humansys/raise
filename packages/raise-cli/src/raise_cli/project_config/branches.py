"""Branch resolution utilities — project_config tier (RAISE-16462).

Extracted from ``raise_cli.story.open_service`` so that both T2 service modules
and T3 domain modules can import without creating upward edges.
"""

from __future__ import annotations

import os
import re
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.project_config.manifest import ReleaseLine

_RELEASE_BRANCH_RE = re.compile(r"^release/(?P<base>\d+\.\d+\.\d+)$")


def _release_version_key(branch: str) -> tuple[int, int, int] | None:
    """Parse a ``release/X.Y.Z`` branch into a sortable version tuple.

    Deliberately not imported from ``raise_cli.release_version``: that module
    is T2, this package is T5 (foundation) per the RAISE-16340 layer contract
    — T5 cannot depend upward on T2. The two implementations are trivial and
    independently pure; the layer boundary, not style, is why this exists.
    """
    match = _RELEASE_BRANCH_RE.fullmatch(branch)
    if match is None:
        return None
    major, minor, patch = match.group("base").split(".")
    return (int(major), int(minor), int(patch))


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


# ---------------------------------------------------------------------------
# Forward-merge propagation chain (RAISE-17076 / S17066.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hop:
    """One forward-merge from a release line to the next non-sunset line."""

    index: int
    source: str
    target: str
    target_status: str


@dataclass(frozen=True)
class SkippedLine:
    """A release line excluded from a computed propagation chain."""

    branch: str
    reason: str


def propagation_chain(
    release_lines: list[ReleaseLine], source_branch: str
) -> tuple[list[Hop], list[SkippedLine]]:
    """Ordered hops from ``source_branch`` to every newer non-sunset line.

    ``main`` is never a target — ``release_lines`` only ever contains release
    lines by construction (ADR-033). Sunset lines newer than the source are
    skipped and reported rather than silently dropped, so
    ``3.1.0 -> [3.2.0 sunset] -> 3.3.0`` yields a single 3.1.0 -> 3.3.0 hop.

    Raises AmbiguousTargetError if ``source_branch`` is not a declared
    release line, is itself sunset, or any declared line is not a
    well-formed ``release/X.Y.Z`` branch.
    """
    from raise_cli.exceptions import AmbiguousTargetError

    keyed: list[tuple[tuple[int, int, int], ReleaseLine]] = []
    for line in release_lines:
        key = _release_version_key(line.branch)
        if key is None:
            raise AmbiguousTargetError(
                f"release line '{line.branch}' is not a release/X.Y.Z branch",
            )
        keyed.append((key, line))
    keyed.sort(key=lambda item: item[0])

    source_key = _release_version_key(source_branch)
    source_line = next((ln for ln in release_lines if ln.branch == source_branch), None)
    if source_key is None or source_line is None:
        raise AmbiguousTargetError(
            f"source '{source_branch}' is not a declared release line "
            "(branches.release_lines)",
        )
    if source_line.status == "sunset":
        raise AmbiguousTargetError(f"source '{source_branch}' is sunset")

    hops: list[Hop] = []
    skipped: list[SkippedLine] = []
    current_source = source_branch
    for key, line in keyed:
        if key <= source_key:
            continue
        if line.status == "sunset":
            skipped.append(SkippedLine(branch=line.branch, reason="sunset"))
            continue
        hops.append(
            Hop(
                index=len(hops) + 1,
                source=current_source,
                target=line.branch,
                target_status=line.status,
            )
        )
        current_source = line.branch

    return hops, skipped


def propagation_branch(work_id: str, source: str, target: str) -> str:
    """``forward-merge/{work_id}/{src_ver}-to-{tgt_ver}`` (D4)."""
    src_ver = source.removeprefix("release/")
    tgt_ver = target.removeprefix("release/")
    return f"forward-merge/{work_id}/{src_ver}-to-{tgt_ver}"
