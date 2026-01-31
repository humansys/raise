---
id: tools-research
titulo: "Research: Evidence-Based Investigation"
work_cycle: tools
frequency: as-needed
fase_metodologia: 0

prerequisites: []
template: templates/raise/tools/research-report.md
gate: null
next_kata: null

adaptable: true
shuhari:
  shu: "Follow all steps with full evidence catalog"
  ha: "Scale depth to decision importance"
  ri: "Create domain-specific research protocols"

version: 1.0.0
---

# Research: Evidence-Based Investigation

## Purpose

Conduct epistemologically rigorous research to inform decisions. Standing on the shoulders of giants, not reinventing wheels.

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

| Level | Criteria | Examples |
|-------|----------|----------|
| **Very High** | Peer-reviewed, production-proven, >1000 stars | Academic papers, official docs, major OSS |
| **High** | Expert practitioners, well-maintained projects | Engineering blogs (FAANG), 100+ star repos |
| **Medium** | Community validated, emerging consensus | Dev.to, tutorials with engagement |
| **Low** | Single source, unvalidated claims | Random blogs, no corroboration |

## Steps

### Step 1: Frame the Question

Define research scope:
- Primary question (what we need to know)
- Secondary questions (supporting context)
- Decision this informs (ADR, implementation, backlog)
- Depth constraint (timeboxed hours or thoroughness level)

**Verification:** Question is specific and falsifiable.

> **If you can't continue:** Question too vague → Decompose into sub-questions.

### Step 2: Survey the Landscape

Gather sources systematically:
- Academic papers (Google Scholar, arXiv)
- Official documentation
- GitHub repos (stars, activity, issues)
- Engineering blogs (search "[topic] engineering blog")
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

> **If you can't continue:** No clear decision → Research may be exploratory; archive in `work/research/`.

## Output Structure

```
work/research/{topic}/
├── README.md                 ← Navigation + 15-min overview
├── {topic}-report.md         ← Main findings (this template)
├── executive-summary.md      ← 5-min version (optional for deep research)
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

## Scaling Guidance (ShuHaRi)

| Depth | Time | Sources | Use When |
|-------|------|---------|----------|
| **Quick Scan** | 1-2h | 5-10 | Low-stakes decisions, familiar domains |
| **Standard** | 4-8h | 15-30 | Most ADRs, new technology evaluation |
| **Deep Dive** | 2-5d | 50-100+ | Strategic decisions, unfamiliar domains |

## References

- Existing research: `work/research/`
- ADR template: `templates/raise/adr.md`
- Constitution: `framework/reference/constitution.md` (Principle: Kaizen)
