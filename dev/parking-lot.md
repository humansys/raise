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
  - **From OpenClaw research (RES-OPENCLAW-001):**
    - [x] ~~Pre-compaction memory flush~~ **→ E3** (F3.5 /session-close flush)
    - [ ] Gateway abstraction — single control plane for multi-interface (Jira, Rovo, CLI, MCP)
    - [ ] Typed kata execution — Lobster-inspired pipelines with approval gates + resume tokens
    - [ ] Token monitoring — track session context usage, trigger flush at soft threshold
    - [ ] Hybrid skills — markdown process + JSON schema + validation code

---

## Ideas

### Framework Improvements

- [ ] **Post-Session Alignment Skill** (`/align-docs`) - After strategic sessions, auto-update docs:
  - Generate ADRs from decisions made
  - Update vision/architecture docs
  - Sync CLAUDE.md with new patterns
  - Could be triggered by `/session-close` for ideation/research sessions
  - Note: Doing manually now (2026-02-01) for quality; automate later
- [x] ~~**Identity Core Implementation**~~ **→ PROMOTED to E3** - See `dev/epic-e3-scope.md`
  - `.rai/` with identity/, memory/, relationships/, growth/
  - JSONL + Graph for memory (MVC pattern from E2)
  - ADR-013, ADR-014, ADR-015 define architecture
- [x] ~~**Session Graph Enabler Epic**~~ **→ ADDRESSED by E3** - Memory Graph (F3.3)
  - Same pattern: extract→graph→query for memory
  - JSONL storage + concept graph + BFS traversal
  - Reuses E2 infrastructure
- [ ] Translate all katas to English (currently some in Spanish)
- [ ] Apply Lean Spec Principles to katas (after research)
- [ ] Session management for Claude Code (`raise session start/wrap`) - standardize human-AI collaboration patterns
- [x] ~~**Session Start Skill** (`/session-start`)~~ **RESOLVED** — Already exists at `.claude/skills/session-start/`
  - Loads memory, analyzes progress, proposes session goal
  - Used at start of this session
- [ ] **Add "test with real data" checkpoint to feature-plan kata** - After design validation, verify patterns/rules against real project data (F2.2 retro)
- [ ] **Document Pyright + Pydantic exception in guardrails.md** - `Field(default_factory=list)` false positives acceptable when Ruff passes (F2.2 retro)
- [ ] **Create ADR template for inference rule decisions** - When to be conservative vs aggressive in pattern matching (F2.2 retro)
- [ ] **Add kata-optimized estimation multiplier to planning guidance** - Apply 0.5x to estimates when using full kata cycle (F2.3 retro: 3 features at 2-3x velocity)
- [ ] **Add Python naming best practices to guardrails** - "Prefer clear names over acronyms unless universally understood" (F2.3 retro: MVCQuery→ContextQuery)
- [ ] **Document "compose, don't duplicate" architecture pattern** - Create ADR or concept doc with F2.2→F2.3 BFS reuse example (F2.3 retro)
- [ ] **Add "Simple First" concrete examples to constitution** - Keyword matching (no NLP), token heuristics; elevate from value to principle (F2.3 retro)

### Research Needed

- [ ] What are the Lean Spec Principles? How do they apply to governance artifacts? **← In progress (subagent researching for /epic-design skill)**
- [x] ~~Are agent personas really needed for katas?~~ **RESOLVED** — No. See `work/research/agent-personas/` (RES-PERSONA-001)
- [x] ~~OpenClaw/Moltbot architecture patterns for V3~~ **RESOLVED** — See `work/research/openclaw-architecture/` (RES-OPENCLAW-001)

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
*Last reviewed: 2026-02-01*
*Last updated: 2026-02-01 (E3 promotions: Identity Core, Session Graph, Pre-compaction flush; Session Start resolved)*
