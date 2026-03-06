# Research: Python Code Quality Standards

**Question:** What criteria does a senior Python developer use to evaluate code quality, architecture, and elegance?

**Decision:** Code governance for raise-commons before open source publication.

**Date:** 2026-03-06

## Contents

- `code-quality-standards-report.md` — Synthesized report with 5-dimension framework and recommendations
- `sources/evidence-catalog.md` — 24 sources, 8 triangulated claims with confidence ratings

## Key Findings

1. Senior review evaluates 5 dimensions: Correctness, Readability/Idiom, Type Safety/API, Architecture, Collaboration
2. Ruff expansion (zero new deps) + import-linter (one new dep) covers most automated enforcement
3. Pyright strict (already enabled) is the gold standard — we're ahead here
4. "Beautiful" code = Zen-compliant + idiomatically Python + architecturally sound + tooling-verified + human-reviewed
