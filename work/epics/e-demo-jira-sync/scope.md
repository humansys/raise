# Epic E-DEMO: JIRA Sync Enabler - Scope

> **Status:** IN PROGRESS
> **Type:** Enabler Epic (commercial feature validation + dogfooding)
> **Release:** N/A (Demo-scoped, not part of v2 release)
> **Branch:** `demo/atlassian-webinar`
> **Created:** 2026-02-14 (Saturday 16:00)
> **Target:** 2026-02-16 11:00 AM (Monday - 42 hours from start)
> **Client:** Coppel (Jose Gregorio Molina Guerrero, demo to Zaira - National Manager of Agility)

---

## Objective

Demonstrate **bidirectional workflow orchestration** between RaiSE and JIRA for Coppel's product management governance needs:

**Demo Workflow:**
1. PM/stakeholder creates epic in JIRA (starts product initiative)
2. Rai pulls epic → appears in local backlog
3. Rai designs epic → creates user stories locally
4. Stories pushed to JIRA → team visibility
5. Team approves story in JIRA workflow
6. Story status synced back → prioritized in RaiSE backlog

**Strategic Goals:**
1. **Validate product governance at scale** (Coppel migrating from Plan View to JIRA)
2. **Dogfood RaiSE under extreme pressure** (42 hours validates framework under brutal constraints)
3. **Prove AI-assisted PM workflow** (governance automation without 1:1 coaching)
4. **Foundation for RaiSE PRO** (commercial offering architecture validation)

**Value proposition:** Proves RaiSE enables governance at scale through bidirectional workflow orchestration. Demonstrates AI agents guiding product owners through governance in their existing tools.

**Success criteria:**
- Demo executes end-to-end: JIRA epic → Rai design → JIRA stories → status sync
- Manual triggers acceptable (`pull`/`push` commands, not webhooks)
- Full RaiSE process followed despite 42-hour constraint
- Coppel context understood: governance scalability, JIRA adoption, value measurement

---

## Architectural Context

### Affected Modules

| Module | Domain | Layer | Role in Epic |
|--------|--------|-------|--------------|
| **mod-cli** | Application Layer | Orchestration | New `rai backlog sync` command group |
| **mod-config** | Shared Kernel | Leaf | Sync configuration (provider, credentials, scope) |
| **mod-memory** | Ontology | Integration | Sync state tracking (last sync, entity mapping) |
| **New: mod-providers** | Integration | Integration | JIRA/GitLab/Odoo adapter implementations |

### Bounded Context Spans

- **Primary:** bc-ontology (backlog is part of knowledge graph)
- **Secondary:** bc-application-layer (CLI commands)
- **New:** bc-external-integration (provider adapters)

**Cross-context justification:** External tool sync inherently crosses boundaries. Clean separation via port/adapter pattern (BacklogProvider interface).

### Key Constraints

**MUST guardrails (from mod-cli, mod-config, mod-memory):**
- Type annotations on all code (pyright strict)
- >90% test coverage
- Pydantic models for all schemas
- Engine/content separation
- No secrets in code

**Architecture patterns to follow:**
- PAT-E-150: Drift review before implementation
- ADR-012: Skills orchestrate, CLI provides data
- ADR-015: File-first design, optional DB upgrade

---

## Features (16 SP estimated, 42 hours, ~10 SP/day aggressive velocity)

| ID | Feature | Size | Dependencies | Description |
|----|---------|:----:|:------------:|-------------|
| **S-DEMO.1** | Research synthesis & architecture design | M (3 SP) | — | ✅ **COMPLETE** - 6 research outputs consolidated, 3 ADRs created (OAuth, sync architecture, entity schema) |
| **S-DEMO.2** | OAuth 2.0 authentication | M (3 SP) | S-DEMO.1 | ✅ **COMPLETE** - Full OAuth 2.0 + PKCE flow, Fernet encryption, automatic token refresh, CLI command (44 min, 6.8x velocity) |
| **S-DEMO.3** | JIRA client (bidirectional) | M (3 SP) | S-DEMO.2 | ✅ **COMPLETE** - Bidirectional JIRA client: read epics/stories, write stories, rate limiting (10 req/sec), field filtering, BacklogProvider interface (135 min, 1.33x velocity) |
| **S-DEMO.4** | Entity properties & sync metadata | S (2 SP) | S-DEMO.3 | ✅ **COMPLETE** - Pydantic models (RaiSyncMetadata, EntityProperty), storage/retrieval functions (set/get/has), integration test infrastructure, manual validation script (110 min, 1.22x velocity) |
| **S-DEMO.5** | Sync engine (pull + push) | L (4 SP) | S-DEMO.4 | **Bidirectional sync:** `pull` (JIRA → local), `push` (local → JIRA). Epic + Story granularity. Manual triggers. Idempotent. Dry-run mode. |
| **S-DEMO.6** | Demo rehearsal & retrospective | XS (1 SP) | S-DEMO.5 | Rehearse Coppel workflow 3+ times. Demo script. Capture learnings. Epic retrospective. |

