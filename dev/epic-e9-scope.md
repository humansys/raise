# Epic E9: Telemetry & Self-Awareness - Scope

> **Status:** DRAFT
> **Branch:** TBD (`feature/e9/telemetry`)
> **Created:** 2026-02-02
> **Target:** Post-F&F (Feb 15+)
> **Depends on:** E8 Work Tracking Graph

---

## Problem Statement

Retrospectives are currently manual and subjective. Rai doesn't have objective data about:
- How long features actually take vs estimates
- Where time is spent (design vs implementation vs debugging)
- Which patterns lead to better outcomes
- Session productivity trends

**Without telemetry:** Retros rely on memory and gut feel.
**With telemetry:** Retros are informed by data, calibration improves automatically.

---

## Objective

Instrument the development workflow to collect objective metrics that inform:
1. **Rai's self-awareness** — Know how we're performing
2. **Retrospectives** — Data-driven insights, not just opinions
3. **Calibration** — Automatic adjustment of estimates based on actuals
4. **Continuous improvement** — Detect patterns, suggest process changes

**Value proposition:** Close the learning loop. Every session contributes to getting better.

---

## What to Measure

### Session Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| Session duration | Start/end timestamps | Productivity patterns |
| Features touched | Git diff + graph query | Focus vs context switching |
| Commits made | Git log | Output cadence |
| Tests added/modified | Git diff | Quality investment |
| Lines changed | Git diff | Scope indicator |

### Feature Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| Estimated size | Epic scope (T-shirt) | Baseline |
| Actual duration | Session logs | Calibration |
| Velocity ratio | Actual / Estimated | Drift detection |
| Blockers encountered | Manual tag or detection | Process improvement |
| Rework count | Same file touched >2 sessions | Quality signal |

### Process Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| Kata adherence | Skill invocations | Process discipline |
| Retro completion rate | Session logs | Learning loop closure |
| Parking lot growth | Parking lot file | Scope creep indicator |
| Memory updates | .rai/memory/ changes | Learning capture |

---

## Features

| ID | Feature | Size | Priority | Description |
|----|---------|:----:|:--------:|-------------|
| F9.1 | **Session Tracker** | S | P0 | Record session start/end, features touched |
| F9.2 | **Feature Timer** | S | P0 | Track actual time per feature |
| F9.3 | **Velocity Calculator** | S | P0 | Compute estimated vs actual ratios |
| F9.4 | **Telemetry Storage** | S | P0 | JSONL storage in `.rai/telemetry/` |
| F9.5 | **Telemetry CLI** | M | P1 | `raise telemetry velocity`, `raise telemetry drift` |
| F9.6 | **Retro Integration** | S | P1 | `/feature-review` queries telemetry automatically |
| F9.7 | **Calibration Updater** | M | P2 | Auto-update calibration.jsonl from actuals |
| F9.8 | **Dashboard Export** | M | P2 | Export metrics for visualization |

**F&F Scope:** F9.1-F9.4 (collection + storage)
**Post-F&F:** F9.5-F9.8 (CLI + integration)

---

## Architecture

### Data Flow

```
Session Start (hook)
    ↓
    Record: timestamp, goal, focus_epic, focus_feature
    ↓
Work happens...
    ↓
    Track: commits, files changed, skill invocations
    ↓
Session Close (hook/skill)
    ↓
    Record: duration, outcome, blockers
    ↓
    Calculate: velocity, drift
    ↓
    Store: .rai/telemetry/sessions.jsonl
    ↓
Feature Complete
    ↓
    Aggregate: total time, sessions count, velocity ratio
    ↓
    Store: .rai/telemetry/features.jsonl
    ↓
/feature-review
    ↓
    Query: telemetry for objective data
    ↓
    Enrich: retro with metrics
```

### Storage Structure

```
.rai/
├── telemetry/
│   ├── sessions.jsonl      # Per-session metrics
│   ├── features.jsonl      # Per-feature aggregates
│   └── daily.jsonl         # Daily summaries
└── memory/
    └── calibration.jsonl   # Updated by telemetry
```

### Session Record Schema

