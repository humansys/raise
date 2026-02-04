# Implementation Plan: F3.1 Identity Core Structure

## Overview

- **Feature:** F3.1 Identity Core Structure
- **Story Points:** 2 SP (lean scope)
- **Feature Size:** S
- **Created:** 2026-02-02
- **Design:** `work/features/f3.1-identity-core-structure/design.md`

## Tasks

### Task 1: Create Directory Structure + Manifest

- **Description:** Create `.rai/` directory with subdirectories and manifest.yaml
- **Files:**
  - `.rai/manifest.yaml`
  - `.rai/identity/` (directory)
  - `.rai/memory/` (directory)
  - `.rai/memory/sessions/` (directory)
  - `.rai/relationships/` (directory)
- **Verification:** Directories exist, manifest.yaml parses as valid YAML
- **Size:** XS
- **Dependencies:** None

### Task 2: Create Identity Files (Markdown)

- **Description:** Create core.md and perspective.md by migrating content from existing files
- **Files:**
  - `.rai/identity/core.md` — Migrate from `.claude/rai/identity.md` + extract from `RAI.md`
  - `.rai/identity/perspective.md` — Migrate from `.claude/RAI.md` perspective sections
- **Verification:** Files exist, markdown is well-formed, token budget < 3,500 combined
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Create Memory JSONL Files

- **Description:** Convert memory.md and calibration.md tables to JSONL format
- **Files:**
  - `.rai/memory/patterns.jsonl` — Convert from `.claude/rai/memory.md`
  - `.rai/memory/calibration.jsonl` — Convert from `.claude/rai/calibration.md`
  - `.rai/memory/sessions/index.jsonl` — Convert from `.claude/rai/session-index.md`
- **Verification:** Each JSONL file parses line-by-line, schemas match design spec
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Create Relationships JSONL

- **Description:** Extract Emilio's preferences from RAI.md into structured JSONL
- **Files:**
  - `.rai/relationships/humans.jsonl`
- **Verification:** JSONL parses, contains Emilio entry with required fields
- **Size:** XS
- **Dependencies:** Task 1

### Task 5: Archive Old Structure

- **Description:** Move `.claude/rai/` to `.claude/rai.archive/` for backup
- **Files:**
  - `.claude/rai/` → `.claude/rai.archive/`
- **Verification:** Archive exists, original location empty (except RAI.md which stays for now)
- **Size:** XS
- **Dependencies:** Tasks 2, 3, 4

## Execution Order

```
Task 1 (structure + manifest)
    ↓
┌───┴───┬───────┐
↓       ↓       ↓
Task 2  Task 3  Task 4  (parallel - independent content)
↓       ↓       ↓
└───┬───┴───────┘
    ↓
Task 5 (archive)
```

**Recommended sequence:** 1 → 2 → 3 → 4 → 5 (sequential for single developer)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Content loss during migration | Low | High | Keep `.claude/rai.archive/` until E3 complete |
| JSONL schema needs iteration | Medium | Low | Start with examples from design, adjust if needed |
| Token budget exceeded | Low | Medium | Measure after Task 2, trim if needed |

## Validation Gate

Before marking complete:
- [x] `.rai/` structure matches design spec (7 files)
- [x] All JSONL files parse correctly (43 total entries)
- [x] Identity markdown is coherent
- [x] Token budget: minimal load ~955 tokens (target <2,000)
- [x] Archive created at `.claude/rai.archive/`

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. Directory + Manifest | XS | 5 min | 2 min | |
| 2. Identity Markdown | S | 15 min | 5 min | Refactored from existing content |
| 3. Memory JSONL | S | 15 min | 5 min | 23 patterns, 9 calibration, 10 sessions |
| 4. Relationships JSONL | XS | 5 min | 2 min | |
| 5. Archive | XS | 2 min | 1 min | |
| **Total** | **S** | **~42 min** | **~15 min** | **2.8x velocity** |

---

*Implementation complete: 2026-02-02*
