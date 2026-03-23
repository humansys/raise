"""CLI commands for session management.

This module provides the `raise session` command group for managing
working sessions — the lifecycle of a developer's focused work period.

Sessions are first-class workflow state, distinct from:
- Profile (developer identity)
- Memory (persistent knowledge)

Example:
    $ raise session start              # Start a new session
    $ raise session start --context   # Start with context bundle
    $ raise session close              # End the current session
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from raise_cli.onboarding.skills import SkillScaffoldResult

import typer

from raise_cli.cli.commands.journal import journal_app
from raise_cli.cli.error_handler import cli_error
from raise_cli.exceptions import RaiSessionNotFoundError
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import (
    BeforeSessionCloseEvent,
    SessionCloseEvent,
    SessionStartEvent,
)
from raise_cli.memory.writer import validate_session_index
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    end_session,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
)
from raise_cli.schemas.session_state import SessionState
from raise_cli.session.bundle import assemble_context_bundle, assemble_sections
from raise_cli.session.close import CloseInput, load_state_file, process_session_close
from raise_cli.session.resolver import resolve_session_id
from raise_cli.session.identity import generate_session_id
from raise_cli.session.index import (
    ActiveSessionPointer,
    SessionIndexEntry,
    clear_active_session,
    read_active_session,
    read_session_entries,
    write_active_session,
    write_session_entry,
)
from raise_cli.session.prefix import PrefixRegistry
from raise_cli.session.state import (
    cleanup_session_dir,
    load_session_state,
    migrate_flat_to_session,
)

_ERR_NO_PROFILE = "No developer profile found"
_DOT_RAISE = ".raise"


def _get_current_branch() -> str:
    """Get current git branch name, or empty string if not in a repo."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _maybe_sync_skills(project_path: Path) -> SkillScaffoldResult | None:
    """Auto-sync skills if CLI version is newer than last deployed version.

    Compares raise_cli.__version__ against .raise/manifests/skills.json.
    If CLI is newer, runs scaffold_skills for each detected agent.

    Returns:
        SkillScaffoldResult if sync happened, None if skipped.
    """
    from raise_cli.onboarding.skill_manifest import load_skill_manifest

    manifest = load_skill_manifest(project_path)
    if manifest is None:
        return None

    from raise_cli import __version__ as cli_version

    if manifest.raise_cli_version == cli_version:
        return None

    # Version mismatch — sync skills
    from raise_cli.config.agent_registry import load_registry
    from raise_cli.onboarding.skills import scaffold_skills

    registry = load_registry(project_root=project_path)
    agent_types = registry.detect_agents(project_path)
    result: SkillScaffoldResult | None = None

    for agent_type in agent_types:
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)
        result = scaffold_skills(project_path, agent_config=config, plugin=plugin)

    # Report what happened
    if result is not None:
        parts: list[str] = []
        if result.skills_updated:
            parts.append(f"{len(result.skills_updated)} updated")
        if result.skills_installed:
            parts.append(f"{len(result.skills_installed)} new")
        if parts:
            typer.echo(f"Skills synced to {cli_version} ({', '.join(parts)})")

    return result


session_app = typer.Typer(
    name="session",
    help="Manage working sessions",
    no_args_is_help=True,
)
session_app.add_typer(journal_app, name="journal")


def _check_cwd_guard(
    profile: DeveloperProfile,
    session_id: str,
    close_project: Path,
) -> None:
    """Poka-yoke: reject session close if CWD project != session project.

    Compares the resolved absolute path of the close project against the
    project recorded in the ActiveSession. Raises cli_error on mismatch.

    Args:
        profile: Developer profile with active sessions.
        session_id: The session being closed.
        close_project: Project path from --project flag or CWD.
    """
    for active in profile.active_sessions:
        if active.session_id == session_id and active.project:
            session_path = Path(active.project).resolve()
            close_path = close_project.resolve()
            if session_path != close_path:
                cli_error(
                    f"CWD mismatch — session {session_id} started in "
                    f"{session_path} but close is running from {close_path}. "
                    f"Run from the correct project directory, or use "
                    f"--project {session_path}.",
                )
            break


