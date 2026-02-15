---
research_id: "pm-sync-boundaries-20260214"
primary_question: "What scope, granularity, and metadata do production PM sync tools synchronize?"
decision_context: "RaiSE backlog sync design (S15.6) - defining project-to-personal sync boundaries"
depth: "standard"
created: "2026-02-14"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: PM Sync Boundaries

> Structured research on sync scope decisions in production PM tools
> Informing RaiSE backlog sync design

---

## Role Definition

You are a **Research Specialist** with expertise in **project management tools, API design, and data synchronization patterns**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across official docs, GitHub repos, and engineering blogs
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What do production PM sync tools synchronize in terms of scope (full backlog vs filtered), granularity (epic/story/task), metadata fields (standard vs custom), and platform-specific feature handling?

**Secondary** (supporting questions):
1. Do tools sync the entire backlog or apply filters (active items, date ranges, status)?
2. What granularity boundaries exist — epic-only, story-only, or full hierarchy?
3. Which metadata fields are synchronized (core fields vs custom fields vs calculated fields)?
4. How do tools handle platform-specific features that don't map 1:1 (e.g., Jira epics → GitHub projects)?
5. What performance/conflict trade-offs drive these sync boundary decisions?

---

## Decision Context

**This research will inform**: RaiSE backlog sync design (S15.6) — defining what data crosses project-to-personal boundary

**Stakeholder**: RaiSE framework development team

**Timeline**: Feature design phase (week of 2026-02-14)

**Impact**: Wrong boundaries create:
- Too narrow → Missing context for agent reasoning
- Too broad → Performance issues, conflict surface area, noise
- Too granular → Complex sync logic, fragile mappings
- Too coarse → Insufficient detail for execution

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Official documentation**
   - Jira Cloud API sync patterns
   - GitHub Projects API and sync tools
   - Linear API and sync capabilities
   - Asana API sync documentation
   - Monday.com API sync features
   - Purpose: Authoritative technical specifications

2. **Production evidence**
   - GitHub repositories (filter: >100 stars, active maintenance):
     - Jira-GitHub sync tools
     - Multi-platform PM integrations
     - Backlog sync libraries
   - Engineering blogs: Atlassian, GitHub, Linear, Asana engineering teams
   - Purpose: Real-world validation, battle-tested patterns

3. **Community validation**
   - Reddit (r/projectmanagement, r/agile, r/devops)
   - Hacker News discussions on PM tool sync
   - Integration marketplace docs (Zapier, Make, Unito patterns)
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "project management sync scope"
- "Jira API sync granularity"
- "GitHub Projects sync metadata"
- "backlog synchronization patterns"
- "epic story task sync boundaries"
- "custom field mapping PM tools"
- "bi-directional sync conflict resolution"
- "PM tool integration architecture"
- "active sprint vs backlog sync"
- "hierarchical sync epic story subtask"

**Sources to avoid**: Deprecated Jira Server APIs, outdated v1 APIs

---

### Evidence Evaluation

For each source you find, assess and record:

- **Type**:
  - Primary (official API docs, source code, engineering blog from tool makers)
  - Secondary (integration tool docs, tutorials, sync library maintainers)
  - Tertiary (aggregations, comparison posts, listicles)

- **Evidence Level** (use RaiSE engineering criteria):
  - **Very High**: Official API docs, OSS sync tools >10k stars with proven production use
  - **High**: Engineering blogs from PM tool companies, well-maintained integration tools >1k stars
  - **Medium**: Community-validated resources, emerging tools >100 stars, detailed integration guides
  - **Low**: Single sources, <100 stars, unvalidated claims, personal blogs without corroboration

- **Key Finding**: One-line takeaway from this source

- **Relevance**: How does this answer our research question?

- **Date**: Publication or last update date (recency matters for APIs)

---

### Triangulation Requirements

**Minimum source counts** (standard depth):
- 15-30 sources total
- 3+ official API documentation sources
- 5+ production sync tool repositories
- 3+ engineering blog posts
- 2+ community discussions with engagement

