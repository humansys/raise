"""Lifecycle hooks infrastructure for raise-cli.

Provides typed event infrastructure for cross-cutting concerns (telemetry,
notifications, compliance) to react to CLI operations without coupling
to skill content.

Architecture: ADR-039 (Lifecycle Hooks & Workflow Gates)
"""

from raise_cli.hooks.emitter import EventEmitter, create_emitter
from raise_cli.hooks.events import (
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
from raise_cli.hooks.protocol import LifecycleHook
from raise_cli.hooks.registry import HookRegistry

__all__ = [
    # Base types
    "HookEvent",
    "HookResult",
    "EmitResult",
    # Protocol + Registry
    "LifecycleHook",
    "HookRegistry",
    # Emitter
    "EventEmitter",
    "create_emitter",
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
