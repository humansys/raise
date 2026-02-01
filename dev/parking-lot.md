# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## Urgent

- [ ] **Marketing strategy** - ASAP, identify dependencies before Feb 15 launch
- [ ] **Rovo AI integration** - Required for Mar 14 webinar (Atlassian agentic dev platform)
- [ ] **V3: Rai as Commercial Offering** - Hosted Rai before Mar 14 webinar:
  - Rai = trained RaiSE agent (not generic Claude)
  - Value: accumulated judgment, calibration, collaborative intelligence
  - Integration: Jira, Confluence, Rovo Dev (Atlassian ecosystem)
  - Architecture: V2 decisions should enable V3 (session graph, memory persistence)
  - See: `.claude/rai/identity.md` for vision

---

## Ideas

### Framework Improvements

- [ ] **Session Graph Enabler Epic** - Apply E2 pattern (extract→graph→query) to session continuity:
  - Extract session concepts (outcomes, learnings, blockers, patterns)
  - Build temporal graph with momentum tracking
  - Progressive disclosure for context loading (reduce token consumption)
  - Similar to governance graph: 97% token savings potential
- [ ] Translate all katas to English (currently some in Spanish)
- [ ] Apply Lean Spec Principles to katas (after research)
- [ ] Session management for Claude Code (`raise session start/wrap`) - standardize human-AI collaboration patterns
- [ ] **Session Start Skill** (`/session-start`) - Automate grounding protocol:
  - Read RAI.md + CLAUDE.local.md + recent session logs
  - Check deadlines and blockers
  - Generate proactive greeting with suggested next steps
- [ ] **Add "test with real data" checkpoint to feature-plan kata** - After design validation, verify patterns/rules against real project data (F2.2 retro)
- [ ] **Document Pyright + Pydantic exception in guardrails.md** - `Field(default_factory=list)` false positives acceptable when Ruff passes (F2.2 retro)
- [ ] **Create ADR template for inference rule decisions** - When to be conservative vs aggressive in pattern matching (F2.2 retro)
- [ ] **Add kata-optimized estimation multiplier to planning guidance** - Apply 0.5x to estimates when using full kata cycle (F2.3 retro: 3 features at 2-3x velocity)
- [ ] **Add Python naming best practices to guardrails** - "Prefer clear names over acronyms unless universally understood" (F2.3 retro: MVCQuery→ContextQuery)
- [ ] **Document "compose, don't duplicate" architecture pattern** - Create ADR or concept doc with F2.2→F2.3 BFS reuse example (F2.3 retro)
- [ ] **Add "Simple First" concrete examples to constitution** - Keyword matching (no NLP), token heuristics; elevate from value to principle (F2.3 retro)

### Research Needed

- [ ] What are the Lean Spec Principles? How do they apply to governance artifacts?
- [x] ~~Are agent personas really needed for katas?~~ **RESOLVED** — No. See `work/research/agent-personas/` (RES-PERSONA-001)

### Governance Content Improvements (E2)

- [ ] **Refine relationship inference rules** - Based on real governance patterns discovered in F2.2 (F2.2 retro)
- [ ] **Add §N references to requirements in PRD** - Enable `governed_by` edges in concept graph (F2.2 retro)
- [ ] **Add explicit outcome keywords to requirements** - Enable `implements` edges in concept graph (F2.2 retro)
- [ ] **Consider "mentions" relationship type** - Lower confidence than `related_to` for broader semantic links (F2.2 retro)

### Future Scope (Deferred)

- [ ] MCP server for raise-cli (v2.x consideration)
- [ ] Skill audit feature for ecosystem governance (v3.0 consideration)

---

*Created: 2026-01-31*
*Last reviewed: 2026-01-31*
*Last updated: 2026-01-31 (F2.2 retrospective items added)*
