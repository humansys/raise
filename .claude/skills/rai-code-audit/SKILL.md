---
name: rai-code-audit
description: Audit modules against code-standards.md for naming, idioms, and API design.

allowed-tools:
  - Read
  - Grep
  - Glob

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: on-demand
  raise.prerequisites: code-standards.md exists, S370.2 tooling gates passing
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Code Audit

## Purpose

Systematically evaluate the raise-commons codebase against the code quality standard (`.raise/governance/code-standards.md`), focusing on the 26 criteria that require human judgment (HUMAN and BOTH classifications). TOOL-only criteria are already enforced by Ruff, Pyright, and import-linter gates from S370.2.

This skill complements `/rai-quality-review` (story-scoped, changed-files focus) and `/rai-architecture-review` (proportionality and necessity focus) by providing a governance-standard-driven, codebase-wide audit.

## Mastery Levels (ShuHaRi)

- **Shu**: Evaluate every module against all 26 criteria systematically. Full scorecard.
- **Ha**: Focus on dimensions most relevant to each layer (e.g., D4 Architecture for Domain modules, D3 API for Core modules). Skip criteria unlikely to apply.
- **Ri**: Pattern-match across modules, identify systemic issues, minimal per-file ceremony.

## Context

**When to use:**
- After completing all stories in an epic, before epic close
- When onboarding a new code standard and validating existing code against it
- Periodic codebase health check (quarterly or after major refactors)

**When to skip:**
- For story-level review of changed files only (use `/rai-quality-review` instead)
- For architecture proportionality and necessity (use `/rai-architecture-review` instead)
- When TOOL-only gates are not yet passing (fix tooling first via S370.2)

**Inputs required:**
- Module path(s) to audit, or "all" for full codebase
- `.raise/governance/code-standards.md` (the evaluation reference)

**Output:**
- Per-module scorecard (pass/partial/fail per dimension)
- Aggregated summary report with findings by severity

## Steps

### Step 1: Define Scope

Determine which modules to audit.

**If input is specific module path(s):**
- Confirm each path exists under `src/raise_cli/`
- Identify the ADR-001 layer for each module

**If input is "all":**
- Enumerate all modules in `src/raise_cli/` grouped by ADR-001 architectural layer:

| Layer | Modules |
|-------|---------|
| **Presentation** | `cli/`, `output/` |
| **Application** | `session/`, `context/`, `onboarding/`, `handlers/`, `publish/` |
| **Domain** | `discovery/`, `graph/`, `gates/`, `doctor/`, `skills/`, `governance/`, `memory/`, `telemetry/`, `adapters/`, `mcp/`, `backlog/`, `hooks/` |
| **Core** | `core/`, `config/`, `schemas/`, `rai_base/` |

```bash
# List all Python modules under src/raise_cli/
ls -d src/raise_cli/*/
```

**Verification:** Target module list is complete and each module is assigned to a layer.

> **If you can't continue:** Check `src/raise_cli/` for any new modules not in the layer table. Assign them to the closest layer and note the gap.

### Step 2: Load Standards Reference

Read `.raise/governance/code-standards.md` as the evaluation reference.

**Focus on HUMAN and BOTH criteria only.** TOOL-only criteria (11 total) are already enforced by automated gates and should be skipped:

**TOOL-only (skip these):**
- D1.4 (mutable defaults — B006), D1.5 (return consistency — RET), D1.6 (security — S rules)
- D2.8 (modern syntax — UP rules)
- D3.1 (annotations — Pyright strict), D3.4 (explicit Optional — Pyright+UP007), D3.5 (no Any — Pyright strict)
- D4.1 (dependency direction — import-linter), D4.8 (layer contracts — import-linter)
- D5.2 (import organization — I+F401), D5.5 (pre-commit hooks — CI)

**HUMAN criteria to evaluate (15):**
- D1.7: Thread safety awareness
- D2.2: Data model usage (dunder methods)
- D2.3: Standard library collections
- D2.5: Nesting depth (max 3 levels)
- D2.6: Domain naming (no generic names)
- D2.7: Comments explain WHY
- D3.2: Abstract parameter types
- D3.6: Flat API surface
- D3.7: Custom exception hierarchy
- D3.8: Pydantic for data models
- D4.3: Testability by design
- D4.4: Single responsibility
- D4.5: Composition over inheritance
- D4.6: Declarative over imperative
- D5.6: Dependency justification

**BOTH criteria — evaluate the human-judgment portion (11):**
- D1.1: Exception broadness — check that `except Exception:` is justified and logged (E722 bare except already caught by Ruff)
- D1.2: Exception chaining completeness — check for missing `raise X from Y` beyond what B904 catches
- D1.3: Custom resource review — check that custom resources implement `__enter__`/`__exit__` (SIM115 catches basic `open()`)
- D2.1: Idiom completeness — check for index-manipulation patterns that C4/SIM rules miss
- D2.4: Function line count — check functions under complexity threshold but over 40 lines (C901 catches complexity)
- D3.3: Return type concreteness — check for overly abstract return types (Pyright enforces presence)
- D4.2: Domain purity — check for I/O via function calls in domain modules (import-linter catches import-level violations)
- D4.7: Global mutable state judgment — check for acceptable exceptions like PAT-E-589 test seams (PLW catches some patterns)
- D5.1: Docstring quality — check content quality and completeness (D rules check presence)
- D5.3: Test assertion quality and naming — check specificity and behavior-spec names (PT rules + coverage are TOOL)
- D5.4: Commit granularity — check that commits represent one logical change (message format is TOOL)

