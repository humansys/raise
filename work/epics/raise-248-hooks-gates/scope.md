---
epic: RAISE-248
title: "Lifecycle Hooks & Workflow Gates"
status: in-progress
branch: epic/e248/hooks-gates
rfc: RFC-001
date: 2026-02-21
size: L
depends_on: [RAISE-211, RAISE-247]
---

# RAISE-248: Lifecycle Hooks & Workflow Gates

## Objective

Implement the lifecycle hooks and workflow gates defined in RFC-001. Cross-cutting
concerns (telemetry, notifications, compliance) move from skill content to CLI
infrastructure. Skills lose their ceremony overhead and become pure process instructions.

## Problem

Every lifecycle skill repeats the same pattern:

```
Step 0:    rai signal emit work ... --event start     ← telemetry (in every skill)
Step 0.1:  rai graph query "..."                      ← context loading (in every skill)
Step 0.2:  rai graph context mod-X                    ← context loading (in every skill)
Step N:    [actual work]
Step N+1:  rai signal emit work ... --event complete   ← telemetry (in every skill)
```

68% of CLI calls in skills are this ceremony. It wastes ~1,000 tokens and ~2 seconds
per skill invocation. It's also fragile — if a skill forgets to emit, telemetry has gaps.

## Solution

The CLI emits typed events at command boundaries. Hooks listen and react. Skills don't
need to know telemetry exists.

```
# Without hooks (today):
skill calls → rai signal emit work ... --event start     (explicit, in skill content)

# With hooks:
rai graph build → CLI emits after:graph:build event
  → TelemetryHook writes to signals.jsonl              (automatic, invisible to skill)
  → SlackNotifyHook posts to channel                   (PRO, if installed)
  → AuditHook logs to compliance system                (Enterprise, if installed)
```

## Stories

### S1: Event emitter infrastructure

**What:** Core event bus that CLI commands use to emit typed events.

**Includes:**
- `HookEvent` base dataclass (timestamp, project_path, event name)
- Typed event dataclasses for each event in the catalog (see below)
- `emit(event)` function that dispatches to registered hooks
- Graceful degradation: if no hooks registered, emit is a no-op (~0ms overhead)

**Event catalog (from RFC-001):**

| Event | Emitted when | Context payload |
|-------|-------------|-----------------|
| `session:start` | Session begins | session_id, project, agent |
| `session:close` | Session ends | session_id, summary, duration, patterns |
| `graph:build` | Knowledge graph rebuilt | project_path, node_count, edge_count |
| `pattern:added` | New pattern recorded | pattern_id, content, context |
| `signal:emitted` | Work/session/calibration signal | signal_type, work_id, event, phase |
| `discover:scan` | Code scan completes | language, file_count, symbol_count |
| `init:complete` | Project initialized | project_path, detected_conventions |
| `release:publish` | Release published | version, channel |
| `adapter:loaded` | Adapter passes validation | adapter_name, extension_point |
| `adapter:failed` | Adapter fails validation | adapter_name, error |

Each event has `before:` and `after:` variants. `before:` hooks can abort.

**Size:** M

### S2: Hook Protocol and registry

**What:** The `LifecycleHook` Protocol and hook discovery via entry points.

**Includes:**
- `LifecycleHook` Protocol (events list, handle method)
- `HookResult` dataclass (ok/error/abort status)
- Hook discovery via `rai.hooks` entry point group (same mechanism as RAISE-211 adapters)
- Hook execution: sequential, priority-ordered, with timeout (5s default)
- Error isolation: hook exception → log warning, continue. Hooks never crash the CLI.
- `before:*` abort handling: hook returns abort → operation cancelled with reason

**Size:** M

### S3: Built-in TelemetryHook (COMMUNITY)

**What:** A hook bundled with raise-core that replaces manual `rai signal emit` calls
in skills by automatically writing to `signals.jsonl` on relevant events.

**Listens to:**
- `after:session:start` → emit session start signal
- `after:session:close` → emit session close signal
- `after:graph:build` → emit build signal
- `after:pattern:added` → emit pattern signal

**What this enables:**
- Skills no longer need `rai signal emit` calls — telemetry is automatic
- Telemetry coverage is complete — no gaps from forgotten emit calls
- The same hook mechanism PRO/Enterprise use for their own telemetry

**Size:** S

### S4: Wire events into existing CLI commands

