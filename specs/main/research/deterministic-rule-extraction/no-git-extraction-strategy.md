# No-Git Extraction Strategy for Brownfield Rule Extraction

**Document Type**: Strategy Revision
**Date**: 2026-01-24
**Status**: ACTIVE
**Constraint**: Target codebases have no git or version control infrastructure

---

## Executive Summary

This document consolidates the revised approach for brownfield rule extraction when target codebases lack version control. It synthesizes findings from prior art research and updates the MVP tooling and scoring algorithms accordingly.

---

## 1. Critical Constraint Impact

### What We Lost (Requires Git)

| Signal | Original Source | Value |
|--------|-----------------|-------|
| Author Diversity | `git blame` | Indicates team consensus |
| Pattern Stability | `git log --since` | Indicates mature conventions |
| Commit Messages | `git log --format` | Explains "why" behind patterns |
| PR Comments | GitHub/GitLab API | Reviewer-validated rules |
| Evolution History | `git log -p` | How patterns emerged |

### What We Keep (No Git Required)

| Signal | Source | Value |
|--------|--------|-------|
| Occurrence Count | ast-grep/ripgrep | Frequency of pattern |
| Module Spread | dirname analysis | Proxy for team consensus |
| Structural Consistency | AST comparison | Pattern uniformity |
| Documentation | grep on comments/docs | Explicit rule mentions |
| Human Classification | Manual rating | Expert judgment |

---

## 2. Revised Tool Stack

### Active Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **ast-grep (sg)** | AST-based pattern matching | `npm i -g @ast-grep/cli` |
| **ripgrep (rg)** | Fast text search | `apt install ripgrep` |
| **Bash** | Orchestration | Built-in |

### Removed Tools

| Tool | Original Purpose | Why Removed |
|------|------------------|-------------|
| ~~git~~ | History analysis | No VCS in target codebases |
| ~~jc~~ | git output to JSON | Dependency of git |

---

## 3. Revised Scoring Algorithm

### Original (With Git)
```
S = 0.30*Frequency + 0.35*Criticality + 0.20*Stability + 0.15*Author_Diversity
```

### Revised (No Git)
```
S = 0.40*Frequency + 0.40*Criticality + 0.20*Locality

Where:
- Frequency (F): log10(occurrences) / log10(max_occurrences)
- Criticality (C): Human classification (HIGH=1.0, MEDIUM=0.7, LOW=0.4)
- Locality (L): module_spread / total_modules
```

### Weight Redistribution Rationale

| Factor | Old Weight | New Weight | Rationale |
|--------|------------|------------|-----------|
| Frequency | 0.30 | **0.40** | Strongest remaining signal |
| Criticality | 0.35 | **0.40** | Human judgment compensates for lost signals |
| Stability | 0.20 | **0.00** | Requires git history |
| Author Diversity | 0.15 | **0.00** | Requires git blame |
| Locality (new) | N/A | **0.20** | Module spread as proxy for team consensus |

---

## 4. Evidence Collection (No-Git)

### Pattern Mining Commands

**1. Find naming patterns:**
```bash
# Count class naming conventions
rg -c 'class \w+Repository' src/ | sort -t: -k2 -rn

# Find all class declarations
sg --pattern 'class $NAME' --json src/ | jq '.matches[] | .file'
```

**2. Module spread analysis (replaces author diversity):**
```bash
# Count unique directories containing pattern
rg -l 'class.*Repository' src/ | xargs -I{} dirname {} | sort -u | wc -l

# Get breakdown by module
rg -l 'class.*Repository' src/ | xargs -I{} dirname {} | sort | uniq -c | sort -rn
```

**3. Structural pattern detection:**
```bash
# Find consistent error handling patterns
sg --pattern 'try { $$$ } catch($ERR) { $$$ }' --json src/

# Find async/await patterns
sg --pattern 'async function $NAME($$$) { $$$ }' --json src/
```

**4. Documentation mention check:**
```bash
# Check if pattern is documented
rg -i 'repository.*convention|naming.*repository' docs/ README.md CONTRIBUTING.md
```

### Evidence YAML Schema (No-Git)

```yaml
pattern:
  id: "naming-001-repository-suffix"
  description: "Classes in src/repositories end with 'Repository'"
  type: naming_convention
  source: "pattern-mining"

evidence:
  query: "rg -l 'class.*Repository' src/repositories/"
  occurrences: 12
  files:
    - path: src/repositories/UserRepository.ts
      line: 5
      snippet: "export class UserRepository implements..."
    # ... more files

  # Module spread (replaces author diversity)
  modules:
    - src/repositories/
    - src/domain/
    - lib/persistence/
  module_count: 3
  module_ratio: 0.60  # 3 of 5 total modules

  counter_examples:
    - path: src/repositories/UserStore.ts
      reason: "Does not follow naming convention"

  documentation_mentions:
    - path: docs/architecture.md
      line: 45
      snippet: "All repository classes should end with 'Repository'"

score:
  frequency: 0.85       # 12 occurrences, log-scaled
  criticality: 0.90     # Human-rated HIGH
  locality: 0.60        # 3/5 modules
  total: 0.82           # 0.40(0.85) + 0.40(0.90) + 0.20(0.60)

recommendation:
  include: true
  priority: P1
  confidence: MEDIUM    # Lower than with-git due to reduced signals
```

---

## 5. Quality Tiers (No-Git)

| Tier | Signals Required | Confidence |
|------|------------------|------------|
| **GOLD** | 5+ occurrences, 3+ modules, human HIGH criticality, documented | HIGH |
| **SILVER** | 3+ occurrences, 2+ modules, human MEDIUM+ criticality | MEDIUM |
| **BRONZE** | 1-2 occurrences OR 1 module OR LOW criticality | LOW |

