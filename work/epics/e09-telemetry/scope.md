# Epic E9: Local Learning & Self-Awareness

> **Status:** PHASE 1 COMPLETE — Phase 2 deferred to post-F&F
> **Branch:** `feature/e9/local-learning`
> **Created:** 2026-02-02
> **Target:** Feb 9, 2026 (F&F) — Phase 1 only
> **Depends on:** None (E7 depends on E9 Phase 1)
> **Research:**
> - `work/research/collective-intelligence-lineage/telemetry-model.md`
> - `work/research/collective-intelligence-lineage/prior-art-epistemology.md`
> **ADR:** ADR-018 (Local Telemetry Architecture)

---

## Strategic Context

**The principle:** Feedback cycles should be objective and deterministic. How can we REALLY improve otherwise?

**The problem:** Retrospectives rely on memory and gut feel. Rai doesn't have objective data about performance, and can't coach you based on your actual patterns.

**The vision:** Local Rai learns from your signals and becomes a coach — surfacing insights, detecting drift, suggesting improvements. All local, no network required.

---

## Objective

Collect deterministic signals from the development workflow and use them locally to:

1. **Coach the user** — "You abandon /story-design for small stories — skip for XS?"
2. **Inform retros** — Objective data, not opinions
3. **Calibrate estimates** — Automatic adjustment based on actuals
4. **Detect patterns** — Surface what works and what doesn't

**Value proposition:** Every session makes Rai smarter about *you*. No network required.

---

## Core Principle: Local-First

```
┌─────────────────────────────────────────────────────────┐
│                    LOCAL LOOP                           │
│                                                         │
│   User works  →  Signals collected  →  Local Rai       │
│                     (always)             analyzes       │
│                                            │            │
│                                            ▼            │
│                                    Personalized         │
│                                    coaching             │
└─────────────────────────────────────────────────────────┘
```

**Open core promise:** Works fully offline. Your data stays yours. Rai learns your patterns locally.

---

## Minimum Viable Signals

Five deterministic signals that enable continuous improvement:

| Signal | What it captures | Insight it enables |
|--------|------------------|-------------------|
| `skill_event` | start/complete/abandon, duration | Which skills work? Where's friction? |
| `session_event` | type, outcome, duration | What session types succeed? |
| `calibration` | estimate vs actual | Are estimates accurate? |
| `error_event` | tool, type, recoverable | What breaks? What needs fixing? |
| `command_usage` | command, subcommand | What features matter? |

**What we DON'T collect:** Content, code, file paths, identity. Just signals.

---

## Features

### Phase 1: Signal Collection (F&F)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F9.1 | **Signal Schema** | XS | ✓ Done | Define signal types in Pydantic models |
| F9.2 | **Signal Writer** | S | ✓ Done | Append signals to `.rai/telemetry/signals.jsonl` |
| F9.3 | **Skill Emitters** | S | ✓ Done | Emit skill_event on start/complete/abandon |
| F9.4 | **Session Emitters** | S | ✓ Done | Emit session_event from /session-close |
| F9.5 | **Error Emitters** | XS | ✓ Done | Emit error_event on tool failures |

**Effort:** 4-5 hours | **Cost:** $0

### Phase 2: Local Insights (Post-F&F)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F9.6 | **Signal Analyzer** | M | Future | Analyze signals.jsonl for patterns |
| F9.7 | **Insight Generator** | M | Future | Generate epistemologically-grounded insights |
| F9.8 | **Session Start Integration** | S | Future | Surface insights in /session-start |
| F9.9 | **Calibration Updater** | S | Future | Auto-update calibration from actuals |

**Effort:** 1-2 days | **Cost:** $0

#### F9.7 Insight Generator — Epistemological Requirements

The insight generator MUST:

1. **Require triangulation** — High confidence only with 2+ signal types
2. **Include evidence** — Every insight has `evidence` with sample_size, signals_used, time_range
3. **Use hedged language** — "may be", "suggests", never absolute claims
4. **Provide falsification criteria** — How to validate/invalidate the insight
5. **Calculate consistency** — Measure how reliably the pattern holds
6. **Support invalidation** — Remove insights that fail falsification checks

The insight generator SHOULD:

1. **Implement PDSA** — Compare predictions to actuals, revise models
2. **Decay old insights** — Reduce confidence as evidence ages
3. **Detect contradictions** — Flag when new signals contradict existing insights