@session_app.command()
def start(  # noqa: C901
    session_name: Annotated[
        str | None,
        typer.Argument(
            help="Session name (e.g., 'gemba research', 'epic design')",
        ),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Your name (required for first-time setup)",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path to associate with this session",
        ),
    ] = None,
    agent: Annotated[
        str | None,
        typer.Option(
            "--agent",
            help="Agent type (e.g., claude-code, cursor). Default: unknown",
        ),
    ] = None,
    context: Annotated[
        bool,
        typer.Option(
            "--context",
            help="Output a context bundle for AI consumption",
        ),
    ] = False,
) -> None:
    """Start a new working session.

    Increments the session counter and sets active session state.
    Checks for orphaned sessions (started but not closed) and warns if found.
    For first-time users, creates a new developer profile.

    With --context, outputs a token-optimized context bundle (~150 tokens)
    assembled from the developer profile, session state, and memory graph.

    Examples:
        $ raise session start                    # Start session
        $ raise session start --name "Alice"    # First-time setup
        $ raise session start --project /my/proj # Start with project path
        $ raise session start --project . --context  # Context bundle
    """
    profile = load_developer_profile()

    if profile is None:
        # First-time user - need name to create profile
        if name is None:
            cli_error(
                _ERR_NO_PROFILE,
                hint="Provide --name for first-time setup: raise session start --name 'Your Name'",
            )
            return  # cli_error raises, but this helps pyright

        # Create new profile
        profile = DeveloperProfile(name=name)
        typer.echo(f"Welcome to RaiSE, {name}! Creating your developer profile...")

    # Check for active session
    if profile.current_session is not None:
        prev = profile.current_session
        if prev.is_stale():
            typer.echo(
                f"Warning: Stale session detected (started {prev.started_at.date()}, "
                f"project: {prev.project})\n"
                "Previous session was not closed. Learnings may have been lost.\n"
                "Tip: Use /rai-session-close before ending work."
            )
        else:
            typer.echo(
                f"Note: Session already active (project: {prev.project})\n"
                "Starting new session anyway. Previous session not closed."
            )

    # Jidoka: Validate session index if project specified
    if project is not None:
        personal_dir = Path(project) / _DOT_RAISE / "rai" / "personal"
        if personal_dir.exists():
            validation = validate_session_index(personal_dir)
            if not validation.is_valid:
                typer.echo(f"Warning: {validation.summary()}")
                typer.echo("Run `raise memory validate` to fix data quality issues.\n")

    # Auto-sync skills if CLI was upgraded
    if project is not None:
        _maybe_sync_skills(Path(project))

    # Increment session count
    updated = increment_session(profile, project_path=project)

    # Generate session ID and add to active_sessions
    session_id: str | None = None
    prev_state: SessionState | None = None
    if project is not None:
        project_path_obj = Path(project)

        # Auto-register developer prefix
        from raise_cli.config.paths import get_prefixes_path

        prefixes_path = get_prefixes_path(project_path_obj)
        registry = PrefixRegistry.load(prefixes_path)
        dev_prefix = profile.get_pattern_prefix()
        try:
            registry.register(dev_prefix, profile.name)
            registry.save(prefixes_path)
        except ValueError:
            # Collision — use suggested extended prefix
            dev_prefix = registry.resolve_collision(dev_prefix, profile.name)
            registry.register(dev_prefix, profile.name)
            registry.save(prefixes_path)

        # Generate new-format session ID
        from datetime import datetime

        start_time = datetime.now()
        session_id = generate_session_id(dev_prefix, now=start_time)

        # Write active session pointer (carries name + start time to close)
        pointer = ActiveSessionPointer(
            id=session_id,
            name=session_name or "",
            started=start_time,
        )
        write_active_session(pointer, project_root=project_path_obj)

        # Load prior state before migration moves the flat file
        prev_state = load_session_state(Path(project))

        # Migrate flat files if they exist (before creating dir)
        migrate_flat_to_session(project_path_obj, session_id)

        # Ensure per-session directory exists
        from raise_cli.config.paths import get_session_dir

        session_dir = get_session_dir(session_id, project_path_obj)
        session_dir.mkdir(parents=True, exist_ok=True)

        # Add to active_sessions (with stale warning)
        agent_name = agent if agent else "unknown"
        updated, stale_sessions = start_session(
            updated, session_id=session_id, project_path=project, agent=agent_name
        )

        # Warn about stale sessions
        if stale_sessions:
            typer.echo("{WARN} Warning: Stale sessions detected (started >24h ago):")
            for stale in stale_sessions:
                typer.echo(
                    f"  - {stale.session_id} (started {stale.started_at.date()}, project: {stale.project})"
                )
            typer.echo(
                "Consider closing these sessions with: rai session close --session <ID>\n"
            )

    save_developer_profile(updated)

    # Emit session:start event
    emitter = create_emitter()
    emitter.emit(
        SessionStartEvent(
            session_id=session_id or "",
            developer=updated.name,
        )
    )

    # Format agent for output
    agent_name = agent if agent else "unknown"

    if context and project is not None:
        project_path = Path(project)
        state = prev_state
        bundle = assemble_context_bundle(
            updated, state, project_path, session_id=session_id
        )
        typer.echo(bundle)
    else:
        display_name = f" — {session_name}" if session_name else ""
        if session_id:
            typer.echo(f"▶ Session {session_id}{display_name} started ({agent_name})")
        else:
            typer.echo(f"▶ Session started ({agent_name})")
        typer.echo(f"Session recorded. (last: {updated.last_session})")


