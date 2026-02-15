---
research_id: "offline-first-sync-20260214"
primary_question: "What sync strategies do offline-first tools use for reliable sync with eventual consistency?"
decision_context: "ADR for RaiSE backlog sync architecture"
depth: "standard"
created: "2026-02-14"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Offline-First Sync Strategies

> Template for structured AI research with epistemological rigor
> Based on evidence from 20 sources (meta-research 2026-01-31)

---

## Role Definition

You are a **Research Specialist** with expertise in **distributed systems, eventual consistency, and offline-first architectures**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What sync strategies do offline-first tools (Git, CouchDB, PouchDB, local-first software) use for reliable sync with eventual consistency?

**Secondary** (supporting questions):
1. How do these systems handle conflict resolution (automatic vs manual, CRDTs, operational transforms)?
2. What patterns exist for partial sync (incremental, selective, delta-based)?
3. How do they achieve network failure resilience (retry policies, queue management, offline queues)?
4. What are the trade-offs between different sync approaches (performance, complexity, correctness)?
5. How do they maintain local-first queryability during sync (non-blocking, background sync)?
6. What are the token efficiency implications for AI-driven systems?

---

## Decision Context

**This research will inform**: Architecture Decision Record (ADR) for RaiSE backlog sync strategy

**Stakeholder**: RaiSE development team, first client onboarding 2026-02-10

**Timeline**: Decision needed before implementing backlog sync to external systems (Linear, Jira, GitHub)

**Impact**: Getting this wrong means:
- Data loss or corruption in team collaboration scenarios
- Poor user experience with sync conflicts
- Token inefficiency (re-syncing, conflict resolution queries)
- Technical debt from wrong abstraction

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `"offline-first" "eventual consistency" "conflict resolution"`
   - Google Scholar: `CRDTs "distributed systems" "local-first"`
   - arXiv: `"operational transformation" sync`
   - Purpose: Theoretical foundations, correctness proofs

2. **Official documentation**
   - CouchDB/PouchDB replication protocol
   - Git internals (object model, merge strategies)
   - Automerge, Yjs documentation
   - CRDT libraries (automerge, yjs, json-joy)
   - Purpose: Authoritative technical specifications

3. **Production evidence**
   - GitHub repos: CouchDB, PouchDB, Automerge, Yjs, ElectricSQL, PowerSync
   - Engineering blogs: Linear (sync engine), Figma (multiplayer), Notion (offline)
   - ink & switch research (local-first software)
   - Purpose: Real-world validation, battle-tested patterns

4. **Community validation**
   - Reddit: r/webdev, r/reactjs, r/programming
   - Hacker News: discussions on local-first, CRDTs, sync
   - local-first.fm podcast
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "offline-first sync"
- "eventual consistency patterns"
- "CRDT conflict resolution"
- "local-first software"
- "sync engine architecture"
- "partial sync incremental"
- "network resilience retry policy"
- "Git merge strategies"
- "CouchDB replication"
- "operational transformation"

**Sources to avoid**:
- Pre-2020 mobile sync patterns (Firebase Realtime DB, old Parse)
- Client-server architectures without offline-first design

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
- Standard (4-8h): 15-30 sources

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

Produce the following artifacts in `work/research/offline-first-sync/`:

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
- [ ] Minimum source count met (15-30 for standard depth)
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

**Time**: 4-8 hours (standard depth)

**Focus priorities** (if time-constrained):
1. Conflict resolution strategies (highest priority for RaiSE)
2. Partial sync patterns (token efficiency)
3. Network resilience patterns
4. Performance implications

**Out of scope**:
- Real-time collaboration (WebRTC, WebSockets) - not needed for RaiSE
- Blockchain/distributed ledger approaches - overkill
- Mobile-specific sync (app backgrounding, push notifications)

---

## Reproducibility Metadata

Include in final output (typically in README.md):

```markdown
**Research Metadata**:
- Tool/model used: [e.g., "WebSearch", "perplexity-sonar", "ddgr + manual synthesis"]
- Search date: 2026-02-14
- Prompt version: 1.0
- Researcher: Claude (Sonnet 4.5)
- Total time: [Hours spent]
```

---

## Tool Selection Guide

Choose research tool based on depth and availability:

| Depth | First Choice | Fallback | Always Available |
|-------|--------------|----------|------------------|
| Standard | `llm -m perplexity` | ddgr + synthesis | WebSearch |

**Check availability**:
```bash
# ddgr (free, no API key)
which ddgr

# perplexity (requires llm + API key)
llm models list | grep perplexity
```

---

## Context for RaiSE

**Current architecture**:
- Local backlog: SQLite + unified graph
- Token efficiency: Critical (every query costs)
- Query patterns: Filtered by status, labels, dependencies
- Collaboration: External systems (Linear, Jira, GitHub) as secondary

**Design constraints**:
- Local is source of truth (local-first)
- External systems are collaboration layer
- No real-time sync needed (eventual consistency OK)
- Must handle offline work gracefully
- Token budget limits re-sync frequency

**Success metrics**:
- Zero data loss
- Predictable conflict resolution
- Low token overhead
- Developer-friendly UX

---

**Template Version**: 1.0
**Created**: 2026-02-14
**Based on**: Research prompt template v1.0 (2026-01-31)
