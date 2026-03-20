"""Scaffold bundled skills into a project with version-aware sync.

Copies RaiSE skills from the raise_cli.skills_base package to the project's
IDE skill directory during `rai init`. Uses the dpkg three-hash algorithm
to safely update skills: auto-update untouched files, keep customized,
prompt on conflict.

Uses importlib.resources to read bundled skill files (Python 3.9+).
Handles reference subdirectories (e.g., references/, _references/).

Example:
    from raise_cli.onboarding.skills import scaffold_skills

    result = scaffold_skills(project_path)
    if result.skills_updated:
        print(f"Updated {len(result.skills_updated)} skills")
"""

from __future__ import annotations

import logging
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.config.agent_plugin import AgentPlugin
from raise_cli.config.agents import AgentConfig, get_agent_config
from raise_cli.onboarding.skill_manifest import (
    SkillEntry,
    SkillManifest,
    SkillSyncAction,
    classify_skill,
    compute_content_hash,
    load_skill_manifest,
    save_skill_manifest,
)

logger = logging.getLogger(__name__)

SKILL_MD_FILENAME = "SKILL.md"


class SkillScaffoldResult(BaseModel):
    """Result of skill scaffolding operation."""

    # New sync-aware fields
    skills_installed: list[str] = Field(default_factory=list)
    skills_updated: list[str] = Field(default_factory=list)
    skills_conflicted: list[str] = Field(default_factory=list)
    skills_kept: list[str] = Field(default_factory=list)
    skills_overwritten: list[str] = Field(default_factory=list)
    skills_current: list[str] = Field(default_factory=list)

    # Backward-compat fields
    skills_copied: int = 0
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    skills_skipped_names: list[str] = Field(default_factory=list)


def _apply_plugin_transform(
    content: str,
    plugin: AgentPlugin,
    agent_config: AgentConfig,
) -> str:
    """Apply plugin.transform_skill to a SKILL.md content string."""
    import yaml

    from raise_cli.skills.parser import parse_frontmatter

    fm, body = parse_frontmatter(content)
    fm_out, body_out = plugin.transform_skill(fm, body, agent_config)
    # Re-serialize: frontmatter + body
    if fm_out:
        return f"---\n{yaml.dump(fm_out, default_flow_style=False, allow_unicode=True)}---\n{body_out}"
    return body_out


def _read_bundled_content(
    base: Traversable,
    skill_name: str,
    *,
    plugin: AgentPlugin | None = None,
    agent_config: AgentConfig | None = None,
) -> str:
    """Read bundled SKILL.md content, applying plugin transforms if needed.

    Args:
        base: The skills_base package traversable.
        skill_name: Name of the skill directory.
        plugin: Optional plugin for content transforms.
        agent_config: Agent config for plugin.

    Returns:
        The SKILL.md content as it would be written to disk.
    """
    raw = (base / skill_name / SKILL_MD_FILENAME).read_text(encoding="utf-8")
    if plugin is not None and agent_config is not None:
        raw = _apply_plugin_transform(raw, plugin, agent_config)
    return raw


def copy_skill_tree(
    source_dir: Path | Traversable,
    dest_dir: Path,
    result: SkillScaffoldResult,
    *,
    plugin: AgentPlugin | None = None,
    agent_config: AgentConfig | None = None,
    overwrite: bool = False,
) -> int:
    """Recursively copy skill files from source to destination.

    Accepts both importlib Traversable (for bundled skills) and Path
    (for filesystem overlay skills). Both types support iterdir(),
    is_file(), is_dir(), read_text(), and name. (AR R1, S340.1)

    Args:
        source_dir: Resource directory (Traversable or Path).
        dest_dir: Target directory on filesystem.
        result: Result object to track copied/skipped files.
        plugin: Optional plugin to transform SKILL.md files.
        agent_config: Agent config passed to plugin.
        overwrite: If True, overwrite existing files.

    Returns:
        Number of files copied.
    """
    copied = 0
    for item in source_dir.iterdir():
        if item.name in {"__init__.py", "__pycache__"}:
            continue
        dest = dest_dir / item.name
        if item.is_file():
            if dest.exists() and not overwrite:
                result.files_skipped.append(str(dest))
                logger.debug("Skipped (exists): %s", dest)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            raw_content = item.read_text(encoding="utf-8")
            if (
                plugin is not None
                and agent_config is not None
                and item.name == "SKILL.md"
            ):
                raw_content = _apply_plugin_transform(raw_content, plugin, agent_config)
            dest.write_text(raw_content, encoding="utf-8")
            result.files_copied.append(str(dest))
            copied += 1
            logger.debug("Copied: %s", dest)
        elif item.is_dir():
            copied += copy_skill_tree(
                item,
                dest,
                result,
                plugin=plugin,
                agent_config=agent_config,
                overwrite=overwrite,
            )
    return copied


