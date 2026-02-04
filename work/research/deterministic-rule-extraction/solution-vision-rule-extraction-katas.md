# Solution Vision: Rule Extraction Katas (L2-01 & L2-03)

**Document Type**: Solution Vision (Options Analysis)
**Date**: 2026-01-24
**Status**: REVISED - No-Git Constraint Applied
**Goal**: Define KISS/DRY/YAGNI approach for PoC implementation

---

## Critical Constraint

> **Target codebases will be brownfield projects WITHOUT git or any version control infrastructure.**

This constraint eliminates approaches that rely on:
- Git history mining (Amazon CodeGuru pattern)
- PR comment inference (Greptile pattern)
- Author diversity scoring (git blame)
- Stability scoring based on commit age
- Temporal pattern analysis from commits

---

## Problem Statement

We need to extract governance-grade rules from brownfield codebases **without VCS** and populate a deterministic rule graph.

### Revised Research Conclusions (No-Git):

1. **Tool Stack**: ast-grep, ripgrep, bash (~~git+jc~~ removed)
2. **Scoring Algorithm**: `S = 0.40F + 0.40C + 0.20L` (stability removed, weights redistributed)
3. **Evidence Standards**: 3+ examples, 2+ counter-examples, 2+ modules (~~authors~~ removed)
4. **Output Format**: YAML frontmatter + Markdown (Rule Template v2)
5. **Target Metrics**: Precision ≥95%, Recall ≥80%, Consistency ≥99%

### What Remains Valid (No-Git):

| Approach | Source | Why It Works |
|----------|--------|--------------|
| **BMAD document-project** | BMAD-METHOD | Analyzes current codebase state, not history |
| **Self-improving rules** | Cursor | Works on current code patterns |
| **CONVENTIONS.md bootstrap** | Aider | Manual capture, no git needed |
| **ast-grep/ripgrep mining** | CLI tools | Static codebase analysis |
| **Autogrep LLM extraction** | Semgrep research | Works on current code |
| **EditorConfig inference** | editorconfig-tools | File-based style detection |

### What's Invalidated (Requires Git):

| Approach | Why Invalidated |
|----------|-----------------|
| PR comment → rule inference | Requires git history + PRs |
| Author diversity scoring | Requires git blame |
| Stability scoring (age-based) | Requires git log |
| Amazon CodeGuru mining | Requires repository history |
| Temporal pattern analysis | Requires commit sequence |

**The Question**: What level of automation is appropriate for MVP **without git**?

---

## Design Space Analysis

### Axis 1: Automation Level

| Level | Description | Human Effort | Build Effort |
|-------|-------------|--------------|--------------|
| **L0** | Fully manual with CLI guidance | High | Minimal |
| **L1** | Script-assisted aggregation | Medium | Low |
| **L2** | AI-assisted with human validation | Low | Medium |
| **L3** | Fully automated pipeline | Minimal | High |

### Axis 2: Pattern Discovery Method

| Method | Determinism | Accuracy | Speed |
|--------|-------------|----------|-------|
| **M1** | SAR-derived (from existing analysis) | HIGH | HIGH | Fast |
| **M2** | Tool-mined (ast-grep/ripgrep) | HIGH | MEDIUM | Medium |
| **M3** | AI-inferred (Claude analyzes code) | LOW | HIGH | Fast |
| **M4** | Hybrid (SAR + Tool + AI verification) | MEDIUM | HIGH | Slow |

### Axis 3: Rule Generation Method

| Method | Quality | Speed | Human Oversight |
|--------|---------|-------|-----------------|
| **R1** | Manual rule authoring | HIGH | Slow | Full |
| **R2** | Template-assisted generation | HIGH | Medium | Review |
| **R3** | AI-generated with validation gate | MEDIUM | Fast | Approve/Reject |
| **R4** | Fully automated (no human) | VARIABLE | Instant | None |

---

## Option Analysis

### Option A: "Guided Manual" (L0 + M1 + R1)

**Philosophy**: Kata provides step-by-step instructions; human does everything manually.

