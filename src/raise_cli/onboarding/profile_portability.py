"""Profile export/import for developer identity portability.

Enables transferring a DeveloperProfile between machines via a YAML bundle
that strips machine-local state (active sessions, paths).
"""

from __future__ import annotations

import platform
from datetime import UTC, datetime
from typing import Any, cast

import yaml
from pydantic import BaseModel

from raise_cli.onboarding.profile import DeveloperProfile

BUNDLE_VERSION = 1
MACHINE_LOCAL_FIELDS: frozenset[str] = frozenset(
    {"active_sessions", "current_session", "projects"}
)


class BundleMeta(BaseModel):
    """Metadata for a profile export bundle."""

    version: int
    exported_at: datetime
    source_machine: str


class ProfileBundle(BaseModel):
    """Portable profile bundle with metadata."""

    meta: BundleMeta
    profile: dict[str, Any]


def export_profile(profile: DeveloperProfile) -> ProfileBundle:
    """Export a DeveloperProfile into a portable bundle.

    Strips machine-local fields (active_sessions, current_session, projects)
    and adds export metadata.

    Args:
        profile: The developer profile to export.

    Returns:
        ProfileBundle ready for serialization.
    """
    data = profile.model_dump(mode="json")
    for field in MACHINE_LOCAL_FIELDS:
        data.pop(field, None)

    meta = BundleMeta(
        version=BUNDLE_VERSION,
        exported_at=datetime.now(UTC),
        source_machine=platform.node(),
    )

    return ProfileBundle(meta=meta, profile=data)


def serialize_bundle(bundle: ProfileBundle) -> str:
    """Serialize a ProfileBundle to YAML string.

    Uses `_meta` key in output (per contract) even though the Pydantic
    field is named `meta` (to avoid private attribute conflicts).

    Args:
        bundle: The bundle to serialize.

    Returns:
        YAML string with _meta and profile keys.
    """
    output = {
        "_meta": bundle.meta.model_dump(mode="json"),
        "profile": bundle.profile,
    }
    return yaml.dump(
        output, default_flow_style=False, allow_unicode=True, sort_keys=False
    )


def parse_bundle(content: str) -> ProfileBundle:
    """Parse a YAML bundle string into a ProfileBundle.

    Validates structure: requires _meta with supported version and profile key.

    Args:
        content: YAML string to parse.

    Returns:
        Validated ProfileBundle.

    Raises:
        ValueError: If structure is invalid or version unsupported.
    """
    raw = yaml.safe_load(content)
    if not isinstance(raw, dict):
        msg = "Invalid bundle: expected YAML mapping"
        raise ValueError(msg)
    data = cast("dict[str, Any]", raw)

    if "_meta" not in data:
        msg = "Invalid bundle: missing _meta section"
        raise ValueError(msg)

    if "profile" not in data:
        msg = "Invalid bundle: missing profile section"
        raise ValueError(msg)

    if not isinstance(data["_meta"], dict):
        msg = "Invalid bundle: _meta must be a mapping"
        raise ValueError(msg)
    meta_data = cast("dict[str, Any]", data["_meta"])
    if meta_data.get("version") != BUNDLE_VERSION:
        msg = f"Unsupported bundle version: {meta_data.get('version')} (expected {BUNDLE_VERSION})"
        raise ValueError(msg)

    meta = BundleMeta.model_validate(meta_data)
    if not isinstance(data["profile"], dict):
        msg = "Invalid bundle: profile must be a mapping"
        raise ValueError(msg)
    profile_data = cast("dict[str, Any]", data["profile"])
    return ProfileBundle(meta=meta, profile=profile_data)


def import_profile(bundle: ProfileBundle) -> DeveloperProfile:
    """Reconstruct a DeveloperProfile from a bundle.

    Ensures machine-local fields are cleared regardless of bundle content.

    Args:
        bundle: The parsed profile bundle.

    Returns:
        DeveloperProfile with machine-local fields reset.
    """
    profile_data = dict(bundle.profile)
    profile_data["active_sessions"] = []
    profile_data["current_session"] = None
    profile_data["projects"] = []

    return DeveloperProfile.model_validate(profile_data)
