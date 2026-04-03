---
name: rai-research
description: Research with triangulated evidence to inform decisions. Use before ADRs or evaluations.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public

---

# Research

## Purpose

Conduct epistemologically rigorous research to inform decisions. Standing on the shoulders of giants, not reinventing wheels.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps with full evidence catalog and research prompt template
- **Ha**: Scale depth to decision importance; adapt prompt template
- **Ri**: Create domain-specific research protocols and custom prompts

## Context

**When to use:** Before ADRs, when evaluating competing approaches, entering unfamiliar domains, or resolving parking lot items.

**When to skip:** Decision is low-stakes and reversible, or prior research exists in `work/research/`.

**Inputs:** Clear research question(s), decision context, depth constraint (quick/standard/deep).

| Depth | Time | Sources | Use when |
|-------|------|---------|----------|
| Quick scan | 1-2h | 5-10 | Low-stakes, familiar domains |
| Standard | 4-8h | 15-30 | Most ADRs, technology evaluation |
| Deep dive | 2-5d | 50-100+ | Strategic decisions, unfamiliar domains |

## Steps

### Step 1: Frame the Question

Define: primary question, secondary questions, decision this informs, depth constraint.

**Epistemological principles:** Seek disconfirming evidence (falsifiability), require 3+ sources per claim (triangulation), primary > secondary > tertiary sources.

<verification>
Question is specific and falsifiable.
</verification>

<if-blocked>
Question too vague → decompose into sub-questions.
</if-blocked>

### Step 2: Select Tool & Survey

**Tool selection:**

| Tool | Best for |
|------|----------|
| `ddgr "query"` | Quick scans, no API key needed |
| `llm -m perplexity "query"` | Deep research with citations |
| WebSearch | Reliable fallback |

Gather sources: academic papers, official docs, GitHub repos (stars/activity), engineering blogs, community discussions.

<verification>
10+ sources collected (scaled to depth).
</verification>

### Step 3: Build Evidence Catalog

Per source: type (primary/secondary/tertiary), evidence level, key finding, relevance.

| Evidence level | Criteria |
|---------------|----------|
| Very High | Peer-reviewed, production-proven at scale, >10k stars |
| High | Expert practitioners at established companies, >1k stars |
| Medium | Community-validated, emerging consensus, >100 stars |
| Low | Single source, unvalidated, <100 stars |

Save to `work/research/{topic}/sources/evidence-catalog.md`.

<verification>
Evidence catalog created with levels rated.
</verification>

### Step 4: Triangulate & Synthesize

Per major claim: find 3+ independent confirmations, note consensus vs disagreement, assign confidence (HIGH/MEDIUM/LOW), acknowledge contrary evidence explicitly.

Extract patterns: convergence points, gaps, RaiSE-specific vs general findings.

<verification>
Major claims have 3+ sources. Contrary evidence documented.
</verification>

### Step 5: Recommend & Link

Produce: recommendation with confidence level, trade-offs, implementation implications, risks.

Connect to governance: create/reference ADR if architectural, update backlog if actionable, update parking lot if deferred.

<verification>
Recommendation is actionable and traces to evidence.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Report | `work/research/{topic}/{topic}-report.md` |
| Evidence catalog | `work/research/{topic}/sources/evidence-catalog.md` |
| Navigation | `work/research/{topic}/README.md` |
| Next | ADR, backlog item, or parking lot update |

## Quality Checklist

- [ ] Research question is specific and falsifiable
- [ ] 10+ sources consulted (scaled to depth)
- [ ] Evidence catalog created with levels rated
- [ ] Major claims triangulated (3+ independent sources)
- [ ] Confidence level explicitly stated on recommendation
- [ ] Contrary evidence acknowledged (not hidden)
- [ ] Governance linkage established (ADR, backlog, or parking lot)
- [ ] NEVER present single-source findings as consensus

## References

- Research prompt template: `references/research-prompt-template.md`
- Existing research: `work/research/`
- Epistemology: falsifiability, triangulation, source hierarchy
