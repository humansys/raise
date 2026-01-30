# RaiSE Documentation Corpus Audit for v2.3 Migration

**Date:** 2026-01-29
**Auditor:** RaiSE Ontology Architect
**Scope:** All files in `docs/` directory
**Reference:** ADR-008 (Kata/Skill/Context Simplification)

---

## Executive Summary

### Key Findings

1. **Ontological Misalignment:** The `docs/` directory contains documentation from v2.0-v2.1 that uses the **deprecated 4-level kata hierarchy** (principios/flujo/patron/tecnica). ADR-008 eliminates this in favor of **Work Cycles** (project/feature/setup/improve).

2. **Duplication with `.raise/`:** There is significant overlap between `docs/` and `.raise/` directories:
   - Gates duplicated (different content/quality)
   - Templates partially duplicated
   - Katas organized differently

3. **Golden Data vs Reference:** The `docs/core/` directory contains updated v2.3-aligned content (especially `glossary.md`), while `docs/corpus/` contains v1.0 content from December 2025 that is largely outdated.

4. **SAR/CTX Terminology:** Multiple files still reference deprecated "SAR Component" and "CTX Component" terminology (eliminated in v2.2).

5. **Reference Docs Value:** `docs/reference/` contains valuable architectural content that should be migrated but needs terminology updates.

### Recommendation

**Consolidate documentation into `.raise/` as the single source of truth.** Archive `docs/` as historical reference. The new structure should follow the v2.3 ontology:

```
.raise/
├── context/     # Context layer (constitution, patterns, rules, golden data)
├── katas/       # Kata layer (organized by Work Cycle)
│   ├── project/
│   ├── feature/
│   ├── setup/
│   └── improve/
├── skills/      # Skill layer (atomic operations)
├── gates/       # Validation Gates
└── templates/   # Artifact scaffolds
```

---

## 1. Corpus Analysis (`docs/corpus/`)

### Assessment Summary

| File | Purpose | Assessment | Deprecated Terms |
|------|---------|------------|------------------|
| `00-constitution.md` | RaiSE principles | **DEPRECATED** | Outdated vs `docs/core/constitution.md` |
| `01-product-vision.md` | Product vision doc | **ARCHIVE ONLY** | None critical |
| `02-business-model.md` | Business model | **ARCHIVE ONLY** | None |
| `03-market-context.md` | Market analysis | **ARCHIVE ONLY** | None |
| `04-stakeholder-map.md` | Stakeholder analysis | **ARCHIVE ONLY** | None |
| `05-learning-philosophy.md` | Heutagogy philosophy | **UPDATE NEEDED** | References L0-L3 levels |
| `10-system-architecture.md` | System architecture | **UPDATE NEEDED** | References old command structure |
| `11-data-architecture.md` | Data architecture | **UPDATE NEEDED** | References SAR/CTX |
| `12-integration-patterns.md` | Integration patterns | **UPDATE NEEDED** | References old components |
| `13-security-compliance.md` | Security/compliance | **CARRY FORWARD** (P2) | Minor updates needed |
| `14-adr-index.md` | ADR index | **DEPRECATED** | Not synchronized with actual ADRs |
| `15-tech-stack.md` | Tech stack decisions | **UPDATE NEEDED** | References old structure |
| `20-glossary.md` | Terminology | **DEPRECATED** | Superseded by `docs/core/glossary.md` v2.3 |
| `21-methodology.md` | Methodology overview | **UPDATE NEEDED** | References kata levels, old structure |
| `22-templates-catalog.md` | Template catalog | **UPDATE NEEDED** | References SAR templates, old paths |
| `23-commands-reference.md` | Commands reference | **DEPRECATED** | Commands replaced by Katas/Skills in v2.3 |
| `24-examples-library.md` | Usage examples | **UPDATE NEEDED** | Uses old command syntax |
| `30-roadmap.md` | Project roadmap | **ARCHIVE ONLY** | Historical, dates passed |
| `31-current-state.md` | Project state | **ARCHIVE ONLY** | Historical snapshot |
| `32-session-log.md` | Session log | **ARCHIVE ONLY** | Historical |
| `33-issues-decisions.md` | Issues/decisions | **ARCHIVE ONLY** | Historical |
| `34-dependencies-blockers.md` | Dependencies | **ARCHIVE ONLY** | Historical |

