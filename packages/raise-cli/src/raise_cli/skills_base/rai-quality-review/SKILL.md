---
name: rai-quality-review
description: Audit code for semantic bugs, type lies, and test muda. Use after implementation.
model: opus

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
  raise.visibility: public
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

### Instrument

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

### Step 2: Load Patterns & Design Context

Before auditing for bugs, understand what patterns should have been followed:

1. **Code orientation**: Load SA-ranked code symbols for the current branch. Use `raise_session_context` MCP tool with sections="code_context", `cwd="{project_or_worktree_path}"`.
   If MCP tools are not available, fall back to:
   ```bash
   rai session context -s code_context -p .
   ```
   Returns ~20 symbols ranked by structural proximity to active work modules. Empty result is valid. Use these as starting points — not exhaustive scope.
2. **Query the knowledge graph** for known patterns. Use `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, query="patterns for {affected_modules}".
   If MCP tools are not available, fall back to:
   ```bash
   rai graph query "patterns for {affected_modules}" --types pattern
   ```
3. **Read the design doc** (if exists) — what approach was intended?
4. **Check established patterns** (PAT-E-*) — deviations from proven patterns are a quality signal.

> **JIT**: For deeper code exploration beyond the orientation map, query the graph directly:
> ```bash
> rai graph query "symbol_name" --types symbol --limit 10
> rai graph query "module_name" --module mod-raise-cli--session
> rai graph query "callers of function_name" --types symbol
> ```
> Use `--file path/to/file.py` to scope results to a specific file.

Pattern awareness prevents false positives (flagging code that follows a deliberate pattern) and catches real issues (code that ignores a pattern established after a past bug).

### Step 2.5: Vocabulary consistency check (DDD-3, RAISE-16487)

Check symbol names in the diff against the project's domain vocabulary. Emits recommendations only — never contributes to a FAIL verdict.

```bash
# 1. Query for vocabulary terms
TERMS_JSON=$(rai graph query "" --types term --limit 50 --format json 2>/dev/null || echo '{"results":[]}')
TERM_COUNT=$(echo "$TERMS_JSON" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('results',[])))" 2>/dev/null || echo "0")

if [ "$TERM_COUNT" = "0" ]; then
  echo "ℹ Naming consistency check skipped — no domain vocabulary in graph (run rai graph build first)"
else
  # 2. Extract public symbol names from changed Python files (def/class at any indent)
  DEV_BRANCH=$(python3 -c "import yaml; print(yaml.safe_load(open('.raise/manifest.yaml'))['branches']['development'])" 2>/dev/null || echo "release/3.1.0")
  SYMBOLS=$(git diff --unified=0 "$(git merge-base HEAD "$DEV_BRANCH")"..HEAD -- '*.py' \
    | grep -E '^\+\s*(def|class)\s+\w' \
    | grep -oE '(def|class)\s+\w+' \
    | awk '{print $2}' \
    | sort -u)

  if [ -n "$SYMBOLS" ]; then
    TERMS_JSON="$TERMS_JSON" DEV_BRANCH="$DEV_BRANCH" python3 - <<'PYEOF'
import json, os, subprocess, re

terms_json = json.loads(os.environ["TERMS_JSON"])
terms = [r.get("properties", r) for r in terms_json.get("results", [])]

# Import helper — available after DDD-3 ships
try:
    from raise_cli.context.drift import detect_naming_drift
    symbols_raw = subprocess.run(
        ["git", "diff", "--unified=0",
         subprocess.run(["git", "merge-base", "HEAD", os.environ.get("DEV_BRANCH", "release/3.1.0")],
                        capture_output=True, text=True).stdout.strip(),
         "--", "*.py"],
        capture_output=True, text=True
    ).stdout
    symbols = list({
        m.group(1)
        for m in re.finditer(r"^\+\s*(?:def|class)\s+(\w+)", symbols_raw, re.MULTILINE)
    })
    findings = detect_naming_drift(symbols, terms)
    for f in findings:
        print(f)
except ImportError:
    print("ℹ drift helper not available — skipping vocabulary check")
PYEOF
  fi
fi
```

Add any findings to the **Step 6** output under a `### Naming consistency` sub-heading with severity `Recommendations`. These findings never appear in `### Critical`.

### Step 3: Semantic Correctness Audit

#### Universal Checks (all languages)

