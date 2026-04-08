"""Session close orchestrator.

Processes structured session output and performs all writes atomically:
1. Record session in personal/sessions/index.jsonl (developer-specific)
2. Append patterns to memory/patterns.jsonl (project knowledge)
3. Update coaching corrections in developer.yaml
4. Update coaching observations in developer.yaml
5. Clear current_session in developer.yaml
6. Write session-state.yaml (project-level working state)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import cast

import yaml

from raise_cli.memory.writer import (
    PatternInput,
    PatternSubType,
    SessionInput,
    WriteResult,
    append_pattern,
    append_session,
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
from raise_cli.session.state import save_session_state

logger = logging.getLogger(__name__)


@dataclass
class CloseInput:
    """Structured input for session close.

    Can be populated from CLI flags or from a state file.
    """

    session_id: str = ""
    summary: str = ""
    session_type: str = "feature"
    outcomes: list[str] = field(default_factory=lambda: list[str]())
    patterns: list[dict[str, str]] = field(
        default_factory=lambda: list[dict[str, str]]()
    )
    corrections: list[dict[str, str]] = field(
        default_factory=lambda: list[dict[str, str]]()
    )
    current_work: dict[str, str] | None = None
    pending: dict[str, list[str]] | None = None
    progress: dict[str, int | str] | None = None
    completed_epics: list[str] = field(default_factory=lambda: list[str]())
    coaching: dict[str, object] | None = None
    notes: str = ""
    narrative: str = ""
    next_session_prompt: str = ""


@dataclass
class CloseResult:
    """Result of session close operation."""

    success: bool
    session_id: str = ""
    patterns_added: int = 0
    corrections_added: int = 0
    messages: list[str] = field(default_factory=lambda: list[str]())


def load_state_file(path: Path) -> CloseInput:
    """Load close input from a YAML state file.

    Args:
        path: Path to the state file written by the AI skill.

    Returns:
        CloseInput populated from the file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        yaml.YAMLError: If the file is not valid YAML.
    """
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    if not isinstance(data, dict):
        msg = f"State file must be a YAML mapping, got {type(data).__name__}"
        raise ValueError(msg)

    d = cast("dict[str, object]", data)

    return CloseInput(
        session_id=str(d.get("session_id", "")),
        summary=str(d.get("summary", "")),
        session_type=str(d.get("type", "feature")),
        outcomes=list(d.get("outcomes", []) or []),  # type: ignore[arg-type]
        patterns=list(d.get("patterns", []) or []),  # type: ignore[arg-type]
        corrections=list(d.get("corrections", []) or []),  # type: ignore[arg-type]
        current_work=d.get("current_work"),  # type: ignore[arg-type]
        pending=d.get("pending"),  # type: ignore[arg-type]
        progress=d.get("progress"),  # type: ignore[arg-type]
        completed_epics=list(d.get("completed_epics", []) or []),  # type: ignore[arg-type]
        coaching=d.get("coaching"),  # type: ignore[arg-type]
        notes=str(d.get("notes", "")),
        narrative=str(d.get("narrative", "")),
        next_session_prompt=str(d.get("next_session_prompt", "")),
    )


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
    result.session_id, msg = _resolve_session_id(
        session_id, close_input, personal_dir
    )
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
            strengths=c.get("strengths"),  # type: ignore[arg-type]
            growth_edge=c.get("growth_edge"),  # type: ignore[arg-type]
            trust_level=c.get("trust_level"),  # type: ignore[arg-type]
            autonomy=c.get("autonomy"),  # type: ignore[arg-type]
            relationship=c.get("relationship"),  # type: ignore[arg-type]
            communication_notes=c.get("communication_notes"),  # type: ignore[arg-type]
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
            release=cw.get("release", ""),
            epic=cw.get("epic", ""),
            story=cw.get("story", ""),
            phase=cw.get("phase", ""),
            branch=cw.get("branch", ""),
        )
    else:
        current_work = CurrentWork(release="", epic="", story="", phase="", branch="")

    pending = PendingItems()
    if close_input.pending:
        pending = PendingItems(
            decisions=close_input.pending.get("decisions", []),
            blockers=close_input.pending.get("blockers", []),
            next_actions=close_input.pending.get("next_actions", []),
        )

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
    # Write to flat file (not per-session dir) — flat file serves as
    # cross-session continuity buffer. Next session start will migrate
    # it to the new per-session directory.
    save_session_state(project_path, session_state)
    result.messages.append("Session state saved")

    return result
