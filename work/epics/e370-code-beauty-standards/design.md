# Epic Design: E370 — Code Beauty Standards

## Objective

Make raise-commons pass a senior Python developer's architectural review. Not just functional — idiomatic, elegant, with deliberate design choices. The standard is distilled from practice, not imposed top-down.

**Value:** This is the gate before open source publication. Without this, the code "works but looks AI-generated." With this, a developer opens the code and sees craft.

## Gemba: Current State

### What We Have (strengths)
- **Pyright strict** — already gold standard for type safety
- **91% test coverage** — solid foundation
- **ADR-001 three-layer architecture** — clear separation (Presentation → Application → Domain → Core)
- **ADR-002 Pydantic everywhere** — runtime validation, type-safe models
- **src layout, pyproject.toml** — modern packaging
- **197 modules, 247 test files, ~95K lines** — substantial codebase

### What We're Missing
- **Ruff config is minimal** — only E, W, F, I, N, UP, B, C4, SIM. Missing security (S), complexity (C90), performance (PERF), refactoring (FURB, RET), dead code (ERA), pytest style (PT), type-checking imports (TC), builtins (A), pylint (PL), unused args (ARG)
- **No architecture enforcement** — ADR-001 defines layers but nothing prevents violations
- **No systematic audit** — never evaluated our own code against senior-review criteria
- **No code governance artifact** — standards exist in ADRs and CLAUDE.md rules but not as a unified, verifiable document

### Architecture (from ADR-001)

```
Presentation (CLI)  →  Application (Handlers)  →  Domain (Engines)
     cli/                 session/                   discovery/
     output/              context/                   graph/
                          onboarding/                gates/
                          handlers/                  doctor/
                                                     skills/
                                    ↓
                             Core (Schemas, Config)
                                  core/
                                  config/
                                  schemas/
```

**Dependency rule:** Layers only depend downward. Enforced by convention today, by import-linter after S370.2.

## 5-Dimension Review Framework

From research (24 sources, 8 triangulated claims):

| # | Dimension | What We Check | Automated? |
|---|-----------|--------------|------------|
| D1 | Correctness & Safety | Error handling, mutable defaults, resource cleanup, security | Ruff S, B; Pyright |
| D2 | Readability & Idiom | Pythonic patterns, function size, naming, modern syntax | Ruff UP, SIM, C90, FURB |
| D3 | Type Safety & API | Annotations, API surface, custom exceptions | Pyright strict |
| D4 | Architecture & Design | Layer violations, dependency direction, domain purity | import-linter |
| D5 | Collaboration | Docstrings, import organization, test quality, commit style | Ruff I, PT, ERA |

**Key insight:** D1-D2 and parts of D5 are automatable via Ruff expansion. D4 via import-linter. D3 already covered by Pyright strict. Only the "human judgment" aspects of each dimension require the audit skill.

## Stories

### S370.1: Draft Code Standard (M)

**Delivers:** `.raise/governance/code-standards-draft.md`

Concrete, verifiable criteria per dimension. Each criterion has:
- What to check (specific, not vague)
- How to verify (tool command or review checklist)
- Why it matters (source from research)

The document is explicitly DRAFT — it will evolve based on what the audit discovers.

**Depends on:** Research (done)

### S370.2: Expand Tooling Gates (M)

**Delivers:** Updated `pyproject.toml` + `import-linter` config + all violations fixed

Three changes:
1. **Ruff expansion** — add S, C90, PL, PERF, FURB, RET, ARG, ERA, PT, TC, A rule sets
2. **import-linter** — define layer contracts per ADR-001
3. **Complexity cap** — `max-complexity = 10` (McCabe)

Strategy: enable one rule set at a time, fix violations, commit. Not a big bang.

**Depends on:** S370.1 (standard defines what rules matter)

### S370.3: Code Audit Skill (M)

**Delivers:** `/rai-code-audit` skill

