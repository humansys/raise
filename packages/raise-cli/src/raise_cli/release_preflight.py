"""Observable preflight for the effective release fixVersion."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from raise_cli.adapters.protocols import ProjectVersionManagementAdapter
from raise_cli.release_version import (
    resolve_fix_version_with_source,
    resolve_target_fix_version,
)


class ReleasePreflightResult(BaseModel):
    """Machine-readable comparison of release version authorities."""

    status: Literal["ok", "warn", "blocked", "skipped"]
    resolved_version: str | None
    source: str | None
    release_branch: str
    target_ref: str | None = None
    target_head_sha: str | None = None
    local_version: str | None = None
    portfolio_versions: list[str] = Field(default_factory=list)
    jira_versions: list[str] = Field(default_factory=list)
    portfolio_contains_resolved: bool | None = None
    jira_contains_resolved: bool | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def run_release_preflight(
    project: Path,
    development_branch: str,
    *,
    project_key: str = "",
    adapter: ProjectVersionManagementAdapter | None = None,
    adapter_error: str = "",
    strict: bool = False,
) -> ReleasePreflightResult:
    """Compare the release target with worktree, portfolio, and Jira metadata."""
    target = resolve_target_fix_version(project, development_branch)
    local = resolve_fix_version_with_source(project, development_branch)
    if target.version is None:
        return ReleasePreflightResult(
            status="skipped",
            resolved_version=None,
            source=None,
            release_branch=development_branch,
        )

    warnings: list[str] = []
    errors: list[str] = []
    portfolio_versions = _manifest_portfolio_versions(project)
    portfolio_contains = target.version in portfolio_versions

    if local.version != target.version:
        message = (
            f"worktree resolves {local.version or 'no version'} but release target "
            f"{target.target_ref or development_branch} resolves {target.version}; "
            "merge the target branch before close"
        )
        (errors if strict else warnings).append(message)

    if not portfolio_contains:
        stale = _same_release_prereleases(portfolio_versions, target.version)
        stale_text = f"; stale entries: {', '.join(stale)}" if stale else ""
        warnings.append(
            f"portfolio omits resolved fixVersion {target.version}{stale_text}; "
            "add it to project.portfolio.tracked_versions"
        )

    jira_versions: list[str] = []
    jira_contains: bool | None = None
    if project_key:
        if adapter is None:
            message = adapter_error or "configured Jira adapter is unavailable"
            (errors if strict else warnings).append(
                f"cannot verify Jira project {project_key}: {message}"
            )
        else:
            try:
                jira_versions = [
                    item.name for item in adapter.list_versions(project_key)
                ]
                jira_contains = target.version in jira_versions
            except Exception as exc:  # noqa: BLE001 — diagnostic boundary
                (errors if strict else warnings).append(
                    f"cannot verify Jira project {project_key}: {exc}"
                )
            else:
                if not jira_contains:
                    message = (
                        f"resolved fixVersion {target.version} is not configured in "
                        f"Jira project {project_key}; create or select it before close"
                    )
                    (errors if strict else warnings).append(message)

    status: Literal["ok", "warn", "blocked", "skipped"]
    status = "blocked" if errors else ("warn" if warnings else "ok")
    return ReleasePreflightResult(
        status=status,
        resolved_version=target.version,
        source=target.source,
        release_branch=development_branch,
        target_ref=target.target_ref,
        target_head_sha=target.target_head_sha,
        local_version=local.version,
        portfolio_versions=portfolio_versions,
        jira_versions=jira_versions,
        portfolio_contains_resolved=portfolio_contains,
        jira_contains_resolved=jira_contains,
        warnings=warnings,
        errors=errors,
    )


def _manifest_portfolio_versions(project: Path) -> list[str]:
    manifest = project / ".raise" / "manifest.yaml"
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    tracked = ((data.get("project") or {}).get("portfolio") or {}).get(
        "tracked_versions"
    )
    if not isinstance(tracked, list):
        return []
    return [str(item) for item in tracked]


def _same_release_prereleases(versions: list[str], resolved: str) -> list[str]:
    release_base = resolved.split("a", 1)[0].split("b", 1)[0].split("rc", 1)[0]
    return [
        version
        for version in versions
        if version != resolved and version.startswith(release_base)
    ]
