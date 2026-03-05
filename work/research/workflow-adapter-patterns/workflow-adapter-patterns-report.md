# Research Report: Workflow Adapter Patterns for Multi-Tool Work Item Management

**Date:** 2026-03-03
**Depth:** Standard
**Decision context:** E347 Backlog Automation — ADR-043 revision
**Evidence catalog:** `sources/evidence-catalog.md` (9 sources, 3 Very High, 3 High, 3 Medium)

## Research Questions

1. What is the established pattern for modeling a canonical work item model that translates to multiple PM backends?
2. How do existing tools handle workflow state mapping between systems with different states?
3. Is a canonical data model the right approach, or is it an anti-pattern?
4. How should operations that one backend supports and another doesn't be handled?

## Key Findings

### Finding 1: The Two-Layer State Model is the Industry Standard

**Confidence: HIGH** (triangulated across 4 independent sources: S1, S6, S7, S4)

Every production system that maps workflow states between tools uses a **two-layer model**:

| Layer | Azure DevOps (S1) | Jira Align (S6) | Plane.so (S7) | Nango (S4) |
|-------|-------------------|------------------|---------------|------------|
| **Abstract/canonical** | 4 State Categories (Proposed, InProgress, Resolved, Complete) | Align States (system-defined, non-customizable) | Plane workflow states | Unified model (your data model) |
| **Concrete/backend** | Custom workflow states per work item type | Jira Software statuses | GitHub states (open/closed) | Provider-specific implementations |
| **Mapping** | Each custom state → exactly one category | Configurable paths (5 directions) | User-configurable per project | Per-provider adapter file |

**The canonical layer is small and stable.** Azure DevOps has had 4 categories for 15+ years. Tools operate on the canonical layer; backends implement the concrete layer.

### Finding 2: Use YOUR Domain Model, Not a Generic One

**Confidence: HIGH** (triangulated: S3, S5, S9)

Nango (S3) is explicit: "Use your existing, internal data model as the unified schema." The canonical model should be what YOUR system needs, not an attempt to capture every possible PM tool's concepts.

