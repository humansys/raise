# Deep Research Prompt: Brownfield Codebase Documentation for Agentic Development

**Research ID**: RES-BFLD-AGENT-DOC-001
**Date Created**: 2026-01-23
**Priority**: High
**Estimated Effort**: 2-4 hours of research + 2-3 hours of synthesis
**Target Outcome**: Actionable recommendations for improving raise.1.analyze.code

---

## Research Objective

Investigate how top-tier engineering teams using agentic development (AI code assistants, code generation agents, autonomous coding systems) are documenting brownfield (existing) codebases to:

1. **Align code generation agents** with existing architecture and patterns
2. **Reduce hallucinations and off-pattern code generation**
3. **Accelerate onboarding** of both human developers and AI agents
4. **Maintain consistency** between human and AI-generated code
5. **Enable effective refactoring** guided by AI

**Core Question**: What documentation artifacts, formats, and processes enable AI agents to understand and work effectively with existing codebases?

---

## Research Scope

### In Scope

1. **Empirical practices** from companies/teams using AI coding assistants at scale
2. **Open source projects** with documented AI agent integration strategies
3. **Emerging standards and formats** for AI-consumable codebase documentation
4. **Tools and automation** for generating/maintaining such documentation
5. **Validation methods** for ensuring documentation accuracy and completeness
6. **Case studies** with measurable outcomes (time saved, quality metrics, etc.)

### Out of Scope

- General software documentation practices not specific to AI agents
- Theoretical papers without implementation evidence
- Documentation for greenfield projects only
- API documentation tools (Swagger, etc.) unless explicitly used for agent alignment

---

## Key Research Questions

### Category 1: Documentation Artifacts

**Q1.1**: What types of documentation artifacts are teams creating specifically for AI agents?

**Investigate**:
- Architecture Decision Records (ADRs) - format, level of detail
- System Context Documents (C4 model, architecture diagrams)
- Pattern Catalogs (approved patterns vs anti-patterns)
- Codebase Maps (entry points, data flow, component boundaries)
- Domain Model Documentation (ubiquitous language, entity relationships)
- Dependency Graphs (visualized and machine-readable)
- Code Style Guides (with examples, not just rules)
- Testing Strategy Documentation (test pyramid, coverage requirements)
- Other novel artifact types

**Look for**:
- Examples of actual documents (GitHub repos, public case studies)
- Templates or standardized formats
- Frequency of updates (how stale before refresh needed)
- Ownership (who maintains them)

---

**Q1.2**: How are teams structuring these artifacts for AI consumption?

**Investigate**:
- **Markdown vs structured formats** (JSON, YAML, custom DSLs)
- **Human-readable vs machine-readable** balance
- **Hierarchical organization** (overview → detail)
- **Linking strategies** (cross-references between documents)
- **Embedding metadata** (tags, categories, relationships)
- **Version control integration** (co-located with code, separate repo)

**Look for**:
- Specific file naming conventions
- Directory structures
- Metadata schemas
- Tools that parse/validate these structures

---

### Category 2: Content and Granularity

**Q2.1**: What level of detail are teams documenting?

**Investigate spectrum**:
- **High-level only** (architecture, major components)
- **Mid-level** (module boundaries, interfaces, data flows)
- **Low-level** (class responsibilities, function contracts, edge cases)
- **Code-level** (inline comments, docstrings enriched for AI)

**Key questions**:
- What level provides best ROI for agent alignment?
- How do teams avoid documentation rot at different levels?
- Are there "critical junctions" that must be documented?

---

**Q2.2**: What specific information are teams capturing?

**Investigate presence of**:
- **Architectural constraints** ("Never access database from controllers")
- **Design patterns used** ("We use Repository pattern here")
- **Anti-patterns to avoid** ("Don't use Singleton for X")
- **Business rules encoded in code** ("Discounts calculated in OrderService")
- **Technical debt inventory** ("This module needs refactoring but works")
- **Migration/evolution history** ("We're moving from REST to GraphQL")
- **Performance characteristics** ("This endpoint must respond in <100ms")
- **Security boundaries** ("Auth layer enforced at middleware")
- **Data ownership** ("CustomerService owns Customer table")
- **External dependencies** ("Stripe for payments, SendGrid for emails")

