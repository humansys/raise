---
research_id: "[TOPIC]-[YYYYMMDD]"
primary_question: "[Specific, falsifiable question]"
decision_context: "[What this informs: ADR, feature, backlog]"
depth: "[quick-scan|standard|deep-dive]"
created: "[YYYY-MM-DD]"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: [Topic]

> Template for structured AI research with epistemological rigor
> Based on evidence from 20 sources (meta-research 2026-01-31)

---

## Role Definition

You are a **Research Specialist** with expertise in **[domain]**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: [Main question to answer - must be specific and falsifiable]

**Secondary** (supporting questions):
1. [Supporting question 1]
2. [Supporting question 2]
3. [Supporting question 3]

---

## Decision Context

**This research will inform**: [Specific decision, ADR, story design, architecture choice, etc.]

**Stakeholder**: [Who needs this information]

**Timeline**: [When decision will be made]

**Impact**: [Consequences of getting this wrong - why rigor matters]

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `[specific search terms]`
   - arXiv: `[topic keywords]`
   - Purpose: Peer-reviewed research, theoretical foundations

2. **Official documentation**
   - [Technology/framework] official docs
   - Standards bodies (W3C, IETF, etc.)
   - Purpose: Authoritative technical specifications

3. **Production evidence**
   - GitHub repositories (filter: >100 stars, active maintenance)
   - Engineering blogs: FAANG, GitLab, Atlassian, established companies
   - Purpose: Real-world validation, battle-tested patterns

4. **Community validation**
   - Reddit (r/[relevant]), Hacker News, Discord/Slack communities
   - Conference talks, podcasts
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**: [List 5-10 specific search terms]

**Sources to avoid**: [If any - e.g., outdated frameworks, deprecated APIs]

---

### Evidence Evaluation

For each source you find, assess and record:

- **Type**:
  - Primary (original research, official docs, first-hand experience)
  - Secondary (practitioner synthesis, curated guides, tutorials)
  - Tertiary (aggregations, summaries, listicles)

- **Evidence Level** (use RaiSE engineering criteria):
  - **Very High**: Peer-reviewed papers, official docs, OSS >10k stars with proven production use
  - **High**: Expert practitioners at established companies, well-maintained projects >1k stars
  - **Medium**: Community-validated resources, emerging projects >100 stars, engaged articles
  - **Low**: Single sources, <100 stars, unvalidated claims, personal blogs without corroboration

- **Key Finding**: One-line takeaway from this source

- **Relevance**: How does this answer our research question?

- **Date**: Publication or last update date (recency matters for tech)

---

### Triangulation Requirements

**Minimum source counts** (scale to depth):
- Quick scan (1-2h): 5-10 sources
- Standard (4-8h): 15-30 sources
- Deep dive (2-5d): 50-100+ sources

**For major claims**:
- Require **3+ independent confirmations** from different sources
- If <3 sources: Lower confidence level or mark as "emerging/unconfirmed"

**Handling disagreement**:
- Document contrary evidence explicitly
- Describe the nature of disagreement (methodological, contextual, temporal)
- Don't ignore conflicts - they're valuable information

**Confidence calibration**:
- HIGH: 3+ Very High or High sources, convergent evidence, no significant contrary findings
- MEDIUM: 2-3 sources, some convergence, minor conflicts or gaps
- LOW: <2 sources, significant disagreement, or mostly Low evidence level

---

## Output Format

Produce the following artifacts in `work/research/[topic]/`:

### 1. Evidence Catalog (`sources/evidence-catalog.md`)

For each source:

```markdown
**Source**: [Title + Link]
- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low
- **Date**: [YYYY-MM-DD or YYYY]
- **Key Finding**: [One-line takeaway]
- **Relevance**: [How it answers the question]
```

Include summary statistics:
- Total sources: [N]
- Evidence distribution: Very High (X%), High (Y%), Medium (Z%), Low (W%)
- Temporal coverage: [Date range]

---

### 2. Synthesis Document (`synthesis.md`)

#### Major Claims (Triangulated)

For each significant finding:

