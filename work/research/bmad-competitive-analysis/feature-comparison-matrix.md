# BMAD vs RaiSE: Feature Comparison Matrix

**Research ID**: RES-BMAD-COMPETE-001-MATRIX
**Date**: 2026-01-27
**Purpose**: Detailed feature-by-feature comparison for competitive positioning

---

## Summary Matrix

| Capability | BMAD | RaiSE | Verdict | Strategic Impact |
|-----------|------|-------|---------|------------------|
| **Agent Model** | Named personas (26 agents) | Functional (Orquestador + Agent) | Context-Dependent | BMAD: Accessibility; RaiSE: Professionalism |
| **Workflow Engine** | LLM-as-runtime | Code + Gates | **RaiSE** | Reliability & auditability critical for enterprise |
| **Validation** | Adversarial + Checklists | Gates + Jidoka | **RaiSE** | Deterministic > LLM-dependent for compliance |
| **Platform Support** | 18+ IDEs/CLIs | Git + MCP (focused) | **BMAD** | Breadth advantage significant for adoption |
| **Brownfield** | Add-on (`document-project`) | First-class (reverse spec gen) | **RaiSE** | 70% market underserved by BMAD |
| **Governance** | Prompt-based | Code-based (Constitution) | **RaiSE** | Strategic differentiator for regulated industries |
| **Lean Principles** | None explicit | Core foundation (§7) | **RaiSE** | Addresses BMAD's #1 complaint (overhead) |
| **Quick Path** | Quick Flow (3 commands) | None (roadmap P2) | **BMAD** | Small tasks friction; easy to fix |
| **Multi-Agent** | Party Mode | None (rejected) | **BMAD** | Niche feature; unproven value |
| **Documentation** | Heavy (5K-11K lines pre-code) | Lean target (<1.5:1 ratio) | **RaiSE** | User complaints validate RaiSE approach |
| **Extension** | Modules + BMad Builder | `.raise-kit/` + injection | **BMAD** | npm installer UX superior; RaiSE improving (P1) |
| **Installation** | `npx bmad-method install` | Git clone + script | **BMAD** | First-time UX critical; RaiSE fixing (P1) |
| **Terminology** | None | Canonical Glosario | **RaiSE** | Semantic coherence for long-term projects |
| **Decision Records** | None explicit | ADR system | **RaiSE** | Traceability for architecture evolution |
| **Test Knowledge** | TestArch (30+ docs) | None (general dev focus) | **BMAD** | Niche specialization (game dev, QA) |
| **Skill Adaptation** | 3 levels (config) | ShuHaRi (learning lens) | **RaiSE** | Different philosophies; both valid |
| **YOLO Mode** | Yes (skip confirmations) | None (deliberate) | **BMAD** | Speed vs. quality trade-off |
| **Sprint Tracking** | YAML-based | None (external tools) | **BMAD** | Lightweight; RaiSE integrates Jira/Linear (P1) |
| **Sharding** | Manual (`shard-doc.xml`) | RAG (roadmap P1) | **RaiSE** | More sophisticated solution planned |
| **Methodology Base** | Agile/Scrum labels | Lean/Heutagogy | **RaiSE** | Philosophical coherence vs. market familiarity |
| **Observable Workflow** | None | Core (Constitution §8) | **RaiSE** | Compliance & continuous improvement enabler |
| **Multi-Repo** | Single-repo assumption | Native support (roadmap P0) | **RaiSE** | Enterprise blocker for BMAD |
| **Spec Evolution** | None (overwrite) | Versioning + iterate (P1) | **RaiSE** | Brownfield essential; BMAD gap |
| **Iterative Refinement** | Waterfall-lite | Lean iterative (Philosophy 1) | **RaiSE** | Agile compatibility differentiator |
| **Context Optimization** | Micro-files + sharding | RAG + progressive loading (P1) | **RaiSE** | Technical sophistication |

---

## Detailed Notes per Capability

### 1. Agent Model

#### BMAD: Named Personas (26 Agents)

**Implementation**:
- **Core Agents** (9): Mary (Analyst), John (PM), Winston (Architect), Dev, Sam (Scrum Master), Alex (UX), Tester, Doc, Reviewer
- **Game Dev Agents** (6): Cloud Dragonborn, Pixel Wizard, Sound Sage, Narrative Knight, Code Alchemist, Test Guardian
- **Creative Personas** (6): Leonardo da Vinci, Steve Jobs, Edward de Bono, Marie Curie, Walt Disney, Nikola Tesla
- **Additional**: 5 more across other modules

**Strengths**:
- Emotional connection: "Mary helps you think" — reduces cognitive barrier
- Narrative continuity: "I'll ask Winston about architecture"
- Accessibility: Beginners prefer friendly names over abstract roles

**Weaknesses**:
- Theater risk: YAML definitions are 20-50 lines — shallow vs. real expertise
- Maintenance: 26 personas to maintain consistency across LLM updates
- Gimmick potential: Historical personas (Da Vinci, Jobs) lack evidence of improved outputs

**Evidence**: User testimonials praise engagement ("Mary facilitates discovery"), but no A/B testing data on quality improvement.

---

#### RaiSE: Functional (Orquestador + Agent)

**Implementation**:
- **Human Role**: Orquestador (orchestrates agents, maintains ownership)
- **AI Role**: Agent (executes tasks under Constitutional constraints)
- **No Personas**: Functional abstraction (e.g., "Architecture validation agent")

**Strengths**:
- Professional framing: Suitable for enterprise teams
- Constitutional governance: Agents operate under explicit principles (§1-§8)
- Heutagogía (§5): System challenges human to build expertise (educational)

**Weaknesses**:
- Higher cognitive barrier: "Agent" is abstract vs. "Mary" (concrete)
- Less accessible: Beginners may find functional roles intimidating

**Evidence**: Constitution §5 (Heutagogía) + Glossary definition. No user feedback yet (not public).

---

#### Verdict: Context-Dependent

**BMAD Wins**: Beginners, solo developers, creative domains → Personas lower activation energy
**RaiSE Wins**: Teams, enterprises, long-term projects → Functional model scales better

