"""Session close orchestrator.

Processes structured session output and performs all writes atomically:
1. Write session-state.yaml (project-level working state)
2. Append patterns to patterns.jsonl
3. Update coaching corrections in developer.yaml
4. Record session in sessions/index.jsonl
5. Emit telemetry (session_close signal)
6. Clear current_session in developer.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

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
)
from raise_cli.schemas.session_state import (
    CurrentWork,
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

    summary: str = ""
    session_type: str = "feature"
    outcomes: list[str] = field(default_factory=list)
    patterns: list[dict[str, str]] = field(default_factory=list)
    corrections: list[dict[str, str]] = field(default_factory=list)
    current_work: dict[str, str] | None = None
    pending: dict[str, list[str]] | None = None
    notes: str = ""


@dataclass
class CloseResult:
    """Result of session close operation."""

    success: bool
    session_id: str = ""
    patterns_added: int = 0
    corrections_added: int = 0
    messages: list[str] = field(default_factory=list)


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

    return CloseInput(
        summary=data.get("summary", ""),
        session_type=data.get("type", "feature"),
        outcomes=data.get("outcomes", []),
        patterns=data.get("patterns", []),
        corrections=data.get("corrections", []),
        current_work=data.get("current_work"),
        pending=data.get("pending"),
        notes=data.get("notes", ""),
    )


def process_session_close(
    close_input: CloseInput,
    profile: DeveloperProfile,
    project_path: Path,
) -> CloseResult:
    """Process session close — perform all writes.

    Args:
        close_input: Structured session close data.
        profile: Current developer profile.
        project_path: Absolute path to the project root.

    Returns:
        CloseResult with operation summary.
    """
    result = CloseResult(success=True)
    memory_dir = project_path / ".raise" / "rai" / "memory"

    # 1. Record session in index.jsonl
    session_input = SessionInput(
        topic=close_input.summary,
        session_type=close_input.session_type,
        outcomes=close_input.outcomes,
    )
    session_result = append_session(memory_dir, session_input)
    result.session_id = session_result.id
    result.messages.append(f"Session {session_result.id} recorded")

    # 2. Append patterns
    for pat_data in close_input.patterns:
        description = pat_data.get("description", "")
        if not description:
            continue
        context = pat_data.get("context", "")
        context_list = (
            [c.strip() for c in context.split(",")]
            if isinstance(context, str)
            else context
        )
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
        pat_result: WriteResult = append_pattern(memory_dir, pat_input)
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

    # 4. Clear current_session and save profile
    updated_profile = end_session(updated_profile)
    save_developer_profile(updated_profile)
    result.messages.append("Profile updated")

    # 5. Write session-state.yaml
    if close_input.current_work:
        cw = close_input.current_work
        current_work = CurrentWork(
            epic=cw.get("epic", ""),
            story=cw.get("story", ""),
            phase=cw.get("phase", ""),
            branch=cw.get("branch", ""),
        )
    else:
        current_work = CurrentWork(
            epic="", story="", phase="", branch=""
        )

    pending = PendingItems()
    if close_input.pending:
        pending = PendingItems(
            decisions=close_input.pending.get("decisions", []),
            blockers=close_input.pending.get("blockers", []),
            next_actions=close_input.pending.get("next_actions", []),
        )

    session_state = SessionState(
        current_work=current_work,
        last_session=LastSession(
            id=result.session_id,
            date=date.today(),
            developer=profile.name,
            summary=close_input.summary,
            patterns_captured=[
                f"PAT-{result.session_id}"
                for _ in close_input.patterns
            ] if close_input.patterns else [],
        ),
        pending=pending,
        notes=close_input.notes,
    )
    save_session_state(project_path, session_state)
    result.messages.append("Session state saved")

    return result
