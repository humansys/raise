# Synthesis: PM Sync Boundaries

**Research Date:** 2026-02-14
**Sources Analyzed:** 34
**Decision Context:** RaiSE backlog sync design (S15.6)

---

## Major Claims (Triangulated)

### Claim 1: Active/Sprint Filtering is the Primary Scope Boundary

**Confidence:** HIGH

**Evidence:**
1. [Linear Backlog and Active Issues](https://linear.app/changelog/2019-06-27-backlog-and-active-issues) - Linear explicitly separates Backlog (unprioritized) from Active Issues (on roadmap)
2. [Azure DevOps Sprint Assignment](https://learn.microsoft.com/en-us/azure/devops/boards/sprints/assign-work-sprint?view=azure-devops) - Sprint assignment is the primary filter for active work
3. [Zoho Sprints Backlog Management](https://www.zoho.com/sprints/backlog-management.html) - Quick filters and custom filters focus on active vs backlog sections
4. [Jira Sprint Planning](https://activitytimeline.com/blog/how-to-manage-resources-during-jira-sprint-planning) - Resource planning focuses on sprint-assigned items
5. [ClickUp Sprint Backlog](https://clickup.com/blog/how-developers-can-manage-sprint-backlogs/) - Automations trigger on "task added to backlog" vs sprint

**Disagreement:** None found — universal pattern across all surveyed tools

**Implication for RaiSE:**
- Default sync scope should be **active items only** (current epic/sprint)
- Full backlog sync should be opt-in or triggered separately
- Status-based filtering (e.g., "In Progress", "Todo" vs "Backlog", "Done") is secondary boundary
- This aligns with agent reasoning needs — agents work on active items, not entire backlog

---

### Claim 2: Epic-Story-Task Hierarchy Synced Selectively, Not Fully

**Confidence:** HIGH

**Evidence:**
1. [Exalate Epic Sync](https://docs.exalate.com/docs/how-to-sync-epics-in-jira-on-premise) - Epics must sync before stories to preserve parent-child relationships
2. [Atlassian Epics, Stories, Initiatives](https://www.atlassian.com/agile/project-management/epics-stories-themes) - 3-level hierarchy (initiative → epic → story)
3. [Wrike Hierarchy Guide](https://www.wrike.com/agile-guide/epics-stories-tasks/) - 4-level hierarchy (theme → epic → story → task) for enterprises
4. [Tempo Jira Hierarchy](https://www.tempo.io/products/project-portfolio-management-software-ppm/jira-hierarchy) - Advanced features connect projects in shared delivery plans for enterprise visibility
5. [GitHub-Jira Integration (Exalate)](https://exalate.com/blog/jira-github-issues-integration/) - Jira hierarchy flattened to GitHub labels/descriptions (no native hierarchy)

**Disagreement:** Platform capabilities differ — Jira/Asana support hierarchy, GitHub does not

**Implication for RaiSE:**
- **Epic + Story levels** are sufficient for most use cases
- Task-level sync creates noise and performance issues (too granular)
- Hierarchical sync requires **dependency ordering** (parent before child)
- For graph-native storage, RaiSE can preserve hierarchy metadata without platform constraints
- **Recommendation:** Sync epic (context) + stories (executable units), skip tasks/subtasks

---

### Claim 3: Core Fields + Selective Custom Fields, Not All Fields

**Confidence:** HIGH

**Evidence:**
1. [Jira REST API](https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/) - Custom fields as `customfield_<ID>`; create metadata API defines valid fields per issue type
2. [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) - Up to 50 custom fields (built-in + custom)
3. [Asana Task Metadata](https://github.com/Asana/asana-api-meta/blob/master/src/resources/task.yaml) - Custom fields as array in `custom_fields` property
4. [Monday.com Column Values](https://developer.monday.com/api-reference/reference/column-values-v2) - GraphQL fragments for selective field retrieval
5. [Unito Jira-GitHub](https://unito.io/blog/how-to-integrate-github-and-jira/) - Field mapping flexibility: "Customer Impact" (Jira) → GitHub label
6. [Linear API Filtering](https://linear.app/developers/filtering) - Filter server-side instead of fetching all fields and filtering client-side

**Disagreement:** None — universal pattern to allow field selection

**Implication for RaiSE:**
- **Core fields** always synced: ID, title, description, status, assignee, created_at, updated_at
- **Agile fields** context-dependent: epic_link, sprint, story_points (only if using agile workflow)
- **Custom fields** user-configurable: define mapping in sync configuration
- **Performance optimization:** Request only needed fields (GraphQL fragments pattern)
- **Calculated/derived fields** excluded by default — don't trigger sync, cause timestamp issues (see Source 32: Salesforce formula fields)

**Recommended Core Field Set for RaiSE:**
```
Required: id, title, description, status, type
High Priority: assignee, priority, labels, created_at, updated_at
Context-Dependent: epic_link, sprint, story_points, due_date
Excluded: calculated fields, system metadata (views, watchers, comments_count)
```

---

### Claim 4: Platform-Specific Features Require Transformation Rules

**Confidence:** HIGH

**Evidence:**
1. [Exalate Jira-GitHub](https://exalate.com/blog/jira-github-issues-integration/) - Jira work item types (Epic/Story/Bug) don't map to GitHub's flat structure; use transformation rules to convert to labels/descriptions
2. [Jira Software Cloud API - Epic](https://developer.atlassian.com/cloud/jira/software/rest/api-group-epic/) - Agile fields (sprint, closedSprints, flagged) are Jira-specific
3. [Getint vs Exalate](https://www.getint.io/blog/getint-vs-exalate) - Centralized UI (Getint) vs scripting engine (Exalate Groovy) for transformations
4. [Unito GitHub Integration](https://guide.unito.io/en/articles/5131988-a-guide-to-unito-s-github-integration) - Custom rules decide which data points sync and how (comments, attachments)

**Disagreement:** None — transformation is universal requirement for cross-platform sync

**Implication for RaiSE:**
- RaiSE as **platform-agnostic graph** avoids this problem — no platform-specific constraints
- Sync from external PM tools **into** RaiSE requires **inbound transformation** (Jira epic → RaiSE epic node)
- Sync from RaiSE **out** to external tools requires **outbound transformation** (RaiSE epic → Jira epic or GitHub project)
- For S15.6 (project → personal sync), **no transformation needed** — same RaiSE schema on both sides
- Store platform origin metadata for future external sync: `source_platform: jira`, `source_id: PROJ-123`

---

### Claim 5: Bidirectional Sync Requires Conflict Resolution Strategy

**Confidence:** HIGH

**Evidence:**
1. [Stacksync Conflict Resolution](https://www.stacksync.com/blog/deep-dive-stacksyncs-conflict-resolution-engine-for-bidirectional-crm-integration) - Define clear precedence rules; automated resolution with manual review for critical data
2. [Bi-Directional Sync Challenges](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - Traditional conflict resolution is error-prone, requires manual intervention
3. [Data Sync Best Practices](https://xreinn.com/blog/10-best-practices-for-managing-data-synchronization) - Test bidirectional sync before committing; status updates should flow automatically
4. [github-jira-sync (yksanjo)](https://github.com/yksanjo/github-jira-sync) - Production tool includes conflict resolution in architecture
5. [PM Tool Integration Guide](https://daily.dev/blog/7-steps-to-integrate-project-management-tools) - Native integrations preferred over third-party to avoid API breakage

**Disagreement:** Strategy varies — last-write-wins vs merge procedures vs manual resolution

**Implication for RaiSE:**
- For S15.6 (project → personal), **unidirectional sync** sufficient initially (project is source of truth)
- Bidirectional needed if personal changes should propagate back (e.g., status updates, notes)
- **Conflict strategy options:**
  - **Last-write-wins with timestamp:** Simple, risk of data loss
  - **Field-level merge:** Title/description from source, status/notes from personal
  - **Project-wins for structure, personal-wins for state:** Hybrid approach
- **Recommendation for RaiSE:** Start with **unidirectional (project → personal)**, add bidirectional in future story with field-level precedence rules

---

### Claim 6: Webhook + Queue Architecture for Scalable Real-Time Sync

**Confidence:** MEDIUM

**Evidence:**
1. [github-jira-sync (yksanjo)](https://github.com/yksanjo/github-jira-sync) - Webhook-based with queue architecture for production use
2. [ClickUp Sprint Backlog](https://clickup.com/blog/how-developers-can-manage-sprint-backlogs/) - Automations trigger on events ("when task added to backlog")
3. [Atlassian Epic Automation](https://www.atlassian.com/agile/tutorials/how-to-sync-epics-stories-with-jira-software-automation) - Event-driven field updates for internal sync

**Disagreement:** Not all tools use real-time — some use polling intervals

**Implication for RaiSE:**
- For project → personal sync, **event-driven** preferred over polling (lower latency, no wasted cycles)
- **Trigger events:** Epic created, story added to epic, story status changed, story assigned
- **Queue benefits:** Decouples event capture from sync processing; handles bursts; retry on failure
- RaiSE CLI context: Events could trigger filesystem watches → sync on change detection
- **Recommendation:** File-based event triggers (inotify/fswatch) or explicit `rai sync` command initially; webhook integration for external PM tools in future

---

### Claim 7: Performance Trade-Off Between Sync Scope and Latency

**Confidence:** HIGH

**Evidence:**
1. [GitHub Projects API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects) - Requires 2N API calls (add item + update fields separately); no atomic operations
2. [Bi-Directional Sync Challenges](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - Middleware serialization/deserialization adds delays
3. [Linear API Filtering](https://linear.app/developers/filtering) - Server-side filtering recommended to avoid fetching all issues
4. [Monday.com GraphQL Fragments](https://developer.monday.com/api-reference/reference/column-values-v2) - Selective field retrieval for performance
5. [Salesforce Formula Fields](https://www.fivetran.com/blog/automatically-sync-formula-field-values-in-salesforce) - Derived data doesn't trigger modified_at updates, complicates change detection

**Disagreement:** None

**Implication for RaiSE:**
- **Narrow scope = faster sync, less conflict surface, lower API costs**
- **Broad scope = more context, but performance penalty, higher complexity**
- For RaiSE project → personal sync (local filesystem):
  - No API rate limits (major advantage over cloud PM tools)
  - File I/O is bottleneck, not network
  - **Optimize:** Read only changed files (mtime tracking), write only diff
- **Recommendation:** Active items only (default), full backlog on-demand

---

## Patterns & Paradigm Shifts

### Pattern 1: Scope Filtering Over Full Replication

**Observation:** All modern PM sync tools apply filters rather than syncing entire databases. Common filter dimensions:
- **Status-based:** Active/Backlog, In Progress/Done, Open/Closed
- **Time-based:** Current sprint, last N days, upcoming milestones
- **Hierarchy-based:** Epic-level only, Story-level only, Epic+Stories (not tasks)
- **Assignment-based:** My tasks, Team tasks, Unassigned

**Paradigm:** From "replicate everything" to "sync what you need, when you need it"

**RaiSE Application:**
- Default to **current epic + active stories**
- Allow explicit scope expansion via CLI flags: `--include-backlog`, `--all-epics`, `--with-tasks`

---

### Pattern 2: Field Selection Over Full Object Sync

**Observation:** GraphQL adoption in PM tools (Linear, GitHub Projects, Monday.com) enables selective field retrieval. REST APIs increasingly support field projection (`?fields=id,title,status`).

**Paradigm:** From "sync all fields" to "request only needed fields"

**RaiSE Application:**
- Define **minimal field set** for performance (id, title, status)
- Define **standard field set** for typical use (+ description, assignee, priority)
- Define **full field set** for comprehensive sync (+ custom fields, metadata)
- User-configurable in `.raise/config.toml` or CLI args

---

### Pattern 3: Transformation Layers for Platform Differences

**Observation:** No 1:1 mapping between platforms. Successful sync tools use transformation rules:
- Jira Epic → GitHub Project
- Jira Story Points (number) → GitHub Label ("3 points")
- Asana Custom Field → Monday.com Column
- Bidirectional transformations require inbound + outbound rules

**Paradigm:** From "direct mapping" to "transformation as first-class concept"

**RaiSE Application:**
- RaiSE graph is **canonical format** (platform-agnostic)
- External sync (future) requires transformation layer
- Internal sync (project ↔ personal) needs **no transformation** (same schema)
- Store `source_platform` and `source_id` metadata for provenance

---

### Pattern 4: Hierarchical Sync with Dependency Ordering

**Observation:** Parent-child relationships (Epic → Story → Task) require sync ordering. Creating child before parent causes failures. Tools handle this by:
- Syncing top-down (epics first, then stories)
- Queuing child items until parent synced
- Using temporary placeholders (orphan resolution)

**Paradigm:** From "flat sync" to "topology-aware sync"

**RaiSE Application:**
- RaiSE backlog already hierarchical (epic → stories)
- Sync must preserve order: Epic nodes before Story nodes
- Graph can represent hierarchy as edges (`story BELONGS_TO epic`)
- Sync algorithm: Topological sort, sync in dependency order

---

### Pattern 5: Event-Driven Sync Over Polling

**Observation:** Modern PM tools use webhooks for real-time sync:
- Jira webhooks on issue created/updated
- GitHub webhooks on issue/PR events
- Linear webhooks on issue state changes
Polling (check every N minutes) still used for:
- Legacy systems without webhook support
- Fallback when webhooks fail
- Initial bulk sync

**Paradigm:** From "periodic polling" to "event-driven push"

**RaiSE Application:**
- CLI context: Filesystem events (inotify) or explicit `rai sync` command
- No webhook infrastructure needed for local sync
- Future external PM sync: Implement webhook receivers

---

### Pattern 6: Conflict Resolution as Configuration, Not Code

**Observation:** Best sync tools make conflict strategy **user-configurable**:
- Exalate: Groovy scripts for custom logic
- Unito: UI-based precedence rules
- Getint: Centralized conflict resolution settings
Hard-coded strategies (e.g., always last-write-wins) cause user frustration.

**Paradigm:** From "opinionated conflict resolution" to "user-defined precedence"

**RaiSE Application:**
- For S15.6 (unidirectional project → personal), conflicts unlikely
- Future bidirectional: Define precedence in `.raise/sync-config.toml`:
  ```toml
  [sync.conflict_resolution]
  strategy = "field_level"  # or "last_write_wins", "manual"

  [sync.field_precedence]
  title = "project"        # Project always wins for structure
  description = "project"
  status = "personal"      # Personal wins for state
  notes = "personal"
  ```

---

## Gaps & Unknowns

### Gap 1: Offline Sync Strategies

**What we couldn't find:**
- How PM tools handle offline edits on both sides (mobile apps, disconnected mode)
- Operational transformation (OT) or CRDT usage in PM sync
- Conflict resolution for long-lived offline branches

**Why it matters for RaiSE:**
- RaiSE is offline-first by design
- Project and personal scopes may diverge significantly before sync
- Need strategy for "sync after days/weeks of independent work"

**Mitigation:**
- Start with "project → personal" unidirectional (no offline conflict)
- Document as known limitation for bidirectional
- Future research: CRDTs for conflict-free sync

---

### Gap 2: Custom Field Mapping at Scale

**What we couldn't find:**
- How organizations manage custom field mappings across 100+ projects
- Governance for custom field proliferation
- Schema evolution strategies (field added/removed/renamed)

**Why it matters for RaiSE:**
- Custom fields create long-term maintenance burden
- Mapping configuration becomes technical debt
- No clear industry best practice found

**Mitigation:**
- For S15.6, avoid custom field sync initially
- Sync only core fields (well-defined, stable schema)
- Custom field support in future story with governance model

---

### Gap 3: Performance Benchmarks for Sync Scope

**What we couldn't find:**
- Quantitative data on sync performance by scope size
- "How many items can sync in <1 second?" for different tools
- Trade-off curves (latency vs scope size vs field count)

**Why it matters for RaiSE:**
- Unknown if "active epic only" is sufficient performance-wise
- Can't predict if full backlog sync is feasible
- No data-driven threshold for "too much data"

**Mitigation:**
- Instrument sync performance in S15.6 implementation
- Log metrics: items synced, fields per item, total time, bottlenecks
- Iterate on scope boundaries based on real performance data

---

## Synthesis Summary

### Convergent Findings (High Confidence)

1. **Scope:** Active items (current sprint/epic) is universal default; full backlog is opt-in
2. **Granularity:** Epic + Story levels sufficient; Task-level creates noise
3. **Fields:** Core fields always; custom fields selectively; calculated fields excluded
4. **Hierarchy:** Parent-before-child ordering required for hierarchical sync
5. **Transformation:** Required for cross-platform; not needed for same-schema sync
6. **Performance:** Narrow scope and selective fields optimize for speed; broad scope trades latency for completeness

### Divergent Findings (Context-Dependent)

1. **Conflict Resolution:** Varies by tool — last-write-wins vs field-level vs manual
2. **Sync Trigger:** Event-driven (modern) vs polling (legacy/fallback)
3. **Architecture:** Distributed (Exalate) vs centralized (Getint/Unito)
4. **Hierarchy Depth:** 3-level (small teams) vs 4-level (enterprises)

### Unanswered Questions

1. How to handle offline sync conflicts (CRDT? OT? Manual?)
2. Best practices for custom field governance at scale
3. Quantitative performance benchmarks for scope decisions

---

## Next Steps

1. **Review synthesis with stakeholders** — validate findings align with RaiSE design goals
2. **Draft recommendation** — translate findings into actionable sync scope for S15.6
3. **Create ADR** — document architectural decision with evidence references
4. **Update S15.6 plan** — refine implementation tasks based on research
