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
import json
import re
import sys
from pathlib import Path

_MCP_RE = re.compile(r"^rai-mcp-pipeline-(?P<platform>.+)\.(?:tar\.gz|zip)$")
_RAI_RE = re.compile(r"^rai-(?P<platform>.+)\.(?:tar\.gz|zip)$")


def _strip_v_prefix(version: str) -> str:
    """Strip a leading 'v' (git tag style) — VersionManifest/parse_version
    expect bare PEP 440 (see self_update/manifest.py, is_newer())."""
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


def build_manifest(*, version: str, base_url: str, dist_dir: Path) -> dict:
    """Build the version.json content — validated by the caller against
    raise_cli.self_update.manifest.VersionManifest, not re-validated here
    (no schema duplication, design.md D4)."""
    platforms = _discover_platform_archives(dist_dir)

    return {
        "version": _strip_v_prefix(version),
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
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            version=args.version, base_url=args.base_url, dist_dir=args.dist_dir
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)

    args.output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {args.output} ({len(manifest['platforms'])} platform(s))")


if __name__ == "__main__":
    main()