```jsonl
{
  "id": "SESSION-2026-02-02-001",
  "date": "2026-02-02",
  "start": "2026-02-02T08:00:00Z",
  "end": "2026-02-02T12:30:00Z",
  "duration_min": 270,
  "type": "feature",
  "goal": "Implement E8 Work Tracking Graph",
  "epic": "E8",
  "features": ["F8.1", "F8.2"],
  "outcome": "complete",
  "commits": 5,
  "files_changed": 12,
  "lines_added": 450,
  "lines_removed": 120,
  "tests_added": 15,
  "skills_used": ["/feature-implement", "/session-close"],
  "blockers": [],
  "notes": "Smooth session, parser worked first try"
}
```

### Feature Record Schema

```jsonl
{
  "id": "F8.1",
  "epic": "E8",
  "name": "Backlog Parser",
  "size": "S",
  "estimated_hours": 2,
  "actual_hours": 1.5,
  "velocity_ratio": 1.33,
  "sessions": ["SESSION-2026-02-02-001"],
  "started": "2026-02-02",
  "completed": "2026-02-02",
  "blockers_count": 0,
  "rework_count": 0
}
```

---

## CLI Commands

```bash
# Session metrics
$ raise telemetry session --last
Session: 2026-02-02 (4.5h)
  Features: F8.1, F8.2
  Commits: 5
  Velocity: 1.33x (faster than estimated)

# Velocity trends
$ raise telemetry velocity --last 10
Feature     Est    Actual  Ratio
F3.1        2h     0.25h   8.0x   ← Kata cycle boost
F3.3        2h     1h      2.0x
F8.1        2h     1.5h    1.33x
Average:                   2.5x

# Drift detection
$ raise telemetry drift --threshold 0.5
⚠ Calibration drift detected
  S features: Estimated 2h, Actual avg 0.8h
  Recommendation: Adjust S estimate to 1h

# Feature summary (for retros)
$ raise telemetry feature F8.1
Feature: F8.1 Backlog Parser
  Size: S (estimated 2h)
  Actual: 1.5h across 1 session
  Velocity: 1.33x
  Blockers: None
  Rework: None
```

---

## Integration Points

### /session-start

```markdown
## Telemetry Context

Last 5 sessions: avg 3.2h, velocity 2.1x
Current streak: 3 sessions completing goals
Calibration status: Healthy (drift < 0.3x)
```

### /session-close

```markdown
## Session Telemetry

Duration: 4.5h
Features: F8.1 ✓, F8.2 ✓
Velocity this session: 1.5x
Commits: 5 (healthy cadence)

→ Recorded to .rai/telemetry/sessions.jsonl
```

### /feature-review

```markdown
## Objective Metrics (from telemetry)

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Actual time | 1.5h | Est: 2h |
| Velocity | 1.33x | Avg: 2.1x |
| Sessions | 1 | Target: 1-2 |
| Blockers | 0 | Avg: 0.3 |

Interpretation: Feature completed efficiently, no rework.
```

---

## Privacy & Data Ownership

**Principle:** All telemetry is local. User owns their data.

- Stored in `.rai/telemetry/` (git-ignored by default)
- No external transmission
- User can delete anytime
- Export for personal analysis only

**Future (V3):** Opt-in team aggregation with anonymization.

---

## In Scope (F&F)

**MUST:**
- [ ] Session start/end recording
- [ ] Feature time tracking
- [ ] JSONL storage structure
- [ ] Basic velocity calculation

**SHOULD:**
- [ ] Hook into /session-start and /session-close
- [ ] `raise telemetry session --last`

---

## Out of Scope

- Team aggregation (V3)
- External dashboards (V3)
- Predictive analytics (V4)
- Automated recommendations (V4)

---

## Done Criteria

- [ ] Sessions automatically recorded
- [ ] Feature time tracked accurately
- [ ] `raise telemetry velocity` shows trends
- [ ] /feature-review can query telemetry
- [ ] Data stored locally, git-ignored

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Session capture rate | 100% (when using skills) |
| Velocity calculation accuracy | ±10% of manual tracking |
| Retro data availability | Every feature has metrics |

---

## Future Vision

Telemetry enables:

1. **Predictive estimation** — "Based on history, this M feature will take ~4h"
2. **Pattern detection** — "You're faster in morning sessions"
3. **Team insights** — "Team velocity is 2.3x with RaiSE vs 1.0x without"
4. **Process optimization** — "Kata cycle adds 30min but saves 2h in rework"

---

*Draft created: 2026-02-02*
*Status: Ready for review*
