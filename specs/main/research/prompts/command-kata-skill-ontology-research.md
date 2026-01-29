---
id: research-prompt-002
title: "Command vs Kata vs Skill: Ontological Research for AI Agent Instruction Hierarchies"
date: 2026-01-29
status: draft
purpose: deep-research
estimated_depth: comprehensive
target_sources: academic, industry, open-source frameworks, enterprise patterns
---

# Research Prompt: Command vs Kata vs Skill Ontology

## Context for Researcher

RaiSE is an AI-assisted software engineering framework that uses markdown-based instruction files to guide LLM agents through development workflows. Currently, all instruction files are called "commands" (inherited from spec-kit), but we observe a semantic tension:

| Current Name | Example | Actual Nature |
|--------------|---------|---------------|
| Command | `/context/get` | Atomic utility operation |
| Command | `/project/create-prd` | Multi-step process with learning intent |
| Command | `/validate/architecture` | Verification checkpoint |

The term "Kata" (from martial arts via Toyota/Lean) already exists in RaiSE for structured practice exercises. The question is whether RaiSE should adopt a **hierarchical terminology** that distinguishes:

1. **Katas** = Process-oriented workflows (best practices, learning, mastery)
2. **Skills/Commands** = Atomic operations (utilities, tools, single-purpose)

---

## Research Questions

### RQ1: Industry Terminology Landscape

**Question**: What terminology do major AI agent frameworks, workflow engines, and developer tools use to describe instruction hierarchies?

**Specific areas to investigate**:

1. **AI Agent Frameworks**:
   - How do Claude MCP, OpenAI Assistants, LangChain, CrewAI, AutoGen name their instruction primitives?
   - Do they differentiate between "tools" (atomic) and "workflows" (composite)?
   - What terms appear: prompts, tools, skills, actions, commands, functions, capabilities, workflows, chains, pipelines, runbooks, playbooks?

2. **DevOps/Platform Engineering**:
   - How do Backstage (Spotify), Port, Humanitec name their developer workflows?
   - What's the terminology for "golden paths" vs "actions" vs "templates"?
   - How does Kubernetes Operators terminology (reconcile, sync, watch) relate?

3. **Low-Code/Workflow Platforms**:
   - Temporal, Prefect, Airflow, n8n: how do they name workflow vs task vs activity?
   - Make/Zapier: scenarios vs actions vs modules?

4. **Enterprise Automation**:
   - ServiceNow, Workato, UiPath: how do they distinguish process vs action?
   - What's the "playbook" vs "runbook" distinction?

**Deliverable**: Terminology comparison matrix with source citations.

---

### RQ2: Kata as Differentiator

**Question**: Is "Kata" a unique/valuable term for AI-assisted development, or does it create unnecessary cognitive load?

**Specific areas to investigate**:

1. **Toyota Kata in Software**:
   - How widely is "Kata" used in software (beyond coding katas)?
   - Mike Rother's Toyota Kata vs coding katas (exercism, etc.) - semantic overlap?
   - Does any AI framework use "Kata" for agent workflows?

2. **Pedagogical Value**:
   - Does "Kata" signal "practice/mastery" better than "workflow" or "process"?
   - Is there research on terminology affecting developer behavior/learning?
   - How do ShuHaRi stages map to skill acquisition in AI-assisted work?

3. **Competitive Differentiation**:
   - Would "Kata" be distinctive in the AI agent market?
   - Risk: Does it alienate users unfamiliar with Lean/martial arts terminology?
   - Precedent: Did "Scrum" (rugby) or "Sprint" succeed despite sports origin?

**Deliverable**: Pros/cons analysis of "Kata" as process-level terminology with evidence.

---

### RQ3: Hierarchical Instruction Models

**Question**: What hierarchical models exist for organizing AI agent instructions from atomic to composite?

**Specific areas to investigate**:

1. **Existing Hierarchies**:
   - MCP: Resources → Tools → Prompts → Sampling (is there a hierarchy?)
   - LangChain: Tools → Chains → Agents → Workflows
   - CrewAI: Tools → Tasks → Crews
   - AutoGen: Functions → Conversations → Workflows
   - Semantic Kernel (Microsoft): Plugins → Functions → Plans

2. **Human-Computer Interaction Research**:
   - GOMS model: Goals → Operators → Methods → Selection rules
   - Is there research on optimal granularity for AI agent instructions?
   - Cognitive load theory applied to AI agent taxonomies?

3. **Traditional Software Patterns**:
   - Command Pattern vs Strategy Pattern vs Template Method
   - How do design patterns inform instruction hierarchy?
   - Unix philosophy (small tools, pipelines) vs monolithic workflows?

