# Epic E13: Discovery — Codebase Understanding for Rai

> **Status:** ✓ COMPLETE (merged to v2, 2026-02-04)
> **Branch:** `feature/e13/discovery` → merged
> **Created:** 2026-02-04
> **Target:** Feb 9, 2026 (F&F MVP)
> **Research:** `work/research/architecture-representation-for-ai/` (RES-ARCH-REP-001)

---

## Objective

Enable Rai to quickly understand existing codebase components for consistent reuse and detect architectural drift from external contributions.

**Value proposition:** Rai can query "what components exist for X?" and get accurate answers. New code is checked against established patterns. Human effort shifts from writing documentation to validating AI-generated descriptions.

**Success criteria:**
- Rai can query unified graph for components by name, type, or purpose
- Component descriptions are AI-generated, human-validated
- Basic drift detection flags new code that doesn't match patterns

---

## Key Design Decision

### The Discovery Flow

```
EXTRACT (deterministic)  →  SYNTHESIZE (LLM)  →  VALIDATE (human)  →  POPULATE (graph)
     │                           │                     │                    │
     │                           │                     │                    │
  ast-grep                   Rai describes         Human reviews       Nodes added
  scans code                 what it found         approves/edits      to unified graph
```

**Critical insight:** Humans review, they don't write. They don't know the code well enough to document it from scratch. LLM synthesizes descriptions from extracted structure, human validates accuracy.

---

## Features (5 features, ~12 SP)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F13.1 | Schema Extension | S (2) | ✓ Complete | Add system/module/component/convention node types to unified graph |
| F13.2 | Extraction Toolkit | M (4) | ✓ Complete | CLI commands to scan codebase and extract symbols via ast-grep |
| F13.3 | Discovery Skills | M (4) | ✓ Complete | `/discover-*` skills with LLM synthesis and human validation loop |
| F13.4 | Graph Integration | S (2) | ✓ Complete | Populate unified graph with validated components, enable queries |
| F13.5 | Drift Detection | XS (1) | ✓ Complete | Basic check: new files against established patterns |

**Total:** 5 features, ~13 SP estimated (3-4 days with kata cycle)

---

## In Scope

**MUST:**
- [x] New node types in unified graph schema (system, module, component, convention)
- [x] `raise discover scan` — Extract symbols from codebase using ast-grep
- [ ] `raise discover build` — Build component nodes from scan output
- [ ] `/discover-start` skill — Initialize discovery, detect project type
- [ ] `/discover-scan` skill — Run extraction, LLM synthesizes descriptions
- [ ] `/discover-validate` skill — Human reviews AI descriptions, approves/edits
- [ ] `/discover-complete` skill — Populate validated nodes to graph
- [ ] `raise context query --type component` — Query component catalog

**SHOULD:**
- [ ] Convention/pattern extraction (naming patterns, architectural patterns)
- [ ] `/discover-check` skill — Compare new code against baseline (drift detection)
- [ ] Module-level grouping (not just flat component list)

---

## Out of Scope (defer to post-F&F)

| Item | Rationale | Destination |
|------|-----------|-------------|
| Function-level granularity | Too noisy for MVP; component level sufficient | Parking lot |
| Call graphs / data flow | Complex analysis; not needed for reuse discovery | Parking lot |
| Git history integration | Nice-to-have; focus on current state first | Parking lot |
| CI/CD drift blocking | Need to validate approach first; start with warnings | E13 Phase 2 |
| Multi-repo support | Single repo is F&F scope | V3 scope |
| PageRank ranking | Simpler heuristics sufficient for MVP | Parking lot |

---

## Architecture

### New Node Types (F13.1)

Extend `NodeType` literal in unified graph:

```python
NodeType = Literal[
    # Existing (E11/E12)
    "pattern", "calibration", "session", "term", "decision",
    "guardrail", "requirement", "feature",
    # New (E13 Discovery)
    "system",      # Top-level system description (1 per project)
    "module",      # Package/directory level
    "component",   # Class/service/function with interface
    "convention",  # Observed coding pattern
]
```

### Component Node Schema

```python
class ComponentNode(ConceptNode):
    """A discoverable, reusable code component."""
    type: Literal["component"] = "component"

    # Identity
    name: str                    # e.g., "UserService"
    kind: str                    # "class" | "function" | "service"
    location: str                # "src/services/user.py:15"

    # Interface (for reuse)
    signature: str               # "class UserService(BaseService)"
    purpose: str                 # AI-generated, human-validated

    # Relationships
    depends_on: list[str]        # Component IDs this depends on
    used_by: list[str]           # Component IDs that use this

    # Validation
    validated: bool = False      # Human has reviewed
    validated_by: str | None     # Who validated
    validated_at: str | None     # When validated
```