```
┌─────────────────────────────────────────────────────────────┐
│                    OPTION A: Guided Manual                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │   SAR   │───►│ Human   │───►│ Human   │───►│ Human   │ │
│  │ Reports │    │ Reviews │    │ Writes  │    │ Adds to │ │
│  │         │    │ Patterns│    │ Rules   │    │ Graph   │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                                                             │
│  CLI Tools: Used ad-hoc for verification                    │
│  Automation: None                                           │
│  Scripts: 0                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**What the Kata Contains**:
- Step-by-step instructions for reading SAR reports
- Example CLI commands to run manually
- Template for rule creation (copy-paste)
- Checklist for quality validation

**Pros**:
- ✅ Zero build effort (just documentation)
- ✅ Maximum learning (human does everything)
- ✅ Highest quality (human judgment throughout)
- ✅ Works immediately

**Cons**:
- ❌ Slow (hours per rule)
- ❌ Doesn't scale
- ❌ Inconsistent (human variation)
- ❌ Not suitable for large codebases

**Build Effort**: 1 day (write Kata documentation only)
**Per-Rule Effort**: 30-60 minutes

**KISS/DRY/YAGNI Assessment**:
- KISS: ✅ Simplest possible
- DRY: ❌ Human repeats same steps
- YAGNI: ✅ No unused automation

---

### Option B: "Script-Assisted" (L1 + M2 + R2)

**Philosophy**: Scripts do the tedious work; human makes decisions.

```
┌─────────────────────────────────────────────────────────────┐
│                 OPTION B: Script-Assisted                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │Codebase │───►│ Scripts │───►│ Human   │───►│ Script  │ │
│  │         │    │ Mine &  │    │ Reviews │    │ Generates│ │
│  │         │    │ Score   │    │ Selects │    │ Rule    │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                      │                             │        │
│                      ▼                             ▼        │
│               candidates.yaml              .cursor/rules/   │
│                                                             │
│  Scripts: 3 (mine, score, generate)                         │
│  Automation: Pattern discovery + scoring + file creation    │
│  Human: Selection + review                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**What We Build**:

```bash
# Script 1: mine-patterns.sh
# Runs ast-grep + ripgrep, outputs candidates.yaml
./mine-patterns.sh ./src --output candidates.yaml

# Script 2: score-candidates.sh
# Applies scoring algorithm, ranks candidates
./score-candidates.sh candidates.yaml --output scored.yaml

# Script 3: generate-rule.sh
# Takes selected candidate, creates rule file from template
./generate-rule.sh --candidate scored.yaml:3 --output .cursor/rules/pattern-001.mdc
```

**Pros**:
- ✅ Low build effort (3 bash scripts)
- ✅ Consistent pattern discovery
- ✅ Human retains decision authority
- ✅ Reusable scripts (DRY)

**Cons**:
- ❌ Still requires human for each rule
- ❌ Medium speed (10-15 min per rule)
- ❌ Scripts need maintenance

**Build Effort**: 3-4 days
**Per-Rule Effort**: 10-15 minutes

**KISS/DRY/YAGNI Assessment**:
- KISS: ✅ Simple scripts, clear separation
- DRY: ✅ Scripts eliminate repetition
- YAGNI: ✅ Only builds what's needed

---

### Option C: "AI-Assisted" (L2 + M4 + R3)

**Philosophy**: AI agent runs the pipeline; human approves results.

```
┌─────────────────────────────────────────────────────────────┐
│                   OPTION C: AI-Assisted                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │ Human   │───►│   AI    │───►│   AI    │───►│ Human   │ │
│  │ Invokes │    │ Mines   │    │ Proposes│    │ Approves│ │
│  │ Kata    │    │ Patterns│    │ Rules   │    │ or Edits│ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                      │              │               │       │
│                      ▼              ▼               ▼       │
│               [CLI Tools]    [Rule Draft]    [Final Rule]  │
│                                                             │
│  AI Agent: Follows Kata, uses tools, proposes rules         │
│  Scripts: Same as Option B (AI invokes them)                │
│  Human: Final approval only                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**What We Build**:
1. Same 3 scripts as Option B
2. Kata designed for AI agent execution
3. Approval workflow (human reviews AI output)

**Kata Structure**:
```markdown
### Step 3: Mine Patterns

Run the pattern mining script:
```bash
./mine-patterns.sh $CODEBASE --output $WORKDIR/candidates.yaml
```

**Verification**: `candidates.yaml` exists and contains >0 patterns

