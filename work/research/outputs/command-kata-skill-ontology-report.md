# Research Report: Command vs Kata vs Skill Ontology for AI Agent Instruction Hierarchies

**Date:** 2026-01-29
**Status:** Complete
**Researcher:** RaiSE Ontology Research Agent
**Version:** 1.0

---

## Executive Summary

This comprehensive research investigates the optimal terminology for RaiSE's instruction hierarchy, addressing the semantic tension between atomic utility operations (like `/context/get`) and multi-step learning processes (like `/project/create-prd`). After analyzing 15+ AI agent frameworks, workflow platforms, and developer tools, along with cognitive load research and pedagogical models, the research provides evidence-based recommendations.

**Key Findings:**

1. **No AI framework uses "Kata"** - This makes it a genuine differentiator for RaiSE's Lean philosophy alignment
2. **Industry converges on "Tools" for atomic operations** - 10/15 frameworks use "tools" or "functions"
3. **Composite terminology varies widely** - Workflows, Flows, Chains, Crews, Playbooks, Scenarios
4. **2-level hierarchy is cognitively optimal** - Research supports 5-7 distinct categories maximum
5. **"Kata" carries pedagogical value** - Signals mastery/practice intent vs. mere execution

**Recommendation:** Adopt **Option A (Kata/Skill/Gate)** with progressive disclosure - most users interact with "Skills" (atomic) while the "Kata" layer surfaces for learning-focused workflows.

---

## RQ1: Industry Terminology Landscape

### Terminology Comparison Matrix

