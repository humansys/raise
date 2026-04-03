---
name: rai-quality-review
description: Audit code for semantic bugs, type lies, and test muda. Use after implementation.

allowed-tools:
  - Read
  - Grep
  - Glob

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

**Inputs:** Story ID (to find changed files), passing gates (language-appropriate linters, type checkers, test runners).

## Steps

### Step 0: Detect Project Language

Determine the primary language and toolchain using this priority chain:

1. **Check `.raise/manifest.yaml`** for explicit overrides (`project.test_command`, `project.lint_command`, `project.type_check_command`) — configuration over convention
2. **Detect language** from `project.project_type` in manifest, or scan extensions of changed files (`git diff --name-only`)
3. **Map language to defaults** using the table below

```yaml
# .raise/manifest.yaml — example overrides
project:
  test_command: "npm run test:ci"       # overrides Test Runner column
  lint_command: "biome check"           # overrides Linter column
  type_check_command: "tsc --noEmit"    # overrides Type Checker column
```

Manifest commands always win when present. The table is a **fallback**:

| Language | Extensions | Type Checker | Linter | Test Runner |
|----------|-----------|--------------|--------|-------------|
| Python | `.py`, `.pyi` | pyright/mypy | ruff | pytest |
| TypeScript | `.ts`, `.tsx` | tsc --noEmit | eslint | jest/vitest |
| JavaScript | `.js`, `.jsx` | — | eslint | jest/vitest |
| C# | `.cs` | dotnet build | dotnet format | xunit/nunit |
| Java | `.java` | javac | checkstyle | JUnit |
| Go | `.go` | go vet | golangci-lint | go test |
| PHP | `.php` | phpstan | php-cs-fixer | phpunit |
| Dart | `.dart` | dart analyze | dart fix | flutter test |

If mixed languages, review each language group separately using its section below.

### Step 1: Identify Changed Files

```bash
# Use the parent branch (epic or dev) as merge base — not a hardcoded branch name
git diff --name-only $(git merge-base HEAD <parent-branch>)..HEAD -- '<extensions>'
```

Replace `<extensions>` with language-appropriate patterns from Step 0 (e.g., `'*.py' '*.pyi'` for Python, `'*.ts' '*.tsx'` for TypeScript).

Read every changed file. You cannot review code you haven't read.

### Step 2: Semantic Correctness Audit

#### Universal Checks (all languages)

**Logic correctness:** Inverted conditionals (#1 semantic bug), off-by-one errors, wrong variable in expressions (copy-paste), unhandled edge cases (empty, null/None, zero-length).

#### Language-Specific Checks

**Python:**
- **Type honesty:** `type: ignore` comments (each is a potential lie), `cast()` honesty, annotations claiming more specific types than runtime provides
- **Error handling:** Overly broad `except Exception`, swallowed exceptions, missing `raise X from exc`
- **Idioms:** Mutable default arguments, late binding closures in loops

**TypeScript/JavaScript:**
- **Type honesty:** `as` type assertions (bypasses type checking), `any` types (defeats type safety), `@ts-ignore`/`@ts-expect-error` comments
- **Error handling:** Unhandled promise rejections, missing `.catch()`, overly broad `catch(e)` without type narrowing
- **Idioms:** `==` vs `===`, truthiness traps (`0`, `""`, `[]` are falsy), implicit `any` from untyped imports

**C#/.NET:**
- **Type honesty:** Null-forgiving operator `!` (suppresses null warnings), unchecked casts vs pattern matching, `dynamic` type usage
- **Error handling:** Empty `catch` blocks, catching `System.Exception` broadly, missing `using`/`await using` for `IDisposable`
- **Idioms:** `async void` methods (fire-and-forget), missing `ConfigureAwait`, LINQ deferred execution surprises

**PHP:**
- **Type honesty:** Missing type declarations, `@` error suppression operator, loose comparison (`==` vs `===`)
- **Error handling:** Silenced errors, missing null checks on database results
- **Idioms:** Uninitialized properties, reference parameter side effects

**Go:**
- **Type honesty:** Unchecked type assertions (use comma-ok pattern), interface satisfaction without tests
- **Error handling:** Ignored error returns (`_`), error wrapping without `%w`
- **Idioms:** Goroutine leaks, unbuffered channel deadlocks, deferred close on writable resources

**Dart/Flutter:**
- **Type honesty:** `as` casts without `is` checks, `dynamic` type usage, `!` null assertion operator
- **Error handling:** Uncaught `Future` errors, missing error handling in `StreamBuilder`
- **Idioms:** `setState` after dispose, missing `const` constructors, build method side effects

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

**API (language-adaptive):**

| Language | Visibility Mechanism | Leak Detection |
|----------|---------------------|----------------|
| Python | Lean `__all__`, `_`-prefixed internals | Internal symbols in public API |
| TypeScript | `export` discipline, barrel files | Re-exporting internals, `export *` |
| C# | `internal` vs `public`, `[assembly: InternalsVisibleTo]` | Public types that should be internal |
| Go | Capitalization (exported vs unexported) | Exported helpers that should be internal |
| PHP | `private`/`protected` vs `public` | Public methods that should be protected |
| Dart | `_`-prefixed private, `export` directives | Part-of files leaking implementation |

**Security (universal):** Entry point trust model, input validation at boundaries, dependency justification, no secret exposure in logs/errors.

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

- [ ] Project language detected (Step 0) before reviewing
- [ ] All changed files for detected language read before reviewing
- [ ] Every finding cites specific file:line
- [ ] Every finding explains WHY (not just WHAT)
- [ ] Style issues already caught by language-appropriate linters are excluded
- [ ] Language-specific checks applied from correct section
- [ ] "No issues found" is a valid outcome — do not invent findings

## References

- Evidence: `work/research/quality-review/evidence-catalog.md`
- Complements: `/rai-architecture-review` (proportionality), `/rai-story-review` (retrospective)
- Research: ICSE semantic bugs (arxiv 2205.09428), Google Testing Blog, OWASP
