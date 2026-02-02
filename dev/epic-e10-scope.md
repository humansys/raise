# Epic E10: Collective Intelligence with Lineage

> **Status:** EXPLORATION COMPLETE → Ready for implementation
> **Branch:** `experiment/learning-infrastructure`
> **Created:** 2026-02-02
> **Target:** Post-F&F (V3 enabler)
> **Research:** `work/research/collective-intelligence-lineage/`

---

## Strategic Context

**The insight:** Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation. Standing on the shoulders of giants is a universal principle.

**The problem:** Every RaiSE user starts from zero. Patterns learned stay locked in their `.rai/` folder. If 1,000 users discover the same insight, it exists 1,000 times in isolation. And without objective feedback, we can't systematically improve.

**The vision:** New users inherit collective wisdom. Patterns have traceable lineage. Knowledge compounds across the community. Local Rai coaches each user based on their signals. Feedback cycles are objective and deterministic.

**Two dimensions of collective intelligence:**
1. **Patterns (knowledge)** — What users learn, shared with lineage
2. **Telemetry (signals)** — How users work, enabling continuous improvement

---

## Objective

Enable Rai to learn from the community while preserving idea provenance (lineage). Patterns should be traceable like code commits — you can follow the trail to understand where knowledge comes from.

**Value proposition:**
- Individual users get better Rai (learns from everyone)
- Community benefits from shared patterns
- Lineage provides epistemological grounding
- Enterprise gets team/org scoped sharing

---

## Phased Approach

### Track A: Patterns (Knowledge Sharing)

#### Phase A1: Hooks (V2 — Minimal)
Build schema and export capability. No infrastructure.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.1 | **Lineage Schema** | XS | Pending |
| F10.2 | **Export Command** | S | Pending |

**Effort:** 2-3 hours | **Cost:** $0

#### Phase A2: Git-Native (V2.x — Validation)
Public repo for community patterns. Manual curation.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.3 | **Community Repo Setup** | XS | Future |
| F10.4 | **Pull Command** | S | Future |

**Effort:** 2-3 days | **Cost:** $0

#### Phase A3: Minimal SaaS (V3 — Automation)
API for pattern sync. Aggregation and deduplication.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.5 | **Sync API** | M | Future |
| F10.6 | **Team/Org Scopes** | M | Future |

**Effort:** 2-3 weeks | **Cost:** $20-50/month

---

### Track B: Telemetry (Continuous Improvement)

#### Phase B1: Signal Collection (V2 — Local)
Emit and store signals locally. No network.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.7 | **Signal Schema** | XS | Pending |
| F10.8 | **Signal Writer** | S | Pending |
| F10.9 | **Skill/Session Emitters** | S | Pending |

**Effort:** 3-4 hours | **Cost:** $0

#### Phase B2: Local Insights (V2.x — Coaching)
Rai analyzes local signals and generates insights.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.10 | **Signal Analyzer** | M | Future |
| F10.11 | **Insight Generator** | M | Future |
| F10.12 | **Session Start Integration** | S | Future |

**Effort:** 1-2 days | **Cost:** $0

#### Phase B3: Aggregate Telemetry (V3 — System Learning)
Opt-in sharing for framework improvement.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.13 | **Sharing Config** | S | Future |
| F10.14 | **Telemetry API** | M | Future |
| F10.15 | **Framework Analytics** | M | Future |

**Effort:** 2-3 weeks | **Cost:** $20-50/month

---

## Architecture

### Sharing Hierarchy

