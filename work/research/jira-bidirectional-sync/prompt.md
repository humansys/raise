---
research_id: "jira-bidirectional-sync-20260214"
primary_question: "What are best practices for bidirectional sync with JIRA?"
decision_context: "RaiSE-JIRA sync architecture design"
depth: "standard"
created: "2026-02-14"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: JIRA Bidirectional Sync Best Practices

> Template for structured AI research with epistemological rigor
> Based on evidence from 20 sources (meta-research 2026-01-31)

---

## Role Definition

You are a **Research Specialist** with expertise in **enterprise integration patterns, API design, and JIRA ecosystem**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are best practices for bidirectional sync with JIRA, including sync state tracking, conflict resolution, and webhook vs polling tradeoffs?

**Secondary** (supporting questions):
1. How do existing tools (Zapier, Unito, Exalate) handle sync state tracking and conflict resolution?
2. What are JIRA API best practices for external system integration?
3. What fields are recommended for external system integration (custom fields, labels, metadata)?
4. What are webhook vs polling tradeoffs for JIRA sync?
5. How do production systems handle sync failures and recovery?

---

## Decision Context

**This research will inform**: Architecture design for RaiSE-JIRA bidirectional sync

**Stakeholder**: RaiSE framework development team

**Timeline**: March 14, 2026 (webinar demo), February 10, 2026 (Jumpstart client kick-off)

**Impact**: JIRA is primary integration target (Humansys is Atlassian Gold Partner, Coppel client uses JIRA). Getting sync wrong means data loss, duplicate work, or sync failures in production. Need production-proven patterns, not experimental approaches.

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `bidirectional synchronization`, `eventually consistent sync`, `conflict-free replicated data types`
   - arXiv: `distributed systems synchronization`, `optimistic replication`
   - Purpose: Peer-reviewed research, theoretical foundations for sync patterns

2. **Official documentation**
   - Atlassian JIRA REST API documentation
   - Atlassian webhooks and event system
   - Atlassian integration guidelines and best practices
   - Purpose: Authoritative technical specifications

3. **Production evidence**
   - GitHub repositories: Zapier JIRA integration, Unito, Exalate, sync-engine projects (filter: >100 stars)
   - Engineering blogs: Atlassian, GitHub, GitLab, Linear, Notion (on their JIRA integrations)
   - Case studies: Companies documenting their JIRA sync implementations
   - Purpose: Real-world validation, battle-tested patterns

4. **Community validation**
   - Reddit (r/jira, r/devops, r/programming), Hacker News
   - Atlassian Community forums
   - Stack Overflow (highly-voted JIRA sync questions)
   - Purpose: Emerging consensus, practitioner wisdom, common pitfalls

**Keywords to search**:
- "JIRA bidirectional sync best practices"
- "JIRA API integration patterns"
- "JIRA webhook vs polling"
- "JIRA conflict resolution"
- "JIRA sync state tracking"
- "Zapier JIRA architecture"
- "Unito sync engine"
- "Exalate synchronization"
- "JIRA external system integration"
- "JIRA custom fields integration"

**Sources to avoid**: Pre-2020 content (JIRA Cloud API has evolved significantly), JIRA Server docs (deprecated), unmaintained sync libraries

---

### Evidence Evaluation

For each source you find, assess and record:

- **Type**:
  - Primary (Atlassian official docs, open-source sync implementations, first-hand case studies)
  - Secondary (practitioner synthesis, integration guides, tutorials)
  - Tertiary (aggregations, summaries, listicles)

- **Evidence Level** (use RaiSE engineering criteria):
  - **Very High**: Atlassian official docs, peer-reviewed papers, Zapier/Unito/Exalate architecture docs, OSS >10k stars
  - **High**: Expert practitioners at established companies, well-maintained sync projects >1k stars
  - **Medium**: Community-validated resources, emerging projects >100 stars, engaged articles
  - **Low**: Single sources, <100 stars, unvalidated claims, personal blogs without corroboration

- **Key Finding**: One-line takeaway from this source