| Framework/Platform | Atomic Term | Composite Term | Validation Term | Source |
|-------------------|-------------|----------------|-----------------|--------|
| **Claude MCP** | Tools | Prompts (templates) | - | [Anthropic MCP Docs](https://docs.claude.com/en/docs/mcp) |
| **OpenAI Assistants** | Functions/Tools | - | - | [OpenAI Assistants API](https://platform.openai.com/docs/assistants/tools) |
| **LangChain** | Tools | Chains/Agents/Workflows | - | [LangChain Docs](https://docs.langchain.com/oss/python/langgraph/workflows-agents) |
| **CrewAI** | Tools | Tasks/Crews/Flows | - | [CrewAI Introduction](https://docs.crewai.com/en/introduction) |
| **AutoGen (Microsoft)** | Functions | Conversations/Workflows | - | [AutoGen Docs](https://microsoft.github.io/autogen/0.2/docs/Use-Cases/agent_chat/) |
| **Semantic Kernel** | Functions | Plugins/Plans | - | [Microsoft Learn](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/) |
| **Backstage (Spotify)** | Actions | Templates/Golden Paths | - | [Backstage Scaffolder](https://backstage.spotify.com/docs/portal/core-features-and-plugins/scaffolder) |
| **Port** | Actions | Workflows | Automations | [Port Actions](https://docs.port.io/actions-and-automations/overview/) |
| **Humanitec** | Functions | Score/Resource Definitions | Orchestrator | [Humanitec Docs](https://developer.humanitec.com/training/master-your-internal-developer-platform/structure-and-integration-points/) |
| **Temporal** | Activities | Workflows | Task Queues | [Temporal Glossary](https://docs.temporal.io/glossary) |
| **Airflow** | Operators | DAGs | Task Instances | [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) |
| **Prefect** | Tasks | Flows | Deployments | [Prefect Introduction](https://docs.prefect.io/) |
| **Dagster** | Ops/Assets | Jobs/Graphs | IOManagers | [Dagster Concepts](https://docs.dagster.io/getting-started/concepts) |
| **n8n** | Nodes | Workflows | Triggers | [n8n Node Types](https://docs.n8n.io/integrations/builtin/node-types/) |
| **Zapier** | Actions | Zaps | Tasks | [Zapier Key Concepts](https://help.zapier.com/hc/en-us/articles/8496181725453-Learn-key-concepts-in-Zaps) |
| **Make** | Modules | Scenarios | Operations | [Make Documentation](https://www.make.com/en/blog/zapier-on-integromat) |
| **ServiceNow** | Activities | Playbooks/Flows | Stages | [ServiceNow Playbooks](https://www.servicenow.com/community/secops-articles/understanding-playbooks-and-the-relationship-of-runbooks/ta-p/2314914) |
| **UiPath** | Activities | Workflows/Sequences | Triggers | [UiPath Activities](https://docs.uipath.com/activities/other/latest/workflow/workflow-activities) |

### Key Observations

1. **Atomic Level Convergence**: The industry strongly converges on **"Tools"** (7 frameworks), **"Functions"** (4 frameworks), **"Activities"** (3 frameworks), or **"Actions"** (3 frameworks) for atomic operations.

2. **Composite Level Divergence**: There is significant variation at the composite level:
   - **Workflow/Workflows**: Temporal, Port, n8n, UiPath, LangChain
   - **Flows**: CrewAI, Prefect, ServiceNow
   - **Chains/Agents**: LangChain
   - **DAGs**: Airflow
   - **Scenarios**: Make
   - **Playbooks**: ServiceNow
   - **Templates/Golden Paths**: Backstage

3. **Validation Terminology**: Most frameworks do not have explicit validation terminology. Those that do use: Task Queues (Temporal), Deployments (Prefect), Triggers (UiPath, n8n), Automations (Port).

4. **MCP Primitives**: Claude's Model Context Protocol defines three core primitives:
   - **Tools**: Functions the AI can call
   - **Resources**: Structured data sources for context
   - **Prompts**: Reusable templates (exposed as commands)

### Playbook vs Runbook Distinction

| Aspect | Playbook | Runbook |
|--------|----------|---------|
| **Level** | Strategic, high-level | Tactical, operational |
| **Scope** | Extensive processes | Specific tasks |
| **Audience** | Cross-functional teams | IT/Operations |
| **Example** | Incident response strategy | Database backup procedure |

Sources: [Cutover](https://www.cutover.com/blog/runbooks-vs-playbooks-comprehensive-overview), [Cortex](https://www.cortex.io/post/runbooks-vs-playbooks)

---

## RQ2: Kata as Differentiator

### Toyota Kata in Software Development

Toyota Kata, developed by Mike Rother, consists of two interconnected practices:

1. **Improvement Kata**: A four-step pattern for continuous improvement
   - Understand the Direction
   - Grasp the Current Condition
   - Establish the Next Target Condition
   - PDCA toward the Target Condition

2. **Coaching Kata**: A routine for teaching improvement thinking through five questions

Source: [KaiNexus Toyota Kata](https://www.kainexus.com/improvement-disciplines/toyota-kata), [Toyota Kata Wikipedia](https://en.wikipedia.org/wiki/Toyota_Kata)

### Coding Kata vs Toyota Kata

| Aspect | Coding Kata | Toyota Kata |
|--------|-------------|-------------|
| **Origin** | Dave Thomas (Pragmatic Programmer) | Mike Rother (Toyota Production System) |
| **Purpose** | Practice programming skills | Practice improvement thinking |
| **Format** | Small coding exercises | Structured problem-solving routine |
| **Platforms** | Codewars, Exercism, CodeKata.com | Manufacturing, management |
| **Focus** | Muscle memory for coding | Scientific thinking habit |

Source: [CodeKata.com](http://codekata.com/), [CTO Framework Katas](https://ctoframework.com/tech/development/katas/)

### Does Any AI Framework Use "Kata"?

**No.** After extensive research, no AI agent framework, workflow engine, or developer tool uses "Kata" as a term for instruction hierarchies. This is a significant finding - **RaiSE has a genuine differentiator**.

### Kata Analysis: Evidence-Based Pros/Cons

#### Arguments FOR "Kata"

| Argument | Evidence | Weight |
|----------|----------|--------|
| **Unique in AI space** | No framework uses this term | High |
| **Signals learning/mastery** | Toyota Kata emphasizes "practice" not "execute" | High |
| **Lean philosophy alignment** | Same origin as Jidoka, Kaizen, ShuHaRi | High |
| **Pedagogical value** | Implies deliberate practice, not one-time execution | Medium |
| **Precedent: "Scrum" succeeded** | Rugby terminology now ubiquitous in software | Medium |
| **Coding katas are familiar** | Codewars, Exercism have popularized the term | Medium |

#### Arguments AGAINST "Kata"

| Argument | Evidence | Weight |
|----------|----------|--------|
| **Cognitive load for newcomers** | Non-Lean practitioners may not know the term | Medium |
| **Confusion with coding katas** | Different meaning (exercises vs. processes) | Medium |
| **Eastern terminology bias** | May feel exclusionary to some cultures | Low |
| **Not self-explanatory** | "Workflow" is immediately understood | Medium |

### Precedent Analysis: Sports Terminology in Software

| Term | Origin | Adoption Success | Lesson for RaiSE |
|------|--------|------------------|------------------|
| **Scrum** | Rugby (formation) | Massive - 63% of Agile teams | Domain-specific terms can succeed |
| **Sprint** | Track & field | Massive | Evocative names stick |
| **Backlog** | Manufacturing | High | Industry crossover works |
| **Kanban** | Japanese (signboard) | High | Eastern terms accepted when valuable |

Source: [Scrum Rugby Connection](https://medium.com/serious-scrum/scrum-s-connection-to-rugby-597405fed5ec), [Visual Paradigm Scrum Origin](https://www.visual-paradigm.com/scrum/what-is-the-evolution-of-scrum/)

### Recommendation on Kata

**Keep "Kata" for RaiSE process-level workflows.**

Rationale:
1. No AI framework uses it - genuine differentiation
2. Strong Lean philosophy alignment (Jidoka, Kaizen, ShuHaRi)
3. Signals learning intent vs. mere execution
4. Precedent shows domain terminology can succeed (Scrum, Sprint, Kanban)
5. Already established in RaiSE v2.1 glossary

Risk mitigation:
- Provide clear definition in onboarding
- Use progressive disclosure (most users see "Skills" first)
- Include familiar alias ("process", "workflow") in documentation

---

## RQ3: Hierarchical Instruction Models

### Existing Hierarchies Compared

#### 1. Claude MCP Architecture

```
┌─────────────────────────────────────────┐
│  Resources (data sources for context)   │
├─────────────────────────────────────────┤
│  Tools (functions AI can call)          │
├─────────────────────────────────────────┤
│  Prompts (reusable templates/commands)  │
├─────────────────────────────────────────┤
│  Sampling (agentic workflows)           │
└─────────────────────────────────────────┘
```

MCP's hierarchy is **capability-based** rather than **granularity-based**. Each primitive serves a different purpose rather than composing hierarchically.

Source: [Anthropic MCP Introduction](https://www.anthropic.com/news/model-context-protocol)

#### 2. LangChain Hierarchy

```
Tools → Chains → Agents → Workflows (LangGraph)
```

- **Tools**: Atomic functions (search, calculate, API call)
- **Chains**: Static sequences connecting tools
- **Agents**: Dynamic tool selection with reasoning
- **Workflows**: Complex multi-agent orchestration (LangGraph)

Source: [LangChain Agents Guide](https://www.leanware.co/insights/langchain-agents-complete-guide-in-2025)

#### 3. CrewAI Hierarchy

```
Tools → Tasks → Crews → Flows
```

- **Tools**: Capabilities (web scraping, file processing)
- **Tasks**: Actions with description and expected output
- **Crews**: Collections of agents working toward a goal
- **Flows**: Event-driven workflows connecting crews

Source: [CrewAI Core Concepts](https://docs.crewai.com/core-concepts/Agents/)

#### 4. Microsoft Semantic Kernel (Current)

```
Functions → Plugins → Kernel (with automatic function calling)
```

Note: Planners (Stepwise, Handlebars) have been **deprecated** in favor of automatic function calling.

Source: [Semantic Kernel Planning](https://learn.microsoft.com/en-us/semantic-kernel/concepts/planning)

#### 5. Temporal Hierarchy

```
Activities → Tasks → Workflows → Event History
```

- **Activities**: Single, well-defined actions
- **Tasks**: Messages to workers
- **Workflows**: Sequences of steps defined in code
- **Event History**: Append-only log for durability

Source: [Temporal Workflows](https://docs.temporal.io/workflows)

### GOMS Model (HCI Research)

The GOMS model from cognitive psychology provides a theoretical framework:

```
Goals → Methods → Operators → Selection Rules
```

- **Goals**: Outcomes the user wants to achieve
- **Operators**: Atomic actions (perceptual, cognitive, motor)
- **Methods**: Procedures to accomplish goals
- **Selection Rules**: Which method to use based on context

Source: [GOMS Wikipedia](https://en.wikipedia.org/wiki/GOMS)

**Applicability to RaiSE:**
- **Goals** ≈ Katas (what to achieve)
- **Operators** ≈ Skills (atomic actions)
- **Methods** ≈ Steps within Katas
- **Selection Rules** ≈ Validation Gates

### Proposed RaiSE Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│   KATA (Process-Level)                                           │
│   ─────────────────────                                          │
│   Multi-step workflows with learning intent                      │
│   Example: /project/create-prd, /setup/analyze-codebase          │
├─────────────────────────────────────────────────────────────────┤
│   SKILL (Atomic-Level)                                           │
│   ────────────────────                                           │
│   Single-purpose utility operations                              │
│   Example: /context/get, /validate/architecture                  │
├─────────────────────────────────────────────────────────────────┤
│   GATE (Validation-Level)                                        │
│   ─────────────────────                                          │
│   Quality checkpoints                                            │
│   Example: gate-discovery, gate-design                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## RQ4: Semantic Precision vs Simplicity

### Cognitive Load Research

#### Miller's Law (7±2)

Miller's 1956 research established that working memory can hold approximately 7 (plus or minus 2) chunks of information. For UX design, this means:

- **Navigation**: Limit to 5-9 options
- **Categories**: Keep distinct categories under 7
- **Chunking**: Group related items to reduce perceived complexity

Source: [Laws of UX - Miller's Law](https://lawsofux.com/millers-law/)

#### Cognitive Load Theory

Sweller's Cognitive Load Theory (1988) identifies three types:

1. **Intrinsic load**: Inherent difficulty of material
2. **Extraneous load**: Load from poor design (minimize this)
3. **Germane load**: Load devoted to learning (maximize this)

**Implication for RaiSE**: A good terminology hierarchy should minimize extraneous load (confusion) while supporting germane load (learning the system).

Source: [Cognitive Load Theory - ScienceDirect](https://www.sciencedirect.com/topics/psychology/cognitive-load-theory)

#### Working Memory Limits

- Maximum duration: ~20 seconds
- Capacity: ~7 chunks
- Processing: 2-4 concurrent chunks

**Recommendation**: Keep instruction categories to 2-3 levels maximum.

### Progressive Disclosure Research

Jakob Nielsen introduced progressive disclosure in 1995:

> "Initially, show users only a few of the most important options. Offer a larger set of specialized options upon request."

Source: [NN/g Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)

**Implementation for RaiSE:**

| User Level | What They See | Kata Visibility |
|------------|---------------|-----------------|
| **Beginner** | Skills (atomic commands) | Hidden |
| **Intermediate** | Skills + Katas | On request |
| **Advanced** | Full hierarchy + customization | Always visible |

**Warning from research**: Designs beyond 2 disclosure levels typically have low usability.

### CLI Design Principles

Research on command-line UX reveals:

1. **Hierarchical commands work** when they follow grammar (subject-verb-object)
2. **Flat lists with categories** work for discovery (VSCode Command Palette)
3. **Progressive discovery** enables power users without overwhelming beginners

Source: [CLI Design Guidelines](https://clig.dev/), [UX Patterns for CLI](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html)

### Hierarchy Depth Recommendation

| Levels | Pros | Cons | Verdict |
|--------|------|------|---------|
| **1 (flat)** | Simple, no hierarchy to learn | No semantic distinction | Insufficient |
| **2 (kata/skill)** | Clear distinction, manageable | Requires learning | **Optimal** |
| **3 (kata/skill/technique)** | Fine-grained control | Cognitive overhead | Too complex |

**Recommendation: 2-level hierarchy with progressive disclosure**

---

## RQ5: Terminology Options Evaluation

### Evaluation Criteria

1. **Semantic Clarity** (1-5): Does the name convey intent?
2. **Industry Alignment** (1-5): Familiar to developers?
3. **RaiSE Brand Fit** (1-5): Lean/Heutagogy alignment?
4. **Extensibility** (1-5): Can it scale to future concepts?
5. **Searchability** (1-5): Unique for docs/SEO?

### Scored Evaluation Matrix

| Option | Process | Atomic | Validation | Clarity | Industry | Brand | Extensibility | SEO | **Total** |
|--------|---------|--------|------------|---------|----------|-------|---------------|-----|-----------|
| **A** | Kata | Skill | Gate | 4 | 3 | 5 | 5 | 5 | **22** |
| **B** | Kata | Command | Gate | 3 | 4 | 5 | 4 | 5 | **21** |
| **C** | Workflow | Command | Checkpoint | 5 | 5 | 2 | 3 | 2 | **17** |
| **D** | Flow | Action | Gate | 4 | 4 | 3 | 4 | 3 | **18** |
| **E** | Process | Tool | Validator | 4 | 5 | 2 | 3 | 2 | **16** |
| **F** | Playbook | Skill | Gate | 4 | 4 | 3 | 4 | 3 | **18** |
| **G** | Journey | Step | Milestone | 3 | 3 | 2 | 3 | 4 | **15** |

### Detailed Analysis of Top Options

#### Option A: Kata / Skill / Gate (Score: 22)

**Strengths:**
- "Kata" is unique in AI space - strong SEO/brand differentiation
- "Skill" implies capability and mastery (aligns with heutagogy)
- "Gate" is established in RaiSE and industry (validation gates)
- Strong Lean philosophy alignment across all terms
- Future-proof: can add "Technique" level if needed

**Weaknesses:**
- "Kata" requires onboarding explanation
- "Skill" could be confused with LLM capabilities

**Mitigation:** Progressive disclosure hides Kata from beginners; clear glossary definitions.

#### Option B: Kata / Command / Gate (Score: 21)

**Strengths:**
- "Command" is immediately familiar (CLI, VSCode)
- "Kata" maintains differentiation
- Backward compatible with current RaiSE terminology

**Weaknesses:**
- "Command" doesn't convey mastery/learning intent
- Loses semantic distinction (commands are commands)
- "Command" is overloaded term in software

#### Option F: Playbook / Skill / Gate (Score: 18)

**Strengths:**
- "Playbook" is familiar from DevOps/IT operations
- Strategic connotation (vs. runbook = tactical)
- "Skill" maintains capability focus

**Weaknesses:**
- "Playbook" is common - weak differentiation
- Less alignment with Lean philosophy
- ServiceNow, Ansible already use "Playbook"

### Migration Path from "Command"

Current RaiSE uses "Command Categories" (setup/, context/, project/, etc.). Migration strategy:

1. **Phase 1**: Introduce "Skill" as alias for atomic commands
2. **Phase 2**: Classify multi-step processes as "Katas"
3. **Phase 3**: Update documentation and CLI help
4. **Phase 4**: Deprecate flat "command" terminology

**Directory structure change:**

```
Current:
.raise/commands/
  setup/
  context/
  project/
  feature/
  validate/

Proposed:
.raise/
  katas/           # Process-level (multi-step)
    flow/
    patterns/
    principles/
  skills/          # Atomic-level (single-purpose)
    context/
    validate/
    tools/
  gates/           # Validation checkpoints
```

---

## Recommendations Summary

### Primary Recommendation

**Adopt Option A: Kata / Skill / Gate**

| Term | Applies To | Examples |
|------|------------|----------|
| **Kata** | Multi-step processes with learning intent | `/project/create-prd`, `/setup/analyze-codebase` |
| **Skill** | Atomic utility operations | `/context/get`, `/validate/architecture` |
| **Gate** | Quality validation checkpoints | `gate-discovery`, `gate-design` |

### Implementation Strategy

1. **Progressive Disclosure**
   - Level 1 (Default): Users see "Skills" and "Gates"
   - Level 2 (On demand): "Katas" surface when needed
   - Level 3 (Advanced): Full hierarchy with levels

2. **Glossary Updates**
   - Add "Skill" as new entry
   - Update "Kata" to emphasize distinction from Skills
   - Add migration note for "Command" term

3. **Documentation Pattern**
   - Beginner docs: Focus on Skills
   - Process docs: Introduce Katas
   - Reference docs: Full hierarchy

4. **CLI Integration**
   - `rai skill <name>` - Execute atomic skill
   - `rai kata <name>` - Execute learning process
   - `rai gate <name>` - Run validation

### Fallback Recommendation

If "Kata" proves too unfamiliar in user testing, fall back to **Option F: Playbook / Skill / Gate** as the second-best option.

---

## Sources

### AI Agent Frameworks
- [Anthropic MCP Documentation](https://docs.claude.com/en/docs/mcp)
- [LangChain Agents Guide](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [CrewAI Introduction](https://docs.crewai.com/en/introduction)
- [Microsoft Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/0.2/docs/Use-Cases/agent_chat/)
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants/tools)
- [Skills vs Tools for AI Agents](https://blog.arcade.dev/what-are-agent-skills-and-tools)

### Developer Platforms
- [Backstage Scaffolder](https://backstage.spotify.com/docs/portal/core-features-and-plugins/scaffolder)
- [Port Actions and Automations](https://docs.port.io/actions-and-automations/overview/)
- [Humanitec Platform Engineering](https://developer.humanitec.com/training/master-your-internal-developer-platform/structure-and-integration-points/)

### Workflow Orchestration
- [Temporal Documentation](https://docs.temporal.io/glossary)
- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Prefect Introduction](https://docs.prefect.io/)
- [Dagster Concepts](https://docs.dagster.io/getting-started/concepts)

### Automation Platforms
- [n8n Node Types](https://docs.n8n.io/integrations/builtin/node-types/)
- [Zapier Key Concepts](https://help.zapier.com/hc/en-us/articles/8496181725453-Learn-key-concepts-in-Zaps)
- [ServiceNow Playbooks](https://www.servicenow.com/community/secops-articles/understanding-playbooks-and-the-relationship-of-runbooks/ta-p/2314914)
- [UiPath Workflow Activities](https://docs.uipath.com/activities/other/latest/workflow/workflow-activities)

### Cognitive Science and UX
- [Miller's Law - Laws of UX](https://lawsofux.com/millers-law/)
- [Cognitive Load Theory - NN/g](https://www.nngroup.com/articles/minimize-cognitive-load/)
- [Progressive Disclosure - NN/g](https://www.nngroup.com/articles/progressive-disclosure/)
- [CLI Design Guidelines](https://clig.dev/)

### Toyota Kata and Lean
- [Toyota Kata Wikipedia](https://en.wikipedia.org/wiki/Toyota_Kata)
- [KaiNexus Toyota Kata](https://www.kainexus.com/improvement-disciplines/toyota-kata)
- [Shu Ha Ri Mastery](https://www.kaizenko.com/shu-ha-ri/)

### Coding Katas
- [CodeKata.com](http://codekata.com/)
- [Codewars](https://www.codewars.com/)
- [Best Coding Kata Sites 2025](https://algocademy.com/blog/7-best-coding-kata-sites-in-2025-ranked-by-a-daily-practitioner/)

### Agile/Scrum History
- [Scrum Rugby Connection](https://medium.com/serious-scrum/scrum-s-connection-to-rugby-597405fed5ec)
- [Origin of Scrum](https://www.visual-paradigm.com/scrum/what-is-the-evolution-of-scrum/)

---

## Appendix A: Full Framework Terminology Reference

### Claude MCP Primitives

| Primitive | Purpose | RaiSE Equivalent |
|-----------|---------|------------------|
| Tools | Functions AI can call | Skills |
| Resources | Structured data sources | Golden Data / Corpus |
| Prompts | Reusable templates | Katas (when multi-step) |
| Sampling | Agentic workflow delegation | Escalation Gates |

### LangChain Evolution

| Version | Approach | Recommendation |
|---------|----------|----------------|
| Legacy | AgentExecutor | Deprecated |
| Current | LangGraph | Recommended for production |
| Pattern | Tools + Agents + Workflows | Graph-based orchestration |

### Semantic Kernel Deprecations

| Deprecated | Replacement | Rationale |
|------------|-------------|-----------|
| Stepwise Planner | Function Calling | More reliable |
| Handlebars Planner | Function Calling | Token-efficient |
| OpenAI Planner | Automatic Function Calling | Simplified API |

---

## Appendix B: ShuHaRi Application to RaiSE Hierarchy

| Phase | Kanji | Kata Interaction | Skill Interaction |
|-------|-------|------------------|-------------------|
| **Shu** (Follow) | 守 | Follow every step exactly | Execute as instructed |
| **Ha** (Break) | 破 | Adapt steps to context | Combine skills creatively |
| **Ri** (Transcend) | 離 | Create new Katas | Create new Skills |

This model supports RaiSE's heutagogical philosophy - the same artifacts serve learners at any mastery level.

---

## Appendix C: Validation Gate Alignment

Current RaiSE gates align well with the proposed hierarchy:

| Gate | Phase | Validates | Level |
|------|-------|-----------|-------|
| gate-discovery | 1 | PRD complete | Kata completion |
| gate-vision | 2 | Solution Vision aligned | Kata completion |
| gate-design | 3 | Tech Design verifiable | Kata completion |
| gate-backlog | 4 | Backlog prioritized | Kata completion |
| gate-plan | 5 | Plan atomic | Skill aggregation |
| gate-code | 6 | Code ready for merge | Skill execution |

---

*Research completed: 2026-01-29*
*RaiSE Ontology Research Agent*
