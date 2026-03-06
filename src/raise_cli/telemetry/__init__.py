"""Telemetry module for local signal collection.

This module provides infrastructure for collecting telemetry signals
as specified in ADR-018 (Local Telemetry Architecture).

Signals are stored locally in `.raise/rai/personal/telemetry/signals.jsonl` and follow
OpenTelemetry semantic conventions for future OTLP export.
"""

from __future__ import annotations

from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    CommandUsage,
    ErrorEvent,
    SessionEvent,
    Signal,
    SkillEvent,
    WorkLifecycle,
)
from raise_cli.telemetry.writer import (
    EmitResult,
    emit,
    emit_command_usage,
    emit_error_event,
    emit_skill_event,
)

__all__ = [
    "CalibrationEvent",
    "CommandUsage",
    "EmitResult",
    "ErrorEvent",
    "SessionEvent",
    "Signal",
    "SkillEvent",
    "WorkLifecycle",
    "emit",
    "emit_command_usage",
    "emit_error_event",
    "emit_skill_event",
]
