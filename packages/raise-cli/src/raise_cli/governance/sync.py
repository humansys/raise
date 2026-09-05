"""Governance artifact sync — scan local files and POST to raise-server (ADR-076).

Discovers governance artifacts via inline locator logic,
computes SHA-256 content hashes, and builds ReconcileRequest payloads
for POST /api/v2/governance/reconcile.
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType

logger = logging.getLogger(__name__)

_RECONCILE_ENDPOINT = "/api/v2/governance/reconcile"

_ARTIFACT_TYPE_MAP: dict[str, str] = {
    "prd": "governance_manifest",
    "vision": "governance_manifest",
    "constitution": "governance_manifest",
    "roadmap": "governance_manifest",
    "backlog": "governance_manifest",
    "guardrails": "governance_manifest",
    "glossary": "governance_manifest",
    "adr": "adr",
    "epic_scope": "governance_manifest",
}


@dataclass(frozen=True)
class ArtifactInfo:
    """Scanned governance artifact with metadata."""

    path: str
    artifact_type: str
    content_hash: str
    content_summary: str | None = None


def file_content_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    content = file_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    return f"sha256:{digest}"


def _build_locators(project_root: Path) -> list[ArtifactLocator]:
    """Build ArtifactLocators for all known governance artifact locations.

    Inline version of the locator logic previously in GovernanceExtractor.
    Discovers single-file artifacts, ADR files (4 directories), and epic scope files.
    """
    meta = {"project_root": str(project_root)}
    locators: list[ArtifactLocator] = []

    # Single-file artifacts
    single_files: list[tuple[str, str]] = [
        (CoreArtifactType.PRD, "governance/prd.md"),
        (CoreArtifactType.VISION, "governance/vision.md"),
        (CoreArtifactType.CONSTITUTION, "framework/reference/constitution.md"),
        (CoreArtifactType.ROADMAP, "governance/roadmap.md"),
        (CoreArtifactType.BACKLOG, "governance/backlog.md"),
        (CoreArtifactType.GUARDRAILS, "governance/guardrails.md"),
        (CoreArtifactType.GLOSSARY, "framework/reference/glossary.md"),
    ]

    for artifact_type, rel_path in single_files:
        if (project_root / rel_path).exists():
            locators.append(
                ArtifactLocator(
                    path=rel_path,
                    artifact_type=artifact_type,
                    metadata=dict(meta),
                )
            )

    # ADR files — one locator per file
    for adr_dir in [
        "dev/decisions",
        "dev/decisions/v2",
        "governance/adrs/v1",
        "governance/adrs/v2",
    ]:
        full_dir = project_root / adr_dir
        if full_dir.exists():
            for adr_file in sorted(full_dir.glob("adr-*.md")):
                rel = str(adr_file.relative_to(project_root))
                locators.append(
                    ArtifactLocator(
                        path=rel,
                        artifact_type=CoreArtifactType.ADR,
                        metadata=dict(meta),
                    )
                )

    # Epic scope files — one locator per scope.md
    for scope_file in sorted(project_root.glob("work/epics/*/scope.md")):
        rel = str(scope_file.relative_to(project_root))
        locators.append(
            ArtifactLocator(
                path=rel,
                artifact_type=CoreArtifactType.EPIC_SCOPE,
                metadata=dict(meta),
            )
        )

    # Epic design/plan files (SD-3, S16480.4)
    for pattern in ["work/epics/*/design.md", "work/epics/*/plan.md"]:
        for epic_file in sorted(project_root.glob(pattern)):
            rel = str(epic_file.relative_to(project_root))
            locators.append(
                ArtifactLocator(
                    path=rel,
                    artifact_type=CoreArtifactType.EPIC_SCOPE,
                    metadata=dict(meta),
                )
            )

    # Story files (SD-3, S16480.4)
    for story_file in sorted(project_root.glob("work/epics/*/stories/*.md")):
        rel = str(story_file.relative_to(project_root))
        locators.append(
            ArtifactLocator(
                path=rel,
                artifact_type=CoreArtifactType.EPIC_SCOPE,
                metadata=dict(meta),
            )
        )

    return locators


def scan_governance_artifacts(project_root: Path) -> list[ArtifactInfo]:
    """Scan governance directory and return artifact metadata.

    Discovers governance artifacts via inline locator logic,
    then computes content hashes for each.
    """
    locators = _build_locators(project_root)

    artifacts: list[ArtifactInfo] = []
    for loc in locators:
        full_path = project_root / loc.path
        if not full_path.is_file():
            continue
        artifact_type = _ARTIFACT_TYPE_MAP.get(loc.artifact_type, "governance_manifest")
        summary_line = _first_heading(full_path)
        artifacts.append(
            ArtifactInfo(
                path=loc.path,
                artifact_type=artifact_type,
                content_hash=file_content_hash(full_path),
                content_summary=summary_line,
            )
        )
    return artifacts


def _first_heading(file_path: Path) -> str | None:
    """Extract first markdown heading as summary."""
    try:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()[:200]
    except Exception:  # noqa: BLE001, S110
        pass
    return None


def build_reconcile_payload(
    artifacts: list[ArtifactInfo],
    *,
    repo_url: str,
    branch: str,
    commit_sha: str,
    author: str | None = None,
) -> dict[str, Any]:
    """Build the JSON payload for POST /api/v2/governance/reconcile."""
    return {
        "repo_url": repo_url,
        "branch": branch,
        "artifacts": [
            {
                "path": a.path,
                "type": a.artifact_type,
                "content_hash": a.content_hash,
                "content_summary": a.content_summary,
                "commit_sha": commit_sha,
                "author": author,
            }
            for a in artifacts
        ],
    }


def _server_config() -> tuple[str, str] | None:
    """Return (server_url, api_key) or None if not configured."""
    from raise_cli.config.server import get_server_credentials

    return get_server_credentials()


def _git_info(project_root: Path) -> tuple[str, str, str | None]:
    """Return (repo_url, branch, commit_sha) from git."""

    def _run(args: list[str]) -> str:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=5, cwd=project_root
        )
        return result.stdout.strip()

    repo_url = _run(["git", "remote", "get-url", "origin"])
    branch = _run(["git", "branch", "--show-current"])
    commit_sha = _run(["git", "rev-parse", "HEAD"])
    return repo_url, branch, commit_sha or None


def sync_to_server(
    project_root: Path,
    *,
    server_url: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any] | None:
    """Scan governance artifacts and POST to raise-server.

    Returns the server response dict, or None if server not configured.
    """
    if server_url is None or api_key is None:
        config = _server_config()
        if config is None:
            logger.info("RAISE_SERVER_URL/RAISE_API_KEY not set — skipping sync")
            return None
        server_url, api_key = config

    artifacts = scan_governance_artifacts(project_root)
    if not artifacts:
        logger.info("No governance artifacts found")
        return None

    repo_url, branch, commit_sha = _git_info(project_root)
    if not repo_url or not branch:
        logger.warning("Could not resolve git remote/branch — skipping sync")
        return None

    payload = build_reconcile_payload(
        artifacts,
        repo_url=repo_url,
        branch=branch,
        commit_sha=commit_sha or "0" * 40,
    )

    with httpx.Client(
        base_url=server_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
    ) as client:
        resp = client.post(_RECONCILE_ENDPOINT, json=payload)
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result