### Detailed File Assessments

#### Layer 0: Foundation

**`00-constitution.md`** - **DEPRECATED**
- Purpose: RaiSE founding principles (8 principles)
- Issue: v2.0.0 from Dec 2025, superseded by `docs/core/constitution.md`
- Action: Archive, use `docs/core/constitution.md` as source of truth

#### Layer 1: Vision (01-04)

**`01-product-vision.md`** - **ARCHIVE ONLY**
- Purpose: Product vision, value proposition, differentiators
- Value: Historical context of product decisions
- Action: Archive as historical reference

**`02-business-model.md`** - **ARCHIVE ONLY**
- Purpose: Business model (freemium, enterprise tiers)
- Value: Historical business planning
- Action: Archive

**`03-market-context.md`** - **ARCHIVE ONLY**
- Purpose: Market analysis, competitors, trends
- Value: Historical market analysis
- Action: Archive

**`04-stakeholder-map.md`** - **ARCHIVE ONLY**
- Purpose: Stakeholder identification
- Value: Historical stakeholder analysis
- Action: Archive

#### Layer 2: Philosophy (05)

**`05-learning-philosophy.md`** - **UPDATE NEEDED** (P2)
- Purpose: Deep dive on Heutagogy, Jidoka, Kaizen principles
- Value: Rich philosophical content, unique to RaiSE
- Issues: References L0-L3 kata levels (deprecated)
- Action: Migrate to `.raise/context/philosophy/`, update terminology

#### Layer 3: Architecture (10-15)

**`10-system-architecture.md`** - **UPDATE NEEDED** (P2)
- Purpose: System architecture overview
- Issues: References old command categories, SAR/CTX components
- Action: Update terminology, migrate to `.raise/context/architecture/`

**`11-data-architecture.md`** - **UPDATE NEEDED** (P3)
- Purpose: Data models, storage patterns
- Issues: References SAR data models
- Action: Update for Context/Kata/Skill model

**`12-integration-patterns.md`** - **UPDATE NEEDED** (P2)
- Purpose: MCP integration, agent patterns
- Issues: References old component names
- Action: Update for v2.3 ontology

**`13-security-compliance.md`** - **CARRY FORWARD** (P2)
- Purpose: Security considerations, EU AI Act compliance
- Value: Valuable compliance content
- Action: Minor terminology updates, migrate to `.raise/context/compliance/`

**`14-adr-index.md`** - **DEPRECATED**
- Purpose: Index of ADRs
- Issue: Not synchronized with actual ADRs in `specs/raise/adrs/`
- Action: Generate dynamically or maintain in ADR directory

**`15-tech-stack.md`** - **UPDATE NEEDED** (P3)
- Purpose: Technology decisions
- Issues: References old structure
- Action: Update for current tooling

#### Layer 4: Domain (20-24)

**`20-glossary.md`** - **DEPRECATED**
- Purpose: Canonical terminology
- Issue: Completely superseded by `docs/core/glossary.md` v2.3.0
- Action: Delete, use `docs/core/glossary.md`

**`21-methodology.md`** - **UPDATE NEEDED** (P1)
- Purpose: RaiSE methodology flow
- Issues: Uses kata levels (principios/flujo/patron/tecnica), old structure
- Action: Rewrite for Work Cycles, migrate to `.raise/context/methodology.md`

**`22-templates-catalog.md`** - **UPDATE NEEDED** (P2)
- Purpose: Template documentation
- Issues: References SAR templates, old paths
- Action: Update paths, remove SAR section

**`23-commands-reference.md`** - **DEPRECATED**
- Purpose: CLI and slash commands reference
- Issue: "Commands" concept replaced by Katas/Skills in ADR-008
- Action: Replace with Katas index and Skills reference