**Look for**: Real examples of each type of information capture.

---

### Category 3: Generation and Maintenance

**Q3.1**: How are teams generating this documentation?

**Investigate**:
- **Manual curation** (developers write from scratch)
- **Semi-automated** (AI generates draft, humans refine)
- **Fully automated** (tools extract from codebase)
- **Hybrid approaches** (automated structure + manual enrichment)

**Tools to research**:
- Static analysis tools repurposed for documentation
- AI-powered documentation generators (GPT-4 + codebase analysis)
- Custom scripts/frameworks
- Commercial solutions (Sourcegraph, Codeium, etc.)

**Look for**:
- Open source tools with GitHub repos
- Commercial tool case studies
- Custom in-house solutions (blog posts, conference talks)

---

**Q3.2**: How are teams keeping documentation current?

**Investigate**:
- **CI/CD integration** (validation on every commit)
- **Scheduled regeneration** (weekly/monthly automated updates)
- **Event-driven updates** (triggered by architectural changes)
- **Human-in-the-loop reviews** (periodic audits)
- **Staleness detection** (automated flagging of outdated sections)

**Key questions**:
- What's the acceptable lag between code changes and doc updates?
- How do teams detect when documentation is out of sync?
- What processes prevent documentation rot?

---

### Category 4: AI Agent Integration

**Q4.1**: How are AI agents consuming this documentation?

**Investigate**:
- **RAG (Retrieval-Augmented Generation)** approaches
  - What's indexed? (full docs, summaries, embeddings)
  - What retrieval strategies? (semantic search, keyword, hybrid)
  - What context window sizes are practical?
- **Fine-tuning** on codebase-specific documentation
- **Prompt engineering** patterns (system prompts with architecture context)
- **Multi-shot examples** (before/after code with explanations)
- **Tool use** (agents reading docs via function calls)

**Look for**:
- Specific RAG architectures (vector DBs used, embedding models)
- Prompt templates used in production
- Context management strategies (what to include in each request)

---

**Q4.2**: What outcomes are teams measuring?

**Investigate metrics**:
- **Code quality**:
  - % of AI-generated code following architecture patterns
  - Rate of code review rejections for AI vs human code
  - Adherence to style guides and conventions
- **Productivity**:
  - Time saved in onboarding (human + AI)
  - Reduction in "bad guesses" by AI (fewer revisions needed)
  - Increase in PR velocity
- **Consistency**:
  - Reduction in pattern violations
  - Fewer cross-cutting concerns violations
- **Knowledge retention**:
  - Reduction in "ask senior dev" questions
  - Increase in self-service capability

**Look for**: Case studies with before/after metrics.

---

### Category 5: Emerging Standards and Tools

**Q5.1**: Are there emerging standards for AI-consumable codebase documentation?

**Investigate**:
- **OpenAPI/Swagger extensions** for architectural info
- **C4 Model adoption** (Context, Containers, Components, Code)
- **ADR formats** (MADR, Y-Statements, etc.)
- **Architecture as Code** initiatives (Structurizr, etc.)
- **Graph-based representations** (Neo4j schemas, RDF, etc.)
- **Domain-Specific Languages** for architecture description

**Look for**:
- Standards with tooling ecosystems
- Adoption by major companies
- Integration with popular IDEs/agents

---

**Q5.2**: What tools are leading teams using?

**Research tool categories**:

1. **Static Analysis → Documentation**:
   - Sourcegraph (code intelligence)
   - CodeSee (visual maps)
   - Understand (architecture analysis)
   - Structure101 (dependency analysis)
   - Custom AST parsers

2. **AI-Powered Documentation**:
   - GitHub Copilot Workspace
   - Cursor (codebase-aware AI editor)
   - Codeium (context-aware completions)
   - Tabnine (team knowledge learning)
   - Custom GPT-4/Claude wrappers

3. **Architecture Visualization**:
   - Structurizr (C4 Model)
   - PlantUML (diagrams as code)
   - Mermaid (markdown diagrams)
   - Archi (ArchiMate modeling)

