---
name: rai-cartridge-agent
description: Build a Knowledge Cartridge using the local agent's own inference — no external LLM API key. Propose schema, extract nodes, and relate them via emit-work/ingest.
model: sonnet

allowed-tools:
  - Read
  - Bash
  - Write
  - Edit

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: cartridge-governance
  raise.prerequisites: "scaffolded cartridge with corpus (rai-corpus-curate → init --from-curation)"
  raise.next: "verify (graph build)"
  raise.gate: "schema review before extraction"
  raise.adaptable: "true"
  raise.version: "3.1.0"
  raise.inputs: |
    - cartridge_name: text, required
  raise.outputs: |
    - cartridge instances: .raise/cartridges/{name}/instances/*.json
  raise.visibility: public
---

# Cartridge Agent (key-less build)

## Purpose

Build a Knowledge Cartridge with the inference of the agent already driving the
CLI — **no external API key**. This is the community-tier counterpart of
`/rai-kc-build` (which calls OpenRouter). The deterministic pipeline (chunking,
validation, hygiene, edge materialization, embeddings) stays in `raise_core`;
only the generative steps (propose schema, extract nodes, relate) run on the
local agent via emit-work/ingest.

## Mastery Levels (ShuHaRi)

- **Shu**: Show proposed schema + each extraction, confirm
- **Ha**: Propose schema, confirm once, run extraction + relate
- **Ri**: Propose → present schema → run extract + relate → report

## Context

**When to use:** The `cartridge-governance` phase of the `upgrade` pipeline, or
any key-less cartridge build.

**When to skip:** An API key is configured and batch/unattended extraction is
preferred → use `/rai-kc-build` instead.

**Inputs:** A cartridge already scaffolded with a corpus and `GraphNode` schema
(produced by `/rai-corpus-curate` → `rai cartridge init --from-curation`).

## Steps

### Step 1: Verify the scaffolded cartridge

```bash
ls .raise/cartridges/{cartridge_name}/CARTRIDGE.yaml || echo "MISSING"
```

| Result | Action |
|--------|--------|
| Manifest with corpus + GraphNode schema | Continue |
| Missing / no corpus | Stop: run `/rai-corpus-curate` first |

### Step 2: Propose the schema (local inference — no API)

Read a sample (first ~40 lines) of each corpus doc. From the content, propose:
- **3–8 node types** (e.g. requirement, guardrail, principle, decision,
  component) — names in kebab-case.
- **2–6 relationship types** with one-line descriptions.
- A few **competency questions** the cartridge should answer.

Write the extractor config and schema yourself (this replaces the OpenRouter
`corpus_analyzer` step):
- `extractors/config.yaml` — one spec per node type, each with `type: agent`,
  `sources` = the cartridge corpus globs, `schema_ref:
  extractors/schemas/relationships.yaml`, `relationship_mode: guided`.
- `extractors/schemas/relationships.yaml` — the proposed `relationship_types`.

**Present the proposed schema and confirm** before extracting (quality gate).

### Step 3: Extract nodes (emit-work → fill → ingest)

```bash
rai cartridge extract {cartridge_name} --emit-work
```

For each `.agent-work/*.work.json`, read its `prompt` and write the JSON node
list to the sibling `.result.json` using your own inference. Then:

```bash
rai cartridge ingest {cartridge_name}
```

Report nodes extracted (per type) and any warnings.

### Step 4: Relate (second pass — one-time quality)

```bash
rai cartridge relate {cartridge_name} --emit-work
```

Fill `.agent-work/relationships.result.json` with `{"relationships": [{source,
target, type}]}` over the full node inventory — link across sections/types,
using only existing node ids and schema types. Then:

```bash
rai cartridge relate {cartridge_name} --ingest
```

### Step 5: Report

```
## Cartridge {cartridge_name} (agent-native, no API key)
Nodes: {N} ({by type})
Relationships: {M} attached
Next: verify — rai graph build
```

**STOP HERE.** Return your summary to the orchestrator.

## Output

| Item | Destination |
|------|-------------|
| Schema | `extractors/config.yaml` + `extractors/schemas/relationships.yaml` |
| Instances | `.raise/cartridges/{name}/instances/*.json` |
| Next | verify (`rai graph build`) |

## Quality Checklist

- [ ] No external API key used — all generative steps via local agent
- [ ] Schema reviewed before extraction
- [ ] Extraction via emit-work/ingest (not the OpenRouter extractor)
- [ ] Relationship pass run (one-time quality for the migration)

## References

- API/batch variant: `/rai-kc-build`
- Prereq: `/rai-corpus-curate`
- Engine: `raise_core/cartridges/agent_extract.py`, `relate.py`
