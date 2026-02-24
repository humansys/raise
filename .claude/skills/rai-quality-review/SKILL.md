---
name: rai-quality-review
description: >
  Critical code review with external auditor perspective. Catches what linters,
  type checkers, and coverage gates miss: semantic bugs, type lies, test muda,
  API design issues, and security concerns.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: on-demand
  raise.prerequisites: story-implement
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Quality Review

## Purpose

Act as an external auditor reviewing code that passed all automated gates. Find what the machines missed — semantic bugs account for 51% of all missed bugs in code review (ICSE, arxiv 2205.09428).

## Mastery Levels (ShuHaRi)

- **Shu**: Apply all audit categories systematically, explain each finding
- **Ha**: Focus on highest-risk areas (type honesty, test muda), skip low-risk
- **Ri**: Pattern-match to known vulnerability classes, minimal ceremony

## Context

| Condition | Action |
|-----------|--------|
| After `/rai-story-implement`, all gates pass | Run quality review |
| Before `/rai-story-review` | Catch issues before retrospective |
| Code feels "too clean" | Assumptions may be hiding — review |

**Inputs:** Story ID (to find changed files), passing gates (pyright, ruff, pytest).

## Steps

### Step 1: Identify Changed Files

```bash
git diff --name-only $(git merge-base HEAD v2)..HEAD -- '*.py'
```

Read every changed file. You cannot review code you haven't read.

### Step 2: Semantic Correctness Audit

**Type honesty:** Check `type: ignore` comments (each is a potential lie), `cast()` honesty, annotations claiming more specific types than runtime provides.

**Logic correctness:** Inverted conditionals (#1 semantic bug), off-by-one in ranges/slices, wrong variable in expressions (copy-paste), unhandled edge cases (empty, None, zero-length).

**Error handling:** Overly broad `except Exception`, swallowed exceptions, missing `raise X from exc`.

### Step 3: Test Quality Audit

Apply these heuristics to every test file:

| # | Heuristic | Red Flag |
|---|-----------|----------|
| 1 | Mutation Survival | Test passes regardless of code behavior change |
| 2 | Refactoring Resilience | Test asserts on internals, not behavior |
| 3 | Behavior Specification | Name mirrors code structure, not behavior |
| 4 | Magic Literal | Assertion against hardcoded value from implementation |
| 5 | Mock Depth | Mock returns mock returns mock |
| 6 | Deletion | No unique bug coverage if test deleted |
| 7 | Spec Independence | Assertion requires reading source to understand |

Classify: **Muda** (waste, recommend deletion) / **Fragile** (breaks on refactor) / **Valuable** (leave as-is).

### Step 4: API Surface & Security Audit

**API:** Lean `__all__`, clear naming, no internal leaks, backward compatibility.

**Security:** Entry point trust model, input validation at boundaries, dependency justification, no secret exposure in logs/errors.

### Step 5: Present Findings

```markdown
## Quality Review: {story_id}

### Critical (fix before merge)
### Recommended (improve code quality)
### Observations (no action needed)
### Verdict
- [ ] PASS / PASS WITH RECOMMENDATIONS / FAIL
```

Every finding: specific file:line, WHY it matters, concrete fix suggestion.

## Output

| Item | Destination |
|------|-------------|
| Review findings | Presented inline, saved if requested |
| Verdict | PASS, PASS WITH RECOMMENDATIONS, or FAIL |
| Next | `/rai-story-review` |

## Quality Checklist

- [ ] All changed .py files read before reviewing
- [ ] Every finding cites specific file:line
- [ ] Every finding explains WHY (not just WHAT)
- [ ] Style issues already caught by ruff/pyright are excluded
- [ ] "No issues found" is a valid outcome — do not invent findings

## References

- Evidence: `work/research/quality-review/evidence-catalog.md`
- Complements: `/rai-architecture-review` (proportionality), `/rai-story-review` (retrospective)
- Research: ICSE semantic bugs (arxiv 2205.09428), Google Testing Blog, OWASP
