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

> **Status:** IN PROGRESS
> Branch: `epic/e248/hooks-gates`
> Created: 2026-02-21
> Depends on: RAISE-211 (complete), RAISE-247 (complete)

---

## Objective

Move cross-cutting concerns (telemetry, notifications, compliance) from skill content
to CLI infrastructure via lifecycle hooks and workflow gates. Skills lose ceremony
overhead and become pure process instructions.

**Value proposition:** ~1,000 fewer tokens per skill invocation, 100% telemetry coverage
(no gaps from forgotten emit calls), and the extensibility mechanism PRO/Enterprise
adapters use for their own cross-cutting concerns.

---

## Stories (7)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S248.1 | Event emitter infrastructure | M | Pending | Core event bus with typed dataclass events and before/after pattern |
| S248.2 | Hook Protocol and registry | M | Pending | `LifecycleHook` Protocol, entry point discovery, priority dispatch |
| S248.3 | Built-in TelemetryHook | S | Pending | COMMUNITY hook that replaces manual `rai signal emit` in skills |
| S248.4 | Wire events into CLI commands | M | Pending | Add `emit()` calls to 8 CLI command groups |
| S248.5 | WorkflowGate Protocol and registry | M | Pending | `WorkflowGate` Protocol, gate composition, `rai gate check` command |
| S248.6 | Built-in gates | S | Pending | tests, types, lint, coverage — executable guardrails |
| S248.7 | Remove ceremony from skills | M | Pending | Strip telemetry/prerequisite steps from all 22 skills |

**Total:** 7 stories (4M + 2S + 1M), estimated 5-7 days

---

## In Scope

**MUST:**
- Event emitter with typed dataclass events (frozen, with before/after variants)
- `LifecycleHook` Protocol with entry point discovery (`rai.hooks`)
- `WorkflowGate` Protocol with entry point discovery (`rai.gates`)
- Built-in TelemetryHook (COMMUNITY) replacing manual emit calls
- Built-in quality gates (tests, types, lint, coverage)
- `rai gate check <gate-id>` CLI command
- Ceremony removal from all 22 skills in `skills_base/`
- Hook error isolation (exception → log + continue, never crash CLI)

**SHOULD:**
- Verbose mode showing hook execution (`rai graph build -v` shows hook:telemetry fired)
- `rai hooks list` / `rai gates list` commands for discoverability

---

## Out of Scope (deferred)

- **Context providers** (`rai.providers.context`) → RAISE-242 (Skill Builder). Would eliminate `rai graph query` from skills by pre-loading context. Requires knowing what context each skill needs.
- **Output formatters** (`rai.providers.output`) → Future epic. Low priority.
- **Scaffold providers** (`rai.providers.scaffold`) → Future epic. Useful for `rai init` customization.
- **`rai skill prepare`** → Rejected. Couples skills to CLI. Hooks solve the same problem without coupling.
- **Async hooks** → Not needed for CLI tool. Fire-and-forget to daemon is future scope (parking lot: Local Rai Runtime).

---

## Architecture Decisions

### AD-1: Sync execution, typed events, before/after pattern (ADR-039)

**Decision:** Events are synchronous, typed as frozen dataclasses, with `before:` and `after:` variants.

**Rationale:**
- **Sync** — CLI executes and terminates. No server, no open connections. Async adds event loop complexity with no benefit for local I/O or short HTTP calls. Timeout (5s) handles slow hooks.
- **Typed** — Each event is a frozen dataclass with specific payload fields. Follows RAISE-211 pattern (Pydantic models for boundary objects). IDE autocompletion + pyright validation for adapter authors.
- **before/after** — `before:` hooks can abort operations (compliance, validation). `after:` hooks observe results (telemetry, notifications). Clear separation of intent.

### AD-2: Entry point discovery (same as RAISE-211)

**Decision:** Hooks and gates use `importlib.metadata` entry points, identical to RAISE-211 adapter discovery.

**Rationale:** One model mental for all extensions. `adapters/registry.py` already has the pattern. Adding `get_hooks()` and `get_gates()` is mechanical. Same security model (`rai adapter enable`). Same priority-based dispatch.

**Rejected:** Config-based registration (`.raise/hooks.yaml`). This is a scripting model, not an extensibility model. Shell hooks have their place (Claude Code uses them), but E248 builds typed, validated, Python-level extension points.

### AD-3: Two separate protocols (Hook vs Gate)

**Decision:** `LifecycleHook` and `WorkflowGate` are separate protocols with separate entry point groups.

**Rationale:**
- **Different questions:** Hook = "what happened?" (react). Gate = "is this allowed?" (validate).
- **Different failure semantics:** Hook failure → log + continue. Gate failure → block operation.
- **Different composition:** Hooks are independent (one fails, others run). Gates are all-must-pass (one fails, operation blocked).
- **Different UX:** Gate failures need actionable messages ("Tests failing. Run `pytest`"). Hook failures need warnings ("Telemetry hook failed, continuing").

