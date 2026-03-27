# S760.3: Workflow, Automation & Lifecycle Mapping

**Epic:** RAISE-760
**Story:** RAISE-762
**Date:** 2026-03-27
**Status:** Draft

---

## 1. Gemba: Current Lifecycle Integration

### RaiSE Hook System (exists)

RaiSE has a typed event system (`raise_cli.hooks.events`) with these events:

| Event | Trigger | Current Hook Action |
|-------|---------|-------------------|
| `work:lifecycle` | `rai signal emit-work` | `BacklogHook` → creates/transitions Jira issues |
| `work:start` | Story/Epic start | Available but no consumer beyond backlog |
| `work:close` | Story/Epic close | Available but no consumer beyond backlog |
| `session:start` | `rai session start` | Logging only |
| `session:close` | `rai session close` | Logging only |
| `before:session:close` | Before session close | Abortable gate |
| `graph:build` | `rai graph build` | Logging only |
| `pattern:added` | `rai pattern add` | Logging only |
| `discover:scan` | `rai discover scan` | Logging only |
| `release:publish` | `rai release publish` | Logging only |
| `before:release:publish` | Before release | Abortable gate |
| `mcp:call` | Any MCP tool call | Logging only |

### BacklogHook (the only cross-product integration today)

`BacklogHook` handles `work:lifecycle` events:
- `(story, start)` → creates Jira Story if missing, transitions to "In Progress"
- `(story, complete)` → transitions existing Story to "Done"
- `(epic, start)` → creates Jira Epic if missing, transitions to "In Progress"
- `(epic, complete)` → transitions existing Epic to "Done"

Uses `rai:{work_id}` label for issue resolution. Falls back to summary search.

### Jira Workflow (Software Simplified)

4 states, same for all issue types:
```
Backlog (11) → Selected for Development (21) → In Progress (31) → Done (41)
```

### What's Missing

1. **No Confluence integration from lifecycle events** — session close doesn't create archive page, epic close doesn't create retro page
2. **No Compass updates** — no scorecard or metric updates from lifecycle events
3. **No Jira Automation rules** — everything is push from CLI, nothing is triggered by Jira state changes
4. **No bidirectional sync** — Jira → RaiSE direction doesn't exist (only RaiSE → Jira)
5. **"Selected for Development" is unused** — skills go directly from Backlog to In Progress
6. **No Initiative workflow** — Initiatives don't have lifecycle events

---

## 2. Design Principles

1. **RaiSE CLI is the source of truth for developer actions.** Developers use skills (`/rai-story-start`, `/rai-story-close`), not Jira UI, to drive lifecycle.

2. **Jira Automation is the source of truth for cross-product cascades.** When a Jira issue changes state, Automation rules propagate to Confluence, Compass, notifications.

3. **Unidirectional by design: RaiSE → Jira → Cascade.** The CLI pushes to Jira. Jira Automation cascades to other products. We don't need Jira → RaiSE sync because developers ARE in the CLI.

4. **"Selected for Development" earns its place.** It represents "groomed and ready" — the bridge between product decision and engineering execution.

5. **Automation rules are specifications, not implementations.** This document defines WHAT rules do. Implementation is via Jira Automation UI (no API exists).

---

## 3. Workflow Per Issue Type

### Initiative Workflow

```
Backlog → In Progress → Done
```

No "Selected" — Initiatives are strategic. They're either not started, active, or achieved.

| Transition | Trigger | Notes |
|-----------|---------|-------|
| → In Progress | First child Epic starts | Manual or Automation rule |
| → Done | All child Epics done | Manual — requires retrospective |

### Epic Workflow

```
Backlog → Selected → In Progress → Done
```

| Transition | Trigger | RaiSE Skill | Automation Cascade |
|-----------|---------|-------------|-------------------|
| → Selected | Grooming/prioritization | Manual in Jira | — |
| → In Progress | `/rai-epic-start` | `rai signal emit-work epic start` → BacklogHook | Create Confluence scope page |
| → Done | `/rai-epic-close` | `rai signal emit-work epic complete` → BacklogHook | Create retro page in Confluence; update Compass scorecard |

