---
id: ADR-043
title: "Work Item Ontology — Structure Fixed, Content Configurable"
status: "accepted"
date: "2026-03-03"
epic: "E347"
decision_makers: ["Emilio"]
supersedes: null
research: "work/research/workflow-adapter-patterns/workflow-adapter-patterns-report.md"
---

# ADR-043: Work Item Ontology

## Context

RaiSE needs to manage work items (epics, stories, tasks) across multiple backends (Jira, local files, future: GitHub Issues, Linear). Each backend has its own status model, transitions, and issue types.

The original design proposed "workflow phases" mapping to adapter statuses, with hardcoded state categories (like Azure DevOps's Proposed/InProgress/Resolved/Complete). Architecture review and research (9 sources, see evidence catalog) revealed:

1. Azure DevOps can hardcode categories because it IS the tool. RaiSE is a LAYER on top of tools — forcing a canonical vocabulary limits teams that already have their own workflows.
2. The Anti-Corruption Layer (DDD, Eric Evans) is the correct pattern: domain model protected by adapter boundary.
3. Nango (unified API platform): "Use YOUR internal data model as the unified schema."
4. Counter-argument (Harsanyi, InfoQ): canonical models become bloated and shift coupling. Mitigated by keeping our scope narrow and making content configurable.

## Decision

**RaiSE defines the STRUCTURE of work items (ontology). Teams define the CONTENT (states, transitions, types). The adapter translates between team vocabulary and backend operations.**

### What is Fixed (Structure/Grammar)

- An **issue** has a **type** (e.g., epic, story, bug)
- A **type** has a **workflow**
- A **workflow** has **states** with an ordering
- Each state has a **terminal** flag (is the work done?)
- The **adapter** translates states to/from backend-specific representations

### What is Configurable (Content/Vocabulary)

- Which types exist and what they're called
- Which states each type's workflow has
- How those states map to the backend (Jira transition IDs, file emojis, etc.)
- Which states are terminal

### Default Configuration

RaiSE ships a sensible default that works out-of-the-box with zero config:

```yaml
# .raise/workflows.yaml — ships with rai init, teams can override
workflows:
  defaults:
    states: [backlog, in_progress, done]
    terminal: [done]

  # Per-type overrides (optional)
  story:
    states: [backlog, in_progress, in_review, done]
    terminal: [done]
  epic:
    states: [backlog, in_progress, done]
    terminal: [done]
```

A team like Kurigage can define their own:

```yaml
workflows:
  story:
    states: [backlog, analysis, development, qa, uat, done]
    terminal: [done]
  bug:
    states: [triage, confirmed, fixing, verified, closed]
    terminal: [closed]
```

### Adapter Mapping

Each adapter config maps team states to backend operations:

```yaml
# .raise/jira.yaml (extends existing file)
workflow:
  state_mapping:
    backlog: 11        # Jira transition ID
    in_progress: 31
    in_review: 31      # multiple states can map to same Jira status
    done: 41
```

FileAdapter maps states to display strings (built-in, no config):
```
backlog → "📋 Backlog"
in_progress → "🚀 In Progress"
done → "✅ Complete"
```

### Interaction Model

```
Skill: "rai backlog transition S347.1 in_progress"
        ↓
CLI: validates state exists in workflow config
        ↓
Adapter: translates "in_progress" → Jira transition ID 31
        ↓
Backend: executes transition

Read path (reverse):
Backend: returns Jira status "In Progress"
        ↓
Adapter: translates to team state "in_progress" (via reverse mapping in jira.yaml)
        ↓
Consumer: sees "in_progress" — RaiSE vocabulary, not Jira's
```

### What RaiSE Needs to Function

Minimal requirements from the workflow config:
- **State name** — to display and transition
- **Terminal flag** — to know if work is done (for burndowns, progress, session-start)
- **State ordering** — to validate forward/backward transitions

Skills don't need to understand the states. A skill like `rai-story-close` transitions to the terminal state for that type. It doesn't hardcode "done" — it reads the workflow config.

## Consequences

### Positive
- Teams define their own workflow vocabulary — RaiSE doesn't force its model
- Adapters are pure translators (ACL pattern)
- No reverse-mapping ambiguity — adapter config is explicit in both directions
- Default works out-of-the-box for teams that don't need customization
- Extensible to any future backend without changing the ontology

### Negative
- One config file (workflows.yaml) to manage
- Skills need to read workflow config instead of hardcoding state names
- Teams must maintain jira.yaml mapping when they customize workflows

### Mitigations
- Default ships with `rai init`, zero config for standard use
- `rai adapter check` validates mapping completeness
- Skills reference states by role ("terminal state") not by name

## Alternatives Considered

1. **Hardcode state categories (Azure DevOps model)** — Works for Azure because they ARE the tool. RaiSE is a layer; hardcoding limits teams. Rejected.
2. **No workflow abstraction (pass-through to adapter)** — Skills would need to know Jira concepts. Violates ACL. Rejected.
3. **Full workflow engine (BPMN-like)** — Over-engineering for current needs. YAML config sufficient. Rejected.
4. **Skill binding per state** — Speculative, no consumer in E347. Deferred to parking lot.
