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
from dataclasses import dataclass
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


@dataclass
class _SkillSyncState:
    """Shared context threaded through skill sync helpers."""

    manifest: SkillManifest
    result: SkillScaffoldResult
    cli_version: str
    plugin: AgentPlugin | None
    agent_config: AgentConfig


def _get_cli_version() -> str:
    """Get current skills_base version for manifest."""
    try:
        from raise_cli.skills_base import __version__

        return __version__
    except ImportError:
        return "unknown"


def _apply_skill_write(
    skill_name: str,
    skill_md: Path,
    skill_dest: Path,
    source: Path | Traversable,
    bundled_content: str,
    hash_new: str,
    state: _SkillSyncState,
) -> None:
    """Write SKILL.md, copy tree, and update manifest (shared write pattern)."""
    skill_md.write_text(bundled_content, encoding="utf-8")
    state.result.files_copied.append(str(skill_md))
    copy_skill_tree(
        source,
        skill_dest,
        state.result,
        plugin=state.plugin,
        agent_config=state.agent_config,
        overwrite=True,
    )
    state.manifest.skills[skill_name] = SkillEntry(
        sha256=hash_new, version=state.cli_version
    )


def _handle_new_skill(
    skill_name: str,
    source: Path | Traversable,
    skill_dest: Path,
    hash_new: str,
    state: _SkillSyncState,
    *,
    dry_run: bool,
) -> None:
    """Install a skill that doesn't exist on disk yet."""
    if not dry_run:
        copied = copy_skill_tree(
            source,
            skill_dest,
            state.result,
            plugin=state.plugin,
            agent_config=state.agent_config,
            overwrite=True,
        )
        state.manifest.skills[skill_name] = SkillEntry(
            sha256=hash_new, version=state.cli_version
        )
        if copied > 0:
            state.result.skills_copied += 1
    state.result.skills_installed.append(skill_name)


def _handle_auto_update(
    skill_name: str,
    skill_md: Path,
    skill_dest: Path,
    source: Path | Traversable,
    bundled_content: str,
    hash_new: str,
    state: _SkillSyncState,
    *,
    skip_updates: bool,
    dry_run: bool,
) -> None:
    """Handle AUTO_UPDATE: safe to overwrite since user hasn't customized."""
    if skip_updates:
        state.result.skills_current.append(skill_name)
        state.result.skills_skipped_names.append(skill_name)
    elif not dry_run:
        _apply_skill_write(
            skill_name, skill_md, skill_dest, source, bundled_content, hash_new, state
        )
        state.result.skills_updated.append(skill_name)
    else:
        state.result.skills_updated.append(skill_name)


def _resolve_conflict_interactive(
    skill_name: str,
    skill_md: Path,
    skill_dest: Path,
    source: Path | Traversable,
    bundled_content: str,
    hash_new: str,
    state: _SkillSyncState,
) -> tuple[bool, bool]:
    """Prompt user to resolve a conflict. Returns (batch_keep, batch_overwrite)."""
    from raise_cli.onboarding.skill_conflict import (
        ConflictAction,
        prompt_skill_conflict,
    )

    on_disk_content = skill_md.read_text(encoding="utf-8")
    user_action = prompt_skill_conflict(skill_name, on_disk_content, bundled_content)

    if user_action == ConflictAction.KEEP:
        state.result.skills_kept.append(skill_name)
        return False, False
    if user_action == ConflictAction.KEEP_ALL:
        state.result.skills_kept.append(skill_name)
        return True, False
    if user_action in (ConflictAction.OVERWRITE, ConflictAction.OVERWRITE_ALL):
        _apply_skill_write(
            skill_name, skill_md, skill_dest, source, bundled_content, hash_new, state
        )
        state.result.skills_overwritten.append(skill_name)
        return False, user_action == ConflictAction.OVERWRITE_ALL
    if user_action == ConflictAction.BACKUP_OVERWRITE:
        skill_md.with_suffix(".md.bak").write_text(on_disk_content, encoding="utf-8")
        _apply_skill_write(
            skill_name, skill_md, skill_dest, source, bundled_content, hash_new, state
        )
        state.result.skills_overwritten.append(skill_name)
    return False, False


def _resolve_conflict(
    skill_name: str,
    skill_md: Path,
    skill_dest: Path,
    source: Path | Traversable,
    bundled_content: str,
    hash_new: str,
    state: _SkillSyncState,
    *,
    force: bool,
    skip_updates: bool,
    batch_overwrite: bool,
    batch_keep: bool,
    dry_run: bool,
) -> tuple[bool, bool]:
    """Handle CONFLICT action. Returns updated (batch_keep, batch_overwrite)."""
    if force or batch_overwrite:
        if not dry_run:
            _apply_skill_write(
                skill_name,
                skill_md,
                skill_dest,
                source,
                bundled_content,
                hash_new,
                state,
            )
        state.result.skills_overwritten.append(skill_name)
        return batch_keep, batch_overwrite
    if skip_updates or batch_keep:
        state.result.skills_conflicted.append(skill_name)
        state.result.skills_skipped_names.append(skill_name)
        return batch_keep, batch_overwrite
    if dry_run:
        state.result.skills_conflicted.append(skill_name)
        return batch_keep, batch_overwrite
    new_keep, new_overwrite = _resolve_conflict_interactive(
        skill_name, skill_md, skill_dest, source, bundled_content, hash_new, state
    )
    return batch_keep or new_keep, batch_overwrite or new_overwrite


