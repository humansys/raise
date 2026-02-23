---
name: rai-architecture-review
description: >
  Evaluate design proportionality and necessity using Beck's four rules.
  Catches what correctness gates miss: over-engineering, orphaned abstractions,
  speculative generality, and accumulated complexity. Parametrized for story
  (local) and epic (systemic) scope. Grounded in Fowler's code smells, Beck's
  simple design rules, and ESEM/ASE 2024 LLM detection research.

license: MIT

metadata:
  raise.work_cycle: story, epic
  raise.frequency: on-demand
  raise.prerequisites: story-implement (story scope), last story complete (epic scope)
  raise.distribution: internal
---

# Architecture Review

## Purpose

Evaluate whether code is **necessary and proportional** — not whether it's correct. Correctness is `/rai-quality-review`'s job. This skill asks: "Could we achieve the same outcome with less?"

**Core question:** "If we apply Beck's Rule 4 (fewest elements), what can be removed without breaking Rules 1-3 (tests, intent, no duplication)?"

**Why LLMs need specific heuristics:** Generic "check for YAGNI" prompts achieve F1 <0.40 on design smells. Specific heuristic questions are 2.54x more effective (Silva et al., ESEM 2024). This skill provides those specific questions.

## When to Use

- **Story scope:** After `/rai-story-implement`, before `/rai-story-review`
- **Epic scope:** After last story completes, before `/rai-epic-close`
- **On-demand:** When accumulated complexity feels disproportionate to delivered value

## Inputs

- **Scope:** `story` or `epic` (determines which heuristics apply and what diff to read)
- **Design doc:** `work/epics/.../design.md` or story design — provides intent context for proportionality judgment
- **Changed files:** Determined from git diff (Step 1)

## The Beck Hierarchy

All heuristics trace to Kent Beck's four rules of simple design, in priority order:

1. **Passes the tests** — automated, not our concern
2. **Reveals intention** — naming, structure clarity
3. **No duplication** — semantic, not just textual
4. **Fewest elements** — if removing it doesn't break 1-3, it shouldn't exist

YAGNI = Rule 4. DRY = Rule 3. KISS = Rules 2+4. SOLID = refinements of Rules 2-4 in OOP context. The hierarchy prevents principle conflicts: DRY (Rule 3) takes priority over KISS (Rule 4) — a justified abstraction that removes duplication stays even if it adds an element.

## Steps

### Step 1: Identify Scope and Changed Files

**Story scope:**
```bash
# Files changed in this story branch vs parent
git diff --name-only $(git merge-base HEAD epic/e{N}/{name})..HEAD -- '*.py'
```

**Epic scope:**
```bash
# All files changed in epic vs development branch
git diff --name-only $(git merge-base HEAD v2)..HEAD -- '*.py'
```

Read every changed file. Read the design doc for intent context. You cannot judge proportionality without understanding what was intended (PAT-E-187: Code as Gemba).

**Also read:** The story/epic design document. Heuristic findings without design context produce false positives.

### Step 2: Necessity Audit (YAGNI — Beck Rule 4)

For each changed file, apply these heuristics:

| # | Heuristic | Question | Red Flag |
|---|-----------|----------|----------|
| H1 | **Single Implementation** | Does any Protocol/ABC have exactly one concrete implementation? | Yes, with no documented consumer in scope or next story |
| H2 | **Wrapper Without Logic** | Does any class delegate all work to another without adding behavior? | Pure pass-through: method calls `self._inner.same_method()` and returns |
| H3 | **Unused Parameters** | Are there parameters accepted but never used in the function body? | Parameter exists "for future extensibility" |
| H4 | **Test-Only Consumers** | Is any public function/class used exclusively by test code? | `grep` across `src/` returns zero hits; only `tests/` imports it |
| H5 | **Dead Exports** | Does `__all__` include names that no consumer imports? | Export exists "for completeness" |