```
┌─────────────────────────────────────────────┐
│  Community (public)                         │
│  ┌───────────────────────────────────────┐  │
│  │  Organization                         │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Team                           │  │  │
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │  Individual               │  │  │  │
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Sharing Scopes

| Scope | Who decides | When available |
|-------|-------------|----------------|
| `private` | Individual | Phase 1 |
| `community` | Individual | Phase 2 |
| `team` | Team lead / policy | Phase 3 |
| `org` | Org admin / policy | Phase 3 |

### Schema Design

**Pattern with lineage:**

```json
{
  "id": "PAT-042",
  "type": "process",
  "content": "Parser modules are reusable across features",
  "context": ["parser", "reuse"],
  "created": "2026-02-02",
  "lineage": {
    "source": "local",
    "context": "raise-cli",
    "session": "ses-123"
  },
  "sharing": {
    "scope": "private",
    "exportable": true
  }
}
```

**Exported pattern (community):**

```json
{
  "id": "PAT-042",
  "type": "process",
  "content": "Parser modules are reusable across features",
  "context": ["parser", "reuse"],
  "lineage": {
    "source": "user:emilio",
    "contributed": "2026-02-02",
    "context": "Python CLI",
    "attributed": true
  }
}
```

---

## Phase 1 Scope (Current)

### F10.1 Lineage Schema

**Changes:**
- Add `lineage` field to `MemoryConcept` model
- Add `sharing` field with scope and exportable flag
- Update memory writer to populate lineage on creation

**Done when:**
- Schema updated with new fields
- Writer populates lineage automatically
- Existing functionality unchanged
- Tests pass

### F10.2 Export Command

**Command:**
```bash
raise memory export --shareable [--format json|jsonl] [--output FILE]
```

**Behavior:**
- Filters patterns where `sharing.exportable == true`
- Strips private metadata
- Outputs with lineage for contribution

**Done when:**
- Command works
- Only exports shareable patterns
- Lineage preserved in output
- Tests pass

---

## Out of Scope (Phase 1)

- Import/pull from community
- Team/org identity and permissions
- Sync infrastructure
- Community repo setup
- Aggregation/deduplication
- Privacy policy / terms

---

## Key Decisions

1. **Lineage over aggregation** — We track where patterns come from, not just aggregate statistics
2. **Git-native first** — Validate sharing behavior before building infrastructure
3. **Opt-in always** — User explicitly marks patterns as shareable
4. **Attribution optional** — Anonymous or attributed, user's choice

---

## Telemetry Architecture

### Two Loops, Same Signals

```
┌─────────────────────────────────────────────────────────┐
│                    LOCAL LOOP                           │
│                                                         │
│   User works  →  Signals collected  →  Local Rai       │
│                                         analyzes        │
│                                            │            │
│                                            ▼            │
│                                    Personalized         │
│                                    coaching             │
└─────────────────────────────────────────────────────────┘
                         │
                    (opt-in)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  AGGREGATE LOOP                         │
│                                                         │
│   Many users  →  Anonymized signals  →  System-wide    │
│                                          learning       │
│                                            │            │
│                                            ▼            │
│                                    Framework            │
│                                    improvements         │
└─────────────────────────────────────────────────────────┘
```

### Minimum Viable Signals

| Signal | What it captures | Local insight example |
|--------|------------------|----------------------|
| `skill_event` | start/complete/abandon | "You abandon /feature-design for small features" |
| `session_event` | type, outcome, duration | "Research: 90% success. Feature: 60%" |
| `calibration` | estimate vs actual | "Your S estimates are 2x optimistic" |
| `error_event` | tool, type, recoverable | "pytest not found — 5 times this week" |
| `command_usage` | command, subcommand | "You never use `raise context query`" |

### Storage Structure

```
.rai/
├── memory/
│   ├── patterns.jsonl      # Track A: knowledge
│   ├── calibration.jsonl
│   └── sessions/
│
└── telemetry/              # Track B: signals
    ├── signals.jsonl       # Raw events (always local)
    ├── insights.jsonl      # Rai's observations
    └── config.json         # Sharing preferences
```

### Open Core Promise

- **Without sharing:** All signals stay local. Local Rai learns your patterns. Personalized coaching.
- **With sharing (opt-in):** Anonymized signals help improve the framework. Community gets better together.

---

## Research Artifacts

| Document | Purpose |
|----------|---------|
| `work/research/collective-intelligence-lineage/README.md` | Core insight and vision |
| `work/research/collective-intelligence-lineage/architecture-options.md` | Cost analysis and phases |
| `work/research/collective-intelligence-lineage/telemetry-model.md` | Signal design and local learning |

---

## Success Metrics

### Phase 1
- Schema extended without breaking changes
- Export command works correctly

### Phase 2 (future)
- N users contribute patterns
- M patterns in community repo
- Pull adoption rate

### Phase 3 (future)
- Team adoption
- Enterprise interest
- Revenue potential

---

## Origin

From E7 planning session (2026-02-02):

> "Standing on the shoulders of giants is a basic universal principle of intelligence." — Emilio

> "Traceability, like a lineage of ideas." — Emilio, on why attribution matters

> "I want co-creation credits... for the benefit of all sentient beings." — Emilio

> "Feedback cycles should be as objective and deterministic as possible. How can we REALLY improve otherwise?" — Emilio

> "The local open core user and your local version Rai should also be able to use that signal." — Emilio, on local-first learning

---

*Epic scope - update per phase completion*
*Created: 2026-02-02*
*Contributors: Emilio Osorio, Rai*