The anti-canonical-model argument (S5, S9) warns against bloated enterprise-wide models with many optional fields. **However**, this applies to large-scale integration hubs, not our case (2 adapters with narrow scope). Our model is domain-specific (RaiSE's work items), not enterprise-wide.

**Contrary evidence acknowledged:** Harsanyi (S5) argues canonical models shift coupling. In our case, this is acceptable because the canonical model IS our domain model — we're not creating an intermediary for someone else's benefit. RaiSE defines what a "story" and "epic" mean; adapters translate.

### Finding 3: State Categories Should Be Fixed; Workflow States Customizable

**Confidence: HIGH** (triangulated: S1, S6, S3)

Azure DevOps (S1) enforces this strictly:
- **Categories** (Proposed, InProgress, Resolved, Complete) — fixed, cannot be changed or renamed
- **Workflow states** (New, Active, Resolved, Closed, etc.) — customizable per work item type, but each MUST map to exactly one category

This solves the reverse-mapping problem from our arch review (C1): dashboards, boards, burndowns, and queries operate on **categories**, not states. Session-start should operate on categories too.

### Finding 4: Graceful Degradation for Missing Operations

**Confidence: HIGH** (triangulated: S3, S4, S7)

Nango (S3): "Some properties won't be supported by all external APIs...better to leave as null than to map some random field."

Nango (S4): Three strategies for provider gaps: (1) extended models with provider-specific fields, (2) custom fields, (3) raw data attachment.

This validates our FileAdapter's current approach: `link_to_parent` and `link_issues` are no-ops, `add_comment` returns empty. The key is: make it **explicit** (return type indicates "not supported") rather than silent.

### Finding 5: The Anti-Corruption Layer Pattern is the Correct Architecture

**Confidence: VERY HIGH** (triangulated: S2, S3, S5, S9 — all agree on ACL even when they disagree on canonical models)

The ACL pattern (S2, Eric Evans DDD):
- Domain model (RaiSE's work items) is protected from external concepts
- Adapter translates at the boundary
- Each side uses its own model; the ACL contains all translation logic

Even the anti-canonical-model authors (S5, S9) recommend ACL. The disagreement is about WHETHER to have a shared model — in our case it's our own domain model, so the objection doesn't apply.

## Synthesis: The Recommended Architecture

Based on the evidence, the architecture for RaiSE should be:

### 1. RaiSE Work Item Model (canonical, small, stable)

```
Issue Types: epic, story, task, subtask, bug, spike, improvement
State Categories: proposed, active, resolved, done, removed
  - proposed: not yet started (equivalent to Azure's "Proposed")
  - active: work is happening (equivalent to Azure's "In Progress")
  - resolved: solution implemented, not verified (optional, maps to "active" if backend lacks it)
  - done: finished
  - removed: hidden from views
```

Each issue type has a workflow defining which **state categories** apply and their valid transitions. State categories are fixed (like Azure DevOps). This is what skills, session-start, and all consumers see.

### 2. Adapter State Mapping (per-backend, configurable)

Each adapter maps RaiSE state categories to its backend's states/transitions:

```yaml
# .raise/jira.yaml (already exists, extend)
workflow:
  state_mapping:
    proposed: 11    # Jira: Backlog
    active: 31      # Jira: In Progress
    done: 41        # Jira: Done
```

```yaml
# FileAdapter (built-in, no config needed)
# proposed → "📋 Backlog"
# active → "🚀 In Progress"
# done → "✅ Complete"
```

### 3. ACL Boundary

The adapter IS the anti-corruption layer. `transition_issue(key, "active")` receives a RaiSE state category. The adapter translates to Jira transition ID 31. The protocol never exposes Jira concepts.

### 4. Missing Operations

FileAdapter explicitly signals unsupported operations (return type or warning) rather than silent no-ops. The protocol contract documents which operations are required vs optional.

## Implications for E347

1. **ADR-043 should be revised.** Replace "workflow phases" with "state categories" based on the Azure DevOps model. Remove skill binding (speculative). Remove workflow.yaml (unnecessary file — state categories are fixed in code, mapping lives in adapter config).

2. **No new config file needed.** State categories are code constants (like Azure DevOps). Adapter mapping extends existing `jira.yaml`. `manifest.yaml` gets `backlog.adapter_default` only.

3. **Session-start operates on state categories**, not on backend-specific states. No reverse mapping needed — `get_issue()` returns `IssueDetail` with a `status` field that's already in RaiSE vocabulary (the adapter translates on read too, not just on write).

4. **FileAdapter returns state categories natively** since it controls its own format. McpJiraAdapter translates Jira statuses to RaiSE categories on read and RaiSE categories to Jira transitions on write.

## Risks

- **State category granularity:** 5 categories may be too coarse for teams that want 7+ visible states in their boards. Mitigation: teams can define custom states that map to categories (Azure DevOps model), but this is a v2.3+ concern, not E347.
- **Jira status → category ambiguity:** If a Jira project has 8 statuses, multiple may map to "active". Mitigation: the mapping is user-configured in jira.yaml and read-direction mapping is explicit (each Jira status maps to exactly one category).

## References

See `sources/evidence-catalog.md` for full source list.

Key sources:
- [Azure DevOps State Categories](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories)
- [Anti-Corruption Layer Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Nango Unified API Best Practices](https://nango.dev/blog/best-practices-build-unified-api)
- [Canonical Data Model as Anti-Pattern](https://teivah.medium.com/why-is-a-canonical-data-model-an-anti-pattern-441b5c4cbff8)
- [Jira Align State Mapping](https://confluence.atlassian.com/jakb/mapping-states-process-steps-and-statuses-between-jira-align-and-jira-software-1387599540.html)
- [Plane.so GitHub Sync](https://docs.plane.so/integrations/github)