Also apply **Appendix A: AI-Generated Code Tells** as additional checks:
- A1: Excessive obvious comments
- A2: Generic names without domain language
- A3: Old typing syntax (also caught by UP rules, but check for edge cases)
- A4: Monolithic functions
- A5: Vague test assertions
- A6: Suspiciously uniform structure

**Verification:** All 26 HUMAN/BOTH criteria listed. All 11 TOOL-only criteria marked as skip.

### Step 3: Evaluate Per Module Group

For each layer group (Presentation, Application, Domain, Core), evaluate each module:

1. **Read all `.py` files** in the module directory
2. **For each applicable criterion** from Step 2:
   - Check the specific "What" from code-standards.md
   - For BOTH criteria, evaluate only the human-judgment portion (the tool portion is already passing)
   - Record findings with:
     - **Criterion ID** (e.g., D2.6)
     - **File:line** (specific location)
     - **Severity:** one of:
       - `critical` — correctness or safety risk, must fix before merge
       - `must-fix` — violates standard with clear fix available
       - `recommended` — improves quality, judgment call on timing
       - `observation` — pattern noted, no immediate action needed
     - **Description** — what was found and why it matters
     - **Suggested fix** — concrete remediation
3. **Note exemplary code** — not just problems. Capture what the module does well as positive examples for other modules.

**Layer-specific emphasis:**

| Layer | Primary Focus | Secondary Focus |
|-------|--------------|-----------------|
| Presentation | D2 (naming, comments), D5 (docstrings) | D3 (API surface) |
| Application | D4 (architecture, responsibility), D1 (error handling) | D2 (readability) |
| Domain | D4 (purity, testability), D3 (types, Pydantic) | D1 (correctness) |
| Core | D3 (API surface, types), D4 (no mutable state) | D5 (docstrings) |

**Verification:** Every module has been read. Findings cite specific file:line. Both problems and exemplary code are recorded.

> **If you can't continue:** If a module is too large to read in one pass, split by file and track progress. Ensure no file is skipped.

### Step 4: Produce Scorecard

Generate a scorecard for each audited module:

```markdown
### Module: {module_name} ({layer})

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass/partial/fail | {count} findings |
| D2 Readability | pass/partial/fail | {count} findings |
| D3 Types & API | pass/partial/fail | {count} findings |
| D4 Architecture | pass/partial/fail | {count} findings |
| D5 Collaboration | pass/partial/fail | {count} findings |

**Exemplary:** {what this module does well}

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 1 | D2.6 | must-fix | config/paths.py:42 | Generic name `data` | Rename to `config_data` |
```

**Verdict rules:**
- **pass:** 0 critical or must-fix findings in the dimension
- **partial:** 0 critical, 1+ must-fix findings
- **fail:** 1+ critical findings

**Verification:** Every module has a scorecard. Verdicts follow the rules above.

### Step 5: Aggregate Summary

Produce the final audit summary report:

```markdown
## Code Audit Summary

**Date:** {date}
**Scope:** {modules audited}
**Standard:** code-standards.md v{version}
**Criteria evaluated:** 26 (15 HUMAN + 11 BOTH)

### Layer Summary

| Layer | Modules | Pass | Partial | Fail |
|-------|---------|------|---------|------|
| Presentation | {n} | {n} | {n} | {n} |
| Application | {n} | {n} | {n} | {n} |
| Domain | {n} | {n} | {n} | {n} |
| Core | {n} | {n} | {n} | {n} |

### Critical Findings ({count})

{List each critical finding with module, criterion, and description}

### Must-Fix Findings ({count})

{List each must-fix finding with module, criterion, and description}

### Top Patterns (recurring issues)

{Identify issues that appear across multiple modules — these indicate systemic problems
worth addressing with a dedicated story rather than module-by-module fixes}

### Exemplary Code (what's done well)

{Highlight modules or patterns that other modules should emulate}

### Recommendations

{Prioritized list of suggested remediation actions, grouped by effort}
```

**Verification:** Summary totals match individual scorecards. Patterns are identified across modules, not just listed per-module.

## Output

| Item | Destination |
|------|-------------|
| Per-module scorecards | Audit report artifact |
| Aggregated summary | Audit report artifact |
| Critical/must-fix findings | Input to remediation stories |
| Next skill | `/rai-story-close` or remediation planning |

## Quality Checklist

- [ ] All target modules identified and assigned to ADR-001 layers
- [ ] `code-standards.md` read as evaluation reference
- [ ] All 26 HUMAN/BOTH criteria referenced during evaluation
- [ ] All 11 TOOL-only criteria explicitly skipped
- [ ] Every finding cites specific file:line
- [ ] Every finding includes criterion ID, severity, description, and fix
- [ ] Exemplary code noted (not just problems)
- [ ] Appendix A (AI tells) checked
- [ ] Scorecard verdicts follow pass/partial/fail rules
- [ ] Summary aggregation matches individual scorecards
- [ ] Systemic patterns identified across modules

## References

- **Standard:** `.raise/governance/code-standards.md` (37 criteria, 5 dimensions)
- **Architecture:** `dev/decisions/adr-001-three-layer-architecture.md` (layer model)
- **Data models:** `dev/decisions/adr-002-pydantic-everywhere.md` (Pydantic mandate)
- **Complements:** `/rai-quality-review` (story-scoped correctness), `/rai-architecture-review` (proportionality)
- **Tooling gates:** S370.2 (Ruff, Pyright, import-linter enforce TOOL-only criteria)
