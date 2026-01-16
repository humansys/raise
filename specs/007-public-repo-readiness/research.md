# Research: Public Repository Readiness

**Feature**: 007-public-repo-readiness
**Date**: 2026-01-16
**Purpose**: Document repository state analysis and design decisions for public F&F release

---

## 1. Repository State Inventory

### 1.1 Root Directory Files

| File | Status | Action Needed |
|------|--------|---------------|
| README.md | ❌ Missing | Create (FR-001) |
| LICENSE | ❌ Missing | Create Apache 2.0 (FR-003) |
| CONTRIBUTING.md | ❌ Missing | Create (FR-008) |
| CLAUDE.md | ✅ Present | Review for internal-only content |
| .gitignore | ✅ Present | No action |

### 1.2 Documentation Inventory

**Location**: `docs/framework/v2.1/`

| Directory | File Count | Status |
|-----------|------------|--------|
| model/ | 29 | ✅ Complete - Core ontology |
| adrs/ | 13 | ✅ Complete - Indexed |
| katas/ | 6 | ✅ Present - Educational |
| reportes/ | 3 | ✅ Present - Validation reports |
| specs/ | 0 | Empty (OK - specs in /specs/) |

**Key Documents (Golden Data Sources per CLAUDE.md):**

1. `.specify/memory/constitution.md` - spec-kit principles
2. `docs/framework/v2.1/model/00-constitution-v2.md` - RaiSE Constitution
3. `docs/framework/v2.1/model/20-glossary-v2.1.md` - Canonical terminology
4. `docs/framework/v2.1/model/21-methodology-v2.md` - Methodology
5. `docs/framework/v2.1/adrs/*.md` - Architecture decisions

### 1.3 Katas Inventory

**v2.1 Normalized** (`src/katas-v2.1/`):

| Category | Files | Taxonomy Status |
|----------|-------|-----------------|
| principios/ | 2 | ✅ v2.1 compliant |
| flujo/ | 6 | ✅ v2.1 compliant |
| patrón/ | 4 | ✅ v2.1 compliant |
| técnica/ | 0 | Empty (acceptable) |

**Legacy** (`src/katas/`):
- Marked with DEPRECATED.md
- Contains old L0-L3 naming
- Retained for reference only

### 1.4 Templates Inventory

**Location**: `src/templates/`

| Category | Count | Purpose |
|----------|-------|---------|
| backlog/ | 5 | User stories, epics, bugs |
| solution/ | 5 | Vision, requirements, SOW |
| tech/ | 3 | Component specs, API specs |
| cursor-rules/ | 5 | AI assistant rules |
| sar/ | 6 | Software architecture review |

---

## 2. Terminology Audit

### 2.1 Deprecated Terms Mapping

| Deprecated | Canonical (v2.1) | ADR Reference |
|------------|------------------|---------------|
| DoD | Validation Gate | ADR-006a |
| Rule | Guardrail | ADR-007 |
| Developer | Orquestador | Glossary v2.1 |
| L0/L1/L2/L3 | Principio/Flujo/Patrón/Técnica | ADR-011 |

### 2.2 Audit Strategy

**Files to scan**: `docs/framework/v2.1/**/*.md`

**Grep patterns**:
```bash
# DoD (case-insensitive, word boundary)
grep -rn "\bDoD\b" docs/framework/v2.1/

# Rule (careful: many valid uses of "rule")
grep -rn "Rule" docs/framework/v2.1/ | grep -v "Guardrail"

# Developer (as role, not generic)
grep -rn "Developer" docs/framework/v2.1/ | grep -i "role\|actor\|persona"

# L0-L3 kata levels
grep -rn "\bL[0-3]\b" docs/framework/v2.1/
```

### 2.3 Terminology Policy (Strict)

| Document Type | Deprecated Terms Allowed? |
|---------------|---------------------------|
| User-facing docs (constitution, glossary, methodology, katas, README) | ❌ **NEVER** - must be 100% clean |
| ADRs documenting migration (ADR-006a, ADR-007, ADR-011) | ✅ Acceptable (historical context) |
| Archive content (clearly marked deprecated) | ✅ Acceptable |
| Internal work logs (if they remain) | ✅ Acceptable |

