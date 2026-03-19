# Epic Scope: E370 — Code Beauty Standards

## Objective

Make raise-commons pass a senior Python developer's architectural review. The standard is distilled from practice — draft first, tool, audit, learn, then codify permanently.

## In Scope

- Draft code quality standard (5 dimensions, concrete verifiable criteria)
- Ruff config expansion (+11 rule sets: S, C90, PL, PERF, FURB, RET, ARG, ERA, PT, TC, A)
- import-linter with layer contracts per ADR-001 (Presentation → Application → Domain → Core)
- McCabe complexity cap (<=10 per function)
- Code audit skill (`/rai-code-audit`) for systematic module evaluation
- Full codebase audit: `src/raise_cli/` AND `tests/` (197 + 247 files)
- Refactoring for critical and must-fix findings
- Pattern capture from audit learnings (>=5 patterns)
- Governance artifact distilled from validated standard
- Reconciliation with existing `/rai-quality-review` skill

## Out of Scope

- Feature work (no new CLI commands, no new adapters)
- wemake-python-styleguide (Tier 3 — evaluate after Ruff expansion)
- Radon/Vulture (Tier 3 — defer unless Ruff proves insufficient)
- Documentation rewrite (docstrings improve as part of audit, not a separate effort)
- Performance optimization (unless flagged by PERF rules)

## Stories

| # | Story | Size | Delivers | Depends |
|---|-------|------|----------|---------|
| S370.1 | Draft Code Standard | M | `.raise/governance/code-standards-draft.md` | Research (done) |
| S370.2 | Expand Tooling Gates | M | pyproject.toml + import-linter + all violations fixed | S370.1 |
| S370.3 | Code Audit Skill | M | `/rai-code-audit` skill | S370.1, S370.2 |
| S370.4 | Codebase Audit | L | `audit-results.md` — findings per module, 5 dimensions | S370.3 |
| S370.5a | Quick Wins | S | R1-R4: re-exports, logging, move formatters, remove global | S370.4 |
| S370.5b | Extract Helpers | M | R5-R10: CLI/governance/discovery helpers, Protocol, ThreadPool, DRY | S370.5a |
| S370.5c | God Class Decomposition | L | R11: Decompose context/builder.py into loaders + orchestrator | S370.5b |
| S370.5d | Bundle Split | M | R12: Split session/bundle.py into formatters + data + assembly | S370.5b |
| S370.5e | Onboarding Cleanup | M | R13-R14: Split scaffold_skills + CLI reference to resource | S370.5b |
| S370.5f | Migrate Loaders to YAML ✓ | M | Replace markdown regex parsing with YAML sources in identity + architecture loaders | S370.5c |
| S370.6 | Distill Governance | S | Permanent governance + patterns + skill reconciliation | S370.5a-e |

```
S370.1 → S370.2 → S370.3 → S370.4 → S370.5a → S370.5b → S370.5c → S370.5f
                                                        → S370.5d  → S370.6
                                                        → S370.5e (deferred → RAISE-501)
```

S370.5a is prerequisite for all. S370.5c/d are independent after S370.5b. S370.5e deferred to RAISE-501. S370.6 closes after remaining refactoring.

## Done Criteria

1. All expanded Ruff rules pass (zero violations)
2. import-linter contracts per ADR-001 layers, all green
3. McCabe complexity <=10 for every function
4. Every module in `src/` and `tests/` audited against 5 dimensions
5. All critical and must-fix findings resolved
6. Governance artifact codified as permanent (not draft)
7. >=5 patterns captured from audit learnings
8. `/rai-quality-review` reconciled with `/rai-code-audit`
9. A senior Python developer would read this code and say: "This is well-crafted."

## Dependencies

- Research: `work/research/code-quality-standards/` (done, 24 sources)
- ADR-001: Three-layer architecture (enforced by import-linter in S370.2)
- ADR-002: Pydantic everywhere (verified in S370.4 audit)
- E369: Open source audit (done, v2.2.1 published)

## Implementation Plan

### Sequencing Strategy: Dependency-Driven + Risk-First Signal

