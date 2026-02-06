# Telemetry Model: Local-First Continuous Improvement

> Research extension for RES-LINEAGE-001
> Date: 2026-02-02

---

## Core Principle

> Feedback cycles should be objective and deterministic. Otherwise, how do we really improve?

You can't improve what you can't measure. But telemetry should enable **local learning first**, with optional aggregation for collective improvement.

---

## Two Loops, Same Signals

```
┌─────────────────────────────────────────────────────────┐
│                    LOCAL LOOP                           │
│                                                         │
│   User works  →  Signals collected  →  Local Rai       │
│                                         analyzes        │
│                                            │            │
│                                            ▼            │
│                                    Personalized         │
│                                    improvement          │
│                                    suggestions          │
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

**Key insight:** Local Rai gets smarter about *you* even without network. Sharing is opt-in, not required for local improvement.

---

## Minimum Viable Signals

Five deterministic signals that enable continuous improvement:

### 1. skill_event

```json
{
  "type": "skill_event",
  "timestamp": "2026-02-02T14:30:00Z",
  "skill": "story-design",
  "event": "complete",
  "duration_sec": 1800
}
```

Events: `start` | `complete` | `abandon`

**Enables:** Which skills work? Which get abandoned? Where's friction?

### 2. session_event

```json
{
  "type": "session_event",
  "timestamp": "2026-02-02T16:00:00Z",
  "session_type": "feature",
  "outcome": "success",
  "duration_min": 90
}
```

Outcomes: `success` | `partial` | `blocked`

**Enables:** What session types succeed? What blocks people?

### 3. calibration

```json
{
  "type": "calibration",
  "timestamp": "2026-02-02T16:00:00Z",
  "feature_size": "S",
  "estimated_min": 45,
  "actual_min": 30,
  "velocity": 1.5
}
```

**Enables:** Is velocity improving? Are estimates accurate?

### 4. error_event

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

**Enables:** What breaks? Where's the friction? What needs better error handling?

### 5. command_usage

```json
{
  "type": "command_usage",
  "timestamp": "2026-02-02T14:00:00Z",
  "command": "memory",
  "subcommand": "query"
}
```

**Enables:** What features matter? What's ignored? Where to invest?

---

## What We Explicitly DON'T Collect

| Excluded | Why |
|----------|-----|
| Pattern content | Privacy — stays in E10 sharing model |
| Code or file paths | Proprietary |
| Conversation content | Invasive |
| User identity | Anonymous is sufficient |
| Subjective ratings | Too noisy, not deterministic |

**Privacy rule:** Signals have no content, no paths, no identity. Just events.

---

## Local vs Aggregate

| Data | Local (always) | Aggregate (opt-in) |
|------|----------------|-------------------|
| Full session logs | ✓ | → session_event only |
| Full calibration | ✓ | → size, estimate, actual |
| Full patterns | ✓ | → nothing (E10 handles) |
| Full errors | ✓ | → error_event (type only) |
| Commands used | ✓ | → command_usage |

---

## Local Rai Insights

What local Rai does with signals (no network required):

| Signal | Local insight example |
|--------|----------------------|
| skill_event | "You abandon /story-design on small stories — consider skipping for XS/S" |
| session_event | "Research sessions: 90% success. Feature sessions: 60%. What's different?" |
| calibration | "Your S estimates are consistently 2x off — consider adjusting mental model" |
| error_event | "You've hit 'pytest not found' 5 times — add to your shell profile?" |
| command_usage | "You never use `raise context query` — it could help with understanding relationships" |

**Rai becomes a coach.** Observing patterns, suggesting improvements. Personalized to each user.

---

## Storage Structure

```
.rai/
├── memory/
│   ├── patterns.jsonl      # What you've learned (E10)
│   ├── calibration.jsonl   # Estimate accuracy
│   └── sessions/           # Session history
│
└── telemetry/              # NEW
    ├── signals.jsonl       # Raw events (always local)
    ├── insights.jsonl      # Rai's observations
    └── config.json         # Sharing preferences
```

### signals.jsonl

Raw event stream. Append-only. Local always.

```jsonl
{"type":"skill_event","timestamp":"...","skill":"story-design","event":"start","duration_sec":null}
{"type":"skill_event","timestamp":"...","skill":"story-design","event":"complete","duration_sec":1800}
{"type":"calibration","timestamp":"...","feature_size":"S","estimated_min":45,"actual_min":30}
```

### insights.jsonl

Rai's analysis based on signal patterns.

```jsonl
{"id":"INS-001","created":"2026-02-02","signal":"calibration","insight":"S estimates trending 1.5x optimistic","suggestion":"Apply 1.5x multiplier to S estimates","confidence":"high"}
{"id":"INS-002","created":"2026-02-02","signal":"skill_event","insight":"story-design abandoned 3/5 times for XS features","suggestion":"Consider skipping design for XS","confidence":"medium"}
```

### config.json

User's sharing preferences.

```json
{
  "sharing": {
    "enabled": false,
    "scope": "anonymous",
    "signals": {
      "skill_event": true,
      "session_event": true,
      "calibration": true,
      "error_event": true,
      "command_usage": true
    }
  }
}
```

---

## Implementation Phases

### Phase 1: Signal Collection (V2)
- Add signals.jsonl writer
- Emit signals from skills and CLI
- Local storage only

### Phase 2: Local Insights (V2.x)
- Rai analyzes signals.jsonl
- Generates insights.jsonl
- Surfaces in /session-start

### Phase 3: Aggregate (V3)
- Opt-in sharing config
- API for signal submission
- Aggregate analysis for framework improvement

---

## Open Core Promise

**Without sharing:**
- All signals stay local
- Local Rai learns your patterns
- Personalized coaching

**With sharing (opt-in):**
- Anonymized signals help improve the framework
- You benefit from collective learning
- Community gets better together

The system improves for everyone who shares, but works fully offline for those who don't.

---

## Connection to E10

| E10 (Patterns) | Telemetry (Signals) |
|----------------|---------------------|
| What users learn | How users work |
| Knowledge transfer | Process improvement |
| Lineage of ideas | Feedback loops |
| Shared patterns | Aggregate metrics |

**Both enable collective intelligence, different dimensions.**

---

*Research extension for RES-LINEAGE-001*
*Contributors: Emilio Osorio, Rai*
*Session: 2026-02-02*