**Important — the justification question:** When a heuristic triggers, don't auto-flag. Ask: "Does the design doc or plan justify this?" Speculative Generality is only speculative if there's no documented consumer. If the design says "S211.4 will add a second implementation," it's intentional — note as Observation, not finding.

**Mechanical checks you can run:**
```bash
# H1: Find Protocols/ABCs with single implementation
# (read the file and count subclasses)

# H4: Check if a public symbol is imported outside tests/
# grep -r "from module import symbol" src/ --include="*.py"

# H5: Check if exported names are imported anywhere
# For each name in __all__, grep across the codebase
```

### Step 3: Proportionality Audit (KISS — Beck Rules 2+4)

| # | Heuristic | Question | Red Flag |
|---|-----------|----------|----------|
| H6 | **Indirection Depth** | How many layers between the caller and the actual work? | >2 layers of delegation for a simple operation |
| H7 | **Abstraction-to-LOC Ratio** | Is there more scaffolding (imports, class defs, type annotations) than logic? | A 50-line file with 10 lines of actual logic |
| H8 | **Configuration Over Convention** | Is something configurable that has only one valid value in practice? | Enum with one member, config param never overridden |

**The proportionality test:** Compare the complexity of the solution to the complexity of the problem. A 3-class hierarchy to dispatch 2 cases is disproportionate. A Protocol with 6 implementations serving 3 consumers is proportionate.

### Step 4: Duplication Audit (DRY — Beck Rule 3)

| # | Heuristic | Question | Red Flag |
|---|-----------|----------|----------|
| H9 | **Semantic Duplication** | Is the same concept expressed in multiple places with different code? | Two functions that transform data the same way but in different modules |
| H10 | **Pattern Duplication** | Do separate files solve the same structural problem differently? | Module A uses a registry pattern, Module B uses if/elif for the same dispatch need |

**Note:** Textual duplication (copy-paste) is usually caught by linters. Semantic duplication requires understanding intent — this is where LLM review adds value over tools.

### Step 5: Responsibility Audit (SRP — Beck Rule 2)

| # | Heuristic | Question | Red Flag |
|---|-----------|----------|----------|
| H11 | **Change Reason Count** | Would this module change for more than one unrelated reason? | File handles both parsing and persistence |
| H12 | **Import Fan-In** | Does this module import from many unrelated modules? | A file importing from 5+ distinct packages for a single function |

### Step 6: Systemic Audit (Epic Scope Only)

**Skip this step for story scope.**

These heuristics require cross-module visibility that only makes sense at epic scope:

| # | Heuristic | Question | Red Flag |
|---|-----------|----------|----------|
| H13 | **Orphaned Abstractions** | Did abstractions introduced in early stories gain consumers by epic end? | Protocol introduced in S1 still has ≤1 implementor at S7 |
| H14 | **Coupling Direction** | Do dependencies flow toward stable modules? | A stable core module imports from a volatile/new module |
| H15 | **Cyclic Dependencies** | Are there circular import paths between modules? | A→B→C→A (check with import analysis) |
| H16 | **Shotgun Surgery** | Does one logical change require modifying many files across modules? | Adding a new type touches 5+ files in 3+ directories |
| H17 | **Export Surface Growth** | Did public API grow proportionally to functionality? | `__all__` grew 3x while behavior grew 1.5x |
| H18 | **Pattern Consolidation** | Did separate stories introduce patterns that should be unified? | Two modules solve the same problem with different abstractions |

**Cyclic dependency check:**
```bash
# Quick check for circular imports at module level
python -c "
import ast, sys
from pathlib import Path
# Parse imports from changed files and build adjacency graph
# Flag cycles
"
```

**Orphaned abstraction check:**
```bash
# For each Protocol/ABC introduced in the epic:
# Count concrete implementations
# Count consumer call sites outside tests
# Flag if implementations ≤ 1 AND consumers = 0
```

### Step 7: Present Findings

Structure findings identically to `/rai-quality-review` for consistency:

