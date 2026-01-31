---
research_id: "lean-feature-specs-20260131"
primary_question: "What are the critical success factors for a lean feature specification format that optimizes for both human understanding and AI alignment in software development?"
decision_context: "Design feature-level spec template for RaiSE framework (feature/design kata)"
depth: "standard"
created: "2026-01-31"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Lean Feature Specification Format

> Dogfooding the research prompt template
> For RaiSE feature spec design (human-AI collaboration context)

---

## Role Definition

You are a **Research Specialist** with expertise in **requirements engineering, technical specification design, and AI-assisted software development**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are the critical success factors for a lean feature specification format that optimizes for both human understanding (reviewability, clarity) and AI alignment (sufficient context for accurate implementation)?

**Secondary** (supporting questions):
1. What specification elements are most critical for AI code generation accuracy?
2. What formats enable quick human review (5-10 min scan for approval)?
3. How do examples/samples compare to prose descriptions for AI understanding?
4. What level of acceptance criteria detail is optimal (Gherkin vs informal vs none)?
5. What's the minimal viable spec (MVS) that prevents misalignment?
6. How do AI-assisted development specs differ from traditional specs?

---

## Decision Context

**This research will inform**: Design of `feature/design` kata and `.raise/templates/tech/tech-design-feature.md` template updates

**Stakeholder**: RaiSE framework users (developers working with AI assistants like Claude)

**Timeline**: Before implementing F1.1 (Project Scaffolding) - need spec format defined first

**Impact**: Wrong format = misalignment across 20+ features in raise-cli backlog, wasted implementation cycles, poor human oversight. This is a foundational process decision affecting all feature development.

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `"AI-assisted software development" requirements specification`
   - arXiv: `"large language models" software specification, "AI code generation" requirements`
   - Purpose: Research on human-AI collaboration in software engineering

2. **Official documentation**
   - GitHub Copilot best practices (if available)
   - Cursor AI documentation on prompt context
   - Anthropic Claude documentation on code generation
   - Purpose: Vendor guidance on effective spec formats for AI

3. **Production evidence**
   - GitHub repos using AI-assisted development (search for CLAUDE.md, .cursorrules patterns)
   - Engineering blogs: "writing specs for AI", "AI code generation best practices"
   - Companies known for AI-assisted dev: Vercel, Supabase, Linear
   - Purpose: Real-world patterns that work in practice

4. **Community validation**
   - Reddit r/ClaudeAI, r/programming: discussions on spec formats
   - Hacker News: AI coding assistant discussions
   - Discord communities: Anthropic, Cursor, AI dev tools
   - Purpose: Practitioner feedback on what works/doesn't

**Keywords to search**:
- "lean specification AI code generation 2024 2025"
- "requirements engineering AI assisted development"
- "feature spec format for language models"
- "human AI collaboration software specifications"
- "minimal viable specification AI alignment"
- "acceptance criteria AI code generation"
- "CLAUDE.md best practices"
- "prompt engineering for software development"
- "AI context for code generation"
- "specification formats LLM understanding"

**Sources to avoid**: Pre-2023 sources (before widespread LLM code generation adoption)

---

### Evidence Evaluation

For each source you find, assess and record:

- **Type**:
  - Primary (research papers, official vendor docs, direct experience)
  - Secondary (engineering blogs, tutorials, case studies)
  - Tertiary (community discussions, aggregations)

- **Evidence Level** (use RaiSE engineering criteria):
  - **Very High**: Peer-reviewed research on human-AI dev, official AI vendor docs, >10k star projects with AI-assisted workflows
  - **High**: Engineering blogs from established companies using AI dev, well-documented AI-assisted projects >1k stars
  - **Medium**: Community-validated practices, emerging patterns >100 stars, conference talks on AI development
  - **Low**: Single anecdotes, personal blogs without validation, speculation

- **Key Finding**: One-line takeaway relevant to spec format design

- **Relevance**: How does this inform our lean feature spec template?

- **Date**: Publication date (field evolving rapidly - recency critical)

---

### Triangulation Requirements

**Minimum source counts**: Standard depth = 15-30 sources

**For major claims** (e.g., "Examples are more effective than prose for AI"):
- Require **3+ independent confirmations**
- At least 1 from academic/vendor research
- At least 1 from production validation
- If contradictory: Document both perspectives with context

**Handling disagreement**:
- AI vs traditional spec approaches will differ - document paradigm shift
- Different AI tools (Copilot vs Claude vs Cursor) may need different formats - note tool-specific guidance
- Human preferences vs AI alignment may conflict - identify and articulate trade-offs

**Confidence calibration**:
- HIGH: 3+ sources, vendor research + production validation, convergent evidence
- MEDIUM: 2-3 sources, some validation, emerging consensus
- LOW: <2 sources, speculation, or significant disagreement

---

## Output Format

Produce the following artifacts in `work/research/lean-feature-specs/`:

### 1. Evidence Catalog (`sources/evidence-catalog.md`)

For each source:

