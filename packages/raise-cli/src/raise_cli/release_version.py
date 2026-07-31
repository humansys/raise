"""Resolve the Jira fixVersion associated with the active release."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

from pydantic import BaseModel

_RELEASE_BRANCH_RE = re.compile(r"^release/(?P<base>\d+\.\d+\.\d+)$")
_PACKAGE_VERSION_RE = re.compile(
    r"^(?P<base>\d+\.\d+\.\d+)(?P<prerelease>(?:(?:a|b|rc)\d+)?)"
    r"(?:\.dev\d+)?$"
)


class FixVersionResolution(BaseModel):
    """The effective release fixVersion and the authority that selected it."""

    version: str | None
    source: str | None
    release_branch: str
    target_ref: str | None = None
    target_head_sha: str | None = None


def resolve_fix_version(project: Path, development_branch: str) -> str | None:
    """Return the Jira fixVersion for a release branch, if applicable.

    Package metadata preserves an active prerelease label. The release branch
    remains the compatibility fallback when metadata is absent or belongs to a
    different release line.
    """
    return resolve_fix_version_with_source(project, development_branch).version


def resolve_fix_version_with_source(
    project: Path, development_branch: str
) -> FixVersionResolution:
    """Resolve the effective fixVersion while retaining its provenance."""
    release_match = _RELEASE_BRANCH_RE.fullmatch(development_branch)
    if release_match is None:
        return FixVersionResolution(
            version=None, source=None, release_branch=development_branch
        )

    release_base = release_match.group("base")
    package_version = _package_fix_version(project, release_base)
    if package_version is not None:
        return FixVersionResolution(
            version=package_version,
            source="cli_package_metadata",
            release_branch=development_branch,
        )
    return FixVersionResolution(
        version=release_base,
        source="release_branch",
        release_branch=development_branch,
    )


def resolve_target_fix_version(
    project: Path, development_branch: str
) -> FixVersionResolution:
    """Resolve fixVersion from the release target, falling back to the worktree.

    The remote-tracking release branch is authoritative when available. This
    prevents a stale story branch package version from silently selecting an
    obsolete prerelease.
    """
    release_match = _RELEASE_BRANCH_RE.fullmatch(development_branch)
    if release_match is None:
        return resolve_fix_version_with_source(project, development_branch)

    release_base = release_match.group("base")
    for target_ref in (f"origin/{development_branch}", development_branch):
        pyproject = _git_text(
            project,
            "show",
            f"{target_ref}:packages/raise-cli/pyproject.toml",
        )
        if pyproject is None:
            continue
        package_version = _package_fix_version_from_toml(pyproject, release_base)
        target_head_sha = _git_text(project, "rev-parse", target_ref)
        if package_version is not None:
            return FixVersionResolution(
                version=package_version,
                source="cli_package_metadata",
                release_branch=development_branch,
                target_ref=target_ref,
                target_head_sha=target_head_sha,
            )
        return FixVersionResolution(
            version=release_base,
            source="release_branch",
            release_branch=development_branch,
            target_ref=target_ref,
            target_head_sha=target_head_sha,
        )

    return resolve_fix_version_with_source(project, development_branch)


def _git_text(project: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(  # noqa: S603 — fixed git executable and controlled args
            ["git", *args],
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _package_fix_version(project: Path, release_base: str) -> str | None:
    try:
        pyproject = (project / "packages" / "raise-cli" / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    except OSError:
        return None
    return _package_fix_version_from_toml(pyproject, release_base)


def _package_fix_version_from_toml(content: str, release_base: str) -> str | None:
    try:
        data = tomllib.loads(content)
        raw_version = str(data["project"]["version"])
    except (KeyError, tomllib.TOMLDecodeError):
        return None

    package_match = _PACKAGE_VERSION_RE.fullmatch(raw_version)
    if package_match is None or package_match.group("base") != release_base:
        return None
    return package_match.group("base") + package_match.group("prerelease")
