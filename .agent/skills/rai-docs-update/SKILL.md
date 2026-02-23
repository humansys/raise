---
name: rai-docs-update
description: >
  Compare knowledge graph against module architecture docs and update
  drifted fields. Deterministic frontmatter comparison using existing
  rai graph commands, with inference for narrative sections. HITL
  before any writes.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: per-story
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
---

# Docs Update

## Purpose

Close the coherence loop between code and architecture documentation. The knowledge graph (built from code analysis, discovery, and governance) contains ground truth about module dependencies, exports, and component counts. This skill compares that truth against what module docs currently declare in their YAML frontmatter, and updates drifted fields.

Two layers (ADR-025):
1. **Frontmatter comparison** — mechanical field-by-field diff, no inference needed
2. **Narrative review** — inference-based update of prose sections when structural changes are detected

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, present every diff, ask before every change
- **Ha**: Batch frontmatter changes with single HITL gate, focus narrative review on structural changes only
- **Ri**: Autonomous frontmatter updates, HITL only for narrative

## Context

**When to use:**
- After completing a story that changed code structure (new modules, changed dependencies, new exports)
- During `/rai-story-close` as a coherence check (S16.4 integration)
- Manually when architecture docs feel stale
- After running `rai discover scan` or a full discovery refresh

**When to skip:**
- Stories that only changed tests, docs, or non-code files
- No graph available (`rai graph build` hasn't been run)

**Inputs required:**
- Knowledge graph: `.raise/rai/memory/index.json` (from `rai graph build`)
- Module docs: `governance/architecture/modules/*.md`

**Output:**
- Updated module doc frontmatter (machine-owned fields only)
- Optionally updated narrative sections (with HITL approval)

## Steps

### Step 1: Build Fresh Graph

Build the unified knowledge graph to get current code truth and a diff against the previous build:

```bash
rai graph build
```

This produces:
- `.raise/rai/memory/index.json` — the full graph
- `.raise/rai/personal/last-diff.json` — what changed since last build

**If build fails:** Check that the project has discoverable source code and governance files. Run `rai graph build -v` for diagnostics.

### Step 2: Identify Affected Modules

Read the diff to determine which modules need checking:

```bash
cat .raise/rai/personal/last-diff.json
```

**Decision tree:**
- **Diff exists with `affected_modules`** → Focus on those modules
- **Diff exists with no affected modules but node changes** → Check all modules (changes may affect dependencies)
- **Diff shows "no changes"** → Still check all modules (docs may have drifted from prior sessions)
- **No diff file** → Check all modules

To get the list of all modules:

```bash
ls governance/architecture/modules/*.md
```

### Step 3: Compare Frontmatter Per Module

For each module to check, gather graph truth and current doc state:

```bash
rai graph context mod-{name} --format json
```

This returns a JSON object with:
- `module.metadata.depends_on` — what the **doc declares** as dependencies
- `module.metadata.depended_by` — what the **doc declares** as dependents
- `module.metadata.public_api` — what the **doc declares** as public API
- `module.metadata.components` — what the **doc declares** as component count
- `module.metadata.code_imports` — what **code analysis** found as actual imports
- `module.metadata.code_exports` — what **code analysis** found as actual exports
- `module.metadata.code_components` — what **code analysis** found as component count

Then read the current module doc:

```bash
# Read the frontmatter section of the module doc
```
Read the file `governance/architecture/modules/{name}.md` using the Read tool.

**Compare these field pairs:**

| Doc Field (declared) | Graph Field (truth) | Comparison |
|---------------------|--------------------|--------------------|
| `depends_on` | `code_imports` | Sort both, compare sets |
| `depended_by` | Computed from other modules' `code_imports` | Reverse lookup |
| `public_api` | `code_exports` | Sort both, compare sets |
| `components` | `code_components` | Direct number comparison |

**Computing `depended_by`:** For each module X, check all other modules' `code_imports`. If module Y's `code_imports` includes X's name, then Y depends on X, so X's `depended_by` should include Y.

**IMPORTANT — Fields the skill MUST NOT touch:**
- `purpose` — human-authored, may be refined by narrative review only
- `constraints` — human domain knowledge
- `status` — human decision
- `entry_points` — partially human-maintained (CLI commands are not in code_exports)
- `name`, `type` — identity fields

### Step 4: Present Frontmatter Diffs

For each module with differences, present a clear before/after:

```
## Frontmatter Drift Report

### mod-memory
  depends_on: [config] → [config, schemas]
    added: schemas
  components: 30 → 34
  public_api: +get_memory_dir_for_scope, +migrate_to_personal, +needs_migration

### mod-context
  public_api: +GraphDiff, +NodeChange, +diff_graphs
  components: 25 → 25  (no change)

### mod-session
  depends_on: [memory, onboarding, schemas, context] → [context, memory, onboarding, schemas]
    (reordered only — code_imports is alphabetical)

2 modules with substantive changes, 1 with ordering-only changes.
```

**Ordering note:** `code_imports` and `code_exports` are alphabetically sorted from the analyzer. Doc-declared fields may have a different order. When the only difference is ordering, flag it but don't treat it as drift unless the user wants consistent ordering.

### Step 5: HITL Gate — Frontmatter Changes

Present the drift report and ask:

> "Apply frontmatter updates to N modules? [y/n/selective]"

- **y** → Apply all frontmatter changes
- **n** → Skip frontmatter, move to narrative review
- **selective** → Ask per-module

**Applying changes:** Use the Edit tool to modify only the YAML frontmatter section (between the `---` delimiters) of each module doc. Preserve all other content unchanged. Preserve field ordering as much as possible — only change values, don't reorder keys.

### Step 6: Check for Narrative Review Triggers

**Trigger A — Structural changes (full narrative review):**

- New modules appeared in the graph (not yet documented)
- Modules removed from the graph (docs exist but code doesn't)
- Major dependency changes (>2 new dependencies or >2 removed)
- Significant public API changes (>5 new exports or >5 removed)

**Trigger B — Stale value references (targeted scan):**

For **every** module with any frontmatter change (even a single field), scan the narrative body for hardcoded references to old values:

- `components` changed → search prose for the old count (e.g., "component count (60)" when frontmatter now says 69)
- `depends_on` removed a dependency → search prose for mentions of the removed module name outside the Dependencies table
- `depended_by` changed → check if any prose references the old dependent list
- `public_api` removed entries → search for mentions of removed function/class names in Key Files or Architecture sections

This is a mechanical text search, not inference. It catches stale hardcoded numbers and names that contradict updated frontmatter.

**If no triggers:** Skip to Step 8.

**If Trigger A:** Proceed to Step 7 (full narrative review).

**If Trigger B only:** Proceed to Step 7 but scope to targeted fixes for the stale references found.

### Step 7: Narrative Review

**For Trigger A modules (structural changes):** Read the full module doc and propose updates to narrative sections using inference:

- **Architecture** section — if dependencies changed significantly
- **Key Files** section — if new files were added to the module
- **Dependencies** table — if depends_on changed
- **Conventions** section — rarely needs updating

Present proposed changes as a diff and ask for HITL approval before applying.

**IMPORTANT:** Trigger A changes use inference. Changes are suggestions, not facts. Always present them for review.

**For Trigger B modules (stale value references):** Apply targeted mechanical fixes:

- Replace old component counts with new values from frontmatter
- Remove references to dropped dependencies in prose paragraphs
- Update any mentions of old API names that were removed

These are factual corrections (the frontmatter is already approved as truth), but still present them for HITL confirmation before writing.

### Step 8: Rebuild Graph (if docs changed)

If any frontmatter or narrative changes were applied in Steps 5-7, rebuild the graph so it reflects the updated docs:

```bash
rai graph build
```

This closes the coherence loop — the graph now contains both the code truth AND the corrected doc-declared values. Without this step, the graph would still hold pre-update frontmatter until the next manual build.

**If no changes were applied:** Skip this step.

### Step 9: Summary

Present a summary of what was done:

```
## Docs Update Summary

Modules checked: 12
Frontmatter updated: 3 (mod-memory, mod-context, mod-session)
Narrative updated: 1 (mod-context)
Graph rebuilt: yes
No changes needed: 8
Skipped: 0
```

## Output

| Item | Destination |
|------|-------------|
| Updated frontmatter | `governance/architecture/modules/*.md` |
| Narrative changes | `governance/architecture/modules/*.md` (with HITL) |
| Summary | Displayed (not saved) |

## Notes

- **No new Python code.** This skill uses existing `rai graph` commands and Claude's file editing tools.
- **PAT-172:** Skill-over-CLI for infrequent tasks. Frontmatter comparison is mechanical but runs per-story at most.
- **PAT-196:** Architecture docs are the map — keeping them current prevents future sessions from using wrong paths.
- **`entry_points` excluded from auto-update** because CLI command names aren't captured in `code_exports`. These are human-maintained.
- **Idempotent:** Running the skill twice with no code changes produces no updates.

## References

- ADR-025: Incremental Coherence — Graph Diffing and AI-Driven Doc Regeneration
- S16.2: Graph Diff Engine (prerequisite — provides diff infrastructure)
- S16.4: Lifecycle Integration (future — wires this into story-close)
- Module docs: `governance/architecture/modules/*.md`
- Graph: `.raise/rai/memory/index.json`
