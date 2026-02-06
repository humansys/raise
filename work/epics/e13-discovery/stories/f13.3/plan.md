# Implementation Plan: F13.3 Discovery Skills

## Overview

- **Feature:** F13.3 Discovery Skills
- **Story Points:** 4 SP (M)
- **Feature Size:** M
- **Created:** 2026-02-04
- **Design:** `work/stories/f13.3/design.md`

## Tasks

### Task 1: Create `/discover-start` Skill

- **Description:** Create the discovery initialization skill that detects project type and creates context file
- **Files:**
  - Create: `.claude/skills/discover-start/SKILL.md`
  - Create: `work/discovery/.gitkeep` (ensure directory exists)
- **TDD Cycle:** N/A (skill is markdown, tested via manual invocation)
- **Verification:**
  - Skill loads when invoked with `/discover-start`
  - Creates `work/discovery/context.yaml` with project info
- **Size:** S
- **Dependencies:** None

**Skill content includes:**
- YAML frontmatter with hooks (Stop hook for telemetry)
- Purpose section
- ShuHaRi mastery levels
- Context (when to use/skip)
- Steps: detect languages, identify directories, create context.yaml
- Output section with summary template

### Task 2: Create `/discover-scan` Skill

- **Description:** Create the extraction and synthesis skill that runs `raise discover scan` and has Rai synthesize descriptions
- **Files:**
  - Create: `.claude/skills/discover-scan/SKILL.md`
- **TDD Cycle:** N/A (skill is markdown)
- **Verification:**
  - Skill loads when invoked with `/discover-scan`
  - Reads `work/discovery/context.yaml`
  - Runs `raise discover scan` command
  - Outputs `work/discovery/components-draft.yaml`
- **Size:** M
- **Dependencies:** Task 1

**Skill content includes:**
- Prerequisites check (context.yaml exists)
- CLI invocation step with proper command
- Synthesis prompt pattern for Rai to follow
- YAML output format specification
- Component ID generation pattern (comp-{module}-{name})

### Task 3: Create `/discover-validate` Skill

- **Description:** Create the human validation skill with batch review flow (approve/edit/skip)
- **Files:**
  - Create: `.claude/skills/discover-validate/SKILL.md`
- **TDD Cycle:** N/A (skill is markdown)
- **Verification:**
  - Skill loads when invoked with `/discover-validate`
  - Reads `work/discovery/components-draft.yaml`
  - Presents components in batches
  - Uses AskUserQuestion for approve/edit/skip
  - Updates YAML with validated status
- **Size:** M
- **Dependencies:** Task 2

**Skill content includes:**
- Prerequisites check (components-draft.yaml exists)
- Batch presentation format
- AskUserQuestion pattern for choices
- Edit flow (corrected purpose/category)
- Progress tracking (batch N of M)
- Resume capability (skip already-validated)

### Task 4: Create `/discover-complete` Skill

- **Description:** Create the completion skill that exports validated components to JSON
- **Files:**
  - Create: `.claude/skills/discover-complete/SKILL.md`
- **TDD Cycle:** N/A (skill is markdown)
- **Verification:**
  - Skill loads when invoked with `/discover-complete`
  - Reads `work/discovery/components-draft.yaml`
  - Filters to validated=true only
  - Outputs `work/discovery/components-validated.json`
  - Shows summary statistics
- **Size:** S
- **Dependencies:** Task 3

**Skill content includes:**
- Prerequisites check (components-draft.yaml with validated items)
- JSON output format matching ConceptNode schema
- Summary statistics template
- Next steps guidance (F13.4 integration)

### Task 5 (Final): Manual Integration Test

- **Description:** Run full discovery flow on raise-cli codebase to validate end-to-end
- **Verification:**
  - `/discover-start` → creates context.yaml
  - `/discover-scan` → extracts symbols, synthesizes descriptions
  - `/discover-validate` → review at least one batch
  - `/discover-complete` → outputs validated JSON
  - Telemetry signals appear in signals.jsonl for each skill
- **Size:** S
- **Dependencies:** Tasks 1-4

**Test scope:**
- Run on `src/raise_cli/discovery/` (small module, known symbols)
- Verify context detection (Python)
- Verify synthesis produces reasonable descriptions
- Validate at least 3-5 components
- Confirm JSON output is valid for F13.4

## Execution Order

```
Task 1: /discover-start (foundation)
    ↓
Task 2: /discover-scan (needs context.yaml)
    ↓
Task 3: /discover-validate (needs components-draft.yaml)
    ↓
Task 4: /discover-complete (needs validated components)
    ↓
Task 5: Manual Integration Test (validates all)
```

Sequential execution — each skill depends on the previous skill's output.

## Risks

| Risk | Mitigation |
|------|------------|
| Skill markdown format errors | Copy from existing skill (story-start) as template |
| Stop hook not triggering | Test with `/discover-start` first, verify signals.jsonl |
| YAML output format issues | Document exact schema in skill, validate manually |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. discover-start | S | 15-20 min | — | |
| 2. discover-scan | M | 25-30 min | — | Most complex synthesis logic |
| 3. discover-validate | M | 25-30 min | — | Batch + AskUserQuestion flow |
| 4. discover-complete | S | 15-20 min | — | Straightforward transform |
| 5. Integration Test | S | 15-20 min | — | Full flow validation |
| **Total** | **M** | **~2 hrs** | — | |

## Notes

### Skill Structure Consistency

All skills must follow the established pattern from `story-start`:
- YAML frontmatter with name, description, license, metadata, hooks
- Stop hook pointing to `log-skill-complete.sh`
- Purpose, ShuHaRi, Context, Steps, Output, Notes sections

### AskUserQuestion Pattern for Validation

Task 3 uses AskUserQuestion tool for batch validation:
```markdown
For each component in batch:
  - Present: name, file, purpose, category
  - Ask: Approve / Edit / Skip
  - If Edit: Ask for corrected text
  - Update YAML
```

This leverages existing Claude Code capability rather than custom UI.

### Telemetry Verification

After each skill runs, verify in signals.jsonl:
```bash
tail -5 .rai/telemetry/signals.jsonl | grep discover
```

Should show `skill_event` with skill name and duration.

---

*Plan created: 2026-02-04*
*Next: `/story-implement` to execute tasks*