```markdown
**Source**: [Title + Link]
- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low
- **Date**: [YYYY-MM-DD]
- **Key Finding**: [Specific insight about spec formats]
- **Relevance**: [How it applies to RaiSE feature specs]
```

Include summary statistics:
- Total sources: [N]
- Evidence distribution by level
- Source types: Academic (X), Vendor (Y), Production (Z), Community (W)
- Temporal: 2023 (X), 2024 (Y), 2025 (Z)

---

### 2. Synthesis Document (`synthesis.md`)

#### Major Claims (Triangulated)

Example structure:

```markdown
**Claim 1**: Concrete examples outperform prose descriptions for AI code generation accuracy

**Confidence**: HIGH/MEDIUM/LOW

**Evidence**:
1. [Source A] - [Specific finding with data if available]
2. [Source B] - [Supporting finding]
3. [Source C] - [Production validation]

**Disagreement**: [Any contrary evidence or contexts where this doesn't hold]

**Implication**: Feature spec template should include code examples, not just descriptions
```

#### Critical Success Factors

Ranked list of what makes a good feature spec for human-AI collaboration:
1. [Factor 1] - [Why critical] - [Evidence sources]
2. [Factor 2] - [Why critical] - [Evidence sources]
...

#### Minimal Viable Specification (MVS)

What sections are absolutely required vs optional?
- Required: [List with rationale]
- Optional but valuable: [List with when to include]
- Skip: [What can be omitted without harm]

#### Human vs AI Optimization

Comparison matrix:

| Element | Human Benefit | AI Benefit | Trade-off |
|---------|--------------|------------|-----------|
| Prose description | Context, why | Low value | Verbose |
| Code examples | Quick scan | High value | Takes time |
| Gherkin scenarios | Test clarity | ? | Verbose |
| ... | ... | ... | ... |

---

### 3. Recommendation (`recommendation.md`)

```markdown
## Recommendation

**Decision**: [Specific feature spec template structure]

**Confidence**: HIGH/MEDIUM/LOW

**Rationale**: [Evidence-based reasoning]

**Template Structure** (proposed):
1. [Section 1] - [Purpose] - [Evidence]
2. [Section 2] - [Purpose] - [Evidence]
...

**Trade-offs**:
- Accept: [What we sacrifice for AI alignment]
- Accept: [What we sacrifice for human speed]
- Gain: [What we achieve with this balance]

**Risks**:
- [Risk 1] - [Mitigation]
- [Risk 2] - [Mitigation]

**Next Steps**:
1. Create feature/design kata using this template
2. Test with F1.1 (Project Scaffolding)
3. Iterate based on real usage
```

---

## Quality Criteria

Your research output will be validated against this checklist:

**Question & Scope**
- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (feature spec template design)
- [x] Scope boundaries defined (feature-level, not project-level)

**Evidence Gathering**
- [ ] Minimum 15-30 sources gathered
- [ ] Mix of academic, vendor, production, community sources
- [ ] Recent sources (2023-2025 preferred)
- [ ] Evidence catalog complete

**Rigor & Validation**
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicit
- [ ] Trade-offs between human/AI needs documented
- [ ] Gaps acknowledged (this is emerging field)

**Actionability**
- [ ] Specific template structure proposed
- [ ] Each section justified by evidence
- [ ] Trade-offs explicitly stated
- [ ] Testing plan for validation

**Reproducibility**
- [ ] All sources cited with URLs
- [ ] Search keywords documented
- [ ] Tool used recorded
- [ ] Research date recorded

---

## Constraints

**Time**: 6 hours max (standard depth)

**Focus priorities**:
1. Critical success factors for AI alignment (highest)
2. Human reviewability requirements (highest)
3. Minimal viable spec structure (high)
4. Examples vs prose effectiveness (medium)
5. Gherkin necessity (lower - likely overkill for simple features)

**Out of scope**:
- Project-level specs (we have those templates already)
- User-facing documentation (different purpose)
- API documentation (different audience)
- Full Gherkin/BDD frameworks (too heavy for our use case)

---

## Reproducibility Metadata

```markdown
**Research Metadata**:
- Tool/model used: WebSearch (ddgr unavailable, perplexity not configured)
- Search date: 2026-01-31
- Prompt version: 1.0
- Researcher: Claude Sonnet 4.5
- Total time: [To be recorded]
```

---

## Tool Selection Guide

**Selected tool**: WebSearch (built-in fallback)

**Rationale**:
- ddgr failed in earlier research (HTTP 202 errors)
- llm/perplexity not installed
- WebSearch proven reliable in meta-research
- Standard depth suitable for WebSearch + synthesis

---

## Expected Outcomes

This research should answer:
1. What sections go in the feature spec template?
2. How detailed should each section be?
3. Should we use Gherkin for acceptance criteria?
4. How important are code examples vs prose?
5. What's different from traditional specs given AI collaboration?

**Success criteria**: Clear recommendation for `feature/design` kata and template structure, validated by 15+ sources with HIGH confidence on critical factors.

---

**Prompt Status**: READY FOR EXECUTION
**Next Action**: Execute research using WebSearch
