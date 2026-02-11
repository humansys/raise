---
name: rai-discover-scan
description: >
  Extract symbols from codebase using rai discover scan, then synthesize
  meaningful descriptions for each component. Creates draft for human validation.

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "2"
  raise.prerequisites: discover-start
  raise.next: discover-validate
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Discovery Scan: Extract & Synthesize

## Purpose

Extract symbols from the codebase using the `rai discover scan` CLI command, then synthesize meaningful descriptions for each component. The output is a draft component catalog ready for human validation.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, synthesize descriptions for all public symbols.

**Ha (破)**: Filter to public APIs only; skip internal helpers automatically.

**Ri (離)**: Custom synthesis prompts for domain-specific codebases.

## Context

**When to use:**
- After `/rai-discover-start` has created context
- When refreshing component descriptions after code changes
- For targeted scan of specific directory

**When to skip:**
- `work/discovery/components-draft.yaml` exists and is current
- Just need to re-validate existing descriptions

**Inputs required:**
- `work/discovery/context.yaml` from `/rai-discover-start`
- OR explicit path argument for targeted scan

**Output:**
- `work/discovery/components-draft.yaml` — Draft components with synthesized descriptions
- Ready for `/rai-discover-validate`

## Steps

### Step 1: Load Discovery Context

Read the context file to determine scan scope:

```
Read: work/discovery/context.yaml
```

**Extract:**
- `languages` — Which extractors to use
- `root_dirs` — Directories to scan

**Alternative:** If user provides explicit path, use that instead of context.

**Verification:** Context loaded OR explicit path provided.

> **If you can't continue:** No context and no path → Run `/rai-discover-start` first.

### Step 2: Run Extraction

Execute the `rai discover scan` command:

```bash
# For each root_dir in context
rai discover scan {root_dir} --language {language} --output json
```

**Example:**
```bash
rai discover scan src/rai_cli --language python --output json
```

**Capture the JSON output** — it contains all extracted symbols.

**Verification:** JSON output received with symbols array.

> **If you can't continue:** Scan fails → Check path exists and language is supported.

### Step 3: Run Analysis

Run the deterministic analyzer on the scan output to compute confidence scores, auto-categorize components, fold methods into parent classes, and group by module:

```bash
rai discover analyze --input {scan_output_json} --output human
```

Or pipe directly:
```bash
rai discover scan {root_dir} --language {language} --output json | rai discover analyze --output human
```

**This produces:**
- Confidence scores for each component (high/medium/low tiers)
- Auto-categorization from path conventions and naming patterns
- Hierarchical folding (methods grouped under parent classes)
- Module grouping (for parallel AI synthesis batches)
- `work/discovery/analysis.json` — the primary artifact for `/rai-discover-validate`

**Review the summary output:**
- High-confidence components can be auto-validated (no AI synthesis needed)
- Medium-confidence components need AI synthesis in module batches
- Low-confidence components need individual human review

**Verification:** `work/discovery/analysis.json` exists with components and module_groups.

> **If you can't continue:** Analysis fails → Check scan output is valid JSON.

### Step 4: Synthesize Descriptions (Medium/Low Confidence Only)

**High-confidence components** (score >= 70): Use `auto_purpose` and `auto_category` from the analyzer — no AI synthesis needed.

**Medium and low-confidence components**: Synthesize descriptions using the module groups from the analysis. Process each module group as a batch:

For each module group in `analysis.json`:
1. Read all components in that module
2. Synthesize purpose and category for components that lack good auto_purpose

**Synthesis approach per component:**

Given:
```
name: {name}
kind: {kind} (class/function)
signature: {signature}
docstring: {docstring}  # may be None for low-confidence
file: {file}
auto_category: {category}  # from analyzer
auto_purpose: {purpose}  # from docstring first sentence, may be empty
```

Synthesize:
1. **Purpose** — What does it do? Why does it exist? (1-2 sentences, focus on reuse value)
2. **Category** — Verify or correct the auto_category
3. **Dependencies** — Key types/classes it depends on (from signature)

**Quality criteria:**
- Purpose is actionable (describes what, not how)
- Purpose highlights reuse value
- Category matches the symbol's role
- Dependencies are specific, not generic (`BaseModel`, not `pydantic`)

### Step 5: Generate Component IDs

Create unique IDs for each component:

**Pattern:** `comp-{module}-{name}`
- `module` = file stem without extension, lowercase
- `name` = symbol name, lowercase, hyphens for underscores

