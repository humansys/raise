# Research Prompt: Architecture Representation for AI Understanding

## Research ID
RES-ARCH-REP-001

## Primary Question
How can we represent software architecture at a level that enables fast AI understanding and consistent component reuse?

## Secondary Questions
1. What architectural representation models exist (C4, arc42, dependency graphs)?
2. How do AI coding tools handle codebase understanding today?
3. What graph structures effectively represent software architecture?
4. What abstraction level enables reuse discovery without full codebase mapping?
5. What's the minimum viable representation for an AI to understand "what exists and how to use it"?

## Decision Context
This research informs the **Discovery** epic for RaiSE — specifically:
- What should Rai extract from a codebase?
- How should it be represented in the unified graph?
- What enables "fast understanding" for component reuse?

## Depth
Standard (4-8h equivalent) — This is a strategic decision affecting core functionality.

## Search Strategy

### Keywords
- "software architecture representation"
- "C4 model" + "automation" OR "AI"
- "arc42" + "documentation"
- "codebase understanding AI"
- "code graph" + "LLM" OR "AI assistant"
- "dependency graph visualization"
- "architecture as code"
- "software composition analysis"
- "component catalog"
- "AI code assistant context"

### Source Types
1. Academic: Software architecture reconstruction papers
2. Industry: How Sourcegraph, GitHub Copilot, Cursor handle context
3. Open Source: Architecture documentation tools (Structurizr, C4-PlantUML)
4. Community: Dev blogs on AI + architecture understanding

## Evidence Evaluation Criteria
- Proven at scale (>1000 users or production systems)
- Applicable to brownfield codebases
- Supports AI/LLM consumption
- Enables incremental discovery (not all-or-nothing)

## Output Format
1. Evidence catalog with source ratings
2. Comparison matrix of representation models
3. Recommendation for RaiSE Discovery
4. Draft node types for unified graph

## Quality Checklist
- [ ] 15+ sources consulted
- [ ] Major claims triangulated
- [ ] AI-specific considerations addressed
- [ ] Practical implementation path identified
