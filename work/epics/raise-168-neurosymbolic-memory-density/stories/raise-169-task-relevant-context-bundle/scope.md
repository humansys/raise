# Story Scope: RAISE-169

## Task-relevant context bundle — parametrize sections by session type

**Epic:** RAISE-168 (Neurosymbolic Memory Density)
**Size:** M
**Branch:** `story/raise-169/task-relevant-context-bundle`

## In Scope

- Define which bundle sections are relevant per session type (implement, research, debug, maintenance) and story phase (design, plan, implement, review)
- Mechanism to load only task-relevant primes instead of full fixed set
- Preserve always_on content (work state, narrative, pending) across all profiles
- Evidence: RES-MEMORY-002 (RQ2) — removing irrelevant content improves LLM performance up to 21.4%

## Out of Scope

- Changes to CLAUDE.md (already optimized in RAISE-165)
- New CLI commands or subcommands
- Session type auto-detection (deterministic identification is not viable — see design input)
- Changes to memory graph structure

## Design Input (Pre-Discussion)

**Key concern (Emilio):** Session type identification must not be assumed deterministically. The skill should ask the human what they want to focus on, then decide what context to load.

**Two approaches to evaluate in design:**
1. **Two-phase CLI call:** Phase 1 loads always_on only, skill asks focus, Phase 2 loads relevant primes
2. **Single call with selective interpretation:** Bundle loads all sections labeled, skill ignores irrelevant ones after confirming focus

**Trade-off:** Approach 1 reduces tokens sent to LLM but changes CLI interface. Approach 2 is leaner implementation but doesn't save on bundle size.

## Done Criteria

- [ ] Bundle sections parametrized by session type and/or story phase
- [ ] Session start skill asks for focus before loading context-specific primes
- [ ] always_on content preserved regardless of session type
- [ ] Measurable reduction in irrelevant primes loaded per session
- [ ] Tests pass (existing + new)
- [ ] Retrospective complete