**What:** Add `emit()` calls to the CLI commands that should produce events.

**Commands to wire:**
- `rai session start` → `before:session:start` / `after:session:start`
- `rai session close` → `before:session:close` / `after:session:close`
- `rai graph build` → `before:graph:build` / `after:graph:build`
- `rai pattern add` → `after:pattern:added`
- `rai signal emit` → `after:signal:emitted`
- `rai discover scan` → `after:discover:scan`
- `rai init` → `after:init:complete`
- `rai release publish` → `before:release:publish` / `after:release:publish`

**Note:** Uses RAISE-247 command names (`graph`, `pattern`, `signal`). If RAISE-247
is not yet complete, wire under current `memory` names and update in RAISE-247 S8.

**Size:** M

### S5: WorkflowGate Protocol and registry

**What:** The `WorkflowGate` Protocol for declarative transition validation.

**Includes:**
- `WorkflowGate` Protocol (gate_id, check method returning GateResult)
- `GateResult` dataclass (passed/failed/skipped, message, details)
- Gate discovery via `rai.gates` entry point group
- `rai gate check <gate-id>` command for manual gate verification
- Gate composition: multiple gates run for same checkpoint, all must pass

**Distinct from hooks:** Gates guard transitions (validate, block). Hooks react to events
(observe, log). A gate failure prevents the operation. A hook failure is logged and skipped.

**Size:** M

### S6: Built-in gates (COMMUNITY)

**What:** Basic gates bundled with raise-core.

**Gates:**
- `gate-tests` — `pytest` exits 0
- `gate-types` — `pyright` exits 0
- `gate-lint` — `ruff check .` exits 0
- `gate-coverage` — `pytest --cov` meets threshold

**These already exist as guardrails in governance docs** — this makes them executable
and composable via the gate protocol instead of manual checks in skills.

**Size:** S

### S7: Remove ceremony from skills

**What:** After hooks and gates are wired, remove the ceremony steps from all 22
skills in `skills_base/`.

**Removes from skills:**
- All `rai signal emit` / `rai memory emit-work` calls (TelemetryHook handles it)
- Prerequisite checks that gates now handle (graph exists, tests pass)

**Keeps in skills:**
- `rai graph query` / `rai graph context` — context loading is input the agent needs,
  not a side effect a hook can replace (unless a ContextProvider exists — deferred)
- `rai pattern add` / `rai pattern reinforce` — knowledge capture is skill substance

**Size:** M

## Dependency Order

```
S1 (event emitter) → S2 (hook protocol) → S3 (telemetry hook) → S4 (wire events)
                                        → S5 (gate protocol) → S6 (built-in gates)
                                                                         ↓
                                                              S7 (remove ceremony)
```

S1-S2 are infrastructure. S3-S6 can partially parallelize. S7 goes last.

## What This Does NOT Include

- **Context providers** (`rai.providers.context`) — Deferred. Would eliminate
  `rai graph query` from skills by pre-loading context. Requires the Skill Builder
  (RAISE-242) to know what context each skill needs. Future epic.
- **Output formatters** (`rai.providers.output`) — Deferred. Low priority.
- **Scaffold providers** (`rai.providers.scaffold`) — Deferred. Useful for `rai init`
  customization but not urgent.
- **`rai skill prepare`** — Rejected (couples skills to CLI). Hooks solve the same
  problem without coupling.

## Verification Gate

```bash
# Hooks fire on CLI commands
rai graph build 2>&1 | grep -q "hook:telemetry"  # with -v flag

# No emit calls in skills
grep -r "signal emit\|memory emit" src/rai_cli/skills_base/ && exit 1

# Gates work
rai gate check gate-tests
rai gate check gate-types

# Hook error isolation
# (test that a broken hook doesn't crash the CLI)
```

## Epic Dependency Chain

```
RAISE-211 (Adapter Foundation — entry points, TierContext)
  → RAISE-247 (CLI Ontology — rename commands)
    → RAISE-248 (THIS — hooks + gates on new ontology)
      → RAISE-242 (Skill Builder — generates skills without ceremony)
```

## References

- RFC-001: `dev/rfcs/rfc-001-extensibility-architecture.md` (full design)
- RFC-002: `dev/rfcs/rfc-002-skill-builder-vision.md` (ceremony analysis)
- ADR-038: CLI Ontology Restructuring
- SES-234: Ontological analysis session (2026-02-21)
