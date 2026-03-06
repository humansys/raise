# Epic Brief: E370 — Code Beauty Standards

## Hypothesis

If we define explicit code quality standards based on what senior Python developers evaluate, create tooling to enforce them, audit our codebase against them, and iterate — then raise-commons will pass external review as professional, idiomatic, and elegant Python. The standard itself will be refined through practice, not imposed top-down.

## Success Metrics

| Metric | Target |
|--------|--------|
| Ruff expanded rules | All new rule sets pass (S, C90, PL, PERF, FURB, RET, ARG, ERA, PT, TC, A) |
| import-linter | Layer contracts defined and passing |
| Module audit | All modules reviewed against 5-dimension framework |
| Anti-patterns eliminated | Zero "AI-generated" tells in codebase |
| Governance codified | `code-standards.md` as permanent governance artifact |
| Rai identity | Code quality becomes a recognizable Rai trait |

## Appetite

Medium — 5-7 stories, iterative. Standard evolves through practice.

## Rabbit Holes

- Perfectionism: "beautiful" is subjective — define concrete, verifiable criteria
- Over-tooling: wemake + Radon + Vulture adds friction — start with Ruff expansion
- Scope creep: this is about code quality, not feature work
- Docstring completeness: coverage vs value — don't document the obvious

## Key Insight

The standard is a DRAFT until validated by auditing our own code. We learn what matters by evaluating real code, not by theorizing. The governance artifact is the OUTPUT of this epic, not the INPUT.

## Research

See `work/research/code-quality-standards/` — 24 sources, 8 triangulated claims.
