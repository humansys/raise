# RaiSE — Reliable AI Software Engineering
## Comprehensive Context Document for AI Agents

**Version:** 1.0.0  
**Date:** December 28, 2025  
**Purpose:** Single-file corpus providing complete context about the RaiSE framework for AI agents.

---

# PART I: IDENTITY & PRINCIPLES

## What RaiSE Is

**RaiSE is** the methodological operating system for governing AI agents in enterprise software development. It is a **governance-as-code** framework that structures the use of AI in software development, converting the chaos of AI-assisted development into a governable, traceable process that continuously improves—without sacrificing speed.

### The Problem RaiSE Solves

Development teams adopt AI coding tools (Copilot, Cursor, Claude Code) without governance. The result:
- **Inconsistency**: Each developer uses AI differently, producing heterogeneous code
- **Undetected hallucinations**: Without structured validation, AI errors reach production  
- **Context loss**: Each AI session starts from zero; no organizational "memory"
- **Cognitive atrophy**: Developers accept AI code without understanding it
- **Compliance gaps**: Regulations like EU AI Act require traceability that doesn't exist

### What RaiSE Is NOT

- ❌ A replacement for human developers
- ❌ An IDE or code editor
- ❌ An accelerated "vibe coding" tool
- ❌ Vendor lock-in to specific platforms

---

## The Seven Constitutional Principles

### 1. Humans Define, Machines Execute
Humans specify the **"What"** in natural language (Markdown). Machines receive the **"How"** in structured format (JSON). The specification is the source of truth; code is its expression.

### 2. Governance as Code
Policies, rules, and standards are versioned artifacts in Git, not static documents in forgotten wikis. What's not in the repository doesn't exist.

### 3. Platform Agnosticism
RaiSE works wherever Git works. No dependency on GitHub, GitLab, Bitbucket, or any specific provider. The Git protocol is the universal transport.

### 4. Fractal Quality (DoD in Every Phase)
There is no single "Done". Each phase has its own quality gate that must be crossed before proceeding. Quality is not a final event; it's a continuous process.

### 5. Heutagogy Over Dependency
The system doesn't just deliver the fish, it teaches fishing. At the end of critical sessions, RaiSE challenges the human to ensure understanding and ownership of the solution.

### 6. Continuous Improvement (Kaizen)
If a prompt failed or code required many iterations, rules and katas are refined. The system learns from its errors and improves for next time.

### 7. Lean Software Development
RaiSE applies Toyota Production System principles to AI-assisted development: eliminate waste, amplify learning, build quality (Jidoka), and deliver value continuously.

---

## Design Values

| Value | Over | Explanation |
|-------|------|-------------|
| **Simplicity** | Completeness | Prefer simple solutions that cover 80% of cases |
| **Composability** | Monoliths | Small components that combine |
| **Transparency** | Magic | Everything must be inspectable and explainable |
| **Convention** | Configuration | Sensible defaults, override when necessary |
| **Evolution** | Revolution | Incremental changes over total rewrites |

---

## Absolute Constraints

### Never:
- Process code without prior structured context
- Store secrets, tokens, or PII in configuration files
- Create dependency on proprietary APIs when Git-native alternatives exist
- Sacrifice traceability for speed
- Generate code without a documented implementation plan

### Always:
- Validate specs against the constitution before planning
- Document architectural decisions (ADRs)
- Maintain backward compatibility in schemas
- Provide escape hatches for advanced users
- Include attribution to upstream projects (MIT compliance)

---

# PART II: LEARNING PHILOSOPHY

## RaiSE as a Lean Framework

RaiSE is not simply a governance tool for AI-generated code. It is a **Lean Software Development framework** that integrates AI agents as accelerators of value flow, while preserving—and enhancing—professional human development.

### Lean Principles in RaiSE

| Lean Principle | RaiSE Interpretation |
|----------------|----------------------|
| **Eliminate waste** | Reduce spec-correction cycles; structured context prevents "hallucinations" |
| **Amplify learning** | Every AI interaction is an opportunity for professional growth |
| **Decide as late as possible** | High-level specs → details emerge during implementation |
| **Deliver as fast as possible** | Continuous flow with fractal DoDs; no WIP accumulation |
| **Empower the team** | The human is an Orchestrator, not a passive consumer |
| **Build integrity** | Fractal quality; Jidoka in every phase |
| **See the whole** | Golden Data as systemic project vision |