```markdown
**Claim [N]**: [Statement of finding]

**Confidence**: HIGH/MEDIUM/LOW

**Evidence**:
1. [Source A Title](URL) - [Specific finding]
2. [Source B Title](URL) - [Specific finding]
3. [Source C Title](URL) - [Specific finding]

**Disagreement**: [Any contrary evidence or "None found"]

**Implication**: [What this means for our decision]
```

#### Patterns & Paradigm Shifts

Identify recurring themes across sources:
- What architectural patterns emerge?
- What trade-offs are commonly discussed?
- Any paradigm shifts in recent years?

#### Gaps & Unknowns

Document what you **couldn't** find:
- Unanswered sub-questions
- Areas with insufficient evidence
- Topics requiring deeper investigation

---

### 3. Recommendation (`recommendation.md`)

```markdown
## Recommendation

**Decision**: [What we should do - specific and actionable]

**Confidence**: HIGH/MEDIUM/LOW

**Rationale**: [Why, based on triangulated evidence - reference specific sources]

**Trade-offs**: [What we're accepting/sacrificing with this choice]

**Risks**: [What could go wrong]

**Mitigations**: [How to address the risks]

**Alternatives Considered**: [Other options and why not chosen]
```

---

## Quality Criteria

Your research output will be validated against this checklist:

**Question & Scope**
- [ ] Research question is specific and falsifiable
- [ ] Decision context clearly stated
- [ ] Scope boundaries defined (what NOT to research)

**Evidence Gathering**
- [ ] Minimum source count met (scaled to depth)
- [ ] Mix of academic, official, and practitioner sources
- [ ] Sources include publication/update dates
- [ ] Evidence catalog complete with all required fields

**Rigor & Validation**
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicitly stated for each claim
- [ ] Contrary evidence acknowledged (if present)
- [ ] Gaps and unknowns documented

**Actionability**
- [ ] Recommendation is specific and actionable
- [ ] Trade-offs explicitly acknowledged
- [ ] Risks identified with mitigations
- [ ] Clear link to decision context

**Reproducibility**
- [ ] All sources cited with URLs
- [ ] Search keywords documented
- [ ] Tool/model used recorded
- [ ] Research date recorded

---

## Constraints

**Time**: [Specific timebox if applicable - e.g., "4 hours max"]

**Focus priorities**: [What to prioritize if time-constrained]

**Out of scope**: [What explicitly NOT to research]

---

## Reproducibility Metadata

Include in final output (typically in README.md):

```markdown
**Research Metadata**:
- Tool/model used: [e.g., "perplexity-sonar", "WebSearch", "ddgr + manual synthesis"]
- Search date: [YYYY-MM-DD]
- Prompt version: [From frontmatter - currently 1.0]
- Researcher: [Agent or human name]
- Total time: [Hours spent]
```

---

## Tool Selection Guide

Choose research tool based on depth and availability:

| Depth | First Choice | Fallback | Always Available |
|-------|--------------|----------|------------------|
| Quick scan | `ddgr` | WebSearch | WebSearch |
| Standard | `llm -m perplexity` | ddgr + synthesis | WebSearch |
| Deep dive | `llm -m perplexity` | Manual + Task agent | WebSearch + synthesis |

**Check availability**:
```bash
# ddgr (free, no API key)
which ddgr

# perplexity (requires llm + API key)
llm models list | grep perplexity

# WebSearch (always available)
# Built-in capability, no check needed
```

---

## Example Usage

See `examples/tech-stack-evaluation-prompt.md` for a complete example of this template in use.

---

## References

- Research kata: `.raise/katas/tools/rai-research.md`
- Evidence catalog template: `.raise/templates/tools/evidence-catalog.md`
- Meta-research on this template: `work/research/ai-research-prompts/`

---

**Template Version**: 1.0
**Created**: 2026-01-31
**Based on**: Meta-research with 20 sources (7 Very High, 8 High, 5 Medium evidence)
**Last Reviewed**: 2026-01-31
**Next Review**: 2026-04-30 (quarterly)
