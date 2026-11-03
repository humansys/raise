"""Telemetry module for local signal collection.

Signals are stored in the project SQLite database and optionally forwarded
to raise-server. Follows OpenTelemetry semantic conventions (ADR-018).
"""

from __future__ import annotations

from raise_cli.telemetry.emitter import (
    EmitResult,
    UnifiedEmitter,
    emit,
    emit_command_usage,
    emit_error_event,
    emit_skill_event,
)
from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    CommandUsage,
    ErrorEvent,
    SessionEvent,
    Signal,
    SkillEvent,
    WorkLifecycle,
)

__all__ = [
    "CalibrationEvent",
    "CommandUsage",
    "EmitResult",
    "ErrorEvent",
    "SessionEvent",
    "Signal",
    "SkillEvent",
    "UnifiedEmitter",
    "WorkLifecycle",
    "emit",
    "emit_command_usage",
    "emit_error_event",
    "emit_skill_event",
]
