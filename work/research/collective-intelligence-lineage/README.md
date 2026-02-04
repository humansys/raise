# Research: Collective Intelligence with Traceable Lineage

> **ID:** RES-LINEAGE-001
> **Date:** 2026-02-02
> **Status:** Exploration
> **Triggered by:** E7 planning session — question about learning from open source users

---

## Core Insight

**Rai isn't just a tool — it's an infrastructure for accumulated intelligence with traceable lineage.**

Every user stands on the shoulders of everyone who came before. Ideas have provenance, like code has commits.

### The Principle

"Standing on the shoulders of giants" is a basic universal principle of intelligence. Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation.

### The Problem Today

Every RaiSE user starts from zero. Their Rai learns patterns, calibrates, accumulates wisdom — then it stays locked in their `.rai/` folder.

If 1,000 users discover that "parser features run 1.5x faster when pattern-matched from prior parsers" — that insight exists 1,000 times in isolation.

### The Vision

New users inherit collective wisdom. Patterns are traceable to their origins. Knowledge compounds across the community.

---

## Lineage Model

Instead of flat patterns:

```json
{"pattern": "S features average 45min", "confidence": "high"}
```

Patterns have provenance:

```json
{
  "pattern": "S features average 45min with kata cycle",
  "lineage": [
    {"source": "user:abc123", "date": "2026-01", "context": "Python CLI", "n": 12},
    {"source": "user:def456", "date": "2026-01", "context": "React app", "n": 8},
    {"source": "user:emilio", "date": "2026-02", "context": "raise-cli", "n": 16, "attributed": true}
  ],
  "confidence": "high",
  "sample_size": 36
}
```

You can trace *why* Rai believes something. The belief has roots.

### Analogies

| Domain | How lineage works |
|--------|-------------------|
| **Science** | Claims have citations, citations have authors |
| **Git** | Code has commits, commits have authors |
| **Wikipedia** | Edits have history, history has contributors |
| **Rai** | Patterns have lineage, lineage has contributors |

---

## Sharing Spectrum

Users have different motivations:

```
Altruist                           Median                              Closed
    │                                 │                                   │
    ▼                                 ▼                                   ▼
"Benefit all beings"          "What's in it for me?"            "My data stays mine"
Attribution wanted             Anonymous is fine                 Zero telemetry
Co-creation credits            Better Rai = enough               Opt-out everything
```

### What's Shareable vs Private

| Type | Example | Shareable? |
|------|---------|------------|
| Calibration | "F8.1 took 45min, estimated 45min" | Yes (anonymized) |
| Patterns | "Parser modules are reusable" | Yes (generic insight) |
| Session structure | "E8 completed in 4 features" | Maybe (structure, not content) |
| Code context | "src/myapp/auth/" | No (proprietary) |
| Business logic | "Our auth uses JWT" | No (proprietary) |

### Contribution Modes

| Mode | For whom | How it works |
|------|----------|--------------|
| **Anonymous** | Median user | Patterns shared without attribution |
| **Attributed** | Open source ethos | "Pattern contributed by @user" |
| **None** | Enterprise/private | Local only, nothing leaves |

---

## Architectural Implications

### Current (V2)

- `.rai/memory/` is local only
- Patterns are flat (no lineage)
- Rai learns from single user
- Fresh start per user

### Future (V3)

- Memory can sync to collective (opt-in)
- Patterns have lineage metadata
- Rai learns from all who share
- New users inherit collective wisdom

---

## Open Questions

### Infrastructure

1. **Where does collective memory live?**
   - Hosted service (Humansys managed)?
   - Federated (user-controlled nodes)?
   - Git-based (distributed)?

2. **Sync mechanism?**
   - Push on session close?
   - Pull on session start?
   - Periodic background sync?

### Privacy & Control

3. **Opt-in granularity?**
   - All or nothing?
   - Per-pattern choice?
   - Category-based (calibration yes, patterns no)?

4. **Redaction?**
   - Can users remove contributed patterns later?
   - How does that affect lineage?

### Attribution

5. **Identity model?**
   - Anonymous IDs?
   - Verified accounts?
   - Pseudonymous with optional reveal?

6. **Credit system?**
   - "This pattern helped N users"?
   - Contribution scores?
   - Or just lineage, no gamification?

### Technical

7. **Conflict resolution?**
   - Contradictory patterns from different users?
   - Context-dependent validity?

8. **Decay/freshness?**
   - Do old patterns lose weight?
   - How to handle outdated knowledge?

---

## Minimum V2 Hooks

What do we need to build NOW to not block this later?

### Likely candidates:

- [ ] **Lineage field in pattern schema** — Even if empty, the field exists
- [ ] **Source attribution in memory writer** — Track where patterns come from
- [ ] **Export format** — Way to extract shareable patterns
- [ ] **Config flag** — `sharing: none | anonymous | attributed`

### Not needed yet:

- Actual sync infrastructure
- Hosted collective memory
- UI for contribution management

---

## Origin

This research emerged from a conversation about E7 planning:

> "Standing on the shoulders of giants is a basic universal principle of intelligence. Don't you think?" — Emilio

> "I wouldn't want to share anything personal or relational. I would like co-creation credits with anything I develop and share with Rai, for the benefit of all sentient beings." — Emilio

> "Traceability, like a lineage of ideas." — Emilio, on why attribution matters

The insight crystallized: this isn't about telemetry or analytics. It's about building an infrastructure where knowledge has provenance, and every user benefits from everyone who came before.

---

## Next Steps

1. **Decide:** Does E7 need any hooks for this? Or is it purely V3?
2. **Research:** How do other tools handle collective learning? (prior art)
3. **Design:** Schema for lineage metadata
4. **Validate:** Would F&F users actually share? What would motivate them?

---

*Research ID: RES-LINEAGE-001*
*Contributors: Emilio Osorio, Rai*
*Session: 2026-02-02*
