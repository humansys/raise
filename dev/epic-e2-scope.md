# Epic E2: Governance Toolkit - Scope

> **Status:** COMPLETE ✅
> Branch: `feature/e2/governance-toolkit`
> Created: 2026-01-31
> Completed: 2026-01-31
> Target: Feb 9, 2026 (Friends & Family pre-launch)

---

## Objective

Build the governance toolkit that enables concept-level graph representation of governance artifacts, providing 97% token savings for AI context queries via Minimum Viable Context (MVC) retrieval.

**Architecture:** Skills + CLI Toolkit (per ADR-011, ADR-012)
- **Skills** execute processes by reading markdown guides
- **CLI toolkit** provides deterministic data extraction and validation
- **Concept graph** enables semantic queries with massive token savings

---

## Features (9 SP)

| ID | Feature | SP | Status | Actual Time | Velocity |
|----|---------|:--:|:------:|:-----------:|:--------:|
| F2.1 | Concept Extraction | 3 | ✅ Complete | 52 min | 3.5x |
| F2.2 | Graph Builder | 2 | ✅ Complete | 65 min | 2.8x |
| F2.3 | MVC Query Engine | 2 | ✅ Complete | 90 min | 2.1x |
| F2.4 | CLI Commands | 2 | Merged into F2.1-F2.3 | - | - |

**Total:** 9 SP planned (85% reduction from original 60 SP)
**Delivered:** 7 SP actual (F2.4 merged into others - 100% functionality delivered)
**Completed:** 7 SP (100% of actual scope)
**Actual Velocity:** 2.7x average (207 min total)

---

## In Scope

**MUST:**
- Parse governance artifacts (PRD, Vision, Constitution) to extract concepts
- Build concept graph with relationships (requires, implements, validates, etc.)
- Serialize graph to JSON/YAML for persistence
- Graph traversal for MVC queries (breadth-first search)
- CLI commands: `raise graph extract`, `raise graph build`, `raise context query`
- Validation: `raise validate structure` checks governance structure
- Type safety: all code type-annotated
- Tests: >90% coverage on new code
- Quality: passes ruff, pyright, bandit

**SHOULD:**
- Graceful fallback to file-level context if graph unavailable
- Clear error messages when governance files missing/malformed
- Support for multiple governance artifact types (PRD, Vision, Constitution, Guardrails)

---

## Out of Scope (defer or deprecated)

**Deprecated (merged into E2 as skills):**
- ~~Gate Engine as separate engine~~ → Gates become validation skills
- ~~Kata Engine as separate engine~~ → Katas become process skills

**Deferred to later epics:**
- LinkML schema transpilation → Post-MVP (proved not needed)
- Full ontology support → Post-MVP (concept-level sufficient)
- Interactive graph visualization → Post-MVP
- Graph edit/merge operations → Post-MVP (read-only for now)
- SAR integration → E5
- Context generation → E4 (uses graph output)
- Observability/metrics → E6

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] **Docstrings on all public APIs** (Google-style)
- [ ] **Component catalog updated** (`dev/components.md`)
- [ ] **ADR created if architectural decision** (`dev/decisions/`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] All 4 features complete (F2.1-F2.4)
- [ ] Graph can extract 20+ concepts from raise-commons governance
- [ ] MVC query returns relevant concepts with <3% token usage vs full files
- [ ] CLI commands functional: `raise graph build`, `raise context query`
- [ ] **Skills created** for governance validation (e.g., `/validate-prd`)
- [ ] **Architecture guide updated** (`dev/architecture-overview.md`)
- [ ] Integration tests prove E2E workflow works
- [ ] **Framework docs synced** via `/framework-sync` if needed

---

## Dependencies

```
F2.1 (Concept Extraction)
  ↓
F2.2 (Graph Builder)
  ↓
F2.3 (MVC Query Engine)
  ↓
F2.4 (CLI Commands)
```

**Sequential:** Each feature builds on the previous one
**Blockers:** None (E1 foundation complete)

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Concept-level graph | ADR-011 | 97% token savings vs file-level |
| Skills + Toolkit | ADR-012 | 85% scope reduction vs engines |
| Validation spike | `dev/experiments/concept_extraction_spike.py` | 23 concepts extracted, proven feasible |
| Graph MVC spike | `dev/experiments/test_mvc.py` | BFS traversal, 19x more efficient |

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Token savings | >90% | MVC query vs full file comparison |
| Concept extraction | 20+ concepts | From raise-commons governance |
| Graph build time | <2 seconds | On raise-commons corpus |
| Query accuracy | >95% | Relevant concepts returned |
| Test coverage | >90% | Per feature + integration |

---

## Notes

### Why This Matters
- **Feb 9 deadline:** Need governance toolkit working for Friends & Family pre-launch
- **Unblocks E4:** Context generation needs graph output
- **Validates architecture:** Proves concept-level approach works at scale

### Key Risks
- Governance files may be inconsistent → Validation helps catch this
- Graph relationships complex → Start simple (5 relationship types max)
- MVC query tuning → Start with BFS, iterate if needed

### Experiment Validation
- ✅ Concept extraction: 23 concepts from 3 files (spike proven)
- ✅ Graph traversal: BFS with deque (spike proven)
- ✅ Token savings: 97% measured (architecture validation)
- ✅ Skills viability: ADR-012 approved

---

## Completion Summary

**Delivered:** 2026-01-31
**Duration:** 207 minutes (3.45 hours)
**Velocity:** 2.7x average (stabilizing at 2-3x)
**Tests:** 243 tests added (81 + 63 + 99)
**Coverage:** 95-100% across all modules
**Bugs:** 0 bugs found during development

**Scope Evolution:**
- F2.4 (CLI Commands) merged into F2.1-F2.3
- Each feature delivered its own CLI commands
- More efficient: avoided duplicate work
- Result: 7 SP delivered, 100% of planned functionality

**Key Achievements:**
- Concept extraction: 23 concepts from raise-commons governance
- Graph builder: BFS traversal with cycle detection
- MVC queries: 97% token savings validated
- CLI commands: `raise governance extract`, `raise graph build`, `raise graph validate`, `raise context query`

**Process Innovations:**
- Post-Retrospective Action Protocol SOP created
- `/epic-close` skill created (first use for this epic)
- SHOULD-CODE-002 guardrail added (Python naming best practices)

**Epic Retrospective:** `dev/epic-e2-retrospective.md`

---

*Epic tracking - update per feature completion*
*Epic complete: 2026-01-31*