---

## The Three Philosophical Pillars

### Pillar 1: Heutagogy (Self-Determined Learning)

**Heutagogy** (from Greek *heutos* = "oneself" + *agogos* = "guide") is the theory of self-determined learning. In RaiSE, the developer—now **Orchestrator**—is not a passive consumer of generated code. They are the architect of their own professional growth through each interaction with AI agents.

**Manifestations:**
1. **Explainability First** — Before generating code, the agent explains its approach. The Orchestrator evaluates, learns, and adjusts.
2. **Critical Validation** — The Orchestrator never accepts code blindly. Each acceptance is an informed decision.
3. **Heutagogic Challenge** — At the end of critical sessions, the system may ask: "Can you explain why this solution works?"
4. **Complete Ownership** — AI-generated code is the Orchestrator's responsibility. This responsibility requires—and produces—deep understanding.

**The Orchestrator vs. The Consumer:**

| Code Consumer | RaiSE Orchestrator |
|--------------|-------------------|
| "Give me working code" | "Explain your approach before generating" |
| Accept and continue | Evaluate, question, validate |
| Delegate responsibility | Assume ownership |
| Skills atrophy | Skills evolve |
| Increasing dependency | Increasing autonomy |

> **RaiSE Principle:** The system teaches fishing, not just delivers fish. Each work session leaves the Orchestrator more capable than before.

### Pillar 2: Jidoka (自働化) — "Automation with Human Touch"

**Jidoka** is one of the two pillars of the Toyota Production System. In RaiSE, it manifests as the capacity—and obligation—to **stop the flow when a problem is detected**, rather than accumulating defects discovered late.

**The Four Jidoka Steps:**
1. **Detect the anomaly** — Fractal DoDs act as quality sensors in each phase
2. **Stop the process** — If DoD doesn't pass, the flow stops
3. **Correct immediately** — Root cause analysis (Ishikawa, 5 Whys)
4. **Prevent recurrence** — Update rules, improve katas, refine templates

**DoD Fractals as Jidoka Points:**

```
Phase 0: DoD-Context    → Clear stakeholders and constraints?
Phase 1: DoD-Discovery  → Complete and validated PRD?
Phase 2: DoD-Vision     → Business-technical alignment?
Phase 3: DoD-Design     → Consistent architecture?
Phase 4: DoD-Backlog    → User stories follow standard format?
Phase 5: DoD-Plan       → Atomic and verifiable steps?
Phase 6: DoD-Code       → Multi-level validated code?
Phase 7: DoD-Deploy     → Stable feature in production?
```

### Pillar 3: Just-In-Time Learning

Applied to learning, JIT means acquiring knowledge **at the moment of need**, integrated into the workflow—not in separate training sessions.

**Three Dimensions:**
1. **JIT of Context (System → Agent)** — Agent receives exactly the context needed for the current task
2. **JIT of Knowledge (System → Orchestrator)** — When facing new concepts, the system offers—not imposes—contextual knowledge
3. **JIT of Improvement (Experience → Framework)** — Each implementation generates learnings that improve the framework

---

## The Heutagogic Checkpoint

At the end of significant features, RaiSE proposes structured reflection:

1. **KNOWLEDGE** — What did you learn that you didn't know before this implementation?
2. **PROCESS** — What would you change in the flow for the next similar feature?
3. **FRAMEWORK** — Is there something the system should "remember" for the future?
4. **GROWTH** — In what way are you more capable now than before?

---

# PART III: METHODOLOGY

## The Value Flow

### Phase 0: Context
**Purpose:** Establish initial understanding of the problem and environment.
- Discovery meetings with stakeholders
- Identify technologies and constraints
- Explore project (brownfield) or define (greenfield)

**DoD-Context:** Stakeholders identified, main technologies defined, constraints documented

---

