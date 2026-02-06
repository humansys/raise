# F13.3 Discovery Skills — Design Specification

> **Feature:** F13.3 Discovery Skills
> **Epic:** E13 Discovery
> **Size:** M (4 SP)
> **Created:** 2026-02-04

---

## What & Why

**Problem:** When Rai scans a codebase with `raise discover scan`, the output is raw symbol data (names, signatures, locations). To build a useful component catalog, someone must describe what each component does and how it relates to others. Manually writing descriptions is tedious and requires deep codebase knowledge humans often lack.

**Value:** Discovery skills enable Rai to synthesize meaningful descriptions from extracted symbols, then present them to humans for validation. Human effort shifts from *writing* to *reviewing*. The result: accurate component documentation at AI speed.

---

## Approach

Create 4 skills that form a discovery workflow:

```
/discover-start  →  /discover-scan  →  /discover-validate  →  /discover-complete
     │                   │                    │                      │
  Detect project      Extract +            Human reviews         Output validated
  Create system       Synthesize           Approves/edits        nodes for graph
```

**Key design decisions:**

1. **Skills call CLI toolkit** — Skills orchestrate, `raise discover scan` does extraction
2. **Intermediate state as YAML** — Draft components stored in `work/discovery/` for human review
3. **Batch validation** — Present components in batches (5-10), not one by one
4. **Telemetry at each step** — Track discovery lifecycle for learning

---

## Components

| Component | Type | Location | Purpose |
|-----------|------|----------|---------|
| `/discover-start` | Skill | `.claude/skills/discover-start/` | Initialize discovery, detect project type |
| `/discover-scan` | Skill | `.claude/skills/discover-scan/` | Run extraction, synthesize descriptions |
| `/discover-validate` | Skill | `.claude/skills/discover-validate/` | Human validation loop |
| `/discover-complete` | Skill | `.claude/skills/discover-complete/` | Output validated nodes |
| `work/discovery/` | Artifacts | `work/discovery/` | Intermediate discovery state |

---

## Detailed Design

### 1. `/discover-start` — Initialize Discovery

**Purpose:** Detect project type, identify key directories, create system-level context.

**Flow:**
1. Detect languages present (check file extensions)
2. Identify entry points (`src/`, `lib/`, `app/`)
3. Create discovery context file
4. Emit telemetry: `discovery_event` type=start

**Output:** `work/discovery/context.yaml`

```yaml
# work/discovery/context.yaml
project:
  name: raise-cli
  languages: [python]
  root_dirs:
    - src/raise_cli
  entry_points:
    - src/raise_cli/cli/main.py
  detected_at: 2026-02-04T10:00:00Z

status: initialized
```

**Telemetry:**
```bash
raise telemetry emit discovery {project} --event start
```

### 2. `/discover-scan` — Extract & Synthesize

**Purpose:** Run extraction toolkit, then Rai synthesizes descriptions for each symbol.

**Flow:**
1. Read `work/discovery/context.yaml` for scope
2. Run `raise discover scan {path} --output json`
3. For each extracted symbol, Rai synthesizes:
   - `purpose`: 1-2 sentence description of what it does
   - `depends_on`: List of dependencies (from imports/signatures)
   - `category`: Suggested category (service, model, utility, etc.)
4. Output draft components to `work/discovery/components-draft.yaml`
5. Emit telemetry: `discovery_event` type=scan

**Synthesis prompt pattern:**

```
Given this extracted symbol:
  name: {name}
  kind: {kind}
  signature: {signature}
  docstring: {docstring}
  file: {file}

Synthesize:
1. Purpose (1-2 sentences, what it does, why it exists)
2. Category (service|model|utility|handler|parser|builder|schema|command)
3. Key dependencies (from signature/docstring)

Be concise. Focus on reuse value.
```

**Output:** `work/discovery/components-draft.yaml`

