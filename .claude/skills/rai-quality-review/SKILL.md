---
name: rai-quality-review
description: >
  Critical code review with external auditor perspective. Catches what linters,
  type checkers, and coverage gates miss: semantic bugs, type lies, test muda,
  API design issues, and security concerns. Grounded in evidence from ICSE
  research, Google testing practices, and OWASP.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: on-demand
  raise.prerequisites: story-implement
  raise.distribution: internal
---

# Quality Review

## Purpose

Act as an external auditor reviewing code that just passed all automated gates (pyright strict, ruff, pytest, coverage). Find what the machines missed. Semantic bugs account for 51% of all missed bugs in code review (ICSE, arxiv 2205.09428) — linters catch 0% of these.

**Core question:** "If someone audits this code with an LLM, what would they find?"

## When to Use

- After `/rai-story-implement` completes and all gates pass
- Before `/rai-story-review` (catch issues before they become retrospective items)
- On-demand for any code that feels "too clean" — that's when assumptions hide

## Inputs

- Story ID (to find changed files)
- Passing gates (pyright, ruff, pytest) — prerequisite, not sufficient

## Steps

### Step 1: Identify Changed Files

```bash
# Files changed in this story (commits on current branch vs parent)
git diff --name-only $(git merge-base HEAD v2)..HEAD -- '*.py'
```

Read every changed file. You cannot review code you haven't read (PAT-E-187: Code as Gemba).

### Step 2: Semantic Correctness Audit

For each changed file, check:

**Type honesty:**
- Are there `type: ignore` comments? Each one is a potential lie. Is the ignore justified or hiding a real mismatch?
- Does any annotation claim a more specific type than the runtime provides? (e.g., annotating `Any` as `type`, `str` as `Literal`)
- Are `cast()` calls honest? Does the cast match what actually flows through at runtime?

**Logic correctness:**
- Could any conditional be inverted? (The #1 semantic bug pattern)
- Are there off-by-one risks in ranges, slices, or boundary checks?
- Is the right variable used in every expression? (Copy-paste errors with similar names)
- Are edge cases handled? Empty inputs, None, zero-length collections, missing keys

**Error handling:**
- Are exceptions too broad (`except Exception`) without justification?
- Are exceptions swallowed silently (bare `except:` or `except: pass`)?
- Is error information preserved in re-raises? (`raise X from exc`)

### Step 3: Test Quality Audit

Apply these 7 evidence-based heuristics to every test file:

| # | Heuristic | Question to ask | Red flag |
|---|-----------|-----------------|----------|
| 1 | **Mutation Survival** | "If I changed the code's behavior (flip a conditional, change a return value), would this test fail?" | Test passes regardless of code change |
| 2 | **Refactoring Resilience** | "If I refactored internals without changing the public contract, would this test break?" | Test asserts on internal calls, not behavior |
| 3 | **Behavior Specification** | "Does this test name describe a behavior (given-when-then) or a structural element (test_method_X)?" | Name mirrors code structure, not behavior |
| 4 | **Magic Literal** | "Is this assertion against a hardcoded value copied from the implementation?" | `assert len(__all__) == 21`, `assert X == "literal_from_source"` |
| 5 | **Mock Depth** | "Does the test mock more than one layer? Does mock setup encode implementation knowledge?" | Mock returns mock returns mock |
| 6 | **Deletion** | "If I deleted this test entirely, what bug could escape that no other test catches?" | No unique bug coverage |
| 7 | **Spec Independence** | "Can I write this assertion from the requirements/docstring alone, without reading the implementation?" | Assertion requires reading source to understand |

**Classify each finding:**
- **Muda** (waste): Test exists for coverage, not confidence. Recommend deletion or replacement.
- **Fragile**: Test will break on refactor. Recommend rewriting as behavior test.
- **Valuable**: Test catches real bugs. Leave as-is.

### Step 4: API Surface Audit

For any module with `__all__` or public exports:

- **Lean API**: Does `__all__` expose only what consumers need? Every export is a maintenance commitment.
- **Naming clarity**: Do public names communicate intent? Would a new developer understand what `get_pm_adapters()` returns from the name alone?
- **Internal leak**: Are `_private` functions accidentally exposed? Are implementation details leaking through type hints?
- **Backward compatibility**: Could any change break existing consumers? (relevant for published packages)

### Step 5: Security & Supply Chain Audit

For code that loads external code, handles user input, or crosses trust boundaries:

- **Entry points**: Does `ep.load()` execute arbitrary code? Is the trust model documented? (Checkmarx Oct 2024: entry points are a supply chain vector)
- **Input validation**: Is user/external input validated at the boundary?
- **Dependency trust**: Are new dependencies justified? Could they be avoided?
- **Secret exposure**: Are secrets, tokens, or credentials at risk of logging or error messages?

### Step 6: Present Findings

Structure findings as:

```markdown
## Quality Review: {story_id}

### Critical (fix before merge)
- [Finding with file:line, explanation, and fix suggestion]

### Recommended (improve code quality)
- [Finding with explanation and suggested alternative]

### Observations (no action needed)
- [Patterns noted for future reference]

### Verdict
- [ ] PASS — No critical findings
- [ ] PASS WITH RECOMMENDATIONS — Fix recommended items
- [ ] FAIL — Critical findings must be addressed
```

**Rules for findings:**
- Every finding must reference a specific file:line
- Every finding must explain WHY it matters (not just WHAT is wrong)
- Every finding must suggest a concrete fix
- Do NOT flag style issues that ruff/pyright already catch
- Do NOT add findings just to have findings — "no issues found" is a valid outcome

## What This Skill Does NOT Do

- Replace linters (ruff handles style, pyright handles types)
- Replace tests (pytest validates behavior)
- Replace the retrospective (`/rai-story-review` captures learnings)
- Generate code (this is review only — implementation is separate)

## Quality Standards

| Metric | Target |
|--------|--------|
| Review time | <15 minutes per story |
| False positive rate | <20% (findings should be actionable) |
| Coverage | All changed .py files read |

## Evidence Base

This skill's heuristics are grounded in:
- **ICSE research**: Semantic bugs = 51% of missed bugs (arxiv 2205.09428)
- **Google Testing Blog**: "Test behavior, not implementation" (2013); coverage as signal not gate (2020); mutation testing at scale (2021)
- **TDD founders**: Beck, Fowler, Cooper — convergent on behavior-based testing
- **Checkmarx**: Entry point supply chain attacks (Oct 2024)
- **testsmells.org**: 20+ cataloged test smells (Garousi et al., 166 sources)

Full evidence catalog: `work/research/quality-review/evidence-catalog.md`

## References

- Evidence: `work/research/quality-review/evidence-catalog.md`
- Complements: `/rai-story-implement` (before), `/rai-story-review` (after)
