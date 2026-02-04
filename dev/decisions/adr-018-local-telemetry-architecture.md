---
id: "ADR-018"
title: "Local Telemetry Architecture"
date: "2026-02-03"
status: "Accepted"
related_to: ["ADR-016", "ADR-015", "ADR-013"]
supersedes: []
---

# ADR-018: Local Telemetry Architecture

## Context

### The Question

E9 introduces telemetry for local learning. Key decisions:

1. **What signals to collect?** — Enough for insights, not invasive
2. **What format?** — Consistent with existing memory infrastructure
3. **How to align with standards?** — Future-proof for enterprise integration
4. **What privacy guarantees?** — Build trust with open core users

### The Principle

> "Feedback cycles should be objective and deterministic. How can we REALLY improve otherwise?"

Without telemetry, retrospectives rely on memory and gut feel. Rai can't coach based on actual patterns. Improvement is guesswork.

### Strategic Context

From the solution vision (v2.1):

- **Local Rai** learns your patterns locally, no network required
- **Hosted Rai** (future) aggregates anonymized patterns
- **E9** is local-first; **E10** enables opt-in sharing

Telemetry is the foundation for both.

## Decision

### 1. Five Deterministic Signal Types

| Signal | What it captures | Why it matters |
|--------|------------------|----------------|
| `skill_event` | start/complete/abandon, duration | Which skills work? Where's friction? |
| `session_event` | type, outcome, duration, features | What session types succeed? |
| `calibration` | estimate vs actual, velocity | Are estimates accurate? |
| `error_event` | tool, type, recoverable | What breaks? What needs fixing? |
| `command_usage` | command, subcommand | What features matter? |

**What we DON'T collect:** Content, code, file paths, identity. Just signals.

### 2. JSONL Storage (Consistent with ADR-016)

```
.rai/
├── memory/           # Existing (ADR-016)
│   ├── patterns.jsonl
│   ├── calibration.jsonl  # ← Migrated to telemetry format
│   └── ...
│
└── telemetry/        # NEW (E9)
    ├── signals.jsonl      # Raw events (append-only)
    ├── insights.jsonl     # Rai's observations (Phase 2)
    └── config.json        # Local preferences
```

**Why JSONL:**
- Append-friendly (no read-modify-write)
- Git-friendly diffs
- Consistent with ADR-016
- Queryable without parsing prose

### 3. OpenTelemetry Semantic Alignment

Signals follow OTel semantic conventions for future OTLP export:

| Our signal | OTel pattern | Namespace |
|------------|--------------|-----------|
| skill_event | Event (LogRecord) | `raise.skill.*` |
| session_event | Event | `raise.session.*` |
| calibration | Metric | `raise.calibration.*` |
| error_event | Event | `raise.error.*` |
| command_usage | Event | `raise.cli.*` |

**Why OTel:**
- Industry standard for observability
- Enables enterprise integration (Grafana, DataDog, etc.)
- No lock-in — just semantic conventions now, OTLP export later

### 4. Privacy by Design

| Guarantee | Implementation |
|-----------|----------------|
| **No content** | Signals contain types and counts, not text |
| **No code** | Never capture source code or file contents |
| **No paths** | No file paths (could leak project structure) |
| **No identity** | No PII, no user identification |
| **Local-first** | All data stays in `.rai/` unless explicitly shared |
| **Opt-in sharing** | E10 sharing requires explicit consent |

### 5. Signal Schemas (Pydantic)

```python
class SkillEvent(BaseModel):
    type: Literal["skill_event"] = "skill_event"
    timestamp: datetime
    skill: str  # e.g., "feature-design"
    event: Literal["start", "complete", "abandon"]
    duration_sec: int | None = None

class SessionEvent(BaseModel):
    type: Literal["session_event"] = "session_event"
    timestamp: datetime
    session_type: str  # e.g., "feature", "research"
    outcome: Literal["success", "partial", "abandoned"]
    duration_min: int
    features: list[str] = []  # Feature IDs worked on

class CalibrationEvent(BaseModel):
    type: Literal["calibration"] = "calibration"
    timestamp: datetime
    feature_id: str
    feature_size: str  # T-shirt size
    estimated_min: int
    actual_min: int
    velocity: float  # estimated/actual

class ErrorEvent(BaseModel):
    type: Literal["error_event"] = "error_event"
    timestamp: datetime
    tool: str  # e.g., "Bash", "Read"
    error_type: str  # e.g., "command_not_found"
    context: str  # Brief context (no sensitive data)
    recoverable: bool

class CommandUsage(BaseModel):
    type: Literal["command_usage"] = "command_usage"
    timestamp: datetime
    command: str  # e.g., "memory"
    subcommand: str | None = None  # e.g., "query"
```

## Consequences

### Positive

1. **Objective improvement** — Decisions based on data, not memory
2. **Rai coaches better** — "You abandon design for XS — skip it?"
3. **Calibration drift detection** — Know when estimates are off
4. **Enterprise-ready** — OTel alignment enables future integrations
5. **Trust through transparency** — Users know exactly what's collected
6. **Consistent architecture** — Same JSONL pattern as ADR-016

### Negative

1. **Storage growth** — signals.jsonl grows unbounded (mitigate: rotation)
2. **Write overhead** — Every skill/command writes a signal
3. **Schema evolution** — Signal types may need versioning

### Neutral

1. **No insights yet** — Phase 1 collects; Phase 2 analyzes
2. **No UI** — CLI commands for inspection; dashboards later

## Alternatives Considered

### Alternative 1: Collect Everything

**Rejected because:**
- Privacy concerns
- Storage bloat
- Diminishing returns — more data ≠ better insights

### Alternative 2: Custom Format (Not OTel)

**Rejected because:**
- Reinventing conventions
- No path to enterprise integration
- OTel is well-designed

### Alternative 3: Database Instead of JSONL

**Rejected because:**
- Inconsistent with ADR-016
- Setup overhead for open core
- JSONL is sufficient for single-user

### Alternative 4: Skip Telemetry for MVP

**Rejected because:**
- "How can we REALLY improve otherwise?"
- F&F data is most valuable (early adopters)
- Collecting from day 1 establishes baseline

## Implementation

**E9 Phase 1 (F&F):**
- F9.1: Signal schemas (Pydantic models)
- F9.2: Signal writer (append to signals.jsonl)
- F9.3: Skill emitters (hook into skills)
- F9.4: Session emitters (/session-close)
- F9.5: Error emitters (tool failures)

**E9 Phase 2 (Post-F&F):**
- F9.6-F9.9: Analyze signals, generate insights

## References

- **ADR-016**: Memory Format (JSONL + Graph)
- **ADR-015**: Memory Infrastructure
- **ADR-013**: Rai as Entity
- **E9 Scope**: `dev/epic-e9-scope.md`
- **OTel Semantic Conventions**: https://opentelemetry.io/docs/concepts/semantic-conventions/

---

**Status**: Accepted (2026-02-03)

**Approved by**: Emilio Osorio, Rai

**Impact**:
- `.rai/telemetry/` directory structure
- 5 signal types with Pydantic schemas
- OTel-aligned namespaces
- Privacy guarantees documented