**Total:** 6 features, 16 SP estimated, 42 hours (Sat 16:00 → Mon 11:00)

**Critical path:** S-DEMO.1 ✅ → S-DEMO.2 → S-DEMO.3 → S-DEMO.4 → S-DEMO.5 → S-DEMO.6 (sequential, no parallelism)

**Scope note:** Task-level sync deferred to post-demo (epic + story sufficient for workflow demonstration)

---

## In Scope

### MUST (Demo Blockers)

**Core Functionality (Bidirectional Workflow):**
- **Bidirectional sync:** JIRA ↔ RaiSE backlog (pull + push operations)
- **Demo granularity:** Epic + Story levels (task sync deferred to post-demo)
- OAuth 2.0 authentication with JIRA Cloud (authorization code + PKCE)
- Entity properties for sync metadata tracking (epic/story IDs + Forge metadata)
- CLI commands:
  - `rai backlog pull --source jira` (JIRA epic → local backlog)
  - `rai backlog push --source jira` (local stories → JIRA)
- **Manual triggers** (not webhooks/polling — acceptable for demo)
- Active epic detection (sync current epic from git branch context)
- Dry-run mode: `--dry-run` flag (preview changes without execution)
- Basic error handling with user-friendly messages

**Demo Workflow (Coppel Scenario):**
```
1. PM creates epic in JIRA:
   JIRA Epic: "Product Governance Initiative"

2. Rai pulls epic:
   `rai backlog pull --source jira`
   → Epic appears in governance/backlog.md

3. Rai designs epic locally:
   `/rai-epic-design` → Creates 5 stories locally

4. Rai pushes stories to JIRA:
   `rai backlog push --source jira`
   → 5 JIRA Stories appear linked to epic

5. Team approves story in JIRA:
   JIRA Story status: "To Do" → "Approved"

6. Rai syncs status back:
   `rai backlog pull --source jira`
   → Story prioritized in RaiSE backlog
```

**JIRA Hierarchy (Demo Scope - Epic + Story only):**
```
JIRA Epic (Product Governance Initiative)
  ├── JIRA Story (Define governance principles)
  ├── JIRA Story (Create compliance checklist)
  ├── JIRA Story (Build approval workflow)
  ├── JIRA Story (Implement value metrics)
  └── JIRA Story (Train product owners)
```

**Note:** Task-level sync (subtasks) deferred to post-demo for timeline feasibility.

**Research-Backed Architecture:**
- Local-first sync (local is source of truth for Rai)
- Hub-and-spoke topology (memory graph as central hub)
- Field-level ownership (Rai owns workflow state, team owns collaboration fields)
- Exponential backoff retry (3-7 retries over 1-3 days)
- Internal IDs + JIRA IDs (stable cross-project identifiers for Forge)

**Forge Vision (Designed for V3, Foundation Now):**

This MVP is the foundation for **Rai in Forge** — hosted intelligence aggregating data across projects/teams.

**Architecture Evolution:**
```
MVP (Demo):
  Local Dev (RaiSE CLI) → JIRA (one-way push)

V3 (Forge):
  Local Devs ↔ JIRA ↔ Remote Devs (JIRA only)
              ↕️
        Rai in Forge
    (Cross-project intelligence)
```

**Why Design for Forge Now:**
1. **Full granularity** (epic/story/task) → Execution-level visibility for pattern recognition
2. **Internal IDs** (E-DEMO, S-DEMO.1, T-DEMO.1.1) → Stable across projects, enables aggregation
3. **Entity properties** → Metadata travels with JIRA items, queryable cross-project
4. **Bidirectional schema ready** → Remote devs update JIRA, Rai stays in sync (V3)