def _get_cli_version() -> str:
    """Get current skills_base version for manifest."""
    try:
        from raise_cli.skills_base import __version__

        return __version__
    except ImportError:
        return "unknown"


def scaffold_skills(  # noqa: C901 -- multi-step scaffolding with many conditions; defer decomposition to S370.5
    project_root: Path,
    *,
    agent_config: AgentConfig | None = None,
    plugin: AgentPlugin | None = None,
    force: bool = False,
    skip_updates: bool = False,
    dry_run: bool = False,
    skill_set: str | None = None,
) -> SkillScaffoldResult:
    """Copy bundled skills to project skill directory with version-aware sync.

    Uses the dpkg three-hash algorithm to detect changes:
    - Untouched files are auto-updated silently
    - Customized files are preserved (user's version kept)
    - Conflicts (both changed) default to keep in non-interactive mode

    When ``skill_set`` is provided, overlay skills from
    ``.raise/skills/{skill_set}/`` are copied on top of builtins
    after the standard deployment. Same-name overlay wins. (S340.1)

    Args:
        project_root: Project root directory.
        agent_config: Agent configuration. Defaults to Claude.
        plugin: Optional plugin to transform SKILL.md files during copy.
        force: If True, overwrite all files without prompting.
        skip_updates: If True, only install new skills (legacy behavior).
        dry_run: If True, compute actions but don't write files.
        skill_set: Skill set name for overlay (e.g. "my-team").
            None = builtins only.

    Returns:
        SkillScaffoldResult with details of what was done.
    """
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    config = agent_config or get_agent_config()
    if config.skills_dir is None:
        return SkillScaffoldResult()

    base = files("raise_cli.skills_base")
    skills_dir = project_root / config.skills_dir
    result = SkillScaffoldResult()
    manifest = load_skill_manifest(project_root) or SkillManifest()
    cli_version = _get_cli_version()
    batch_keep = False
    batch_overwrite = False

    for skill_name in DISTRIBUTABLE_SKILLS:
        skill_dest = skills_dir / skill_name
        skill_md = skill_dest / SKILL_MD_FILENAME
        source = base / skill_name

        bundled_content = _read_bundled_content(
            base, skill_name, plugin=plugin, agent_config=config
        )
        hash_new = compute_content_hash(bundled_content)

        # --- Case: skill doesn't exist on disk → install ---
        if not skill_md.exists():
            if not dry_run:
                copied = copy_skill_tree(
                    source,
                    skill_dest,
                    result,
                    plugin=plugin,
                    agent_config=config,
                    overwrite=True,
                )
                manifest.skills[skill_name] = SkillEntry(
                    sha256=hash_new,
                    version=cli_version,
                )
                if copied > 0:
                    result.skills_copied += 1
            result.skills_installed.append(skill_name)
            continue

        # --- Skill exists on disk → classify with three-hash ---
        hash_on_disk = compute_content_hash(skill_md.read_text(encoding="utf-8"))
        entry = manifest.skills.get(skill_name)
        hash_distributed = entry.sha256 if entry else None

        action = classify_skill(hash_distributed, hash_on_disk, hash_new)

        if action == SkillSyncAction.CURRENT:
            result.skills_current.append(skill_name)
            # Ensure manifest entry exists (legacy fixup)
            if skill_name not in manifest.skills:
                manifest.skills[skill_name] = SkillEntry(
                    sha256=hash_on_disk,
                    version=cli_version,
                )

        elif action == SkillSyncAction.AUTO_UPDATE:
            if skip_updates:
                result.skills_current.append(skill_name)
                result.skills_skipped_names.append(skill_name)
            elif not dry_run:
                # Safe to overwrite — user hasn't touched it
                skill_md.write_text(bundled_content, encoding="utf-8")
                result.files_copied.append(str(skill_md))
                # Also update reference files
                copy_skill_tree(
                    source,
                    skill_dest,
                    result,
                    plugin=plugin,
                    agent_config=config,
                    overwrite=True,
                )
                manifest.skills[skill_name] = SkillEntry(
                    sha256=hash_new,
                    version=cli_version,
                )
                result.skills_updated.append(skill_name)
            else:
                result.skills_updated.append(skill_name)

        elif action == SkillSyncAction.KEEP_USER:
            result.skills_current.append(skill_name)
            result.skills_skipped_names.append(skill_name)

        elif action == SkillSyncAction.CONFLICT:
            if force or batch_overwrite:
                if not dry_run:
                    skill_md.write_text(bundled_content, encoding="utf-8")
                    result.files_copied.append(str(skill_md))
                    copy_skill_tree(
                        source,
                        skill_dest,
                        result,
                        plugin=plugin,
                        agent_config=config,
                        overwrite=True,
                    )
                    manifest.skills[skill_name] = SkillEntry(
                        sha256=hash_new,
                        version=cli_version,
                    )
                result.skills_overwritten.append(skill_name)
            elif skip_updates or batch_keep:
                result.skills_conflicted.append(skill_name)
                result.skills_skipped_names.append(skill_name)
            elif dry_run:
                result.skills_conflicted.append(skill_name)
            else:
                # Interactive conflict resolution
                from raise_cli.onboarding.skill_conflict import (
                    ConflictAction,
                    prompt_skill_conflict,
                )

                on_disk_content = skill_md.read_text(encoding="utf-8")
                user_action = prompt_skill_conflict(
                    skill_name,
                    on_disk_content,
                    bundled_content,
                )

                if user_action == ConflictAction.KEEP:
                    result.skills_kept.append(skill_name)
                elif user_action == ConflictAction.KEEP_ALL:
                    result.skills_kept.append(skill_name)
                    batch_keep = True
                elif user_action in (
                    ConflictAction.OVERWRITE,
                    ConflictAction.OVERWRITE_ALL,
                ):
                    skill_md.write_text(bundled_content, encoding="utf-8")
                    result.files_copied.append(str(skill_md))
                    copy_skill_tree(
                        source,
                        skill_dest,
                        result,
                        plugin=plugin,
                        agent_config=config,
                        overwrite=True,
                    )
                    manifest.skills[skill_name] = SkillEntry(
                        sha256=hash_new,
                        version=cli_version,
                    )
                    result.skills_overwritten.append(skill_name)
                    if user_action == ConflictAction.OVERWRITE_ALL:
                        batch_overwrite = True
                elif user_action == ConflictAction.BACKUP_OVERWRITE:
                    # Save backup before overwriting
                    backup_path = skill_md.with_suffix(".md.bak")
                    backup_path.write_text(on_disk_content, encoding="utf-8")
                    skill_md.write_text(bundled_content, encoding="utf-8")
                    result.files_copied.append(str(skill_md))
                    copy_skill_tree(
                        source,
                        skill_dest,
                        result,
                        plugin=plugin,
                        agent_config=config,
                        overwrite=True,
                    )
                    manifest.skills[skill_name] = SkillEntry(
                        sha256=hash_new,
                        version=cli_version,
                    )
                    result.skills_overwritten.append(skill_name)

        elif action == SkillSyncAction.LEGACY:
            # No manifest entry — first encounter
            if hash_on_disk == hash_new:
                # File matches bundled — safe to record
                manifest.skills[skill_name] = SkillEntry(
                    sha256=hash_new,
                    version=cli_version,
                )
            else:
                # File differs — treat as customized, record on-disk hash
                manifest.skills[skill_name] = SkillEntry(
                    sha256=hash_on_disk,
                    version=cli_version,
                )
            result.skills_current.append(skill_name)
            result.files_skipped.append(str(skill_md))
            result.skills_skipped_names.append(skill_name)

    # --- Skill set overlay (S340.1) ---
    if skill_set is not None and not dry_run:
        from raise_cli.config.paths import get_raise_dir

        overlay_dir = get_raise_dir(project_root) / "skills" / skill_set
        if overlay_dir.is_dir():
            for skill_dir in sorted(overlay_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                if not (skill_dir / SKILL_MD_FILENAME).exists():
                    continue
                copy_skill_tree(
                    skill_dir,
                    skills_dir / skill_dir.name,
                    result,
                    plugin=plugin,
                    agent_config=config,
                    overwrite=True,
                )
                overlay_content = (skill_dir / SKILL_MD_FILENAME).read_text(
                    encoding="utf-8"
                )
                manifest.skills[skill_dir.name] = SkillEntry(
                    sha256=compute_content_hash(overlay_content),
                    version=cli_version,
                    origin="project",
                )
            manifest.skill_set = skill_set
        else:
            logger.warning("Skill set '%s' not found at %s", skill_set, overlay_dir)

    # Update backward-compat flag
    result.already_existed = (
        len(result.skills_installed) == 0 and len(result.skills_updated) == 0
    )

    # Persist manifest
    if not dry_run:
        manifest.raise_cli_version = cli_version
        save_skill_manifest(manifest, project_root)

    return result
