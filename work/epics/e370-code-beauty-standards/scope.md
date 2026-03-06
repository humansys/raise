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
| S370.5 | Refactor Critical | M-L | Code changes resolving critical/must-fix findings | S370.4 |
| S370.6 | Distill Governance | S | Permanent governance + patterns + skill reconciliation | S370.5 |

```
S370.1 → S370.2 → S370.3 → S370.4 → S370.5 → S370.6
```

Linear: each story produces the input for the next.

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

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Ruff expansion produces hundreds of violations | Medium | Medium | One rule set at a time, fix incrementally |
| import-linter reveals architectural violations | Low | High | Fix in S370.5, update ADR if architecture evolved |
| Audit finds too much to fix | Medium | Medium | Prioritize by dimension (correctness first) |
| Standard too rigid | Low | Medium | Draft → validate → codify cycle prevents rigidity |
| Scope creep into features | Low | High | Explicit boundary enforced |