**For major claims**:
- Require **3+ independent confirmations** from different sources
- If <3 sources: Lower confidence level or mark as "emerging/unconfirmed"

**Handling disagreement**:
- Document contrary evidence explicitly
- Describe differences (Jira vs GitHub vs Linear philosophies)
- Context matters: enterprise vs startup, 2-way vs 1-way sync

**Confidence calibration**:
- HIGH: 3+ Very High or High sources, convergent evidence across platforms
- MEDIUM: 2-3 sources, some convergence, platform-specific variations
- LOW: <2 sources, significant disagreement, or mostly Low evidence level

---

## Output Format

Produce the following artifacts in `work/research/pm-sync-boundaries/`:

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
- Platform coverage: Jira, GitHub, Linear, Asana, etc.

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

**Disagreement**: [Platform differences or "None found"]

**Implication**: [What this means for RaiSE sync design]
```

#### Patterns & Paradigm Shifts

Focus on:
- Sync scope filtering patterns (active vs archived, date-based, status-based)
- Granularity boundaries (when to sync hierarchy, when to flatten)
- Metadata selection strategies (core fields, custom fields, calculated fields)
- Platform-specific feature mapping approaches
- Performance optimization techniques
- Conflict resolution strategies

#### Gaps & Unknowns

Document what you **couldn't** find:
- Sync patterns for distributed/offline PM workflows
- Custom field mapping strategies across platforms
- Performance benchmarks for different sync scopes

---

### 3. Recommendation (`recommendation.md`)

```markdown
## Recommendation

**Decision**: [Specific sync scope/granularity/metadata for RaiSE]

**Confidence**: HIGH/MEDIUM/LOW

**Rationale**: [Why, based on triangulated evidence - reference sources]

**Trade-offs**: [What we're accepting with this boundary]

**Risks**: [What could go wrong]

**Mitigations**: [How to address the risks]

**Alternatives Considered**: [Other sync strategies and why not chosen]

**RaiSE-Specific Considerations**:
- Graph-native storage implications
- Agent reasoning requirements (what context do agents need?)
- Project-to-personal scope boundary
- Offline-first design constraints
```

---

## Quality Criteria

**Question & Scope**
- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (S15.6 sync boundaries)
- [x] Scope boundaries defined (PM sync tools, not general data sync)

**Evidence Gathering**
- [ ] 15-30 sources minimum
- [ ] Mix of official docs, production tools, and engineering blogs
- [ ] Sources include publication/update dates
- [ ] Evidence catalog complete with all required fields

**Rigor & Validation**
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicitly stated for each claim
- [ ] Platform differences acknowledged
- [ ] Gaps and unknowns documented

**Actionability**
- [ ] Recommendation is specific for RaiSE sync design
- [ ] Trade-offs explicitly acknowledged
- [ ] Risks identified with mitigations
- [ ] Clear link to S15.6 story implementation

**Reproducibility**
- [ ] All sources cited with URLs
- [ ] Search keywords documented
- [ ] Tool/model used recorded
- [ ] Research date recorded

---

## Constraints

**Time**: 4-8 hours (standard depth)

**Focus priorities** (if time-constrained):
1. Scope boundaries (full vs filtered) — HIGHEST PRIORITY
2. Granularity decisions (epic vs story vs task)
3. Metadata field selection
4. Custom field handling — DEFER if needed

**Out of scope**:
- Real-time sync protocols (WebSocket, polling intervals)
- Authentication/authorization mechanisms
- Sync conflict UI/UX patterns
- Historical data migration strategies

---

## Reproducibility Metadata

```markdown
**Research Metadata**:
- Tool/model used: [To be filled after execution]
- Search date: 2026-02-14
- Prompt version: 1.0
- Researcher: Claude Code Agent
- Total time: [To be tracked]
```

---

**Template Version**: 1.0
**Created**: 2026-02-14
**Based on**: RaiSE research prompt template v1
