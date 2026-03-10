---
epic_id: "RAISE-292"
title: "TDD Policy Reform"
status: "draft"
created: "2026-02-26"
---

# Epic Brief: TDD Policy Reform

## Hypothesis
For AI-assisted development teams who follow TDD with fixed coverage gates (--cov-fail-under=90),
the TDD Policy Reform is a governance and tooling update
that replaces Goodhart-prone coverage gates with diagnostic coverage + test quality heuristics.
Unlike the current policy where agents write tautological tests to hit a number (PAT-E-444),
our solution ensures each test justifies its existence by catching real defects.

## Success Metrics
- **Leading:** Test muda ratio drops — fewer constant assertions, mock-implementation tests, and magic-number counts in new stories
- **Leading:** Modules exceeding 2x test-to-source ratio get cleaned up (session 3.2x, hooks 2.7x, context 2.6x, memory 2.4x, telemetry 2.2x, gates 2.1x)
- **Lagging:** `/rai-story-implement` skill produces tests that survive mutation (mutmut spot-checks)
- **Lagging:** Coverage stays >70% as diagnostic alarm, not gate

## Appetite
M — 4 pillars: research, governance update, skill update, module cleanup.
Research is timeboxed (1 session). Governance + skill update are S each.
Cleanup is mechanical per module (XS each, 6 modules).
Estimated ~3-4 sessions.

## Scope Boundaries
### In (MUST)
- Research SOTA testing policy for CLI frameworks / Python AI-assisted projects
- Update governance: Definition of Done, gates, guardrails with new testing guidelines
- Update `/rai-story-implement` skill to follow new TDD policy
- Clean up modules exceeding threshold: session, hooks, context, memory, telemetry, gates

### In (SHOULD)
- Evaluate mutation testing tools (mutmut, cosmic-ray) for spot-check integration
- Document test quality heuristics (what makes a good test vs muda)

### No-Gos
- Full mutation testing CI gate (too slow for current pipeline)
- Rewriting all existing tests project-wide (only modules above threshold)
- Changing pre-commit hook architecture (separate concern, RAISE-293 if needed)
- Coverage target below 70% (diagnostic floor stays)

### Rabbit Holes
- Over-engineering mutation testing integration (spot-check only, not CI gate)
- Debating pre-commit vs RaiSE gates (capture decision, don't solve both)
- Attempting to define "perfect" test taxonomy (heuristics > taxonomy)
