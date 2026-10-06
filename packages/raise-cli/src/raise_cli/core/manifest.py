"""Version manifest model and comparison for `rai self-update` (RAISE-15632).

Moved from raise_cli.self_update.manifest to raise_cli.core (RAISE-16509 W9)
so that session (T3) can import it without an upward waiver into self_update (T2).

The manifest schema defined here is the contract that the release facade
(releases.raiseframework.ai, S9/RAISE-15633) must produce — see design.md
Open Question 1. It is provisional until S9 exists.
"""

from __future__ import annotations

import httpx
from packaging.version import Version
from pydantic import BaseModel

DEFAULT_TIMEOUT = 10

# Served from a GitHub Release asset in humansys/raise (RAISE-15664) — the
# build.yml release job publishes version.json alongside the binaries on
# every tag. Canonical location for this constant (RAISE-15715) — both the
# `rai self-update` command and the session-open proactive check import it
# from here.
MANIFEST_URL = "https://github.com/humansys/raise/releases/latest/download/version.json"


class ArtifactRef(BaseModel):
    """A single downloadable artifact: its URL and expected checksum."""

    url: str
    sha256: str


class PlatformArtifact(BaseModel):
    """The two binaries published for one platform tag (e.g. linux-x86_64)."""

    rai: ArtifactRef
    rai_mcp_pipeline: ArtifactRef


class VersionManifest(BaseModel):
    """Remote manifest at releases.raiseframework.ai/latest/version.json."""

    version: str
    platforms: dict[str, PlatformArtifact]
    # Optional (RAISE-15661) — manifests published before this story lack
    # the field; VersionManifest must keep parsing them without error.
    severity: str | None = None


def is_newer(*, remote: str, local: str) -> bool:
    """Return True if `remote` is a newer release than `local`.

    Delegates to `packaging.Version` (canonical PEP 440 ordering: alpha <
    beta < rc < stable), so a stable release is correctly detected as newer
    than a pre-release of the same major.minor.patch (RAISE-15971).
    """
    return Version(remote) > Version(local)


def fetch_manifest(
    url: str,
    *,
    transport: httpx.BaseTransport | None = None,
    timeout_s: float = DEFAULT_TIMEOUT,
) -> VersionManifest:
    """Fetch and parse the remote version manifest.

    Args:
        url: Full URL to version.json.
        transport: Optional httpx transport override (for tests).
        timeout_s: Request timeout in seconds — short-lived callers (e.g. the
            session-open check, RAISE-15715) pass a smaller value than the
            interactive `rai self-update` default.

    Raises:
        httpx.HTTPStatusError: If the server returns a non-2xx response.
    """
    with httpx.Client(
        transport=transport, timeout=timeout_s, follow_redirects=True
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return VersionManifest.model_validate(resp.json())
