---
name: discover-complete
description: >
  Export validated components to JSON format ready for graph integration.
  Filters to approved components and transforms to unified graph node schema.

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "4"
  raise.prerequisites: discover-validate
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=discover-complete \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Discovery Complete: Export Validated Components

## Purpose

Export validated components to JSON format ready for graph integration. This transforms the human-validated draft into the final component catalog that can be added to the unified context graph.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Export all validated components; show summary statistics.

**Ha (破)**: Filter by category or minimum validation threshold.

**Ri (離)**: Custom export formats; integration with external systems.

## Context

**When to use:**
- After `/discover-validate` has marked components as validated
- When ready to integrate components into unified graph
- To generate component catalog for documentation

**When to skip:**
- No validated components yet (run `/discover-validate` first)
- Need to re-validate before export

**Inputs required:**
- `work/discovery/components-draft.yaml` with validated components

**Output:**
- `work/discovery/components-validated.json` — Final component catalog
- Ready for F13.4 Graph Integration

## Steps

### Step 1: Load Draft Components

Read the draft file:

```bash
cat work/discovery/components-draft.yaml
```

**Count:**
- Total components
- Validated (`validated: true`)
- Skipped (`skipped: true`)
- Pending (neither validated nor skipped)

**Verification:** Draft file exists with validated components.

> **If you can't continue:** No validated components → Run `/discover-validate` first.

### Step 2: Check Validation Threshold

Verify sufficient validation for export:

**Minimum threshold:** At least 1 validated component (configurable).

**Warning if:**
- Many components still pending (>50%)
- Low validation rate suggests incomplete review

**Proceed if:**
- User confirms partial export is acceptable
- OR validation threshold met

**Verification:** Threshold met OR user confirmed partial export.

### Step 3: Filter Validated Components

Select components for export:

**Include:**
- `validated: true`

**Exclude:**
- `validated: false` (pending)
- `skipped: true` (human excluded)
- `internal: true` AND `validated: false`

**Verification:** Export list created.

### Step 4: Transform to Graph Node Format

Convert each validated component to unified graph node schema:

**Input (from YAML):**
```yaml
id: comp-scanner-symbol
name: Symbol
kind: class
file: src/raise_cli/discovery/scanner.py
line: 44
signature: "class Symbol(BaseModel)"
purpose: "Represents a code symbol extracted from source files."
category: model
depends_on:
  - pydantic.BaseModel
validated: true
validated_at: "2026-02-04T10:25:00Z"
validated_by: human
```

**Output (to JSON):**
```json
{
  "id": "comp-scanner-symbol",
  "type": "component",
  "content": "Represents a code symbol extracted from source files.",
  "source_file": "src/raise_cli/discovery/scanner.py",
  "created": "2026-02-04T10:30:00Z",
  "metadata": {
    "name": "Symbol",
    "kind": "class",
    "line": 44,
    "signature": "class Symbol(BaseModel)",
    "category": "model",
    "depends_on": ["pydantic.BaseModel"],
    "validated_by": "human",
    "validated_at": "2026-02-04T10:25:00Z"
  }
}
```

**Mapping:**
| YAML Field | JSON Field |
|------------|------------|
| `id` | `id` |
| (constant) | `type: "component"` |
| `purpose` | `content` |
| `file` | `source_file` |
| (generated) | `created` |
| (all other) | `metadata.*` |

### Step 5: Write JSON Output

Create `work/discovery/components-validated.json`:

```json
{
  "generated_at": "2026-02-04T10:30:00Z",
  "source_file": "work/discovery/components-draft.yaml",
  "component_count": 32,
  "components": [
    { ... },
    { ... }
  ]
}
```

**Write the file** using the Write tool.

**Verification:** File created at `work/discovery/components-validated.json`.

### Step 6: Update Discovery Status

Update `work/discovery/context.yaml` status:

```yaml
status: complete  # was: initialized
completed_at: {ISO_TIMESTAMP}
component_count: {N}
```

**Verification:** Context status updated.

### Step 7: Display Summary

Present completion summary:

```markdown
## Discovery Complete

**Components exported:** {N}
**Output file:** `work/discovery/components-validated.json`

### Category Breakdown
| Category | Count |
|----------|-------|
| model | 12 |
| service | 8 |
| utility | 7 |
| handler | 3 |
| command | 2 |

### Validation Summary
- Total discovered: {N}
- Validated: {N} ({percent}%)
- Skipped: {N}
- Pending: {N}

### Sample Components
1. **Symbol** (model) — Represents a code symbol extracted from source files.
2. **scan_directory** (utility) — Scans a directory tree for source files.
3. **ConceptNode** (model) — A node in the unified context graph.

### Next Steps

**Graph Integration (F13.4):**
```bash
uv run raise discover build --input work/discovery/components-validated.json
```

This will add components to the unified context graph, enabling queries like:
```bash
uv run raise memory query --type component "scanner"
```

### Re-discovery

To refresh after code changes:
1. Run `/discover-start` (re-detect project structure)
2. Run `/discover-scan` (extract updated symbols)
3. Run `/discover-validate` (re-validate new/changed)
4. Run `/discover-complete` (export updated catalog)
```

**Verification:** Summary displayed; user knows next steps.

## Output

- **Artifact:** `work/discovery/components-validated.json`
- **Telemetry:** `skill_event` via Stop hook
- **Next:** F13.4 Graph Integration (`raise discover build`)

## JSON Output Schema

```json
{
  "generated_at": "ISO timestamp",
  "source_file": "path to draft YAML",
  "component_count": "number",
  "components": [
    {
      "id": "comp-{module}-{name}",
      "type": "component",
      "content": "purpose description",
      "source_file": "path/to/file.py",
      "created": "ISO timestamp",
      "metadata": {
        "name": "SymbolName",
        "kind": "class|function|method",
        "line": 123,
        "signature": "full signature",
        "category": "model|service|utility|...",
        "depends_on": ["dep1", "dep2"],
        "validated_by": "human",
        "validated_at": "ISO timestamp"
      }
    }
  ]
}
```

## Notes

### Partial Export

It's valid to export with some components still pending. The JSON will contain only validated components. Later:
- Re-run `/discover-validate` to review pending
- Re-run `/discover-complete` to update export

### Idempotency

Running `/discover-complete` multiple times:
- Overwrites previous JSON output
- Uses latest validated state from YAML
- Safe to re-run after additional validation

### Graph Integration Preview

The JSON output is designed to be consumed by F13.4's `raise discover build` command:

```bash
# Add components to unified graph
uv run raise discover build --input work/discovery/components-validated.json

# Then query components
uv run raise memory query --type component "service"
uv run raise memory query "authentication" --types component
```

### Component Type in Graph

Components use `type: "component"` in the unified graph, distinct from:
- `pattern` — Learned patterns
- `decision` — ADRs
- `guardrail` — Code standards
- `term` — Glossary definitions

This enables filtered queries: `--type component`

## References

- Previous skill: `/discover-validate`
- Graph integration: F13.4 (future)
- Design: `work/features/f13.3/design.md`
- Unified graph schema: `src/raise_cli/context/models.py`