### Phase 3: Telemetry CLI (Post-F&F)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F9.10 | **Telemetry Commands** | M | Future | `raise telemetry velocity`, `drift`, `insights` |
| F9.11 | **Retro Integration** | S | Future | /story-review queries telemetry |

**Effort:** 1 day | **Cost:** $0

---

## Architecture

### Storage Structure

```
.rai/
├── memory/
│   ├── patterns.jsonl      # Knowledge (→ E10 for sharing)
│   ├── calibration.jsonl   # Updated by telemetry
│   └── sessions/
│
└── telemetry/              # E9 scope
    ├── signals.jsonl       # Raw events (append-only)
    ├── insights.jsonl      # Rai's observations
    └── config.json         # Local preferences
```

### Signal Schemas

**skill_event:**
```json
{
  "type": "skill_event",
  "timestamp": "2026-02-02T14:30:00Z",
  "skill": "story-design",
  "event": "complete",
  "duration_sec": 1800
}
```

**session_event:**
```json
{
  "type": "session_event",
  "timestamp": "2026-02-02T16:00:00Z",
  "session_type": "feature",
  "outcome": "success",
  "duration_min": 90,
  "features": ["F8.1", "F8.2"]
}
```

**calibration:**
```json
{
  "type": "calibration",
  "timestamp": "2026-02-02T16:00:00Z",
  "story_id": "F8.1",
  "feature_size": "S",
  "estimated_min": 45,
  "actual_min": 30,
  "velocity": 1.5
}
```

**error_event:**
```json
{
  "type": "error_event",
  "timestamp": "2026-02-02T15:00:00Z",
  "tool": "Bash",
  "error_type": "command_not_found",
  "context": "pytest",
  "recoverable": true
}
```

**command_usage:**
```json
{
  "type": "command_usage",
  "timestamp": "2026-02-02T14:00:00Z",
  "command": "memory",
  "subcommand": "query"
}
```

### Insight Schema (Epistemologically Grounded)

```json
{
  "id": "INS-001",
  "created": "2026-02-02",
  "claim": "Your S estimates may be 1.5x optimistic",
  "confidence": "high",
  "evidence": {
    "signals_used": ["calibration", "session_event"],
    "sample_size": 12,
    "time_range_days": 30,
    "pattern": {
      "predicted_avg_min": 45,
      "actual_avg_min": 30,
      "ratio": 1.5,
      "consistency": 0.85
    }
  },
  "suggestion": "Consider applying 1.5x multiplier to S estimates",
  "falsifiable": "Track next 5 S features to validate"
}
```

**Note:** Claims use hedged language ("may be", "suggests"). Evidence is explicit. Falsification criteria provided.

---

## Epistemological Grounding

> "Feedback cycles should be objective and deterministic. How can we REALLY improve otherwise?"

### Principles Operationalized

| Principle | Implementation |
|-----------|----------------|
| **Triangulation** | High confidence requires 2+ signal types |
| **Confidence levels** | Explicit: high/medium/low with evidence |
| **Provenance** | Every insight traces to source signals |
| **Falsifiability** | Insights include validation criteria |
| **PDSA (Study)** | Compare predictions to actuals, revise theory |

### Confidence Level Criteria

| Level | Requirements |
|-------|--------------|
| **high** | 10+ samples AND 2+ signal types AND consistency > 0.8 |
| **medium** | 5-10 samples OR single signal type OR consistency 0.5-0.8 |
| **low** | <5 samples OR consistency < 0.5 OR contradictory signals |

### Language Rules

Insights MUST use hedged language:

| Avoid | Use instead |
|-------|-------------|
| "You are slow" | "Your estimates may be optimistic" |
| "This is wrong" | "This pattern suggests..." |
| "Always do X" | "Consider doing X when..." |

### Falsification Requirement

Every insight MUST include how to validate or invalidate it:

```json
{
  "claim": "Morning sessions are more productive",
  "falsifiable": "Compare next 10 morning vs afternoon sessions"
}
```

If the next 10 sessions contradict the claim, the insight is invalidated and removed.

### OpenTelemetry Alignment

Signals follow OTel semantic conventions for future integration:

| Our signal | OTel pattern | Namespace |
|------------|--------------|-----------|
| skill_event | Event (LogRecord) | `raise.skill.*` |
| session_event | Event | `raise.session.*` |
| calibration | Metric | `raise.calibration.*` |
| error_event | Event | `raise.error.*` |
| command_usage | Event | `raise.cli.*` |