**Decision**: User-facing documentation must have **ZERO deprecated terms**. No exceptions for "educational context" or "backward-compatibility explanations" in user-facing content. If a user sees "DoD" or "L0-L3" in their learning path, we have failed.

---

## 3. Link Integrity Analysis

### 3.1 Link Types

| Type | Pattern | Risk |
|------|---------|------|
| Relative internal | `[text](./path.md)` | Medium - path changes |
| Root-relative | `[text](/docs/...)` | Low - stable |
| External | `[text](https://...)` | High - may break |
| Anchor | `[text](#section)` | Medium - section renames |

### 3.2 Audit Strategy

```bash
# Extract all markdown links
grep -roh "\[.*\](.*)" docs/framework/v2.1/ | \
  grep -v "http" | \
  sort -u

# Verify each file exists
# (Manual or scripted verification)
```

### 3.3 Known Risk Areas

- Cross-references between model documents
- ADR references to glossary terms
- Kata references to methodology sections

---

## 4. Sensitive Information Scan

### 4.1 Patterns to Check

| Pattern | Risk | Example |
|---------|------|---------|
| API keys | Critical | `sk-...`, `api_key=...` |
| Internal URLs | High | `*.humansys.io`, `gitlab.com/humansys-demos` |
| Credentials | Critical | `password=`, `token=` |
| Private paths | Medium | `/Users/...`, `C:\Users\...` |

### 4.2 Scan Commands

```bash
# API keys
grep -rn "sk-\|api_key\|apikey\|API_KEY" .

# Internal domains
grep -rn "humansys\|internal\." docs/

# Credentials
grep -rn "password\|secret\|credential\|token=" .

# Private paths
grep -rn "/Users/\|/home/\|C:\\\\Users" docs/
```

### 4.3 CLAUDE.md Review

File contains:
- GitLab remote URL: `gitlab.com:humansys-demos/product/raise1/raise-commons`
- This is **acceptable** for public repo (repo URL will be public)

---

## 5. Content Audit: What Doesn't Belong

> ⚠️ **Critical**: Current repo structure is ARBITRARY. Content was accumulated organically, not designed for public consumption.

### 5.1 Suspect Documents (Likely Remove)

| Document | Current Location | Why Remove |
|----------|------------------|------------|
| `02-business-model-v2.md` | model/ | Business doc, not for public devs |
| `03-market-context-v2.md` | model/ | Business analysis, not for public |
| `04-stakeholder-map-v2.md` | model/ | Internal stakeholder info |
| `30-roadmap-v2.1.md` | model/ | Internal planning |
| `31-current-state-v2.1.md` | model/ | Internal status tracking |
| `32-session-log-v2.md` | model/ | Work artifact |
| `33-issues-decisions-v2.md` | model/ | Internal tracking |
| `34-dependencies-blockers-v2.md` | model/ | Internal tracking |
| `35-ontology-backlog-v2.md` | model/ | Internal backlog |
| `36-roadmap-tecnico-mvp.md` | model/ | Internal MVP planning |
| `37-roadmap-tecnico-mvp-legacy.md` | model/ | Legacy internal |
| `docs/framework/v2.1/reportes/` | reportes/ | Internal validation reports |
| `specs/` directory | root | Active development work, not public |

### 5.2 Content Classification Framework

| Classification | Belongs in Public Repo? | Examples |
|----------------|-------------------------|----------|
| **Core Ontology** | ✅ YES | Constitution, Glossary, Methodology |
| **Technical Decisions** | ✅ YES | ADRs |
| **Learning Exercises** | ✅ YES | Katas |
| **Reusable Templates** | ⚠️ MAYBE | Only if useful to external users |
| **Business Documents** | ❌ NO | Business model, market analysis |
| **Internal Roadmaps** | ❌ NO | Any planning/status docs |
| **Work Artifacts** | ❌ NO | Session logs, specs, reports |
| **Research Notes** | ⚠️ DEPENDS | Only if publishable quality |

### 5.3 Where Should Removed Content Go?

| Option | Use Case |
|--------|----------|
| Private repo (raise-internal) | Business docs, roadmaps, planning |
| Delete | Truly obsolete, no historical value |
| Archive in this repo | Has historical reference value but not user-facing |

**Decision needed in WP0**: Destination for each removed document.

---

## 6. Navigation Design Decisions

