"""Version manifest model and comparison for `rai self-update` (RAISE-15632).

The manifest schema defined here is the contract that the release facade
(releases.raiseframework.ai, S9/RAISE-15633) must produce — see design.md
Open Question 1. It is provisional until S9 exists.
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from raise_cli.publish.version import parse_version

DEFAULT_TIMEOUT = 10


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


def is_newer(*, remote: str, local: str) -> bool:
    """Return True if `remote` is a newer stable release than `local`.

    Compares major.minor.patch only (design.md D3) — pre-release/dev
    ordering is out of scope for v1; releases.raiseframework.ai is
    expected to publish stable versions only.
    """
    remote_v = parse_version(remote)
    local_v = parse_version(local)
    return (remote_v.major, remote_v.minor, remote_v.patch) > (
        local_v.major,
        local_v.minor,
        local_v.patch,
    )


def fetch_manifest(
    url: str, *, transport: httpx.BaseTransport | None = None
) -> VersionManifest:
    """Fetch and parse the remote version manifest.

    Args:
        url: Full URL to version.json.
        transport: Optional httpx transport override (for tests).

    Raises:
        httpx.HTTPStatusError: If the server returns a non-2xx response.
    """
    with httpx.Client(transport=transport, timeout=DEFAULT_TIMEOUT) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return VersionManifest.model_validate(resp.json())