**Rejected:** Single protocol with `blocking: bool` flag. Mixes semantics, forces dispatcher to branch on type at runtime, confuses adapter authors about intent.

### AD-4: Side effects → hooks, inputs/outputs → skills

**Decision:** Skills keep `rai graph query`, `rai graph context`, `rai pattern add`. Skills lose `rai signal emit`, `rai memory emit-work`, prerequisite checks.

**Rationale:** The dividing line is whether the agent needs the result in its context. Graph queries are inputs the agent reads and uses for decisions. Signal emissions are side effects invisible to the agent. Gates replace prerequisite checks that skills currently do manually.

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on story code)
- [ ] All quality checks pass (ruff, pyright, bandit)
- [ ] TDD cycle followed (red-green-refactor)

### Epic Complete
- [ ] All 7 stories complete (S248.1–S248.7)
- [ ] Zero `rai signal emit` / `rai memory emit-work` calls remain in `skills_base/`
- [ ] TelemetryHook produces same signals.jsonl output as manual emit calls
- [ ] Hook error isolation verified (broken hook doesn't crash CLI)
- [ ] `rai gate check` works for all 4 built-in gates
- [ ] Architecture docs updated
- [ ] Epic merged to `v2`

---

## Dependency Order

```
S248.1 (event emitter) → S248.2 (hook protocol) → S248.3 (telemetry hook)
                                                 → S248.4 (wire events)
                          S248.5 (gate protocol) → S248.6 (built-in gates)
                                                            ↓
                                                 S248.7 (remove ceremony)
```

- S248.1–S248.2: infrastructure (sequential)
- S248.3–S248.6: can partially parallelize after S248.2
- S248.5 depends on S248.1 (uses same event model) but NOT on S248.2
- S248.7 goes last — requires S248.3, S248.4, S248.6 all complete

---

## Problem

Every lifecycle skill repeats the same pattern:

```
Step 0:    rai signal emit work ... --event start     ← telemetry (in every skill)
Step 0.x:  rai graph query "..."                      ← context loading (in every skill)
Step N:    [actual work]
Step N+1:  rai signal emit work ... --event complete   ← telemetry (in every skill)
```

68% of CLI calls in skills are this ceremony. ~1,000 tokens and ~2 seconds per skill
invocation. Fragile — if a skill forgets to emit, telemetry has gaps.

---

## Verification Gate

```bash
# Hooks fire on CLI commands
rai graph build -v 2>&1 | grep -q "hook:telemetry"

# No emit calls in skills
grep -r "signal emit\|memory emit" src/rai_cli/skills_base/ && exit 1

# Gates work
rai gate check gate-tests
rai gate check gate-types

# Hook error isolation
# (test that a broken hook doesn't crash the CLI)
```

---

## Epic Dependency Chain

```
RAISE-211 (Adapter Foundation — entry points, TierContext) ✅
  → RAISE-247 (CLI Ontology — rename commands) ✅
    → RAISE-248 (THIS — hooks + gates on new ontology)
      → RAISE-242 (Skill Builder — generates skills without ceremony)
```

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Adapter architecture | ADR-033 | Protocol + entry points pattern E248 reuses |
| Governance extensibility | ADR-034 | Schema/parser/target extension points |
| Hooks & Gates architecture | ADR-039 | Sync, typed, two protocols, side-effect boundary |

---

## Notes

### Key Risks
- **S248.7 blast radius:** Touching 22 skills is a large surface. Mitigate with grep gate (zero remaining emit calls) and manual spot-check of 3-4 skills.
- **Hook timeout tuning:** 5s default may be too long for fast CLI commands, too short for HTTP hooks. Mitigate by making it configurable per-hook and starting conservative.
- **Backward compat:** Skills that explicitly call `rai signal emit` still work (the command exists). But double-emit could occur if both skill and TelemetryHook fire. Mitigate: S248.7 removes skill calls before TelemetryHook is widely deployed.

### Why This Epic Now
- RAISE-211 and RAISE-247 are complete — the infrastructure foundation is ready
- Ceremony overhead is the #1 token cost in skill execution
- PRO/Enterprise extensibility requires the hook mechanism to exist
- Skill Builder (RAISE-242) needs hooks to exist before it can generate ceremony-free skills

---

## References

- RFC-001: `dev/rfcs/rfc-001-extensibility-architecture.md` (full design)
- RFC-002: `dev/rfcs/rfc-002-skill-builder-vision.md` (ceremony analysis)
- ADR-033: Open-Core Adapter Architecture
- ADR-034: Governance Extensibility
- ADR-039: Lifecycle Hooks & Workflow Gates
- SES-234: Ontological analysis session (2026-02-21)

---

*Epic tracking — update per story completion*
*Created: 2026-02-21*
*Design complete: 2026-02-23*