4. **Knowledge Graphs**:
   - Neo4j (codebase as graph)
   - AWS Neptune (dependency graphs)
   - Custom graph databases

**Look for**:
- Open source options vs commercial
- Integration capabilities (IDE, CI/CD, agents)
- Adoption signals (stars, downloads, case studies)

---

### Category 6: Company-Specific Case Studies

**Q6.1**: What are specific companies doing?

**Companies to research** (if public information available):

- **GitHub** (own agents + Copilot)
- **Anthropic** (Claude for code + workspaces)
- **OpenAI** (GPT-4 code interpreter)
- **Google** (Gemini code assist)
- **Microsoft** (Copilot for Azure)
- **Meta** (Llama for code)
- **Sourcegraph** (Cody AI)
- **Replit** (Ghostwriter AI)
- **Cursor** (AI-first editor)
- **Augment Code** (team-specific AI)
- **Tabnine** (enterprise AI coding)

**Look for**:
- Blog posts from engineering teams
- Conference talks (DORA, QCon, StaffEng, etc.)
- Open source "dogfooding" repos
- Documentation of their own systems
- Patents/research papers

---

**Q6.2**: What are startups/scale-ups reporting?

**Look for**:
- Y Combinator companies using AI coding
- Seed/Series A startups blogging about practices
- DevOps/Platform engineering communities
- Reddit (r/ExperiencedDevs, r/MachineLearning)
- Hacker News discussions
- Twitter/X threads from practitioners

**Key signals**:
- Real world pain points solved
- Tools abandoned vs adopted
- Evolution of practices over time

---

## Research Sources

### Primary Sources (Highest Value)

1. **Company Engineering Blogs**:
   - eng.uber.com, netflixtechblog.com, github.blog/engineering
   - Look for: "onboarding", "documentation", "AI agents", "code generation"

2. **Conference Talks (2024-2026)**:
   - QCon, GOTO, StaffEng, LeadDev, DevOpsDays
   - Search YouTube/InfoQ for: "AI coding", "LLM for code", "agent development"

3. **Open Source Repositories**:
   - GitHub search: `"for AI agents" OR "for LLM" documentation`
   - Look for: `.ai/`, `.agent/`, `docs/architecture/`, `ADRs/`

4. **Research Papers (arXiv, ACM, IEEE)**:
   - Keywords: "code generation", "LLM alignment", "codebase understanding"
   - Focus on: empirical studies, not just model architectures

5. **Developer Communities**:
   - Reddit: r/ExperiencedDevs, r/MachineLearning, r/coding
   - Hacker News: Search "AI coding", "agent alignment"
   - Discord/Slack: AI engineer communities

### Secondary Sources

6. **Tool Documentation**:
   - Read docs of leading tools (Cursor, Codeium, Copilot)
   - Look for: "best practices", "setup", "customization"

7. **Podcasts/Interviews**:
   - Software Engineering Daily, Changelog, CoRecursive
   - Search for: "AI coding", "code generation", "developer tools"

8. **Books (Recent)**:
   - "AI-Assisted Programming" (if published)
   - "Engineering AI Systems" chapters on code generation

9. **Standards Bodies**:
   - OpenAPI Initiative
   - Cloud Native Computing Foundation (CNCF)
   - IEEE Software Architecture standards

---

## Analysis Framework

For each practice/tool/pattern discovered, evaluate:

### Adoption Signals
- [ ] **Evidence Level**: Anecdotal / Single case study / Multiple case studies / Industry standard
- [ ] **Maturity**: Experimental / Production use / Widely adopted
- [ ] **Accessibility**: Open source / Commercial / Proprietary
- [ ] **Integration Complexity**: Trivial / Moderate / Significant

### Effectiveness Indicators
- [ ] **Quantitative Results**: Metrics reported (time saved, quality improvement, etc.)
- [ ] **Qualitative Feedback**: Developer satisfaction, agent accuracy, etc.
- [ ] **Sustainability**: How maintained over time
- [ ] **Scalability**: Works for codebases of what size

