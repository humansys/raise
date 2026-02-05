# Team AI Memory & Sharing Patterns

> Research ID: RES-TEAM-MEM-001
> Date: 2026-02-05
> Researcher: Rai
> Focus: How AI coding tools handle team/shared context and memory for E14 design

## Summary

Current AI coding tools are rapidly evolving team features, but most remain focused on **shared rules/conventions** rather than **shared learning**. The emerging research pattern is a **dual-tier memory architecture** (private + shared) with **namespace-based multi-tenancy** and **dynamic access control**. Key insight: treating memory as structured, attributable data with clear provenance enables team collaboration while preserving privacy. RaiSE should adopt a federated approach where patterns flow up to team level through explicit promotion, not automatic aggregation.

---

## Current Tool Landscape

### Cursor Business/Teams

**Evidence Level: Secondary (official blog, changelog)**

**Team Features:**
- Shared chats and commands across team members
- Centralized billing, usage analytics, RBAC
- Team rules set once in dashboard, available to all members
- $40/user/month Teams tier (collaboration requires minimum Teams tier)

**Memory Architecture:**
- "Memories" feature stores facts from conversations for future sessions
- Currently **per-project** memory, not organization-wide
- Future roadmap: organization-wide AI memory across all codebases + internal docs

**Team Learning Status:**
- Rules are shared, but **learned patterns are not**
- No mechanism for promoting individual learnings to team level
- Memory is conversational context, not structured knowledge