def _apply_skill_set_overlay(
    project_root: Path,
    skills_dir: Path,
    skill_set: str,
    state: _SkillSyncState,
) -> None:
    """Copy skill-set overlay on top of builtins (S340.1)."""
    from raise_cli.config.paths import get_raise_dir

    overlay_dir = get_raise_dir(project_root) / "skills" / skill_set
    if not overlay_dir.is_dir():
        logger.warning("Skill set '%s' not found at %s", skill_set, overlay_dir)
        return
    for skill_dir in sorted(overlay_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / SKILL_MD_FILENAME).exists():
            continue
        copy_skill_tree(
            skill_dir,
            skills_dir / skill_dir.name,
            state.result,
            plugin=state.plugin,
            agent_config=state.agent_config,
            overwrite=True,
        )
        overlay_content = (skill_dir / SKILL_MD_FILENAME).read_text(encoding="utf-8")
        state.manifest.skills[skill_dir.name] = SkillEntry(
            sha256=compute_content_hash(overlay_content),
            version=state.cli_version,
            origin="project",
        )
    state.manifest.skill_set = skill_set


def _sync_skill(
    skill_name: str,
    source: Path | Traversable,
    skill_dest: Path,
    base: Traversable,
    state: _SkillSyncState,
    *,
    force: bool,
    skip_updates: bool,
    batch_overwrite: bool,
    batch_keep: bool,
    dry_run: bool,
) -> tuple[bool, bool]:
    """Process one skill: install if new, classify and sync if existing.

    Returns updated (batch_keep, batch_overwrite) for subsequent iterations.
    """
    skill_md = skill_dest / SKILL_MD_FILENAME
    bundled_content = _read_bundled_content(
        base, skill_name, plugin=state.plugin, agent_config=state.agent_config
    )
    hash_new = compute_content_hash(bundled_content)

    if not skill_md.exists():
        _handle_new_skill(
            skill_name, source, skill_dest, hash_new, state, dry_run=dry_run
        )
        return batch_keep, batch_overwrite

    hash_on_disk = compute_content_hash(skill_md.read_text(encoding="utf-8"))
    entry = state.manifest.skills.get(skill_name)
    action = classify_skill(entry.sha256 if entry else None, hash_on_disk, hash_new)

    if action == SkillSyncAction.CURRENT:
        state.result.skills_current.append(skill_name)
        if skill_name not in state.manifest.skills:
            state.manifest.skills[skill_name] = SkillEntry(
                sha256=hash_on_disk, version=state.cli_version
            )
    elif action == SkillSyncAction.AUTO_UPDATE:
        _handle_auto_update(
            skill_name,
            skill_md,
            skill_dest,
            source,
            bundled_content,
            hash_new,
            state,
            skip_updates=skip_updates,
            dry_run=dry_run,
        )
    elif action == SkillSyncAction.KEEP_USER:
        state.result.skills_current.append(skill_name)
        state.result.skills_skipped_names.append(skill_name)
    elif action == SkillSyncAction.CONFLICT:
        batch_keep, batch_overwrite = _resolve_conflict(
            skill_name,
            skill_md,
            skill_dest,
            source,
            bundled_content,
            hash_new,
            state,
            force=force,
            skip_updates=skip_updates,
            batch_overwrite=batch_overwrite,
            batch_keep=batch_keep,
            dry_run=dry_run,
        )
    elif action == SkillSyncAction.LEGACY:
        hash_to_record = hash_new if hash_on_disk == hash_new else hash_on_disk
        state.manifest.skills[skill_name] = SkillEntry(
            sha256=hash_to_record, version=state.cli_version
        )
        state.result.skills_current.append(skill_name)
        state.result.files_skipped.append(str(skill_md))
        state.result.skills_skipped_names.append(skill_name)

    return batch_keep, batch_overwrite


def scaffold_skills(
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
    state = _SkillSyncState(
        manifest=load_skill_manifest(project_root) or SkillManifest(),
        result=SkillScaffoldResult(),
        cli_version=_get_cli_version(),
        plugin=plugin,
        agent_config=config,
    )
    batch_keep = False
    batch_overwrite = False

    for skill_name in DISTRIBUTABLE_SKILLS:
        skill_dest = skills_dir / skill_name
        batch_keep, batch_overwrite = _sync_skill(
            skill_name,
            base / skill_name,
            skill_dest,
            base,
            state,
            force=force,
            skip_updates=skip_updates,
            batch_overwrite=batch_overwrite,
            batch_keep=batch_keep,
            dry_run=dry_run,
        )

    if skill_set is not None and not dry_run:
        _apply_skill_set_overlay(project_root, skills_dir, skill_set, state)

    state.result.already_existed = (
        len(state.result.skills_installed) == 0
        and len(state.result.skills_updated) == 0
    )

    if not dry_run:
        state.manifest.raise_cli_version = state.cli_version
        save_skill_manifest(state.manifest, project_root)

    return state.result
