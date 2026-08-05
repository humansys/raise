"""CLI commands for session management.

This module provides the `rai session` command group for managing
working sessions — the lifecycle of a developer's focused work period.

Sessions are first-class workflow state, distinct from:
- Profile (developer identity)
- Memory (persistent knowledge)

Example:
    $ rai session start              # Start a new session
    $ rai session start --context   # Start with context bundle
    $ rai session close              # End the current session
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, cast

import typer

if TYPE_CHECKING:
    from raise_cli.onboarding.skills import SkillScaffoldResult
    from raise_cli.session.open_service import CheckResult
    from raise_cli.telemetry.emitter import UnifiedEmitter

import yaml

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.cli.commands.journal import journal_app
from raise_cli.cli.commands.ledger import ledger_app
from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import resolve_checkout_root
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
from raise_cli.schemas.session_state import CurrentWork, SessionInsights, SessionState
from raise_cli.session import (
    ActiveSessionPointer,
    CloseInput,
    PrefixRegistry,
    SessionIndexEntry,
    assemble_context_bundle,
    assemble_sections,
    cleanup_session_dir,
    clear_active_session,
    count_missing_prefix_sessions,
    find_last_closed_in_scope,
    generate_session_id,
    load_session_state,
    load_state_file,
    migrate_flat_to_session,
    process_session_close,
    read_active_session,
    read_session_entries,
    resolve_session_id,
    write_active_session,
    write_session_entry,
)
from raise_cli.session.donor import ContinuityDonorDecision, resolve_continuity_donor
from raise_cli.session.scope import resolve_scope

logger = logging.getLogger(__name__)

_ERR_NO_PROFILE = "No developer profile found"
_DOT_RAISE = ".raise"


def _get_session_insights(
    project_path: Path, session_id: str
) -> SessionInsights | None:
    """Get session insights from WorkstreamMonitor, or None on failure."""
    try:
        from raise_cli.session.monitor import LocalWorkstreamMonitor

        monitor = LocalWorkstreamMonitor(project_path)
        return monitor.analyze_session(session_id)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Session insights failed — skipping", exc_info=True)
        return None


def _format_insights(insights: SessionInsights) -> str:
    """Format session insights for CLI output."""
    test_pct = f"{insights.test_commit_ratio:.0%}"
    return (
        f"  Session insights: {insights.commit_count} commits | "
        f"Test ratio: {test_pct} | "
        f"Reverts: {insights.revert_count} | "
        f"Duration: {insights.duration_minutes}m"
    )


def _format_token_summary(totals: dict[str, int]) -> str:
    """Format per-phase token totals as a plain-text summary block."""
    lines = ["Token Summary (current session)"]
    for phase in sorted(totals):
        lines.append(f"  {phase:<16} {totals[phase]:>10,}")
    lines.append("  " + "─" * 26)
    grand_total = sum(totals.values())
    lines.append(f"  {'Total':<16} {grand_total:>10,}")
    return "\n".join(lines)


def _emit_replay_events(
    project_path: Path,
    session_id: str,
    *,
    work_ref: str | None,
    repo_slug: str | None,
    emitter: UnifiedEmitter,
) -> None:
    """Emit per-skill replay events. Called from _emit_token_usage_daily.

    Silent on any failure — called inside contextlib.suppress(Exception).
    Scans the current session JSONL, builds one token_usage_daily event per
    skill, and posts each. Fire-and-forget; never blocks session close (D6).
    """
    from raise_cli._agent_session import (
        discover_agent_runtime,
        discover_agent_session_id,
    )
    from raise_cli.telemetry.cost_report import scan_single_session
    from raise_cli.telemetry.session_tokens import (
        build_replay_events,
        find_current_session_jsonl,
    )

    jsonl = find_current_session_jsonl(project_path)
    if jsonl is None:
        return
    report = scan_single_session(jsonl)
    if not report.skills:
        return

    from datetime import UTC, datetime

    events = build_replay_events(
        report,
        session_id=session_id,
        date=datetime.now(UTC).strftime("%Y-%m-%d"),
        repo_slug=repo_slug or "",
        work_item_ref=work_ref,
        agent_id=discover_agent_session_id(),
        runtime=discover_agent_runtime(),
    )
    for ev in events:
        emitter.post_direct(ev)


def _emit_token_usage_daily(project_path: Path, session_id: str) -> None:
    """Extract token totals from CC JSONL and POST token_usage_daily to server.

    Posts the aggregate token_usage_daily event, then calls _emit_replay_events
    to post per-skill breakdown events. Silent on any failure — must never
    block session close.
    """
    import contextlib

    from raise_cli.config.server import get_server_credentials
    from raise_cli.telemetry.session_tokens import (
        build_token_usage_daily_event,
        get_session_token_totals,
    )

    with contextlib.suppress(Exception):
        totals = get_session_token_totals(project_path)
        if totals is None:
            return

        if get_server_credentials() is None:
            return

        from raise_cli.pipeline.mcp_tools_session import (
            _resolve_session_jira_key,  # noqa: PLC2701  # pyright: ignore[reportPrivateUsage]
        )
        from raise_cli.storage.connection import get_project_id

        work_ref = (
            _resolve_session_jira_key()
        )  # passes None → uses discover_agent_session_id()

        repo_slug = get_project_id(resolve_checkout_root())

        event = build_token_usage_daily_event(
            totals,
            session_id=session_id,
            work_item_ref=work_ref,
            repo_slug=repo_slug,
        )

        from raise_cli.telemetry.emitter import UnifiedEmitter

        emitter = UnifiedEmitter(project_root=project_path)
        emitter.post_direct(event)

        _emit_replay_events(
            project_path,
            session_id,
            work_ref=work_ref,
            repo_slug=repo_slug,
            emitter=emitter,
        )


def _emit_story_cost_summary(
    project_path: Path,
    session_id: str,
    *,
    story_id: str | None = None,
) -> None:
    """Compute story-scoped cost and POST story_cost_summary event to server.

    Mirrors _emit_token_usage_daily: fire-and-forget, never blocks session/story close.
    No-op when: RAISE_SERVER_URL+RAISE_API_KEY absent, no active story key, or
    no JSONL found. Falls back to full-session window when lifecycle signals missing.

    Args:
        project_path: Project root for DB and JSONL lookup.
        session_id: CC session ID (JSONL stem).
        story_id: Story identifier in story_id format (e.g. "S6456.2").
            When provided, used to query SQLite for lifecycle timestamps.
            When None (session-close path), lifecycle window is not available
            and the full-session fallback is used.
    """
    import contextlib
    import os

    from raise_cli.config.server import get_server_credentials

    with contextlib.suppress(Exception):
        if get_server_credentials() is None:
            return

        from raise_cli.pipeline.mcp_tools_session import (
            _resolve_session_jira_key,  # noqa: PLC2701  # pyright: ignore[reportPrivateUsage]
        )

        jira_key = _resolve_session_jira_key()
        if jira_key is None:
            return  # no active story — no-op (AC5)

        from raise_cli.telemetry.session_tokens import (
            build_story_cost_summary_event,
            find_current_session_jsonl,
            story_window,
        )

        jsonl = find_current_session_jsonl(project_path)
        if jsonl is None:
            return

        # story_window now queries SQLite using story_id (e.g. "S6456.2").
        # When story_id is None (session-close path) we skip the window lookup.
        window = story_window(project_path, story_id) if story_id is not None else None
        since, until = (window[0], window[1]) if window is not None else (None, None)

        from raise_cli.telemetry.cost_report import scan_single_session

        report = scan_single_session(jsonl, since=since, until=until)

        # Circuit breaker: warn or block when cost exceeds rolling avg (S8741.1).
        # Fail-open: any error returns 0.0 → no trigger.
        from raise_cli.storage.connection import get_project_db_path
        from raise_cli.telemetry.guardrails import (
            check_circuit_breaker,
            rolling_avg_from_sqlite,
        )

        _cb_multiplier = float(os.getenv("RAISE_CIRCUIT_BREAKER_MULTIPLIER", "2.5"))
        _cb_db_path = get_project_db_path(project_path)
        _cb_avg = rolling_avg_from_sqlite(_cb_db_path)
        _cb_result = check_circuit_breaker(report, _cb_avg, _cb_multiplier)
        if _cb_result.triggered:
            logger.warning(
                "circuit-breaker[%s]: %s", _cb_result.severity, _cb_result.reason
            )
            if _cb_result.severity == "block":
                from raise_cli.telemetry.emit_work import emit_work_lifecycle

                _active_story = story_id or jira_key
                emit_work_lifecycle(
                    "story", _active_story, "blocked", "guardrail-circuit-breaker"
                )

        from raise_cli._agent_session import (
            discover_agent_runtime,
            discover_agent_session_id,
        )
        from raise_cli.storage.connection import get_project_id

        repo_slug = get_project_id(resolve_checkout_root())

        resolved_sid = session_id or discover_agent_session_id() or jsonl.stem
        event = build_story_cost_summary_event(
            report,
            story_id=story_id or jira_key,
            jira_key=jira_key,
            session_id=resolved_sid,
            repo_slug=repo_slug,
            agent_id=discover_agent_session_id(),
            runtime=discover_agent_runtime(),
            since=since,
            until=until,
        )

        from raise_cli.telemetry.emitter import UnifiedEmitter

        emitter = UnifiedEmitter(project_root=project_path)
        emitter.post_direct(event)


def _show_token_summary(project_path: Path) -> None:
    """Print per-phase token summary from current session JSONL. Silent on failure."""
    from raise_cli.telemetry.session_tokens import get_session_token_summary

    try:
        totals = get_session_token_summary(project_path)
    except Exception:  # noqa: BLE001
        return
    if totals:
        typer.echo(_format_token_summary(totals))


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


def _infer_agent_type(project_root: Path) -> str:
    """Infer agent type from manifest.yaml, falling back to 'unknown'."""
    manifest_path = project_root / ".raise" / "manifest.yaml"
    if manifest_path.exists():
        try:
            raw_data: object = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if isinstance(raw_data, dict):
                data = cast("dict[str, object]", raw_data)
                agents = data.get("agents")
                if isinstance(agents, dict):
                    agent_data = cast("dict[str, object]", agents)
                    agent_types = agent_data.get("types")
                    if isinstance(agent_types, list) and agent_types:
                        typed_agent_types = cast("list[object]", agent_types)
                        first_agent_type = typed_agent_types[0]
                        if isinstance(first_agent_type, str):
                            return first_agent_type
        except (OSError, yaml.YAMLError):  # noqa: S110
            pass
    return "unknown"


def _sync_skills(project_path: Path) -> tuple[SkillScaffoldResult | None, list[str]]:
    """Sync skills and return result + summary parts."""
    from raise_cli.config.agent_registry import load_registry
    from raise_cli.onboarding.skills import scaffold_skills

    registry = load_registry(project_root=project_path)
    agent_types = registry.detect_agents(project_path)
    result: SkillScaffoldResult | None = None

    for agent_type in agent_types:
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)
        result = scaffold_skills(project_path, agent_config=config, plugin=plugin)
        plugin.post_init(project_path, config)

    parts: list[str] = []
    if result is not None:
        if result.skills_updated:
            parts.append(f"{len(result.skills_updated)} skills updated")
        if result.skills_installed:
            parts.append(f"{len(result.skills_installed)} skills new")
    return result, parts


def _maybe_auto_upgrade(project_path: Path) -> SkillScaffoldResult | None:
    """Auto-upgrade skills, patterns, and methodology on version mismatch.

    Compares raise_cli.__version__ against .raise/manifests/skills.json.
    If CLI is newer, syncs skills, base patterns, and methodology.

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

    from raise_cli.onboarding.bootstrap import sync_base_patterns, sync_methodology

    result, parts = _sync_skills(project_path)

    pat_added, pat_updated = sync_base_patterns(project_path)
    if pat_added:
        parts.append(f"{pat_added} patterns new")
    if pat_updated:
        parts.append(f"{pat_updated} patterns updated")

    if sync_methodology(project_path):
        parts.append("methodology updated")

    if parts:
        typer.echo(f"Auto-upgraded to {cli_version} ({', '.join(parts)})")

    return result


