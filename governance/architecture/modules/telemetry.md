---
type: module
name: telemetry
purpose: "Local signal collection — append-only JSONL telemetry following OpenTelemetry conventions"
status: current
depends_on: [config]
depended_by: [cli]
entry_points:
  - "raise memory emit"
  - "raise memory emit-work"
public_api:
  - "CalibrationEvent"
  - "CommandUsage"
  - "EmitResult"
  - "ErrorEvent"
  - "SessionEvent"
  - "Signal"
  - "SkillEvent"
  - "WorkLifecycle"
  - "emit"
  - "emit_command_usage"
  - "emit_error_event"
  - "emit_skill_event"
components: 13
constraints:
  - "Signals are local-only — no network transmission"
  - "Append-only JSONL — never read/modify existing signals"
  - "Follow OpenTelemetry semantic conventions for future OTLP export"
---

## Purpose

The telemetry module records what happens during RaiSE usage as structured signals — command invocations, skill executions, story lifecycle events, errors. All signals are stored locally in `.raise/rai/personal/telemetry/signals.jsonl` as append-only JSONL (personal scope — developer-specific, gitignored). There is no network transmission; this is purely local observability.

The signals follow OpenTelemetry semantic conventions so they could be exported to OTLP-compatible backends in the future, but for now they serve two purposes: **velocity tracking** (how long do stories take?) and **usage patterns** (which commands are used most?).

## Key Files

- **`schemas.py`** — Pydantic models for all signal types: `Signal` (base), `CommandUsage`, `SkillEvent`, `WorkLifecycle`, `SessionEvent`, `CalibrationEvent`, `ErrorEvent`. Each has a discriminator field for type-safe deserialization.
- **`writer.py`** — `emit()` function that appends a signal to the JSONL file. Specialized emitters: `emit_command_usage()`, `emit_skill_event()`, `emit_error_event()`. Returns `EmitResult` with file path and signal ID.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Directory resolution for telemetry file path |

## Conventions

- Signals are fire-and-forget — emission never raises exceptions (fails silently)
- Each signal has a unique ID and ISO timestamp
- `WorkLifecycle` tracks story/epic events with start/complete phases
- Signal types use Pydantic discriminated unions for type safety
