# Epic E12: Complete Knowledge Graph

> **Status:** PLANNED — Ready for implementation
> **Branch:** `epic/e12/complete-knowledge-graph`
> **Created:** 2026-02-03
> **Target:** Post-F&F (Feb 15+)
> **Depends on:** E11 (Unified Context Architecture)
> **ADR:** ADR-020 (Knowledge Graph Completion)
> **Research:** Session analysis (2026-02-03) — Memory recall assessment

---

## Objective

**Complete the knowledge graph** so that all feature cycle skills have MVC (Minimum Viable Context) through graph recall, and skills can write back learnings for continuous improvement.

**Value proposition:**
- /feature-design sees prior ADRs before making architecture decisions
- /feature-implement has guardrails surfaced contextually
- /feature-review can compare against calibration and persist patterns immediately
- Knowledge compounds — learnings during features aren't lost

---

## In Scope

**MUST:**
- ADR extraction into unified graph (40+ decisions)
- Guardrails extraction (code standards queryable)
- Skill query alignment (fix type mismatches)
- Memory write from /feature-review (bidirectional flow)

**SHOULD:**
- Glossary extraction (terminology alignment)
- Phase-specific MVC documentation per skill
- Domain hints for targeted queries

---

## Out of Scope (defer to parking lot)

- **Research output extraction** → Lower priority, complex format variance
- **Component catalog extraction** → Nice-to-have, not blocking MVC
- **Session-aware loading** → Optimization; re-querying is cheap (<1ms)
- **Embedding/vector search** → Future enhancement per ADR-019

---

## Features (10 SP estimated)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F12.1 | **ADR Extractor** | M | ✅ Done | Extract ADRs as `decision` nodes from `dev/decisions/` |
| F12.2 | **Guardrails Extractor** | S | ✅ Done | Extract guardrails as queryable nodes |
| F12.3 | **Glossary Extractor** | S | ✅ Done | Extract glossary terms for terminology |
| F12.4 | **Schema Extension** | XS | ✅ Done | Add `decision`, `guardrail`, `term` to NodeType |
| F12.5 | **Skill Query Alignment** | S | Pending | Fix query/type mismatches in feature cycle skills |
| F12.6 | **Memory Write CLI** | M | Pending | `raise memory add-pattern` command |

**Total:** 6 features, ~10 SP estimated

---

## Feature Details

### F12.1: ADR Extractor (M)

**Problem:** 40+ ADRs exist but /feature-design can't query them.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/adr.py`
- Extract: ID, title, status, decision summary, related ADRs
- Node type: `decision`
- Handle three formats:
  - Root level: `dev/decisions/adr-*.md` (YAML frontmatter)
  - v1: `dev/decisions/v1/adr-*.md` (older format)
  - v2: `dev/decisions/v2/adr-*.md` (sub-directory)

**Files:**
- `src/raise_cli/governance/parsers/adr.py` (new)
- `src/raise_cli/governance/extractor.py` (integrate)
- `tests/governance/parsers/test_adr.py` (new)

**Example output:**
```json
{
  "id": "ADR-019",
  "type": "decision",
  "content": "Unified Context Graph Architecture - Single unified NetworkX graph",
  "source_file": "dev/decisions/adr-019-unified-context-graph.md",
  "metadata": {
    "status": "accepted",
    "date": "2026-02-03",
    "related_to": ["ADR-011", "ADR-015"]
  }
}
```

---

### F12.2: Guardrails Extractor (S)

