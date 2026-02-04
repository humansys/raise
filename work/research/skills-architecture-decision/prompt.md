---
research_id: "skills-architecture-20260131"
primary_question: "Should RaiSE use Skills as an interface layer (Option 2) or migrate katas entirely to Skills format (Option 3)?"
decision_context: "ADR for RaiSE Skills architecture - affects core framework design"
depth: "standard"
created: "2026-01-31"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Skills Architecture Decision

> Comparing Option 2 (Skills as Interface) vs Option 3 (Migrate Katas to Skills)

---

## Role Definition

You are a **Research Specialist** with expertise in **AI agent frameworks, developer tooling architecture, and open standards**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: Should RaiSE use Skills as an interface layer (keeping katas as internal methodology) or migrate katas entirely to the Agent Skills format?

**Secondary** (supporting questions):
1. What technical patterns do existing frameworks use when adopting open standards?
2. What are the maintenance costs of dual-format vs single-format approaches?
3. How do teams balance proprietary value (methodology) with ecosystem compatibility?
4. What migration patterns exist for converting internal formats to open standards?

---

## Decision Context

**This research will inform**: ADR for RaiSE Skills architecture

**Stakeholder**: Emilio (RaiSE creator), framework users

**Timeline**: Today (2026-01-31) - decision needed before F1.4 implementation

**Impact**: Affects core framework design, user adoption, ecosystem integration, long-term maintenance

---

## Options Being Compared

### Option 2: Skills as Interface Layer

**Description**: Skills expose katas externally; katas remain internal process definitions

**Structure**:
```
.raise/katas/          # RaiSE methodology (rich metadata, gates, shuhari)
.claude/skills/        # Interface for AI agents (portable, minimal)
```

**Mapping**: Katas can expose themselves as Skills when appropriate

### Option 3: Migrate Katas to Skills Format

**Description**: Single format migration - all katas become Skills

**Structure**:
```
.claude/skills/        # Everything is a Skill (with extended metadata)
```

**Implication**: RaiSE-specific metadata (gates, shuhari, workflow) must fit in Skills format

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Official documentation**
   - Agent Skills specification (agentskills.io)
   - Claude Code documentation
   - MCP specification
   - Purpose: Authoritative technical specifications

2. **Production evidence**
   - GitHub repositories adopting Skills
   - Framework migration case studies
   - Engineering blogs on standard adoption
   - Purpose: Real-world validation, battle-tested patterns

3. **Architecture patterns**
   - Adapter pattern vs format migration literature
   - Standards adoption in software engineering
   - Dual-format maintenance research
   - Purpose: Theoretical grounding

4. **Community validation**
   - Discussions on Skills adoption strategies
   - Framework authors' perspectives
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "Agent Skills migration strategy"
- "open standard adoption dual format"
- "framework wrapper vs native adoption"
- "Skills specification extensibility custom metadata"
- "adapter pattern software standards"
- "internal format external interface architecture"

**Sources to avoid**: Marketing content, product announcements without technical depth

---

## Evaluation Criteria for Options

For each option, evaluate:

1. **Technical Fit**: How well does the format support RaiSE's needs?
2. **Ecosystem Compatibility**: How portable is the result?
3. **Maintenance Burden**: What's the long-term cost?
4. **User Experience**: How does it affect RaiSE users?
5. **Unique Value Preservation**: Does RaiSE retain its differentiators?

---

## Output Format

Produce artifacts in `work/research/skills-architecture-decision/`:

1. `sources/evidence-catalog.md` - All sources with ratings
2. `synthesis.md` - Triangulated claims
3. `recommendation.md` - Actionable decision

---

## Constraints

**Time**: Standard depth (~4h equivalent)

**Focus priorities**:
1. Skills extensibility (can we add custom metadata?)
2. Real-world migration patterns
3. Maintenance implications

**Out of scope**:
- MCP implementation details
- Skills marketplace strategies
- Claude Code internals beyond Skills

---

## Reproducibility Metadata

- Tool/model used: WebSearch (fallback)
- Search date: 2026-01-31
- Prompt version: 1.0
- Researcher: Rai (Claude Opus 4.5)
