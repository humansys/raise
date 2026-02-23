---
type: module
name: hooks
purpose: "Typed lifecycle event infrastructure for cross-cutting concerns (telemetry, notifications, compliance)"
status: current
depends_on: []
depended_by: []
entry_points: []
public_api:
  - "HookEvent"
  - "HookResult"
  - "EmitResult"
  - "EventEmitter"
  - "SessionStartEvent"
  - "SessionCloseEvent"
  - "GraphBuildEvent"
  - "PatternAddedEvent"
  - "DiscoverScanEvent"
  - "InitCompleteEvent"
  - "AdapterLoadedEvent"
  - "AdapterFailedEvent"
  - "ReleasePublishEvent"
  - "BeforeSessionCloseEvent"
  - "BeforeReleasePublishEvent"
architecture_decision: "ADR-039"
layer: leaf
bounded_context: infrastructure
---

# Module: hooks

Provides the event emitter and typed event catalog for lifecycle hooks.
Events are frozen dataclasses dispatched synchronously to registered handlers
with error isolation (handler failures are logged and skipped).

## Key Design

- **Events:** 9 after-events + 2 before-events (selective per AD-6)
- **Emitter:** Register handlers by event name, dispatch with try/except per handler
- **Before-abort:** Handlers can abort `before:` events; abort on `after:` events is ignored
- **No singleton:** EventEmitter is instantiated per CLI invocation

## Files

| File | Purpose |
|------|---------|
| `events.py` | HookEvent base, HookResult, EmitResult, 11 event dataclasses |
| `emitter.py` | EventEmitter with register/emit/error isolation |

## Future (S248.2+)

- Hook Protocol and entry point discovery (`rai.hooks`) — S248.2
- Priority-based dispatch and per-hook timeout — S248.2
- TelemetryHook built-in consumer — S248.3
