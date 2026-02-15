---
research_id: "bidirectional-sync-20260214"
primary_question: "What are production-proven patterns for bidirectional synchronization between heterogeneous systems with dual-truth ownership?"
decision_context: "ADR for RaiSE backlog sync architecture"
depth: "standard"
created: "2026-02-14"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Bidirectional Sync & Conflict Resolution

> Template for structured AI research with epistemological rigor
> Based on evidence from 20 sources (meta-research 2026-01-31)

---

## Role Definition

You are a **Research Specialist** with expertise in **distributed systems, data synchronization, and conflict resolution**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are production-proven patterns for bidirectional synchronization between heterogeneous systems with dual-truth ownership (local system as source of truth for workflows, external system as source of truth for team collaboration)?

**Secondary** (supporting questions):
1. What conflict resolution strategies exist (CRDTs, Operational Transform, Last-Write-Wins, Vector Clocks, Three-Way Merge) and when should each be used?
2. How do production systems handle "dual source of truth" scenarios where different systems own different aspects of the same data?
3. What are the architectural patterns for sync across heterogeneous backends (REST APIs, webhooks, polling, event streams)?
4. What trade-offs exist between different conflict resolution approaches in practice?

---

## Decision Context

**This research will inform**: Architecture Decision Record (ADR) for RaiSE backlog synchronization system

**Stakeholder**: RaiSE framework development team (Emilio + collaborators)

**Timeline**: Immediate - needed for upcoming client kick-off (2026-02-10 already passed, but pattern needed for production)

**Impact**: This is a critical architectural decision that affects:
- Data integrity across local (governance/backlog.md + memory graph) and external systems (JIRA, GitLab, Odoo)
- Developer experience (merge conflicts, lost work, sync failures)
- Multi-developer collaboration in brownfield repos
- Foundation for future integrations with other backends

Getting this wrong means: data loss, sync conflicts, developer frustration, and potential client trust issues.

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `"conflict-free replicated data types" CRDT`, `"operational transformation"`, `"distributed system synchronization"`
   - arXiv: `bidirectional sync`, `conflict resolution distributed systems`
   - Purpose: Peer-reviewed research, theoretical foundations

2. **Official documentation**
   - JIRA/Atlassian sync documentation
   - Git internals (three-way merge)
   - CouchDB (master-master replication)
   - Purpose: Authoritative technical specifications

3. **Production evidence**
   - GitHub repositories (filter: >100 stars, active maintenance):
     - Sync engines (e.g., Syncthing, ownCloud, git-sync)
     - CRDT libraries (Automerge, Yjs, etc.)
   - Engineering blogs: Figma (multiplayer sync), Linear (offline-first), Notion (blocks sync), Atlassian, GitLab
   - Purpose: Real-world validation, battle-tested patterns

4. **Community validation**
   - Hacker News, Reddit r/distributed, r/programming
   - Conference talks (Strange Loop, QCon on sync/CRDTs)
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "bidirectional sync patterns"
- "conflict resolution strategies production"
- "CRDT operational transform comparison"
- "dual source of truth synchronization"
- "heterogeneous system integration"
- "JIRA GitLab sync architecture"
- "last write wins vector clocks trade-offs"
- "three-way merge conflict resolution"
- "eventual consistency sync"
- "offline-first sync patterns"

**Sources to avoid**: Academic-only papers without production validation, deprecated frameworks (e.g., Google Wave OT)

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

Produce the following artifacts in `work/research/bidirectional-sync/`:

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

**Time**: 4-8 hours max (standard depth)

**Focus priorities**:
1. Production-proven conflict resolution strategies (primary focus)
2. Dual source-of-truth patterns
3. Heterogeneous backend integration patterns
4. Trade-off matrices for RaiSE decision-making

**Out of scope**:
- Blockchain/cryptocurrency consensus (overkill for this use case)
- Real-time collaborative editing (not the problem we're solving)
- Pure academic theory without production validation

---

## Reproducibility Metadata

Include in final output (typically in README.md):

```markdown
**Research Metadata**:
- Tool/model used: [e.g., "WebSearch", "perplexity-sonar", "ddgr + manual synthesis"]
- Search date: 2026-02-14
- Prompt version: 1.0
- Researcher: Claude Sonnet 4.5
- Total time: [Hours spent]
```

---

## RaiSE-Specific Context

**Current architecture**:
- Local backlog: `governance/backlog.md` (markdown) + memory graph (JSONL)
- External: JIRA, GitLab Issues, Odoo (REST APIs)
- Requirement: Bidirectional sync without data loss
- Challenge: Local is truth for Rai workflows, external is truth for team collaboration

**Key considerations**:
- Multi-developer repos (sync conflicts likely)
- Offline-first for local work (eventual consistency acceptable)
- Different backends have different capabilities (REST vs webhooks vs polling)
- Must work generically across JIRA, GitLab, Odoo, future integrations

---

**Template Version**: 1.0
**Created**: 2026-02-14
**Based on**: research-prompt-template.md v1.0