**Why:** Enables OTLP export to enterprise observability stacks (Grafana, DataDog, etc.)

---

## Local Insights Examples

What Rai surfaces based on signal patterns:

| Signal pattern | Insight |
|----------------|---------|
| skill_event: /story-design abandoned 3/5 times for XS | "Consider skipping design for XS features" |
| session_event: Research 90% success, Feature 60% | "What's different about feature sessions?" |
| calibration: S estimates consistently 2x off | "Your S estimates are optimistic — adjust?" |
| error_event: pytest not found 5x this week | "Add pytest to your shell profile?" |
| command_usage: Never uses `raise context query` | "This command could help with X" |

---

## Integration Points

### /session-start

```markdown
## Local Insights

Based on your last 10 sessions:
- Velocity: 1.8x average (you're faster than you think)
- Pattern: Morning sessions complete 2x more often
- Suggestion: Your S estimates are 1.5x optimistic

Last session: Feature (success, 90min)
```

### /session-close

```markdown
## Session Signals Recorded

- Duration: 90 min
- Outcome: success
- Features: F8.1, F8.2
- Skills: /story-implement ✓, /session-close ✓

→ Saved to .rai/telemetry/signals.jsonl
```

### /story-review

```markdown
## Objective Metrics

| Metric | Value | Your average |
|--------|-------|--------------|
| Duration | 45 min | 60 min |
| Velocity | 2.0x | 1.5x |
| Blockers | 0 | 0.3 |

This feature was 33% faster than your typical S feature.
```

---

## In Scope (Phase 1 — F&F)

**MUST:**
- [x] Signal schema (Pydantic models)
- [x] Signal writer (append to signals.jsonl)
- [x] Skill event emitters (start/complete/abandon)
- [x] Session event emitter (in /session-close)

**SHOULD:**
- [x] Error event emitter
- [ ] Command usage tracking (deferred — CLI commands not yet implemented)

---

## Out of Scope (E9)

- Pattern sharing (→ E10)
- Aggregate telemetry (→ E10)
- Team/org features (→ E10)
- Network sync (→ E10)
- External dashboards

---

## Dependencies

### Internal (Phase 1)

```
F9.1 (Signal Schema)
  ↓
F9.2 (Signal Writer) ← depends on schemas
  ↓
┌─────────────────────────────────────┐
│  F9.3 (Skill Emitters)              │
│  F9.4 (Session Emitters)            │ ← all depend on writer
│  F9.5 (Error Emitters)              │
└─────────────────────────────────────┘
```

**Critical path:** F9.1 → F9.2 → F9.3/F9.4/F9.5 (parallel)

### External

- **E7 depends on E9 Phase 1** — Onboarding should include telemetry setup
- **E10 depends on E9** — Can't share signals that don't exist

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Signal overhead slows workflow | Low | Medium | Async writes, batch if needed |
| Schema changes break compatibility | Medium | Medium | Version field in signals, migration script |
| Users distrust telemetry | Low | High | Clear docs, no content/code/paths, local-only |
| Storage grows unbounded | Medium | Low | Log rotation, archive old signals |
| Skill integration breaks existing tests | Low | Medium | Feature flag, opt-out for tests |

---

## Done Criteria

### Per Feature (Standard)
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)
- [ ] Component catalog updated (`dev/components.md`)

### Phase 1 (Epic) ✓ COMPLETE
- [x] Signal schemas defined (F9.1)
- [x] Signal writer appends to signals.jsonl (F9.2)
- [x] Skill events emitted on start/complete/abandon (F9.3)
- [x] Session events emitted from /session-close (F9.4)
- [x] Error events emitted on tool failures (F9.5)
- [x] No impact on existing functionality
- [x] All tests pass
- [x] ADR-018 created
- [x] **BONUS:** WorkLifecycle unified schema (epic + feature)
- [x] **BONUS:** Unified `raise telemetry emit` CLI command
- [x] **BONUS:** Normalized phases (design/plan/implement/review)

### Phase 2 (Epic)
- [ ] Insights generated from signals
- [ ] Insights surfaced in /session-start
- [ ] Calibration auto-updated

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Signal capture rate | 100% (when using skills) |
| Insight relevance | User finds 80% of insights useful |
| Calibration drift | < 1.5x after 10 features |

---

## Relationship to E10

