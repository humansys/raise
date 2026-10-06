"""Session lifecycle orchestration — RAISE-17550 (E17495 S1).

Lives in the pipeline layer (Layer 1) so it can import raise_cli.onboarding
and raise_cli.hooks, which are Layer 1 siblings (forbidden from session Layer 2).

Types (SessionMeta, SessionOpenError) and helpers live in raise_cli.session.lifecycle.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from pathlib import Path

from raise_cli.session.lifecycle import SessionMeta, SessionOpenError

_log = logging.getLogger(__name__)


def _get_current_branch(project_path: Path) -> str:
    """Current git branch, best-effort — returns '' on any failure."""
    try:
        proc = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def _infer_agent_type(project_root: Path) -> str:
    """Infer agent type from .raise/manifest.yaml agents.types[0], or 'unknown'."""
    manifest_path = project_root / ".raise" / "manifest.yaml"
    if not manifest_path.exists():
        return "unknown"
    try:
        import yaml  # type: ignore[import-untyped]

        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            agents = raw.get("agents")
            if isinstance(agents, dict):
                types = agents.get("types")
                if isinstance(types, list) and types and isinstance(types[0], str):
                    return types[0]
    except Exception:  # noqa: BLE001,S110
        pass
    return "unknown"


def _sync_skills(project_path: Path) -> list[str]:
    """Sync skills for all detected agents; return summary parts."""
    from raise_cli.config.agent_registry import load_registry
    from raise_cli.onboarding.skills import scaffold_skills

    parts: list[str] = []
    registry = load_registry(project_root=project_path)
    for agent_type in registry.detect_agents(project_path):
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)
        result = scaffold_skills(project_path, agent_config=config, plugin=plugin)
        plugin.post_init(project_path, config)
        if result.skills_updated:
            parts.append(
                f"{len(result.skills_updated)} skills updated: {', '.join(result.skills_updated)}"
            )
        if result.skills_installed:
            parts.append(
                f"{len(result.skills_installed)} skills new: {', '.join(result.skills_installed)}"
            )
    return parts


def _maybe_auto_upgrade(project_path: Path) -> list[str]:
    """Auto-upgrade skills, patterns, methodology on version mismatch (D10).

    Compares raise_cli.__version__ against .raise/manifests/skills.json.
    Opt-out: RAI_NO_AUTO_UPGRADE=1. Returns summary parts (empty if skipped).
    """
    import os

    if os.environ.get("RAI_NO_AUTO_UPGRADE") == "1":
        return []

    from raise_cli.onboarding.skill_manifest import load_skill_manifest

    manifest = load_skill_manifest(project_path)
    if manifest is None:
        return []

    from raise_cli import __version__ as cli_version

    if manifest.raise_cli_version == cli_version:
        return []

    from raise_cli.onboarding.bootstrap import sync_base_patterns, sync_methodology

    parts = _sync_skills(project_path)

    pat_added, pat_updated = sync_base_patterns(project_path)
    if pat_added:
        parts.append(f"{pat_added} patterns new")
    if pat_updated:
        parts.append(f"{pat_updated} patterns updated")
    if sync_methodology(project_path):
        parts.append("methodology updated")

    if parts:
        _log.info("Auto-upgraded to %s (%s)", cli_version, ", ".join(parts))

    return parts


def ensure_session_lifecycle(
    project_path: Path,
    *,
    session_name: str | None = None,
    agent: str | None = None,
) -> SessionMeta:
    """Run the 23 session-start operations; return structured session metadata.

    Raises SessionOpenError when no developer profile exists (AC-07).
    Fail-open on migration errors — adds warning, continues (AC-04).
    Auto-upgrades skills/patterns on version mismatch (D10).
    Writes cc_session_id to the active session pointer (D-S1-06).
    """
    from raise_cli._agent_session import discover_agent_session_id
    from raise_cli.config.paths import get_prefixes_path, get_session_dir
    from raise_cli.hooks.emitter import create_emitter
    from raise_cli.hooks.events import SessionStartEvent
    from raise_cli.onboarding.profile import (
        increment_session,
        load_developer_profile,
        save_developer_profile,
        start_session,
    )
    from raise_cli.session import (
        ActiveSessionPointer,
        PrefixRegistry,
        SessionIndexEntry,
        migrate_flat_to_session,
        write_active_session,
        write_session_entry,
    )
    from raise_cli.session.donor import resolve_continuity_donor
    from raise_cli.session.identity import generate_session_id
    from raise_cli.session.state import load_session_state
    from raise_cli.storage.migrate import migrate_if_needed

    profile = load_developer_profile()
    if profile is None:
        raise SessionOpenError(
            "run rai session start --name to create your developer profile"
        )

    # D10: auto-upgrade before any session state mutation
    upgraded = _maybe_auto_upgrade(project_path)

    updated = increment_session(profile, project_path=str(project_path))

    # Auto-register developer prefix
    dev_prefix = profile.get_pattern_prefix()
    prefixes_path = get_prefixes_path(project_path)
    registry = PrefixRegistry.load(prefixes_path)
    try:
        registry.register(dev_prefix, profile.name)
        registry.save(prefixes_path)
    except ValueError:
        dev_prefix = registry.resolve_collision(dev_prefix, profile.name)
        registry.register(dev_prefix, profile.name)
        registry.save(prefixes_path)

    # Fail-open migration (AC-04)
    warnings: list[str] = []
    try:
        result = migrate_if_needed(project_path)
        if not result.success:
            warnings.append(f"migration: {'; '.join(result.errors)}")
    except Exception:  # noqa: BLE001
        warnings.append("migration failed — retry with rai data migrate")

    start_time = datetime.now()
    session_id = generate_session_id(dev_prefix, now=start_time)
    branch = _get_current_branch(project_path)

    start_entry = SessionIndexEntry(
        id=session_id,
        name=session_name or "",
        started=start_time,
        branch=branch,
    )
    write_session_entry(dev_prefix, start_entry, project_root=project_path)

    # Detect active worktree (best-effort)
    _wt_id = ""
    active_worktree = None
    try:
        from raise_cli.config.paths import resolve_checkout_root
        from raise_cli.storage.worktrees import SqliteWorktreeStore

        wt_store = SqliteWorktreeStore(project=project_path)
        _wt = wt_store.get_by_path(str(resolve_checkout_root()))
        if _wt.status == "open":
            active_worktree = _wt
            _wt_id = _wt.worktree_id
    except Exception:  # noqa: BLE001,S110
        pass

    # Write active session pointer WITH cc_session_id (D-S1-06)
    cc_sid = discover_agent_session_id() or ""
    pointer = ActiveSessionPointer(
        id=session_id,
        name=session_name or f"{dev_prefix}@{branch}",
        started=start_time,
        cc_session_id=cc_sid,
        worktree_id=_wt_id,
    )
    write_active_session(pointer, project_root=project_path)

    donor_decision = resolve_continuity_donor(
        project_path=project_path,
        developer_prefix=dev_prefix,
        active_worktree=active_worktree,
        load_state=load_session_state,
    )

    migrate_flat_to_session(project_path, session_id)

    session_dir = get_session_dir(session_id, project_path)
    session_dir.mkdir(parents=True, exist_ok=True)

    agent_name = agent or _infer_agent_type(project_path)
    updated, stale_sessions = start_session(
        updated,
        session_id=session_id,
        project_path=str(project_path),
        agent=agent_name,
        cc_session_id=cc_sid or None,
    )

    save_developer_profile(updated)

    emitter = create_emitter()
    emitter.emit(SessionStartEvent(session_id=session_id, developer=updated.name))

    return SessionMeta(
        session_id=session_id,
        started=start_time,
        worktree_id=_wt_id,
        donor_state=donor_decision.state,
        stale_sessions=stale_sessions,
        upgraded=upgraded,
        agent_session_id=cc_sid or None,
        warnings=warnings,
    )
