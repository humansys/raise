# Data Model: Repository Structure Analysis

**Feature**: 007-public-repo-readiness
**Date**: 2026-01-16
**Status**: PRELIMINARY - Final structure determined in WP0 execution

---

## 1. Current Structure Inventory

```
raise-commons/
├── CLAUDE.md                          # Dev guide (internal)
├── .gitignore
│
├── docs/
│   ├── framework/v2.1/
│   │   ├── model/                     # 29 core ontology docs
│   │   ├── adrs/                      # 13 ADRs
│   │   ├── katas/                     # 6 kata docs (DUPLICATE?)
│   │   ├── reportes/                  # 3 validation reports
│   │   └── specs/                     # Empty
│   └── archive/                       # v1.x content
│
├── src/
│   ├── katas-v2.1/                    # Normalized katas (DUPLICATE?)
│   │   ├── principios/
│   │   ├── flujo/
│   │   ├── patrón/
│   │   └── técnica/
│   ├── katas/                         # Legacy (DEPRECATED)
│   └── templates/                     # 20+ reusable templates
│
├── specs/                             # Feature specs (spec-kit)
│
├── .specify/                          # spec-kit config (hidden)
│   ├── memory/constitution.md
│   ├── templates/
│   └── scripts/
│
├── .raise/                            # Agent config (hidden)
│   └── agents/
│
└── .claude/                           # Claude commands (hidden)
    └── commands/
```

---

## 2. Semantic Categories Identified

| Category | Description | Current Location(s) |
|----------|-------------|---------------------|
| **Core Ontology** | Constitution, Glossary, Methodology | `docs/framework/v2.1/model/` |
| **Decisions** | Architecture Decision Records | `docs/framework/v2.1/adrs/` |
| **Exercises** | Katas for learning/practicing | `docs/framework/v2.1/katas/` + `src/katas-v2.1/` |
| **Templates** | Reusable document templates | `src/templates/` |
| **Archive** | Deprecated/historical content | `docs/archive/` + `src/katas/` |
| **Tooling** | spec-kit, agent configs, commands | `.specify/`, `.raise/`, `.claude/` |
| **Feature Work** | Active development specs | `specs/` |

---

## 3. Structural Problems

### 3.1 Duplication

| Content | Location A | Location B | Resolution Needed |
|---------|------------|------------|-------------------|
| Katas | `docs/framework/v2.1/katas/` | `src/katas-v2.1/` | Consolidate to ONE |

### 3.2 Naming/Semantics

| Issue | Current | Problem |
|-------|---------|---------|
| `src/` for non-code | `src/templates/`, `src/katas-v2.1/` | Implies source code; misleading |
| Version in path | `docs/framework/v2.1/` | Unnecessary depth; v2.1 IS current |
| Mixed languages | Some dirs Spanish, some English | Inconsistent |

### 3.3 Depth Analysis

| Path | Depth | Content Type |
|------|-------|--------------|
| `docs/framework/v2.1/model/00-constitution-v2.md` | 5 | Core doc |
| `src/katas-v2.1/flujo/01-discovery.md` | 4 | Exercise |
| `docs/archive/` | 2 | Archive |

**Observation**: Core content is deeper than archive content - inverted priority.

### 3.4 Visibility

| Content | Visible? | Should Be? |
|---------|----------|------------|
| Core ontology | Requires navigation | YES - front and center |
| Tooling configs | Hidden (dot-dirs) | Probably OK hidden |
| Templates | Under `src/` | Maybe more visible? |

---

## 4. Analysis Questions for WP0

### Question 1: What is the canonical Kata location?

**Options**:
- A) `docs/framework/v2.1/katas/` (alongside other v2.1 docs)
- B) `src/katas-v2.1/` (separate, with semantic subdirs)
- C) New location: `katas/` at root
- D) Merge into single location TBD

### Question 2: Should `src/` exist in a conceptual repo?

**Options**:
- A) Keep `src/` - familiar convention
- B) Rename to `resources/` or `assets/`
- C) Eliminate - move contents elsewhere
- D) Keep but clarify purpose in README

### Question 3: How to handle versioning in paths?

**Options**:
- A) Keep `v2.1` in path (explicit versioning)
- B) Remove `v2.1` - current is assumed, archive is explicit
- C) Use symlinks (`current/` → `v2.1/`)

### Question 4: Optimal depth for core content?

**Options**:
- A) Keep current depth (consistency)
- B) Flatten to max 2 levels from root
- C) Flatten selectively (core docs shallow, reference deep)

### Question 5: Should tooling configs be documented publicly?

**Options**:
- A) Keep hidden, document in CLAUDE.md only
- B) Keep hidden, add `docs/tooling/` with public docs
- C) Make visible (rename to non-dot dirs)

---

## 5. Proposed Structure Options

### Option A: Minimal Change (Conservative)

```
raise-commons/
├── README.md                    # NEW
├── LICENSE                      # NEW
├── CONTRIBUTING.md              # NEW
├── docs/
│   └── framework/v2.1/          # Keep as-is
├── src/
│   ├── katas-v2.1/              # CANONICAL (remove docs/framework/v2.1/katas/)
│   └── templates/
└── [hidden dirs unchanged]
```

**Pros**: Minimal disruption, fewer broken links
**Cons**: Doesn't address depth or naming issues

### Option B: Flattened Semantic (Moderate)

```
raise-commons/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── model/                       # Core ontology (was docs/framework/v2.1/model/)
│   ├── constitution.md
│   ├── glossary.md
│   └── methodology.md
├── decisions/                   # ADRs (was docs/framework/v2.1/adrs/)
├── katas/                       # Exercises (consolidated)
│   ├── principios/
│   ├── flujo/
│   ├── patrón/
│   └── técnica/
├── templates/                   # Reusable templates (was src/templates/)
├── archive/                     # Historical (was docs/archive/)
└── [hidden dirs unchanged]
```

**Pros**: Clear categories, shallow depth, semantic naming
**Cons**: Many file moves, link updates needed

### Option C: Documentation Hub (Aggressive)

```
raise-commons/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── docs/
│   ├── README.md                # Docs index
│   ├── core/                    # Constitution, Glossary, Methodology
│   ├── decisions/               # ADRs
│   ├── exercises/               # Katas
│   └── reference/               # Templates, schemas
├── archive/                     # All deprecated content
└── .internal/                   # All tooling (consolidate dot-dirs)
```

**Pros**: Single `docs/` entry point, very clean
**Cons**: Most disruptive, requires careful migration

---

## 6. Decision Framework

**Criteria for evaluation (WP0):**

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Navigability | High | First-time visitor can find content easily |
| Semantic clarity | High | Directory names reflect content purpose |
| Migration cost | Medium | Number of files to move, links to update |
| Convention alignment | Medium | Follows common OSS patterns |
| Tool compatibility | Low | Works with existing tooling |

---

## 7. Next Steps

1. **WP0 Execution**: Interactive analysis with Orquestador
2. **Decision**: Select structure option (A, B, C, or hybrid)
3. **Document**: Create ADR if Option B or C chosen
4. **Execute**: WP1 restructuring based on decision

---

*Data model prepared: 2026-01-16*
*Final structure: TBD in WP0 execution*