### Story Workflow

```
Backlog → Selected → In Progress → Done
```

| Transition | Trigger | RaiSE Skill | Automation Cascade |
|-----------|---------|-------------|-------------------|
| → Selected | Sprint planning / grooming | Manual or `rai backlog transition` | — |
| → In Progress | `/rai-story-start` | `rai signal emit-work story start` → BacklogHook | — |
| → Done | `/rai-story-close` | `rai signal emit-work story complete` → BacklogHook | If all stories in Epic done → notify Epic owner |

### Bug Workflow

```
Backlog → Selected → In Progress → Done
```

Same as Story. `/rai-bugfix` lifecycle maps identically.

### Task Workflow

```
Backlog → In Progress → Done
```

No "Selected" — Tasks are technical work, usually not groomed separately.

---

## 4. RaiSE Skill Lifecycle → Jira Transition Mapping

### Full Lifecycle Chain

```
EPIC LIFECYCLE:
/rai-epic-start    → Epic: Backlog → In Progress
                     Creates scope page in Confluence (Automation)
/rai-epic-design   → (no transition — still In Progress)
                     Creates/updates design page in Confluence (Automation)
/rai-epic-plan     → (no transition — still In Progress)
/rai-epic-close    → Epic: In Progress → Done
                     Creates retro page in Confluence (Automation)
                     Updates Compass scorecard (Automation)

STORY LIFECYCLE:
/rai-story-start   → Story: Backlog/Selected → In Progress
                     Creates branch (Bitbucket auto-links via smart commits)
/rai-story-design  → (no transition)
/rai-story-plan    → (no transition)
/rai-story-implement → (no transition — already In Progress)
/rai-story-review  → (no transition)
/rai-story-close   → Story: In Progress → Done
                     Branch merged (PR in Bitbucket dev panel)

SESSION LIFECYCLE:
/rai-session-start → (no Jira transition)
                     Session journal created locally
/rai-session-close → (no Jira transition)
                     Session archived to Confluence (Automation via webhook)
```

### Transition Map (for jira.yaml)

```yaml
lifecycle_mapping:
  # Current (unchanged)
  story_start: 31      # In Progress
  story_close: 41      # Done
  epic_start: 31       # In Progress
  epic_close: 41       # Done
  selected: 21         # Selected for Development
  backlog: 11          # Backlog

  # New (proposed additions)
  bug_start: 31        # In Progress
  bug_close: 41        # Done
  initiative_start: 31 # In Progress
  initiative_close: 41 # Done
```

---

## 5. Jira Automation Rules

### Overview

Jira Automation operates on triggers → conditions → actions. No API for rule management — configured via Jira UI. Rules below are specifications for implementation.

### Rule 1: Epic Started → Create Confluence Scope Page

```
TRIGGER: Issue transitioned to "In Progress"
CONDITION: Issue type = Epic
ACTION:
  1. Create Confluence page in space RaiSE1
     Title: "{{issue.key}} — {{issue.summary}} — Scope"
     Parent: "Work > Epics" page
     Content: Template with issue fields
  2. Add comment to Jira issue with link to page
```

**Smart values used:** `{{issue.key}}`, `{{issue.summary}}`, `{{issue.description}}`

### Rule 2: Epic Closed → Create Retrospective Page

```
TRIGGER: Issue transitioned to "Done"
CONDITION: Issue type = Epic
ACTION:
  1. Create Confluence page in space RaiSE1
     Title: "{{issue.key}} — {{issue.summary}} — Retrospective"
     Parent: "Work > Epics" page
     Content: Retro template with story summary
  2. Add comment to Jira issue with link to page
  3. Send notification to team
```

### Rule 3: All Stories in Epic Done → Notify

