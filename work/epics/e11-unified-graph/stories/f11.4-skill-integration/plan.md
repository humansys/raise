# Implementation Plan: F11.4 Skill Integration

## Overview
- **Feature:** F11.4
- **Epic:** E11 Unified Context Architecture
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-03

## Tasks

### Task 1: Add Query Context Step to All 9 Skills
- **Description:** Add "Step 0.5: Query Context" after telemetry step in each skill
- **Files:** 9 SKILL.md files
- **Pattern:** Query unified graph with skill-specific focus keywords
- **Size:** M (9 files, but repetitive)

### Skills and Query Focus

| Skill | Query Keywords | Types Filter |
|-------|----------------|--------------|
| `/session-start` | session, epic, patterns | session, pattern |
| `/session-close` | session, patterns, learnings | pattern, session |
| `/story-design` | architecture, patterns, ADR | pattern, feature |
| `/story-plan` | planning, estimation, calibration | pattern, calibration |
| `/story-implement` | codebase, testing, patterns | pattern |
| `/story-review` | retrospective, process, patterns | pattern, session |
| `/epic-design` | architecture, ADR, epic | pattern, epic |
| `/epic-plan` | sequencing, calibration, planning | pattern, calibration |
| `/research` | research, methodology, evidence | pattern, session |

### Task 2: Verify Skills Work
- **Description:** Manual test that skill query context step works
- **Verification:** Run one skill, verify context query executes
- **Size:** XS

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | M | 30-40m | ~12m | 9 files, repetitive pattern |
| 2 | XS | 5m | ~3m | Grep verification |
| **Total** | **S** | **35-45m** | **~15m** | 2.5x velocity |
