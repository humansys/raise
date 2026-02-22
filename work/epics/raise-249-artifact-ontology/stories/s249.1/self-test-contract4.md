---
story_id: "S-EXAMPLE"
title: "Add export command to CLI"
epic_ref: "E-EXAMPLE"
complexity: "moderate"
status: "draft"
---

# Design: Add export command to CLI

## 1. What & Why

**Problem:** Users cannot export their session data in a portable format. They must manually copy files to share context with other team members.

**Value:** An `export` command enables portable session sharing, reducing onboarding time for new team members joining mid-project.

## 2. Approach

Add a new `export` subcommand to the CLI that serializes session state + selected memory entries into a single JSON file. Modify the session module to support serialization.

**Components affected:**
- `src/cli/commands/` — create `export.py` (new)
- `src/session/state.py` — modify (add serialization)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `src/cli/commands/__init__.py` | Registers 5 subcommands via `register_commands(app)` | Add `export` to registration | Existing commands unchanged |
| `src/session/state.py` | `class SessionState` with `load()`, `save()`, `close()` | Add `to_dict() -> dict` method | Load/save/close unchanged |
| `src/memory/index.py` | `class MemoryIndex` with `query()`, `build()` | No changes | Read-only consumption via `query()` |

## 4. Target Interfaces

### New/Modified Functions
```
// TypeScript-style for this example project:

// NEW: src/cli/commands/export.ts
function exportSession(outputPath: string, options: ExportOptions): ExportResult

// MODIFIED: src/session/state.ts
// Added method:
toDict(includeMemory: boolean): SessionDict
```

### New/Modified Models
```
// NEW:
interface ExportOptions {
  format: "json" | "yaml";
  includeMemory: boolean;
  memoryQuery?: string;
}

interface ExportResult {
  outputPath: string;
  entriesExported: number;
  sizeBytes: number;
}

interface SessionDict {
  sessionId: string;
  project: string;
  state: Record<string, unknown>;
  memoryEntries?: MemoryEntry[];
}
```

### Integration Points
- `exportSession()` calls `SessionState.toDict()` to serialize current state
- `exportSession()` calls `MemoryIndex.query()` to fetch memory entries (read-only)
- `register_commands()` registers `exportSession` as the `export` subcommand

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

*(Fallback — no story.md for this example:)*
- **MUST:** `export` command produces valid JSON with session + memory
- **MUST:** Export file is importable (round-trip)
- **SHOULD:** Support YAML format option
- **MUST NOT:** Modify existing session state during export

## 6. Constraints

- Export file must be < 10MB for typical sessions
- No new dependencies allowed

---

*Self-test artifact for Contract 4 validation (S249.1)*

**Verification:** Can story-plan derive tasks from this?
- Gemba table → knows exactly which 3 files to touch
- Target Interfaces → `exportSession()`, `toDict()`, 3 models = clear task deliverables
- Integration Points → task dependencies (state before export, registration last)
- AC → test specs derivable from MUST items

**Result: YES** — story-plan could produce SDLD blueprints from this artifact.
