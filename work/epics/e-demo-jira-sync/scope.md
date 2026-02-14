# Epic E-DEMO: JIRA Sync Enabler - Scope

> **Status:** IN PROGRESS
> **Type:** Enabler Epic (commercial feature validation + dogfooding)
> **Release:** N/A (Demo-scoped, not part of v2 release)
> **Branch:** `demo/atlassian-webinar`
> **Created:** 2026-02-14
> **Target:** 2026-03-14 (Atlassian Webinar Demo - 28 days)

---

## Objective

Build a JIRA bidirectional sync prototype using the full RaiSE process to:
1. **Demonstrate Atlassian ecosystem integration** at March 14 webinar
2. **Dogfood RaiSE under timeline pressure** (28-day deadline validates framework under real constraints)
3. **Validate commercial feature architecture** (foundation for future RaiSE PRO package)
4. **Capture learnings** from research-to-implementation to refine framework

**Value proposition:** Proves RaiSE can handle commercial feature development under deadline pressure while maintaining quality gates. Validates Atlassian partnership opportunity. Creates reusable architecture for future raise-pro package.

**Success criteria:**
- Demo successfully executes: one epic syncs from local → JIRA without errors
- Full RaiSE process followed: all stories complete design → review → close
- Learnings captured: 5+ patterns added to memory from dogfooding experience
- Architecture decision made: raise-pro package vs monorepo vs fork (post-demo)

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

## Features (14 SP estimated, 28 days, ~2 SP/week velocity)

| ID | Feature | Size | Dependencies | Description |
|----|---------|:----:|:------------:|-------------|
| **S-DEMO.1** | Research synthesis & architecture design | M (3 SP) | — | Consolidate 6 research outputs into unified architecture. Create 3 ADRs (OAuth, sync engine, entity schema). Define BacklogProvider interface. |
| **S-DEMO.2** | OAuth 2.0 authentication | M (3 SP) | S-DEMO.1 | Implement JIRA Cloud OAuth flow (authorization code + PKCE). Token storage, refresh logic. CLI-friendly device flow. |
| **S-DEMO.3** | JIRA client & API wrapper | S (2 SP) | S-DEMO.2 | Thin wrapper over `atlassian-python-api`. Rate limit handling (March 2 deadline). Field filtering for token economy. |
| **S-DEMO.4** | Entity properties & sync metadata | S (2 SP) | S-DEMO.3 | JIRA entity properties for sync state (last_sync_at, rai_epic_id, rai_story_id). Schema design, storage/retrieval. |
| **S-DEMO.5** | Sync engine (one-way: Local → JIRA) | M (3 SP) | S-DEMO.4 | Detect active epic, map to JIRA format, create epics/issues. Idempotent operations. Dry-run mode. Error handling. |
| **S-DEMO.6** | Demo validation & retrospective | XS (1 SP) | S-DEMO.5 | Rehearse demo scenario 3+ times. Capture learnings. Epic retrospective. Architecture decision (raise-pro vs monorepo vs fork). |

**Total:** 6 features, 14 SP estimated, 28 days (2 SP/week aggressive velocity)

**Critical path:** S-DEMO.1 → S-DEMO.2 → S-DEMO.3 → S-DEMO.4 → S-DEMO.5 → S-DEMO.6 (sequential, no parallelism)

---

## In Scope

### MUST (Demo Blockers)

**Core Functionality:**
- One-way sync: Local backlog (governance/backlog.md) → JIRA
- OAuth 2.0 authentication with JIRA Cloud (authorization code + PKCE)
- Entity properties for sync metadata tracking
- CLI command: `rai backlog sync --provider jira --direction push`
- Active epic detection (sync current epic from git branch context)
- Dry-run mode: `--dry-run` flag (preview changes without execution)
- Basic error handling with user-friendly messages

**Research-Backed Architecture:**
- Local-first sync (local is source of truth for Rai)
- Hub-and-spoke topology (memory graph as central hub)
- Field-level ownership (Rai owns workflow state, team owns collaboration fields)
- Exponential backoff retry (3-7 retries over 1-3 days)
- Rate limit compliance (March 2 JIRA API change deadline)

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

### Deferred to V3 / raise-pro

**Bidirectional Sync:**
- ❌ JIRA → Local sync (pull changes from JIRA)
- ❌ Conflict resolution UI
- ❌ Three-way merge implementation
- ❌ Field-level conflict detection

**Real-Time Sync:**
- ❌ Webhooks (push notifications from JIRA)
- ❌ Polling reconciliation (periodic sync daemon)
- ❌ Auto-sync on epic lifecycle events

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

### Weekly Breakdown (28 Days, 4 Weeks)

| Week | Dates | Stories | Focus | Gate |
|------|-------|---------|-------|------|
| **1** | Feb 14-20 | S-DEMO.1, S-DEMO.2 | Architecture + OAuth | Auth working, 3 ADRs created |
| **2** | Feb 21-27 | S-DEMO.3, S-DEMO.4 | JIRA client + Metadata | One epic data ready to sync |
| **3** | Feb 28-Mar 6 | S-DEMO.5 | Sync engine + Error handling | One epic syncs reliably |
| **4** | Mar 7-13 | S-DEMO.6 | Demo validation + Polish | Demo-ready, 3+ rehearsals |
| **Demo** | Mar 14 | — | Atlassian webinar | ✅ Success |
| **Decision** | Mar 15-31 | — | Architecture choice | Migrate/archive |

### Velocity Assumptions

- **Estimated:** 14 SP / 28 days = 0.5 SP/day = 2 SP/week (aggressive)
- **Baseline (no kata cycle):** 1.5 SP/week (from calibration data)
- **Multiplier:** 1.33x (aggressive velocity needed for 28-day deadline)

**Velocity Factors:**
- ✅ **Positive:** Research complete (6 outputs = no unknowns), clear architecture
- ⚠️ **Risk:** Timeline pressure (28 days tight), new domain (OAuth, JIRA API)
- ✅ **Mitigation:** Aggressive sizing (S/M bias), daily progress checks, HITL at story boundaries

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
