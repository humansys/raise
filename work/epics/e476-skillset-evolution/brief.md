---
epic_id: "E476"
title: "Skillset Evolution: raise-dev + Language-Agnostic Standards"
status: "draft"
created: "2026-03-06"
---

# Epic Brief: Skillset Evolution

## Hypothesis
For developers using RaiSE on non-Python projects who need consistent governance workflows,
the skillset system is a composable layer
that delivers language-specific tooling without coupling core skills to any single stack.
Unlike the current state where skills hardcode `pytest`, `ruff`, `pyright`,
our solution uses a `raise-dev` skillset for Python-specific gates and keeps standard skills language-agnostic.

## Success Metrics
- **Leading:** Skills reference gate commands via variables/config, not hardcoded tool names
- **Lagging:** A non-Python project (e.g. TypeScript) can use RaiSE skills without editing skill files

## Appetite
M — 5-7 stories

## Scope Boundaries
### In (MUST)
- Create `raise-dev` skillset with Python-specific gate configuration (pytest, ruff, pyright)
- Make core skills (implement, bugfix, story-close) language-agnostic — reference gates by role (test, lint, typecheck), not by tool name
- Skills invoke gates before merge via configurable commands

### In (SHOULD)
- Provide a `raise-dev-ts` example skillset for TypeScript (vitest, eslint, tsc)
- Document how to create custom skillsets for other stacks

### No-Gos
- Full multi-language CI/CD integration — that's a separate concern
- Rewriting all 36 skills — only touch skills that hardcode language-specific commands
- Runtime language detection to auto-select skillset — explicit configuration preferred

### Rabbit Holes
- Over-engineering a plugin system for gate commands — simple config file is enough
- Trying to support every possible test runner/linter combination upfront
