# Self-Test: Contract 1 — Epic Brief Artifact

> Validates that the brief.md template from Step 3.5 is consumable by epic-design.

## Sample Artifact

Below is a hypothetical brief.md for a fictional epic "RAISE-300".

---

```markdown
---
epic_id: "RAISE-300"
title: "Backlog Abstraction Layer"
status: "draft"
created: "2026-03-01"
---

# Epic Brief: Backlog Abstraction Layer

## Hypothesis
For development teams using RaiSE who manage work in external tools (Jira, GitLab, Azure DevOps),
the Backlog Abstraction Layer is a platform-agnostic interface
that enables rai backlog commands to work against any backend.
Unlike the current local-only approach, our solution connects to external project management tools without vendor lock-in.

## Success Metrics
- **Leading:** First adapter (Jira) passes read/write integration tests within S1
- **Lagging:** 3+ adapters available, zero vendor-specific code in core commands

## Appetite
M — 5-7 stories (Port/Adapter pattern, 3 adapters, CLI commands, sync protocol)

## Scope Boundaries
### In (MUST)
- BacklogProvider interface (Protocol)
- JiraAdapter with full CRUD
- LocalAdapter (current work/epics/ files)
- rai backlog list/create/update commands

### In (SHOULD)
- GitLabAdapter
- Bidirectional sync

### No-Gos
- Real-time sync (polling or webhooks) — too complex for MVP, batch sync sufficient
- UI dashboard — CLI only

### Rabbit Holes
- Trying to abstract every Jira field (start with summary, status, priority, assignee)
- Building a universal query language (use provider-native queries with thin wrapper)
```

---

## Consumption Verification

### epic-design reads Hypothesis → frames objective
- **Consumes:** "For development teams... Backlog Abstraction Layer... platform-agnostic interface"
- **Result:** Objective = "Enable platform-agnostic backlog management via Port/Adapter pattern". ✅

### epic-design reads Appetite → constrains feature count
- **Consumes:** "M — 5-7 stories"
- **Result:** Design produces 5-7 stories, not 3 or 12. ✅

### epic-design reads No-Gos → Out of Scope
- **Consumes:** "Real-time sync", "UI dashboard"
- **Result:** These appear verbatim in scope.md Out of Scope section. ✅

### epic-design reads Rabbit Holes → Risks
- **Consumes:** "abstracting every Jira field", "universal query language"
- **Result:** These become risk rows with mitigations. ✅

## Verdict

Contract 1 artifact is **consumable** by epic-design. All four consumption points verified:
1. Hypothesis → Objective ✅
2. Appetite → Feature count constraint ✅
3. No-Gos → Out of Scope ✅
4. Rabbit Holes → Risks ✅