**Problem:** Guardrails are in CLAUDE.md but not queryable by topic.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/guardrails.py`
- Extract sections: Type Safety, Linting, Testing, Security, Documentation
- Node type: `guardrail`

**Files:**
- `src/raise_cli/governance/parsers/guardrails.py` (new)
- `src/raise_cli/governance/extractor.py` (integrate)
- `tests/governance/parsers/test_guardrails.py` (new)

**Source:** `governance/solution/guardrails.md`

---

### F12.3: Glossary Extractor (S)

**Problem:** Terminology in glossary but not surfaced in queries.

**Scope:**
- New parser: `src/raise_cli/governance/parsers/glossary.py`
- Extract: Term, definition, deprecated alternatives
- Node type: `term`

**Files:**
- `src/raise_cli/governance/parsers/glossary.py` (new)
- `src/raise_cli/governance/extractor.py` (integrate)
- `tests/governance/parsers/test_glossary.py` (new)

**Source:** `framework/reference/glossary.md`

---

### F12.4: Schema Extension (XS)

**Problem:** New node types not in schema.

**Scope:**
- Add `decision`, `guardrail`, `term` to `NodeType` literal
- Update `context/models.py`
- Update `governance/models.py` ConceptType enum

**Files:**
- `src/raise_cli/context/models.py`
- `src/raise_cli/governance/models.py`

---

### F12.5: Skill Query Alignment (S)

**Problem:** Skills query for types that don't exist.

**Current mismatches:**
| Skill | Current Query | Issue |
|-------|---------------|-------|
| /feature-design | `--types pattern,feature` | Needs `decision` |
| /feature-review | `--types pattern,session` | Needs `calibration` |

**Scope:**
- Audit all 9 skill queries
- Update type filters to match phase MVC
- Document MVC in each skill

**Files:** `.claude/skills/*/SKILL.md` (6 feature cycle skills)

**MVC per phase:**
| Phase | Types to Query |
|-------|----------------|
| design | decision, pattern |
| plan | calibration, pattern |
| implement | pattern, guardrail |
| review | calibration, pattern, session |

---

### F12.6: Memory Write CLI (M)

**Problem:** Patterns only persist via /session-close.

**Scope:**
- New command: `raise memory add-pattern`
- Add to patterns.jsonl immediately
- Deduplicate by content similarity
- Integrate into /feature-review

**Files:**
- `src/raise_cli/cli/commands/memory.py` (extend)
- `src/raise_cli/memory/patterns.py` (new or extend)
- `.claude/skills/feature-review/SKILL.md` (integrate)

**CLI signature:**
```bash
raise memory add-pattern "Pattern content" \
  --context testing,workflow \
  --learned-from F12.1
```

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] All 6 features complete (F12.1-F12.6)
- [ ] `raise context query "ADR" --unified --types decision` works
- [ ] `raise context query "testing" --unified --types guardrail` works
- [ ] `/feature-design` queries return ADR nodes
- [ ] `/feature-review` can persist patterns via CLI
- [ ] ADR-020 status updated to "Accepted"
- [ ] Epic merged to v2

---

## Dependencies

```
F12.4 (Schema Extension)
  ↓
F12.1 (ADR Extractor) ──┐
F12.2 (Guardrails)      ├─► F12.5 (Skill Query Alignment)
F12.3 (Glossary)    ────┘

F12.6 (Memory Write CLI) — Independent track
```

**External blockers:** None (E11 complete)

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Unified Graph | ADR-019 | Single graph, multiple node types |
| Knowledge Completion | ADR-020 | Extend with decision, guardrail, term |
| Concept-Level MVC | ADR-011 | 97% token savings via concept extraction |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| ADR format variance | Medium | Medium | Flexible parser with fallbacks |
| Guardrails structure changes | Low | Low | Section-based extraction resilient |
| Pattern deduplication complex | Medium | Low | Simple content hash first |
| Schema change breaks existing code | Low | High | Add types, don't remove |

---

## Notes

### Why Now (Post-F&F)

- E11 provides foundation (unified graph works)
- F&F release doesn't require complete MVC
- Post-F&F allows quality implementation
- Improves all future development velocity

### Parser Velocity

Per PAT-038: Second parser was 1.5x faster than first due to pattern familiarity. Expect:
- F12.1 (ADR): Normal velocity
- F12.2 (Guardrails): 1.3x
- F12.3 (Glossary): 1.5x

### Graph Growth

Current: 157 nodes
Expected after E12: ~220-250 nodes (40 ADRs + 10 guardrails + 30 terms)
Still well under 1K — no performance concerns.

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-03

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 1 | F12.4: Schema Extension | XS | None | M1 | Foundation — types must exist first |
| 2 | F12.1: ADR Extractor | M | F12.4 | M1 | Risk-first — highest uncertainty (format variance) |
| 3 | F12.2: Guardrails Extractor | S | F12.4 | M2 | Parallel with F12.3, leverages parser pattern |
| 3 | F12.3: Glossary Extractor | S | F12.4 | M2 | Parallel with F12.2, leverages parser pattern |
| 4 | F12.6: Memory Write CLI | M | None | M2 | Independent track, can start after M1 |
| 5 | F12.5: Skill Query Alignment | S | F12.1-F12.4 | M3 | Last — depends on all types existing |

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F12.4, F12.1 | Day 1-2 | `raise context query "ADR" --types decision` works | Query returns ADR-019, ADR-020 |
| **M2: Full Extraction** | +F12.2, F12.3, F12.6 | Day 3-4 | All governance types extractable, memory write works | Query guardrails, glossary; add pattern via CLI |
| **M3: Skills Aligned** | +F12.5 | Day 5 | All feature cycle skills use correct types | /feature-design finds ADRs |
| **M4: Epic Complete** | Integration | Day 6 | Done criteria met, ADR-020 accepted | Full demo, retrospective |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1 (Critical): F12.4 ─► F12.1 ──────────────► F12.5
                              ↓ enables
Stream 2 (Parallel):         F12.2 ───────────────► merge
                              ↓ parallel            ↑
Stream 3 (Parallel):         F12.3 ────────────────┘

Stream 4 (Independent):      F12.6 ─────────────────────────
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Merge points:**
- After F12.4: Split into parallel extractor streams
- Before F12.5: Merge all extractors, align skill queries
- F12.6 independent: Can start anytime after M1, no merge needed

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F12.4: Schema Extension | XS | ✅ Done | ~5 min | Fast | Added 3 types to both models |
| F12.1: ADR Extractor | M | ✅ Done | ~20 min | 2x | YAML frontmatter only (26 ADRs), fixed project NodeType |
| F12.2: Guardrails Extractor | S | ✅ Done | ~20 min | 1.5x | 20 guardrails, PAT-059 documented |
| F12.3: Glossary Extractor | S | ✅ Done | ~20 min | 1.75x | 59 terms, PAT-038 validated |
| F12.6: Memory Write CLI | M | Pending | - | - | |
| F12.5: Skill Query Alignment | S | Pending | - | - | |

**Milestone Progress:**
- [x] M1: Walking Skeleton (Day 1-2) — F12.4 + F12.1 complete, 19 ADR nodes in graph
- [ ] M2: Full Extraction (Day 3-4)
- [ ] M3: Skills Aligned (Day 5)
- [ ] M4: Epic Complete (Day 6)

### Sequencing Rationale

#### F12.4: Schema Extension (First)
- **Position:** First
- **Rationale:** All extractors need new types to exist; XS size means quick unblock
- **Dependencies:** None
- **Enables:** F12.1, F12.2, F12.3
- **Risk:** Low (additive change, no breaking)
- **Parallel:** No (blocking)

#### F12.1: ADR Extractor (Second)
- **Position:** Second (after F12.4)
- **Rationale:** Risk-first — format variance is highest uncertainty; most value (40+ nodes)
- **Dependencies:** F12.4
- **Enables:** F12.5
- **Risk:** Medium (three ADR formats to handle)
- **Parallel:** No (on critical path for M1)

#### F12.2 + F12.3: Guardrails + Glossary (Parallel)
- **Position:** Third (parallel after F12.1)
- **Rationale:** Lower risk; leverage parser pattern from F12.1; 1.3-1.5x velocity expected
- **Dependencies:** F12.4
- **Enables:** F12.5
- **Risk:** Low (single format each, familiar pattern)
- **Parallel:** Yes (with each other and F12.6)

#### F12.6: Memory Write CLI (Independent)
- **Position:** Flexible (start after M1)
- **Rationale:** Independent track; doesn't block extractors
- **Dependencies:** None (uses existing patterns.jsonl)
- **Enables:** /feature-review integration
- **Risk:** Medium (deduplication logic)
- **Parallel:** Yes (fully independent)

#### F12.5: Skill Query Alignment (Last)
- **Position:** Fifth (after all extractors)
- **Rationale:** Depends on all types existing; validates end-to-end flow
- **Dependencies:** F12.1, F12.2, F12.3, F12.4
- **Enables:** Epic complete
- **Risk:** Low (configuration changes only)
- **Parallel:** No (depends on all extractors)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| ADR v1 format harder than expected | Medium | Medium | Timebox to 2h; fallback to root+v2 only |
| Parallel extractors conflict on extractor.py | Low | Low | Clear integration points; feature branches |
| Memory write dedup blocks review | Medium | Low | Start simple (exact match); iterate |

### Velocity Assumptions

- **Baseline:** 2-3x multiplier with kata cycle (PAT-016)
- **Parser familiarity:** 1.3-1.5x for F12.2, F12.3 (PAT-038)
- **Schema extension:** Fast (XS = <30 min)
- **Buffer:** 20% for integration, polish

**Expected timeline:**
| Size | Estimate | With Buffer |
|:----:|:--------:|:-----------:|
| XS | 20-30 min | 30 min |
| S | 40-90 min | 1-1.5h |
| M | 1.5-3h | 2-4h |

**Total:** ~10 SP ≈ 8-12 hours ≈ 2-3 days focused work

---

*Epic planned: 2026-02-03*
*ADR: ADR-020 (Proposed)*
*Next: `/feature-design` for F12.4 (Schema Extension)*
