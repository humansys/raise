"""Writer module for appending telemetry signals to JSONL.

This module provides the `emit()` function to append signals to
`.raise/rai/personal/telemetry/signals.jsonl` (gitignored, per-developer).

Signals are written as JSON lines (one JSON object per line),
which is append-friendly and git-friendly.

Note: Telemetry is personal data (F14.15) and should not be committed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from raise_cli.compat import file_lock, file_unlock
from raise_cli.config.paths import (
    SIGNALS_FILE,
    TELEMETRY_SUBDIR,
    get_personal_dir,
    get_session_dir,
)

if TYPE_CHECKING:
    from raise_cli.telemetry.schemas import Signal

# Type alias for skill event types (matches SkillEvent.event)
SkillEventType = Literal["start", "complete", "abandon"]


@dataclass
class EmitResult:
    """Result of emitting a signal.

    Attributes:
        success: Whether the signal was written successfully.
        path: Path where the signal was written.
        error: Error message if failed, None otherwise.
    """

    success: bool
    path: Path | None = None
    error: str | None = None


def _get_telemetry_path(base_path: Path | None = None) -> Path:
    """Get the path to the signals.jsonl file in personal directory.

    Telemetry is personal data (per-developer, gitignored) per F14.15.
    Path: .raise/rai/personal/telemetry/signals.jsonl

    Args:
        base_path: Project root directory. Defaults to current directory.

    Returns:
        Path to signals.jsonl file in personal directory.
    """
    return get_personal_dir(base_path) / TELEMETRY_SUBDIR / SIGNALS_FILE


def _ensure_directory(path: Path) -> None:
    """Ensure the parent directory exists.

    Args:
        path: Path to file whose parent directory should exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)


def emit(
    signal: Signal,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
) -> EmitResult:
    """Emit a telemetry signal to the signals.jsonl file.

    When session_id is provided, writes to per-session directory:
        .raise/rai/personal/sessions/{session_id}/signals.jsonl

    When session_id is None, writes to shared telemetry directory:
        .raise/rai/personal/telemetry/signals.jsonl

    Creates the directory if it doesn't exist. Uses file locking for
    thread-safe writes. Telemetry is personal data (gitignored).

    Args:
        signal: The signal to emit (any of the 5 signal types).
        base_path: Base directory for telemetry. Defaults to current directory.
        session_id: Optional session ID for per-session isolation.

    Returns:
        EmitResult with success status and path or error message.
    """
    if session_id is not None:
        path = get_session_dir(session_id, base_path) / SIGNALS_FILE
    else:
        path = _get_telemetry_path(base_path)

    try:
        _ensure_directory(path)

        # Serialize signal to JSON line
        json_line = signal.model_dump_json() + "\n"

        # Append with file locking for thread safety
        with open(path, "a", encoding="utf-8") as f:
            file_lock(f)
            try:
                f.write(json_line)
            finally:
                file_unlock(f)

        return EmitResult(success=True, path=path)

    except PermissionError as e:
        return EmitResult(
            success=False, error=f"Permission denied writing to {path}: {e}"
        )
    except OSError as e:
        return EmitResult(success=False, error=f"OS error writing to {path}: {e}")


def emit_skill_event(
    skill: str,
    event: SkillEventType,
    duration_sec: int | None = None,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
) -> EmitResult:
    """Convenience function to emit a skill event.

    Args:
        skill: Name of the skill (e.g., "story-design").
        event: Event type ("start", "complete", "abandon").
        duration_sec: Duration in seconds (for complete/abandon).
        base_path: Base directory for telemetry.
        session_id: Optional session ID for per-session isolation.

    Returns:
        EmitResult with success status.
    """
    from raise_cli.telemetry.schemas import SkillEvent

    signal = SkillEvent(
        timestamp=datetime.now(UTC),
        skill=skill,
        event=event,
        duration_sec=duration_sec,
    )
    return emit(signal, base_path=base_path, session_id=session_id)


def emit_command_usage(
    command: str,
    subcommand: str | None = None,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
) -> EmitResult:
    """Convenience function to emit a command usage event.

    Args:
        command: Main command name (e.g., "memory").
        subcommand: Subcommand name if any (e.g., "query").
        base_path: Base directory for telemetry.
        session_id: Optional session ID for per-session isolation.

    Returns:
        EmitResult with success status.
    """
    from raise_cli.telemetry.schemas import CommandUsage

    signal = CommandUsage(
        timestamp=datetime.now(UTC),
        command=command,
        subcommand=subcommand,
    )
    return emit(signal, base_path=base_path, session_id=session_id)


def emit_error_event(
    tool: str,
    error_type: str,
    context: str,
    recoverable: bool,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
) -> EmitResult:
    """Convenience function to emit an error event.

    Args:
        tool: Name of the tool that failed (e.g., "Bash").
        error_type: Type of error (e.g., "command_not_found").
        context: Brief context (no sensitive data).
        recoverable: Whether the error was recoverable.
        base_path: Base directory for telemetry.
        session_id: Optional session ID for per-session isolation.

    Returns:
        EmitResult with success status.
    """
    from raise_cli.telemetry.schemas import ErrorEvent

    signal = ErrorEvent(
        timestamp=datetime.now(UTC),
        tool=tool,
        error_type=error_type,
        context=context,
        recoverable=recoverable,
    )
    return emit(signal, base_path=base_path, session_id=session_id)