**Example Forge Capabilities (V3):**
- "OAuth tasks slip 2x estimate across 3 projects" (pattern recognition)
- "E-DEMO architecture similar to E-AUTH in raise-gtm" (reuse recommendations)
- "5 teams blocked on same dependency" (systemic blocker detection)
- "Teams syncing tasks have 25% better estimation accuracy" (process insights)

**Process Validation (Dogfooding):**
- Full RaiSE epic lifecycle (design → plan → stories → close)
- TDD throughout (RED-GREEN-REFACTOR, no exceptions)
- Quality gates enforced (type annotations, >90% coverage, pyright strict)
- Retrospectives capture learnings → patterns

### SHOULD (Nice-to-Have)

- Progress indicators (show sync progress: "Syncing epic E9... 3/5 stories created")
- Sync history log (`.raise/rai/sync-history.jsonl` - timestamp, items synced, errors)
- Config validation (`rai backlog validate-config --provider jira`)
- Multiple JIRA projects support (sync to different JIRA projects per RaiSE epic)

---

## Out of Scope

### Deferred to Post-Demo

**Advanced Sync:**
- ❌ Task-level sync (JIRA subtasks) — epic + story sufficient for demo
- ❌ Conflict resolution UI
- ❌ Three-way merge implementation
- ❌ Field-level conflict detection

**Real-Time Sync:**
- ❌ Webhooks (push notifications from JIRA)
- ❌ Polling reconciliation (periodic sync daemon)
- ❌ Auto-sync on epic lifecycle events
- **Demo uses manual triggers:** `pull` and `push` commands

**Multi-Backend:**
- ❌ GitLab Issues/Epics adapter
- ❌ Odoo adapter
- ❌ Abstract BacklogProvider interface (define, but implement JIRA only)

**Advanced Features:**
- ❌ Custom field mapping
- ❌ Workflow status mapping (JIRA statuses ↔ RaiSE phases)
- ❌ Multi-project sync
- ❌ Team/org sync (shared memory)
- ❌ Attachment sync

**Production Hardening:**
- ❌ Retry policy configuration (use hardcoded exponential backoff)
- ❌ Monitoring/observability (metrics, dashboards)
- ❌ SLOs/SLIs
- ❌ Enterprise auth (SSO, SAML)

### Deferred to Post-Demo

- Commercial architecture decision (raise-pro package vs monorepo vs fork) → March 15-31
- Commercial pricing model → Post-customer validation
- Open-source retrofit decision → TBD, may never happen

---

## Done Criteria

### Per-Story Done Criteria (Standard)

- [ ] Code implemented with type annotations (pyright strict passes)
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Unit tests passing (>90% coverage on story code)
- [ ] Integration tests for CLI commands
- [ ] All quality checks pass (ruff, pyright, bandit)
- [ ] Story retrospective completed (/rai-story-review)

### Epic Done Criteria (E-DEMO Specific)

**Demo Success:**
- [ ] One epic syncs from local → JIRA without errors
- [ ] OAuth flow works (token acquisition + refresh)
- [ ] Entity properties track sync state correctly
- [ ] CLI provides clear feedback (progress, errors, dry-run output)
- [ ] Demo rehearsed successfully 3+ times (March 13 deadline)

**Process Success:**
- [ ] All 6 stories follow full lifecycle (design → review → close)
- [ ] TDD maintained throughout (100% compliance, no commits without tests)
- [ ] 5+ learnings captured in retrospectives → patterns added to memory

**Deliverables:**
- [ ] 3 ADRs created (OAuth provider, sync engine design, entity schema)
- [ ] BacklogProvider interface defined (for future raise-pro)
- [ ] Architecture documentation updated (module docs for mod-providers)

**Post-Demo Decision:**
- [ ] Commercial architecture chosen (raise-pro vs monorepo vs fork)
- [ ] Code migrated or archived (April 1 target)

---

## Dependencies

### Feature Dependencies (Sequential Critical Path)

```
S-DEMO.1 (Research synthesis + ADRs)
    ↓
S-DEMO.2 (OAuth authentication)
    ↓
S-DEMO.3 (JIRA client wrapper)
    ↓
S-DEMO.4 (Entity properties)
    ↓
S-DEMO.5 (Sync engine)
    ↓
S-DEMO.6 (Demo validation + retro)
```

**No parallelism possible:** Each story builds on previous. OAuth needed before JIRA client, JIRA client needed before entity properties, etc.

