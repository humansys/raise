# E-ANTHROPIC: Scope & Research Design

> RAISE-789 — Systematic benchmarking of Anthropic's published agent patterns against RaiSE's architecture.

## Objective

Evaluate Anthropic's 9 published articles (Dec 2024 — Mar 2026) through RaiSE's lens:
- What do we already have that maps to their recommendations?
- What are we missing that would strengthen our core value proposition?
- What do they recommend that conflicts with our principles?
- What should we adopt, adapt, or deliberately reject?

## Evaluation Criteria

Every gap is scored on 4 RaiSE-native dimensions:

| Dimension | Question | Scale |
|-----------|----------|-------|
| **Value to Core** | Does this strengthen memory, methodology, or entity (the moat)? | 0-3 |
| **Simplicity Cost** | How much complexity does adoption add? (lower = better) | 0-3 |
| **Observability Gain** | Does this make work more traceable/auditable? | 0-3 |
| **Adoption Effort** | Story points estimate for implementation | XS/S/M/L/XL |

**Priority formula:** `(Value to Core + Observability Gain) - Simplicity Cost`
- Score 4-6: Do now (release 2.4.0)
- Score 1-3: Plan for enterprise (E9)
- Score 0 or negative: Reject or defer indefinitely

## Source Articles

| # | Article | Date | Key Patterns |
|---|---------|------|-------------|
| Art.1 | Building Effective Agents | Dec 2024 | Augmented LLM, workflow patterns, agent loops |
| Art.2 | Effective Harnesses for Long-Running Agents | Nov 2025 | Checkpointing, test oracles, feature verification |
| Art.3 | Harness Design for Long-Running Apps | Mar 2026 | Evaluator-generator, iterative loops, grading |
| Art.4 | Effective Context Engineering | Sep 2025 | Compaction, context windows, MVC |
| Art.5 | Writing Tools for Agents | Sep 2025 | Tool descriptions, progressive disclosure |
| Art.6 | Multi-Agent Research System | Jun 2025 | Orchestrator-worker, effort scaling, specialization |
| Art.7 | Building a C Compiler with Parallel Claudes | Feb 2026 | File-lock, bare-git, parallel coordination |
| Art.8 | Claude Code Best Practices | Apr 2025 | CLAUDE.md, context priming, command patterns |
| Art.9 | Code Execution with MCP | Nov 2025 | Code-mode tools, sandbox execution |

## Gap Mapping Against RaiSE Blueprint

### EVALUATION domain (5 gaps)

| Gap | Anthropic Says | RaiSE Has Today | Delta | Blueprint Ref |
|-----|---------------|-----------------|-------|--------------|
| **G1: Interactive evaluator** | Use Playwright MCP for visual verification of agent output | `rai gate check` (code gates only). No visual/interactive verification | **Missing capability** — but RaiSE is CLI-first, not UI-first. Relevance depends on target users | G-EVAL-1 |
| **G2: Calibrated grading** | Scoring rubrics + few-shot examples for consistent evaluation | Binary pass/fail gates. No scoring, no rubrics, no few-shot calibration | **Design gap** — our gates are rigorous but coarse. Scoring would improve AR/QR skills | G-EVAL-2 |
| **G3: Iterative eval loop** | Run evaluator N rounds until quality threshold met | Single-pass gate check. No retry-with-feedback loop | **Missing pattern** — aligns with Kaizen but we don't do it programmatically | G-EVAL-3 |
| **G5: Feature verification checklist** | Checklist as test oracle — verify each feature exists and works | Story AC exist but aren't used as automated oracle | **Partial** — we have AC in story design, gap is connecting them to automated verification | G-EVAL-4 |
| **G13: Contract negotiation** | Evaluator and generator negotiate sprint scope before work | No equivalent. Planning is human-driven via /rai-story-plan | **Philosophical question** — do we want agent-to-agent negotiation? RaiSE says "humans define" | G-EVAL-5 |

**Research questions for RAISE-790:**
1. How do Anthropic's evaluation patterns compare to RaiSE's gate system? Where are gates sufficient and where do we need scoring?
2. What would a calibrated grading rubric look like for `/rai-architecture-review` and `/rai-quality-review`? Can we stay simple?
3. Is iterative evaluation (N rounds) compatible with RaiSE's HITL principle, or does it bypass human judgment?
4. Can story acceptance criteria be automatically converted to verification checklists without adding ceremony?
5. Does evaluator↔generator negotiation violate P1 (Humans Define, Machines Execute)? Under what conditions is agent-to-agent negotiation acceptable?

---

### CONTEXT & HARNESS domain (4 gaps)