**Minimum for inclusion**: SILVER (lowered threshold due to reduced signals)

---

## 6. Applicable Prior Art (No-Git)

### Directly Applicable

| Approach | Source | Why It Works Without Git |
|----------|--------|--------------------------|
| **BMAD document-project** | BMAD-METHOD | Scans current codebase state |
| **Self-improving rules** | Cursor | Works on current code patterns |
| **CONVENTIONS.md bootstrap** | Aider | Manual capture, no history needed |
| **ast-grep/ripgrep mining** | CLI tools | Static codebase analysis |
| **Autogrep LLM extraction** | Semgrep research | Works on current code |
| **EditorConfig inference** | editorconfig-tools | File-based style detection |

### Not Applicable (Requires Git)

| Approach | Source | Why Invalidated |
|----------|--------|-----------------|
| ~~PR comment inference~~ | Greptile | Requires PR history |
| ~~Author diversity scoring~~ | Original design | Requires git blame |
| ~~Stability scoring~~ | Original design | Requires git log |
| ~~Amazon CodeGuru mining~~ | AWS | Requires repository history |

---

## 7. Recommended Workflow

### Phase 1: Bootstrap Discovery

```
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 1: Bootstrap Discovery                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Run BMAD-style document-project analysis                │
│     - Scan directory structure                              │
│     - Identify technology stack                             │
│     - Generate initial architecture overview                │
│                                                             │
│  2. Check for existing documentation                        │
│     - CONTRIBUTING.md, CODE_STYLE.md, etc.                  │
│     - Extract explicit conventions                          │
│                                                             │
│  3. Human expert interview (if available)                   │
│     - "What patterns does your team follow?"                │
│     - Capture as initial rule candidates                    │
│                                                             │
│  Output: Initial pattern candidates list                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Deterministic Validation

```
┌─────────────────────────────────────────────────────────────┐
│               PHASE 2: Deterministic Validation              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  For each pattern candidate:                                │
│                                                             │
│  1. Generate ast-grep/ripgrep query                         │
│     ./validate-pattern.sh "pattern description"             │
│                                                             │
│  2. Collect evidence                                        │
│     - Occurrence count                                      │
│     - Module spread (dirname | sort -u)                     │
│     - Counter-examples                                      │
│                                                             │
│  3. Calculate score                                         │
│     S = 0.40F + 0.40C + 0.20L                               │
│                                                             │
│  4. Human criticality rating                                │
│     - HIGH/MEDIUM/LOW based on impact                       │
│                                                             │
│  Output: evidence.yaml per pattern                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Rule Generation

```
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 3: Rule Generation                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  For patterns meeting SILVER+ tier:                         │
│                                                             │
│  1. Generate rule from template                             │
│     ./generate-rule.sh --evidence evidence.yaml             │
│                                                             │
│  2. Add to rule graph                                       │
│     ./add-to-graph.sh --rule rule.mdc                       │
│                                                             │
│  3. Validate rule quality                                   │
│     - Check for conflicts                                   │
│     - Verify examples compile                               │
│                                                             │
│  Output: .cursor/rules/*.mdc + rules-graph.yaml             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. MVP Scripts (Revised)

| Script | Purpose | Status |
|--------|---------|--------|
| `validate-pattern.sh` | Collect evidence for pattern (no-git version) | P0 |
| `generate-rule.sh` | Create rule file from template | P0 |
| `add-to-graph.sh` | Add rule to rules-graph.yaml | P0 |
| `calculate-score.sh` | Apply no-git scoring algorithm | P1 |
| ~~`extract-authors.sh`~~ | ~~Get author diversity~~ | REMOVED |
| ~~`extract-stability.sh`~~ | ~~Get pattern age~~ | REMOVED |

---

## 9. Risk Mitigation

### Risk: Lower Confidence Without Git

**Impact**: Rules may be extracted that don't reflect team consensus (just one developer's style).

**Mitigation**:
1. Require SILVER tier minimum (3+ occurrences, 2+ modules)
2. Human criticality rating adds expert judgment
3. Counter-example requirement catches inconsistencies
4. Periodic rule review with actual team members

### Risk: Module Spread Not Reliable

**Impact**: One developer may have touched all modules.

**Mitigation**:
1. Combined with high occurrence count
2. Documentation mention check adds signal
3. Human validation before rule promotion

### Risk: No Historical Pattern Evolution

**Impact**: Can't tell if pattern is emerging, stable, or deprecated.

**Mitigation**:
1. Focus on high-occurrence patterns (likely stable)
2. Flag low-occurrence patterns as "experimental"
3. Build rule evolution into ongoing process (Cursor self-improvement pattern)

---

## 10. Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| End-to-end works | YES | Pattern → rule in graph |
| Time per rule | <20 min | Stopwatch (increased from <15 due to manual steps) |
| Rule quality | Passes validation | Quality gates script |
| Determinism | Same input → same output | Run twice, diff |
| Module spread threshold | ≥2 modules | Evidence validation |

---

## References

- [Solution Vision (Revised)](./solution-vision-rule-extraction-katas.md)
- [MVP Tooling Selection (Revised)](./mvp-tooling-selection.md)
- [Prior Art Research](./prior-art-rule-extraction.md)
- [Deterministic Extraction Patterns](./deterministic-extraction-patterns.md)

---

**Document Status**: Active
**Next Step**: Implement revised MVP scripts with no-git constraints
