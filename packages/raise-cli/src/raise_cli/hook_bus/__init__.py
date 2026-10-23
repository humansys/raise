"""Hook bus — T5 foundation package for the lifecycle event infrastructure.

The hook bus provides typed events, the LifecycleHook protocol, the
EventEmitter dispatcher, and the HookRegistry. Placed at T5 so that
telemetry, distillation, and work_events can import from it directly
without upward boundary violations.

Architecture: ADR-039 (Lifecycle Hooks & Workflow Gates), RAISE-16455
"""

from raise_cli.hook_bus.emitter import EventEmitter, create_emitter
from raise_cli.hook_bus.events import (
    AdapterFailedEvent,
    AdapterLoadedEvent,
    BacklogTransitionEvent,
    BeforeBugCloseEvent,
    BeforeInitiativeConcludedEvent,
    BeforeInitiativeValidatedEvent,
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
    BeforeStoryCloseEvent,
    DiscoverScanEvent,
    EmitResult,
    GraphBuildEvent,
    HookEvent,
    HookResult,
    InitCompleteEvent,
    McpCallEvent,
    PatternAddedEvent,
    PipelinePhaseEvent,
    ReleasePublishEvent,
    SessionCloseEvent,
    SessionStartEvent,
    WorkCloseEvent,
    WorkLifecycleEvent,
    WorkStartEvent,
)
from raise_cli.hook_bus.protocol import LifecycleHook
from raise_cli.hook_bus.registry import HookRegistry

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
    # After-events
    "SessionStartEvent",
    "SessionCloseEvent",
    "GraphBuildEvent",
    "PatternAddedEvent",
    "DiscoverScanEvent",
    "InitCompleteEvent",
    "AdapterLoadedEvent",
    "AdapterFailedEvent",
    "ReleasePublishEvent",
    "PipelinePhaseEvent",
    "WorkStartEvent",
    "WorkCloseEvent",
    "WorkLifecycleEvent",
    "BacklogTransitionEvent",
    "McpCallEvent",
    # Before-events
    "BeforeSessionCloseEvent",
    "BeforeReleasePublishEvent",
    "BeforeBugCloseEvent",
    "BeforeStoryCloseEvent",
    "BeforeInitiativeValidatedEvent",
    "BeforeInitiativeConcludedEvent",
]