**Source:** [Cursor Enterprise Review](https://www.superblocks.com/blog/cursor-enterprise), [Cursor Enterprise](https://cursor.com/enterprise)

---

### GitHub Copilot Enterprise

**Evidence Level: Primary (official documentation)**

**Team Features:**
- Knowledge Bases (being sunset Nov 2025) → replaced by **Copilot Spaces**
- Organization custom instructions for coding agent
- Fine-tuned private models for code completion
- Codebase indexing for organization-level understanding

**Memory Architecture:**
- Copilot Spaces: Organize context with repos, code, PRs, issues, notes, images
- Spaces can be created by any user, not just admins
- Custom instructions now support organization defaults

**Team Learning Status:**
- Spaces are **manually curated**, not automatically learned
- No velocity/calibration sharing
- Focus on **context provision**, not pattern extraction

**Source:** [Copilot Knowledge Bases](https://docs.github.com/en/enterprise-cloud@latest/copilot/customizing-copilot/managing-copilot-knowledge-bases), [Copilot Spaces](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/provide-context/use-knowledge-bases), [Org Custom Instructions](https://github.blog/changelog/2025-11-05-copilot-coding-agent-supports-organization-custom-instructions/)

---

### Continue.dev

**Evidence Level: Secondary (blog, documentation)**

**Team Features:**
- **Continue Agents**: Shareable, remixable AI definitions
- Team creates agent in Hub → entire team invokes from CLI or Mission Control
- Agents carry custom context, rules, tool permissions

**Memory Architecture:**
- Per-project configuration (models, context providers, rules, slash commands)
- MCP (Model Context Protocol) integration for external data sources
- Context providers via `@` mentions

**Team Learning Status:**
- Agents are **defined**, not learned
- Good pattern for **codifying conventions**, not learning from execution
- Open source, highly configurable

**Source:** [Continue Agents](https://blog.continue.dev/what-are-continue-agents-any-workflow-your-teams-way/), [Context Providers](https://docs.continue.dev/customize/deep-dives/custom-providers)

---

### Aider

**Evidence Level: Primary (documentation, code)**

**Team Features:**
- **CONVENTIONS.md** file for team coding standards
- Community-contributed convention files repository
- Load via `--read CONVENTIONS.md` (read-only, cached)

**Memory Architecture:**
- File-based conventions (markdown)
- No persistent memory beyond session
- Conventions forwarded to LLM in context

**Team Learning Status:**
- **Manual convention sharing** via committed files
- No automatic learning or pattern extraction
- Simple but effective for explicit standards

**Source:** [Aider Conventions](https://aider.chat/docs/usage/conventions.html), [Conventions Repo](https://github.com/Aider-AI/conventions)

---

### Windsurf (Codeium)

**Evidence Level: Secondary (official site, reviews)**

**Team Features:**
- Granular rules files in `.windsurf/rules/`
- Memory remembers coding style, team preferences, project rules
- Admin-controlled model selection for teams
- SOC 2 Type II, FedRAMP High, ZDR defaults

**Memory Architecture:**
- Rules: Always-on, @mentionable, or attached to file globs
- Cascade carries context from previous sessions
- Memory persists across all development tasks

**Team Learning Status:**
- Rules are **defined**, memory is **conversational**
- No explicit team learning aggregation
- Enterprise focus on governance/compliance

**Source:** [Windsurf](https://windsurf.com/), [Windsurf Enterprise](https://windsurf.com/enterprise)

---

### Augment Code

**Evidence Level: Secondary (official blog, marketing)**

**Team Features:**
- **Context Engine**: Live understanding of entire stack
- 200k-token context engine
- Slack integration for team Q&A
- SOC 2 Type II, no training on customer code

**Memory Architecture:**
- Real-time retrieval (no learning on customer code)
- Context includes: code, dependencies, architecture, history
- "Institutional memory" through context, not learned patterns

**Team Learning Status:**
- **Context-first**, not learning-first
- Turns "tribal knowledge into shared intelligence" via indexing
- No pattern extraction or calibration sharing

**Source:** [Augment Code](https://www.augmentcode.com), [Meet Augment](https://www.augmentcode.com/blog/meet-augment-code-developer-ai-for-teams)

---

### Tabnine Enterprise

**Evidence Level: Secondary (blog, documentation)**

**Team Features:**
- **Enterprise Context Engine**: Learns org architecture, frameworks, standards
- Private customized model retrained on org code
- Shared custom commands (`.tabnine_commands` in repo)
- Jira, design doc integration

**Memory Architecture:**
- Organization-level model fine-tuning
- Guardrails for coding standards, architecture, security
- Context from code repos + external systems

**Team Learning Status:**
- **Model-level learning** on org codebase (unique approach)
- Guardrails are defined, not extracted
- Closest to "team learns" but through fine-tuning

**Source:** [Tabnine Platform](https://www.tabnine.com/platform/), [Personalization](https://docs.tabnine.com/main/welcome/readme/personalization)

---

### OpenClaw

**Evidence Level: Secondary (documentation, GitHub)**

**Team Features:**
- Multi-agent routing to isolated workspaces
- Per-agent: files, AGENTS.md, SOUL.md, USER.md, config
- Auth profiles per-agent (not shared)
- OpenclawInterSystem (OIS) for multi-agent collaboration

**Memory Architecture:**
- Deterministic routing (bindings, most-specific wins)
- Shared storage via VPS/NAS/cloud
- Agent registration, Gateway API for messaging

**Team Learning Status:**
- **Isolation-first** architecture
- Collaboration through explicit sharing, not automatic
- Good pattern for privacy-preserving team setup

**Source:** [OpenClaw Multi-Agent](https://docs.openclaw.ai/concepts/multi-agent), [OpenclawInterSystem](https://github.com/Mayuqi-crypto/OpenclawInterSystem)

---

## Memory Architecture Patterns

### Letta (formerly MemGPT)

**Evidence Level: Primary (documentation, research paper)**

**Architecture:**
```
┌─────────────────────────────────────┐
│           Context Window            │
│  ┌──────────┐  ┌──────────────┐    │
│  │  Persona │  │ User Info    │    │  ← Core Memory (RAM-like)
│  │  Block   │  │ Block        │    │    Always in context
│  └──────────┘  └──────────────┘    │    2,000 char limit/block
└─────────────────────────────────────┘
              │
              ▼ (agent tools)
┌─────────────────────────────────────┐
│        External Storage             │
│  ┌────────────┐ ┌────────────────┐ │
│  │  Archival  │ │  Recall        │ │  ← Disk-like storage
│  │  Memory    │ │  Memory        │ │    Vector DB backed
│  │  (facts)   │ │  (history)     │ │    Searchable
│  └────────────┘ └────────────────┘ │
└─────────────────────────────────────┘
```

**Key Innovation: Self-Editing Memory**
- Agent actively manages its own memory using tools
- Can edit persona, update user info, archive facts
- Memory blocks are structured XML in prompt

**Persistence:**
- All state persisted by default (DB backend)
- Recall memory saves to disk automatically
- Full interaction history searchable

**Team Implications:**
- Architecture supports multi-user (separate user blocks)
- No explicit team memory tier yet
- Pattern: **structured blocks** + **agent-driven management**

**Source:** [Letta Memory Overview](https://docs.letta.com/guides/agents/memory/), [MemGPT Research](https://docs.letta.com/concepts/memgpt/)

---

### LangMem

**Evidence Level: Primary (documentation, GitHub)**

**Memory Types:**
1. **Semantic Memory**: Facts, knowledge (collections or profiles)
2. **Episodic Memory**: Interaction context, decision patterns
3. **Procedural Memory**: How to perform tasks (stored in prompts)

**Namespace Architecture:**
```python
# Multi-tenant isolation via namespaces
namespace = ("org_id", "team_id", "user_id", "memory_type")

# Example scopes:
("email_assistant", "lance", "examples")  # User-specific
("email_assistant", "*", "procedures")     # Shared procedures
```

**Multi-User Support:**
- All memories namespaced
- Multi-level: org → team → user → memory type
- Prevents cross-over of user memories
- Memories can be scoped to routes, users, teams, or global

**Integration:**
- Native LangGraph integration
- MongoDB Store for long-term persistence
- Tools for extraction, optimization, retrieval

**Source:** [LangMem Docs](https://langchain-ai.github.io/langmem/), [LangMem Conceptual Guide](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)

---

### Collaborative Memory Research (ICML 2025)

**Evidence Level: Primary (peer-reviewed research)**

**Framework:** Multi-user, multi-agent with dynamic access control

**Architecture:**
```
┌─────────────────────────────────────┐
│          Private Memory             │  ← Fragments visible only to
│  User A fragments | User B frags    │    originating user
└─────────────────────────────────────┘
              │
              ▼ (write policy)
┌─────────────────────────────────────┐
│          Shared Memory              │  ← Selectively shared
│    Fragments with provenance:       │    Per access control
│    - Contributing agents            │
│    - Accessed resources             │
│    - Timestamps                     │
└─────────────────────────────────────┘
              │
              ▼ (read policy)
┌─────────────────────────────────────┐
│     Memory View (per agent)         │  ← Dynamically constructed
│   Tailored to current permissions   │    based on access graph
└─────────────────────────────────────┘
```

**Key Innovations:**
1. **Provenance Attributes**: Immutable metadata on each fragment
2. **Bipartite Access Graphs**: Users ↔ Agents ↔ Resources
3. **Policy Levels**: System-wide, agent-specific, user-specific
4. **Time-Evolving**: Access controls can change over time

**Granularity:** First formulation with fine-grained access asymmetries

**Source:** [Collaborative Memory Paper](https://arxiv.org/abs/2505.18279)

---

## Shared vs Private Boundary

### What Should Be Shared (Team Level)

| Category | Examples | Rationale |
|----------|----------|-----------|
| **Coding Conventions** | Style rules, naming patterns, architecture guidelines | Universal standards |
| **Patterns** | Successful approaches, "this worked for X" | Team learning |
| **Procedures** | How to deploy, test, review | Process standardization |
| **Calibration** (anonymized) | Aggregate velocity trends | Planning accuracy |
| **Facts** | Architecture decisions, tech choices | Institutional memory |

### What Should Stay Private (Individual Level)

| Category | Examples | Rationale |
|----------|----------|-----------|
| **Communication Preferences** | Verbosity, language, style | Personal |
| **Working Style** | Session patterns, focus areas | Individual productivity |
| **Raw Velocity** | Specific task times | Performance sensitivity |
| **Mistakes/Learning** | Individual errors, corrections | Psychological safety |
| **Personal Context** | Current focus, blockers | Privacy |

### Promotion Pattern

```
Individual Learning
       │
       ▼ (explicit promotion)
┌──────────────────────────┐
│  Review & Anonymization  │  ← Human or AI curation
│  - Remove personal data  │
│  - Generalize pattern    │
│  - Add provenance        │
└──────────────────────────┘
       │
       ▼
Team Knowledge Base
```

**Key Principle:** Learning flows **up** through explicit promotion, not automatic aggregation.

---

## Conflict Resolution Patterns

### From Multi-Agent Research

1. **Consensus Mechanisms**
   - When agents have conflicting info, determine authoritative source
   - Propagate corrections to agents with outdated knowledge

2. **Priority-Based Resolution**
   - Resolve based on: agent role, information recency, confidence level
   - Specialized agent > general-purpose agent on domain topics

3. **Semantic Conflict Resolution**
   - Event sourcing: Capture reasoning behind each write
   - Arbiter agents review conflicts and generate reconciliations

4. **Rollback and Recovery**
   - Revert to known-good state on inconsistency
   - Retry with better conflict resolution

### Recommended for RaiSE

```
Pattern Conflict:
1. Detect: Two patterns contradict
2. Context Check: Are they for different contexts?
   → Yes: Both valid, add context discriminator
   → No: Continue to 3
3. Recency: Which is more recent?
4. Success Rate: Which has better outcomes?
5. Escalate: Human decision if still unclear
6. Archive: Keep losing pattern with "superseded" status
```

---

## Anti-Patterns / Failures

### Enterprise Deployment Failures

**Evidence Level: Secondary (industry analysis)**

1. **Context Without Orchestration**
   - Failure: Agents lack structured codebase understanding
   - Fix: Context as engineering surface (graph, conventions, history)

2. **No Training Strategy**
   - Failure: "Deploy and self-learn" doesn't work
   - Fix: Explicit workflow restructuring, not just tool addition

3. **Individual Output vs Organizational Outcome**
   - Failure: 21% more tasks but same organizational velocity
   - Fix: Measure team outcomes, not individual metrics

4. **Code Quality Degradation**
   - Failure: AI-generated code has errors up to 52% of time
   - Fix: Validation gates, peer review, explicit standards

5. **Unvetted Dependencies**
   - Failure: Subtle license violations, undocumented modules
   - Fix: Guardrails, security scanning, provenance tracking

**Source:** [VentureBeat Analysis](https://venturebeat.com/ai/why-most-enterprise-ai-coding-pilots-underperform-hint-its-not-the-model), [EclipseSource](https://eclipsesource.com/blogs/2025/06/11/why-ai-coding-fails-in-enterprises/)

### Privacy Anti-Patterns

1. **Permission Inheritance**
   - AI agents inherit user permissions, see all accessible data
   - No understanding of context boundaries

2. **Assumed Confidentiality**
   - Users treat AI interactions as private even when shared
   - Explicit privacy boundaries needed

**Source:** [Metomic Analysis](https://www.metomic.io/resource-centre/how-are-ai-agents-exposing-your-organizations-most-sensitive-data-through-inherited-permissions)

---

## Recommendations for RaiSE E14

### Core Architecture

```
┌────────────────────────────────────────────────────┐
│                  Personal Layer                     │
│  ~/.rai/                                           │
│  ├── developer.yaml (communication, skills, prefs) │
│  ├── memory/                                       │
│  │   ├── patterns.jsonl (personal patterns)        │
│  │   ├── calibration.jsonl (personal velocity)     │
│  │   └── sessions/                                 │
│  └── identity/                                     │
└────────────────────────────────────────────────────┘
              │
              ▼ (explicit promotion + anonymization)
┌────────────────────────────────────────────────────┐
│                   Team Layer                        │
│  .rai/ (project root)                              │
│  ├── team/                                         │
│  │   ├── patterns.jsonl (promoted patterns)        │
│  │   ├── calibration.jsonl (aggregate velocity)    │
│  │   ├── conventions.md (coding standards)         │
│  │   └── decisions.jsonl (architecture)            │
│  ├── identity/ (Rai's identity)                    │
│  └── memory/ (project memory)                      │
└────────────────────────────────────────────────────┘
              │
              ▼ (optional federation)
┌────────────────────────────────────────────────────┐
│               Organization Layer                    │
│  (Future: central server or shared repo)           │
│  - Cross-project patterns                          │
│  - Organization-wide conventions                   │
│  - Aggregate calibration                           │
└────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Promotion over Aggregation**
   - Individual patterns don't automatically become team patterns
   - Explicit `/promote-pattern` command with review
   - Preserves privacy, ensures quality

2. **Namespace-Based Isolation**
   - Follow LangMem pattern: `(project, team, user, type)`
   - Clear boundary between personal and shared
   - Query by scope: `--scope personal|team|org`

3. **Provenance on Everything**
   - Every pattern has: author, date, source, success_count
   - Enables trust calibration and conflict resolution
   - Anonymization removes author for team promotion

4. **Git-Native Team Layer**
   - Team patterns in `.rai/team/` committed to repo
   - Version controlled, auditable, mergeable
   - No external server required for MVP

5. **Conflict Resolution Strategy**
   - Context-first: Different contexts can have different patterns
   - Recency + success rate for same context
   - Human escalation via PR review

6. **Privacy Boundary**
   - Personal: communication style, raw velocity, mistakes
   - Team: conventions, successful patterns, aggregate calibration
   - Organization (future): cross-project patterns

### Implementation Priorities for E14

| Priority | Feature | Rationale |
|----------|---------|-----------|
| P0 | Team patterns schema | Foundation for sharing |
| P0 | `/promote-pattern` command | Explicit promotion flow |
| P1 | Aggregate calibration | Team planning accuracy |
| P1 | Conflict detection | Prevent contradictions |
| P2 | Anonymous attribution | Privacy-preserving sharing |
| P2 | Organization layer design | Future scalability |

### What NOT to Build

- Automatic pattern aggregation (privacy risk)
- Real-time sync (complexity, offline-first violated)
- Individual velocity comparison (psychological safety)
- Model fine-tuning on team code (IP concerns)

---

## Evidence Catalog

### Primary Sources (Documentation, Code, Research)

| Source | Type | Rating |
|--------|------|--------|
| [Letta Memory Docs](https://docs.letta.com/guides/agents/memory/) | Documentation | Very High |
| [LangMem Docs](https://langchain-ai.github.io/langmem/) | Documentation | Very High |
| [Collaborative Memory Paper (ICML 2025)](https://arxiv.org/abs/2505.18279) | Research | Very High |
| [Aider Conventions](https://aider.chat/docs/usage/conventions.html) | Documentation | Very High |
| [Copilot Enterprise Docs](https://docs.github.com/en/enterprise-cloud@latest/copilot) | Documentation | Very High |

### Secondary Sources (Official Blogs, Marketing)

| Source | Type | Rating |
|--------|------|--------|
| [Cursor Enterprise Review](https://www.superblocks.com/blog/cursor-enterprise) | Analysis | High |
| [Augment Code Blog](https://www.augmentcode.com/blog/meet-augment-code-developer-ai-for-teams) | Official Blog | High |
| [Tabnine Personalization](https://docs.tabnine.com/main/welcome/readme/personalization) | Documentation | High |
| [Continue Agents Blog](https://blog.continue.dev/what-are-continue-agents-any-workflow-your-teams-way/) | Official Blog | High |
| [VentureBeat Analysis](https://venturebeat.com/ai/why-most-enterprise-ai-coding-pilots-underperform-hint-its-not-the-model) | Industry Analysis | Medium |

### Tertiary Sources (Community, Reviews)

| Source | Type | Rating |
|--------|------|--------|
| [MongoDB Multi-Agent Memory](https://www.mongodb.com/company/blog/technical/why-multi-agent-systems-need-memory-engineering) | Technical Blog | Medium |
| [Privacy Boundaries Research](https://arxiv.org/abs/2509.21712) | Research | Medium |

---

## Open Questions for E14 Design

1. **Calibration Aggregation**: How do we aggregate velocity without revealing individual performance?
2. **Pattern Quality Gate**: What makes a pattern "good enough" for team promotion?
3. **Offline-First Sync**: How do team patterns sync when developers work offline?
4. **Cross-Repo Patterns**: Should patterns from one project apply to another?
5. **Rai Identity per Team**: Does each team have its own Rai, or shared?

---

*Research complete. Ready for E14 epic design synthesis.*
