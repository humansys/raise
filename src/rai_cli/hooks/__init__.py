"""Lifecycle hooks infrastructure for rai-cli.

Provides typed event infrastructure for cross-cutting concerns (telemetry,
notifications, compliance) to react to CLI operations without coupling
to skill content.

Architecture: ADR-039 (Lifecycle Hooks & Workflow Gates)
"""

from rai_cli.hooks.emitter import EventEmitter
from rai_cli.hooks.events import (
    AdapterFailedEvent,
    AdapterLoadedEvent,
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
    DiscoverScanEvent,
    EmitResult,
    GraphBuildEvent,
    HookEvent,
    HookResult,
    InitCompleteEvent,
    PatternAddedEvent,
    ReleasePublishEvent,
    SessionCloseEvent,
    SessionStartEvent,
)

__all__ = [
    # Base types
    "HookEvent",
    "HookResult",
    "EmitResult",
    # Emitter
    "EventEmitter",
    # After-events (9)
    "SessionStartEvent",
    "SessionCloseEvent",
    "GraphBuildEvent",
    "PatternAddedEvent",
    "DiscoverScanEvent",
    "InitCompleteEvent",
    "AdapterLoadedEvent",
    "AdapterFailedEvent",
    "ReleasePublishEvent",
    # Before-events (2)
    "BeforeSessionCloseEvent",
    "BeforeReleasePublishEvent",
]
