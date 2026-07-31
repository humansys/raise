---
name: rai-research
description: Research with triangulated evidence to inform decisions. Use before ADRs or evaluations.
model: sonnet

allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(ddgr:*)"
  - WebFetch
  - WebSearch

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

**Supply Chain Health evaluation** — When research involves package or dependency selection, evaluate supply chain health for each package under consideration:

- **PyPI version history** — stable releases? frequent yanks?
- **Download count** — established package or niche?
- **Last release date** — actively maintained?
- **Maintainer count** — bus factor (single point of failure)?
- **Yank history** — has this package had yanked versions?
- **Alternative evaluation** — lighter alternative available? DIY in <50 LOC?
- **Isolation strategy** — can this be confined to a single module?

> See pattern **PAT-E-1282**: *Consumer reputation ≠ package stability — verify supply chain independently*

Document findings under a "Supply Chain Health" section in the research report. When research doesn't involve package evaluation, state "N/A — no package evaluation in scope."

<verification>
10+ sources collected (scaled to depth). Supply chain health evaluated for each package under consideration (or N/A).
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

### Step 6: Publish Report

Persist report to local path and docs adapter:

Use `raise_docs_write` MCP tool with doc_type="research", title="{topic} — Research Report {YYYY-MM-DD}", content="[assembled report: question, evidence synthesis, recommendation, trade-offs, risks]", output_path="work/research/{topic}/{topic}-report.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write research \
  --title "{topic} — Research Report {YYYY-MM-DD}" \
  --stdin \
  --output-path work/research/{topic}/{topic}-report.md << 'EOF'
[assembled report: question, evidence synthesis, recommendation, trade-offs, risks]
EOF
```

Evidence catalog and README are local-only — write with Write tool as usual.

<verification>
Report persisted locally and published via docs adapter. Evidence catalog and README saved locally.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Report | `work/research/{topic}/{topic}-report.md` (local) + docs adapter (type: research) |
| Evidence catalog | `work/research/{topic}/sources/evidence-catalog.md` (local) |
| Navigation | `work/research/{topic}/README.md` (local) |
| Next | ADR, backlog item, or parking lot update |

## Quality Checklist

- [ ] Research question is specific and falsifiable
- [ ] 10+ sources consulted (scaled to depth)
- [ ] Evidence catalog created with levels rated
- [ ] Major claims triangulated (3+ independent sources)
- [ ] Confidence level explicitly stated on recommendation
- [ ] Contrary evidence acknowledged (not hidden)
- [ ] Supply chain health evaluated for packages under consideration (or N/A)
- [ ] Governance linkage established (ADR, backlog, or parking lot)
- [ ] NEVER present single-source findings as consensus

## References

- Research prompt template: `references/research-prompt-template.md`
- Existing research: `work/research/`
- Epistemology: falsifiability, triangulation, source hierarchy
