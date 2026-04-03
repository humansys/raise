"""Skill manifest for tracking distributed skills and detecting upgrades.

The manifest (.raise/manifests/skills.json) stores per-file SHA256 hashes
of distributed skill files, enabling the dpkg three-hash algorithm for
safe upgrades: auto-update untouched files, keep customized, prompt on conflict.

The manifest also serves as the authoritative registry of RaiSE-managed skills
for the memory graph — skills not in the manifest are unmanaged.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from raise_cli.config.paths import MANIFESTS_SUBDIR, SKILLS_MANIFEST_FILE, get_raise_dir

logger = logging.getLogger(__name__)


class SkillSyncAction(StrEnum):
    """Classification of a skill's sync state using dpkg three-hash model."""

    CURRENT = "current"
    AUTO_UPDATE = "auto_update"
    KEEP_USER = "keep_user"
    CONFLICT = "conflict"
    NEW = "new"
    LEGACY = "legacy"


class SkillEntry(BaseModel):
    """Metadata for a single distributed skill file.

    Attributes:
        sha256: SHA256 hex digest of the SKILL.md content as written to disk.
        version: raise-cli version that distributed this skill.
        origin: Who distributed this skill ('framework' or 'org').
        distributed_at: When this skill was last written.
    """

    sha256: str
    version: str
    origin: str = "framework"
    distributed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SkillManifest(BaseModel):
    """Manifest tracking all distributed skills for upgrade detection.

    Attributes:
        schema_version: Manifest format version for forward compat.
        raise_cli_version: Which CLI version last wrote this manifest.
        distributed_at: When the manifest was last written.
        skills: Per-skill tracking entries keyed by skill name.
    """

    schema_version: str = "1.0"
    raise_cli_version: str = Field(default_factory=lambda: _get_cli_version())
    distributed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    skill_set: str | None = Field(
        default=None, description="Skill set name last deployed (None = builtins only)"
    )
    skills: dict[str, SkillEntry] = Field(default_factory=dict)


def _get_cli_version() -> str:
    """Get the current raise-cli version."""
    try:
        from raise_cli.skills_base import __version__

        return __version__
    except ImportError:
        return "unknown"


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hex digest of a string.

    Args:
        content: The text content to hash.

    Returns:
        64-character hex digest string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def classify_skill(
    hash_distributed: str | None,
    hash_on_disk: str,
    hash_new: str,
) -> SkillSyncAction:
    """Classify a skill's sync state using the dpkg three-hash algorithm.

    Args:
        hash_distributed: Hash of what we shipped last time (None if no manifest).
        hash_on_disk: Hash of the file currently on disk.
        hash_new: Hash of the new bundled version.

    Returns:
        SkillSyncAction indicating what to do with this skill.
    """
    if hash_distributed is None:
        return SkillSyncAction.LEGACY

    user_changed = hash_distributed != hash_on_disk
    upstream_changed = hash_distributed != hash_new

    if not user_changed and not upstream_changed:
        return SkillSyncAction.CURRENT

    if not user_changed and upstream_changed:
        return SkillSyncAction.AUTO_UPDATE

    if user_changed and not upstream_changed:
        return SkillSyncAction.KEEP_USER

    # Both changed — but if user's version matches new, they converged
    if hash_on_disk == hash_new:
        return SkillSyncAction.CURRENT

    return SkillSyncAction.CONFLICT


def save_skill_manifest(manifest: SkillManifest, project_root: Path) -> None:
    """Save skill manifest to .raise/manifests/skills.json.

    Creates directories if they don't exist.

    Args:
        manifest: The manifest to save.
        project_root: Root directory of the project.
    """
    manifest_dir = get_raise_dir(project_root) / MANIFESTS_SUBDIR
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / SKILLS_MANIFEST_FILE
    data = manifest.model_dump(mode="json")
    manifest_path.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )
    logger.debug("Saved skill manifest: %s", manifest_path)


def load_skill_manifest(project_root: Path) -> SkillManifest | None:
    """Load skill manifest from .raise/manifests/skills.json.

    Args:
        project_root: Root directory of the project.

    Returns:
        SkillManifest if file exists and is valid, None otherwise.
    """
    manifest_path = (
        get_raise_dir(project_root) / MANIFESTS_SUBDIR / SKILLS_MANIFEST_FILE
    )

    if not manifest_path.exists():
        logger.debug("Skill manifest not found: %s", manifest_path)
        return None

    try:
        content = manifest_path.read_text(encoding="utf-8")
        data = json.loads(content)
        return SkillManifest.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("Invalid skill manifest: %s", e)
        return None