### External Dependencies

**Hard Deadlines:**
- **March 2, 2026:** JIRA rate limit changes enforce → Field filtering must be implemented (affects S-DEMO.3)
- **March 14, 2026:** Atlassian webinar demo → All stories must be complete

**Third-Party Services:**
- JIRA Cloud API (v3) - stable, well-documented
- OAuth 2.0 provider (Atlassian Identity) - standard flow

**Team Availability:**
- Emilio + Rai (full-time on this epic)
- No external dependencies on other teams

---

## Architecture References

### ADRs to Create (3)

| Decision | Document | Key Question |
|----------|----------|--------------|
| **OAuth Provider Choice** | ADR-023 | Authorization code + PKCE vs device flow vs service account? |
| **Sync Engine Architecture** | ADR-024 | Hub-and-spoke vs peer-to-peer? Field-level ownership strategy? |
| **Entity Schema Design** | ADR-025 | Entity properties vs custom fields vs external DB for sync metadata? |

### Research Foundation (6 Outputs, 184+ Sources)

| Research | Location | Key Recommendation |
|----------|----------|-------------------|
| Bidirectional Sync Patterns | `/work/research/bidirectional-sync/` | Local-first, hub-and-spoke, three-way merge, field-level ownership |
| JIRA Sync Best Practices | `/work/research/jira-bidirectional-sync/` | Webhook-first + polling backup, entity properties, field filtering (March 2 deadline) |
| GitLab Sync Patterns | `/work/research/gitlab-sync-patterns/` | (Deferred to V3, but informs abstraction design) |
| Offline-First Sync | `/work/research/offline-first-sync/` | Local-first delta sync, sequence IDs, exponential backoff |
| Sync Scope & Granularity | `/work/research/pm-sync-boundaries/` | Active items only, epic + story levels, core + agile fields |
| Sync Triggers & Events | `/work/research/sync-trigger-patterns/` | Three-tier hybrid (manual commands, lifecycle events, periodic reconciliation) |

**Total Research:** 184+ sources, ~6,500 lines of evidence-backed documentation

---

## Timeline

### Sprint Breakdown (42 Hours Total, 29 Working Hours)

| Phase | Time | Stories | Focus | Gate |
|-------|------|---------|-------|------|
| **Sat PM** | 16:00-23:00 (7h) | ✅ S-DEMO.1, S-DEMO.2 | ADRs ✅, OAuth impl | Auth working |
| **Sun AM** | 08:00-12:00 (4h) | S-DEMO.3 | JIRA client (bidirectional) | Read epic, write story, read status |
| **Sun PM** | 12:00-16:00 (4h) | S-DEMO.4 | Entity properties schema | Metadata working |
| **Sun Eve** | 16:00-06:00 (14h) | S-DEMO.5 | Sync engine (pull + push) | Bidirectional workflow works |
| **Mon AM** | 06:00-10:00 (4h) | S-DEMO.6 | Demo rehearsal + script | 3+ successful runs |
| **Mon 11am** | — | — | **DEMO to Zaira (Coppel)** | ✅ Success |

**Total:** 42 hours (Sat 16:00 → Mon 11:00), 29 working hours, 16 SP = ~0.55 SP/hour = **~10-12 SP/day**

### Velocity Assumptions

- **Estimated:** 16 SP / 42 hours = 10 SP/day (hyper-aggressive but achievable)
- **Historical:** User confirms "days where we do 20 SP" with RaiSE
- **This sprint:** 16 SP in 29 working hours = 0.55 SP/hour
- **Risk:** Timeline is BRUTAL (42 hours end-to-end) — any blocker could slip demo