**Logic correctness:** Inverted conditionals (#1 semantic bug), off-by-one errors, wrong variable in expressions (copy-paste), unhandled edge cases (empty, null/None, zero-length).

```bash
# Re-read manifest vars (PAT-129)
_CFG=$(rai manifest env)
DRIFT_CATALOG=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('governance',{}).get('drift_catalog',''))")
```

**Agent-authored drift residue** (see `$DRIFT_CATALOG` §1 for full definitions if declared in manifest — tier-3: if absent, use inline definitions only):
- **AG3:** Unresolved symbol references — grep for calls to non-existent functions, stale imports, or type refs that never existed
- **AG5:** Auth/injection patterns in agent-authored hunks — CWE-89 (SQL injection), CWE-79 (XSS), CWE-798 (hardcoded credentials)

#### Language-Specific Checks

**Python:**
- **Type honesty:** `type: ignore` comments (each is a potential lie), `cast()` honesty, annotations claiming more specific types than runtime provides
- **Error handling:** Overly broad `except Exception`, swallowed exceptions, missing `raise X from exc`
- **Idioms:** Mutable default arguments, late binding closures in loops
- **Drift signals** (see `$DRIFT_CATALOG` §1 if declared in manifest — tier-3: if absent, use inline AG2/AG6 definitions only): duplicate logic blocks relative to adjacent modules (AG2); literal-constant conditionals matching prompt examples rather than runtime values (AG6)

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

### Step 4: Test Quality Audit

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

### Step 5: API Surface & Security Audit

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

### Step 6: Present Findings

```markdown
## Quality Review: {story_id}

### Critical (fix before merge)
### Recommended (improve code quality)
### Observations (no action needed)
### Verdict
- [ ] PASS / PASS WITH RECOMMENDATIONS / FAIL
```

Every finding: specific file:line, WHY it matters, concrete fix suggestion.

### Step 7: Write Review Artifact

The `bugfix` and `story` pipelines validate this exact file before the phase can advance — writing it is not optional (RAISE-16030). Quality review fires at `size >= S` in bugfix-enterprise, a lower threshold than architecture-review, so this is the more frequently hit scope.

Every review artifact MUST identify the exact synchronized history it reviewed.
Place these lines immediately after the `# Quality Review: {issue_key}` heading:

```markdown
Reviewed implementation: `{40-character HEAD SHA}`
Synchronized target: `{40-character target SHA}`
```

Resolve both values before reviewing. If the target is merged again or any
implementation, configuration, or skill file changes, the prior review is stale
and a new review artifact must be produced. A later same-issue QR/retro/PIR-only
commit does not change the reviewed implementation identity.

| Scope | Output path |
|-------|-------------|
| `bugfix` | `work/bugs/{issue_key}/qr.md` |
| `story` | `work/epics/e{N}-{name}/stories/s{N}.{M}-qr.md` |
| `epic` | `work/epics/e{N}-{name}/qr.md` |

Use `raise_docs_write` MCP tool with doc_type="quality-review", title="{id}: quality review", content="[Step 6 findings, verbatim]", output_path="{path from table above}", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write quality-review \
  --title "{id}: quality review" \
  --stdin \
  --output-path {path from table above} << 'EOF'
[Step 6 findings, verbatim]
EOF
```

```bash
git add {path from table above}
```

<verification>
Verdict rendered (PASS / PASS WITH RECOMMENDATIONS / FAIL). Critical findings fixed or acknowledged. Review artifact written to the scope-appropriate path and staged. Signal emitted.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Review findings | `work/bugs/{issue_key}/qr.md` (bugfix) or `work/epics/e{N}-{name}/stories/s{N}.{M}-qr.md` (story) |
| Verdict | PASS, PASS WITH RECOMMENDATIONS, or FAIL |
| Next | `/rai-story-review` (story) or `/rai-bugfix-review` (bugfix) |

## Quality Checklist

- [ ] Project language detected (Step 0) before reviewing
- [ ] Patterns and design context loaded (Step 2) before auditing
- [ ] All changed files for detected language read before reviewing
- [ ] Every finding cites specific file:line
- [ ] Artifact records exact reviewed implementation and synchronized target SHAs
- [ ] Every finding explains WHY (not just WHAT)
- [ ] Known patterns (PAT-E-*) checked — deviations flagged with justification
- [ ] Style issues already caught by language-appropriate linters are excluded
- [ ] Language-specific checks applied from correct section
- [ ] "No issues found" is a valid outcome — do not invent findings

## References

- Evidence: `work/research/quality-review/evidence-catalog.md`
- Complements: `/rai-architecture-review` (proportionality), `/rai-story-review` (retrospective)
- Research: ICSE semantic bugs (arxiv 2205.09428), Google Testing Blog, OWASP