```markdown
## Architecture Review: {story_id|epic_id} (scope: {story|epic})

### Evaluation Framework
Beck's Simple Design Rules applied at {story|epic} level.

### Critical (fix before merge)
- [Finding: file:line, heuristic violated, WHY it matters, suggested simplification]

### Recommended (simplify before next cycle)
- [Finding: file:line, heuristic, explanation, alternative approach]

### Questions (require human judgment)
- [Heuristic triggered but design context suggests intentionality — needs confirmation]

### Observations (patterns noted)
- [Trends, accumulations, or deferred items for future review]

### Verdict
- [ ] PASS — Design is proportional to requirements
- [ ] PASS WITH QUESTIONS — Some elements need justification
- [ ] SIMPLIFY — Unnecessary complexity should be reduced before merge
```

**Rules for findings:**
- Every finding must reference a specific file:line
- Every finding must cite which heuristic (H1-H18) triggered it
- Every finding must explain the proportionality concern (not just "this violates YAGNI")
- Every finding must suggest a concrete simplification
- **Questions are not findings.** When the design doc justifies an element but you're unsure, ask — don't flag.
- "No issues found — design is proportional" is a valid and desirable outcome

**Severity guidance:**
- **Critical:** Cyclic dependencies (H15), dead code in production path (H5), clear YAGNI with no justification (H1 without design context)
- **Recommended:** Single implementation without near-term consumer (H1 with partial justification), disproportionate abstraction (H6-H8)
- **Questions:** Anything where the design doc provides context that might justify the element

## What This Skill Does NOT Do

- Replace `/rai-quality-review` (correctness: bugs, type lies, test muda)
- Replace linters or type checkers (style and type correctness)
- Replace architecture fitness functions (automated metrics like coupling scores)
- Generate code or refactor (review only — implementation is separate)
- Override design decisions without human judgment

## Boundary with /rai-quality-review

| Concern | quality-review | architecture-review |
|---------|---------------|-------------------|
| Semantic bugs | Yes | No |
| Type honesty | Yes | No |
| Test muda | Yes | No |
| Security | Yes | No |
| YAGNI / Speculative Generality | No | Yes |
| KISS / Proportionality | No | Yes |
| DRY / Semantic duplication | No | Yes |
| Coupling / Cohesion | No | Yes |
| Orphaned abstractions | No | Yes (epic) |
| Cyclic dependencies | No | Yes (epic) |

## Quality Standards

| Metric | Target |
|--------|--------|
| Review time | <15 min (story), <30 min (epic) |
| False positive rate | <30% (design smells are inherently more subjective than correctness bugs) |
| Coverage | All changed .py files read + design doc |
| Questions ratio | >30% of findings should be Questions, not assertions (humility signal) |

## Evidence Base

This skill's heuristics are grounded in:
- **Beck**: Four rules of simple design — the universal design evaluation framework
- **Fowler**: Code smells catalog (Refactoring 2nd ed.) — Speculative Generality, Lazy Element, Middle Man, Shotgun Surgery, Divergent Change
- **Silva et al. (ESEM 2024)**: Specific prompts 2.54x more effective than generic for LLM smell detection
- **LLM smell detection (arxiv 2601.09873, 2025)**: LLMs strong on structural smells (F1 0.88), weak on design smells (F1 <0.40) — motivates concrete heuristics
- **iSMELL (ASE 2024)**: Ensemble (LLM + tools) outperforms LLM-only by 35% F1 — motivates mechanical checks alongside judgment
- **Ford**: Architecture fitness functions as automated complement
- **Empirical SE**: CBO (coupling) is reliable fault predictor; LCOM (cohesion) is NOT — focus on coupling over cohesion
- **Architectural smells evolution (ESE 2022)**: Cyclic deps grow complex through merging — early intervention critical

Full evidence catalog: `work/research/architecture-review/sources/evidence-catalog.md`

## References

- Evidence: `work/research/architecture-review/`
- Complements: `/rai-quality-review` (correctness), `/rai-story-review` (retrospective)
- Framework: Beck Design Rules, Fowler Code Smells, Ford Fitness Functions
