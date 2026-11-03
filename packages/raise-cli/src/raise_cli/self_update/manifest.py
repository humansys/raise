"""Re-export shim: raise_cli.self_update.manifest → raise_cli.core.manifest.

Canonical location moved to core/ (RAISE-16509 W9) so that session (T3)
can import without an upward waiver. All existing T2/T1 callers (self_update,
cli commands) continue to import from this shim — T2→T5 and T1→T2→T5 are
valid downward imports.
"""

from raise_cli.core.manifest import (
    DEFAULT_TIMEOUT,
    MANIFEST_URL,
    ArtifactRef,
    PlatformArtifact,
    VersionManifest,
    fetch_manifest,
    is_newer,
)

__all__ = [
    "ArtifactRef",
    "DEFAULT_TIMEOUT",
    "MANIFEST_URL",
    "PlatformArtifact",
    "VersionManifest",
    "fetch_manifest",
    "is_newer",
]
