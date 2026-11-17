"""Version manifest model and comparison for `rai self-update` (RAISE-15632).

Moved from raise_cli.self_update.manifest to raise_cli.core (RAISE-16509 W9)
so that session (T3) can import it without an upward waiver into self_update (T2).

The manifest schema defined here is the contract that the release facade
(releases.raiseframework.ai, S9/RAISE-15633) must produce — see design.md
Open Question 1. It is provisional until S9 exists.

RAISE-19635 (S19413.2): adds fetch_channel_manifest() for rc/alpha channels.
"""

from __future__ import annotations

import logging
import re

import httpx
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10

# Served from a GitHub Release asset in humansys/raise (RAISE-15664) — the
# build.yml release job publishes version.json alongside the binaries on
# every tag. Canonical location for this constant (RAISE-15715) — both the
# `rai self-update` command and the session-open proactive check import it
# from here.
MANIFEST_URL = "https://github.com/humansys/raise/releases/latest/download/version.json"

# GitHub API URL used to discover alpha/rc releases (RAISE-19634).
# Shared with channel_manifest_url() to avoid a second literal.
_GITHUB_API_RELEASES_URL = "https://api.github.com/repos/humansys/raise/releases"

_VALID_CHANNELS = frozenset({"stable", "rc", "alpha"})
# Public alias — single source of truth for callers outside this module.
VALID_CHANNELS = _VALID_CHANNELS

# PEP 440 tag patterns for each prerelease channel (RAISE-20016 testing finding).
# GitHub releases for alpha use tags like v3.1.8a1; rc uses v3.1.8rc1.
# The old "-alpha." / "-rc." patterns matched a non-PEP440 convention that was
# never actually used — check-tag-provenance.sh enforces PEP440 throughout.
_CHANNEL_TAG_RE: dict[str, re.Pattern[str]] = {
    "alpha": re.compile(r"a\d+"),
    "rc": re.compile(r"rc\d+"),
}


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
    # RAISE-19634: Alembic schema metadata — optional for retrocompat with
    # manifests published before 3.1.8; both fields are required in new releases.
    schema_version: int | None = None
    schema_revision: str | None = None
    channel: str = "stable"

    @field_validator("channel")
    @classmethod
    def _validate_channel(cls, v: str) -> str:
        if v not in _VALID_CHANNELS:
            raise ValueError(f"unknown channel {v!r} (expected: stable, rc, alpha)")
        return v


def channel_manifest_url(channel: str) -> str:
    """Resolve the version.json URL for the given release channel.

    Args:
        channel: One of ``"stable"``, ``"rc"``, or ``"alpha"``.

    Returns:
        The URL where the version manifest for that channel is hosted.

    Raises:
        ValueError: If ``channel`` is not a recognized value.
    """
    if channel not in _VALID_CHANNELS:
        raise ValueError(f"unknown channel {channel!r} (expected: stable, rc, alpha)")
    if channel == "stable":
        return MANIFEST_URL
    return _GITHUB_API_RELEASES_URL


def is_newer(*, remote: str, local: str) -> bool:
    """Return True if `remote` is a newer release than `local`.

    Delegates to `packaging.Version` (canonical PEP 440 ordering: alpha <
    beta < rc < stable), so a stable release is correctly detected as newer
    than a pre-release of the same major.minor.patch (RAISE-15971).
    """
    return Version(remote) > Version(local)


def _fetch_json(
    url: str,
    *,
    transport: httpx.BaseTransport | None = None,
    timeout_s: float = DEFAULT_TIMEOUT,
) -> object:
    """Fetch a JSON response from *url* and return the parsed object.

    Separated from fetch_manifest so it can be mocked in tests for the
    GitHub releases API path without coupling to VersionManifest parsing.
    """
    with httpx.Client(
        transport=transport, timeout=timeout_s, follow_redirects=True
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()


def _pick_latest_prerelease_asset_url(releases: object, channel: str) -> str:  # noqa: C901
    """Find the version.json download URL for the latest matching prerelease.

    Args:
        releases: Parsed JSON from GitHub releases API (expected: list[dict]).
        channel: ``"rc"`` or ``"alpha"`` — used to filter by tag pattern.

    Returns:
        The ``browser_download_url`` of the ``version.json`` asset in the
        most-recent matching release.

    Raises:
        ValueError: If no matching release or ``version.json`` asset is found.
    """
    if not isinstance(releases, list):
        raise ValueError(
            f"Expected list from GitHub releases API, got {type(releases)}"
        )

    # Match PEP 440 prerelease tags: alpha → "a\d+" (e.g. v3.1.8a1),
    # rc → "rc\d+" (e.g. v3.1.8rc1). Requires isPrerelease=True on the release.
    tag_re = _CHANNEL_TAG_RE[channel]
    matching = [
        r
        for r in releases
        if isinstance(r, dict)
        and r.get("prerelease", False)
        and tag_re.search(str(r.get("tag_name", "")))
    ]
    if not matching:
        raise ValueError(
            f"No {channel} releases found in GitHub releases API response "
            f"(looked for PEP 440 pattern {tag_re.pattern!r} in tag names)"
        )

    def _sort_key(r: object) -> Version:
        if not isinstance(r, dict):
            return Version("0.0.0")
        # Tags are PEP 440 (e.g. v3.1.8a1, v3.1.8rc1) — strip leading "v" only.
        tag = str(r.get("tag_name", "0.0.0")).lstrip("v")
        try:
            return Version(tag)
        except InvalidVersion:
            logger.debug("Unparseable tag %r — skipping", r.get("tag_name"))
            return Version("0.0.0")

    latest = max(matching, key=_sort_key)
    assets = latest.get("assets", [])
    if not isinstance(assets, list):
        raise ValueError("No assets in release")

    for asset in assets:
        if isinstance(asset, dict) and asset.get("name") == "version.json":
            url = asset.get("browser_download_url", "")
            if url:
                return str(url)

    raise ValueError(
        f"No version.json asset found in latest {channel} release "
        f"({latest.get('tag_name', '?')})"
    )


def fetch_channel_manifest(
    channel: str,
    *,
    transport: httpx.BaseTransport | None = None,
    timeout_s: float = DEFAULT_TIMEOUT,
) -> VersionManifest:
    """Fetch the VersionManifest for the given release channel.

    For ``"stable"``: delegates to :func:`fetch_manifest` with
    :data:`MANIFEST_URL` (GitHub latest release asset).

    For ``"rc"`` / ``"alpha"``: queries the GitHub releases API, filters by
    tag pattern, resolves the latest matching prerelease's ``version.json``
    asset URL, then fetches and validates that manifest.

    Args:
        channel: One of ``"stable"``, ``"rc"``, or ``"alpha"``.
        transport: Optional httpx transport override (for tests).
        timeout_s: Request timeout in seconds.

    Returns:
        Validated :class:`VersionManifest`.

    Raises:
        ValueError: If ``channel`` is not recognised or no matching release exists.
        httpx.HTTPError: If any HTTP request fails.
    """
    if channel not in _VALID_CHANNELS:
        raise ValueError(f"unknown channel {channel!r} (expected: stable, rc, alpha)")

    if channel == "stable":
        return fetch_manifest(MANIFEST_URL, transport=transport, timeout_s=timeout_s)

    # rc / alpha: GitHub releases API → filter by tag pattern → fetch version.json
    releases = _fetch_json(
        _GITHUB_API_RELEASES_URL,
        transport=transport,
        timeout_s=timeout_s,
    )
    asset_url = _pick_latest_prerelease_asset_url(releases, channel)
    return fetch_manifest(asset_url, transport=transport, timeout_s=timeout_s)


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