**`24-examples-library.md`** - **UPDATE NEEDED** (P2)
- Purpose: Practical usage examples
- Value: Good pedagogical content
- Issues: Uses old command syntax
- Action: Update examples for v2.3 workflow

#### Layer 5: Execution (30-34)

**`30-roadmap.md`** - **ARCHIVE ONLY**
- Purpose: Development roadmap
- Issue: Dates from Q1-Q4 2025, historical
- Action: Archive

**`31-current-state.md`** - **ARCHIVE ONLY**
- Purpose: Project state snapshot
- Issue: From Dec 2025, outdated
- Action: Archive

**`32-session-log.md`** - **ARCHIVE ONLY**
- Purpose: Work session log
- Value: Historical work tracking
- Action: Archive

**`33-issues-decisions.md`** - **ARCHIVE ONLY**
- Purpose: Open issues and decisions
- Issue: Historical snapshot
- Action: Archive

**`34-dependencies-blockers.md`** - **ARCHIVE ONLY**
- Purpose: Dependencies and blockers
- Issue: Historical snapshot
- Action: Archive

---

## 2. Templates Analysis (`docs/templates/`)

### Current Structure

```
docs/templates/
├── backlog/      (user_story.md, etc.)
├── cursor-rules/ (rule templates)
├── sar/          (SAR templates - DEPRECATED)
├── solution/     (PRD, vision templates)
└── tech/         (tech design templates)
```

### Comparison with `.raise/templates/`

```
.raise/templates/
├── architecture/
├── backlog/
├── solution/
└── tech/
```

### Assessment

| Directory | docs/templates/ | .raise/templates/ | Assessment |
|-----------|-----------------|-------------------|------------|
| backlog/ | Present | Present | **DUPLICATE** - consolidate to .raise |
| solution/ | Present | Present | **DUPLICATE** - consolidate to .raise |
| tech/ | Present | Present | **DUPLICATE** - consolidate to .raise |
| cursor-rules/ | Present | Not present | **UPDATE NEEDED** - move to .raise/context/rules/ |
| sar/ | Present | Not present | **DEPRECATED** - SAR terminology eliminated |
| architecture/ | Not present | Present | .raise has additional content |

### Recommendation

1. **Delete `docs/templates/sar/`** - SAR terminology deprecated
2. **Consolidate to `.raise/templates/`** - single source of truth
3. **Move cursor-rules to `.raise/context/rules/`** - aligns with Context layer

---

## 3. Reference Docs Analysis (`docs/reference/`)

### Files Assessment

| File | Purpose | Assessment | Conflicts with ADR-008? |
|------|---------|------------|------------------------|
| `architecture.md` | Architecture overview | **UPDATE NEEDED** (P2) | Yes - old component model |
| `commands-reference.md` | Commands documentation | **DEPRECATED** | Yes - Commands replaced |
| `data-architecture.md` | Data models | **UPDATE NEEDED** (P3) | Yes - SAR/CTX data |
| `examples-library.md` | Usage examples | **UPDATE NEEDED** (P2) | Yes - old syntax |
| `integration-patterns.md` | Integration docs | **UPDATE NEEDED** (P2) | Partial |
| `kata-schema.md` | Kata structure | **UPDATE NEEDED** (P1) | Yes - uses kata levels |
| `learning-philosophy.md` | Philosophy deep-dive | **CARRY FORWARD** (P1) | Minor - valuable content |
| `product-vision.md` | Product vision | **ARCHIVE ONLY** | No |
| `security-compliance.md` | Security/compliance | **CARRY FORWARD** (P2) | No |
| `tech-stack.md` | Technology decisions | **UPDATE NEEDED** (P3) | Minor |
| `templates-catalog.md` | Template docs | **UPDATE NEEDED** (P2) | Yes - SAR references |
| `work-cycles.md` | Work cycles definition | **CARRY FORWARD** (P1) | Partial alignment |