```yaml
# work/discovery/components-draft.yaml
generated_at: 2026-02-04T10:05:00Z
source_scan: raise discover scan src/raise_cli --language python
symbol_count: 45

components:
  - id: comp-scanner-symbol
    name: Symbol
    kind: class
    file: src/raise_cli/discovery/scanner.py
    line: 44
    signature: "class Symbol(BaseModel)"
    # Synthesized by Rai:
    purpose: "Represents a code symbol extracted from source files. Core data structure for discovery output."
    category: model
    depends_on: [pydantic.BaseModel]
    validated: false

  - id: comp-scanner-scan-directory
    name: scan_directory
    kind: function
    file: src/raise_cli/discovery/scanner.py
    line: 450
    signature: "def scan_directory(path: Path, ...) -> ScanResult"
    purpose: "Scans a directory tree for source files and extracts all symbols. Main entry point for discovery."
    category: utility
    depends_on: [Symbol, ScanResult, extract_python_symbols]
    validated: false
```

**ID Generation:** `comp-{module}-{name}` lowercase, hyphens.

### 3. `/discover-validate` — Human Review Loop

**Purpose:** Present draft components to human for review, capture approvals/edits.

**Flow:**
1. Load `work/discovery/components-draft.yaml`
2. Present in batches of 5-10 components
3. For each component, ask human:
   - **Approve** — Mark as validated
   - **Edit** — Human provides corrected purpose/category
   - **Skip** — Mark for exclusion (internal/trivial)
4. Update `components-draft.yaml` with `validated: true` or edits
5. Continue until all reviewed or human exits
6. Emit telemetry: `discovery_event` type=validate

**Presentation format:**

```markdown
## Component 1/10: Symbol

**File:** src/raise_cli/discovery/scanner.py:44
**Kind:** class
**Signature:** `class Symbol(BaseModel)`

**Purpose (Rai):** Represents a code symbol extracted from source files. Core data structure for discovery output.

**Category:** model
**Dependencies:** pydantic.BaseModel

---

[ Approve ]  [ Edit ]  [ Skip ]
```

**Edit flow:**
- If human chooses Edit, ask for corrected purpose/category
- Apply correction to draft YAML

**Batch control:**
- Default batch size: 10
- Human can type "done" to stop early
- Progress saved after each batch

### 4. `/discover-complete` — Output Validated Nodes

**Purpose:** Export validated components in format ready for graph integration (F13.4).

**Flow:**
1. Load `work/discovery/components-draft.yaml`
2. Filter to `validated: true` only
3. Transform to unified graph node format
4. Output to `work/discovery/components-validated.json`
5. Show summary statistics
6. Emit telemetry: `discovery_event` type=complete

**Output:** `work/discovery/components-validated.json`

```json
{
  "generated_at": "2026-02-04T10:30:00Z",
  "component_count": 32,
  "components": [
    {
      "id": "comp-scanner-symbol",
      "type": "component",
      "content": "Represents a code symbol extracted from source files. Core data structure for discovery output.",
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
  ]
}
```

**Note:** This is F13.3's output. F13.4 (Graph Integration) will consume this and add to unified graph.

---

## Skill Structure Pattern

All discovery skills follow the existing skill structure:

```
.claude/skills/discover-{name}/
├── SKILL.md          # Main skill document
```

**Frontmatter pattern:**

```yaml
---
name: discover-{name}
description: >
  {One-line description}

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "{1-4}"
  raise.prerequisites: "{previous skill or empty}"
  raise.next: "{next skill or empty}"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=discover-{name} \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---
```

**Metadata values:**
- `work_cycle: discovery` — New cycle type for discovery workflow
- `fase: 1-4` — Position in discovery flow (start=1, scan=2, validate=3, complete=4)
- `prerequisites`: Empty for start, previous skill for others
- `next`: Next skill in flow, empty for complete

---

## Telemetry Integration

**New signal type:** `discovery_event`

Following ADR-018 pattern:

```json
{
  "type": "discovery_event",
  "timestamp": "2026-02-04T10:00:00Z",
  "project": "raise-cli",
  "event": "start|scan|validate|complete",
  "metadata": {
    "languages": ["python"],
    "symbol_count": 45,
    "validated_count": 32,
    "duration_sec": 120
  }
}
```