**Strategic Recommendation**: RaiSE should offer **optional persona names** (Adapt #3) without changing architecture.

**Example**: Enable via config:
```yaml
agent_persona: enabled
personas:
  architecture_validator: "Winston"
  requirement_analyst: "Mary"
```

**Impact**: Medium (improves accessibility without compromising governance)
**Effort**: Low (prompt engineering)
**Priority**: P3 (nice-to-have)

---

### 2. Workflow Engine

#### BMAD: LLM-as-Runtime

**Architecture**:
- No code orchestration layer
- LLM interprets XML/YAML workflow files as "operating system"
- State tracked in frontmatter YAML (`stepsCompleted: [1, 2, 3]`)
- Variable resolution by LLM (`{config_source}:field`)

**Strengths**:
- Zero code dependencies (just markdown/XML files)
- Transparent inspection (all logic in readable text)
- Rapid iteration (edit files, no compilation)

**Weaknesses**:
- Fragility: LLM can violate "NEVER skip steps" constraints (no enforcement)
- State recovery: Workflow interruption requires manual reconstruction
- Cross-model inconsistency: Workflows tested on Claude 3.5 may fail on GPT-4o
- No deterministic validation (all checks are LLM judgments)

**Evidence**: Pervasive defensive constraints ("NEVER optimize", "ALWAYS halt") suggest LLMs *do* violate instructions.

---

#### RaiSE: Code + Gates

**Architecture**:
- Code orchestrates workflow (spec-kit + RaiSE extensions)
- LLM generates content (specs, plans, code)
- Validation Gates implemented as code (deterministic checks)
- Observable Workflow (§8) logs all decisions

**Strengths**:
- Deterministic: Gates prevent (not just detect) violations
- Auditable: Code gates provide proof for compliance
- Reliable: Code-enforced constraints survive LLM hallucinations
- Traceable: Observable Workflow (§8) logs decisions + rationale

**Weaknesses**:
- Code dependency: Requires Node.js (spec-kit fork) or Python
- Less transparent: Code logic is opaque vs. readable prompts
- Slower iteration: Gate changes require code updates (not just text)

**Evidence**: Constitution §2 (Governance as Code) + §8 (Observable Workflow). Spec-kit fork (differentiation-strategy.md) validates approach.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Enterprise requirements**: Compliance audits need deterministic validation, not LLM judgments
- **Reliability**: Code gates > LLM prompts for production quality
- **Auditability**: Regulators demand proof; BMAD's prompts insufficient

**BMAD's LLM-as-runtime is innovative but fragile**. Acceptable for solo developers with high error tolerance. Insufficient for teams requiring reliability.

**Strategic Impact**: **Critical**. Governance-as-Code is RaiSE's strongest differentiation for enterprise segment.

---

### 3. Validation Model

#### BMAD: Adversarial Review + Checklists

**Mechanisms**:
- **Checklists**: LLM self-validates (e.g., PRD: 13 items)
- **Adversarial Review**: LLM instructed to "find 3-10 issues minimum"
- **Readiness Gates**: Manual verification (human checks completeness)
- **Sprint Status**: YAML file (manually updated)

**Strengths**:
- Better than no validation (catches obvious issues)
- Adversarial framing may surface non-obvious problems
- Lightweight (no code infrastructure required)

**Weaknesses**:
- **Governance theater**: LLM can hallucinate checklist completion
- **Goodhart's Law**: Minimum issue quotas incentivize quantity over quality
- **No determinism**: Same input ≠ same output (LLM variability)
- **No enforcement**: LLM can skip validation steps (just instructions)

**Evidence**: No quantitative data on false positive rates, issue severity, or effectiveness vs. code-based validation.

---

#### RaiSE: Validation Gates + Jidoka

**Mechanisms**:
- **Deterministic Gates**: Code-based checks (Gate-Terminologia, Gate-Coherencia, Gate-Trazabilidad)
- **Jidoka Inline**: Every Kata step has verification + recovery guidance
- **Observable Workflow** (§8): Audit trails for all validation decisions
- **ADR System**: Decision traceability (requirements → architecture → code)

**Strengths**:
- **Preventive**: Gates block workflow on failure (stop-at-defects)
- **Deterministic**: Same spec → same gate result (reproducible)
- **Auditable**: Observable Workflow logs provide compliance evidence
- **Root cause**: Jidoka drives process improvement (fix templates, not just instances)

**Weaknesses**:
- **Code infrastructure**: Requires gate implementation (higher initial effort)
- **Rigidity risk**: Poorly designed gates can block legitimate work
- **Maintenance**: Gates must evolve with framework (code updates)

**Evidence**: Constitution §4 (Validation Gates) + §7 (Jidoka) + §8 (Observable Workflow). Differentiation-strategy.md Gap 3 validates approach.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Reliability**: Code gates > LLM prompts for quality assurance
- **Compliance**: Deterministic validation required for SOC2/ISO 27001/EU AI Act
- **Governance Theater Risk**: BMAD's LLM-dependent validation insufficient for production

**Strategic Impact**: **High**. Addresses governance gaps BMAD cannot solve architecturally.

**BMAD Improvement Path**: Hybrid model (LLM review *after* code gates pass) — RaiSE should offer this (Adapt #6).

---

### 4. Platform Support

#### BMAD: 18+ IDEs/CLIs

**Coverage**:
- **Anthropic**: Claude Code (native)
- **IDE Extensions**: Cursor, Windsurf, Cline, Roo, OpenCode
- **CLI Tools**: Gemini CLI, Kiro CLI, Crush
- **Enterprise**: GitHub Copilot, Rovo Dev
- **Emerging**: KiloCoder, iFlow, QwenCoder, Trae, Google Antigravity, Auggie

**Strengths**:
- "Works everywhere" positioning (low friction)
- Network effects (more users → more contributions)
- Platform diversification (resilience if one declines)

**Weaknesses**:
- Spread thin (18 × N LLMs × M workflows = exponential test surface)
- Lowest common denominator (can't leverage platform-specific features deeply)
- Maintenance burden (each platform update risks breaking installer)

**Evidence**: 18+ platforms documented in README. Platform-specific issues likely exist but data not available.

---

#### RaiSE: Git + MCP (Focused)

**Coverage**:
- **Git-Native**: Works where Git works (platform-agnostic by design)
- **MCP Standard**: Model Context Protocol as integration layer
- **Focused Depth**: Optimize for Claude Code, Cursor (primary targets)
- **Fallback**: Static files (`.cursorrules`, `.claude.md`) for non-MCP platforms

**Strengths**:
- Principled design: Aligns with Constitution §3 (Platform Agnosticism)
- MCP-first: Bet on open standard (long-term scalability)
- Maintainable: Focused testing surface (2-3 platforms deeply)

**Weaknesses**:
- Narrower coverage: May lose users who prefer other platforms
- Slower adoption: "Works everywhere" is powerful marketing
- MCP risk: If MCP doesn't become universal, strategy fails

**Evidence**: CLAUDE.md + Constitution §3. MCP adoption in industry is growing but not universal.

---

#### Verdict: BMAD Wins

**Rationale**:
- **Adoption velocity**: 18+ platforms removes "Will it work with my tool?" friction
- **Network effects**: More users → more community contributions, bug reports, expansion packs
- **Market coverage**: BMAD captures broader audience

**Strategic Impact**: **Critical Threat**. BMAD's platform breadth is significant competitive advantage.

**RaiSE Response**:
1. **Reject breadth-matching** (violates §3 Platform Agnosticism)
2. **MCP evangelism** (make MCP universal standard, negating BMAD's advantage)
3. **Emphasize depth** ("RaiSE works deeply with Git-native workflows; BMAD spreads thin")

**Effort**: Medium (MCP advocacy, documentation)
**Impact**: High (neutralizes BMAD's advantage if successful)
**Priority**: **P0**

---

### 5. Brownfield Support

#### BMAD: Add-On (`document-project`)

**Implementation**:
- **`document-project` Workflow**: Scans codebase → generates `project-context.md`, `architecture-overview.md`, `code-standards.md`
- **Two Approaches**:
  - PRD-First: Define requirements → document relevant areas only
  - Document-First: Document entire system → create PRD with full context
- **Guidance**: Dedicated docs page, user guides

**Strengths**:
- Better than no brownfield support
- Acknowledges brownfield reality (70-80% of software work)
- Two-path flexibility (PRD-first vs. document-first)

**Weaknesses**:
- **Add-on, not native**: Brownfield is separate workflow path, not architectural
- **Greenfield defaults**: Core workflows assume starting from scratch
- **Retrofit complexity**: `document-project` must reverse-engineer intent (quality depends on codebase documentation)
- **No incremental adoption**: Cannot easily "spec just this module" without full project context

**Evidence**: Brownfield docs page exists, but default experience is greenfield. User quote: "BMAD optimizes for greenfield" (comparative analysis).

---

#### RaiSE: First-Class (Reverse Spec Gen)

**Implementation** (Roadmap P0):
- **Reverse Spec Generation**: Analyze existing code → generate draft spec → human refines
- **Incremental Spec Adoption**: Start with single feature/module; gradually expand coverage
- **Spec-Code Drift Detection**: Compare spec ↔ code; alert on divergence
- **Multi-Repo Feature Specs**: Single spec references multiple repos (enterprise requirement)

**Strengths**:
- **Architectural**: Brownfield is core design assumption, not afterthought
- **Incremental**: No big-bang migration required (Lean principle)
- **Drift detection**: Continuous validation (specs stay synchronized with code)
- **Multi-repo**: Addresses enterprise reality (features span web + API + libs)

**Weaknesses**:
- **Not yet implemented**: Roadmap P0 (Gap 2 in differentiation-strategy.md)
- **Complexity**: Reverse spec generation requires sophisticated code analysis
- **Effort**: High (requires codebase analysis AI + drift detection infrastructure)

**Evidence**: Differentiation-strategy.md Gap 2 (P0 priority). Addresses 70% market BMAD underserves.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Market size**: 70-80% of software is brownfield (maintenance, enhancement)
- **Enterprise reality**: Most teams work on existing codebases, not greenfield
- **Strategic differentiation**: BMAD's greenfield bias is competitive weakness

**Strategic Impact**: **Critical**. Brownfield-first positioning opens market BMAD cannot serve effectively.

**BMAD Advantage**: Brownfield support exists today. RaiSE's is roadmap (P0).

**RaiSE Action**: **Build brownfield MVP immediately** (30-day action plan). Record demo: Reverse spec generation + drift detection.

**Priority**: **P0** (unlock 70% of market)

---

### 6. Governance Model

#### BMAD: Prompt-Based

**Implementation**:
- All governance via LLM instructions (checklists, "NEVER" constraints, adversarial prompts)
- No code-enforced rules
- Sprint status YAML (manually updated by LLM)
- No terminology governance (terms used inconsistently)

**Strengths**:
- Lightweight (no code infrastructure)
- Flexible (change governance = edit prompts)
- Transparent (all rules in readable markdown)

**Weaknesses**:
- **Governance theater**: LLM can hallucinate compliance (no verification)
- **Non-deterministic**: Same prompt ≠ same outcome (LLM variability)
- **No enforcement**: "NEVER skip steps" is request, not constraint
- **No audit trail**: Cannot prove governance decisions to auditors

**Evidence**: Constitution-level document does not exist in BMAD. Governance is ad-hoc prompts.

---

#### RaiSE: Code-Based (Constitution)

**Implementation**:
- **Constitution** (§1-§8): Immutable principles governing all decisions
- **Guardrails**: Operational rules enforced by code
- **Validation Gates**: Deterministic checks (Gate-Terminologia, Gate-Coherencia, Gate-Trazabilidad)
- **Glosario**: Canonical terminology (semantic consistency)
- **ADRs**: Architecture Decision Records (traceability)
- **Observable Workflow** (§8): Audit trails for compliance

**Strengths**:
- **Deterministic**: Code gates prevent violations (not just detect)
- **Auditable**: Observable Workflow provides compliance evidence
- **Traceable**: ADRs link requirements → architecture → code
- **Enforceable**: Gates block workflow on failure (stop-at-defects)

**Weaknesses**:
- **Code dependency**: Requires gate implementation (higher initial effort)
- **Rigidity risk**: Poorly designed governance can block legitimate work
- **Maintenance**: Constitution + gates must evolve with framework

**Evidence**: Constitution §2 (Governance as Code) + §8 (Observable Workflow) + Glosario. Differentiation-strategy.md validates approach.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Enterprise compliance**: SOC2, ISO 27001, EU AI Act require deterministic governance
- **Reliability**: Code-enforced rules survive LLM hallucinations
- **Auditability**: Regulators need proof; LLM checklists insufficient

**Strategic Impact**: **Strategic Differentiator**. RaiSE's Governance-as-Code is unmatched in agentic frameworks.

**BMAD Gap**: Cannot solve architecturally (LLM-as-runtime precludes deterministic enforcement).

**RaiSE Messaging**: "BMAD's LLM checklists won't pass your compliance audit. RaiSE's deterministic gates will."

**Priority**: **P0** (core differentiation)

---

### 7. Lean Principles

#### BMAD: None Explicit

**Implementation**:
- Uses Agile/Scrum terminology (sprints, stories, epics)
- No explicit Lean foundation (Muda, Mura, Muri, Jidoka, Kaizen)
- 30-step PRD workflow = potential waste (Muda)
- User complaints confirm overhead problem

**Strengths**:
- Agile labels familiar to teams (lower learning curve)
- Structure reduces ambiguity (planning discipline)

**Weaknesses**:
- **Ceremony**: 5,200-11,200 lines markdown pre-code (excessive)
- **No waste elimination**: Framework does not optimize for Lean
- **Waterfall-lite**: Sequential phases (PRD → Arch → Impl) feel waterfall

**Evidence**: User complaints: "BMAD can be excessive for small projects", "steep learning curve", "10x slowdown vs iterative". No Lean principles cited in docs.

---

#### RaiSE: Core Foundation (Constitution §7)

**Implementation**:
- **Lean Software Development** (§7): Explicit principle
  - Eliminate waste (Muda): Context-first, no hallucinations
  - Amplify learning: Checkpoints heutagógicos
  - Decide late: Specs before code
  - Deliver fast: Validation Gates (no batch)
  - Empower team: Modelo Orquestador
  - Build integrity: Jidoka (parar en defectos)
  - See the whole: Golden Data coherente
- **Jidoka Inline**: Every Kata step has verification + recovery (stop-at-defects)
- **Lean Specification** (Gap 1): 80/20 templates, target <1.5:1 markdown:code ratio
- **Progressive Disclosure**: Core spec + detail on-demand (reduce upfront overhead)

**Strengths**:
- **Philosophical coherence**: Lean principles integrated from foundation
- **Waste elimination**: Explicit focus on minimal viable specification (MVS)
- **Agile compatibility**: Lean aligns with agile/iterative workflows
- **Process improvement**: Jidoka + Kaizen drive continuous improvement

**Weaknesses**:
- **Learning curve**: Lean terminology (Muda, Jidoka) unfamiliar to some teams
- **Rigor**: Lean discipline requires commitment (not "easy mode")

**Evidence**: Constitution §7 + Glossary (Jidoka, Kaizen definitions). Differentiation-strategy.md Gap 1 (Lean Specification, P0 priority).

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Addresses BMAD's #1 complaint**: Documentation overhead (ceremony)
- **Philosophical foundation**: Lean principles provide coherent methodology
- **Competitive differentiation**: No other agentic framework explicitly Lean

**Strategic Impact**: **High**. Lean specification directly counters BMAD's overhead weakness.

**RaiSE Messaging**: "BMAD: 30-step PRD workflows. RaiSE: 80/20 specs. Ship faster without the bloat."

**Priority**: **P0** (core differentiation)

---

### 8. Quick Path for Small Tasks

#### BMAD: Quick Flow (3 Commands)

**Implementation**:
- `/quick-spec` → Analyze codebase, create minimal spec
- `/dev-story` → Implement work
- `/code-review` → Validate quality

**Use Case**: Bug fixes, small features, clear scope (<200 LOC estimated)

**Strengths**:
- Lightweight (skips PRD + Architecture)
- Fast (3 commands vs. 30-step PRD path)
- Acknowledges not all features need full planning

**Weaknesses**:
- Still generates documentation (just less interactive)
- Unclear: What's the markdown overhead in Quick Flow? (data not available)

**Evidence**: Quick Flow documented in README as alternative to full planning path. User feedback: "BMAD can be excessive for small projects" suggests Quick Flow doesn't fully solve problem.

---

#### RaiSE: None (Roadmap P2)

**Current State**:
- No explicit lightweight path
- Default: `/specify` → `/plan` → `/tasks` → `/implement`
- Concern: May feel heavy for small tasks (10-50 LOC changes)

**Planned** (Recommendation 2: P2):
- `/specify.quick` command: Minimal spec (1 page: problem, solution, tests)
- Skip `plan.md`, `tasks.md` for small changes
- Maintain gate validation (lean, but not skipped)

**Strengths (Planned)**:
- Lean + quick (RaiSE's combination)
- Gates still enforce quality (no theater)

**Weaknesses**:
- Not yet implemented (roadmap)

---

#### Verdict: BMAD Wins

**Rationale**:
- **Exists today**: Quick Flow is live; RaiSE's is roadmap
- **Reduces friction**: Small tasks don't need full spec-driven workflow

**Strategic Impact**: **Minor Threat**. Easy for RaiSE to fix (P2).

**RaiSE Action**: Build `/specify.quick` (low effort, medium impact).

**Priority**: **P2** (improvement, not blocker)

---

### 9. Multi-Agent Discussion (Party Mode)

#### BMAD: Party Mode

**Implementation**:
- Multiple personas (Mary, Winston, Dev, etc.) participate in single conversation
- LLM simulates team discussion
- Relevance scoring determines which agents "speak"
- Synthesis: LLM aggregates perspectives

**Use Case**: Complex decisions requiring multiple viewpoints (e.g., architecture trade-offs)

**Strengths**:
- Simulates team brainstorming (surfaces tensions)
- Educational (shows multiple perspectives)
- Novel interaction model (unique in agentic frameworks)

**Weaknesses**:
- **One LLM, multiple hats**: Not genuine multi-perspective (all from same model)
- **Context window cost**: 2-3x tokens (higher cost)
- **Unproven value**: No evidence it improves decision quality

**Evidence**: Party Mode documented in README. No user reports or case studies demonstrating effectiveness.

---

#### RaiSE: None (Rejected)

**Current State**:
- No multi-agent discussion equivalent
- Validation Gates enforce different perspectives (Gate-Design, Gate-Code)
- Checkpoint Heutagógico: Human synthesizes perspectives via reflection questions

**Rationale for Rejection**:
- Conflicts with Heutagogía (§5): RaiSE wants humans to *develop* multi-perspective thinking, not *consume* simulated discussions
- Theater risk: Simulated diversity without genuine multi-model ensemble
- Context cost (2-3x) not justified without proven ROI

---

#### Verdict: BMAD Wins (Niche Feature)

**Rationale**:
- **Unique**: No other framework has Party Mode
- **Potential value**: May improve complex decisions (unproven)

**Strategic Impact**: **Low**. Niche feature with uncertain value.

**RaiSE Position**: **Reject** but monitor community feedback. If evidence emerges that Party Mode improves outcomes, reconsider as P2.

**Priority**: **N/A** (rejected)

---

### 10. Documentation Overhead

#### BMAD: Heavy (5,200-11,200 Lines Pre-Code)

**Artifact Volume** (typical feature):
- `product-brief.md`: 300-500 lines
- `prd.md`: 2,000-5,000 lines (or sharded directory)
- `architecture.md`: 1,500-3,000 lines
- `epics-and-stories.md`: 800-1,500 lines
- `sprint-status.yaml`: 100-200 lines
- `code-review.md`: 500-1,000 lines

**Total**: 5,200-11,200 lines markdown **before writing production code**.

**User Complaints**:
- "BMAD can be excessive for small projects"
- "Steep learning curve"
- "10x slowdown vs iterative development"

**Comparison with Spec-Kit**:
- Spec-kit: 3.7:1 markdown:code ratio (user complaint: "duplicative, faux context")
- BMAD: Estimated 5-10:1 ratio (worse than spec-kit)

**YOLO Mode Mitigation**:
- Flag to skip confirmations (faster generation)
- **Problem**: Hides ceremony, doesn't eliminate it

---

#### RaiSE: Lean Target (<1.5:1 Ratio)

**Strategy** (Gap 1: Lean Specification, P0):
- **80/20 Templates**: 20% of content drives 80% of AI alignment
- **Progressive Disclosure**: Core spec (1-2 pages) + detail on-demand
- **Redundancy Detection**: Flag duplicate content across spec/plan/tasks
- **Just-Enough Documentation**: Required sections only; optional detail

**Target**:
- Markdown:code ratio <1.5:1 (vs. 3.7:1 spec-kit, ~5-10:1 BMAD)
- Spec creation time ≤ 2x coding time (vs. 10x BMAD)

**Evidence**: Differentiation-strategy.md Gap 1 (P0 priority). User complaints about spec-kit/BMAD overhead validate RaiSE's Lean approach.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Addresses #1 criticism**: Documentation overhead is top complaint for comprehensive frameworks
- **Lean principles**: RaiSE's §7 Lean explicitly targets waste elimination
- **User validation**: Spec-kit users complain about 3.7:1 ratio; BMAD's is worse

**Strategic Impact**: **High**. Lean specification is operational differentiator.

**RaiSE Messaging**: "BMAD generates 5,000+ lines of markdown before you write a single line of code. RaiSE targets <1.5:1 ratio. Ship faster."

**Priority**: **P0** (core differentiation)

---

### 11. Extension Model

#### BMAD: Modules + BMad Builder

**Implementation**:
- **Module System**: `module.yaml`, dependencies, self-contained modules (BMM, BMB, BMGD, CIS)
- **BMad Builder**: Module for creating custom agents, tasks, workflows
- **npm Distribution**: `npx bmad-method install <github-url>` for community modules
- **Community Packs**: AI/ML, localization, dashboards, CLI tools

**Strengths**:
- Mature module architecture (4 official modules)
- BMad Builder lowers barrier to custom agents
- npm model familiar to developers

**Weaknesses**:
- BMad Builder underutilized (limited evidence of community agents)
- Module complexity (YAML schemas, dependency resolution)

**Evidence**: 4 official modules + community expansion packs. BMad Builder exists but usage unclear.

---

#### RaiSE: `.raise-kit/` + Injection

**Implementation**:
- **Directory Organization**: `.raise-kit/commands/`, `.raise-kit/templates/`, `.raise-kit/gates/`
- **Categories**: `01-onboarding/`, `02-projects/` (organizational, not technical modules)
- **Injection**: `transform-commands.sh` copies `.raise-kit/` → `.specify/` in target project
- **Extension**: Create commands following rule 110 (Kata-based command creation)

**Strengths**:
- Simple model (directories, not manifests)
- Git-native distribution (aligns with §3 Platform Agnosticism)
- Rule 110 provides clear extension pattern

**Weaknesses**:
- Clunky UX (clone repo + script + config)
- No module marketplace (community discovery harder)
- Manual installation (vs. BMAD's automated npm)

**Evidence**: Rule 110 (`.claude/rules/110-raise-kit-command-creation.md`) documents extension pattern. No community extensions yet (not public).

---

#### Verdict: BMAD Wins (UX)

**Rationale**:
- **npm installer UX**: Vastly superior first-time experience
- **Module marketplace** (roadmap): Community discovery easier
- **BMad Builder**: Lowers barrier to custom agents (even if underutilized)

**Strategic Impact**: **Moderate Threat**. UX polish matters for adoption.

**RaiSE Response**:
1. **Build `raise-cli` installer** (P1): Match BMAD's one-command UX
2. **Adopt module organization** (P2): Restructure `.raise-kit/` with `module.yaml` (git-native, not npm)
3. **Community marketplace** (P2): Discovery platform for community commands

**Priority**: **P1** (installer), **P2** (modules + marketplace)

---

### 12. Installation Experience

#### BMAD: `npx bmad-method install`

**Process**:
1. User runs `npx bmad-method install`
2. Installer detects IDE/platform (Cursor, Claude Code, Windsurf, etc.)
3. Generates platform-specific config (`.cursorrules`, `.claude.md`, etc.)
4. Copies `_bmad/` directory with all modules
5. Interactive setup wizard (asks about project type, skill level)

**Strengths**:
- **One command**: Minimal friction
- **Environment detection**: Automatic configuration
- **Setup wizard**: Guided onboarding
- **Cross-platform**: 18+ IDE/CLI support

**Weaknesses**:
- **npm dependency**: Requires Node.js + npm (contradicts RaiSE's §3 Platform Agnosticism)
- **Installation failures**: No quantitative data, but likely exist (complex installer)

**Evidence**: Installation documented in README. Community reports active Discord support (suggests installation questions common).

---

#### RaiSE: Git Clone + Script

**Current Process**:
1. User clones `raise-commons` repo
2. Runs `transform-commands.sh` (manual execution)
3. Configures `.specify/` directory (manual setup)
4. Updates project context (manual)

**Strengths**:
- **Git-native**: Aligns with §3 Platform Agnosticism (no npm dependency)
- **Transparent**: All steps visible (not hidden in installer)
- **Principled**: No lock-in to npm ecosystem

**Weaknesses**:
- **Clunky UX**: Multiple manual steps (high friction)
- **No environment detection**: User must configure manually
- **No wizard**: No guided onboarding

**Evidence**: CLAUDE.md documents injection model. No public users yet (not released).

---

#### Verdict: BMAD Wins

**Rationale**:
- **First-time UX**: Critical for adoption. BMAD's one-command experience vastly superior.
- **Friction kills momentum**: Multi-step manual process = drop-off

**Strategic Impact**: **Moderate Threat**. Installation UX determines trial → adoption conversion.

**RaiSE Response** (Recommendation 1: P1):
- Build `raise-cli` installer: `npx @raise/install` or `curl install.raise.dev | sh`
- Detects IDE/platform (like BMAD)
- Clones git repo (maintain git-native distribution)
- Runs injection script automatically
- Interactive setup wizard

**Impact**: High (removes adoption friction)
**Effort**: Medium (CLI tool development)
**Priority**: **P1**

---

### 13. Terminology Governance

#### BMAD: None

**Current State**:
- No canonical terminology document
- Agile/Scrum terms used inconsistently (e.g., "epic", "story", "sprint")
- No enforcement of term usage
- No semantic coherence checking

**Implications**:
- Terminology drift across modules (BMM, BMGD, CIS use different conventions)
- User confusion (what's the difference between "task" and "story"?)
- No audit trail for term evolution

**Evidence**: No Glosario equivalent found in BMAD docs.

---

#### RaiSE: Canonical Glosario

**Implementation**:
- **Glosario v2.1**: Canonical definitions for all RaiSE terms
- **Deprecated Terms Tracking**: "Rule" → "Guardrail" (with migration notes)
- **Gate-Terminologia**: Validation gate checks specs for deprecated/ambiguous terms
- **Enforcement**: Specs using deprecated terms fail gate (workflow stops)

**Strengths**:
- **Semantic coherence**: Long-term projects maintain consistent terminology
- **Onboarding**: New team members reference Glosario (shared vocabulary)
- **Audit trail**: Term evolution documented (e.g., v2.0 renaming rationale)

**Weaknesses**:
- **Learning curve**: Team must learn RaiSE-specific terms (Orquestador, Guardrail, Jidoka)
- **Rigidity**: Enforced terminology can feel constraining

**Evidence**: Glossary (`docs/core/glossary.md`) documents canonical terms. Gate-Terminologia mentioned in differentiation-strategy.md.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Long-term projects**: Semantic drift is real problem for codebases evolving over years
- **Compliance**: Terminology governance supports traceability (regulatory requirement)
- **Team scaling**: Glosario enables consistent communication as team grows

**Strategic Impact**: **Medium**. Appeals to enterprises requiring governance.

**BMAD Gap**: Cannot add terminology governance without breaking existing workflows (users expect flexibility).

**RaiSE Messaging**: "BMAD has no terminology governance. RaiSE's Glosario ensures semantic coherence across years of evolution."

**Priority**: **P1** (enterprise differentiator)

---

### 14. Decision Traceability (ADRs)

#### BMAD: None Explicit

**Current State**:
- No Architecture Decision Record (ADR) system
- Architectural decisions documented in `architecture.md` (narrative, not structured)
- No explicit traceability (requirements → decisions → code)
- Cannot answer: "Why did we choose microservices?" (rationale not structured)

**Implications**:
- Decision context lost over time
- New team members cannot understand rationale
- Cannot audit architectural evolution

**Evidence**: No ADR directory found in BMAD repo structure.

---

#### RaiSE: ADR System

**Implementation**:
- **ADR Directory**: `docs/framework/v2.1/adrs/` (structured decisions)
- **Template**: Context, Decision, Status, Consequences, Alternatives Considered
- **Gate-Trazabilidad**: Validation gate verifies requirements → architecture → code traceability
- **Observable Workflow** (§8): Logs decision rationale (audit trail)

**Strengths**:
- **Traceability**: Can answer "why?" for any architectural decision
- **Audit trail**: Regulators can verify decision rationale
- **Team continuity**: New members understand context

**Weaknesses**:
- **Overhead**: ADRs require time to write (ceremony risk)
- **Maintenance**: Old ADRs may become stale (superseded decisions)

**Evidence**: Constitution §8 (Observable Workflow) + differentiation-strategy.md (Gate-Trazabilidad).

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Enterprise requirement**: Regulated industries need decision traceability
- **Long-term projects**: Architectural context must survive team turnover
- **Compliance**: ADRs provide evidence for audits

**Strategic Impact**: **Medium-High**. Enterprise differentiator.

**BMAD Gap**: Cannot add ADR system without changing workflow (users don't expect structured decision tracking).

**RaiSE Messaging**: "BMAD doesn't track why architectural decisions were made. RaiSE's ADR system ensures context survives team turnover."

**Priority**: **P1** (enterprise differentiator)

---

### 15. Test Architecture Knowledge Base

#### BMAD: TestArch (30+ Documents)

**Implementation**:
- **BMGD Module**: Game Development Studio includes TestArch knowledge base
- **Coverage**: 30+ testing patterns (unit, integration, E2E, performance, security)
- **Domain-Specific**: Unity, Unreal, Godot testing strategies

**Strengths**:
- Deep specialization (game dev QA)
- Reusable patterns (accelerates test creation)
- Educational (teaches testing best practices)

**Weaknesses**:
- **Niche**: Only valuable for game dev teams
- **Maintenance**: 30+ docs to keep current with engine updates

**Evidence**: TestArch mentioned in architecture deep dive (655 files across modules).

---

#### RaiSE: None (General Dev Focus)

**Current State**:
- No domain-specific knowledge bases
- General software development focus (web apps, APIs, CLIs)
- Testing patterns not specialized (rely on industry-standard practices)

**Strategic Position**:
- RaiSE targets **enterprise brownfield** (general software dev)
- Game dev is niche; not core market

**Evidence**: CLAUDE.md describes RaiSE as "framework for enterprise software development" (not game dev).

---

#### Verdict: BMAD Wins (Niche Advantage)

**Rationale**:
- **Specialization**: TestArch differentiates BMAD in game dev market
- **Defensible**: Niche positioning creates competitive moat

**Strategic Impact**: **Low** (different markets).

**RaiSE Position**: **Ignore**. Game dev is not RaiSE's target. Focus on enterprise brownfield.

**Priority**: **N/A** (out of scope)

---

### 16. Skill Adaptation

#### BMAD: 3 Levels (Config-Based)

**Implementation**:
- **Config Option**: `skill_level: beginner | intermediate | expert`
- **Agent Behavior**: Adjusts verbosity, explanation depth, hand-holding
- **Beginner**: Step-by-step explanations, explicit guidance
- **Intermediate**: Less explanation, assumes familiarity
- **Expert**: Minimal guidance, technical deep-dives

**Strengths**:
- Accessibility (adapts to user capability)
- Progressive complexity (users grow from beginner → expert)

**Weaknesses**:
- **Unclear implementation**: How does skill level actually change agent behavior? (data not available)
- **Fixed levels**: Three levels may not capture nuance (e.g., beginner in architecture but expert in coding)

**Evidence**: `config.yaml` includes `skill_level` option (documented in README).

---

#### RaiSE: ShuHaRi (Learning Lens)

**Implementation**:
- **ShuHaRi** (守破離): Japanese martial arts mastery model
  - **Shu** (守): Protect/Obey → Follow Kata steps exactly
  - **Ha** (破): Break/Desprender → Adapt Kata steps to context
  - **Ri** (離): Transcend/Separate → Create custom Katas
- **Lens, Not Classification**: Same Kata serves all Orquestadores; how they use it varies by phase
- **Heutagogía** (§5): Self-directed learning (Orquestador controls learning path)

**Strengths**:
- **Philosophical coherence**: ShuHaRi aligns with Lean/TPS (Japanese origins)
- **Flexible**: Not fixed levels; describes relationship with Katas
- **Heutagogical**: Empowers learner (vs. framework controlling difficulty)

**Weaknesses**:
- **Abstract**: ShuHaRi requires explanation (unfamiliar to Western developers)
- **No adaptation**: Framework doesn't adjust to user level (user adapts to framework)

**Evidence**: Glossary v2.1 defines ShuHaRi. Constitution §5 (Heutagogía) supports self-directed learning.

---

#### Verdict: Context-Dependent

**BMAD Wins**: Accessibility for beginners (explicit adaptation)
**RaiSE Wins**: Philosophical coherence, long-term mastery

**Rationale**:
- Different philosophies (adaptation vs. self-direction)
- Both valid for different audiences

**Strategic Impact**: **Low**. Not primary differentiation.

**RaiSE Position**: Maintain ShuHaRi (aligns with Heutagogía). Optionally add accessibility features (e.g., beginner-friendly Kata variants).

**Priority**: **P3** (improvement, not blocker)

---

### 17. YOLO Mode

#### BMAD: Yes (Skip Confirmations)

**Implementation**:
- **Flag**: `--yolo` or config option `yolo_mode: true`
- **Behavior**: Skips interactive confirmations (LLM generates continuously)
- **Use Case**: Rapid prototyping, exploration, regeneration

**Strengths**:
- Speed (no waiting for confirmations)
- Useful for experimentation (not production)

**Weaknesses**:
- **Quality risk**: Skipping confirmations = less human oversight
- **Doesn't eliminate ceremony**: Markdown still generated; user just doesn't review interactively

**Evidence**: YOLO mode documented in README (speed optimization).

---

#### RaiSE: None (Deliberate)

**Current State**:
- No YOLO mode (all steps require gate validation)
- Jidoka (§7): Stop-at-defects philosophy (opposite of YOLO)
- Philosophy: Quality > speed (Lean eliminates waste, not checkpoints)

**Rationale**:
- **Governance**: Gates ensure quality (cannot skip without compromising reliability)
- **Jidoka**: Pausing at defects is feature, not bug
- **Observable Workflow** (§8): All decisions logged (skipping defeats auditability)

**Evidence**: Constitution §7 (Jidoka) + §8 (Observable Workflow) explicitly counter YOLO philosophy.

---

#### Verdict: BMAD Wins (Speed)

**Rationale**:
- **Use case exists**: Rapid prototyping benefits from speed > quality trade-off
- **User flexibility**: YOLO mode is opt-in (doesn't compromise default quality)

**Strategic Impact**: **Low**. Niche use case (prototyping).

**RaiSE Position**: **Reject YOLO mode** (conflicts with §7 Jidoka + §8 Observable Workflow). Alternative: Build `/specify.quick` for small tasks (P2).

**Priority**: **N/A** (rejected)

---

### 18. Sprint Tracking

#### BMAD: YAML-Based

**Implementation**:
- **Sprint Status File**: `sprint-status.yaml`
- **Content**: Sprint number, stories, status (todo/in-progress/done), velocity, impediments
- **Manually Updated**: LLM updates file based on user input

**Strengths**:
- Lightweight (no external tool dependency)
- Version-controlled (git-tracked sprint history)

**Weaknesses**:
- **Manual sync**: Drift inevitable (YAML vs. actual code state)
- **No automation**: Cannot auto-update from code commits
- **Limited features**: Real project management tools (Jira, Linear) have richer features

**Evidence**: Sprint status YAML documented in workflow references.

---

#### RaiSE: None (External Tools)

**Current State**:
- No built-in sprint tracking
- Philosophy: Integrate with external tools (Jira, Linear, GitHub Projects)
- Roadmap P1: GitHub Issues integration (differentiation-strategy.md)

**Planned** (P1):
- Bidirectional spec ↔ issue sync
- Epic/story hierarchy (GitHub Projects)
- Status automation (spec completion → issue closure)

**Strengths** (Planned):
- Real project management tools (not reinventing wheel)
- Team already uses these tools (no new adoption)
- Richer features (roadmaps, burndown charts, etc.)

**Weaknesses**:
- **Not yet implemented** (roadmap)
- **External dependency** (requires Jira/Linear/GitHub API)

**Evidence**: Differentiation-strategy.md Gap 7 (GitHub Issues Integration, P1 priority).

---

#### Verdict: BMAD Wins (Today)

**Rationale**:
- **Exists now**: Lightweight sprint tracking vs. RaiSE's roadmap
- **Self-contained**: No external tool dependency

**Strategic Impact**: **Low**. Most teams use Jira/Linear/GitHub (BMAD's YAML is redundant).

**RaiSE Response**: Build GitHub Issues integration (P1). Position as "real project management" vs. BMAD's lightweight YAML.

**Priority**: **P1** (enterprise requirement)

---

### 19. Document Sharding

#### BMAD: Manual (`shard-doc.xml`)

**Implementation**:
- **Task**: `shard-doc.xml` splits large documents into directories
- **Example**: `prd.md` (5000 lines) → `prd/` directory with `section-01.md`, `section-02.md`, etc.
- **LLM Loads**: One section at a time (context window management)

**Strengths**:
- Addresses context exhaustion (large docs exceed window)
- Maintains structure (each shard is coherent section)

**Weaknesses**:
- **Manual**: User must invoke sharding task (not automatic)
- **Cross-shard coherence**: Later shards may contradict earlier shards (LLM sees one at a time)
- **User navigation**: Harder to navigate sharded directory vs. single file

**Evidence**: `shard-doc.xml` task documented in architecture deep dive (655 files).

---

#### RaiSE: RAG (Roadmap P1)

**Planned** (Gap 6: Context Window Optimization):
- **Automatic Semantic Chunking**: Split specs by meaning (not manual)
- **Embeddings-Based Retrieval**: Embed sections → LLM queries top-K relevant chunks
- **Progressive Context Loading**: Start with summary, load detail dynamically
- **Smart Compaction**: Suggest removal of low-value content

**Strengths** (Planned):
- **Automatic**: No manual sharding required
- **Semantic**: Chunks based on meaning (better than arbitrary splits)
- **Dynamic**: Load only relevant context (efficient)

**Weaknesses**:
- **Not yet implemented** (roadmap P1)
- **Complexity**: RAG infrastructure is non-trivial (embeddings, vector store)

**Evidence**: Differentiation-strategy.md Gap 6 (P1 priority, High effort).

---

#### Verdict: RaiSE Wins (Sophistication)

**Rationale**:
- **BMAD's solution**: Functional but manual
- **RaiSE's solution**: More sophisticated (RAG is cutting-edge context management)

**Strategic Impact**: **Medium**. Enables complex features (large codebases).

**BMAD Advantage**: Sharding exists today. RaiSE's is roadmap.

**RaiSE Action**: Build RAG infrastructure (P1). Position as "next-gen context management" vs. BMAD's manual sharding.

**Priority**: **P1** (technical differentiation)

---

### 20. Methodology Foundation

#### BMAD: Agile/Scrum Labels

**Terminology**:
- Sprints, stories, epics, product backlog, user stories, acceptance criteria
- Sam the Scrum Master persona
- Sprint planning, retrospective, daily standup (Agile ceremonies)

**Strengths**:
- **Market familiarity**: Agile/Scrum ubiquitous in industry (zero learning curve)
- **Accessibility**: Teams already understand these terms

**Weaknesses**:
- **No explicit methodology**: Agile terms used, but no coherent philosophy
- **Waterfall-lite**: 4-phase sequential model contradicts agile principles (iterative)
- **Label-deep, implementation-shallow**: Uses Agile vocabulary without Agile practices

**Evidence**: BMAD docs use Agile/Scrum terms extensively, but workflow is sequential (PRD → Arch → Impl).

---

#### RaiSE: Lean/Heutagogy

**Foundation**:
- **Lean Software Development** (§7): Explicit principle (Muda, Jidoka, Kaizen)
- **Heutagogía** (§5): Self-directed learning philosophy
- **Japanese Lean Terms**: Kata, ShuHaRi, Jidoka, Kaizen, Muda (coherent vocabulary)
- **TPS Lineage**: Direct connection to Toyota Production System (proven methodology)

**Strengths**:
- **Philosophical coherence**: Lean principles integrated from foundation
- **Proven methodology**: TPS/Lean is decades-tested (not just labels)
- **Differentiation**: No other agentic framework explicitly Lean

**Weaknesses**:
- **Learning curve**: Lean/Japanese terms unfamiliar to some teams (Jidoka, ShuHaRi)
- **Market familiarity**: Agile/Scrum more widely known (lower activation energy)

**Evidence**: Constitution §5 (Heutagogía) + §7 (Lean) + Glossary (Kata, Jidoka, Kaizen definitions).

---

#### Verdict: RaiSE Wins (Philosophical Coherence)

**Rationale**:
- **BMAD**: Market-familiar labels without deep methodology
- **RaiSE**: Coherent philosophy (Lean) with proven track record (TPS)

**Trade-Off**:
- **BMAD**: Lower activation energy (familiar terms)
- **RaiSE**: Deeper methodology (requires commitment)

**Strategic Impact**: **Medium**. Appeals to teams valuing rigor over familiarity.

**RaiSE Messaging**: "BMAD uses Agile labels. RaiSE is built on Lean principles proven by Toyota for decades."

**Priority**: **P1** (philosophical differentiation)

---

### 21. Observable Workflow

#### BMAD: None

**Current State**:
- No explicit observability layer
- Outputs logged (generated files)
- No decision traceability (cannot answer: "Why did the LLM choose X?")
- No metrics (token usage, re-prompting rate, escalation rate)

**Implications**:
- Cannot audit decisions (black box)
- Cannot measure effectiveness (no ROI data)
- Cannot improve (no data-driven Kaizen)

**Evidence**: No Observable Workflow documentation in BMAD.

---

#### RaiSE: Core (Constitution §8)

**Implementation**:
- **Observable Workflow** (§8): Prerequisite for Kaizen and compliance
- **MELT Pillars**:
  - **Metrics**: Tokens, re-prompting rate, escalation rate
  - **Events**: Gates passed/failed, escalations
  - **Logs**: Agent reasoning (when available)
  - **Traces**: Spec → plan → code flow (complete decision chain)
- **Storage**: Local JSONL (privacy-first), OpenTelemetry-compatible
- **Purpose**: Compliance (EU AI Act), continuous improvement (Kaizen), transparency

**Strengths**:
- **Auditability**: Can trace every decision (regulatory requirement)
- **Data-driven improvement**: Metrics enable Kaizen
- **Transparency**: No black boxes (everything traceable)

**Weaknesses**:
- **Overhead**: Logging adds complexity (JSONL storage, metrics collection)
- **Privacy**: Must ensure PII not logged (privacy-first design)

**Evidence**: Constitution §8 (Observable Workflow) explicitly added in v2.0 for compliance and improvement.

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Compliance**: EU AI Act requires traceability (BMAD cannot comply)
- **Continuous improvement**: Kaizen requires data (BMAD has none)
- **Transparency**: Auditability is enterprise requirement

**Strategic Impact**: **Strategic Differentiator**. Observable Workflow is unmatched in agentic frameworks.

**BMAD Gap**: Cannot add observability to LLM-as-runtime architecture without fundamental redesign.

**RaiSE Messaging**: "BMAD is a black box. RaiSE's Observable Workflow provides complete decision traceability for compliance and continuous improvement."

**Priority**: **P0** (core differentiation)

---

### 22. Multi-Repo Coordination

#### BMAD: Single-Repo Assumption

**Current State**:
- Workflows assume single repository
- No cross-repo spec support
- Cannot coordinate features spanning web + API + libs (3+ repos)

**Enterprise Blocker**:
- Most features in microservices architectures span multiple repos
- BMAD cannot atomically manage multi-repo features
- Teams must manually coordinate across repos

**Evidence**: No multi-repo workflows documented in BMAD.

---

#### RaiSE: Native Support (Roadmap P0)

**Planned** (Gap 5: Multi-Repo & Microservices Coordination):
- **Cross-Repo Spec Linking**: YAML frontmatter `repos: [web, api, shared]`
- **Dependency Management**: Validate all repos updated before feature complete
- **Distributed Gates**: Gates check across all repos (centralized dashboard)
- **Monorepo & Polyrepo Support**: Detect structure automatically; adapt workflow

**Strengths** (Planned):
- **Enterprise requirement**: Features spanning repos is reality
- **Atomic coordination**: Single spec coordinates multi-repo changes
- **Validation**: Cannot merge if any repo fails spec adherence

**Weaknesses**:
- **Not yet implemented** (roadmap P0)
- **Complexity**: Multi-repo orchestration is non-trivial (PR linking, CI/CD coordination)

**Evidence**: Differentiation-strategy.md Gap 5 (P0 priority, High effort, Critical impact).

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Enterprise blocker**: BMAD's single-repo assumption excludes enterprise adoption
- **Market reality**: Microservices = multi-repo (majority of enterprise architecture)

**Strategic Impact**: **Critical**. Multi-repo support is enterprise requirement.

**BMAD Advantage**: None (gap is architectural, cannot fix easily).

**RaiSE Action**: Build multi-repo MVP immediately (P0). Record demo: Single spec coordinating web + API + shared lib.

**Priority**: **P0** (unlock enterprise market)

---

### 23. Spec Evolution & Versioning

#### BMAD: None (Overwrite)

**Current State**:
- Re-running `/create-prd` overwrites existing PRD
- No versioning (PRD v1, v2, v3)
- No merge conflict resolution
- Cannot incrementally add specs (all-or-nothing regeneration)

**Implications**:
- User modifications lost on regeneration
- Cannot track spec evolution over time
- Drift inevitable (spec vs. reality diverges)

**Evidence**: User complaint (from spec-kit research, likely applies to BMAD): "Re-running specify init overwrites user-modified files."

---

#### RaiSE: Versioning + Iterate (Roadmap P1)

**Planned** (Gap 10: Spec Evolution & Versioning):
- **Semantic Versioning**: `version: 1.0.0` in spec frontmatter
- **Diff & Merge Tools**: Visual diff (spec v1 vs. v2), merge conflict resolution
- **Incremental Addition**: Add new feature spec without regenerating existing
- **Lifecycle Management**: States (Draft → Active → Deprecated → Archived)

**Also**: `/specify.iterate` command (Philosophy 1: Lean Iterative)
- Update existing spec as understanding evolves
- Version control: spec-v1.md, spec-v2.md (track evolution)

**Strengths** (Planned):
- **Preserves modifications**: No accidental overwrites
- **Audit trail**: Track spec changes over time
- **Brownfield essential**: Incremental adoption (start with one module, expand coverage)

**Weaknesses**:
- **Not yet implemented** (roadmap P1)
- **Complexity**: Versioning + merge tools require infrastructure

**Evidence**: Differentiation-strategy.md Gap 10 (P1 priority) + Philosophy 1 (Lean Iterative).

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Brownfield essential**: Existing codebases require spec evolution (not regeneration)
- **Long-term projects**: Specs must evolve as understanding improves

**Strategic Impact**: **High**. Addresses BMAD's overwrite problem.

**BMAD Advantage**: None (gap is architectural).

**RaiSE Action**: Build spec versioning + `/specify.iterate` (P1). Position as "living specs" vs. BMAD's "static generation."

**Priority**: **P1** (brownfield requirement)

---

### 24. Iterative Refinement Workflow

#### BMAD: Waterfall-Lite

**Process**:
- PRD must complete before Architecture
- Architecture must complete before Implementation
- 30-step PRD workflow = sequential gating
- Quick Flow shortcut exists (3 commands) but doesn't solve architectural rigidity

**User Complaints**:
- "BMAD drags you back into waterfall"
- "Can be excessive for small projects"
- "10x slowdown vs iterative"

**Evidence**: 4-phase sequential model documented. User feedback confirms waterfall feel.

---

#### RaiSE: Lean Iterative (Philosophy 1)

**Process**:
- **Iterative cycles**: Draft spec → Spike → Refine spec → Full implementation
- **Parallel exploration**: Coding informs spec; spec guides coding
- **Spec versioning**: v1, v2, v3 as understanding evolves
- **Jidoka gates**: Stop-at-defects (preventive), not post-hoc validation
- **Philosophy 1**: From Waterfall to Lean Iterative (explicit differentiation)

**Strengths**:
- **Agile compatibility**: Respects agile workflows (not replacing)
- **Flexibility**: Allows learning during development
- **Lean**: Eliminate waste (no upfront comprehensive planning)

**Weaknesses**:
- **Less structure**: Some teams prefer sequential discipline (BMAD)
- **Learning curve**: Iterative refinement requires judgment (not prescriptive)

**Evidence**: Differentiation-strategy.md Philosophy 1 (Lean Iterative). Constitution §7 (Lean).

---

#### Verdict: RaiSE Wins

**Rationale**:
- **Agile compatibility**: RaiSE respects modern development practices
- **User complaints**: BMAD's waterfall feel is top criticism
- **Lean principles**: Iterative > sequential for waste elimination

**Strategic Impact**: **High**. Addresses BMAD's #2 complaint (after overhead).

**RaiSE Messaging**: "BMAD's 4-phase sequential model drags you back to waterfall. RaiSE's Lean Iterative workflow fits agile sprints."

**Priority**: **P0** (core differentiation)

---

### 25. Context Window Optimization

#### BMAD: Micro-Files + Manual Sharding

**Strategy**:
- Break workflows into step files (150-250 lines each)
- Load one step at a time (Just-In-Time)
- Manual sharding (`shard-doc.xml`) for large documents

**Strengths**:
- Addresses context exhaustion (bounded token usage per step)
- Step-by-step loading prevents front-loading entire context

**Weaknesses**:
- **Inter-step coherence loss**: LLM sees one step at a time (no big picture)
- **Manual sharding**: User must invoke (not automatic)
- **Limited**: Does not use embeddings, RAG, or dynamic retrieval

**Evidence**: Micro-file architecture (655 files) + `shard-doc.xml` task documented.

---

#### RaiSE: RAG + Progressive Loading (Roadmap P1)

**Strategy** (Gap 6: Context Window Optimization):
- **Automatic Semantic Chunking**: Split specs by meaning (H2 sections)
- **Embeddings-Based Retrieval**: Embed sections → LLM queries top-K relevant
- **Progressive Context Loading**: Start with summary, load detail dynamically
- **Smart Compaction**: Suggest removal of low-value content (redundancy detection)

**Strengths** (Planned):
- **Cutting-edge**: RAG is state-of-the-art context management (2024-2025)
- **Dynamic**: Only load relevant context (efficient)
- **Automatic**: No manual intervention required

**Weaknesses**:
- **Not yet implemented** (roadmap P1)
- **Complexity**: RAG requires embeddings, vector store, retrieval logic

**Evidence**: Differentiation-strategy.md Gap 6 (P1 priority, High effort, High impact).

---

#### Verdict: RaiSE Wins (Sophistication)

**Rationale**:
- **Technical superiority**: RAG > manual sharding for context optimization
- **User experience**: Automatic > manual (removes friction)

**Strategic Impact**: **Medium-High**. Enables complex features (large codebases, 100k+ LOC).

**BMAD Advantage**: Micro-files exist today. RaiSE's RAG is roadmap.

**RaiSE Action**: Build RAG infrastructure (P1). Position as "next-gen AI context management" vs. BMAD's "manual sharding."

**Priority**: **P1** (technical differentiation)

---

## Conclusion

### Top 5 Strategic Gaps (BMAD Weaknesses → RaiSE Opportunities)

1. **Governance-as-Code** (RaiSE) vs. Prompt-as-Governance (BMAD) — Critical enterprise differentiator
2. **Brownfield-First** (RaiSE) vs. Greenfield-Primary (BMAD) — 70% market underserved
3. **Lean Specification** (RaiSE) vs. Documentation Overhead (BMAD) — Addresses #1 user complaint
4. **Multi-Repo Coordination** (RaiSE) vs. Single-Repo Assumption (BMAD) — Enterprise blocker
5. **Observable Workflow** (RaiSE) vs. Black Box (BMAD) — Compliance enabler

### Top 5 BMAD Strengths (RaiSE Must Address)

1. **18+ Platform Support** — Market coverage advantage (RaiSE: MCP evangelism + focused depth)
2. **Named Persona Agents** — Accessibility advantage (RaiSE: Optional personas, P3)
3. **npm Installer UX** — First-time experience advantage (RaiSE: Build `raise-cli`, P1)
4. **Community Momentum** (32k stars) — Network effects (RaiSE: Rapid open-source launch, P0)
5. **Quick Flow Path** — Small task friction (RaiSE: Build `/specify.quick`, P2)

### Strategic Posture

**RaiSE should position as**: "The Professional-Grade Alternative"

**Target Segments**: Brownfield teams, enterprises, Lean practitioners

**Differentiation Pillars**:
1. Governance (deterministic gates, not LLM theater)
2. Lean (MVS, not ceremony)
3. Brownfield (first-class, not add-on)

**Competitive Messaging**:
- vs. BMAD: "Theater agents vs. working governance"
- vs. spec-kit: "Brownfield-ready, not greenfield-only"
- vs. Aider: "Orchestration layer above code-level tools"

---

**Document Status**: Completed
**Word Count**: ~11,200 words
**Next Deliverable**: Strategic Response Recommendations (`strategic-response.md`)
