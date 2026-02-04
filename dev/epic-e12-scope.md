# Epic E12: Complete Knowledge Graph

> **Status:** DESIGNED — Ready for /epic-plan
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
| F12.1 | **ADR Extractor** | M | Pending | Extract ADRs as `decision` nodes from `dev/decisions/` |
| F12.2 | **Guardrails Extractor** | S | Pending | Extract guardrails as queryable nodes |
| F12.3 | **Glossary Extractor** | S | Pending | Extract glossary terms for terminology |
| F12.4 | **Schema Extension** | XS | Pending | Add `decision`, `guardrail`, `term` to NodeType |
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

*Epic designed: 2026-02-03*
*ADR: ADR-020 (Proposed)*
*Next: /epic-plan for task breakdown*