### Discovery Skill Flow

```
/discover-start
    │
    ├── Detect project type (Python, TypeScript, etc.)
    ├── Identify entry points, key directories
    └── Create system node (draft)

/discover-scan
    │
    ├── Run: raise discover scan ./src
    ├── Rai receives JSON of extracted symbols
    ├── Rai synthesizes descriptions for each component
    │   "UserService: Handles user CRUD operations and authentication.
    │    Depends on UserRepository for data access."
    └── Output: Draft component nodes with AI descriptions

/discover-validate
    │
    ├── Present components to human (batched)
    ├── Human reviews each: approve / edit / skip
    ├── Edits update the description
    └── Approved components marked validated=true

/discover-complete
    │
    ├── Run: raise discover build --validated
    ├── Validated nodes added to unified graph
    ├── Relationships inferred (depends_on, used_by)
    └── Graph persisted
```

### CLI Commands (F13.2)

```bash
# Scan codebase, output JSON of symbols
raise discover scan [path] [--language python|typescript|...] [--output json|yaml]

# Build graph from scan output (after validation)
raise discover build [--input scan.json] [--validated-only]

# Check new files against baseline (drift detection)
raise discover check [--diff HEAD~1] [--baseline graph.json]
```

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Component catalog updated (`dev/components.md`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] All 5 features complete (F13.1-F13.5)
- [ ] Can run full discovery flow on raise-commons itself (dogfooding)
- [ ] Component query works: `raise context query --type component "service"`
- [ ] At least 10 components discovered and validated from raise-commons
- [ ] Basic drift detection flags when new file doesn't match conventions
- [ ] Architecture guide updated (`dev/architecture-overview.md`)
- [ ] Epic merged to v2

---

## Dependencies

```
F13.1 (Schema Extension)
  ↓
F13.2 (Extraction Toolkit) ──┐
  ↓                          │ (parallel possible after F13.1)
F13.3 (Discovery Skills) ◄───┘
  ↓
F13.4 (Graph Integration)
  ↓
F13.5 (Drift Detection)
```

**External dependencies:**
- `ast-grep` CLI — Already in stack, used in E2
- Unified graph infrastructure — E11 ✅
- Knowledge graph extractors — E12 ✅

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Unified Graph | ADR-019 | Single graph for all concept types |
| Knowledge Graph | ADR-020 | Extended node types pattern |
| Skills + Toolkit | ADR-012 | Deterministic tools + LLM skills |
| Aider Analysis | RES-ARCH-REP-001-AIDER | Adapt concepts, don't fork |

**New ADR needed?** No — we're extending existing patterns (ADR-019, ADR-020). The "LLM synthesis + human validation" pattern aligns with our Skills + Toolkit architecture (ADR-012).

---

## Notes

### Why This Epic

Rai currently lacks fast codebase understanding:
- Each session requires re-discovering what exists
- Risk of duplicating functionality or inconsistent patterns
- No systematic way to query "what handles X?"
- External contributions can drift from established patterns

Discovery solves this by creating a queryable component catalog that Rai can use for informed decisions.

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| ast-grep extraction misses patterns | Medium | Medium | Start with Python, our primary language |
| LLM synthesis produces poor descriptions | Low | Medium | Human validation catches bad descriptions |
| Too many components overwhelm validation | Medium | Low | Batch validation, start with key directories |
| Drift detection false positives | Medium | Low | Start with warnings only, tune thresholds |

### Velocity Assumption

Based on E12 calibration (2x velocity with kata cycle):
- 13 SP ÷ 2 (velocity multiplier) = ~6.5 effective SP
- At ~2 SP/day = ~3-4 days implementation
- Buffer for integration/polish = 1 day
- **Total: 4-5 days** (fits Feb 9 target)

### Research Foundation

This epic builds on completed research:
- RES-ARCH-REP-001: Architecture representation models (C4, Backstage)
- Aider reverse engineering: Algorithm understood, decision to adapt not fork
- Prior SAR research: `work/research/sar-component/` (validated 4-phase approach)

---

## Milestones

