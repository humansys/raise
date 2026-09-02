---
name: rai-kc-build
description: Build a Knowledge Cartridge from source documents — guided flow from corpus analysis to extraction and review.
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Write
  - "Bash(rai:*)"
  - "Bash(uv:*)"

license: MIT

metadata:
  raise.work_cycle: creation
  raise.frequency: per-cartridge
  raise.fase: ""
  raise.prerequisites: "rai cartridge init <name> --corpus <path>"
  raise.next: "rai cartridge publish"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - cartridge_name: string, required, argument
  raise.outputs: |
    - config_yaml: file_path (.raise/cartridges/<name>/extractors/config.yaml)
    - relationships_yaml: file_path (.raise/cartridges/<name>/extractors/schemas/relationships.yaml)
    - instances: file_path[] (.raise/cartridges/<name>/instances/*.json)
---

# Knowledge Cartridge Build

## Purpose

Orchestrate the full Knowledge Cartridge creation flow from source documents to a queryable, publishable cartridge. Guides the user (or agent) through corpus analysis, seed schema generation, extraction, canonicalization, and review.

## Context

**When to use:** After `rai cartridge init <name> --corpus <path>` has scaffolded a cartridge with corpus documents.

**Prerequisite:** A cartridge directory exists at `.raise/cartridges/<name>/` with a valid `CARTRIDGE.yaml` and corpus files.

## Steps

### Step 1: Validate Cartridge

Verify the cartridge exists and has corpus files defined.

```bash
rai cartridge check {cartridge_name}
```

| Condition | Action |
|-----------|--------|
| Check passes | Continue |
| Cartridge not found | **STOP** — guide user to run `rai cartridge init {name} --corpus <path>` |
| No corpus defined | **STOP** — guide user to add `corpus:` paths to CARTRIDGE.yaml |

### Step 2: Build Seed Schema

Run corpus analysis and generate extractor configuration.

```bash
rai cartridge build {cartridge_name}
```

This analyzes the corpus documents, proposes node types and relationship types, and generates:
- `extractors/config.yaml` — one LLM extractor per proposed node type
- `extractors/schemas/relationships.yaml` — relationship type definitions
- Updates `CARTRIDGE.yaml` with `domain_context` and `competency_questions`

If `extractors/config.yaml` already exists, use `--force`:
```bash
rai cartridge build {cartridge_name} --force
```

Report the generated schema to the user:
- Number of node types proposed
- Number of relationship types
- Competency questions

### Step 3: Extract Nodes

Run the extraction pipeline with the generated configuration.

```bash
rai cartridge extract {cartridge_name}
```

Report:
- Number of nodes extracted
- Any warnings or errors

| Condition | Action |
|-----------|--------|
| Extraction succeeds | Continue |
| 0 nodes extracted | Warn user — corpus may be too sparse for the proposed schema |
| Extraction errors | Report errors, suggest adjusting config.yaml |

### Step 4: Canonicalize (Entity Resolution)

This step is handled automatically by the extraction hygiene pipeline (`apply_hygiene` in extract_cartridge). Report the hygiene results:
- Duplicate nodes merged
- Edge types normalized
- Broken relationships found

### Step 5: Review

Present the extraction summary for review.

```bash
rai cartridge review {cartridge_name}
```

Report:
- Nodes by type (counts)
- Coverage by source document
- Total node count

Ask the user if the results look good:
- If satisfied → proceed to Step 6
- If types need adjustment → use `--drop-type` / `--add-type` feedback:
  ```bash
  rai cartridge review {cartridge_name} --drop-type {type} --add-type {type}
  ```
  Then re-run Step 3 (extract) and Step 5 (review)

### Step 6: Complete

Report the cartridge is ready:

```
Cartridge '{cartridge_name}' is ready.
  Nodes: {count}
  Types: {type_list}

Next steps:
  - Query locally: rai cartridge query {cartridge_name} "your question"
  - Publish to server: rai cartridge publish {cartridge_name}
  - Pack for distribution: rai cartridge pack {cartridge_name}
```

## Quality Checklist

- [ ] Cartridge validated before any operation
- [ ] Seed schema generated from actual corpus analysis (not hardcoded)
- [ ] Extraction runs with generated config
- [ ] Review summary presented before declaring complete
- [ ] User guided through feedback loop if quality is insufficient
- [ ] NEVER skip the review step — it closes the quality loop
