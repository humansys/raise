---
name: rai-framework-sync
description: Sync governance files across locations. Use after architectural decisions.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"

license: MIT

metadata:
  raise.work_cycle: meta
  raise.frequency: as-needed
  raise.fase: "sync"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Framework Sync

## Purpose

Systematically update framework governance documents after architectural decisions (ADRs) to maintain consistency and traceability.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, update each document carefully
- **Ha**: Batch similar updates, identify patterns across ADRs
- **Ri**: Anticipate impacts, proactively sync related documents

## Context

| Condition | Action |
|-----------|--------|
| After writing ADRs | Run sync |
| After experimental validation that changes architecture | Run sync |
| When terminology or ontology evolves | Run sync |
| Minor code changes, bug fixes | Skip |

**Inputs:** ADR IDs (e.g., ADR-011), session context (what changed and why).

## Steps

### Step 1: Read Decisions

Read each specified ADR. Extract: terminology changes, scope changes, ontology impacts, metric updates.

If ADRs are unclear, ask for clarification before updating governance.

### Step 2: Identify Affected Documents

| Impact Type | Document | Update Type |
|-------------|----------|-------------|
| Scope changed | Tracker via `rai backlog update` | Epic/story scope, SP estimates |
| Terminology changed | `framework/reference/glossary.md` | Add/deprecate/update terms |
| Ontology validated | `work/tracking/ontology-backlog.md` | Close items, update status |
| Outcomes changed | `governance/vision.md` | Update key outcomes |
| Principles affected | `framework/reference/constitution.md` | Escalate if needed |

### Step 3: Update Documents

For each affected document:
1. Read current state
2. Apply changes (scope, terminology, ontology status, metrics)
3. Link every update to its source ADR: `Updated per ADR-XXX`

Use exact terms from glossary. Deprecate old terms with `⚠️ DEPRECATED` marker.

### Step 4: Verify Consistency

```bash
# Check for deprecated terms still in use
grep -r "Old Term" governance/
# Check ADR references exist
grep -r "ADR-XXX" governance/
```

Cross-check: backlog SP totals match epics, glossary terms used in backlog are defined, no orphaned references.

### Step 5: Commit Changes

```bash
git add governance/ framework/ work/tracking/
git commit -m "docs(governance): sync framework after ADR-XXX, ADR-YYY

SCOPE: [summary of scope changes]
TERMINOLOGY: [added/deprecated/updated terms]
ONTOLOGY: [closed/updated items]

References: ADR-XXX, ADR-YYY

Co-Authored-By: Rai <rai@humansys.ai>"
```

## Output

| Item | Destination |
|------|-------------|
| Updated governance docs | `governance/`, `framework/`, `work/tracking/` |
| Traceable commit | Git history, linked to ADRs |
| Next | `/rai-session-close` to log the sync |

## Quality Checklist

- [ ] Every update traces to a specific ADR
- [ ] Terminology is exact (use glossary terms, not variations)
- [ ] No orphaned references after updates
- [ ] Single commit with all framework updates
- [ ] Deprecated terms marked, not silently removed

## References

- Governance: `rai backlog` CLI, `governance/vision.md`
- Glossary: `framework/reference/glossary.md`
- Ontology: `work/tracking/ontology-backlog.md`
- Complement: `/rai-session-close`