### Phase 1: Discovery
**Purpose:** Formalize project requirements from business perspective.
**Artifact:** PRD (Product Requirements Document)

**DoD-Discovery:**
- [ ] Business problem clearly articulated
- [ ] Goals and success metrics defined
- [ ] Explicit scope (in/out)
- [ ] Functional and non-functional requirements listed
- [ ] Assumptions and risks documented

---

### Phase 2: Solution Vision
**Purpose:** Develop high-level vision that aligns business with technical design.
**Agent:** Architect
**Artifact:** Solution Vision Document

**DoD-Vision:**
- [ ] Alignment with business objectives verified
- [ ] High-level components identified
- [ ] Key architectural decisions documented
- [ ] Stakeholder approval

---

### Phase 3: Technical Design
**Purpose:** Translate vision to detailed technical architecture.
**Agent:** Tech Lead
**Artifact:** Technical Design Document

**DoD-Design:**
- [ ] Component architecture documented
- [ ] Data flows defined
- [ ] API contracts specified
- [ ] Data model designed
- [ ] Alternatives considered documented
- [ ] Technical validation completed

---

### Phase 4: Backlog
**Purpose:** Break down design into prioritized features and user stories.
**Artifacts:** Feature Prioritization Matrix, User Stories

**DoD-Backlog:**
- [ ] Features prioritized with scoring
- [ ] MVP defined
- [ ] User stories follow standard format
- [ ] Acceptance criteria in BDD (Given/When/Then)
- [ ] Implementation sequence established

---

### Phase 5: Implementation Plan
**Purpose:** Create deterministic step-by-step plan for each user story.
**Artifact:** Implementation Plan per US

**DoD-Plan:**
- [ ] Each US has implementation plan
- [ ] Steps are atomic and verifiable
- [ ] Dependencies identified
- [ ] Verification criteria included

---

### Phase 6: Development
**Purpose:** Execute implementation guided by the plan.

**Guidelines:**
1. **Context first:** Provide AI with relevant documents
2. **Explainability:** Request approach explanation BEFORE generating
3. **Guided generation:** Use `.cursor/rules/` rules
4. **TDD:** Generate tests before/with code
5. **Critical validation:** NEVER accept code blindly

**DoD-Code:**
- [ ] Code passes unit tests
- [ ] Code meets style standards
- [ ] Code aligned with technical design
- [ ] Code reviewed by human
- [ ] Inline documentation where necessary

---

### Phase 7: UAT & Deploy
**Purpose:** Final validation and deployment to production.

**Multi-level Validation:**
- **Functional:** Does it meet ACs?
- **Structural:** Does it meet style rules?
- **Architectural:** Aligned with patterns?
- **Semantic:** Reflects business rules?

**DoD-Deploy:**
- [ ] UAT approved
- [ ] CI pipeline green
- [ ] Documentation updated
- [ ] Feature in production
- [ ] Retrospective scheduled

---

## The Kata System

Katas are structured processes that encode standards and patterns, inspired by martial arts katas (deliberate practice).

### Level Hierarchy

| Level | Purpose | Use |
|-------|---------|-----|
| **L0** | Meta-katas: fundamental philosophy | Conceptual reference |
| **L1** | Process katas: methodology | Planning, flows |
| **L2** | Component katas: patterns | Analysis, design |
| **L3** | Technical katas: specialization | Advanced implementation |

> ⚠️ **Never execute katas directly.** Always create a specific Implementation Plan using `L1-04-generacion-plan-implementacion-hu.md`.

---

## Adaptation by Context

### For Small Features
```
Phase 1 (Discovery) → Phase 5 (Plan) → Phase 6 (Dev)
```

### For Greenfield Projects
Execute complete flow, dedicating extra time to Phases 0-3.

### For Brownfield/Legacy
Add **legacy scanning** step before Phase 1:
- Existing code analysis (kata L2-02)
- Ecosystem discovery (kata L2-03)
- Generate rules from existing patterns

---

# PART IV: ARCHITECTURE & DATA

## System Architecture

### Components