**Emit via CLI:**

```bash
# From skill, manual emit (until raise telemetry supports discovery_event)
echo '{"type":"discovery_event",...}' >> .rai/telemetry/signals.jsonl
```

**Alternative (simpler):** Use `skill_event` with skill names `discover-start`, etc. The existing hook handles this automatically on skill Stop.

**Decision:** Use existing `skill_event` mechanism (hook-based). The 4 skill events give us the discovery lifecycle without new signal types.

---

## Acceptance Criteria

### MUST

- [ ] `/discover-start` detects Python/TS/JS projects and creates `work/discovery/context.yaml`
- [ ] `/discover-scan` runs `raise discover scan` and synthesizes descriptions for each symbol
- [ ] `/discover-validate` presents components for human review with approve/edit/skip
- [ ] `/discover-complete` outputs validated components in JSON format ready for F13.4
- [ ] All skills emit telemetry via Stop hook

### SHOULD

- [ ] Batch validation supports configurable batch size (default 10)
- [ ] `/discover-scan` groups symbols by module for better synthesis context
- [ ] Skills follow ShuHaRi pattern (explicit mastery levels)

### MUST NOT

- [ ] Skills must not directly modify the unified graph (that's F13.4)
- [ ] Skills must not require external services (local-only)
- [ ] Validation must not auto-approve without human confirmation

---

## Examples

### Example 1: Full Discovery Flow

```bash
# Human invokes discovery
/discover-start

# Rai detects project, creates context
# Output: work/discovery/context.yaml

/discover-scan

# Rai runs extraction, synthesizes descriptions
# Output: work/discovery/components-draft.yaml (45 components)

/discover-validate

# Human reviews in batches of 10
# Approves 32, skips 13 (internal helpers)
# Updates: work/discovery/components-draft.yaml

/discover-complete

# Rai exports validated components
# Output: work/discovery/components-validated.json (32 components)
# Ready for F13.4 graph integration
```

### Example 2: Validation Interaction

```markdown
## Batch 1/5 — Components 1-10

### 1. Symbol (class)
**File:** scanner.py:44 | **Category:** model
**Purpose:** Represents a code symbol extracted from source files.

Your choice: [A]pprove / [E]dit / [S]kip? **A**
✓ Approved

### 2. _get_signature (function)
**File:** scanner.py:96 | **Category:** utility
**Purpose:** Extract signature from an AST node.

Your choice: [A]pprove / [E]dit / [S]kip? **S**
⊘ Skipped (internal helper)

### 3. ScanResult (class)
**File:** scanner.py:77 | **Category:** model
**Purpose:** Result of scanning a directory or file.

Your choice: [A]pprove / [E]dit / [S]kip? **E**
Enter corrected purpose: **Container for scan operation results including symbols found, files processed, and any errors encountered.**
✓ Updated

---
Batch 1 complete: 8 approved, 2 skipped
Continue to batch 2? [Y/n]
```

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|:----------:|------------|
| Synthesis produces poor descriptions | Medium | Human validation catches; edit flow allows correction |
| Too many components overwhelm human | Medium | Batch validation; skip trivial via naming heuristics |
| Validation state lost on interruption | Low | YAML persists after each batch; resume from last state |

---

## Notes

### Why YAML for Intermediate State

- Human-readable for debugging
- Easy to hand-edit if needed
- Git-friendly diffs
- JSON for final output (machine consumption)

### Why Not Direct Graph Integration

Separation of concerns:
- F13.3 = Generate + Validate (human-in-loop)
- F13.4 = Persist + Query (machine operation)

This allows re-running validation without touching graph, and makes testing easier.

### Synthesis Context Strategy

Group symbols by module before synthesis to give Rai better context:
```
Module: src/raise_cli/discovery/scanner.py
  - Symbol (class)
  - ScanResult (class)
  - extract_python_symbols (function)
  - scan_directory (function)
```

Rai can understand relationships better when seeing module context.

---

*Design created: 2026-02-04*
*Next: `/story-plan` to decompose into tasks*
