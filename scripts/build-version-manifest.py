#!/usr/bin/env python3
"""Build version.json for the releases.raiseframework.ai facade (RAISE-15633).

Reads the .sha256 sidecars that scripts/package-binary-archive.sh (S7,
RAISE-15631) already produced alongside each platform archive in a dist/
directory, and assembles the manifest dict that
raise_cli.self_update.manifest.VersionManifest (S8, RAISE-15632) validates.

Deliberately does NOT recompute any checksum (design.md D3) — a missing
sidecar is a hard failure, not something this script derives itself.

Usage:
    python scripts/build-version-manifest.py \\
        --version v3.2.0 \\
        --base-url https://releases.raiseframework.ai/rai-binaries/v3.2.0 \\
        --dist-dir packages/raise-cli/dist \\
        --output version.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

_MCP_RE = re.compile(r"^rai-mcp-pipeline-(?P<platform>.+)\.(?:tar\.gz|zip)$")
_RAI_RE = re.compile(r"^rai-(?P<platform>.+)\.(?:tar\.gz|zip)$")

# Path to the single source of truth for schema_version → schema_revision
# (RAISE-19634 / RAISE-19413 QR C1). Loaded via importlib, not a package
# import — this script runs in CI jobs where raise-cli is not installed
# (only its built binaries are downloaded), exactly as schema_revisions.py's
# own docstring anticipates.
_SCHEMA_REVISIONS_MODULE = (
    Path(__file__).resolve().parent.parent
    / "packages"
    / "raise-cli"
    / "src"
    / "raise_cli"
    / "storage"
    / "schema_revisions.py"
)


def _latest_schema_info() -> tuple[int, str]:
    """Return (schema_version, schema_revision) for the newest known revision.

    Derives both from SCHEMA_REVISIONS in schema_revisions.py instead of a
    hardcoded literal — a forgotten manual bump there would silently publish
    a stale schema_revision, pointing a future downgrade at the wrong Alembic
    revision (RAISE-19413 QR C1).
    """
    spec = importlib.util.spec_from_file_location(
        "schema_revisions", _SCHEMA_REVISIONS_MODULE
    )
    if spec is None or spec.loader is None:
        msg = f"cannot load schema_revisions module from {_SCHEMA_REVISIONS_MODULE}"
        raise ValueError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    revisions: dict[int, str] = module.SCHEMA_REVISIONS
    if not revisions:
        msg = f"SCHEMA_REVISIONS is empty in {_SCHEMA_REVISIONS_MODULE}"
        raise ValueError(msg)
    latest_version = max(revisions)
    return latest_version, revisions[latest_version]

# Derive channel from a version string when not provided explicitly (RAISE-19634).
_CHANNEL_RE = re.compile(r"(?:alpha|a\d)", re.IGNORECASE)
_RC_RE = re.compile(r"rc", re.IGNORECASE)


def _derive_channel(version: str) -> str:
    """Return 'alpha', 'rc', or 'stable' from a version/tag string."""
    if _CHANNEL_RE.search(version):
        return "alpha"
    if _RC_RE.search(version):
        return "rc"
    return "stable"


_SEVERITY_RE = re.compile(r"^severity:\s*(\S+)\s*$", re.MULTILINE)


def _extract_severity(changelog_text: str, version: str) -> str | None:
    """Read the declared severity for `version` from CHANGELOG.md text.

    Self-contained (no raise_cli import, RAISE-15661) — this script runs
    via plain `python3` in CI (build.yml) before the raise-cli wheel
    exists, so it cannot depend on the package it is helping to publish.
    Mirrors raise_cli.publish.changelog.extract_severity()'s section
    lookup; kept independent deliberately, not duplicated by oversight.
    """
    section = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*$(.*?)(?=(?:^## \[|\Z))",
        changelog_text,
        re.DOTALL | re.MULTILINE,
    )
    if section is None:
        return None
    match = _SEVERITY_RE.search(section.group(1))
    return match.group(1) if match else None


def _strip_v_prefix(version: str) -> str:
    """Strip a leading 'v' (git tag style) — VersionManifest/parse_version
    expect bare PEP 440 (see self_update/manifest.py, is_newer()).
    """
    if version.startswith("v") and version[1:2].isdigit():
        return version[1:]
    return version


def _read_sha256_sidecar(archive: Path) -> str:
    """Read the .sha256 sidecar next to `archive` — never recompute (D3)."""
    sidecar = archive.with_name(archive.name + ".sha256")
    if not sidecar.exists():
        msg = f"missing sha256 sidecar: {sidecar}"
        raise FileNotFoundError(msg)
    # sha256sum/shasum format: "<hash>  <filename>"
    return sidecar.read_text().split()[0]


def _discover_platform_archives(dist_dir: Path) -> dict[str, dict[str, Path]]:
    """Group archives in dist_dir by platform tag: {tag: {rai: path, rai_mcp_pipeline: path}}."""
    platforms: dict[str, dict[str, Path]] = {}
    for entry in sorted(dist_dir.iterdir()):
        if not entry.is_file() or entry.name.endswith(".sha256"):
            continue
        mcp_match = _MCP_RE.match(entry.name)
        if mcp_match:
            platforms.setdefault(mcp_match.group("platform"), {})[
                "rai_mcp_pipeline"
            ] = entry
            continue
        rai_match = _RAI_RE.match(entry.name)
        if rai_match:
            platforms.setdefault(rai_match.group("platform"), {})["rai"] = entry

    if not platforms:
        msg = f"no platform archives found in {dist_dir}"
        raise ValueError(msg)

    for tag, binaries in platforms.items():
        if "rai" not in binaries:
            msg = f"platform {tag}: missing rai archive"
            raise ValueError(msg)
        if "rai_mcp_pipeline" not in binaries:
            msg = f"platform {tag}: missing rai-mcp-pipeline archive"
            raise ValueError(msg)

    return platforms


def build_manifest(
    *,
    version: str,
    base_url: str,
    dist_dir: Path,
    changelog_path: Path | None = None,
    schema_version: int | None = None,
    schema_revision: str | None = None,
    channel: str | None = None,
) -> dict:
    """Build the version.json content — validated by the caller against
    raise_cli.self_update.manifest.VersionManifest, not re-validated here
    (no schema duplication, design.md D4).

    `changelog_path` is optional (RAISE-15661): when given and the version's
    CHANGELOG section declares a severity, it is included in the output.
    Omitted entirely when absent — VersionManifest.severity already
    defaults to None for manifests without the field.

    RAISE-19634: `schema_version`, `schema_revision`, and `channel` extend the
    manifest for Alembic-based rollback support. When `channel` is None, it is
    derived from `version` (alpha/rc/stable heuristic). When `schema_version`
    and `schema_revision` are both None, they are derived from the latest
    entry in `schema_revisions.SCHEMA_REVISIONS` (RAISE-19413 QR C1) — never
    hardcoded by the caller, so a new migration's revision is picked up
    automatically on the next release.
    """
    platforms = _discover_platform_archives(dist_dir)
    stripped_version = _strip_v_prefix(version)

    manifest: dict = {
        "version": stripped_version,
        "platforms": {
            tag: {
                "rai": {
                    "url": f"{base_url}/{binaries['rai'].name}",
                    "sha256": _read_sha256_sidecar(binaries["rai"]),
                },
                "rai_mcp_pipeline": {
                    "url": f"{base_url}/{binaries['rai_mcp_pipeline'].name}",
                    "sha256": _read_sha256_sidecar(binaries["rai_mcp_pipeline"]),
                },
            }
            for tag, binaries in platforms.items()
        },
    }

    if changelog_path is not None and changelog_path.exists():
        severity = _extract_severity(
            changelog_path.read_text(encoding="utf-8"), stripped_version
        )
        if severity is not None:
            manifest["severity"] = severity

    # Schema metadata (RAISE-19634). Auto-derived from schema_revisions.py
    # unless the caller explicitly overrides both (e.g. tests) — never
    # hardcoded by a caller such as build.yml (RAISE-19413 QR C1).
    if schema_version is None and schema_revision is None:
        schema_version, schema_revision = _latest_schema_info()
    if schema_version is not None:
        manifest["schema_version"] = schema_version
    if schema_revision is not None:
        manifest["schema_revision"] = schema_revision
    manifest["channel"] = channel if channel is not None else _derive_channel(version)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Release tag (e.g. v3.2.0)")
    parser.add_argument(
        "--base-url", required=True, help="URL prefix the archives are served at"
    )
    parser.add_argument(
        "--dist-dir", required=True, type=Path, help="Directory with archives + .sha256"
    )
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    parser.add_argument(
        "--changelog-path",
        type=Path,
        default=None,
        help="CHANGELOG.md path to read severity from (RAISE-15661, optional)",
    )
    # RAISE-19634: Alembic schema metadata. Normally omitted — derived
    # automatically from schema_revisions.SCHEMA_REVISIONS (RAISE-19413 QR C1).
    # Pass both only to override (e.g. tests).
    parser.add_argument(
        "--schema-version",
        type=int,
        default=None,
        help="Override: integer schema version (e.g. 82). Auto-derived when omitted.",
    )
    parser.add_argument(
        "--schema-revision",
        default=None,
        help="Override: Alembic hex revision ID (e.g. 2fb8043dacd8). Auto-derived when omitted.",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help="Release channel (stable|rc|alpha). Derived from --version when omitted.",
    )
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            version=args.version,
            base_url=args.base_url,
            dist_dir=args.dist_dir,
            changelog_path=args.changelog_path,
            schema_version=args.schema_version,
            schema_revision=args.schema_revision,
            channel=args.channel,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)

    args.output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {args.output} ({len(manifest['platforms'])} platform(s))")


if __name__ == "__main__":
    main()
