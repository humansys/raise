"""Telemetry module for local signal collection.

This module provides infrastructure for collecting telemetry signals
as specified in ADR-018 (Local Telemetry Architecture).

Signals are stored locally in `.rai/telemetry/signals.jsonl` and follow
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
)

__all__ = [
    "CalibrationEvent",
    "CommandUsage",
    "ErrorEvent",
    "SessionEvent",
    "Signal",
    "SkillEvent",
]