> **Si no puedes continuar**: No patterns found → Check codebase path;
> if correct, codebase may lack extractable patterns → JIDOKA: Ask human
```

**Pros**:
- ✅ Fast (AI does heavy lifting)
- ✅ Consistent (AI follows same steps)
- ✅ Human oversight preserved
- ✅ Leverages existing AI agent capabilities

**Cons**:
- ❌ AI may miss nuances
- ❌ Requires well-designed Kata
- ❌ Non-deterministic AI reasoning

**Build Effort**: 4-5 days (scripts + Kata + approval flow)
**Per-Rule Effort**: 2-5 minutes (mostly review time)

**KISS/DRY/YAGNI Assessment**:
- KISS: ⚠️ More moving parts, but each is simple
- DRY: ✅ AI reuses scripts, follows same pattern
- YAGNI: ✅ Only builds what's needed for workflow

---

### Option D: "Hybrid Incremental" (L1.5 + M1+M2 + R2)

**Philosophy**: Start with SAR insights, validate with tools, generate with templates.

```
┌─────────────────────────────────────────────────────────────┐
│                OPTION D: Hybrid Incremental                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐                                                │
│  │   SAR   │──┐                                             │
│  │ Reports │  │   ┌─────────┐    ┌─────────┐    ┌─────────┐│
│  └─────────┘  ├──►│ Human   │───►│ Script  │───►│ Script  ││
│  ┌─────────┐  │   │ Selects │    │Validates│    │Generates││
│  │ Tool    │──┘   │ Pattern │    │ Evidence│    │ Rule    ││
│  │ Mining  │      └─────────┘    └─────────┘    └─────────┘│
│  └─────────┘           │              │              │      │
│       │                ▼              ▼              ▼      │
│       └────────► [Pattern ID]  [evidence.yaml] [rule.mdc]  │
│                                                             │
│  Key Insight: SAR already identified patterns;              │
│  Tools VALIDATE, not discover                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: We already have SAR analysis that identifies patterns and anti-patterns. We don't need to "discover" patterns—we need to:
1. **Validate** SAR-identified patterns with tool evidence
2. **Score** validated patterns
3. **Generate** rule files

**What We Build**:

```bash
# Script 1: validate-pattern.sh
# Given a pattern description, finds evidence with ast-grep/ripgrep
./validate-pattern.sh "Repository suffix naming" --codebase ./src --output evidence.yaml

# Script 2: score-pattern.sh
# Scores pattern based on evidence
./score-pattern.sh evidence.yaml --output score.json

# Script 3: generate-rule.sh (same as Option B)
./generate-rule.sh --evidence evidence.yaml --score score.json --output rule.mdc
```

**Workflow**:
1. Human reads SAR report, identifies pattern (e.g., "All repositories end with 'Repository'")
2. Human runs `validate-pattern.sh` with pattern description
3. Script uses ast-grep to find evidence, outputs `evidence.yaml`
4. Human reviews evidence, confirms pattern is real
5. Script generates rule file from template

**Pros**:
- ✅ Leverages existing SAR work (no duplicate discovery)
- ✅ Tools validate, not discover (more reliable)
- ✅ Clear human decision points
- ✅ Incremental (1 rule at a time)

**Cons**:
- ❌ Requires SAR analysis first
- ❌ Pattern description → tool query translation may be tricky
- ❌ Not fully automated

**Build Effort**: 3-4 days
**Per-Rule Effort**: 10-20 minutes

**KISS/DRY/YAGNI Assessment**:
- KISS: ✅ Clear separation of concerns
- DRY: ✅ Reuses SAR analysis
- YAGNI: ✅ Only validates what SAR identified

---

## Recommendation Matrix

| Criterion | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| **Build Effort** | 1 day | 3-4 days | 4-5 days | 3-4 days |
| **Per-Rule Effort** | 30-60 min | 10-15 min | 2-5 min | 10-20 min |
| **Scalability** | Poor | Medium | Good | Medium |
| **Determinism** | LOW (human) | HIGH | MEDIUM (AI) | HIGH |
| **Learning Value** | HIGH | MEDIUM | LOW | MEDIUM |
| **Quality Control** | HIGH | HIGH | MEDIUM | HIGH |
| **Uses SAR** | Manual | No | Possible | Yes |
| **KISS** | ✅✅✅ | ✅✅ | ✅ | ✅✅ |
| **DRY** | ❌ | ✅✅ | ✅✅ | ✅✅✅ |
| **YAGNI** | ✅✅✅ | ✅✅ | ✅ | ✅✅ |