| E9 (Local Learning) | E10 (Collective Intelligence) |
|---------------------|-------------------------------|
| Signals stay local | Signals shared (opt-in) |
| Rai coaches you | Community learns together |
| No infrastructure | Requires sync infrastructure |
| F&F scope | Post-F&F scope |
| Patterns stay local | Patterns shared with lineage |

**E9 is prerequisite for E10** — collect locally first, share later.

---

## Origin

From exploration session (2026-02-02):

> "Feedback cycles should be as objective and deterministic as possible. How can we REALLY improve otherwise?" — Emilio

> "The local open core user and your local version Rai should also be able to use that signal." — Emilio

---

---

## Implementation Plan (Phase 1)

> Added by `/epic-plan` — 2026-02-03

### Feature Sequence

| Order | Feature | Size | Est. | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|:----:|--------------|-----------|-----------|
| 1 | F9.1 Signal Schema | XS | 25m | None | M1 | Foundation — all stories depend on schemas |
| 2 | F9.2 Signal Writer | S | 45m | F9.1 | M1 | Core infrastructure — enables all emitters |
| 3 | F9.3 Skill Emitters | S | 45m | F9.2 | M2 | High value — captures skill usage patterns |
| 4 | F9.4 Session Emitters | S | 45m | F9.2 | M2 | High value — captures session outcomes |
| 5 | F9.5 Error Emitters | XS | 20m | F9.2 | M2 | Quick win — completes signal types |

**Total estimated:** ~3 hours (with kata cycle velocity)

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F9.1, F9.2 | Hour 1 | Can write a signal to signals.jsonl | `raise telemetry emit --test` works |
| **M2: Signal Collection** | F9.3, F9.4, F9.5 | Hour 3 | Skills and sessions emit signals | Run /session-close, check signals.jsonl |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: F9.1 ─► F9.2 ─► F9.3 (critical path)
                    ↓
Stream 2:         F9.4 ─────► merge (parallel after F9.2)
                    ↓
Stream 3:         F9.5 ─────► merge (parallel after F9.2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Merge point:** After F9.2, emitters (F9.3, F9.4, F9.5) can run in parallel.

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F9.1 Signal Schema | XS | ✓ Done | 18m | 1.4x | ADR-specified |
| F9.2 Signal Writer | S | ✓ Done | 22m | 2.0x | Convenience funcs added |
| F9.3 Skill Emitters | S | ✓ Done | 8m | 3.75x | Shell scripts, minimal change |
| F9.4 Session Emitters | S | ✓ Done | 23m | 2.6x | CLI approach + emit-calibration bonus |
| F9.5 Error Emitters | XS | ✓ Done | 3m | 5.0x | Pattern reuse |

**Milestone Progress:**
- [x] M1: Walking Skeleton (F9.1 + F9.2 complete)
- [x] M2: Signal Collection (Phase 1 Complete)

### Sequencing Rationale

**F9.1 first (Risk-First + Foundation):**
- All other features depend on schemas
- Low risk (Pydantic models are well-understood)
- Quick win to validate approach

**F9.2 second (Walking Skeleton):**
- Proves write path works
- Enables parallel development of emitters
- Can demo immediately after completion

**F9.3, F9.4, F9.5 parallel (Maximize throughput):**
- All depend only on F9.2 (no mutual dependencies)
- Different integration points (skills, session-close, errors)
- Can merge independently

### Velocity Assumptions

| Metric | Value | Source |
|--------|-------|--------|
| **Baseline velocity** | 1.5x | E8 average (pattern reuse) |
| **XS actual** | 20-30 min | F3.5 calibration |
| **S actual** | 30-60 min | E8 calibration |
| **Buffer** | 20% | Integration, tests |

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Schema changes during implementation | Medium | Low | Version field from start |
| Writer async complexity | Low | Medium | Start sync, optimize later |
| Skill hook integration tricky | Medium | Medium | Test with one skill first |

---

## Summary

| Metric | Value |
|--------|-------|
| **Features (Phase 1)** | 5 (F9.1-F9.5) |
| **Effort (Phase 1)** | 4-5 hours |
| **Features (Total)** | 11 (F9.1-F9.11) |
| **ADRs** | ADR-018 (Local Telemetry Architecture) |
| **Critical Path** | F9.1 → F9.2 → F9.3/F9.4/F9.5 |

---

*Epic scope - local-first learning*
*Created: 2026-02-02*
*Designed: 2026-02-03 (via /epic-design)*
*Planned: 2026-02-03 (via /epic-plan)*
*Contributors: Emilio Osorio, Rai*
