---
name: rai-architecture-review
description: Evaluate design proportionality using Beck's four rules. Use after implementation.

allowed-tools:
  - Read
  - Grep
  - Glob

license: MIT

metadata:
  raise.work_cycle: story, epic
  raise.frequency: on-demand
  raise.prerequisites: story-implement (story scope), last story complete (epic scope)
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Architecture Review

## Purpose

Evaluate whether code is **necessary and proportional** using Beck's four rules of simple design. Core question: "Could we achieve the same outcome with less?"

## Mastery Levels (ShuHaRi)

- **Shu**: Apply all heuristics systematically, explain each finding
- **Ha**: Focus on highest-signal heuristics for the scope, skip low-risk areas
- **Ri**: Pattern-match to known anti-patterns, minimal ceremony

## Context

| Condition | Action |
|-----------|--------|
| After `/rai-story-implement` | Run with `story` scope |
| After last story in epic | Run with `epic` scope |
| Accumulated complexity feels disproportionate | Run on-demand |

**Inputs:** Scope (`story` or `epic`), design doc, changed files from git diff.

## Steps

### Step 1: Identify Scope and Changed Files

Detect the project language and filter by appropriate extensions:

1. **Check `.raise/manifest.yaml`** for `project.language` or `project.project_type`
2. **Fallback:** Scan extensions of changed files and pick the dominant language

```bash
# Story scope: files changed vs parent branch
git diff --name-only $(git merge-base HEAD <parent-branch>)..HEAD -- '<extensions>'
# Epic scope: all files changed vs development branch
git diff --name-only $(git merge-base HEAD <dev-branch>)..HEAD -- '<extensions>'
```

Replace `<extensions>` with language-appropriate patterns (e.g., `'*.py' '*.pyi'` for Python, `'*.ts' '*.tsx'` for TypeScript, `'*.cs'` for C#).

Read every changed file and the design doc. You cannot judge proportionality without intent context.

### Step 2: Necessity Audit (YAGNI — Beck Rule 4)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H1 | Single Implementation | Protocol/ABC with exactly one concrete implementation, no documented consumer |
| H2 | Wrapper Without Logic | Class delegates all work without adding behavior |
| H3 | Unused Parameters | Parameters accepted but never used in function body |
| H4 | Test-Only Consumers | Public function/class used exclusively by test code |
| H5 | Dead Exports | Public API includes names no consumer imports (e.g., `__all__` in Python, `export` in TS, `public` in C#) |

When a heuristic triggers, check: "Does the design doc justify this?" If yes, note as Observation.

### Step 3: Proportionality Audit (KISS — Beck Rules 2+4)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H6 | Indirection Depth | >2 layers of delegation for a simple operation |
| H7 | Abstraction-to-LOC Ratio | More scaffolding than logic |
| H8 | Configuration Over Convention | Configurable with only one valid value in practice |

### Step 4: Duplication & Responsibility (Beck Rules 2-3)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H9 | Semantic Duplication | Same concept expressed differently in multiple places |
| H10 | Pattern Duplication | Same structural problem solved differently across modules |
| H11 | Change Reason Count | Module changes for >1 unrelated reason |
| H12 | Import Fan-In | File imports from 5+ distinct packages for one function |

### Step 5: Systemic Audit (Epic Scope Only)

Skip for story scope. Cross-module heuristics:

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H13 | Orphaned Abstractions | Protocol from early story still has ≤1 implementor at epic end |
| H14 | Coupling Direction | Stable core imports from volatile/new module |
| H15 | Cyclic Dependencies | Circular import paths between modules |
| H16 | Shotgun Surgery | One logical change touches 5+ files across 3+ directories |

### Step 6: Present Findings

```markdown
## Architecture Review: {id} (scope: {story|epic})

### Critical (fix before merge)
### Recommended (simplify before next cycle)
### Questions (require human judgment)
### Observations (patterns noted)
### Verdict
- [ ] PASS / PASS WITH QUESTIONS / SIMPLIFY
```

Every finding: specific file:line, heuristic ID, proportionality concern, concrete simplification.

## Output

| Item | Destination |
|------|-------------|
| Review findings | Presented inline, saved if requested |
| Verdict | PASS, PASS WITH QUESTIONS, or SIMPLIFY |
| Next | `/rai-story-review` (story) or `/rai-epic-close` (epic) |

## Quality Checklist

- [ ] Project language detected before filtering files
- [ ] All changed files for detected language read before reviewing
- [ ] Design doc loaded for intent context
- [ ] Every finding cites specific file:line and heuristic ID (H1-H16)
- [ ] Questions ratio >30% of findings (humility signal)
- [ ] "No issues found" is a valid outcome — do not invent findings

## References

- Evidence: `work/research/architecture-review/`
- Complements: `/rai-quality-review` (correctness), `/rai-story-review` (retrospective)
- Framework: Beck's Simple Design Rules, Fowler's Code Smells, Silva et al. (ESEM 2024)
