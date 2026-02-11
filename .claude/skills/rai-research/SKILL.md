---
name: rai-research
description: >
  Conduct epistemologically rigorous research to inform decisions.
  Use before ADRs, when evaluating competing approaches, entering
  unfamiliar domains, or resolving parking lot items. Produces
  evidence catalogs with triangulated claims and actionable recommendations.

license: MIT

metadata:
  raise.work_cycle: tools
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.2.0"

# RaiSE Observable Workflow hooks---

# Research: Evidence-Based Investigation

## Purpose

Conduct epistemologically rigorous research to inform decisions. Standing on the shoulders of giants, not reinventing wheels.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps with full evidence catalog and research prompt template.

**Ha (破)**: Scale depth to decision importance; adapt prompt template.

**Ri (離)**: Create domain-specific research protocols and custom prompts.

## Epistemological Foundation

| Principle | Application |
|-----------|-------------|
| **Falsifiability** | Seek disconfirming evidence, not just confirmation |
| **Triangulation** | 3+ independent sources per major claim |
| **Source Hierarchy** | Primary > Secondary > Tertiary |
| **Confidence Calibration** | Explicit uncertainty acknowledgment |
| **Reproducibility** | Others can verify your findings |

## Context

**When to use:**
- Before architectural decisions (ADRs)
- When evaluating competing approaches
- When entering unfamiliar domains
- When parking lot items need resolution

**Inputs required:**
- Clear research question(s)
- Decision context (what will this research inform?)
- Time/depth constraint (quick scan vs deep dive)

**Output:**
- Research report with evidence catalog
- Actionable recommendation with confidence level

## Evidence Levels

Engineering-specific evidence hierarchy:

| Level | Criteria | Examples |
|-------|----------|----------|
| **Very High** | Peer-reviewed, production-proven at scale, >10k stars | Academic papers, official docs, foundational OSS |
| **High** | Expert practitioners at established companies, >1k stars | FAANG blogs, popular frameworks |
| **Medium** | Community-validated, emerging consensus, >100 stars | Dev.to with engagement, conference talks |
| **Low** | Single source, unvalidated, <100 stars | Personal blogs, new repos, anecdotal |

## Steps

### Step 0.5: Query Context (Optional)

If unified graph is available, query for prior research and methodology patterns:

```bash
rai memory query "research methodology evidence" --types pattern,session --limit 5
```

Review returned patterns to avoid duplicating prior research.

**Verification:** Context loaded or graph not available (proceed without).

> **If context unavailable:** Run `rai memory build` first, or skip to Step 1.

### Step 1: Frame the Question

Define research scope:
- Primary question (what we need to know)
- Secondary questions (supporting context)
- Decision this informs (ADR, implementation, backlog)
- Depth constraint (timeboxed hours or thoroughness level)

**Verification:** Question is specific and falsifiable.

> **If you can't continue:** Question too vague → Decompose into sub-questions.

### Step 1.5: Create Research Prompt & Select Tool

Using the research prompt template (`references/research-prompt-template.md`), document:
- Role definition for research specialist
- Search strategy with specific keywords
- Evidence evaluation criteria
- Output format requirements
- Quality checklist

**Verification:** Research prompt file created in `work/research/{topic}/prompt.md`

#### Tool Selection

| Tool | When to Use | Best For |
|------|-------------|----------|
| `ddgr` | Quick scans (1-2h) | Simple questions, no API key |
| `llm -m perplexity` | Standard/Deep (4h+) | Citations, complex synthesis |
| `WebSearch` | Any depth | Reliable fallback |

**Delegation Pattern:**
1. Create research prompt using template
2. If depth=deep-dive AND perplexity available: `llm -m perplexity "$(cat prompt.md)"`
3. Else if depth=quick-scan AND ddgr available: Execute ddgr searches
4. Else: Use WebSearch + manual synthesis

> **If you can't continue:** All tools fail → Fall back to manual research.

### Step 2: Survey the Landscape

Gather sources systematically:
- Academic papers (Google Scholar, arXiv)
- Official documentation
- GitHub repos (stars, activity, issues)
- Engineering blogs
- Community discussions (Reddit, HN, Discord)

**Verification:** 10+ sources collected (scale to importance).

> **If you can't continue:** Few sources → Topic may be too niche; document the gap.

### Step 3: Build Evidence Catalog

For each source, record:

```markdown
**Source**: [Title + Link]
- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low
- **Key Finding**: [One-line takeaway]
- **Relevance**: [How it answers our question]
```

**Verification:** Evidence catalog file created in `sources/`.

> **If you can't continue:** Sources conflict → Good! Document the disagreement.

### Step 4: Triangulate Claims

For each major finding:
- Find 3+ independent confirmations
- Note consensus vs disagreement
- Identify confidence level

```markdown
**Claim**: [Statement]
**Confidence**: HIGH/MEDIUM/LOW
**Evidence**:
  1. [Source A] - [Finding]
  2. [Source B] - [Finding]
  3. [Source C] - [Finding]
**Disagreement**: [Any contrary evidence]
```

**Verification:** Major claims have 3+ sources.

> **If you can't continue:** Can't triangulate → Lower confidence level; document gap.

### Step 5: Synthesize Findings

Extract patterns:
- What does the evidence converge on?
- What gaps exist?
- What's RaiSE-specific vs general?

Create synthesis sections:
- Key Findings (numbered, evidence-backed)
- Patterns & Paradigm Shifts
- Gaps & Unknowns

**Verification:** Findings trace back to evidence catalog.

> **If you can't continue:** Contradictory evidence → Document as "contested" with both sides.

### Step 6: Formulate Recommendation

Produce actionable output:
- Recommendation with confidence level
- Trade-offs acknowledged
- Implementation implications
- Risks and mitigations

```markdown
## Recommendation

**Decision**: [What we should do]
**Confidence**: HIGH/MEDIUM/LOW
**Rationale**: [Why, based on evidence]
**Trade-offs**: [What we're accepting]
**Risks**: [What could go wrong]
```

**Verification:** Recommendation is actionable and traces to findings.

> **If you can't continue:** Evidence insufficient → Recommend "more research needed" with specific gaps.

### Step 7: Link to Decision

Connect research to governance:
- Reference or create ADR if architectural
- Update backlog if actionable
- Update parking lot if deferred

**Verification:** Research has clear governance linkage.

> **If you can't continue:** No clear decision → Archive in `work/research/`.

## Output Structure

```
work/research/{topic}/
├── README.md                 ← Navigation + 15-min overview
├── {topic}-report.md         ← Main findings
├── executive-summary.md      ← 5-min version (optional)
├── sources/
│   └── evidence-catalog.md   ← All sources with ratings
└── {derivatives}/            ← Decision matrix, specs, roadmaps
```

## Quality Checklist

- [ ] Research question is specific and falsifiable
- [ ] 10+ sources consulted (scaled to importance)
- [ ] Evidence catalog created with levels
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence level explicitly stated
- [ ] Contrary evidence acknowledged
- [ ] Recommendation is actionable
- [ ] Governance linkage established (ADR, backlog, or parking lot)

## Scaling Guidance

| Depth | Time | Sources | Use When |
|-------|------|---------|----------|
| **Quick Scan** | 1-2h | 5-10 | Low-stakes, familiar domains |
| **Standard** | 4-8h | 15-30 | Most ADRs, technology evaluation |
| **Deep Dive** | 2-5d | 50-100+ | Strategic decisions, unfamiliar domains |

## References

- Research prompt template: `references/research-prompt-template.md`
- Existing research: `work/research/`
- Constitution: `framework/reference/constitution.md` (Principle: Kaizen)
