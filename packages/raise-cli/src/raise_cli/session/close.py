"""Session close orchestrator.

Processes structured session output and performs all writes atomically:
1. Record session in personal/sessions/index.jsonl (developer-specific)
2. Append patterns to SQLite patterns table (project knowledge)
3. Update coaching corrections in developer.yaml
4. Update coaching observations in developer.yaml
5. Clear current_session in developer.yaml
6. Write session-state.yaml (project-level working state)
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from raise_cli.exceptions import ConfigurationError
from raise_cli.memory.pattern_evaluator import evaluate_session
from raise_cli.memory.writer import (
    PatternInput,
    PatternSubType,
    SessionInput,
    WriteResult,
    append_pattern,
    append_session,
    reinforce_pattern,
)
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    add_correction,
    end_session,
    save_developer_profile,
    update_coaching,
)
from raise_cli.schemas.session_state import (
    CurrentWork,
    EpicProgress,
    LastSession,
    PendingItems,
    SessionState,
)
from raise_cli.session.state import save_session_state, write_session_record

logger = logging.getLogger(__name__)


def _maybe_emit_session_cost_kpi(project_root: Path) -> None:  # pyright: ignore[reportUnusedFunction]
    """Emit cost_kpi lifecycle signal at session close — best-effort, never raises.

    Reads story attribution from the current session's JSONL files and emits
    a cost_kpi WorkLifecycle event. Sessions without story work emit with n=0
    to contribute to the server-side overhead_ratio metric (RAISE-9902).
    """
    try:
        from contextlib import suppress

        from raise_cli.storage.connection import get_project_db_path
        from raise_cli.telemetry.cost_report import CostReport, build_story_attribution
        from raise_cli.telemetry.emit_work import emit_cost_kpi

        db_path = get_project_db_path(project_root)
        attrs = build_story_attribution(project_root, db_path=db_path)
        report = CostReport(story_attributions=attrs)
        story_count = len([a for a in attrs if not a.overhead])

        with suppress(Exception):
            emit_cost_kpi(
                avg_cost=report.avg_cost_per_story,
                median_cost=report.median_cost_per_story,
                p95_cost=report.p95_cost_per_story,
                stories_count=story_count,
                since=None,
                until=None,
            )
    except Exception:  # noqa: BLE001
        logger.warning("Failed to emit cost_kpi at session close", exc_info=True)


class CoachingInput(BaseModel):
    """Typed coaching sub-structure matching update_coaching() signature."""

    strengths: list[str] | None = None
    growth_edge: str | None = None
    trust_level: str | None = None
    autonomy: str | None = None
    relationship: dict[str, str] | None = None
    communication_notes: list[str] | None = None


class CurrentWorkInput(BaseModel):
    """Input mirror of CurrentWork — typed deserialization of the current_work YAML block."""

    release: str = ""
    epic: str = ""
    story: str = ""
    phase: str = ""
    branch: str = ""


class PendingInput(BaseModel):
    """Input mirror of PendingItems — typed deserialization of the pending YAML block."""

    decisions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class CloseInput(BaseModel):
    """Structured input for session close.

    Can be populated from CLI flags or from a state file.
    """

    session_id: str = ""
    summary: str = ""
    session_type: str = "feature"
    outcomes: list[str] = Field(default_factory=lambda: list[str]())
    patterns: list[dict[str, str]] = Field(
        default_factory=lambda: list[dict[str, str]]()
    )
    corrections: list[dict[str, str]] = Field(
        default_factory=lambda: list[dict[str, str]]()
    )
    current_work: CurrentWorkInput | None = None
    pending: PendingInput | None = None
    progress: dict[str, int | str] | None = None
    completed_epics: list[str] = Field(default_factory=lambda: list[str]())
    coaching: CoachingInput | None = None
    notes: str = ""
    narrative: str = ""
    next_session_prompt: str = ""
    token_summary: dict[str, int] | None = None


class CloseResult(BaseModel):
    """Result of session close operation."""

    success: bool
    session_id: str = ""
    patterns_added: int = 0
    corrections_added: int = 0
    messages: list[str] = Field(default_factory=lambda: list[str]())


def load_state_file(path: Path) -> CloseInput:
    """Load close input from a YAML state file.

    Args:
        path: Path to the state file written by the AI skill.

    Returns:
        CloseInput populated from the file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        yaml.YAMLError: If the file is not valid YAML.
        pydantic.ValidationError: If the data fails model validation.
    """
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    if not isinstance(data, dict):
        msg = f"State file must be a YAML mapping, got {type(data).__name__}"
        raise ConfigurationError(msg)

    if "type" in data and "session_type" not in data:
        data["session_type"] = data.pop("type")

    return CloseInput.model_validate(data)


def _resolve_session_id(
    session_id: str | None,
    close_input: CloseInput,
    personal_dir: Path,
) -> tuple[str, str]:
    """Resolve session ID and message for close result.

    When caller provides session_id (new S-F-* format), uses it directly
    and skips legacy append_session. Falls back to SES-NNN for compat.

    Returns:
        (resolved_id, log_message) tuple.
    """
    if session_id:
        return session_id, f"Session {session_id} recorded"
    session_input = SessionInput(
        topic=close_input.summary,
        session_type=close_input.session_type,
        outcomes=close_input.outcomes,
    )
    session_result = append_session(personal_dir, session_input)
    return session_result.id, f"Session {session_result.id} recorded"


def _get_project_db_for_eval(project_path: Path) -> sqlite3.Connection | None:
    """Get project DB connection for pattern evaluation. Returns None on failure."""
    try:
        from raise_cli.storage.connection import get_project_db
        from raise_cli.storage.schema import create_all

        conn = get_project_db(project_path)
        create_all(conn)
        return conn
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Failed to get project DB for evaluation", exc_info=True)
        return None


def _get_project_id_for_eval(project_path: Path) -> str:
    """Get project ID for pattern evaluation. Returns empty string on failure."""
    try:
        from raise_cli.storage.connection import get_project_id

        return get_project_id(project_path)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return ""


def _auto_evaluate_patterns(
    project_path: Path, session_id: str, result: CloseResult
) -> None:
    """Auto-evaluate returned patterns and reinforce. Never raises."""
    try:
        conn = _get_project_db_for_eval(project_path)
        if conn is None:
            return
        project_id = _get_project_id_for_eval(project_path)
        evals = evaluate_session(conn, session_id, project_path, project_id=project_id)
        if not evals:
            return

        reinforced = 0
        penalized = 0
        for ev in evals:
            if ev.vote == 0:
                continue
            try:
                reinforce_pattern(
                    file_path=project_path,
                    pattern_id=ev.pattern_id,
                    vote=ev.vote,
                    conn=conn,
                )
                if ev.vote == 1:
                    reinforced += 1
                else:
                    penalized += 1
            except KeyError:
                logger.debug("Pattern %s not found for reinforcement", ev.pattern_id)

        result.messages.append(
            f"Patterns evaluated: {len(evals)} ({reinforced} reinforced, {penalized} penalized)"
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Pattern auto-evaluation failed", exc_info=True)


def process_session_close(
    close_input: CloseInput,
    profile: DeveloperProfile,
    project_path: Path,
    session_id: str | None = None,
) -> CloseResult:
    """Process session close — perform all writes.

    Args:
        close_input: Structured session close data.
        profile: Current developer profile.
        project_path: Absolute path to the project root.
        session_id: Optional session identifier for logging.

    Returns:
        CloseResult with operation summary.
    """
    result = CloseResult(success=True)
    memory_dir = project_path / ".raise" / "rai" / "memory"
    personal_dir = project_path / ".raise" / "rai" / "personal"

    # 1. Resolve session ID (new S-F-* format or legacy SES-NNN fallback)
    result.session_id, msg = _resolve_session_id(session_id, close_input, personal_dir)
    result.messages.append(msg)

    # 2. Append patterns
    pattern_ids: list[str] = []
    for pat_data in close_input.patterns:
        description = pat_data.get("description", "")
        if not description:
            continue
        context = pat_data.get("context", "")
        context_list = [c.strip() for c in context.split(",")]
        pat_type = pat_data.get("type", "process")
        try:
            sub_type = PatternSubType(pat_type)
        except ValueError:
            sub_type = PatternSubType.PROCESS

        pat_input = PatternInput(
            content=description,
            sub_type=sub_type,
            context=context_list,
            learned_from=result.session_id,
        )
        pat_result: WriteResult = append_pattern(
            memory_dir, pat_input, developer_prefix=profile.get_pattern_prefix()
        )
        pattern_ids.append(pat_result.id)
        result.patterns_added += 1
        result.messages.append(f"Pattern {pat_result.id} added")

    # 2b. Auto-evaluate returned patterns and reinforce
    _auto_evaluate_patterns(project_path, result.session_id, result)

    # 3. Update coaching corrections
    updated_profile = profile
    for corr_data in close_input.corrections:
        what = corr_data.get("what", "")
        lesson = corr_data.get("lesson", "")
        if what and lesson:
            updated_profile = add_correction(
                updated_profile, result.session_id, what, lesson
            )
            result.corrections_added += 1

    # 4. Update coaching observations
    if close_input.coaching:
        c = close_input.coaching
        updated_profile = update_coaching(
            updated_profile,
            strengths=c.strengths,
            growth_edge=c.growth_edge,
            trust_level=c.trust_level,
            autonomy=c.autonomy,
            relationship=c.relationship,
            communication_notes=c.communication_notes,
        )
        result.messages.append("Coaching updated")

    # 5. Remove session from active_sessions and save profile
    updated_profile = end_session(
        updated_profile, session_id=session_id or result.session_id
    )
    save_developer_profile(updated_profile)
    result.messages.append("Profile updated")

    # 5. Write session-state.yaml
    if close_input.current_work:
        cw = close_input.current_work
        current_work = CurrentWork(
            release=cw.release,
            epic=cw.epic,
            story=cw.story,
            phase=cw.phase,
            branch=cw.branch,
        )
    else:
        current_work = CurrentWork()

    if close_input.pending:
        p = close_input.pending
        pending = PendingItems(
            decisions=p.decisions,
            blockers=p.blockers,
            next_actions=p.next_actions,
        )
    else:
        pending = PendingItems()

    # Build progress if provided
    progress: EpicProgress | None = None
    if close_input.progress:
        p = close_input.progress
        progress = EpicProgress(
            epic=str(p.get("epic", "")),
            stories_done=int(p.get("stories_done", 0)),
            stories_total=int(p.get("stories_total", 0)),
            sp_done=int(p.get("sp_done", 0)),
            sp_total=int(p.get("sp_total", 0)),
        )

    session_state = SessionState(
        current_work=current_work,
        last_session=LastSession(
            id=result.session_id,
            date=date.today(),
            developer=profile.name,
            summary=close_input.summary,
            patterns_captured=pattern_ids,
        ),
        pending=pending,
        notes=close_input.notes,
        narrative=close_input.narrative,
        next_session_prompt=close_input.next_session_prompt,
        progress=progress,
        completed_epics=close_input.completed_epics,
    )
    # Write to per-session directory for isolation. Next session start
    # reads the latest closed session via the index.
    save_session_state(project_path, session_state, session_id=result.session_id)
    result.messages.append("Session state saved")

    write_session_record(
        project_path,
        result.session_id,
        close_input,
        pattern_ids,
        token_summary=close_input.token_summary,
    )
    result.messages.append("Session record written")

    return result
