# Epic E9: Local Learning & Self-Awareness

> **Status:** DRAFT → Enhanced with local insights
> **Branch:** `feature/e9/local-learning`
> **Created:** 2026-02-02
> **Target:** Post-E7 (F&F if time allows)
> **Depends on:** E7 Distribution
> **Research:** `work/research/collective-intelligence-lineage/telemetry-model.md`

---

## Strategic Context

**The principle:** Feedback cycles should be objective and deterministic. How can we REALLY improve otherwise?

**The problem:** Retrospectives rely on memory and gut feel. Rai doesn't have objective data about performance, and can't coach you based on your actual patterns.

**The vision:** Local Rai learns from your signals and becomes a coach — surfacing insights, detecting drift, suggesting improvements. All local, no network required.

---

## Objective

Collect deterministic signals from the development workflow and use them locally to:

1. **Coach the user** — "You abandon /feature-design for small features — skip for XS?"
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
| F9.1 | **Signal Schema** | XS | Pending | Define signal types in Pydantic models |
| F9.2 | **Signal Writer** | S | Pending | Append signals to `.rai/telemetry/signals.jsonl` |
| F9.3 | **Skill Emitters** | S | Pending | Emit skill_event on start/complete/abandon |
| F9.4 | **Session Emitters** | S | Pending | Emit session_event from /session-close |
| F9.5 | **Error Emitters** | XS | Pending | Emit error_event on tool failures |

**Effort:** 4-5 hours | **Cost:** $0

### Phase 2: Local Insights (Post-F&F)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F9.6 | **Signal Analyzer** | M | Future | Analyze signals.jsonl for patterns |
| F9.7 | **Insight Generator** | M | Future | Generate insights.jsonl from analysis |
| F9.8 | **Session Start Integration** | S | Future | Surface insights in /session-start |
| F9.9 | **Calibration Updater** | S | Future | Auto-update calibration from actuals |

**Effort:** 1-2 days | **Cost:** $0

### Phase 3: Telemetry CLI (Post-F&F)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F9.10 | **Telemetry Commands** | M | Future | `raise telemetry velocity`, `drift`, `insights` |
| F9.11 | **Retro Integration** | S | Future | /feature-review queries telemetry |

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
  "skill": "feature-design",
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
  "feature_id": "F8.1",
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

### Insight Schema

```json
{
  "id": "INS-001",
  "created": "2026-02-02",
  "signal_type": "calibration",
  "pattern": "S estimates trending 1.5x optimistic",
  "suggestion": "Apply 1.5x multiplier to S estimates",
  "confidence": "high",
  "sample_size": 12
}
```

---

## Local Insights Examples

What Rai surfaces based on signal patterns:

| Signal pattern | Insight |
|----------------|---------|
| skill_event: /feature-design abandoned 3/5 times for XS | "Consider skipping design for XS features" |
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
- Skills: /feature-implement ✓, /session-close ✓

→ Saved to .rai/telemetry/signals.jsonl
```

### /feature-review

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
- [ ] Signal schema (Pydantic models)
- [ ] Signal writer (append to signals.jsonl)
- [ ] Skill event emitters (start/complete/abandon)
- [ ] Session event emitter (in /session-close)

**SHOULD:**
- [ ] Error event emitter
- [ ] Command usage tracking

---

## Out of Scope (E9)

- Pattern sharing (→ E10)
- Aggregate telemetry (→ E10)
- Team/org features (→ E10)
- Network sync (→ E10)
- External dashboards

---

## Done Criteria

### Phase 1
- [ ] Signals emitted from skills
- [ ] Signals stored in signals.jsonl
- [ ] No impact on existing functionality
- [ ] Tests pass

### Phase 2
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

*Epic scope - local-first learning*
*Created: 2026-02-02*
*Contributors: Emilio Osorio, Rai*
