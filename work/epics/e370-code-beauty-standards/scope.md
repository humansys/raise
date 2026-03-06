# Epic Scope: E370 — Code Beauty Standards

## Objective

Define, enforce, and internalize Python code quality standards that make raise-commons pass a senior developer's architectural review. The standard is distilled from practice — draft first, audit, learn, then codify permanently.

## In Scope

- Draft code quality standard based on research (5 dimensions, concrete criteria)
- Ruff config expansion (security, complexity, performance, refactoring rules)
- import-linter setup with layered architecture contracts
- Quality audit skill/tooling for systematic module evaluation
- Full codebase audit against the draft standard
- Refactoring stories for findings that don't pass
- Pattern capture from audit learnings
- Final governance artifact distilled from validated standard

## Out of Scope

- Feature work (no new CLI commands, no new adapters)
- wemake-python-styleguide (Tier 3 — evaluate after Ruff expansion)
- Radon/Vulture (Tier 3 — defer unless Ruff proves insufficient)
- Documentation rewrite (docstrings improve as part of audit, not a separate effort)
- Performance optimization (unless flagged by PERF rules)

## Planned Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S370.1 | Draft Code Standard | M | Codify 5-dimension framework as `.raise/governance/code-standards-draft.md` with concrete, verifiable criteria |
| S370.2 | Expand Tooling Gates | M | Ruff rule expansion + import-linter + complexity thresholds in pyproject.toml |
| S370.3 | Quality Audit Skill | M | Create `/rai-quality-audit` skill for systematic module-by-module evaluation |
| S370.4 | Codebase Audit | L | Audit all raise-cli modules against draft standard, capture findings |
| S370.5 | Refactor: Critical Findings | M-L | Fix issues that block "senior review" bar (exact scope from S370.4) |
| S370.6 | Distill Governance | S | Evolve draft into permanent governance, capture patterns, update Rai identity |

## Done Criteria

1. All expanded Ruff rules pass on entire codebase
2. import-linter contracts defined and green
3. Every module audited against 5-dimension framework
4. Critical and must-fix findings resolved
5. Governance artifact codified as permanent standard
6. At least 5 patterns captured from audit learnings
7. A senior Python developer would read this code and say: "This is well-crafted."

## Dependencies

- Research complete: `work/research/code-quality-standards/` (done)
- E369 complete: open source audit done (done)
- On `dev` branch, v2.2.1 published (done)

## Risks

| Risk | Mitigation |
|------|-----------|
| Ruff expansion breaks existing code | Fix incrementally, one rule set at a time |
| Audit finds too many issues | Prioritize by dimension (correctness first) |
| Standard too rigid | Draft status allows evolution through practice |
| Scope creep into features | Explicit out-of-scope boundary |