```
TRIGGER: Issue transitioned to "Done"
CONDITION: Issue type = Story
CONDITION: All linked child issues of parent Epic are "Done"
ACTION:
  1. Add comment to parent Epic: "All stories complete — ready for /rai-epic-close"
  2. Send notification to Epic assignee
```

### Rule 4: Session Close → Archive to Confluence (via Webhook)

```
TRIGGER: Incoming webhook from rai session close
  URL: https://automation.atlassian.com/pro/hooks/{id}
  Payload: { session_id, summary, decisions, patterns, duration }
ACTION:
  1. Create Confluence page in space RaiSE1
     Title: "Session {{webhookData.session_id}} — {{webhookData.summary}}"
     Parent: "Sessions" page
     Content: Session archive template
```

**Note:** This requires RaiSE CLI to POST to the Jira Automation webhook URL on session close. New hook needed: `ConfluenceArchiveHook` or extend `BacklogHook`.

### Rule 5: Release Published → Create Release Notes Page

```
TRIGGER: Version released in Jira
CONDITION: Project = RAISE
ACTION:
  1. Lookup all issues with fixVersion = {{version.name}} and status = Done
  2. Create Confluence page in space RaiSE1
     Title: "Release {{version.name}}"
     Parent: "Releases" page
     Content: Release notes template with issue list
  3. Send notification
```

### Rule 6: New Epic → Auto-Link to Initiative (if parent set)

```
TRIGGER: Issue created
CONDITION: Issue type = Epic AND parent is set
ACTION:
  1. If parent issue type = Initiative:
     Add label "initiative:{{parent.summary | slugify}}" to Epic
  2. Add comment: "Linked to Initiative {{parent.key}}"
```

### Rule 7: Stale "In Progress" Alert

```
TRIGGER: Scheduled (weekly, Monday 9am)
CONDITION: Issue type in (Story, Bug) AND status = "In Progress" AND updated < -7d
ACTION:
  1. Add comment: "⚠️ This issue has been In Progress for >7 days without updates"
  2. Send notification to assignee
```

---

## 6. Cross-Product Event Flow

### Complete Flow: Story Lifecycle

```
Developer                RaiSE CLI              Jira                  Confluence         Bitbucket
────────                ─────────              ────                  ──────────         ─────────
/rai-story-start ──→ rai signal emit-work ──→ Create/transition ──→                  ──→ Branch created
                     story S760.1 start        Story → In Progress                       (smart commit
                                                                                          links to issue)
                         │
/rai-story-implement     │ (commits with RAISE-761 in msg)                              ──→ Commits appear
                         │                                                                   in dev panel
                         │
/rai-story-close ───→ rai signal emit-work ──→ Transition          ──→                 ──→ PR merged
                     story S760.1 complete      Story → Done
                                                    │
                                              Automation Rule 3:
                                              "All stories done?"
                                                    │ yes
                                                    ▼
                                              Comment on Epic:
                                              "Ready for close"
```

### Complete Flow: Epic Lifecycle

```
Developer                RaiSE CLI              Jira                  Confluence         Compass
────────                ─────────              ────                  ──────────         ───────
/rai-epic-start ────→ rai signal emit-work ──→ Transition          ──→ Rule 1:
                     epic E760 start            Epic → In Progress     Create scope
                                                                       page
                         │
[stories execute]        │
                         │
/rai-epic-close ────→ rai signal emit-work ──→ Transition          ──→ Rule 2:        ──→ Update
                     epic E760 complete         Epic → Done             Create retro       scorecard
                                                                        page
```

### Complete Flow: Session Lifecycle

```
Developer                RaiSE CLI              Jira                  Confluence
────────                ─────────              ────                  ──────────
/rai-session-start ──→ rai session start        (no Jira action)
                         │
[work happens]           │ journal entries
                         │
/rai-session-close ──→ rai session close ──→ Webhook to            ──→ Rule 4:
                                              Automation               Create session
                                                                       archive page
```

---

## 7. Bidirectional Sync Decision

