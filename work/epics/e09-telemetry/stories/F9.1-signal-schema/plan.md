# Implementation Plan: F9.1 Signal Schema

## Overview
- **Feature:** F9.1
- **Epic:** E9 Local Learning
- **Story Points:** 1 SP
- **Feature Size:** XS
- **Created:** 2026-02-03

## Story

**As** Rai (the AI partner)
**I want** well-defined signal schemas
**So that** telemetry events have consistent structure for collection and analysis

## Acceptance Criteria

- [ ] 5 signal types defined as Pydantic models (SkillEvent, SessionEvent, CalibrationEvent, ErrorEvent, CommandUsage)
- [ ] Each signal has `type` discriminator field (Literal)
- [ ] Each signal has `timestamp` field (datetime)
- [ ] Signal union type for type-safe handling
- [ ] All models serialize to JSON correctly
- [ ] Tests pass with >90% coverage

## Tasks

### Task 1: Create telemetry module with schemas
- **Description:** Create new telemetry module with Pydantic signal schemas following ADR-018 specification
- **Files:**
  - `src/raise_cli/telemetry/__init__.py` (new)
  - `src/raise_cli/telemetry/schemas.py` (new)
- **Verification:** `python -c "from raise_cli.telemetry import SkillEvent"`
- **Size:** XS
- **Dependencies:** None

### Task 2: Add tests for schemas
- **Description:** Unit tests for all signal types - validation, serialization, edge cases
- **Files:**
  - `tests/telemetry/__init__.py` (new)
  - `tests/telemetry/test_schemas.py` (new)
- **Verification:** `pytest tests/telemetry/ -v --cov=src/raise_cli/telemetry`
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order

1. Task 1 (foundation) — Create schemas
2. Task 2 (validation) — Add tests

## Risks

- **Schema drift from ADR-018:** Mitigation — Copy schemas exactly from ADR-018
- **Missing edge cases:** Mitigation — Test optional fields, validation errors

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | XS | 10m | -- | |
| 2 | XS | 15m | -- | |
| **Total** | **XS** | **25m** | -- | |

---

*Plan created: 2026-02-03*
*Next: `/story-implement`*
