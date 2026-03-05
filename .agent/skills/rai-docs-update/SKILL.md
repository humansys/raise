---
description: 'Compare knowledge graph against module architecture docs and update
  drifted fields. Deterministic frontmatter comparison using existing rai graph commands,
  with inference for narrative sections. HITL before any writes.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: ''
  raise.frequency: per-story
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: ''
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: utility
name: rai-docs-update
---

# Docs Update

## Purpose

Close the coherence loop between code and architecture docs. Compare knowledge graph truth against module doc frontmatter, update drifted fields, and optionally refresh narrative sections.

## Mastery Levels (ShuHaRi)

- **Shu**: Present every diff, ask before every change
- **Ha**: Batch frontmatter changes with single HITL gate, narrative only for structural changes
- **Ri**: Autonomous frontmatter updates, HITL only for narrative

## Context

**When to use:** After stories that changed code structure, during `/rai-story-close`, after discovery refresh.

**When to skip:** Stories that only changed tests/docs/non-code. No graph available.

**Inputs:** Knowledge graph (`.raise/rai/memory/index.json`), module docs (`governance/architecture/modules/*.md`).

## Steps

### Step 1: Build Graph & Identify Affected Modules

```bash
rai graph build
```

Read `.raise/rai/personal/last-diff.json` for changed modules. If no diff or no affected_modules, check all modules.

<verification>
Module list identified for comparison.
</verification>

### Step 2: Compare Frontmatter Per Module

```bash
rai graph context mod-{name} --format json
```

Compare doc-declared vs code-truth:

| Doc field | Graph truth | Comparison |
|-----------|------------|------------|
| `depends_on` | `code_imports` | Sort both, compare sets |
| `depended_by` | Reverse lookup from other modules | Computed |
| `public_api` | `code_exports` | Sort both, compare sets |
| `components` | `code_components` | Direct number |

**Fields the skill MUST NOT touch:** `purpose`, `constraints`, `status`, `entry_points`, `name`, `type`.

<verification>
Drifted fields identified per module.
</verification>

### Step 3: HITL Gate — Apply Frontmatter

Present drift report:
```
### mod-memory
  depends_on: [config] → [config, schemas]  (added: schemas)
  components: 30 → 34
```

Ask: "Apply frontmatter updates to N modules? [y/n/selective]"

Apply changes to YAML frontmatter only — preserve all other content and field ordering.

<verification>
Frontmatter updates applied (or skipped by user).
</verification>

### Step 4: Narrative Review (if triggered)

**Trigger A (full review):** New/removed modules, major dependency changes (>2), significant API changes (>5).

**Trigger B (targeted scan):** For any frontmatter change, scan prose for stale hardcoded values (old counts, removed dependency names, removed API names). These are mechanical text fixes.

Present proposed changes as diff. HITL approval before writing.

<verification>
Narrative changes applied or no triggers found.
</verification>

### Step 5: Rebuild & Summarize

If any changes applied:
```bash
rai graph build
```

Present summary: modules checked, frontmatter updated, narrative updated, graph rebuilt.

<verification>
Graph reflects updated docs. Coherence loop closed.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Updated frontmatter | `governance/architecture/modules/*.md` |
| Narrative changes | `governance/architecture/modules/*.md` (with HITL) |
| Summary | Displayed |

## Quality Checklist

- [ ] Graph built fresh before comparison (not stale data)
- [ ] Only machine-owned fields updated (depends_on, depended_by, public_api, components)
- [ ] Human-owned fields preserved (purpose, constraints, status, entry_points)
- [ ] HITL gate before any writes — present diff first
- [ ] Graph rebuilt after changes to close coherence loop
- [ ] NEVER modify purpose or constraints without explicit human request

## References

- ADR-025: Incremental Coherence — Graph Diffing and AI-Driven Doc Regeneration
- Module docs: `governance/architecture/modules/*.md`
- Graph: `.raise/rai/memory/index.json`
- Graph context: `rai graph context mod-{name} --format json`