Purpose: systematic module-by-module evaluation against code-standards-draft.md. Produces a scorecard per module across all 5 dimensions. Focuses on what tools CAN'T catch — the human judgment layer.

What it evaluates (beyond tooling):
- D1: Error handling patterns, exception chaining quality
- D2: Domain naming, code reads like prose, Pythonic idiom usage
- D3: API surface cleanliness, `__all__` discipline
- D4: Actual layer adherence (intent, not just imports)
- D5: Test behavior-specification quality, docstring value (not just presence)

**Depends on:** S370.1 (standard to evaluate against), S370.2 (tooling catches the automatable stuff)

### S370.4: Codebase Audit (L)

**Delivers:** `work/epics/e370-code-beauty-standards/audit-results.md` — findings per module

Execute `/rai-code-audit` across all of `src/raise_cli/` and `tests/`. Group by architectural layer. Prioritize findings by dimension (D1 correctness first, D5 collaboration last).

Expected output: categorized list of findings with severity (critical / must-fix / recommended / observation).

**Depends on:** S370.3 (skill exists)

### S370.5: Refactor Critical Findings (M-L)

**Delivers:** Code changes that resolve critical and must-fix findings

Exact scope determined by S370.4 results. Likely areas:
- Functions exceeding complexity threshold
- Layer violations caught by import-linter
- Error handling improvements
- Naming improvements for domain clarity
- Test quality improvements (muda removal, specific assertions)

Each fix follows TDD — verify the finding, write a test if missing, fix, verify.

**Depends on:** S370.4 (findings exist)

### S370.6: Distill Governance (S)

**Delivers:**
- `.raise/governance/code-standards.md` (permanent, evolved from draft)
- Reconciliation with existing `/rai-quality-review` skill
- 5+ patterns captured from audit learnings
- Updated Rai identity: code quality as a defining trait

The draft becomes governance only after being validated against real code. Criteria that proved impractical are adjusted. Criteria that proved essential are strengthened.

**Depends on:** S370.5 (refactoring validates the standard)

## Dependency Graph

```
S370.1 (draft standard)
  └→ S370.2 (expand tooling)
       └→ S370.3 (audit skill)
            └→ S370.4 (codebase audit)
                 └→ S370.5 (refactor critical)
                      └→ S370.6 (distill governance)
```

Linear. Each story produces the input for the next. No parallelism possible — this is intentionally sequential because the learning from each step feeds the next.

## Done Criteria

1. All expanded Ruff rules pass on entire codebase (zero violations)
2. import-linter contracts defined per ADR-001 layers, all green
3. McCabe complexity <=10 for every function
4. Every module in `src/raise_cli/` and `tests/` audited against 5 dimensions
5. All critical and must-fix findings resolved
6. Governance artifact codified as permanent standard (not draft)
7. >=5 patterns captured from audit learnings
8. `/rai-quality-review` reconciled with new audit skill (clear roles)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Ruff expansion produces hundreds of violations | Medium | Medium | Enable one rule set at a time, fix incrementally |
| import-linter reveals deep architectural violations | Low | High | Fix in S370.5, update ADR-001 if architecture evolved |
| Audit finds "too much" to fix | Medium | Medium | Prioritize by dimension (correctness > idiom > collab) |
| Standard too rigid for future work | Low | Medium | Draft status allows evolution; governance includes escape valves |
| Scope creep into feature work | Low | High | Explicit out-of-scope boundary enforced |

## Architectural Decisions

No new ADRs needed. This epic validates and enforces existing decisions:
- **ADR-001** — Three-layer architecture (import-linter will enforce)
- **ADR-002** — Pydantic everywhere (audit will verify compliance)
- **ADR-038** — CLI ontology (bounded contexts respected)

## References

- Research: `work/research/code-quality-standards/` (24 sources, 8 triangulated claims)
- ADR-001: Three-layer architecture
- ADR-002: Pydantic for all data models
- ADR-038: CLI ontology restructuring
- Existing skill: `/rai-quality-review` (story-level, complementary)