### High-Value Content to Preserve

1. **`learning-philosophy.md`** (43KB) - Richest philosophical content, unique differentiator
2. **`work-cycles.md`** - Already aligned with v2.3 Work Cycle concept
3. **`security-compliance.md`** - Compliance documentation valuable
4. **`kata-schema.md`** - Structure valid, terminology needs update

---

## 4. Gates Analysis (`docs/gates/`)

### Comparison

| Gate | docs/gates/ | .raise/gates/ | Assessment |
|------|-------------|---------------|------------|
| gate-backlog.md | Present (2637B) | Present (2637B) | **DUPLICATE** - identical |
| gate-code.md | Present (4173B) | Not present | **UNIQUE** - migrate to .raise |
| gate-design.md | Present (5737B) | Present (5737B) | **DUPLICATE** - identical |
| gate-discovery.md | Present (3947B) | Present (1224B) | **CONFLICT** - different content |
| gate-plan.md | Present (2520B) | Not present | **UNIQUE** - migrate to .raise |
| gate-vision.md | Present (4418B) | Present (1517B) | **CONFLICT** - different content |
| gate-architecture.md | Not present | Present (1659B) | .raise has additional |
| gate-estimation.md | Not present | Present (5896B) | .raise has additional |

### Conflicts Found

1. **gate-discovery.md**: `docs/gates/` has richer content (3947B vs 1224B)
   - docs version: Full validation criteria with Jidoka inline
   - .raise version: Simplified checklist format

2. **gate-vision.md**: `docs/gates/` has richer content (4418B vs 1517B)
   - docs version: Full validation with process
   - .raise version: Simplified checklist

### Recommendation