**Examples:**
- `Symbol` in `scanner.py` → `comp-scanner-symbol`
- `scan_directory` in `scanner.py` → `comp-scanner-scan-directory`
- `ConceptNode` in `models.py` → `comp-models-conceptnode`

### Step 6: Write Draft YAML

Create `work/discovery/components-draft.yaml`:

```yaml
# work/discovery/components-draft.yaml
# Generated by /rai-discover-scan
# Review with /rai-discover-validate

generated_at: {ISO_TIMESTAMP}
source_command: "raise discover scan {path} --language {lang}"
symbol_count: {N}

components:
  # Module: src/rai_cli/discovery/scanner.py
  - id: comp-scanner-symbol
    name: Symbol
    kind: class
    file: src/rai_cli/discovery/scanner.py
    line: 44
    signature: "class Symbol(BaseModel)"
    docstring: |
      A code symbol extracted from source.
      ...
    # Synthesized by Rai:
    purpose: "Represents a code symbol extracted from source files. Core data structure for discovery output."
    category: model
    depends_on:
      - pydantic.BaseModel
    internal: false
    validated: false

  - id: comp-scanner-get-signature
    name: _get_signature
    kind: function
    file: src/rai_cli/discovery/scanner.py
    line: 96
    signature: "def _get_signature(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str"
    docstring: "Extract signature from an AST node."
    purpose: "Internal helper for signature extraction."
    category: utility
    depends_on:
      - ast.ClassDef
      - ast.FunctionDef
    internal: true
    validated: false
```

**Write the file** using the Write tool.

**Verification:** File created at `work/discovery/components-draft.yaml`.

### Step 7: Display Summary

Present scan results to user:

```markdown
## Discovery Scan Complete

**Scanned:** {path}
**Language:** {language}
**Symbols found:** {total}
  - Classes: {N}
  - Functions: {N}
  - Methods: {N}

**Output:** `work/discovery/components-draft.yaml`

### Component Categories
- Models: {N}
- Services: {N}
- Utilities: {N}
- ...

### Internal (skipped for validation): {N}

### Next Step

Run `/rai-discover-validate` to review and approve component descriptions.
```

**Verification:** Summary displayed; user knows next step.

## Output

- **Artifacts:**
  - `work/discovery/analysis.json` — Deterministic analysis with confidence scores and module groups
  - `work/discovery/components-draft.yaml` — Draft components with synthesized descriptions
- **Telemetry:** `skill_event` via Stop hook
- **Next:** `/rai-discover-validate`

## Component Schema

```yaml
id: string              # Unique ID (comp-{module}-{name})
name: string            # Symbol name
kind: string            # class | function | method | module
file: string            # Relative path to source
line: number            # Line number (1-indexed)
signature: string       # Full signature
docstring: string       # Original docstring (if present)
purpose: string         # Synthesized description (1-2 sentences)
category: string        # service | model | utility | handler | parser | builder | schema | command | test
depends_on: string[]    # Key dependencies
internal: boolean       # True if private/internal
validated: boolean      # True after human review (false initially)
```

## Category Definitions

| Category | Description | Examples |
|----------|-------------|----------|
| `service` | Business logic, orchestration | UserService, AuthHandler |
| `model` | Data structures, schemas | User, ConceptNode, Symbol |
| `utility` | Helper functions, tools | format_date, parse_yaml |
| `handler` | Request/event handlers | handle_request, on_click |
| `parser` | Parsing, extraction | parse_markdown, extract_yaml |
| `builder` | Construction, generation | build_graph, create_report |
| `schema` | Validation, type definitions | UserSchema, ConfigModel |
| `command` | CLI commands | scan, query, emit |
| `test` | Test utilities | fixtures, mocks |

## Notes

### Synthesis Quality

Good synthesis focuses on **reuse value**:
- What problem does this solve?
- When would someone use this?
- What does it integrate with?

Bad synthesis describes implementation:
- "Uses a loop to iterate..."
- "Calls the database..."

### Handling Large Codebases

For codebases with >100 symbols:
1. Scan in chunks (by directory)
2. Focus on public APIs first
3. Use `--exclude` patterns for tests/vendors

### Targeted Scans

User can run for specific path:
```
/rai-discover-scan src/specific/module
```

This overrides context.yaml root_dirs for this scan.

## References

- Previous skill: `/rai-discover-start`
- Next skill: `/rai-discover-validate`
- CLI docs: `rai discover scan --help`
- Design: `work/stories/f13.3/design.md`
