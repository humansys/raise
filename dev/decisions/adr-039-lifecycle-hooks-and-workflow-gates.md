---
id: "ADR-039"
title: "Lifecycle Hooks & Workflow Gates — Two extension mechanisms for cross-cutting concerns"
date: "2026-02-23"
status: "Accepted"
---

# ADR-039: Lifecycle Hooks & Workflow Gates

## Context

RAISE-211 established the adapter architecture: Protocol contracts + entry point discovery
for capabilities the CLI invokes (PM adapters, governance parsers, language extractors).
But adapters solve *invocation* — the core calls them when it needs something done.

Cross-cutting concerns (telemetry, notifications, compliance, quality gates) need a
different mechanism: *reaction*. Code that runs when something happens in the CLI, without
the core knowing what that code does.

Today these concerns live inside skill content (22 skills repeat `rai signal emit` calls,
prerequisite checks, etc.). This creates coupling, token waste (~1,000 per invocation),
and fragile coverage (forgotten emit = telemetry gap).

Three forces in tension:
1. Skills should contain process logic, not infrastructure plumbing
2. Cross-cutting concerns must be extensible (COMMUNITY → PRO → Enterprise)
3. The CLI must never crash because of third-party extension code

## Decision

### 1. Two separate protocols: LifecycleHook (observer) and WorkflowGate (guard)

**LifecycleHook** reacts to CLI events. It observes, logs, notifies. A hook failure is
logged and skipped — hooks never crash the CLI.

```python
@runtime_checkable
class LifecycleHook(Protocol):
    events: ClassVar[list[str]]       # e.g. ["after:session:close", "after:graph:build"]
    priority: ClassVar[int]           # higher wins, default 0

    def handle(self, event: HookEvent) -> HookResult: ...
```

**WorkflowGate** guards transitions. It validates and blocks. A gate failure prevents
the operation with an actionable message.

```python
@runtime_checkable
class WorkflowGate(Protocol):
    gate_id: str                      # e.g. "gate-tests"
    workflow_point: str               # e.g. "before:commit", "before:release"

    def evaluate(self, context: GateContext) -> GateResult: ...
```

### 2. Typed events as frozen dataclasses

Each event has a specific payload type, not a loose dict:

```python
@dataclass(frozen=True)
class GraphBuildEvent(HookEvent):
    event: Literal["graph:build"]
    project_path: Path
    node_count: int
    edge_count: int
```

Events have `before:` and `after:` variants. `before:` hooks can abort; `after:` hooks
observe only.

### 3. Entry point discovery (same as RAISE-211)

Two new entry point groups:
- `rai.hooks` — lifecycle hooks
- `rai.gates` — workflow gates

Same discovery mechanism, same security model (`rai adapter enable`), same priority-based
dispatch as ADR-033 adapters.

### 4. Synchronous execution with error isolation

Hooks run sequentially in-process, priority-ordered, with per-hook timeout (5s default).
An exception in a hook is caught, logged, and skipped. The operation continues.

Gates run all-must-pass at a given workflow point. A single failure blocks the operation
with a reason message.

### 5. Side effects move to hooks; inputs stay in skills

Skills lose: `rai signal emit`, `rai memory emit-work`, prerequisite checks.
Skills keep: `rai graph query`, `rai graph context`, `rai pattern add`.

The boundary: if the agent needs the result in its context, it stays in the skill.
If it's a side effect invisible to the agent, hooks/gates absorb it.

## Consequences

| Type | Impact |
|------|--------|
| ✅ Positive | ~1,000 fewer tokens per skill invocation (ceremony removed) |
| ✅ Positive | 100% telemetry coverage — no gaps from forgotten emit calls |
| ✅ Positive | PRO/Enterprise extend via same mechanism (install hook, higher priority) |
| ✅ Positive | Consistent extension model — adapters, hooks, gates all use entry points |
| ✅ Positive | Skills become pure process instructions — easier to generate (RAISE-242) |
| ⚠️ Negative | Two new protocols to understand for adapter authors |
| ⚠️ Negative | S248.7 touches 22 skills — large blast radius |
| ⚠️ Negative | Hook timeout tuning needs empirical calibration |

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|----------------------|
| Single protocol with `blocking: bool` | Mixes observer and guard semantics. Confuses intent for adapter authors. Dispatcher must branch on type at runtime. |
| Config-based hooks (shell commands in YAML) | Scripting model, not extensibility. No typing, no validation, no IDE support. Has its place (Claude Code uses it) but doesn't build the typed extension layer E248 needs. |
| Async hooks with event loop | CLI is execute-and-terminate, not a server. Async adds complexity (async def, event loop mgmt) with no benefit for local I/O or short HTTP calls. |
| `rai skill prepare` pre-processor | Couples skills to CLI. Skills should be readable markdown, not programs that need a build step. Hooks solve the same problem without coupling. |

---

<details>
<summary><strong>References</strong></summary>

- RFC-001: `dev/rfcs/rfc-001-extensibility-architecture.md`
- ADR-033: Open-Core Adapter Architecture (entry point pattern)
- ADR-034: Governance Extensibility (schema/parser/target extensions)
- RAISE-248 scope: `work/epics/raise-248-hooks-gates/scope.md`

</details>