@session_app.command()
def context(
    sections: Annotated[
        str,
        typer.Option(
            "--sections",
            "-s",
            help="Comma-separated section names to load (e.g., 'governance,behavioral')",
        ),
    ],
    project: Annotated[
        str,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ],
) -> None:
    """Load specific context sections for AI consumption.

    Returns formatted priming sections selected by name. Use after
    `rai session start --context` to load task-relevant context.

    Available sections: governance, behavioral, coaching, deadlines, progress.

    Examples:
        $ raise session context --sections governance,behavioral --project .
        $ raise session context --sections coaching --project /my/proj
    """
    profile = load_developer_profile()
    if profile is None:
        cli_error(_ERR_NO_PROFILE)
        return

    project_path = Path(project)
    state = load_session_state(project_path)

    section_list = [s.strip() for s in sections.split(",") if s.strip()]

    try:
        output = assemble_sections(section_list, project_path, profile, state)
    except ValueError as e:
        cli_error(str(e))
        return

    if output:
        typer.echo(output)


@session_app.command()
def close(  # noqa: C901
    summary: Annotated[
        str | None,
        typer.Option(
            "--summary",
            "-s",
            help="Session summary",
        ),
    ] = None,
    session_type: Annotated[
        str | None,
        typer.Option(
            "--type",
            "-t",
            help="Session type (feature, research, maintenance, etc.)",
        ),
    ] = None,
    pattern: Annotated[
        str | None,
        typer.Option(
            "--pattern",
            help="Pattern description to record (format: 'description')",
        ),
    ] = None,
    correction: Annotated[
        str | None,
        typer.Option(
            "--correction",
            help="Coaching correction observed",
        ),
    ] = None,
    correction_lesson: Annotated[
        str | None,
        typer.Option(
            "--correction-lesson",
            help="Lesson from the correction",
        ),
    ] = None,
    state_file: Annotated[
        str | None,
        typer.Option(
            "--state-file",
            help="YAML file with full structured session output",
        ),
    ] = None,
    session: Annotated[
        str | None,
        typer.Option(
            "--session",
            help="Session ID to close (e.g., SES-177). Falls back to RAI_SESSION_ID env var.",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
) -> None:
    """End the current working session.

    With no flags: clears active session state (legacy behavior).
    With --summary or --state-file: performs full structured close —
    records session, patterns, corrections, and updates state.

    All writes are performed atomically by the CLI — skills should
    NOT call separate telemetry/memory commands.

    Examples:
        $ raise session close
        $ raise session close --summary "Session protocol design" --type feature
        $ raise session close --state-file /tmp/session-output.yaml --project .
    """
    profile = load_developer_profile()

    if profile is None:
        cli_error(_ERR_NO_PROFILE)
        return  # cli_error raises, but this helps pyright

    # Resolve session ID (from --session flag or RAI_SESSION_ID env var)
    resolved_session_id: str | None = None
    if session:
        import os

        try:
            resolved_session_id = resolve_session_id(
                session_flag=session, env_var=os.getenv("RAI_SESSION_ID")
            )
        except RaiSessionNotFoundError as e:
            cli_error(str(e))
            return

    # Determine if this is a structured close
    is_structured = summary is not None or state_file is not None

    if not is_structured:
        # Legacy behavior: just clear active session
        legacy_project = Path(project) if project else Path.cwd()
        if not resolved_session_id:
            # No session specified — find active session for THIS project
            resolved_project = legacy_project.resolve()
            for active in profile.active_sessions:
                if (
                    active.project
                    and Path(active.project).resolve() == resolved_project
                ):
                    resolved_session_id = active.session_id
                    break
            if not resolved_session_id:
                if not profile.active_sessions:
                    typer.echo("No active session to close.")
                else:
                    typer.echo("No active session for this project.")
                return

        # CWD poka-yoke: reject if project mismatch
        _check_cwd_guard(profile, resolved_session_id, legacy_project)

        # Emit before:session:close — hooks can abort
        emitter = create_emitter()
        before_result = emitter.emit(
            BeforeSessionCloseEvent(
                session_id=resolved_session_id,
                outcome="legacy",
            )
        )
        if before_result.aborted:
            typer.echo(f"Session close aborted: {before_result.abort_message}")
            raise typer.Exit(1)

        updated = end_session(profile, session_id=resolved_session_id)
        save_developer_profile(updated)

        emitter.emit(
            SessionCloseEvent(
                session_id=resolved_session_id,
                outcome="legacy",
            )
        )
        typer.echo(f"Session {resolved_session_id} closed.")
        return

    # Structured close: build CloseInput from flags or state file
    if state_file is not None:
        try:
            close_input = load_state_file(Path(state_file))
        except (FileNotFoundError, ValueError) as e:
            cli_error(f"Failed to load state file: {e}")
            return  # cli_error raises
    else:
        close_input = CloseInput(
            summary=summary or "",
            session_type=session_type or "feature",
        )

    # Coherence validation: reject if state file session_id
    # doesn't match the target session. Prevents race condition where
    # parallel sessions overwrite each other's state files.
    if (
        state_file is not None
        and close_input.session_id
        and resolved_session_id
        and close_input.session_id != resolved_session_id
    ):
        cli_error(
            f"State file session_id ({close_input.session_id}) does not match "
            f"target session ({resolved_session_id}).\n"
            f"The file may have been overwritten by a parallel session.\n"
            f"Re-run /rai-session-close to regenerate the state file.",
        )
        return  # cli_error raises

    # Override with CLI flags if provided alongside state file
    if pattern:
        close_input.patterns.append({"description": pattern, "type": "process"})
    if correction and correction_lesson:
        close_input.corrections.append(
            {"what": correction, "lesson": correction_lesson}
        )

    # Resolve project path
    project_path = Path(project) if project else Path.cwd()

    # CWD poka-yoke: reject if project mismatch
    # When no --session flag, find the active session for THIS project
    # (not just the first one — that may belong to a different project)
    guard_session_id = resolved_session_id
    if not guard_session_id and profile.active_sessions:
        resolved_project = project_path.resolve()
        for active in profile.active_sessions:
            if active.project and Path(active.project).resolve() == resolved_project:
                guard_session_id = active.session_id
                break
        # If no session matches this project, skip guard (no session to protect)
    if guard_session_id:
        _check_cwd_guard(profile, guard_session_id, project_path)

    # Emit before:session:close — hooks can abort
    emitter = create_emitter()
    close_sid = guard_session_id or resolved_session_id or ""
    before_result = emitter.emit(
        BeforeSessionCloseEvent(
            session_id=close_sid,
            outcome="structured",
        )
    )
    if before_result.aborted:
        typer.echo(f"Session close aborted: {before_result.abort_message}")
        raise typer.Exit(1)

    # Process close (pass session_id for per-session state writes)
    close_result = process_session_close(
        close_input, profile, project_path, session_id=resolved_session_id
    )

    # Write to shared session index (new registry) — only on success
    # Prefer active pointer ID (new format) over legacy close_result.session_id
    active_pointer = read_active_session(project_root=project_path)
    final_session_id = (
        resolved_session_id
        or (active_pointer.id if active_pointer is not None else None)
        or close_result.session_id
    )
    if final_session_id and close_result.success:
        from datetime import datetime

        close_time = datetime.now()
        dev_prefix = profile.get_pattern_prefix()
        session_name_val = (
            active_pointer.name
            if active_pointer is not None and active_pointer.name
            else close_input.summary or final_session_id
        )
        start_time = (
            active_pointer.started if active_pointer is not None else close_time
        )

        entry = SessionIndexEntry(
            id=final_session_id,
            name=session_name_val,
            started=start_time,
            closed=close_time,
            type=close_input.session_type,
            summary=close_input.summary,
            outcomes=close_input.outcomes,
            branch=_get_current_branch(),
        )
        write_session_entry(dev_prefix, entry, project_root=project_path)

    # Clear active session pointer (only if it matches this session)
    clear_active_session(
        session_id=(active_pointer.id if active_pointer is not None else final_session_id),
        project_root=project_path,
    )

    # Cleanup per-session directories (both new and legacy if different)
    if final_session_id:
        cleanup_session_dir(project_path, final_session_id)
    legacy_id = close_result.session_id
    if legacy_id and legacy_id != final_session_id:
        cleanup_session_dir(project_path, legacy_id)

    # Emit session:close event
    emitter.emit(
        SessionCloseEvent(
            session_id=close_result.session_id,
            outcome="structured",
        )
    )

    # Output summary
    display_id = final_session_id or close_result.session_id
    typer.echo(f"Session {display_id} closed.")
    if close_result.patterns_added > 0:
        typer.echo(f"  Patterns added: {close_result.patterns_added}")
    if close_result.corrections_added > 0:
        typer.echo(f"  Corrections recorded: {close_result.corrections_added}")


@session_app.command("list")
def list_sessions(
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            help="Maximum number of sessions to show",
        ),
    ] = 20,
) -> None:
    """List sessions from the shared session registry.

    Shows sessions recorded in .raise/rai/sessions/{prefix}/index.jsonl.
    Reads from the committed session index that travels with the repo.

    Examples:
        $ raise session list
        $ raise session list --limit 5
        $ raise session list --project /my/project
    """
    profile = load_developer_profile()
    if profile is None:
        cli_error("No developer profile found")
        return

    project_path = Path(project) if project else Path.cwd()
    dev_prefix = profile.get_pattern_prefix()
    entries = read_session_entries(dev_prefix, project_root=project_path)

    if not entries:
        typer.echo("No sessions found in shared registry.")
        typer.echo(
            "Sessions are recorded on close. "
            "Use `rai session start` + `rai session close` to create entries."
        )
        return

    # Show most recent first, limited
    recent = list(reversed(entries[-limit:]))

    # Detect active session
    active_pointer = read_active_session(project_root=project_path)
    active_id = active_pointer.id if active_pointer is not None else None

    typer.echo(f"Sessions for {profile.name} ({dev_prefix}):\n")
    for entry in recent:
        status = "(active)" if entry.id == active_id else ""
        date_str = entry.started.strftime("%Y-%m-%d %H:%M")
        closed_str = ""
        if entry.closed:
            duration_min = int((entry.closed - entry.started).total_seconds() / 60)
            if duration_min >= 60:
                closed_str = f", {duration_min // 60}h{duration_min % 60:02d}m"
            else:
                closed_str = f", {duration_min}m"
        typer.echo(f"  {entry.id}  {entry.name}  ({date_str}{closed_str}) {status}")

    typer.echo(f"\n{len(entries)} total sessions.")
