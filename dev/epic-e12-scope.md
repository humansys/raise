# Epic E12: Complete Knowledge Graph

> **Status:** DRAFT — Needs /epic-design and /epic-plan
> **Branch:** TBD
> **Created:** 2026-02-03
> **Target:** Post-F&F (Feb 15+)
> **Depends on:** E11 (Unified Context Architecture)
> **Research:** Session analysis (2026-02-03) — Memory recall assessment

---

## Problem Statement

The unified context graph (E11) provides infrastructure but is incomplete. **Skills query for context they cannot find:**

| Skill | Queries For | Available Types | Gap |
|-------|-------------|-----------------|-----|
| /feature-design | "architecture patterns ADR" | pattern, feature, skill | **ADRs missing** |
| /feature-implement | "codebase testing patterns" | pattern | Guardrails not queryable |
| /feature-review | "retrospective patterns" | pattern, session | Calibration not queried |

**Current graph inventory (157 nodes):**
- pattern: 52
- feature: 47
- session: 25
- calibration: 12
- epic: 11
- skill: 10

**Missing governance data (40+ files):**
- ADRs: 40+ architectural decisions in `dev/decisions/`
- Guardrails: Code standards in `governance/solution/guardrails.md`
- Glossary: Terminology in `framework/reference/glossary.md`
- Research: 5+ research outputs in `work/research/`
- Components: Catalog in `dev/components.md`

**Additionally:** Skills only **read** from graph — none **write** to memory. Pattern extraction only happens in `/session-close`.

---

## Objective

**Complete the knowledge graph** so that all feature cycle skills have MVC (Minimum Viable Context) through graph recall, and skills can write back learnings for continuous improvement.

**Value proposition:**
- /feature-design sees prior ADRs before making architecture decisions
- /feature-implement has guardrails surfaced contextually
- /feature-review can compare against calibration data
- Patterns learned during features are persisted immediately

---

## Success Criteria

1. **All governance sources extracted** — ADRs, guardrails, glossary in graph
2. **Skill queries match available types** — No query/type mismatches
3. **Skills have phase-appropriate MVC** — Each phase gets right context
4. **Bidirectional memory flow** — Skills can read AND write patterns
5. **Zero redundant queries** — Session-aware context loading

---

## Architecture Extension

Building on ADR-019 (Unified Context Graph):

```
┌──────────────────────────────────────────────────────────────┐
│                    Unified Context Graph                      │
│                    (.raise/graph/unified.json)                │
│                                                               │
│  EXISTING:                                                    │
│  - patterns, calibration, sessions (memory)                   │
│  - principles, requirements, outcomes (governance)            │
│  - epics, features (work)                                     │
│  - skills (process)                                           │
│                                                               │
│  NEW (E12):                                                   │
│  + decisions (ADRs)          ← /feature-design               │
│  + guardrails                ← /feature-implement            │
│  + terms (glossary)          ← terminology alignment         │
│  + research                  ← prior findings                │
│  + components                ← codebase structure            │
└──────────────────────────────────────────────────────────────┘
```

---

## Features (Draft)

| ID | Feature | Size | Priority | Description |
|----|---------|:----:|:--------:|-------------|
| F12.1 | **ADR Extractor** | M | P0 | Extract ADRs into graph as `decision` nodes |
| F12.2 | **Guardrails Extractor** | S | P1 | Extract guardrails as queryable nodes |
| F12.3 | **Glossary Extractor** | S | P2 | Extract glossary terms for terminology |
| F12.4 | **Skill Query Alignment** | S | P0 | Fix query/type mismatches in all skills |
| F12.5 | **Phase-Specific MVC** | M | P1 | Define and implement MVC per skill phase |
| F12.6 | **Memory Write from Skills** | M | P1 | Enable pattern persistence from /feature-review |
| F12.7 | **Session-Aware Loading** | S | P2 | Skip redundant queries in same session |

**Estimated:** 7 features, ~12-15 SP

---

## Feature Details (Draft)

### F12.1: ADR Extractor

**Problem:** 40+ ADRs exist but /feature-design can't query them.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/adr.py`
- Extract: ID, title, status, context, decision, consequences
- Node type: `decision`
- Handle v1, v2, and root-level ADRs

**Source files:**
- `dev/decisions/adr-*.md` (root)
- `dev/decisions/v1/adr-*.md`
- `dev/decisions/v2/adr-*.md`

**Example extraction:**
```json
{
  "id": "ADR-019",
  "type": "decision",
  "content": "Unified Context Graph Architecture - Single unified NetworkX graph with multiple node types",
  "source_file": "dev/decisions/adr-019-unified-context-graph.md",
  "metadata": {
    "status": "accepted",
    "context": ["E11", "memory", "governance", "graph"],
    "consequences": ["single query interface", "cross-domain relationships"]
  }
}
```

---

### F12.2: Guardrails Extractor

