# Research Session: RaiSE CLI Position in Agent Skills Ecosystem

> Session ID: 2026-01-30-skills-ecosystem
> Status: COMPLETED

---

## Research Objective

Determine how raise-cli should position itself within the emerging Agent Skills ecosystem (Anthropic, Moltbot) to maximize strategic value while avoiding terminology confusion and missed opportunities.

---

## Context

### What We Know

1. **Anthropic Agent Skills** (Oct 2025, open standard Dec 2025):
   - SKILL.md files with YAML frontmatter + markdown instructions
   - Portable across Claude.ai, Claude Code, Agent SDK, API
   - 20k+ GitHub stars, enterprise directory with major partners
   - OpenAI has adopted structurally identical architecture

2. **Moltbot/Clawdbot** (viral Jan 2026, 68k stars):
   - Open-source personal AI agent built on Claude
   - "Molthub" registry with 100+ community skills
   - Automates real-world tasks (booking, browsing, scheduling)

3. **RaiSE Current State**:
   - Has internal "skills" concept (`.raise/skills/`) — atomic operations (git, ast-grep, ripgrep wrappers)
   - Different semantic meaning than Anthropic/Moltbot "skills"
   - CLI provides governance layer for AI-assisted development

### The Tension

| RaiSE "Skills" | Anthropic "Skills" |
|----------------|-------------------|
| Internal atomic operations | Agent capability bundles |
| Engine implementation detail | User-facing, shareable |
| Not portable | Cross-platform standard |

---

## Research Questions

### Primary Question

> **How should raise-cli position itself in the Anthropic Agent Skills ecosystem — as a skill provider, skill consumer, governance layer, or hybrid?**

### Secondary Questions

| # | Question | Why It Matters |
|---|----------|----------------|
| 1 | What is the exact Anthropic Agent Skills specification? | Understand the standard we might adopt/complement |
| 2 | How do Skills relate to MCP (Model Context Protocol)? | RaiSE could expose tools via MCP — what's the skill layer above? |
| 3 | What categories of skills exist in the ecosystem? | Identify if "governance" or "methodology" skills exist |
| 4 | How do enterprise customers use skills? | Align with our regulated-industry target market |
| 5 | What are the security/governance concerns with skills? | 26% vulnerability rate cited — is this our opportunity? |
| 6 | Should RaiSE rename internal "skills" to avoid confusion? | Terminology alignment vs. differentiation |

---

## Research Scope

### In Scope

- Anthropic Agent Skills specification (SKILL.md format, manifest, capabilities)
- Moltbot skills architecture and registry model
- Relationship between MCP tools and Agent Skills
- Enterprise skill management patterns
- Security/governance gaps in current skill ecosystems
- Competitive positioning options for RaiSE

### Out of Scope

- Deep technical implementation details of Moltbot internals
- Pricing/business model analysis
- Other AI agent frameworks (LangChain, AutoGPT, etc.) unless directly relevant
- Implementation planning (that comes after research)

---

## Expected Outputs

### 1. Agent Skills Specification Summary
Brief technical summary of the Anthropic Agent Skills standard:
- SKILL.md structure and required fields
- Manifest format
- Execution model (how skills are invoked)
- Distribution model (how skills are shared)

### 2. Ecosystem Map
Visual or tabular map showing:
- Skills vs MCP vs Tools relationship
- Where RaiSE could fit (provider, consumer, governance layer)
- Current gaps in the ecosystem

### 3. Strategic Options Analysis
Evaluate 3-4 positioning options for raise-cli:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | RaiSE as Agent Skill | Publish `raise` as skill in Anthropic/Moltbot registry | ? | ? |
| B | RaiSE as Skill Governance | Layer above skills that validates/audits them | ? | ? |
| C | RaiSE consumes Skills | Use Anthropic skills internally, rename internal concept | ? | ? |
| D | Independent path | Keep current architecture, different market | ? | ? |

### 4. Terminology Recommendation
Clear recommendation on whether to:
- Rename RaiSE internal "skills" to something else (e.g., "operations", "actions", "primitives")
- Align with Anthropic Skills standard
- Keep both with clear differentiation

### 5. Key Findings
Bulleted list of 5-7 key insights that should inform raise-cli PRD/design decisions.

---

## Research Method

1. **Web Research**: Fetch and analyze primary sources
   - Anthropic Agent Skills documentation
   - Anthropic skills GitHub repository
   - Moltbot documentation and skills registry
   - Simon Willison's analysis (cited as authoritative)

2. **Pattern Analysis**: Compare specifications
   - SKILL.md vs RaiSE kata/skill structure
   - MCP tools vs Agent Skills

3. **Gap Analysis**: Identify underserved areas
   - Enterprise governance
   - Security validation
   - Compliance/audit trails

4. **Synthesis**: Produce strategic recommendations

---

## Sources to Consult

| Priority | Source | URL |
|----------|--------|-----|
| 1 | Anthropic Agent Skills Docs | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| 2 | Anthropic Skills GitHub | https://github.com/anthropics/skills |
| 3 | Anthropic Engineering Blog | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| 4 | Simon Willison Analysis | https://simonwillison.net/2025/Oct/16/claude-skills/ |
| 5 | Moltbot Official Site | https://molt.bot/ |
| 6 | Moltbot Skills Collection | https://github.com/VoltAgent/awesome-moltbot-skills |

---

## Success Criteria

Research is complete when:

- [ ] Agent Skills specification is documented (structure, execution, distribution)
- [ ] MCP vs Skills relationship is clear
- [ ] At least 3 strategic options are analyzed with pros/cons
- [ ] Terminology recommendation is provided with rationale
- [ ] Key findings are actionable for PRD refinement

---

## Session Metadata

| Field | Value |
|-------|-------|
| Requested by | Emilio Osorio |
| Project | raise-cli |
| Related artifacts | `governance/projects/raise-cli/prd.md` |
| Estimated depth | Medium (2-3 hours equivalent) |
| Output location | `work/research/outputs/skills-ecosystem-analysis.md` |

---

*Prompt version: 1.0*
*Ready for review*