---

## Recommended Approach: Option D with Option B Fallback

### Rationale

1. **We already have SAR analysis** → Don't rediscover patterns (YAGNI)
2. **Tools validate, not discover** → More reliable (Determinism)
3. **Human makes pattern decisions** → Quality control preserved
4. **Scripts automate evidence collection** → DRY
5. **Fallback to Option B** if pattern not in SAR → Flexibility

### Proposed MVP Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              MVP WORKFLOW: SAR-First Rule Extraction         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  KATA L2-01: Pattern Identification                         │
│  ─────────────────────────────────────                      │
│  1. Read SAR anti-patterns report                           │
│  2. Select pattern to codify (human decision)               │
│  3. Run validate-pattern.sh to collect evidence             │
│  4. Review evidence.yaml                                    │
│  5. If evidence insufficient → mine-patterns.sh (Option B)  │
│                                                             │
│  Output: evidence.yaml with scored pattern                  │
│                                                             │
│  KATA L2-03: Rule Generation                                │
│  ─────────────────────────────────                          │
│  1. Load evidence.yaml from L2-01                           │
│  2. Run generate-rule.sh                                    │
│  3. Review generated rule.mdc                               │
│  4. Run validate-rule.sh (quality gates)                    │
│  5. Add to graph with add-to-graph.sh                       │
│                                                             │
│  Output: .cursor/rules/[id].mdc + updated rules-graph.yaml  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Scripts to Build (MVP)

| Script | Purpose | Complexity | Priority |
|--------|---------|------------|----------|
| `validate-pattern.sh` | Collect evidence for SAR pattern | Medium | P0 |
| `generate-rule.sh` | Create rule file from template | Low | P0 |
| `add-to-graph.sh` | Add rule to rules-graph.yaml | Low | P0 |
| `validate-rule.sh` | Run quality gates on rule | Low | P1 |
| `mine-patterns.sh` | Discover patterns (Option B fallback) | Medium | P1 |
| `score-pattern.sh` | Apply scoring algorithm | Medium | P2 |

**MVP Scope**: P0 scripts only (3 scripts, ~2-3 days build)

---

## MVP Script Specifications

### Script 1: validate-pattern.sh

**Purpose**: Given a pattern description from SAR, find evidence in codebase.

**Input**:
```bash
./validate-pattern.sh \
  --pattern "Classes in src/repositories end with 'Repository'" \
  --codebase ./src \
  --output evidence.yaml
```

**Algorithm**:
1. Parse pattern description → extract:
   - Directory scope (`src/repositories`)
   - Pattern type (naming convention)
   - Expected pattern (`*Repository`)
2. Generate ast-grep/ripgrep query
3. Run query, collect matches
4. Count occurrences, unique authors, date range
5. Output structured evidence

**Output** (`evidence.yaml`) - **No-Git Version**:
```yaml
pattern:
  id: "naming-001-repository-suffix"
  description: "Classes in src/repositories end with 'Repository'"
  type: naming_convention
  source: "SAR anti-patterns report"

evidence:
  query: "rg -l 'class.*Repository' src/repositories/"
  occurrences: 12
  files:
    - path: src/repositories/UserRepository.ts
      line: 5
      snippet: "export class UserRepository implements..."
    - path: src/repositories/OrderRepository.ts
      line: 3
      snippet: "export class OrderRepository {"
    # ... more files

  # Module spread (replaces author diversity for no-git)
  modules:
    - src/repositories/
    - src/domain/
    - lib/persistence/
  module_count: 3

  counter_examples:
    - path: src/repositories/UserStore.ts  # Violation
      reason: "Does not follow naming convention"

score:
  # No-Git scoring algorithm: S = 0.40F + 0.40C + 0.20L
  frequency: 0.85       # 12 occurrences, log-scaled
  criticality: 0.90     # High: naming convention affects API surface
  locality: 0.80        # 3 modules = good spread
  total: 0.86           # 0.40(0.85) + 0.40(0.90) + 0.20(0.80)

recommendation:
  include: true
  priority: P1
  confidence: HIGH
```

