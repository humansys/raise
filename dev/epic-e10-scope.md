# Epic E10: Collective Intelligence with Lineage

> **Status:** EXPLORATION COMPLETE → Ready for implementation
> **Branch:** `experiment/learning-infrastructure`
> **Created:** 2026-02-02
> **Target:** Post-F&F (V3 enabler)
> **Research:** `work/research/collective-intelligence-lineage/`

---

## Strategic Context

**The insight:** Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation. Standing on the shoulders of giants is a universal principle.

**The problem:** Every RaiSE user starts from zero. Patterns learned stay locked in their `.rai/` folder. If 1,000 users discover the same insight, it exists 1,000 times in isolation.

**The vision:** New users inherit collective wisdom. Patterns have traceable lineage. Knowledge compounds across the community.

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

### Phase 1: Hooks (V2 — Minimal)
Build schema and export capability. No infrastructure.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.1 | **Lineage Schema** | XS | Pending |
| F10.2 | **Export Command** | S | Pending |

**Effort:** 2-3 hours
**Cost:** $0

### Phase 2: Git-Native (V2.x — Validation)
Public repo for community patterns. Manual curation.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.3 | **Community Repo Setup** | XS | Future |
| F10.4 | **Pull Command** | S | Future |

**Effort:** 2-3 days
**Cost:** $0

### Phase 3: Minimal SaaS (V3 — Automation)
API for pattern sync. Aggregation and deduplication.

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F10.5 | **Sync API** | M | Future |
| F10.6 | **Team/Org Scopes** | M | Future |

**Effort:** 2-3 weeks
**Cost:** $20-50/month

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

## Research Artifacts

| Document | Purpose |
|----------|---------|
| `work/research/collective-intelligence-lineage/README.md` | Core insight and vision |
| `work/research/collective-intelligence-lineage/architecture-options.md` | Cost analysis and phases |

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

---

*Epic scope - update per phase completion*
*Created: 2026-02-02*
*Contributors: Emilio Osorio, Rai*
