---
description: 'Extract symbols from codebase using rai discover scan, then synthesize
  meaningful descriptions for each component. Creates draft for human validation.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-project
  raise.gate: ''
  raise.next: discover-validate
  raise.prerequisites: discover-start
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: discovery
name: rai-discover-scan
---

# Discovery Scan

> **Deprecated:** Use `/rai-discover` instead, which runs the full pipeline (detect → extract → describe → document → build) in one pass. This skill is kept for backward compatibility.

## Purpose

Extract symbols from the codebase and synthesize meaningful descriptions for each component. Produces a draft component catalog ready for human validation.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, synthesize descriptions for all public symbols
- **Ha**: Filter to public APIs only; skip internal helpers automatically
- **Ri**: Custom synthesis prompts for domain-specific codebases

## Context

**When to use:** After `/rai-discover-start` has created context, or for targeted scan of a specific directory.

**When to skip:** `work/discovery/components-draft.yaml` exists and is current.

**Inputs:** `work/discovery/context.yaml` from `/rai-discover-start`, OR explicit path argument.

## Steps

### Step 1: Extract Symbols

```bash
rai discover scan {root_dir} --language {language} --output json
```

<verification>
JSON output received with symbols array.
</verification>

<if-blocked>
Scan fails → check path exists and language is supported.
</if-blocked>

### Step 2: Run Analysis

```bash
rai discover scan {root_dir} --language {language} --output json | rai discover analyze --output human
```

Produces `work/discovery/analysis.json` with:
- Confidence scores per component (high ≥70 / medium 40-69 / low <40)
- Auto-categorization from path conventions and naming patterns
- Hierarchical folding (methods grouped under parent classes)
- Module grouping (for parallel AI synthesis batches)

<verification>
`work/discovery/analysis.json` exists with components and module_groups.
</verification>

### Step 3: Synthesize Descriptions

| Confidence | Action |
|-----------|--------|
| High (≥70) | Use `auto_purpose` and `auto_category` — no AI synthesis needed |
| Medium/Low | Synthesize per module group batch |

**Per component synthesis:**
1. **Purpose** — What does it do? Why does it exist? (1-2 sentences, focus on reuse value)
2. **Category** — Verify or correct auto_category
3. **Dependencies** — Key types from signature (specific, not generic)

### Step 4: Generate IDs & Write Draft

**ID pattern:** `comp-{module}-{name}` (lowercase, hyphens for underscores).

Write `work/discovery/components-draft.yaml`:

```yaml
generated_at: {ISO_TIMESTAMP}
symbol_count: {N}
components:
  - id: comp-scanner-symbol
    name: Symbol
    kind: class
    file: src/raise_cli/discovery/scanner.py
    line: 44
    signature: "class Symbol(BaseModel)"
    purpose: "Represents a code symbol extracted from source files."
    category: model
    depends_on: [pydantic.BaseModel]
    internal: false
    validated: false
```

<verification>
File created at `work/discovery/components-draft.yaml`.
</verification>

### Step 5: Display Summary

```markdown
## Discovery Scan Complete

**Scanned:** {path} | **Language:** {language} | **Symbols:** {total}
**Categories:** Models: {N}, Services: {N}, Utilities: {N}
**Output:** `work/discovery/components-draft.yaml`

**Next:** `/rai-discover-validate`
```

## Output

| Item | Destination |
|------|-------------|
| Analysis | `work/discovery/analysis.json` |
| Draft catalog | `work/discovery/components-draft.yaml` |
| Next | `/rai-discover-validate` |

## Quality Checklist

- [ ] Synthesis focuses on reuse value (what/why, not how)
- [ ] Categories match symbol roles (see category table below)
- [ ] Dependencies are specific types, not generic packages
- [ ] Large codebases (>100 symbols): scan in chunks by directory
- [ ] NEVER describe implementation details in purpose ("Uses a loop to...")

## References

- Previous: `/rai-discover-start`
- Next: `/rai-discover-validate`
- CLI: `rai discover scan --help`, `rai discover analyze --help`
- Categories: service, model, utility, handler, parser, builder, schema, command, test