### Current: Unidirectional (RaiSE → Jira)

The CLI pushes state to Jira via BacklogHook. Jira is a projection of RaiSE state, not an input.

### Proposed: Stay Unidirectional + Automation Cascades

**Why not add Jira → RaiSE?**

1. **Developers live in the CLI.** They don't transition Jira issues manually. `/rai-story-start` is the primary interface.
2. **Jira webhook → CLI is complex.** Would require a running daemon or polling mechanism. rai-agent could do this, but it's a separate product.
3. **Automation cascades handle the "other direction."** When Jira changes (via BacklogHook), Automation rules cascade to Confluence/Compass. No need for the signal to come back to CLI.

**Exception: rai-agent.** For teams running rai-agent as a daemon, Jira webhooks → rai-agent → CLI actions IS a valid future path. This is NOT in scope for RAISE-760 but should be noted as future capability.

### Sync Model

```
RaiSE CLI ──push──→ Jira ──automation──→ Confluence
                         ──automation──→ Compass
                         ──automation──→ Notifications

              ╳ No pull from Jira → CLI (by design)

Future: Jira ──webhook──→ rai-agent ──→ CLI actions
```

---

## 8. New Hooks Needed (Gap Analysis)

| Hook | Event | Action | Priority |
|------|-------|--------|----------|
| `ConfluenceArchiveHook` | `session:close` | POST session data to Jira Automation webhook URL | P1 — enables Rule 4 |
| `CompassMetricHook` | `release:publish` | POST deployment event to Compass metric API (via Forge) | P2 — enables DORA |
| `GraphSyncHook` | `graph:build` | POST graph to raise-server (already exists as CLI command, not as hook) | P2 — enables auto-sync |
| Extend `BacklogHook` | `work:lifecycle` | Include phase info in Jira comment (design, plan, implement, review) | P1 — better visibility |

---

## 9. Automation Rule Summary

| # | Rule | Trigger | Products | Priority |
|---|------|---------|----------|----------|
| 1 | Epic Started → Scope Page | Epic → In Progress | Jira → Confluence | P1 |
| 2 | Epic Closed → Retro Page | Epic → Done | Jira → Confluence | P1 |
| 3 | All Stories Done → Notify | Story → Done (all in Epic) | Jira → Notification | P1 |
| 4 | Session Close → Archive | Incoming webhook | Webhook → Confluence | P2 |
| 5 | Release → Notes Page | Version released | Jira → Confluence | P2 |
| 6 | New Epic → Auto-Link Initiative | Epic created with parent | Jira → Jira | P1 |
| 7 | Stale In Progress Alert | Scheduled (weekly) | Jira → Notification | P3 |

**P1 rules (4)** deliver the core cross-product automation.
**P2 rules (2)** add session and release lifecycle integration.
**P3 rules (1)** add operational hygiene.

---

## 10. Impact on jira.yaml

### Proposed Additions

```yaml
# ─── Automation (Jira Automation webhook URLs) ────────────────────────
automation:
  session_archive_webhook: ""  # Fill after creating Automation rule
  # Future: compass_metric_webhook, etc.

# ─── Lifecycle Mapping (additions) ────────────────────────────────────
workflow:
  lifecycle_mapping:
    # Existing
    story_start: 31
    story_close: 41
    epic_start: 31
    epic_close: 41
    selected: 21
    backlog: 11
    # New
    bug_start: 31
    bug_close: 41
    initiative_start: 31
    initiative_close: 41
```

---

## References

- `raise_cli.hooks.events` — typed event definitions (13 event types)
- `raise_cli.hooks.builtin.backlog` — BacklogHook implementation
- `.raise/jira.yaml` — current workflow and lifecycle mapping
- ADR-039 — Hook architecture (typed events, entry points, error isolation)
- R1-RAISE-760 — Jira Automation capabilities (no API, webhook triggers, smart values)
- R4-RAISE-760 — Forge async patterns (relevant for Compass metric forwarding)