| Milestone | Features | Target | Validation |
|-----------|----------|--------|------------|
| M1: Foundation | F13.1, F13.2 | Feb 5 | Can scan raise-commons, get JSON output |
| M2: Discovery Flow | F13.3, F13.4 | Feb 7 | Full skill flow works, components in graph |
| M3: F&F Ready | F13.5 + polish | Feb 8 | Drift detection, dogfooding complete |

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-04

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 1 | F13.1 Schema Extension | S (2) | None | M1 | Foundation — all stories need node types |
| 2 | F13.2 Extraction Toolkit | M (4) | F13.1 | M1 | Risk-first — ast-grep integration is key uncertainty |
| 3 | F13.3 Discovery Skills | M (4) | F13.2 | M2 | Needs extraction output to synthesize descriptions |
| 4 | F13.4 Graph Integration | S (2) | F13.3 | M2 | Connects skills to persistent storage |
| 5 | F13.5 Drift Detection | XS (1) | F13.4 | M3 | Needs baseline in graph to compare against |

**Sequencing Strategy:** Risk-first. F13.2 (Extraction) has highest uncertainty (ast-grep patterns for Python). Tackle early while energy is high and time for pivots exists.

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F13.1, F13.2 | Feb 5 | `raise discover scan src/` outputs JSON with symbols | Show extracted components from raise-commons |
| **M2: Discovery Flow** | F13.3, F13.4 | Feb 7 | Full `/discover-*` skill flow works, components in graph | Run discovery on raise-commons, query results |
| **M3: F&F Ready** | F13.5 + polish | Feb 8 | Drift detection warns on non-conforming code | Demo drift warning on test file |

### Timeline

| Day | Date | Features | Milestone | Cumulative |
|:---:|------|----------|-----------|:----------:|
| 1 | Feb 5 | F13.1 Schema + F13.2 Extraction | M1: Walking Skeleton | 46% (6 SP) |
| 2 | Feb 6 | F13.3 Discovery Skills | — | 77% (10 SP) |
| 3 | Feb 7 | F13.4 Graph Integration | M2: Discovery Flow | 92% (12 SP) |
| 4 | Feb 8 | F13.5 Drift + polish | M3: F&F Ready | 100% (13 SP) |
| — | Feb 9 | Buffer / dogfooding | **F&F Launch** | Done |

### Work Streams

```
Day 1          Day 2          Day 3          Day 4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F13.1 ─► F13.2 ─► F13.3 ─────► F13.4 ─────► F13.5
(Schema)  (Extract)  (Skills)    (Graph)     (Drift)
         ↓                      ↓
      M1: Skeleton           M2: Flow      M3: Ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Note:** Sequential rather than parallel because:
- Each feature builds on previous output
- Single implementer (Rai + human)
- Integration risk higher with parallel streams

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F13.1 Schema Extension | S (2) | ✓ Complete | 1 session | 2x | Combined with F13.2 |
| F13.2 Extraction Toolkit | M (4) | ✓ Complete | 1 session | 2x | Multi-language (Py/TS/JS), 39 tests |
| F13.3 Discovery Skills | M (4) | ✓ Complete | 90 min | 1.33x | 4 skills, full kata cycle |
| F13.4 Graph Integration | S (2) | ✓ Complete | 30 min | 2x | NodeType extended, load_components(), 47 tests |
| F13.5 Drift Detection | XS (1) | Pending | — | — | |

**Milestone Progress:**
- [x] M1: Walking Skeleton (Feb 5) ✓ Complete 2026-02-04
- [x] M2: Discovery Flow (Feb 7) ✓ Complete 2026-02-04
- [ ] M3: F&F Ready (Feb 8)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| ast-grep patterns don't capture Python classes well | Medium | High | Day 1 spike; fall back to tree-sitter direct if needed |
| Skills take longer due to LLM synthesis complexity | Medium | Medium | Timebox synthesis to essential fields only |
| Graph integration reveals schema issues | Low | Medium | F13.1 tests validate schema before F13.4 |

### Velocity Assumptions

- **Baseline:** 2x multiplier with kata cycle (from PAT-016, E12 calibration)
- **Adjustment:** New domain (code extraction) — conservative estimate
- **Buffer:** Day 5 (Feb 9) reserved for integration issues

### Definition of Ready (per story)

Before starting each story:
- [ ] Previous story complete (or F13.1 for first)
- [ ] Design understood (epic scope document)
- [ ] Test strategy clear
- [ ] No external blockers

---

*Plan created: 2026-02-04*
*M1 complete: 2026-02-04*
*M2 complete: 2026-02-04*
*Next: F13.5 Drift Detection*