**Deliverable**: Hierarchical model comparison with applicability to RaiSE.

---

### RQ4: Semantic Precision vs Simplicity

**Question**: Is a 2-level (kata/skill) or 3-level hierarchy worth the cognitive cost?

**Specific areas to investigate**:

1. **Cognitive Load Research**:
   - Miller's Law (7±2) applied to category systems
   - How many distinct instruction types can users effectively remember?
   - Evidence for/against flat vs hierarchical command structures?

2. **User Mental Models**:
   - Do developers naturally think in "process" vs "action" terms?
   - How do IDEs structure commands (palettes, menus, shortcuts)?
   - VSCode Command Palette: flat list with categories - lessons?

3. **Progressive Disclosure**:
   - Can the hierarchy be hidden for beginners but available for experts?
   - How do frameworks handle this (e.g., Rails "convention over configuration")?

**Deliverable**: Recommendation on hierarchy depth with UX rationale.

---

### RQ5: Proposed Terminology Options

**Question**: What are the candidate terminologies for RaiSE's restructuring?

**Evaluate these options**:

| Option | Process-Level | Atomic-Level | Gate-Level |
|--------|---------------|--------------|------------|
| A | Kata | Skill | Gate |
| B | Kata | Command | Gate |
| C | Workflow | Command | Checkpoint |
| D | Flow | Action | Gate |
| E | Process | Tool | Validator |
| F | Playbook | Skill | Gate |
| G | Journey | Step | Milestone |

**For each option, evaluate**:
1. Semantic clarity (does the name convey the intent?)
2. Industry alignment (familiar to developers?)
3. RaiSE brand fit (Lean/Heutagogy philosophy alignment?)
4. Extensibility (can it scale to future concepts?)
5. Searchability (unique enough for documentation/SEO?)

**Deliverable**: Scored evaluation matrix with recommendation.

---

## Research Methodology Suggestions

1. **Primary Sources**:
   - Official documentation of: MCP, LangChain, CrewAI, AutoGen, Semantic Kernel
   - Backstage, Port, Temporal, Prefect documentation
   - Mike Rother's Toyota Kata materials

2. **Secondary Sources**:
   - HackerNews/Reddit discussions on AI agent terminology
   - Conference talks (Strange Loop, QCon, KubeCon) on developer experience
   - Academic papers on cognitive load in developer tools

3. **Empirical Validation** (if possible):
   - Survey existing RaiSE users on terminology preferences
   - A/B test documentation with different terminology
   - Interview developers on mental models for "process" vs "action"

---

## Expected Deliverables

1. **Terminology Landscape Matrix** (RQ1)
   - 15+ frameworks compared
   - Columns: atomic term, composite term, validation term, source

2. **Kata Analysis Report** (RQ2)
   - 500-1000 words on Kata's viability
   - Evidence for/against with citations

3. **Hierarchy Model Comparison** (RQ3)
   - Visual diagram of 3-5 hierarchical models
   - Mapping to RaiSE concepts

4. **Cognitive Load Assessment** (RQ4)
   - Research-backed recommendation on hierarchy depth
   - UX implications

5. **Terminology Recommendation** (RQ5)
   - Scored matrix for all options
   - Final recommendation with rationale
   - Migration path from current "command" terminology

---

## Success Criteria

The research is successful if it enables RaiSE to:

1. **Decide**: Adopt hierarchy (kata/skill) OR stay flat (all commands)
2. **Name**: Select precise terminology for each level
3. **Document**: Update glossary, vision, and documentation
4. **Implement**: Restructure command directories if needed
5. **Communicate**: Explain the model clearly to new users

---

## Constraints and Considerations

- **Backwards Compatibility**: Current "command" files work - migration cost matters
- **Platform Agnosticism**: Terms shouldn't imply specific tooling (e.g., "chain" → LangChain)
- **Lean Philosophy Alignment**: Terms should resonate with Toyota/Lean practitioners
- **Heutagogy Fit**: Process-level terms should imply learning/mastery opportunity
- **Simplicity Bias**: When in doubt, fewer concepts is better

---

## Related RaiSE Documents

- `docs/core/glossary.md` (v2.2) - Current terminology
- `specs/raise/vision.md` (v2.2) - Framework vision
- `specs/raise/adrs/adr-007-terminology-simplification.md` - Recent SAR/CTX decision
- `.raise/commands/` - Current command structure

---

*This prompt is designed for deep research. Expected effort: 4-8 hours of focused investigation. Output should be a structured report addressing all RQs.*