- **Relevance**: How does this answer our research question?

- **Date**: Publication or last update date (recency matters for JIRA API evolution)

---

### Triangulation Requirements

**Minimum source counts** (standard depth: 4-8h): 15-30 sources

**For major claims**:
- Require **3+ independent confirmations** from different sources
- If <3 sources: Lower confidence level or mark as "emerging/unconfirmed"

**Handling disagreement**:
- Document contrary evidence explicitly
- Describe the nature of disagreement (webhook reliability debates, polling interval recommendations, conflict resolution strategies)
- Don't ignore conflicts - they're valuable information

**Confidence calibration**:
- HIGH: 3+ Very High or High sources, convergent evidence, no significant contrary findings
- MEDIUM: 2-3 sources, some convergence, minor conflicts or gaps
- LOW: <2 sources, significant disagreement, or mostly Low evidence level

---

## Output Format

Produce the following artifacts in `work/research/jira-bidirectional-sync/`:

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

**Implication**: [What this means for RaiSE-JIRA sync]
```

#### Patterns & Paradigm Shifts

Identify recurring themes across sources:
- What sync architecture patterns emerge?
- What trade-offs are commonly discussed (webhook vs polling, optimistic vs pessimistic locking, etc.)?
- Any paradigm shifts in JIRA integration patterns in recent years?

#### Gaps & Unknowns

Document what you **couldn't** find:
- Unanswered sub-questions
- Areas with insufficient evidence
- Topics requiring deeper investigation

---

### 3. Recommendation (`recommendation.md`)

```markdown
## Recommendation

**Decision**: [What RaiSE should implement - specific and actionable]

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
- [ ] Decision context clearly stated (RaiSE-JIRA sync, March 14 demo)
- [ ] Scope boundaries defined (focus on JIRA-specific patterns, not generic sync)

**Evidence Gathering**
- [ ] Minimum 15-30 sources (standard depth)
- [ ] Mix of Atlassian official docs, production implementations, and community validation
- [ ] Sources include publication/update dates
- [ ] Evidence catalog complete with all required fields

**Rigor & Validation**
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicitly stated for each claim
- [ ] Contrary evidence acknowledged (webhook vs polling debates, etc.)
- [ ] Gaps and unknowns documented

**Actionability**
- [ ] Recommendation is specific and actionable for RaiSE implementation
- [ ] Trade-offs explicitly acknowledged
- [ ] Risks identified with mitigations
- [ ] Clear link to decision context (sync architecture design)

**Reproducibility**
- [ ] All sources cited with URLs
- [ ] Search keywords documented
- [ ] Tool/model used recorded
- [ ] Research date recorded

---

## Constraints

**Time**: 4-8 hours (standard depth)

**Focus priorities**:
1. Sync state tracking mechanisms (highest priority - most complex)
2. Conflict resolution strategies
3. Webhook vs polling tradeoffs
4. Recommended fields for external integration
5. Production failure/recovery patterns

**Out of scope**:
- Generic sync theory (focus on JIRA-specific)
- JIRA Server implementations (Cloud only)
- Authentication/authorization details (separate concern)
- UI/UX for sync configuration (separate story)

---

## Reproducibility Metadata

Include in final output (in README.md):

```markdown
**Research Metadata**:
- Tool/model used: [WebSearch, ddgr, or perplexity]
- Search date: 2026-02-14
- Prompt version: 1.0
- Researcher: Claude (rai-research skill)
- Total time: [Hours spent]
```

---

## Tool Selection Guide

For this research (standard depth, 4-8h):
- First choice: WebSearch (always available, good for recent JIRA docs)
- Fallback: ddgr + manual synthesis if available
- Deep dive option: perplexity if configured

---

## Context: Why This Matters

- **Humansys**: Atlassian Gold Partner - JIRA integration is strategic
- **Coppel client**: Uses JIRA - sync must work for paying customer
- **March 14 webinar**: Public demo - needs to be robust
- **February 10 Jumpstart**: First paying customer - can't afford data loss

Production-proven patterns required, not experimental approaches.