- **Merge docs/gates/ content into .raise/gates/** using the richer docs/ versions as base
- **Standardize format** to the `.raise/gates/` checklist style but preserve criteria from docs/

---

## 5. Katas Analysis (`docs/katas/`)

### Current Structure

```
docs/katas/
├── README.md
├── principles/     # Meta-level katas
├── flow/           # Flow katas by phase
├── patterns/       # Reusable patterns
└── techniques/     # (empty/future)
```

### Comparison with `.raise/katas/`

```
.raise/katas/
├── README.md
├── project/        # Project cycle katas
├── feature/        # Feature cycle katas
├── setup/          # Setup cycle katas
└── improve/        # Improvement cycle katas
```

### Assessment

| Aspect | docs/katas/ | .raise/katas/ | v2.3 Alignment |
|--------|-------------|---------------|----------------|
| Organization | By abstraction level | By Work Cycle | .raise is v2.3 aligned |
| Naming | principios/flujo/patron/tecnica | project/feature/setup/improve | .raise uses correct v2.3 terms |
| README | References kata levels | References Work Cycles | .raise aligned |

### Content Migration Mapping

| docs/katas/ Location | Content | Migrate To |
|---------------------|---------|------------|
| principles/meta-kata.md | What is a kata | .raise/katas/README.md |
| principles/execution-protocol.md | 7 execution steps | .raise/context/methodology.md |
| flow/discovery.md | Discovery process | .raise/katas/project/discovery.md |
| flow/solution-vision.md | Vision creation | .raise/katas/project/vision.md |
| flow/tech-design.md | Tech design | .raise/katas/project/design.md |
| flow/backlog-creation.md | Backlog creation | .raise/katas/project/backlog.md |
| flow/implementation-plan.md | Implementation plan | .raise/katas/feature/plan.md |
| flow/development.md | Development | .raise/katas/feature/implement.md |
| patterns/code-analysis.md | Code analysis | .raise/katas/setup/analyze.md |
| patterns/ecosystem-discovery.md | Ecosystem mapping | .raise/katas/setup/ecosystem.md |
| patterns/tech-design-stack.md | Stack-aware design | .raise/katas/project/design.md (merge) |
| patterns/dependency-validation.md | Dependency check | .raise/katas/feature/review.md (merge) |

### Recommendation

1. **Archive `docs/katas/`** - organizational model deprecated
2. **Ensure `.raise/katas/` has all valuable content** migrated
3. **Update all katas** to remove principios/flujo/patron/tecnica terminology

---

## 6. Other Directories Analysis

### `docs/guides/`

```
docs/guides/
└── agents/        # Agent-specific guides
```

**Assessment:** **UPDATE NEEDED** (P3)
- Contains agent-specific configuration guides
- Needs update for v2.3 Context layer approach
- Migrate to `.raise/context/agents/`

### `docs/core/`

```
docs/core/
├── constitution.md   # v2.0.0 - Updated
├── methodology.md    # v2.1.1 - Uses kata levels (NEEDS UPDATE)
└── glossary.md       # v2.3.0 - FULLY UPDATED (authoritative)
```

**Assessment:**

| File | Assessment | Notes |
|------|------------|-------|
| constitution.md | **CARRY FORWARD** (P1) | Most current, authoritative |
| methodology.md | **UPDATE NEEDED** (P1) | Still uses kata levels |
| glossary.md | **CARRY FORWARD** (P1) | v2.3.0 - authoritative source |

**Relationship with `docs/corpus/`:**
- `docs/core/` is the **updated, authoritative** version
- `docs/corpus/` contains **historical v1.0** content
- `docs/core/glossary.md` is v2.3.0 and supersedes `docs/corpus/20-glossary.md`

---

## Carry Forward List

### Priority 1 (Must Migrate)

| File | Current Location | Target Location | Action |
|------|-----------------|-----------------|--------|
| glossary.md | docs/core/ | .raise/context/glossary.md | Copy as-is (v2.3 ready) |
| constitution.md | docs/core/ | .raise/context/constitution.md | Copy as-is |
| methodology.md | docs/core/ | .raise/context/methodology.md | Update Work Cycles terminology |
| work-cycles.md | docs/reference/ | .raise/context/work-cycles.md | Minor updates |
| learning-philosophy.md | docs/reference/ | .raise/context/philosophy.md | Update kata level refs |
| gate-code.md | docs/gates/ | .raise/gates/ | Copy |
| gate-plan.md | docs/gates/ | .raise/gates/ | Copy |

### Priority 2 (Should Migrate)

| File | Current Location | Target Location | Action |
|------|-----------------|-----------------|--------|
| security-compliance.md | docs/reference/ | .raise/context/compliance.md | Minor updates |
| architecture.md | docs/reference/ | .raise/context/architecture.md | Update component model |
| integration-patterns.md | docs/reference/ | .raise/context/integrations.md | Update terminology |
| templates-catalog.md | docs/reference/ | .raise/templates/README.md | Remove SAR, update paths |
| examples-library.md | docs/reference/ | .raise/guides/examples.md | Update for v2.3 workflow |
| Gate conflict resolution | docs/gates/ | .raise/gates/ | Merge richer content |

### Priority 3 (Nice to Have)

| File | Current Location | Target Location | Action |
|------|-----------------|-----------------|--------|
| data-architecture.md | docs/reference/ | .raise/context/data-model.md | Major rewrite |
| tech-stack.md | docs/reference/ | .raise/context/tech-stack.md | Updates |
| agent guides | docs/guides/agents/ | .raise/context/agents/ | Updates |

---

## Deprecated Content (Archive Without Migration)

### Files to Archive

```
docs/corpus/00-constitution.md      # Superseded by docs/core/
docs/corpus/01-product-vision.md    # Historical
docs/corpus/02-business-model.md    # Historical
docs/corpus/03-market-context.md    # Historical
docs/corpus/04-stakeholder-map.md   # Historical
docs/corpus/14-adr-index.md         # Not synchronized
docs/corpus/20-glossary.md          # Superseded by docs/core/
docs/corpus/23-commands-reference.md # Commands concept deprecated
docs/corpus/30-roadmap.md           # Historical
docs/corpus/31-current-state.md     # Historical
docs/corpus/32-session-log.md       # Historical
docs/corpus/33-issues-decisions.md  # Historical
docs/corpus/34-dependencies-blockers.md # Historical
docs/templates/sar/                  # SAR terminology deprecated
docs/katas/                          # Organizational model deprecated
docs/reference/commands-reference.md # Commands concept deprecated
```

### Archive Location

Create `docs/archive/v2.1/` and move all deprecated content there with a README explaining:
- These files represent the v2.1 documentation state
- They are preserved for historical reference
- They should not be used for v2.3+ development

---

## Conflicts Found

### 1. Gate Content Conflicts

| Gate | docs/gates/ Size | .raise/gates/ Size | Resolution |
|------|------------------|-------------------|------------|
| gate-discovery.md | 3947B (rich) | 1224B (minimal) | Use docs/ content, .raise/ format |
| gate-vision.md | 4418B (rich) | 1517B (minimal) | Use docs/ content, .raise/ format |

**Action:** Merge the detailed validation criteria from `docs/gates/` into the `.raise/gates/` format.

### 2. Organizational Model Conflict

- `docs/katas/` uses: principios/flujo/patron/tecnica (deprecated)
- `.raise/katas/` uses: project/feature/setup/improve (v2.3 correct)

**Action:** `.raise/katas/` structure is authoritative. Migrate content, discard old organization.

### 3. Terminology Conflicts

| Term | docs/ Usage | v2.3 Standard | Files Affected |
|------|-------------|---------------|----------------|
| SAR | Component name | Eliminated (use setup/) | 5+ files |
| CTX | Component name | Eliminated (use context/) | 3+ files |
| Command | Execution unit | Replaced by Kata/Skill | 8+ files |
| L0-L3 | Kata levels | Eliminated (use Work Cycles) | 10+ files |
| principios/flujo/patron/tecnica | Kata levels | Eliminated | 6+ files |

---

## Duplication Analysis

### Fully Duplicated (Same Content)

| File | docs/ | .raise/ | Action |
|------|-------|---------|--------|
| gate-backlog.md | docs/gates/ | .raise/gates/ | Delete from docs/ |
| gate-design.md | docs/gates/ | .raise/gates/ | Delete from docs/ |

### Partially Duplicated (Different Quality)

| Content Type | docs/ | .raise/ | Action |
|--------------|-------|---------|--------|
| Templates | 5 dirs | 5 dirs | Consolidate to .raise/ |
| Gates | 6 files | 6 files | Merge, keep richer content |
| Katas | Old structure | New structure | Migrate content to .raise/ |

### Unique to Each Location

**Unique to docs/:**
- corpus/ (historical context)
- reference/learning-philosophy.md (43KB deep dive)
- reference/work-cycles.md (Work Cycle formalization)
- gates/gate-code.md, gate-plan.md

**Unique to .raise/:**
- gates/gate-architecture.md
- gates/gate-estimation.md
- templates/architecture/
- skills/ (v2.3 new)
- harness/ (v2.3 new)

---

## Recommended v2.3 Documentation Structure

```
.raise/                              # Single source of truth
├── README.md                        # Framework overview
├── context/                         # Context Layer (what informs)
│   ├── constitution.md              # From docs/core/
│   ├── glossary.md                  # From docs/core/ (v2.3)
│   ├── methodology.md               # From docs/core/ (updated)
│   ├── philosophy.md                # From docs/reference/learning-philosophy.md
│   ├── work-cycles.md               # From docs/reference/
│   ├── architecture/                # System architecture docs
│   ├── compliance/                  # Security/compliance docs
│   └── agents/                      # Agent configuration guides
├── katas/                           # Kata Layer (how to do)
│   ├── README.md                    # Kata index by Work Cycle
│   ├── project/                     # 1x per epic
│   │   ├── discovery.md
│   │   ├── vision.md
│   │   ├── design.md
│   │   └── backlog.md
│   ├── feature/                     # Nx per feature
│   │   ├── plan.md
│   │   ├── implement.md
│   │   └── review.md
│   ├── setup/                       # 1x brownfield
│   │   ├── analyze.md
│   │   └── ecosystem.md
│   └── improve/                     # Continuous
│       ├── retrospective.md
│       └── evolve-kata.md
├── skills/                          # Skill Layer (atomic operations)
│   ├── README.md
│   └── *.yaml                       # Skill definitions
├── gates/                           # Validation Gates
│   ├── README.md
│   ├── gate-discovery.md            # Merged from docs/
│   ├── gate-vision.md               # Merged from docs/
│   ├── gate-design.md
│   ├── gate-backlog.md
│   ├── gate-plan.md                 # From docs/
│   ├── gate-code.md                 # From docs/
│   ├── gate-architecture.md
│   └── gate-estimation.md
├── templates/                       # Artifact Scaffolds
│   ├── README.md                    # Template catalog
│   ├── architecture/
│   ├── backlog/
│   ├── solution/
│   └── tech/
├── harness/                         # Kata Harness Configuration
│   └── config.yaml
└── guides/                          # How-to Guides
    └── examples.md                  # From docs/reference/examples-library.md

docs/archive/v2.1/                   # Historical reference
└── [all deprecated content]
```

---

## Migration Checklist

### Phase 1: Immediate (Before v2.3 Release)

- [ ] Copy `docs/core/glossary.md` to `.raise/context/glossary.md`
- [ ] Copy `docs/core/constitution.md` to `.raise/context/constitution.md`
- [ ] Update `docs/core/methodology.md` for Work Cycles, copy to `.raise/context/`
- [ ] Merge `docs/gates/gate-discovery.md` content into `.raise/gates/`
- [ ] Merge `docs/gates/gate-vision.md` content into `.raise/gates/`
- [ ] Copy `docs/gates/gate-code.md` to `.raise/gates/`
- [ ] Copy `docs/gates/gate-plan.md` to `.raise/gates/`
- [ ] Delete `docs/templates/sar/` (deprecated)

### Phase 2: Documentation Consolidation

- [ ] Migrate `docs/reference/learning-philosophy.md` (update terminology)
- [ ] Migrate `docs/reference/work-cycles.md` (minor updates)
- [ ] Migrate `docs/reference/security-compliance.md`
- [ ] Update `docs/reference/templates-catalog.md`, migrate to `.raise/templates/README.md`
- [ ] Archive all `docs/corpus/` files to `docs/archive/v2.1/corpus/`

### Phase 3: Kata Migration

- [ ] Verify all `docs/katas/` content exists in `.raise/katas/` (new structure)
- [ ] Archive `docs/katas/` to `docs/archive/v2.1/katas/`
- [ ] Update all kata files to remove principios/flujo/patron/tecnica references

### Phase 4: Cleanup

- [ ] Delete redundant files from `docs/gates/`
- [ ] Delete redundant files from `docs/templates/`
- [ ] Create `docs/archive/v2.1/README.md` explaining the archive
- [ ] Update all references in remaining docs to point to `.raise/` locations

---

## Appendix: Deprecated Terminology Quick Reference

| Deprecated Term | v2.3 Replacement | Context |
|-----------------|------------------|---------|
| SAR | `setup/` commands | Component name |
| CTX | `context/` commands | Component name |
| SAR Component | setup commands | Abstraction eliminated |
| CTX Component | context commands | Abstraction eliminated |
| Command | Kata or Skill | Execution unit |
| L0, L1, L2, L3 | Work Cycle names | Kata levels |
| principios | project/ or improve/ | Kata level |
| flujo | project/ or feature/ | Kata level |
| patron | setup/ | Kata level |
| tecnica | feature/ | Kata level |
| DoD | Validation Gate | Quality checkpoint |
| Rule | Guardrail | Operational directive |
| Kata Executor Harness | Kata Harness | Simplification |

---

*This audit was conducted following RaiSE principles of Governance as Code and Lean Software Development. All recommendations align with ADR-008 (Kata/Skill/Context Simplification).*