Linear sequence — each story produces the input for the next. S370.2 (tooling) serves as the **risk-first early signal**: run Ruff expanded rules in check-only mode before fixing to dimension the real volume of work.

### Story Sequence

| Order | Story | Size | Rationale | Enables |
|-------|-------|------|-----------|---------|
| 1 | S370.1 Draft Code Standard | M | Foundation — defines what we measure | Everything else |
| 2 | S370.2 Expand Tooling Gates | M | Risk-first — reveals scale of violations, early signal for S370.5 | S370.3 (skill knows what tools cover) |
| 3 | S370.3 Code Audit Skill | M | Builds on standard + tooling — skill focuses on what tools CAN'T catch | S370.4 (execution) |
| 4 | S370.4 Codebase Audit | L | Execution — systematic evaluation, all modules | S370.5 (findings to fix) |
| 5 | S370.5 Refactor Critical | M-L | Scope determined by S370.4 findings | S370.6 (validated standard) |
| 6 | S370.6 Distill Governance | S | Closure — draft → permanent, patterns captured | Epic done |

No parallelism: intentionally sequential because learning from each step feeds the next.

### Milestones

| Milestone | Stories | Success Criteria | Decision Point |
|-----------|---------|-----------------|----------------|
| **M1: Standard + Tooling** | S370.1, S370.2 | Draft codified, Ruff expanded (0 violations), import-linter green, complexity <=10 | Reality check: how solid is our base? Volume of S370.5 becomes clear |
| **M2: Audit Complete** | S370.3, S370.4 | Skill functional, all modules audited, findings categorized by severity | Scope S370.5: exact list of critical/must-fix items |
| **M3: Beautiful Code** | S370.5, S370.6 | Findings resolved, governance permanent, >=5 patterns, skills reconciled | Ready for open source publication |

**M1 is the key checkpoint.** After M1 we know if our foundation is solid (Ruff + import-linter pass clean → refinement epic) or if we need heavy lifting (many violations → adjust S370.5 scope).

### Progress Tracking

| Story | Status | Notes |
|-------|--------|-------|
| S370.1 Draft Code Standard | done | Merged to dev |
| S370.2 Expand Tooling Gates | done | Merged to dev, 11 rule sets + import-linter |
| S370.3 Code Audit Skill | done | Merged to dev |
| S370.4 Codebase Audit | done | 28 modules, 1 critical, 24 must-fix, 14 recommendations |
| S370.5a Quick Wins | done | R1-R3 done, R4 deferred (error handler arch) |
| S370.5b Extract Helpers | done | R4-R10: 40+ helpers extracted, ContextVar, Protocol, DRY |
| S370.5c God Class Decomposition | done | R11: builder.py 1,569 → 267 lines, 7 new modules |
| S370.5d Bundle Split | done | R12: bundle.py 821 → 323 lines, 3 modules |
| S370.5e Onboarding Cleanup | deferred | R13-R14 — moved to RAISE-501 (onboarding redesign) |
| S370.5f Migrate Loaders to YAML | done | RAISE-500: YAML source of truth, MD never parsed |
| S370.6 Distill Governance | done | Standard permanent, skills reconciled, 5 patterns |

### Sequencing Risks

| Risk | Mitigation |
|------|-----------|
| S370.2 early signal shows 500+ violations → S370.5 explodes | Split S370.5 into sub-stories by dimension; prioritize D1 (correctness) |
| S370.4 audit paralysis (too many modules) | Group by architectural layer, audit layer-by-layer not file-by-file |
| S370.3 skill design wrong after seeing real audit data | Skill is a tool, not a gate — iterate the skill in S370.4 if needed |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Ruff expansion produces hundreds of violations | Medium | Medium | One rule set at a time, fix incrementally |
| import-linter reveals architectural violations | Low | High | Fix in S370.5, update ADR if architecture evolved |
| Audit finds too much to fix | Medium | Medium | Prioritize by dimension (correctness first) |
| Standard too rigid | Low | Medium | Draft → validate → codify cycle prevents rigidity |
| Scope creep into features | Low | High | Explicit boundary enforced |
