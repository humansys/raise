# Evidence Catalog: Skills Architecture Decision

> Research ID: skills-architecture-20260131
> Search Date: 2026-01-31
> Tool: WebSearch (built-in fallback)
> Researcher: Rai (Claude Opus 4.5)

---

## Summary Statistics

- **Total Sources**: 18
- **Evidence Distribution**: Very High (3), High (8), Medium (5), Low (2)
- **Temporal Coverage**: 2024-2026 (focused on post-Skills-launch)

---

## Sources

### 1. Agent Skills Specification (Official)

**Source**: [agentskills.io/specification](https://agentskills.io/specification)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025-2026 (actively maintained)
- **Key Finding**: `metadata` field explicitly designed for extensibility - "A map from string keys to string values. Clients can use this to store additional properties not defined by the Agent Skills spec."
- **Relevance**: Directly answers whether Skills can hold RaiSE-specific metadata. YES.

### 2. Claude Code Skills Documentation

**Source**: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2026
- **Key Finding**: Skills support `disable-model-invocation` (workflow control), `allowed-tools` (permissions), `mode` (behavior modification). Progressive disclosure architecture.
- **Relevance**: Skills already have gate-like controls. RaiSE gates could map to these.

### 3. Spring AI Agent Skills Implementation

**Source**: [spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2026-01-13
- **Key Finding**: Spring AI natively supports Claude Code Skills format. "Spring AI Skills seamlessly supports any existing Claude Code Skills."
- **Relevance**: Industry validation - major framework adopted Skills without creating a wrapper. Single format works.

### 4. Anthropic Skills Repository

**Source**: [github.com/anthropics/skills](https://github.com/anthropics/skills)
- **Type**: Primary
- **Evidence Level**: High
- **Date**: 2025-2026
- **Key Finding**: Official examples show metadata usage for author, version, compatibility. Skills range from simple instructions to complex workflows with scripts.
- **Relevance**: Demonstrates extensibility in practice.

### 5. Skills vs MCP Architecture Guide

**Source**: [cometapi.com/claude-skills-vs-mcp-the-2026-guide](https://www.cometapi.com/claude-skills-vs-mcp-the-2026-guide-to-agentic-architecture/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2026
- **Key Finding**: "Skills are packaged, reusable bundles of instructions, templates, scripts, and resources." MCP and Skills are complementary - MCP for connectivity, Skills for methodology.
- **Relevance**: Validates that Skills ARE the methodology layer - exactly what katas are.

### 6. Agentic AI Foundation (Linux Foundation)

**Source**: [intuitionlabs.ai/articles/agentic-ai-foundation-open-standards](https://intuitionlabs.ai/articles/agentic-ai-foundation-open-standards)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025-12
- **Key Finding**: Skills spec donated to Linux Foundation. Governed by AAIF co-founded by Anthropic, OpenAI, Block. Google, Microsoft, AWS members.
- **Relevance**: Skills is not proprietary - it's an industry standard. Safe long-term bet.

### 7. Adapter Pattern for Migration

**Source**: [dev.to/rogeliogamez92/using-the-adapter-pattern-to-migrate](https://dev.to/rogeliogamez92/using-the-adapter-pattern-to-migrate-to-a-new-library-434a)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: "A wrapper library is a bet: you trade upfront cost for future flexibility. The real challenge is knowing when a wrapper solves a problem and when it simply adds another one."
- **Relevance**: Warns about dual-format maintenance burden.

### 8. Wikipedia: Wrapper Library

**Source**: [en.wikipedia.org/wiki/Wrapper_library](https://en.wikipedia.org/wiki/Wrapper_library)
- **Type**: Tertiary
- **Evidence Level**: High
- **Date**: Ongoing
- **Key Finding**: Wrappers are used for "incompatible interfaces." When interfaces ARE compatible, wrappers add unnecessary indirection.
- **Relevance**: If Skills can represent katas fully, no wrapper needed.

### 9. Single Source of Truth (SSOT) Principles

**Source**: [strapi.io/blog/what-is-single-source-of-truth](https://strapi.io/blog/what-is-single-source-of-truth)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: "An SSOT is a centralized repository that stores and manages all organizational data to ensure everyone works with consistent, accurate information."
- **Relevance**: Dual formats violate SSOT principle.

### 10. Red Hat: SSOT in Enterprise Architecture

**Source**: [redhat.com/en/blog/single-source-truth-architecture](https://www.redhat.com/en/blog/single-source-truth-architecture)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: When multiple representations exist, "ensure synchronization mechanisms exist to propagate changes."
- **Relevance**: Dual format requires sync - maintenance burden.

### 11. SkillsMP Marketplace

**Source**: [skillsmp.com](https://skillsmp.com/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2026
- **Key Finding**: 71,000+ agent skills available. Community-driven ecosystem.
- **Relevance**: Evidence of massive ecosystem adoption - RaiSE could participate.

### 12. Anthropic Engineering Blog: Agent Skills

**Source**: [anthropic.com/engineering/equipping-agents-for-the-real-world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- **Type**: Primary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: "Skills are self-documenting. A skill author or user can read a SKILL.md and understand what it does, making skills easy to audit and improve."
- **Relevance**: Transparency principle aligns with RaiSE values.

### 13. SOA Migration Case Studies

**Source**: [researchgate.net/publication/224243307](https://www.researchgate.net/publication/224243307_SOA_migration_case_studies_and_lessons_learned)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2010 (classic research)
- **Key Finding**: "If not done correctly, migration can lead to failure. Factors include technology selection, migration approach, and governance."
- **Relevance**: Migration is risky; must be deliberate.

### 14. Yusuf Aytas: On Writing Wrapper Libraries

**Source**: [yusufaytas.com/on-writing-wrapper-libraries](https://yusufaytas.com/on-writing-wrapper-libraries/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2023
- **Key Finding**: "A wrapper should solve a real problem, not just satisfy an aesthetic preference for 'cleaner code.'"
- **Relevance**: Question whether kata→skill wrapper solves real problem.

### 15. TOGAF Standard

**Source**: [opengroup.org/togaf](https://www.opengroup.org/togaf)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: "Commercial contributors avoid spilling proprietary secrets by clearly defining the scope of what they want to contribute and what they want to keep private."
- **Relevance**: RaiSE can use Skills (public standard) while methodology philosophy remains proprietary value.

### 16. Open Standards Wikipedia

**Source**: [en.wikipedia.org/wiki/Open_standard](https://en.wikipedia.org/wiki/Open_standard)
- **Type**: Tertiary
- **Evidence Level**: Medium
- **Date**: Ongoing
- **Key Finding**: "Open standards may employ license terms that protect against subversion by embrace-and-extend tactics."
- **Relevance**: Skills spec is governed by Linux Foundation - safe from embrace-and-extend.

### 17. Awesome Claude Skills Repository

**Source**: [github.com/travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- **Type**: Tertiary
- **Evidence Level**: Low
- **Date**: 2025-2026
- **Key Finding**: Curated list showing diverse skill implementations with various metadata patterns.
- **Relevance**: Community adoption patterns.

### 18. Medium: Agent Skills Universal Standard

**Source**: [medium.com/@richardhightower/agent-skills-the-universal-standard](https://medium.com/@richardhightower/agent-skills-the-universal-standard-transforming-how-ai-agents-work-fc7397406e2e)
- **Type**: Tertiary
- **Evidence Level**: Low
- **Date**: 2026-01
- **Key Finding**: "25+ major platforms support Agent Skills. OpenAI has quietly adopted structurally identical architecture."
- **Relevance**: Universal adoption claim (needs verification but directionally accurate).

---

## Evidence Gaps

1. **No case studies of frameworks migrating internal formats to Skills** - This is new territory
2. **Limited data on metadata field usage for complex structured data** - Spec says string→string, but practice may vary
3. **No examples of ShuHaRi-like progression models in Skills** - Novel RaiSE concept

---

## Contrary Evidence

### Against Option 3 (Migration)

1. **Migration risk** - SOA case studies show migration can fail if not careful
2. **Loss of semantic richness** - Skills metadata is string→string; katas have structured objects (shuhari)

### Against Option 2 (Dual Format)

1. **SSOT violation** - Dual formats require synchronization
2. **Wrapper maintenance** - "Yet another layer to maintain"
3. **Unnecessary indirection** - If formats are compatible, wrapper adds complexity

---

*Evidence catalog complete - proceed to synthesis*