**Scoring Algorithm (No-Git)**:
```
S = 0.40*Frequency + 0.40*Criticality + 0.20*Locality

Where:
- Frequency (F): log10(occurrences) / log10(max_occurrences)
- Criticality (C): Manual classification (HIGH=1.0, MEDIUM=0.7, LOW=0.4)
- Locality (L): module_spread / total_modules (more spread = more team-wide)
```

**Rationale for Weight Changes**:
- Removed Stability (T) - requires git history
- Removed Author Diversity - requires git blame
- Increased Criticality weight (0.35 → 0.40) - human judgment compensates for lost signals
- Increased Frequency weight (0.30 → 0.40) - occurrence count is strongest no-git signal
- Renamed "Clarity" to "Locality" (L) - measures module spread instead of documentation

**Complexity**: Medium (pattern parsing + query generation)

### Script 2: generate-rule.sh

**Purpose**: Create rule file from evidence using Rule Template v2.

**Input**:
```bash
./generate-rule.sh \
  --evidence evidence.yaml \
  --template .cursor/rules/templates/rule-template-v2.md \
  --output .cursor/rules/naming/naming-001-repository-suffix.mdc
```

**Algorithm**:
1. Load evidence.yaml
2. Load rule template
3. Substitute placeholders:
   - `{{ID}}` → pattern.id
   - `{{CATEGORY}}` → derived from pattern.type
   - `{{PRIORITY}}` → recommendation.priority
   - `{{SCOPE}}` → from pattern directory
   - `{{DO_THIS}}` → generate from positive evidence
   - `{{DONT_DO_THIS}}` → generate from counter_examples
   - `{{VERIFICATION}}` → from evidence.query
4. Write output file

**Output**: Complete rule file in Rule Template v2 format

**Complexity**: Low (template substitution)

### Script 3: add-to-graph.sh

**Purpose**: Add rule to rules-graph.yaml with relationship detection.

**Input**:
```bash
./add-to-graph.sh \
  --rule .cursor/rules/naming/naming-001-repository-suffix.mdc \
  --graph .cursor/rules/rules-graph.yaml
```

**Algorithm**:
1. Parse rule frontmatter
2. Load existing graph
3. Check for:
   - Duplicates (same ID)
   - Conflicts (explicit `conflicts_with`)
   - Dependencies (from `related_rules`)
4. Add rule node with relationships
5. Validate graph (no cycles, all refs exist)
6. Write updated graph

**Output**: Updated rules-graph.yaml

**Complexity**: Low-Medium (graph operations)

---

## Implementation Plan (No-Git Version)

### Day 1: Foundation
- [ ] Create `validate-pattern.sh` skeleton
- [ ] Implement pattern description parser
- [ ] Implement ast-grep query generator for naming patterns
- [ ] Implement ripgrep query generator for text patterns

### Day 2: Evidence Collection (No-Git)
- [ ] Complete `validate-pattern.sh`
- [ ] Implement module spread detection (replaces author diversity)
- [ ] Implement file count/occurrence aggregation
- [ ] Test on sample patterns

### Day 3: Rule Generation
- [ ] Create `generate-rule.sh`
- [ ] Implement template loading and substitution
- [ ] Create `add-to-graph.sh`
- [ ] Implement graph validation

### Day 4: Integration & Kata
- [ ] Write Kata L2-01 (Exploratory Pattern Analysis)
- [ ] Write Kata L2-03 (Iterative Rule Extraction)
- [ ] End-to-end test: pattern discovery → rule in graph

### Day 5: Polish & Documentation
- [ ] Error handling and Jidoka blocks
- [ ] README and usage examples
- [ ] Validation scripts (P1)

**Note**: Git-based extraction (author diversity, stability scoring) has been removed.
Alternative signals: module spread, occurrence frequency, human criticality rating.

---

## No-Git Strategy: Alternative Evidence Signals

### The Challenge

Without git, we lose:
- **Who** wrote the code (author diversity)
- **When** it was written (stability/age)
- **Why** it was written that way (commit messages)
- **What** reviewers said (PR comments)

### Available Signals (No-Git)