### RaiSE Applicability
- [ ] **Alignment with raise.1.analyze.code**: High / Medium / Low
- [ ] **Effort to Adopt**: Low / Medium / High
- [ ] **Value Proposition**: Clear improvement over current SAR system
- [ ] **Multi-Stack Support**: Language/framework agnostic or specific

---

## Synthesis Requirements

### Deliverable 1: Landscape Report

**Format**: Markdown document (~5-8K words)

**Structure**:
```markdown
# Brownfield Documentation for Agentic Development: State of Practice 2026

## Executive Summary
- Key findings (3-5 bullets)
- Paradigm shifts observed
- Gaps in current RaiSE approach

## 1. Documentation Artifact Taxonomy
- Types discovered
- Frequency of use
- Format preferences
- Examples

## 2. Content & Granularity Analysis
- What's documented (with examples)
- Level of detail (with trade-offs)
- Critical vs nice-to-have

## 3. Generation & Maintenance Patterns
- Manual vs automated approaches
- Tools landscape
- Sustainability strategies

## 4. AI Agent Integration Architectures
- RAG patterns
- Prompt engineering strategies
- Context management
- Measured outcomes

## 5. Emerging Standards & Tools
- Standards gaining traction
- Tool categories with leaders
- Open source vs commercial

## 6. Case Studies
- Company A: [Approach + Results]
- Company B: [Approach + Results]
- ...

## 7. Comparison with RaiSE SAR System
- Current strengths to preserve
- Gaps identified
- Opportunities for improvement

## 8. Recommendations for raise.1.analyze.code
[See Deliverable 2]

## References
[Categorized by source type]
```

---

### Deliverable 2: Actionable Recommendations

**Format**: Markdown document with decision matrix

**Structure**:
```markdown
# Recommendations for raise.1.analyze.code Improvement

## Quick Wins (High Impact, Low Effort)

| Recommendation | Impact | Effort | Priority | Source |
|----------------|--------|--------|----------|--------|
| [REC-001] Add machine-readable metadata to SAR reports | High | Low | P0 | [Source] |
| ... | | | | |

## Strategic Improvements (High Impact, High Effort)

| Recommendation | Impact | Effort | Priority | Timeline |
|----------------|--------|--------|----------|----------|
| [REC-010] Implement RAG-optimized documentation format | High | High | P1 | Q2 2026 |
| ... | | | | |

## Experimental Additions (Uncertain Impact, Low-Medium Effort)

| Recommendation | Potential Impact | Effort | Priority | Validation Needed |
|----------------|------------------|--------|----------|-------------------|
| [REC-020] Generate knowledge graph from codebase | Medium-High | Medium | P2 | Pilot study |
| ... | | | | |

## Per Recommendation Detail

### REC-001: Add Machine-Readable Metadata to SAR Reports

**Current State**: SAR reports are pure Markdown for human consumption.

**Proposed State**: Add YAML frontmatter with structured metadata:
```yaml
---
report_type: codigo_limpio
generated_date: 2026-01-23
codebase_version: main@abc123
analyzer_version: raise-1.2.0
metrics:
  total_violations: 42
  critical_count: 7
  medium_count: 18
  low_count: 17
patterns_detected:
  - repository_pattern
  - dependency_injection
anti_patterns_detected:
  - god_class: 3
  - long_method: 12
---
```

**Benefit**: Enables AI agents to:
- Parse key findings without full text analysis
- Track metrics over time
- Query specific aspects ("Show me all critical violations")

**Implementation**:
1. Update SAR templates to include frontmatter
2. Modify raise.1.analyze.code to populate metadata
3. Create validation script for metadata completeness

**Risk**: Low - additive change, doesn't break existing

**Evidence Source**: [Company blog / tool docs / paper]

---

[... repeat for each recommendation]
```

---

### Deliverable 3: Prototype Artifacts (Optional)

If particularly promising patterns are found, create:

1. **Updated SAR Template Example**:
   - Incorporating machine-readable elements
   - With improved structure for AI consumption

2. **Sample Knowledge Graph Schema**:
   - If graph-based approaches are prevalent
   - Neo4j Cypher or RDF format