### 6.1 Problem Statement

**Current state**: No README.md means users land on GitLab's default view showing file list. No guidance on where to start.

**User need**: Understand RaiSE purpose and find relevant documentation within 5 minutes.

### 6.2 Design Decision: Hub-and-Spoke Navigation

**Decision**: README.md as central hub with direct links to all major sections.

**Rationale**:
- Matches user mental model (README = starting point)
- GitLab renders README.md on repository homepage
- Single point of maintenance for navigation

**Alternatives considered**:
- Separate GETTING_STARTED.md → Rejected: extra file, extra click
- Index in docs/ → Rejected: not visible by default

### 6.3 Navigation Hierarchy

```
README.md (Hub)
├── Core Concepts (≤2 clicks)
│   ├── Constitution → docs/framework/v2.1/model/00-constitution-v2.md
│   ├── Glossary → docs/framework/v2.1/model/20-glossary-v2.1.md
│   └── Methodology → docs/framework/v2.1/model/21-methodology-v2.md
│
├── Technical Reference (≤2 clicks)
│   ├── ADRs → docs/framework/v2.1/adrs/adr-000-index.md
│   └── Architecture → docs/framework/v2.1/model/10-system-architecture-v2.1.md
│
├── Practical (≤2 clicks)
│   ├── Katas → src/katas-v2.1/README.md
│   └── Templates → src/templates/
│
└── Meta (≤1 click)
    ├── License → LICENSE
    ├── Contributing → CONTRIBUTING.md
    └── Issues → GitLab Issues
```

---

## 7. Content Decisions

### 7.1 README.md Scope

**Decision**: Concise README (~200-300 lines) focused on:
- What is RaiSE (1 paragraph)
- Why it matters (1 paragraph)
- Quick navigation table
- Repository structure overview
- Ecosystem acknowledgment (brief)
- License and contributing links

**Rationale**: Principle IV (Simplicidad) - "Preferir documentación concisa que cubra el 80% de casos"

### 7.2 LICENSE Selection

**Decision**: Apache 2.0

**Rationale** (from spec clarifications):
- Patent protection clause (Section 3)
- Enterprise-friendly terms
- Compatible with most open-source projects
- Explicit contributor license grant

### 7.3 CONTRIBUTING.md Scope

**Decision**: Lightweight guide (~50-100 lines) covering:
- Clarify this is conceptual repo (not code)
- How to open issues (GitLab)
- Basic contribution process
- Terminology guidelines (link to glossary)

**Rationale**: Most F&F users will consume, not contribute. Keep barrier low.

### 7.4 Language Policy

**Decision**: Spanish and English both acceptable

**Rationale**:
- Existing content is mixed (some Spanish, some English)
- F&F audience likely bilingual
- Enforcing single language would require massive migration
- Constitution allows this flexibility

---

## 8. Risk Mitigations

| Risk | Mitigation | Owner |
|------|------------|-------|
| Broken links at launch | Pre-launch link audit | Implementation |
| Deprecated terms in user docs | Strict 0% policy + grep audit | WP3 |
| Users expect code | "Conceptual repository" statement in README | README design |
| Sensitive info leak | grep scan + manual review | Implementation |
| Poor README quality | Fresh-eyes review before merge | Validation |
| Business docs exposed publicly | Deep content audit in WP0 | WP0 |
| Wrong content stays | Treat ALL content as arbitrary; justify each doc | WP0 |
| Removed content lost | Define destination (private repo/archive) before removing | WP0 |

---

## 9. Resolved Research Questions

| Question | Resolution |
|----------|------------|
| What license? | Apache 2.0 (spec decision) |
| Where to report issues? | GitLab Issues (spec decision) |
| How to handle deprecated terms? | **STRICT**: 0% in user-facing docs. Only allowed in ADRs documenting migration, archive, and internal logs |
| Single language or bilingual? | Bilingual acceptable |
| How many clicks to core docs? | ≤2 clicks (spec SC-004) |
| What about other RaiSE repos? | Acknowledge ecosystem exists, no details |
| Is current content valid? | **NO** - treat as arbitrary. Every doc needs justification |
| Where does removed content go? | Decision per doc: private repo, archive, or delete (WP0) |

---

*Research completed: 2026-01-16*
*Ready for Phase 1 artifact generation*
