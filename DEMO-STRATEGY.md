# Demo Branch Strategy — Atlassian Webinar

> **Branch:** `demo/atlassian-webinar`
> **Target:** March 14, 2026 Atlassian webinar
> **Status:** Active spike (timeboxed prototype)
> **Merge Policy:** ⚠️ **NEVER MERGES TO v2** ⚠️

---

## Purpose

This branch contains JIRA sync functionality for the March 14 Atlassian partnership webinar demo. This code is **commercial-only** and will not be distributed in the open-source version of raise-cli.

---

## Commercial Strategy

### Current Decision (2026-02-14)

**JIRA/backlog sync is commercial-only:**
- Not distributed in open-source raise-cli (PyPI package)
- Part of future RaiSE PRO offering
- May be retrofitted to open version later (decision deferred)

### Why Demo Branch?

**Timeline pressure:** 28 days to demo (March 14, 2026)
**Scope:** V3 feature (E21: Platform Integration) being prototyped early
**Risk:** Don't want experimental code in v2 open-source distribution
**Strategy:** Spike to learn, then decide commercial architecture post-demo

---

## What's In This Branch

### Demo MVP Scope

**Must Have:**
1. Manual CLI command: `rai backlog sync --provider jira --direction push`
2. One-way sync: Local (governance/backlog.md) → JIRA
3. OAuth authentication (JIRA Cloud)
4. Entity properties for sync metadata
5. Basic error handling

**Demo Scenario:**
- Show RaiSE tracking epics/stories locally
- Run `rai backlog sync --provider jira`
- Show epics/issues created in JIRA
- Demonstrate Atlassian ecosystem integration

**Explicitly Out of Scope:**
- Bidirectional sync (V3)
- Conflict resolution (V3)
- Webhooks (V3)
- GitLab/Odoo adapters (V3)
- Production hardening (V3)

---

## Process & Quality

**This is a spike, not production code:**
- ❌ No /rai-epic-start (not tracked as epic)
- ❌ No scope commits
- ❌ No story lifecycle
- ❌ Quality gates relaxed (speed over perfection)
- ✅ Research-informed (6 parallel research outputs available)
- ✅ Functional for demo
- ✅ Learning artifact for future commercial version

**Why:** 28-day deadline requires pragmatism. Build to learn and demo, not to ship.

---

## Post-Demo Decision (March 15+)

After demo, choose commercial architecture:

### Option 1: Separate `raise-pro` Package (Recommended)

```
raise-cli (open, PyPI)
  └── Core functionality
  └── Extension points (BacklogProvider interface)

raise-pro (private, commercial)
  └── Depends on raise-cli
  └── JIRA/GitLab/Odoo adapters
  └── pip install raise-pro
```

**Pros:**
- Clean separation
- Easy to retrofit to open later (just move code)
- Standard commercial open-source model

**Retrofit path:** Move adapters from raise-pro → raise-cli, no architecture change.

---

### Option 2: Monorepo with Private Modules

```
raise-commons/
  ├── src/rai_cli/     (distributed)
  └── src/rai_pro/     (not distributed, build-time filtered)
```

**Pros:** Single repo, easier development
**Cons:** Build complexity, accidental leaks

---

### Option 3: Private Fork

```
raise-commons (open)
raise-commercial (private fork)
```

**Pros:** Total separation
**Cons:** Sync drift, merge hell

---

## Research Foundation

Six parallel research streams completed (2026-02-14):

1. **Bidirectional Sync Patterns** — 1,464 lines, 28 sources, HIGH confidence
2. **JIRA Sync Best Practices** — 1,951 lines, 32 sources, HIGH confidence
3. **GitLab Sync Patterns** — 28 sources, MEDIUM-HIGH confidence
4. **Offline-First Sync Architecture** — 32 sources, HIGH confidence
5. **Sync Scope & Granularity** — 34 sources, HIGH confidence
6. **Sync Triggers & Event Models** — 30+ sources, HIGH confidence

**Total:** 184+ sources, ~6,500 lines of evidence-backed documentation

**Location:** `/work/research/{topic}/`

**Key Recommendations:**
- Local-first, hub-and-spoke architecture
- Three-way merge for conflict resolution
- Webhook-first + polling backup
- Active items only (epic + story levels)
- Field-level ownership (Rai = workflow, Team = collaboration)

---

## Timeline

| Date | Milestone |
|------|-----------|
| **Feb 14-20** | OAuth setup, sync command skeleton |
| **Feb 21-27** | Entity properties, one epic syncs |
| **Feb 28-Mar 6** | Testing, error handling, dry-run mode |
| **Mar 7-13** | Demo validation, polish, rehearsal |
| **Mar 14** | 🎯 **Atlassian webinar demo** |
| **Mar 15-31** | Decide commercial strategy |
| **Apr 1+** | Start raise-pro (if yes) or archive branch |

---

## Critical Constraints

### March 2, 2026: JIRA Rate Limit Change
New rate limiting enforces March 2. Must implement field filtering from day 1.

### Demo Scope Creep
Resist urge to add features beyond MVP. Demo needs to work, not be perfect.

---

## Branch Lifecycle

**Active:** Now → March 14 (demo)
**Decision:** March 15-31 (commercial strategy)
**Archive or Migrate:** April 1+

**If archived:** Research + learnings preserved in `/work/research/`
**If migrated:** Code moves to `raise-pro` package, branch deleted

---

## Who This Affects

**Not affected:**
- ✅ F&F users (raise-cli v2.0.0)
- ✅ Open-source contributors
- ✅ Public PyPI package

**Affected:**
- Demo attendees (see JIRA sync in action)
- Future RaiSE PRO customers (if we build it)
- Atlassian partnership (validation of integration)

---

## Questions & Decisions

### Open Questions (as of 2026-02-14)

1. **Commercial pricing model?** (TBD post-demo)
2. **Standalone product or upsell?** (TBD post-demo)
3. **Open-source retrofit timeline?** (Deferred, may never happen)
4. **Multi-tenant vs self-hosted?** (V3 architecture decision)

### Decisions Made

- ✅ Demo branch, no merge to v2
- ✅ Commercial-only for now
- ✅ Spike process (no formal tracking)
- ✅ Research-informed architecture
- ✅ Post-demo decision on raise-pro package

---

## Related Documents

- **Backlog:** `governance/backlog.md` §7 "Demo & Commercial Strategy"
- **Research:** `/work/research/{bidirectional-sync,jira-sync,gitlab-sync,offline-first,pm-sync-boundaries,sync-triggers}/`
- **Parking Lot:** `dev/parking-lot.md` → "E-NEXT: Backlog Abstraction Layer (RaiSE PRO)"
- **V3 Epics:** E19-E22 (potentially commercial tier)

---

## Contact

**Questions about this branch:** Ask Emilio
**Demo coordination:** Atlassian partnership team
**Commercial strategy:** Emilio + Humansys leadership

---

*Created: 2026-02-14*
*Status: Active*
*Next Review: 2026-03-15 (post-demo)*