**Problem:** Guardrails are in CLAUDE.md but not queryable by topic.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/guardrails.py`
- Extract sections: Type Safety, Linting, Testing, Security, Documentation
- Node type: `guardrail`
- Enable queries like "testing guardrails" → specific rules

**Source:** `governance/solution/guardrails.md`

---

### F12.3: Glossary Extractor

**Problem:** Terminology in glossary but not surfaced in queries.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/glossary.py`
- Extract: Term, definition, deprecated alternatives
- Node type: `term`
- Enable terminology alignment

**Source:** `framework/reference/glossary.md`

---

### F12.4: Skill Query Alignment

**Problem:** Skills query for types that don't exist.

**Current mismatches:**
| Skill | Query | Types Filter | Issue |
|-------|-------|--------------|-------|
| /feature-design | "ADR" | pattern, feature | ADRs aren't patterns |
| /feature-review | "retrospective" | pattern, session | Retros are in progress.md |

**Scope:**
- Audit all skill queries
- Match query terms to available types
- Add `--types decision,pattern` for design
- Add `--types calibration,pattern` for review

**Files:** `.claude/skills/*/SKILL.md` (9 skills)

---

### F12.5: Phase-Specific MVC

**Problem:** Generic queries waste tokens; phases need different context.

**MVC Definition per phase:**

| Phase | Must Have | Nice to Have | Don't Load |
|-------|-----------|--------------|------------|
| **design** | decisions (ADRs), patterns | similar features | calibration, sessions |
| **plan** | calibration, estimation patterns | prior plans | architecture |
| **implement** | codebase patterns, guardrails | similar implementations | calibration |
| **review** | calibration (comparison), patterns | sessions | architecture |

**Scope:**
- Document MVC per skill in skill files
- Tune queries to match MVC
- Add domain hints (optional)

---

### F12.6: Memory Write from Skills

**Problem:** Patterns only extracted in /session-close; learnings during features lost.

**Current flow:**
```
/feature-review → retrospective.md → /session-close → patterns.jsonl
```

**Proposed flow:**
```
/feature-review → patterns.jsonl (immediate) + retrospective.md
```

**Scope:**
- Add `raise memory add-pattern` CLI command
- Integrate into /feature-review Step 4 (Update Framework)
- Emit pattern immediately when identified
- Deduplicate with existing patterns

---

### F12.7: Session-Aware Loading

**Problem:** If design→plan→implement runs in one session, each re-queries.

**Scope:**
- Track queries made in session (via telemetry or state)
- Skip redundant queries
- Or: Accept re-querying is cheap (graph query <1ms)

**Decision needed:** Is this worth the complexity?

---

## Dependencies

```
E11 (Unified Context) ← E12 (Complete Knowledge Graph)
     └── context/ module
     └── UnifiedGraphBuilder
     └── raise context query --unified
```

**Internal dependencies:**
- F12.1-F12.3 (extractors) → F12.4 (query alignment)
- F12.4 → F12.5 (MVC definition)
- F12.6 is independent (memory write)
- F12.7 can be deferred (optimization)

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADR format varies (v1 vs v2) | Extraction fails | Flexible parser with fallbacks |
| Over-engineering MVC | Complexity without value | Start simple, iterate |
| Memory write conflicts | Duplicate patterns | Deduplication logic |
| Graph grows too large | Query performance | Monitor, optimize if needed |

---

## Open Questions

1. **Research outputs** — Should `work/research/*/` be extracted? (Lower priority)
2. **Components catalog** — Should `dev/components.md` be extracted? (Nice to have)
3. **Session-aware loading** — Worth the complexity or just accept re-querying?
4. **Memory write trigger** — Automatic or explicit user approval?

---

## Milestones (Draft)

**M1: Core Extractors (F12.1, F12.2, F12.4)**
- ADR extraction working
- Guardrails extraction working
- Skill queries aligned
- /feature-design can find ADRs

**M2: Complete MVC (F12.3, F12.5, F12.6)**
- Glossary extraction
- Phase-specific queries tuned
- Memory write from /feature-review
- Bidirectional knowledge flow

**M3: Optimization (F12.7)**
- Session-aware loading (if needed)
- Performance tuning

---

## Validation

- [ ] `raise graph build --unified` includes decisions, guardrails, terms
- [ ] `raise context query "ADR architecture"` returns ADR nodes
- [ ] /feature-design queries return relevant ADRs
- [ ] /feature-review can persist patterns immediately
- [ ] All skill queries return expected types

---

## References

- **ADR-019:** Unified Context Graph Architecture
- **E11:** Unified Context Architecture (foundation)
- **Session analysis:** Memory recall assessment (2026-02-03)
- **Parking lot:** Framework improvements section

---

*Epic draft created: 2026-02-03*
*Status: Needs /epic-design for research + architecture decisions*
*Status: Needs /epic-plan for task breakdown*