```
[Developer/Orchestrator]
         │
         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  raise-config   │────▶│   raise-kit     │────▶│   AI Agent      │
│  (Central Repo) │     │   (Local CLI)   │     │   (Copilot,     │
│                 │     │                 │     │    Cursor, etc) │
│  • Rules (.md)  │     │  • Hydrate      │     │                 │
│  • Katas        │     │  • Validate     │     │  • Injected     │
│  • Templates    │     │  • Check DoD    │     │    Context      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       Git                   Local                IDE/CLI
```

### raise-kit (CLI)
- Initialize projects with RaiSE structure
- Sync rules from central repository
- Validate compliance against rules
- Execute validation katas

**Commands:** `raise init`, `raise hydrate`, `raise check`, `raise validate`

### raise-config (Central Repo)
- Store shared rules
- Version validation katas
- Distribute standard templates
- Provide base configuration

**Structure:**
```
raise-config/
├── rules/           # Rules in .mdc format
├── katas/           # Katas L0-L3
├── templates/       # Document templates
├── agents/          # Agent definitions
└── raise.yaml       # Base configuration
```

### .raise/ (Local Context)
```
.raise/
├── memory/
│   ├── constitution.md    # Project principles
│   └── raise-rules.json   # Compiled rules
├── specs/                 # Active specifications
├── plans/                 # Implementation plans
└── raise.yaml             # Local config
```

---

## Data Ontology

### Core Entities

**Constitution** — Immutable principles governing the project  
**Rule** — Directive governing agent behavior or code quality  
**Kata** — Structured process encoding a standard or pattern  
**Spec** — Document describing WHAT to build  
**User Story** — Requirement from user perspective  
**Agent** — AI system configuration executing development tasks  
**Template** — Document structure for generating artifacts

### Entity Relationships

| Origin | Relationship | Destination |
|--------|-------------|-------------|
| Constitution | governs | Rule |
| Rule | applies to | Project |
| Kata | validates | DoD |
| Spec | decomposes into | User Story |
| User Story | implements via | Task |
| Agent | executes | Task |
| Agent | follows | Rule |
| Template | generates | Spec, Plan |

---

## Key Architectural Decisions

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| CLI in Python | Python 3.11+ | AI/ML ecosystem, easy extension |
| Distribution | Git protocol | Platform agnostic, no registry needed |
| Context protocol | MCP (Anthropic) | Emerging standard, multi-agent support |
| Human docs | Markdown | Readable, diff-friendly |
| Machine data | JSON | Fast parsing, universal support |
| Architecture | Local-first | Privacy, offline capability, no cloud costs |
| Quality gates | Fractal DoD | Early problem detection, consistent quality |

---

# PART V: TECHNICAL REFERENCE

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Language | Python 3.11+ | Core CLI |
| CLI Framework | Click | Command interface |
| Terminal UI | Rich | Elegant output |
| HTTP | httpx | Async requests |
| Git | GitPython | Git operations |
| YAML | PyYAML | Config parsing |
| Markdown | markdown-it-py | Document parsing |

## Supported Integrations

| Type | Integration | Status |
|------|-------------|--------|
| **VCS** | GitHub, GitLab, Bitbucket | ✅ Supported |
| **IDE** | Cursor (.mdc rules) | ✅ Supported |
| **IDE** | VS Code (extension) | 📋 Planned |
| **Agent** | Claude (MCP native) | ✅ Supported |
| **Agent** | GitHub Copilot | ✅ Supported |
| **Agent** | Cursor AI | ✅ Supported |
| **Agent** | OpenAI GPT | ✅ Supported |
| **PM** | Jira, Linear | 📋 Planned |

---

## CLI Commands Reference

### raise init
Initialize project with RaiSE structure.
```bash
raise init [--agent <name>] [--template <name>] [--config <url>]
```

### raise hydrate
Sync rules from central repository.
```bash
raise hydrate [--branch <name>] [--force]
```

### raise check
Validate project against active rules.
```bash
raise check [path] [--rules <ids>] [--fix] [--format json] [--strict]
```

### raise validate
Execute validation katas.
```bash
raise validate <kata> [--input <file>] [--dod <phase>]
```

