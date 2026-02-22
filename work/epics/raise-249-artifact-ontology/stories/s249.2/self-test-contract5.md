---
story_id: "S-EXAMPLE"
title: "Add export command to CLI"
task_count: 3
status: "ready"
---

# Plan: Add export command to CLI

## Overview
- **Story:** S-EXAMPLE
- **Size:** M
- **Tasks:** 3
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-21

## Tasks

### Task 1: Implement SessionState.toDict() serialization

**Objective:** Add serialization method to SessionState so export can read session data.

**RED — Write Failing Test:**
- **File:** `tests/session/test_state.ts`
- **Test function:** `test_toDict_includes_session_and_memory`
- **Setup:** Given a SessionState with active session and 3 memory entries
- **Action:** When `toDict(includeMemory: true)` is called
- **Assertion:** Then result contains sessionId, project, state, and 3 memoryEntries
```typescript
describe('SessionState.toDict', () => {
  it('should include session data and memory entries', () => {
    // Given
    const state = new SessionState('SES-001', 'my-project');
    state.addMemoryEntries(mockEntries);
    // When
    const result = state.toDict(true);
    // Then
    expect(result.sessionId).toBe('SES-001');
    expect(result.project).toBe('my-project');
    expect(result.memoryEntries).toHaveLength(3);
  });
});
```

**GREEN — Implement:**
- **File:** `src/session/state.ts`
- **Function/Class:**
```typescript
// MODIFIED: Added method to existing SessionState class
toDict(includeMemory: boolean): SessionDict {
  /** Serialize session state to a portable dictionary. */
  ...
}
```
- **Integration:** Called by `exportSession()` in Task 2

**Verification:**
```bash
npx jest tests/session/test_state.ts --testNamePattern toDict -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** "MUST: `export` command produces valid JSON with session + memory"

---

### Task 2: Implement export command + registration

**Objective:** Create the `export` CLI subcommand that serializes session + memory to a JSON file.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_export.ts`
- **Test function:** `test_export_produces_valid_json`
- **Setup:** Given a running session with memory entries
- **Action:** When `exportSession('/tmp/out.json', { format: 'json', includeMemory: true })` is called
- **Assertion:** Then output file exists, is valid JSON, contains session + memory, and size < 10MB
```typescript
describe('exportSession', () => {
  it('should produce valid JSON with session and memory', () => {
    // Given
    const session = createTestSession();
    // When
    const result = exportSession('/tmp/out.json', {
      format: 'json',
      includeMemory: true,
    });
    // Then
    expect(result.entriesExported).toBeGreaterThan(0);
    const content = JSON.parse(fs.readFileSync('/tmp/out.json', 'utf-8'));
    expect(content.sessionId).toBeDefined();
    expect(content.memoryEntries).toBeDefined();
  });
});
```

**GREEN — Implement:**
- **File:** `src/cli/commands/export.ts` (new)
- **Function/Class:**
```typescript
// NEW: Export command
function exportSession(outputPath: string, options: ExportOptions): ExportResult {
  /** Serialize session state + selected memory entries to a file. */
  ...
}
```
- **File:** `src/cli/commands/index.ts` (modify)
- **Integration:** Calls `SessionState.toDict()` from Task 1; calls `MemoryIndex.query()` (read-only, no changes); registered via `registerCommands(app)`

**Verification:**
```bash
npx jest tests/cli/commands/test_export.ts -v
```

**Size:** M
**Dependencies:** Task 1
**AC Reference:** "MUST: `export` command produces valid JSON with session + memory", "MUST NOT: Modify existing session state during export"

---

### Task 3 (Final): Integration Verification

**Objective:** Validate export works end-to-end with a real session.

**Verification:**
```bash
# Run all story tests
npx jest tests/session/test_state.ts tests/cli/commands/test_export.ts -v

# Lint
npx eslint src/cli/commands/export.ts src/session/state.ts

# Type check
npx tsc --noEmit

# Manual: start a session, add data, run export, inspect output JSON
```

**Size:** XS
**Dependencies:** Tasks 1, 2

## Execution Order

1. Task 1 — SessionState.toDict() (foundation — no dependencies)
2. Task 2 — export command (depends on Task 1)
3. Task 3 — Integration verification (depends on all)

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "MUST: export produces valid JSON with session + memory" | T1, T2 | Target Interfaces → exportSession, toDict |
| "MUST: Export file is importable (round-trip)" | T2 | Target Interfaces → ExportResult |
| "SHOULD: Support YAML format option" | T2 | Target Interfaces → ExportOptions.format |
| "MUST NOT: Modify existing session state during export" | T2 | Target Interfaces → toDict (read-only) |

## Risks

- ExportOptions.format 'yaml' adds a dependency: Mitigation — use JSON as primary, YAML as optional (SHOULD, not MUST)

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | M | -- | |
| 3 | XS | -- | Integration verification |

---

*Self-test artifact for Contract 5 validation (S249.2)*

**Verification: Can story-implement execute this mechanically?**
- RED sections → exact test file, function name, Given/When/Then, code sketch ✅
- GREEN sections → exact file, signature from Contract 4, integration point ✅
- Verification → exact command to run ✅
- AC Reference → every task traces to AC ✅
- Traceability → all 4 AC items covered ✅
- Zero design decisions required by implementer ✅

**Result: YES** — story-implement could execute these tasks without making architectural decisions. Contract 5 works.