3. **RAG Prompt Template**:
   - If RAG is common approach
   - System prompt + retrieval strategy

4. **Validation Script**:
   - Checks documentation completeness
   - Ensures AI-consumable format

---

## Success Criteria

This research will be successful if it produces:

1. **Evidence-Based Insights**:
   - [ ] At least 5 real-world case studies with measurable outcomes
   - [ ] At least 3 open source examples to study directly
   - [ ] At least 10 distinct tools/approaches catalogued

2. **Actionable Recommendations**:
   - [ ] At least 3 "quick win" recommendations (high impact, low effort)
   - [ ] At least 2 "strategic" recommendations (high impact, high effort, clear ROI)
   - [ ] Clear prioritization with effort estimates

3. **Novel Insights**:
   - [ ] At least 1 pattern/practice not currently in RaiSE
   - [ ] At least 1 anti-pattern to avoid (validated by practitioners)
   - [ ] Emerging standard or tool with momentum

4. **RaiSE Alignment**:
   - [ ] Clear mapping to raise.1.analyze.code improvement opportunities
   - [ ] Compatibility with RaiSE ontology and methodology
   - [ ] Feasible within raise-commons architecture

---

## Timeline

**Week 1**:
- Days 1-2: Primary source research (company blogs, conference talks)
- Day 3: Open source repository analysis
- Day 4: Tool landscape research
- Day 5: Initial synthesis

**Week 2**:
- Days 1-2: Deep dive on most promising approaches
- Day 3: Case study documentation
- Days 4-5: Recommendations formulation + report writing

**Total**: ~10 working days for thorough research + synthesis

---

## Output Location

**Deliverables saved to**:
```
specs/main/research/brownfield-agent-docs/
├── landscape-report.md              # Deliverable 1
├── recommendations.md               # Deliverable 2
├── prototypes/                      # Deliverable 3 (optional)
│   ├── sar-template-v2.md
│   ├── knowledge-graph-schema.cypher
│   ├── rag-prompt-template.md
│   └── validation-script.sh
└── sources/
    ├── case-studies/
    ├── tools-reviewed/
    └── papers-analyzed/
```

---

## Meta: How to Use This Prompt

### For AI Research Agent

If executing this research with an AI agent:

1. **Read this prompt completely**
2. **Execute research questions sequentially** (Q1 → Q2 → ... → Q6)
3. **Document sources as you go** (save URLs, quotes, examples)
4. **Build evidence catalog** before synthesizing
5. **Apply analysis framework** to each finding
6. **Generate deliverables** according to templates above
7. **Validate** against success criteria

### For Human Researcher

If executing manually:

1. **Allocate 2-3 hour blocks** for focused research
2. **Use parallel tabs** for broad initial sweep
3. **Take structured notes** (use analysis framework as template)
4. **Bookmark liberally**, organize later
5. **Set time limit** on rabbit holes (30 min max per thread)
6. **Synthesize daily** (don't just accumulate sources)
7. **Pair with practitioner** if possible (validate findings)

---

## Related RaiSE Context

**Current system being improved**: `raise.1.analyze.code`
- Command: `.agent/workflows/01-onboarding/raise.1.analyze.code.md`
- Templates: `.specify/templates/raise/sar/*.md`
- Architecture analysis: `specs/main/analysis/architecture/raise.1.analyze-code-architecture.md`

**RaiSE Principles to Honor**:
- Evidence-based (no speculation)
- Pragmatic over academic
- Business impact oriented
- Multi-stack support
- Sustainability (maintainable documentation)

**Adjacent RaiSE Commands**:
- `raise.1.discovery` (PRD generation) - could consume SAR outputs
- `raise.2.vision` (solution vision) - needs architecture context
- `raise.rules.generate` (guardrail generation) - could use pattern catalogs

---

**Research Start Date**: [YYYY-MM-DD]
**Research End Date**: [YYYY-MM-DD]
**Researcher**: [Name/Agent ID]
**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed

---

*This research prompt is part of the RaiSE Framework evolution, aimed at improving brownfield onboarding and AI agent alignment capabilities.*