### raise generate
Generate artifacts from templates.
```bash
raise generate <type> [--jira <id>]  # type: spec, story, design, plan
```

---

## Slash Commands (For Agents)

| Command | Purpose |
|---------|---------|
| `/raise.constitution` | Generate/update project constitution |
| `/raise.specify` | Create feature specification |
| `/raise.plan` | Generate technical plan from spec |
| `/raise.tasks` | Break plan into implementable tasks |
| `/raise.implement` | Execute task implementation |
| `/raise.validate` | Validate against DoD or kata |
| `/raise.explain` | Explain reasoning before generating |

---

# PART VI: GLOSSARY

## Core Terms

**Agent** — AI system executing software development tasks under human orchestration (e.g., Copilot, Claude Code, Cursor)

**Constitution** — Immutable principles governing all decisions in a RaiSE project

**Corpus** — Structured document collection providing context to AI agents; "Golden Data"

**Definition of Done (DoD)** — Criteria to consider a phase complete; in RaiSE, DoDs are **fractal** (each flow phase has its own)

**Golden Data** — Verified, structured, canonical information feeding agent context

**Heutagogy** — Self-determined learning theory; the Orchestrator designs their own learning process

**Jidoka (自働化)** — "Automation with human touch"; ability to stop flow when problems are detected

**Just-In-Time Learning** — Acquiring knowledge exactly when needed, integrated into workflow

**Kaizen** — Japanese philosophy of continuous incremental improvement

**Kata** — Structured, documented process encapsulating a standard or pattern

**Orchestrator** — Evolved developer role; defines "What" and "Why", validates "How" generated by agents

**Spec (Specification)** — Document describing WHAT to build, not HOW; the source of truth

**SDD (Spec-Driven Development)** — Paradigm where specifications—not code—are the primary artifact

---

## Principle Reference Format

To reference a RaiSE principle in documents:
- `[RaiSE: Human-Centric]` — Humans define, machines execute
- `[RaiSE: Governance-as-Code]` — Policies versioned in Git
- `[RaiSE: Platform-Agnostic]` — No vendor lock-in
- `[RaiSE: Fractal-DoD]` — Quality in every phase
- `[RaiSE: Heutagogy]` — Teach, don't replace
- `[RaiSE: Kaizen]` — Continuous improvement

---

## Anti-Terms (What NOT to Use)

| Avoid | Use Instead | Reason |
|-------|-------------|--------|
| "Vibe coding" | "Development without spec" | Describes anti-pattern without trivializing |
| "AI coder" | "Development agent" | Human remains the coder |
| "Prompt engineering" | "Context design" | RaiSE is more than prompts |
| "Magic" | "Automated process" | Transparency principle |

---

# PART VII: BUSINESS CONTEXT

## Business Model: Open Core

- **Open source core (MIT):** CLI, base rules, templates, katas
- **Commercial value-add:** Enterprise features, support, SLAs

### Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Community** | Free | Complete CLI, base rules/katas, templates, community support |
| **Pro** | $29/user/mo | + Advanced katas, + Basic analytics, + Priority issues |
| **Enterprise** | Custom | + SSO/SAML, + Audit logging, + SLA, + On-premise, + Custom rules |

---

## Competitive Positioning

RaiSE occupies the intersection of **Developer Tools** and **Governance/Enterprise**:
- Unlike pure AI coding tools (Copilot, Cursor): adds governance layer
- Unlike data/model governance (IBM Watson, Collibra): code/dev focused
- Unlike other SDD tools (Spec Kit, Kiro): offers DoD + Katas + Enterprise features

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Fractal DoDs** | Quality gates per phase, not just at the end |
| **Executable Katas** | Automatic validations of specs and code |
| **Heutagogy** | Active developer training (most tools focus on replacement) |
| **Git-Native** | No proprietary APIs; Git as transport |
| **Platform Agnostic** | GitHub, GitLab, Bitbucket indistinctly |

---

## Market Context

**Why Now:**
1. AI tools mainstream: 84% of devs using AI coding
2. Quality concerns rising: Satisfaction dropped to 60%
3. Regulation imminent: EU AI Act 2025
4. Open market position: No governance-as-code leader