**Velocity Factors:**
- ✅ **Positive:** Research complete (6 outputs, 184+ sources, zero unknowns), ADRs done (S-DEMO.1 ✅)
- ✅ **Positive:** Manual triggers accepted (no webhook complexity)
- ⚠️ **Risk:** Bidirectional sync added complexity (pull + push, not just push)
- ⚠️ **Risk:** New domain (OAuth, JIRA API learning curve)
- ✅ **Mitigation:** Epic+story only (task sync deferred), HITL at story boundaries, continuous progress tracking

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **JIRA API changes (March 2 deadline)** | Medium | High | Implement field filtering from day 1 (S-DEMO.3). Monitor Atlassian changelog. |
| **OAuth complexity delays progress** | Medium | Medium | S-DEMO.2 front-loaded (Week 1). Research complete (32 sources). Use `atlassian-python-api` library (proven). |
| **Timeline slip (28 days tight)** | High | High | Aggressive sizing (S/M bias). Daily progress checks. Combined HITL checkpoints (review 2 stories together if needed). |
| **Demo failure (live issues)** | Low | Critical | S-DEMO.6 rehearsal story (3+ successful runs). Dry-run mode for safety. Fallback: recorded demo if live fails. |
| **Scope creep (bidirectional temptation)** | Medium | Medium | Explicit out-of-scope list. HITL enforcement. "Demo MVP only" mantra. |
| **Rate limit exceeded during demo** | Low | High | Field filtering (S-DEMO.3). Dry-run before live demo. Test account with realistic data volume. |
| **Entity properties incompatibility** | Low | Medium | Test with JIRA Cloud (not Server/Data Center). Entity properties well-documented (Very High evidence). |

---

## Notes

### Why This Epic (Strategic Context)

**Business Context:**
- Humansys = Atlassian Gold Partner (all devs + Rai use JIRA/Confluence daily)
- Coppel (new client) uses JIRA — direct customer need
- March 14 webinar — 4 weeks of real usage = polished demo

**Technical Context:**
- RaiSE PRO = commercial offering, backlog sync is first premium feature
- Atlassian ecosystem integration = strategic partnership opportunity
- Dogfooding = validate RaiSE under real deadline pressure

**Meta-Learning Goal:**
Can RaiSE handle commercial feature development under timeline constraints while maintaining quality gates?

### What We're Testing (Dogfooding Validation)

**Process:**
- Epic lifecycle under 28-day deadline
- Story velocity when aggressive (2 SP/week vs 1.5 SP/week baseline)
- Quality gates vs speed trade-offs (can we stay strict on TDD?)

**Expected Learnings:**
- Where process adds value vs friction
- What adaptations work (design concurrency, combined HITL)
- Pain points for time-pressured teams
- Commercial feature workflow patterns

**Pattern Capture Target:** 5+ actionable learnings → memory patterns

### Velocity Assumption Details

**Calibration data (from `.claude/rai/calibration.md` if available):**
- Baseline velocity: ~1.5 SP/week (with full kata cycle)
- Aggressive velocity needed: 2 SP/week (1.33x multiplier)
- Justification: Research complete (no unknowns), clear architecture (ADRs upfront)

**Factors that might affect velocity:**
- ✅ Research reduces unknowns
- ✅ Clear architecture (3 ADRs in S-DEMO.1)
- ⚠️ New domain (OAuth, JIRA API learning curve)
- ⚠️ Timeline pressure (stress affects quality)

---

## Success Metrics

### Demo Metrics

- **Sync latency:** <5s for typical epic (5-10 stories)
- **Error rate:** 0% for happy path (no errors during rehearsed demo)
- **OAuth success:** 100% (no failed auth flows in 3+ rehearsals)
- **Demo rehearsal:** 3+ successful runs (March 13 deadline)

### Process Metrics

- **Story velocity:** 2 SP/week (aggressive, 1.33x baseline)
- **TDD compliance:** 100% (no commits without tests)
- **Quality gate pass rate:** 100% (pyright, ruff, bandit all pass before commit)
- **Retrospective patterns:** 5+ actionable learnings captured

### Strategic Metrics

- **Webinar attendance/engagement:** (measured by Atlassian, not in our control)
- **Customer validation:** Post-demo interest in RaiSE PRO (qualitative)
- **Dogfooding learnings:** 5+ patterns added to memory
- **Architecture decision made:** raise-pro package vs monorepo vs fork (by March 31)

---

## Related Documents

- **Branch Strategy:** `DEMO-STRATEGY.md` (demo branch, post-demo options)
- **Backlog:** `governance/backlog.md` §7 (demo & commercial strategy)
- **Initial Scope:** `scope.md` (root of demo branch, initial overview)
- **Research:** `/work/research/` (6 parallel research outputs, 184+ sources)
- **Pattern:** PAT-E-289 (demo branch strategy for commercial features)

---

*Epic tracking - update per story completion*
*Created: 2026-02-14*
*Epic Owner: Emilio + Rai*
*Type: Enabler Epic (infrastructure/commercial validation)*
*Status: Design Phase*