session_app = typer.Typer(
    name="session",
    help="Manage working sessions",
    no_args_is_help=True,
)
session_app.add_typer(journal_app, name="journal")
session_app.add_typer(ledger_app, name="ledger")


@session_app.command()
def bind(
    key: Annotated[
        str, typer.Argument(help="Context key (e.g. RAISE_SESSION_JIRA_KEY)")
    ],
    value: Annotated[str, typer.Argument(help="Value to bind")],
) -> None:
    """Write a key=value pair to the per-session context.env file."""
    from raise_cli._agent_session import discover_agent_session_id
    from raise_cli.session.context_env import write_context_env

    session_id = discover_agent_session_id()
    if not session_id:
        cli_error(
            "No active agent session detected — RAISE_CC_SESSION_ID is not set "
            "and port/PID discovery found no match. Run inside a CC session."
        )
        raise typer.Exit(code=1)

    project = Path.cwd()
    try:
        write_context_env(project, session_id, key, value)
    except ValueError as exc:
        cli_error(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo(f"Bound {key}={value} to session {session_id}")


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


def resolve_close_guard(
    profile: DeveloperProfile,
    project_path: Path,
    resolved_session_id: str | None,
) -> tuple[str | None, bool]:
    """Resolve which active session to close and whether it was found via CC ID.

    Returns ``(session_id, resolved_via_cc)``.  When ``resolved_via_cc`` is
    True the caller should skip the CWD-mismatch check — the CC session ID
    IS the identity signal; the path difference is expected by design (RAISE-14592).
    """
    if resolved_session_id:
        return resolved_session_id, False

    if not profile.active_sessions:
        return None, False

    resolved_project = project_path.resolve()
    for active in profile.active_sessions:
        if active.project and Path(active.project).resolve() == resolved_project:
            return active.session_id, False

    # RAISE-14592: CC session ID fallback when path lookup fails.
    # A CC session may visit multiple directories; the active_session entry
    # was written for the original project dir, not for the current one.
    cc_sid = discover_agent_session_id()
    if cc_sid:
        for active in profile.active_sessions:
            if active.cc_session_id == cc_sid:
                return active.session_id, True

    return None, False


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
    no_doctor: Annotated[
        bool,
        typer.Option(
            "--no-doctor",
            help="Skip session health check (for CI/automation)",
        ),
    ] = False,
    fleet: Annotated[
        bool,
        typer.Option(
            "--fleet",
            # Hidden with the fleet surface it describes (RAISE-15618). The
            # flag is also a no-op: its whole body is one typer.echo, it writes
            # no session metadata. `mcp_tools_fleet.py`'s claim that it
            # "controls session metadata only" is stale — it controls nothing.
            # Kept rather than deleted so existing scripts passing it do not
            # break; concealment, not removal, same as the command groups.
            hidden=True,
            help=(
                "Print the Fleet Director banner. Experimental: the fleet MCP "
                "tools are registered only when the MCP server is launched with "
                "RAISE_EXPERIMENTAL=1 (RAISE-15618)."
            ),
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
        $ rai session start                    # Start session
        $ rai session start --name "Alice"    # First-time setup
        $ rai session start --project /my/proj # Start with project path
        $ rai session start --project . --context  # Context bundle
    """
    profile = load_developer_profile()

    if profile is None:
        # First-time user - need name to create profile
        if name is None:
            cli_error(
                _ERR_NO_PROFILE,
                hint="Provide --name for first-time setup: rai session start --name 'Your Name'",
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
                typer.echo("Run `rai memory validate` to fix data quality issues.\n")

    # Session Doctor: diagnose and auto-clean safe issues
    if project is not None and not no_doctor:
        try:
            from raise_cli.session.doctor import SessionDoctor, format_findings

            doctor = SessionDoctor(Path(project))
            findings = doctor.diagnose()
            if findings:
                plan = doctor.classify(findings)
                cleaned = doctor.execute(plan, consent={"auto"})
                typer.echo(format_findings(findings, cleaned))
            else:
                typer.echo("Session health: clean (0 issues)")
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Session doctor failed — continuing", exc_info=True)

    # Normalize project path to absolute (prevents duplicates from ., ./, etc.)
    if project is not None:
        project = str(Path(project).resolve())

    # Auto-upgrade skills, patterns, methodology if CLI was upgraded
    if project is not None:
        _maybe_auto_upgrade(Path(project))

    # Increment session count
    updated = increment_session(profile, project_path=project)

    # Generate session ID and add to active_sessions
    session_id: str | None = None
    prev_state: SessionState | None = None
    agent_name: str = agent or "unknown"
    active_worktree = None
    donor_decision: ContinuityDonorDecision | None = None
    if project is not None:
        project_path_obj = Path(project).resolve()

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

        # Auto-migrate legacy JSONL/YAML data on first session start.
        # Result is shown to the user — silent mutation erodes trust (RAISE-5929).
        try:
            from raise_cli.storage.migrate import migrate_if_needed

            result = migrate_if_needed(project_path_obj)
            if not result.success:
                typer.echo(
                    f"! Data migration had issues: {'; '.join(result.errors)}",
                    err=True,
                )
            elif result.sessions or result.journals or result.signals:
                typer.echo(f"Migrated: {result.message}")
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            typer.echo(
                "! Legacy data migration failed — "
                "your data is safe but was not imported. "
                "Run `rai data migrate` to retry.",
                err=True,
            )

        # Generate new-format session ID
        from datetime import datetime

        start_time = datetime.now()
        session_id = generate_session_id(dev_prefix, now=start_time)

        # Record session in sessions table (closed=None until session close).
        # Must happen BEFORE write_active_session so the invariant holds:
        # active pointer always has a matching sessions row.
        start_entry = SessionIndexEntry(
            id=session_id,
            name=session_name or "",
            started=start_time,
            branch=_get_current_branch(),
        )
        write_session_entry(dev_prefix, start_entry, project_root=project_path_obj)

        # Detect if CWD is an open registered worktree — used for narrative fix,
        # Worktree Context section injection, and the new worktree_id field on the
        # active session pointer (RAISE-15131). Detection must happen BEFORE writing
        # the pointer so worktree_id is persisted from the first write.
        active_worktree = None
        _wt_id = ""
        try:
            from raise_cli.storage.worktrees import (
                SqliteWorktreeStore,
            )

            wt_store = SqliteWorktreeStore(project=project_path_obj)
            _wt = wt_store.get_by_path(str(resolve_checkout_root()))
            if _wt.status == "open":
                active_worktree = _wt
                _wt_id = _wt.worktree_id
        except Exception:  # noqa: BLE001,S110
            pass

        # Write active session pointer (carries name + start time to close).
        # Name fallback: dev_prefix@branch so the Sessions tab always shows
        # something human-readable (fixes the empty-name bug reported in DESIGN.md).
        _branch = _get_current_branch()
        pointer = ActiveSessionPointer(
            id=session_id,
            name=session_name or f"{dev_prefix}@{_branch}",
            started=start_time,
            worktree_id=_wt_id,
        )
        write_active_session(pointer, project_root=project_path_obj)

        donor_decision = resolve_continuity_donor(
            project_path=project_path_obj,
            developer_prefix=dev_prefix,
            active_worktree=active_worktree,
            load_state=load_session_state,
        )
        prev_state = donor_decision.state

        # Migrate legacy flat files (if any) into a per-session directory.
        # Must run BEFORE session_dir.mkdir — migration skips if the target dir
        # already exists.
        migrate_flat_to_session(project_path_obj, session_id)

        # Ensure per-session directory exists
        from raise_cli.config.paths import get_session_dir

        session_dir = get_session_dir(session_id, project_path_obj)
        session_dir.mkdir(parents=True, exist_ok=True)

        # Add to active_sessions (infer agent from manifest if not explicit)
        agent_name = agent or _infer_agent_type(project_path_obj)
        updated, stale_sessions = start_session(
            updated,
            session_id=session_id,
            project_path=project,
            agent=agent_name,
            cc_session_id=discover_agent_session_id(),
        )

        # Warn about stale sessions (summarized — avoid noise before context)
        if stale_sessions:
            count = len(stale_sessions)
            projects = sorted({s.project for s in stale_sessions})
            if count <= 3:
                for stale in stale_sessions:
                    typer.echo(
                        f"{{WARN}} Stale session: {stale.session_id} "
                        f"(started {stale.started_at.date()}, project: {stale.project})"
                    )
            else:
                project_list = ", ".join(projects[:3])
                suffix = f" +{len(projects) - 3} more" if len(projects) > 3 else ""
                typer.echo(
                    f"{{WARN}} {count} stale sessions across "
                    f"{len(projects)} projects ({project_list}{suffix})"
                )
            typer.echo(
                "Close with: rai session close --session <ID>  (use --session for each)\\n"
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

    # agent_name already resolved (from manifest in project branch, or default)

    # Regenerate Claude Code MEMORY.md for mission-scoped memory
    if project is not None:
        try:
            from raise_cli.config.paths import get_claude_memory_dir
            from raise_cli.memory.memory_index import regenerate_memory_index

            memory_dir = get_claude_memory_dir(Path(project).resolve())
            if memory_dir.exists():
                regenerate_memory_index(memory_dir)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Memory index regeneration failed", exc_info=True)

    # Pattern sync: pull from server + drain outbox (transparent, non-blocking)
    if project is not None:
        try:
            from raise_cli.storage.connection import get_project_db, get_project_id
            from raise_cli.storage.schema import create_all as ensure_schema

            project_path = Path(project).resolve()
            sync_conn = get_project_db(project_path)
            ensure_schema(sync_conn)
            pid = get_project_id(project_path)

            from raise_cli.memory.sync import (
                drain_outbox,
                maybe_backfill_outbox,
                pull_governance,
                pull_patterns,
            )

            backfill = maybe_backfill_outbox(sync_conn)
            if backfill.get("enqueued", 0) > 0:
                typer.echo(
                    f"Initial sync: {backfill['enqueued']} local patterns "
                    f"queued for push"
                )

            pull_result = cast(
                "dict[str, Any]", pull_patterns(sync_conn, project_id=pid)
            )
            drain_result = cast(
                "dict[str, Any]", drain_outbox(sync_conn, project_id=pid)
            )

            synced_parts: list[str] = []
            if pull_result["pulled"]:
                synced_parts.append(
                    f"pulled {pull_result['pulled']} "
                    f"({pull_result['new']} new, {pull_result['updated']} updated)"
                )
            if drain_result["pushed"]:
                synced_parts.append(f"pushed {drain_result['pushed']} pending")
            if synced_parts:
                typer.echo(f"Pattern sync: {', '.join(synced_parts)}")

            gov_result = pull_governance(sync_conn, pid)
            if gov_result.get("synced"):
                typer.echo(
                    f"Governance sync: {gov_result['projects']} projects, "
                    f"{gov_result['rules']} rules"
                )
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Sync failed — continuing", exc_info=True)

    if context and project is not None:
        project_path = Path(project).resolve()
        state = prev_state
        bundle = assemble_context_bundle(
            updated,
            state,
            project_path,
            session_id=session_id,
            worktree=active_worktree,
            donor_decision=donor_decision,
        )
        typer.echo(bundle)
    else:
        display_name = f" — {session_name}" if session_name else ""
        if session_id:
            typer.echo(f"▶ Session {session_id}{display_name} started ({agent_name})")
        else:
            typer.echo(f"▶ Session started ({agent_name})")
        typer.echo(f"Session recorded. (last: {updated.last_session})")

    if fleet:
        # This CLI process cannot know whether the fleet tools are registered:
        # registration happens at import time in the MCP server, a separate
        # long-lived process that inherits its env from the client's launch
        # config (.mcp.json), not from this shell. An availability claim here
        # would be a cross-process guess — wrong in both directions, and the
        # same false-evidence defect RAISE-15618 exists to remove. State the
        # requirement, never the state.
        typer.echo(
            "⚡ Fleet Director activado\n"
            "   MCP tools: fleet_dispatch · fleet_status · fleet_approve · "
            "fleet_signal\n"
            "   Experimental: registered only when the MCP server is launched "
            "with RAISE_EXPERIMENTAL=1 (env block in .mcp.json + client restart)."
        )


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
    session: Annotated[
        str,
        typer.Option(
            "--session",
            help=(
                "Explicit agent session_id override (RAISE-9886 idiom). "
                "Bypasses env discovery for the ledger section — use when "
                "surfacing under a different session than the ambient env "
                "would resolve (RAISE-13146 AR F1), symmetric with "
                "raise_ledger_add's agent_session_id override. "
                "Also overrides the donor scope for context/measure."
            ),
        ),
    ] = "",
) -> None:
    """Load specific context sections for AI consumption.

    Returns formatted priming sections selected by name. Use after
    `rai session start --context` to load task-relevant context.

    Available sections: governance, behavioral, coaching, deadlines, progress, ledger.

    Examples:
        $ rai session context --sections governance,behavioral --project .
        $ rai session context --sections coaching --project /my/proj
        $ rai session context --sections ledger --project . --session cc-uuid-x
    """
    profile = load_developer_profile()
    if profile is None:
        cli_error(_ERR_NO_PROFILE)
        return

    project_path = Path(project).resolve()
    dev_prefix = profile.get_pattern_prefix()
    agent_session_id = session or None  # --session flag: explicit override wins
    scope = resolve_scope(project_path, agent_session_id)
    last_closed_id = find_last_closed_in_scope(
        dev_prefix, scope, project_root=project_path
    )
    if last_closed_id:
        state = load_session_state(project_path, session_id=last_closed_id)
    else:
        state = load_session_state(project_path)

    section_list = [s.strip() for s in sections.split(",") if s.strip()]

    try:
        output = assemble_sections(
            section_list, project_path, profile, state, agent_session_id
        )
    except ValueError as e:
        cli_error(str(e))
        return

    if output:
        typer.echo(output)


@session_app.command()
def measure(
    fmt: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
    include_agents_md: Annotated[
        bool,
        typer.Option(
            "--include-agents-md",
            help="Include AGENTS.md token count",
        ),
    ] = False,
    project: Annotated[
        str,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = ".",
) -> None:
    """Measure token counts of session context sections.

    Produces per-section breakdown of the session bundle and optionally
    AGENTS.md, with totals and percentage of 200K context window.

    Examples:
        $ rai session measure
        $ rai session measure --format json
        $ rai session measure --include-agents-md
    """
    from raise_cli.session.bundle import (
        SECTION_REGISTRY,
        assemble_orientation,
    )
    from raise_cli.session.measure import measure_bundle

    profile = load_developer_profile()
    if profile is None:
        cli_error(_ERR_NO_PROFILE)
        return

    project_path = Path(project).resolve()
    dev_prefix = profile.get_pattern_prefix()
    scope = resolve_scope(project_path)
    last_closed_id = find_last_closed_in_scope(
        dev_prefix, scope, project_root=project_path
    )
    state = load_session_state(
        project_path,
        session_id=last_closed_id if last_closed_id else None,
    )

    active = read_active_session(project_root=project_path)
    session_id = active.id if active else None

    orientation_text = assemble_orientation(profile, state, project_path, session_id)

    section_texts: dict[str, str] = {}
    for section_name in SECTION_REGISTRY:
        try:
            text = assemble_sections([section_name], project_path, profile, state)
            if text:
                section_texts[section_name] = text
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Failed to assemble section %s", section_name, exc_info=True)

    agents_md_text: str | None = None
    if include_agents_md:
        agents_md_path = project_path / "AGENTS.md"
        if agents_md_path.is_file():
            agents_md_text = agents_md_path.read_text(encoding="utf-8")

    result = measure_bundle(orientation_text, section_texts, agents_md_text)

    if fmt == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        typer.echo("Token Measurement Report")
        typer.echo("=" * 40)
        typer.echo("\nSession Bundle:")
        for name, tokens in result.bundle.items():
            pct = (tokens / result.bundle_total * 100) if result.bundle_total else 0
            typer.echo(f"  {name:<20} {tokens:>6,} tokens  ({pct:>5.1f}%)")
        typer.echo("  " + "─" * 38)
        typer.echo(f"  {'Total':<20} {result.bundle_total:>6,} tokens")
        if result.agents_md is not None:
            typer.echo(f"\nAGENTS.md:           {result.agents_md:>6,} tokens")
        typer.echo(
            f"\nCombined:            {result.combined_total:>6,} tokens"
            f"  ({result.window_pct:.1f}% of {result.window_size // 1000}K window)"
        )


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
    no_tokens: Annotated[
        bool,
        typer.Option(
            "--no-tokens",
            help="Suppress token cost summary at close",
        ),
    ] = False,
) -> None:
    """End the current working session.

    With no flags: clears active session state (legacy behavior).
    With --summary or --state-file: performs full structured close —
    records session, patterns, corrections, and updates state.

    All writes are performed atomically by the CLI — skills should
    NOT call separate telemetry/memory commands.

    Examples:
        $ rai session close
        $ rai session close --summary "Session protocol design" --type feature
        $ rai session close --state-file /tmp/session-output.yaml --project .
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
        try:
            save_developer_profile(updated)
        except OSError as exc:
            cli_error(
                "Could not update developer profile at ~/.rai/developer.yaml. "
                "The session was not closed. Re-run with a writable Rai home "
                f"or appropriate filesystem permissions. Details: {exc}"
            )
            return

        emitter.emit(
            SessionCloseEvent(
                session_id=resolved_session_id,
                outcome="legacy",
            )
        )
        typer.echo(f"Session {resolved_session_id} closed.")

        # Show insights if project available
        if project is not None:
            insights = _get_session_insights(Path(project), resolved_session_id)
            if insights and insights.commit_count > 0:
                typer.echo(_format_insights(insights))

        # Show token summary (S3044.5)
        if not no_tokens:
            _show_token_summary(legacy_project)

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
        typer.echo(
            "Warning: --summary close captures only a summary. "
            "For full session continuity (narrative, patterns, next-session prompt), "
            "use the /rai-session-close skill instead.",
            err=True,
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

    # Resolve project path — always absolute (RAISE-2048)
    project_path = Path(project).resolve() if project else Path.cwd()

    # CWD poka-yoke: reject if project mismatch
    guard_session_id, _resolved_via_cc = resolve_close_guard(
        profile, project_path, resolved_session_id
    )
    if guard_session_id and not _resolved_via_cc:
        _check_cwd_guard(profile, guard_session_id, project_path)
    target_session_id = guard_session_id

    # RAISE-9608 + RAISE-14592: reject structured close when no active session found.
    # Diagnostic error lists available sessions instead of suggesting 'session start'.
    if not target_session_id:
        session_list = (
            "; ".join(f"{a.session_id} → {a.project}" for a in profile.active_sessions)
            or "none"
        )
        cli_error(
            f"No active session for '{project_path}'.\n"
            f"Active sessions: {session_list}\n"
            "Re-run from a registered project directory, or check active sessions above."
        )
        return  # cli_error raises, but this helps pyright

    # Emit before:session:close — hooks can abort
    emitter = create_emitter()
    close_sid = target_session_id or ""
    before_result = emitter.emit(
        BeforeSessionCloseEvent(
            session_id=close_sid,
            outcome="structured",
        )
    )
    if before_result.aborted:
        typer.echo(f"Session close aborted: {before_result.abort_message}")
        raise typer.Exit(1)

    # Collect per-phase token summary before close persists it
    if not no_tokens and close_input.token_summary is None:
        import contextlib

        from raise_cli.telemetry.session_tokens import get_session_token_summary

        with contextlib.suppress(Exception):
            close_input.token_summary = get_session_token_summary(project_path)

    # Emit token_usage_daily to server (S6455.3)
    _emit_token_usage_daily(project_path, close_sid)
    # Emit story_cost_summary if story active (S6456.2 — no-op when no story)
    _emit_story_cost_summary(project_path, close_sid)

    # Process close (pass session_id for per-session state writes)
    close_result = process_session_close(
        close_input, profile, project_path, session_id=target_session_id
    )

    # Write to shared session index (new registry) — only on success
    # Prefer active pointer ID (new format) over legacy close_result.session_id
    active_pointer = read_active_session(project_root=project_path)
    final_session_id = (
        target_session_id
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

        import contextlib

        from raise_cli.session.context_env import read_context_env

        _sp_raw = read_context_env(
            project_path, final_session_id, "RAISE_SESSION_STORY_POINTS"
        )
        _story_points: int | None = None
        if _sp_raw is not None:
            with contextlib.suppress(ValueError):
                _story_points = int(_sp_raw)

        entry = SessionIndexEntry(
            id=final_session_id,
            name=session_name_val,
            started=start_time,
            closed=close_time,
            type=close_input.session_type,
            summary=close_input.summary,
            outcomes=close_input.outcomes,
            branch=_get_current_branch(),
            story_points=_story_points,
        )
        write_session_entry(dev_prefix, entry, project_root=project_path)

        # Update worktree last_session_id if closing inside a registered worktree.
        # Enables rai session start to load the worktree-scoped narrative instead
        # of the global last-closed session (fixes cross-worktree contamination).
        try:
            from raise_cli.storage.worktrees import (
                SqliteWorktreeStore,
            )

            wt_store = SqliteWorktreeStore(project=project_path)
            wt = wt_store.get_by_path(str(resolve_checkout_root()))
            wt_store.set_last_session(wt.worktree_id, final_session_id)
        except Exception:  # noqa: BLE001,S110
            pass

    # Clear active session pointer (only if it matches this session)
    clear_active_session(
        session_id=(
            active_pointer.id if active_pointer is not None else final_session_id
        ),
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
            session_id=final_session_id or close_result.session_id,
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

    # Show session insights
    if final_session_id:
        insights = _get_session_insights(project_path, final_session_id)
        if insights and insights.commit_count > 0:
            typer.echo(_format_insights(insights))

    # Show token summary (S3044.5)
    if not no_tokens:
        _show_token_summary(project_path)


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
        $ rai session list
        $ rai session list --limit 5
        $ rai session list --project /my/project
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

    missing_prefix_count = count_missing_prefix_sessions(project_root=project_path)
    typer.echo(f"\n{len(entries)} developer-scoped sessions.")
    if missing_prefix_count:
        typer.echo(
            f"Warning: {missing_prefix_count} project sessions have no developer "
            "prefix and are excluded from this developer-scoped list."
        )


def _derive_current_work_for_doctor(project_path: Path) -> CurrentWork | None:
    """Derive current work for doctor display — isolated for testability."""
    try:
        from raise_cli.session.derive import GitStateDeriver

        return GitStateDeriver().current_work(project_path)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Git state derivation failed", exc_info=True)
        return None


@session_app.command("doctor")
def doctor(
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
) -> None:
    """Run session health diagnostics.

    Scans for zombie sessions, stale output files, retention issues,
    and shows current git state derivation status. Does not modify
    anything — diagnosis only.

    Examples:
        $ rai session doctor
        $ rai session doctor --project /my/project
    """
    from raise_cli.session.doctor import SessionDoctor, format_findings

    project_path = Path(project).resolve() if project else Path.cwd()

    # Git state derivation status
    work = _derive_current_work_for_doctor(project_path)
    if work:
        typer.echo("Git state derivation: working")
        if work.branch:
            typer.echo(f"  Branch: {work.branch}")
        if work.epic:
            typer.echo(f"  Epic: {work.epic}")
        if work.story:
            typer.echo(f"  Story: {work.story}")
        if work.phase:
            typer.echo(f"  Phase: {work.phase}")
        typer.echo("")
    else:
        typer.echo("Git state derivation: unavailable")
        typer.echo("")

    # Session health scan
    doc = SessionDoctor(project_path)
    findings = doc.diagnose()

    if findings:
        plan = doc.classify(findings)
        typer.echo(format_findings(findings, []))
        consent_count = len(plan.needs_consent)
        if consent_count > 0:
            typer.echo(
                f"  {consent_count} item(s) need review — "
                "use `rai session start` for interactive cleanup."
            )
    else:
        typer.echo("Session health: all clear")


def _maybe_prompt_self_update(update: CheckResult) -> None:
    """Offer to install a detected update — real tty only (RAISE-15715).

    Never fires for `--format json` (agents/automation) or without a real
    terminal — a blocking Y/n prompt there would hang or be meaningless.
    The agent path (raise_session_open, no tty) is handled instead by the
    rai-session-start SKILL.md, which asks in chat.
    """
    if update.status != "warn" or not sys.stdout.isatty():
        return

    from rich.prompt import Confirm

    from raise_cli.cli.commands.self_update import apply_update
    from raise_cli.self_update.manifest import fetch_manifest

    data = update.data
    if not Confirm.ask(
        f"Nueva versión disponible: {data['latest']} (tienes: {data['current']}). "
        "¿Instalar ahora?",
        default=False,
    ):
        return

    manifest = fetch_manifest(data["url"])
    apply_update(manifest)


@session_app.command("open")
def open_session(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project path"),
    ] = ".",
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human | json"),
    ] = "human",
    no_bundle: Annotated[
        bool,
        typer.Option(
            "--no-bundle",
            help="Skip the start flow — checks only, no session record",
        ),
    ] = False,
) -> None:
    """Composite session open: checks + mission + bundle in one command.

    CLI fallback for the raise_session_open MCP tool (ADR-084) — same
    schema. Statuses are ok|warn|blocked; blocked requires a human choice.
    """
    from rich.console import Console

    from raise_cli.session.open_service import (
        build_open_report,
        run_start_for_bundle,
        should_run_start_for_bundle,
        surface_ledger_if_bundle_skipped,
    )

    console = Console()
    project_path = Path(project).resolve()
    report = build_open_report(project_path=project_path, cwd=project_path)
    include_bundle = not no_bundle
    if should_run_start_for_bundle(report, include_bundle):
        report = report.model_copy(
            update={"bundle": run_start_for_bundle(project_path)}
        )
    report = surface_ledger_if_bundle_skipped(project_path, report, include_bundle)

    if output_format == "json":
        print(report.model_dump_json())
        return

    icons = {"ok": "✓", "warn": "⚠", "blocked": "✗"}
    for check in (
        report.hygiene,
        report.drift,
        report.db,
        report.mission,
        report.mcp,
        report.worktrees,
        report.update,
    ):
        console.print(f"{icons[check.status]} {check.name}: {check.status}")
        if check.status != "ok":
            console.print(f"  {check.data}")
    console.print(f"\n[bold]Estado: {report.status}[/bold]")
    if report.bundle:
        console.print(report.bundle)
    elif report.orientation_ledger:
        console.print(report.orientation_ledger)

    _maybe_prompt_self_update(report.update)