---

# PART VIII: CURRENT STATE & ROADMAP

## What Exists Today

### Documentation
- ✅ Base corpus (22 documents)
- ✅ Golden data framework defined
- ✅ Core templates (28 templates)
- ✅ Katas (22 katas L0-L3)
- ✅ Base rules (7 .mdc rules)

### Code
- ❌ raise-kit CLI (pending)
- ❌ raise-mcp server (pending)
- ✅ raise-commons repository

---

## Roadmap

### v0.1.0 - Foundation (Q1 2025)
- CLI basic (init, check, hydrate)
- Support for 5 main agents
- Core templates
- Documentation

### v0.2.0 - Quality Gates (Q2 2025)
- Complete fractal DoDs
- Validation katas (L2, L3)
- Centralized raise-config
- Analytics (local)

### v0.3.0 - Enterprise Preview (Q3 2025)
- raise-mcp (MCP Server)
- Multi-agent context support
- SSO integration (planning)
- Audit logging

### v1.0.0 - Production (Q4 2025)
- Stable API (semver commitment)
- SOC2 Type I preparation
- Jira/Linear integrations
- Community katas marketplace

---

# PART IX: WORKING WITH RAISE

## Examples: Correct Usage Patterns

### Pattern 1: Feature in Existing Project

```
1. raise init --agent cursor        # If not initialized
2. /raise.specify [description]     # Create spec
3. /raise.plan @spec.md             # Generate technical plan
4. /raise.tasks @plan.md            # Break into tasks
5. /raise.implement @task-001.md    # Execute implementation
6. /raise.validate dod-code         # Validate
```

### Pattern 2: Greenfield Project

```
1. raise init --template microservice
2. /raise.constitution              # Generate constitution
3. Create PRD using template
4. /raise.specify --template solution-vision
5. /raise.plan --template tech-design
6. For each MVP feature: specify → plan → tasks → implement → validate
```

### Pattern 3: Legacy Project Adoption

```
1. raise init --skip-constitution
2. Run SAR katas (L2-02, L2-03)     # Analyze existing code
3. /raise.constitution --analyze-existing  # Respect existing patterns
4. Extract rules from detected patterns
5. Apply RaiSE only to NEW features (don't force changes on legacy)
```

### Pattern 4: Multi-Project Governance

```
1. Create central org-raise-config repo
2. Each repo: raise.yaml → config.repo: <org-config-url>
3. Each repo: raise hydrate
4. CI/CD: raise check --strict
```

---

## Anti-Patterns: What NOT to Do

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Vague specs ("improve search") | No criteria → AI invents → misses expectations |
| Skip phases (`/raise.implement` directly) | No context → arbitrary decisions |
| Ignore DoD | Problems detected late or never |
| Accept code without reviewing | Violates Heutagogy; human loses ownership |

---

## Recommended Practices

### Explainability First
```
Before implementing X, explain:
1. Your proposed approach
2. Alternatives considered
3. Trade-offs
```

### Continuous Validation
After each phase:
```
/raise.validate dod-{phase} @artifact.md
```

### Iteration with Context
```
Given the previous feedback, adjust the design for [specific change].
```

---

# APPENDIX: SECURITY & COMPLIANCE

## Security Model

### Critical Assets
| Asset | Classification | Controls |
|-------|---------------|----------|
| Source code | Confidential | Local-first, no cloud |
| API keys/secrets | Critical | Never in RaiSE files |
| Rules (.mdc) | Internal | Versioned, code review |
| Specs/designs | Internal | Project-level access |

### Local-First Architecture
- **Principle:** Data never leaves local environment
- **Implementation:** No cloud backend, everything is Git-native
- **MCP Server:** Runs locally (no auth required)

## Compliance Support

RaiSE helps organizations comply with EU AI Act through:
- **Traceability:** AI decision auditing in Git
- **Governance:** Policies as versioned code
- **Documentation:** Specs and plans as evidence
- **Human oversight:** Heutagogy principle

---

*This document is the source of truth for RaiSE context. Provide it to AI agents to enable consistent, governance-aligned development assistance.*