| Gap | Anthropic Says | RaiSE Has Today | Delta | Blueprint Ref |
|-----|---------------|-----------------|-------|--------------|
| **G4: Context management** | Explicit compaction/reset policy per task type | Session bundles (~600 tokens). CLAUDE.md (~10.5K). No compaction policy — relies on Claude Code defaults | **High-value gap** — directly affects daily reliability. Session management (RAISE-783) depends on this | G-CTX-1, G-CTX-2 |
| **G10: Effort scaling** | Parametrize harness complexity by task size (simple task = light process, complex = full ceremony) | Full skill cycle for all stories (rule #3). ShuHaRi adapts verbosity but not process weight | **Tension with principles** — we said "full skill cycle even for small stories". Anthropic says scale effort. Who's right? | G-CTX-4 |
| **G12: Agent test design** | Tests should be grep-friendly, context-budget-aware, fast-mode compatible | 237 tests, well-structured. Not designed for agent consumption specifically | **Low gap** — our tests work. But are they optimal for agent-driven TDD? | G-TEST-1 |
| **G14: Planner ambition** | Planning agents tend to over-scope. Calibrate scope expansion | /rai-story-plan decomposes but doesn't check for scope creep | **Real problem** — we've seen this. Plans grow beyond story scope | G-CTX-5 |

**Research questions for RAISE-791:**
1. What compaction/reset policies does Anthropic recommend per task type? How do we map these to RaiSE's skill phases (design, plan, implement, review)?
2. Should RaiSE adopt effort scaling (light process for XS stories) or does "full skill cycle always" provide more value through consistency? What data supports each position?
3. How should we design context budgets per skill? What's the token cost of each skill phase today?
4. What specific patterns prevent planner scope creep? Can we add a "scope fence" to `/rai-story-plan` without adding complexity?
5. What makes a test "agent-friendly"? Are there concrete patterns we can apply to our 237 tests?

---

### TOOL & MCP domain (4 gaps)

| Gap | Anthropic Says | RaiSE Has Today | Delta | Blueprint Ref |
|-----|---------------|-----------------|-------|--------------|
| **G6: Tool descriptions** | Optimize tool descriptions for agent comprehension — clear names, structured params, examples | CLI help text is human-first. Typer auto-generates. No agent-specific optimization | **Medium gap** — our CLI works for agents via CLAUDE.md reference, but descriptions could be better | G-TOOL-1 |
| **G7: Progressive disclosure** | Lazy-load tools — show only what's needed for current phase | All tools always available. CLAUDE.md lists all commands. ToolSearch exists but isn't skill-aware | **Interesting** — we have ToolSearch (deferred tools) from Claude Code, but don't leverage it skill-by-skill | G-TOOL-2 |
| **G8: Code-mode MCP** | Expose tools as TypeScript filesystem APIs instead of function calls | MCP bridge is function-call based. No code-mode alternative | **Low relevance** — RaiSE is Python CLI, not TypeScript. Pattern may not translate | G-TOOL-3 |
| **G11: Agent self-improvement** | Let agents improve their own tool descriptions based on usage | No tool improvement loop. Tools are static | **Aligns with Kaizen** — but do we trust agent self-modification of tools? | G-TOOL-4 |

**Research questions for RAISE-792:**
1. What specific tool description patterns does Anthropic recommend? Can we apply them to our 20+ CLI command groups without breaking human UX?
2. How would progressive tool disclosure work within RaiSE skills? Should each skill declare which tools it needs?
3. Is code-mode MCP relevant for a Python CLI framework, or is it TypeScript-specific? What's the underlying principle we should extract?
4. Under what conditions should we let agents improve tool descriptions? How does this interact with Governance as Code (P2) — if tool descriptions are in git, agent changes need commits?
5. What would tool usage analytics look like in RaiSE's telemetry? Would this inform which tools to optimize first?

---

### MULTI-AGENT domain (3+ gaps)

| Gap | Anthropic Says | RaiSE Has Today | Delta | Blueprint Ref |
|-----|---------------|-----------------|-------|--------------|
| **G9: Parallel coordination** | File-lock task claiming, bare-git shared upstream for parallel agents | rai-agent package (basic). Worktree awareness planned. No coordination protocol | **Future capability** — matters for enterprise scale, not for single-developer today | G-AGENT-1 |
| **Specialized roles** | Dedicated agents for dedup, performance, architecture critique | All agents are generalist. Skills provide specialization but agent identity is uniform | **Interesting** — RaiSE already has skill specialization. Gap is agent identity per role | G-AGENT-2 |
| **Orchestrator scaling** | 1 agent for simple, 10+ for complex. Orchestrator dispatches | No orchestrator. Human dispatches via skills | **Tension with P1** — orchestrator-as-agent vs. human-as-orchestrator | G-AGENT-3 |

**Research questions for RAISE-793:**
1. What coordination primitives does Anthropic use for parallel agents? How do file-lock and bare-git compare to RaiSE's file-based communication?
2. Does specialized agent identity (critic agent, performance agent) conflict with Rai's unified entity model? Or can Rai have "modes" without losing identity coherence?
3. At what scale does human-as-orchestrator break down? Is there a threshold where agent-orchestrator becomes necessary?
4. How do Anthropic's multi-agent patterns handle shared memory? Does their approach preserve determinism?
5. What's the minimum viable multi-agent support RaiSE needs for enterprise (E9)?

---

## Story Sequencing

| Order | Story | Rationale |
|-------|-------|-----------|
| 1 | **RAISE-791** Context & Harness | Highest daily impact. Informs RAISE-783 (sessions). Answers effort scaling tension |
| 2 | **RAISE-790** Evaluation | Strengthens AR/QR skills. High value-to-core |
| 3 | **RAISE-792** Tool & MCP | Medium impact, some quick wins (tool descriptions) |
| 4 | **RAISE-793** Multi-Agent | Future-facing. Enterprise roadmap. Lower urgency |

## Deliverable Per Story

Each research story produces:
1. **Evidence catalog** — Sources read, claims extracted, triangulation
2. **Benchmark matrix** — Anthropic pattern vs. RaiSE mechanism, scored on 4 dimensions
3. **Recommendations** — Adopt (as-is), Adapt (modify for RaiSE), Reject (with rationale)
4. **Backlog impact** — New stories to create, existing stories to reprioritize, gaps to close or accept

## Success Criteria

- [ ] All 14 gaps evaluated with 4-dimension scoring
- [ ] At least 3 "Adopt" recommendations with implementation stories created
- [ ] At least 1 "Reject" with principled rationale (proves we're not blindly copying)
- [ ] Effort scaling tension (G10) resolved with ADR or explicit position
- [ ] Session management (RAISE-783) design informed by G4 findings
- [ ] Backlog reprioritized based on findings

---

*Epic design: 2026-03-26*
*Baseline: raise-blueprint.md*
