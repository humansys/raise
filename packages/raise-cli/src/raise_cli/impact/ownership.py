"""Manifest app ownership classification for changed files."""

from __future__ import annotations

from pathlib import Path

from raise_cli.impact.models import AffectedApp, ChangedFileImpact, OwnershipReport
from raise_cli.onboarding.manifest import AppInfo, ProjectManifest


def _normalize_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").strip("/")


def _owns_path(app: AppInfo, path: str) -> bool:
    app_path = _normalize_path(app.path)
    return path == app_path or path.startswith(app_path + "/")


def _find_owner(path: str, apps: list[AppInfo]) -> AppInfo | None:
    owners = [app for app in apps if _owns_path(app, path)]
    if not owners:
        return None
    return max(owners, key=lambda app: len(_normalize_path(app.path)))


def classify_ownership(
    files: list[Path],
    manifest: ProjectManifest,
) -> OwnershipReport:
    """Classify changed files by manifest app ownership."""
    apps = manifest.project.apps or []
    changed_files: list[ChangedFileImpact] = []
    affected_by_name: dict[str, AffectedApp] = {}

    for raw_path in sorted({_normalize_path(path) for path in files}):
        owner = _find_owner(raw_path, apps)
        if owner is None:
            changed_files.append(ChangedFileImpact(path=raw_path))
            continue

        owner_path = _normalize_path(owner.path)
        changed_files.append(
            ChangedFileImpact(
                path=raw_path,
                owner_app=owner.name,
                owner_path=owner_path,
            )
        )
        affected = affected_by_name.setdefault(
            owner.name,
            AffectedApp(name=owner.name, path=owner_path),
        )
        affected.direct_files.append(raw_path)

    affected_apps = sorted(
        (
            app.model_copy(update={"direct_files": sorted(app.direct_files)})
            for app in affected_by_name.values()
        ),
        key=lambda app: (app.name, app.path),
    )
    return OwnershipReport(files=changed_files, affected_apps=affected_apps)