| Signal | Source | Measurement | Replaces |
|--------|--------|-------------|----------|
| **Occurrence Count** | ast-grep/ripgrep | Files/lines matching pattern | Frequency |
| **Module Spread** | Directory analysis | How many directories contain pattern | Author diversity |
| **Structural Consistency** | ast-grep | Same AST pattern across codebase | Stability |
| **Documentation Presence** | grep | Pattern mentioned in docs/comments | Commit messages |
| **Human Classification** | Manual | Expert rates criticality | PR review signals |

### Revised Evidence Collection

**Instead of git blame for authors:**
```bash
# Module spread analysis (no git required)
rg -l 'class.*Repository' | xargs dirname | sort -u | wc -l
# Output: 5 (pattern found in 5 different directories)
```

**Instead of git log for dates:**
```bash
# File modification time (limited but available)
stat -c '%Y' src/repositories/*.ts | sort -n | head -1
# Note: Only shows LAST modification, not creation. Less reliable.
```

**Instead of git blame for author count:**
```bash
# Module ownership proxy (directories as "teams")
rg -l 'class.*Repository' | cut -d'/' -f1-2 | sort -u
# Output: src/repositories, src/domain, lib/persistence
# Assumption: Different directories ≈ different teams/areas
```

### Recommended Approach: BMAD + ast-grep

Given no-git constraint, the best fit is:

1. **BMAD document-project workflow** for initial codebase analysis
   - Scans entire codebase state
   - Generates architecture documentation
   - Identifies patterns without history

2. **ast-grep for structural pattern validation**
   - Deterministic AST matching
   - No git dependency
   - High precision

3. **Human criticality rating** for what git signals would have provided
   - Manual classification compensates for lost historical signals
   - Expert judgment on rule importance

### Evidence Quality Tiers (No-Git)

| Tier | Evidence Quality | Required Signals |
|------|------------------|------------------|
| **GOLD** | High confidence | 5+ occurrences, 3+ modules, human-rated HIGH criticality |
| **SILVER** | Medium confidence | 3+ occurrences, 2+ modules, human-rated MEDIUM+ criticality |
| **BRONZE** | Low confidence | 1-2 occurrences OR 1 module OR unrated criticality |

**Minimum for rule inclusion**: SILVER tier (was GOLD when git was available)

---

## Open Questions

1. **Pattern Description Parsing**: How flexible should the parser be?
   - Option A: Rigid format ("Files in {dir} match {pattern}")
   - Option B: Free text with AI interpretation
   - Option C: YAML input format

   **Recommendation**: Option C (YAML input) for MVP determinism

2. **Graph Storage Format**: YAML vs JSON?
   - YAML: Human-readable, comments
   - JSON: Easier parsing, wider tool support

   **Recommendation**: YAML (aligns with architecture research)

3. **Conflict Detection**: Automatic vs manual?
   - Automatic: May have false positives
   - Manual: Human specifies conflicts

   **Recommendation**: Manual for MVP (KISS)

4. **Counter-Example Collection**: How to find violations?
   - Invert the pattern query
   - Require human to specify

   **Recommendation**: Human specifies for MVP (YAGNI on auto-detection)

---

## Success Criteria for PoC

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| End-to-end works | YES | SAR pattern → rule in graph |
| Time per rule | <15 min | Stopwatch test |
| Rule quality | Passes validation | Quality gates script |
| Determinism | Same input → same output | Run twice, diff |
| Scripts work | No errors | Test on 5 patterns |

---

## Appendix: Pattern Types to Support in MVP

Based on SAR report categories:

| Pattern Type | Query Method | MVP Support |
|--------------|--------------|-------------|
| Naming conventions | ripgrep regex | ✅ Yes |
| File structure | find + glob | ✅ Yes |
| Import patterns | ast-grep | ✅ Yes |
| Class structure | ast-grep | ✅ Yes |
| Function signatures | ast-grep | ✅ Yes |
| Error handling | ast-grep | ⏳ Phase 2 |
| Test patterns | ast-grep | ⏳ Phase 2 |
| Config patterns | ripgrep | ⏳ Phase 2 |

**MVP Scope**: 5 pattern types (naming, file, import, class, function)

---

**Document Status**: Ready for Review
**Next Step**: Validate approach with stakeholder, then proceed to implementation
