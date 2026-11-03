---
name: rai-corpus-curate
description: Discover and curate a project's documents into a governance corpus — classify by relevance, drop noise, confirm with the developer before extraction.
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
  raise.fase: curate-corpus
  raise.prerequisites: "project with documents (governance/, docs/, dev/decisions/, .raise/docs/ legacy)"
  raise.next: "rai-kc-build (governance cartridge)"
  raise.gate: "HITL corpus confirmation before extraction"
  raise.adaptable: "true"
  raise.version: "3.1.0"
  raise.inputs: |
    - project_path: path, required
    - cartridge_name: text, optional (defaults to {project}-governance)
  raise.outputs: |
    - corpus_curation: file_path (work/upgrade/corpus-curation.yaml)
  raise.visibility: public
---

# Corpus Curate

## Purpose

Decide WHICH documents become governance knowledge — before spending any
extraction. Discovery alone (path globbing) over-includes raw material
(transcripts, logs) and misses docs in odd places. This skill reads each
candidate, classifies it by governance relevance, and confirms the corpus with
the developer. The quality of the resulting cartridge is bounded by what enters
the corpus, so this gate matters most on a one-time upgrade.

## Mastery Levels (ShuHaRi)

- **Shu**: Show every candidate + classification, confirm each group
- **Ha**: Present grouped table, confirm once
- **Ri**: Classify, present the table, accept default selection unless told otherwise

## Context

**When to use:** Before building a governance cartridge — the `curate-corpus`
phase of the `upgrade` pipeline, or standalone before `/rai-kc-build`.

**When to skip:** A curated `corpus-curation.yaml` already exists and the docs
have not changed.

**Inputs:** Project root with documents. Optional cartridge name.

## Steps

### Step 1: Discover candidates (no LLM — cheap)

Prune vendored + agent-tooling dirs at any depth (`node_modules .venv .git
.raise .claude .hermes .agent .roo .windsurf .cursor .github`), match doc
locations by prefix (`governance|docs|architecture|work/docs|dev/decisions|
specs|wiki`), and ALSO include the v2.x legacy `.raise/docs/`. Skip empty RaiSE
templates (marker `fill with /rai-project-{create,onboard}` + <60 lines). Emit
each surviving path with its non-blank line count. (Same discovery as
`rai-project-upgrade` Step 5a, plus `.raise/docs/`.)

<verification>
A list of candidate doc paths (with line counts); empty RaiSE templates excluded.
</verification>

### Step 2: Classify by governance relevance (L1 — agent inference, no API key)

For EACH candidate, read the head of the file (title + first ~30 lines) and
assign exactly one class. Use your own inference — this is the agent-native
step, no external key required.

| Class | Includes | Goes to corpus? |
|-------|----------|-----------------|
| `governance` | vision, PRD, requirements, guardrails/standards, ADRs/decisions, architecture, policy, process, runbooks | **Yes** |
| `reference` | API docs, library/tooling reference, how-to guides | No (default) |
| `raw-source` | transcripts, chat/WhatsApp logs, meeting notes, raw requirement dumps | No (default; may opt in as context) |
| `noise` | changelogs, TOC, boilerplate, generated indexes | No |

Also infer a `node_type_hint` for each `governance` doc (guardrail, requirement,
principle, decision, component, …) to seed the extractor config later.

<verification>
Every candidate has exactly one class and, when `governance`, a node_type_hint.
</verification>

### Step 3: Present + confirm (HITL — the gate)

Present a grouped table: governance (selected), reference / raw-source / noise
(deselected). Show counts and let the developer:
- confirm the governance set,
- promote specific `raw-source`/`reference` docs into the corpus,
- drop any false-positive governance doc.

**Shu/Ha/Ri all pause here** — corpus selection determines cartridge quality and
gates the extraction spend.

```
## Corpus curation: {N} candidates
GOVERNANCE (→ corpus): {n}
  governance/guardrails.md        [473]  → guardrail
  dev/decisions/adr-001.md         [27]  → decision
  ...
REFERENCE (excluded): {n}
RAW-SOURCE (excluded — promote?): {n}
  docs/sources/whatsapp-log.md     [77]
NOISE (excluded): {n}

Confirm corpus? (enter to accept, or list paths to add/drop)
```

### Step 4: Write the curation artifact

Write `work/upgrade/corpus-curation.yaml`. Corpus paths are relative to the
cartridge directory (`.raise/cartridges/{cartridge}/`), i.e. prefixed to climb
back to the project root, so the cartridge `build`/`extract` resolves them.

```yaml
cartridge: {cartridge_name}
curated:
  - path: ../../../governance/guardrails.md
    classification: governance
    node_type_hint: guardrail
  - path: ../../../dev/decisions/adr-001.md
    classification: governance
    node_type_hint: decision
excluded:
  - path: docs/sources/whatsapp-log.md
    classification: raw-source
    reason: input material, not governance
```

### Step 5: Materialize the cartridge from the curation (bridge)

Turn the curated list into a ready-to-build cartridge in one call — this is the
curate→cartridge bridge, and it sets the corpus paths AND the `GraphNode` schema
so the next phase's `build`/`extract` work with no manual manifest edits:

```bash
rai cartridge init {cartridge_name} --from-curation work/upgrade/corpus-curation.yaml
```

Commit the artifact and the scaffolded cartridge:

```bash
git add work/upgrade/corpus-curation.yaml .raise/cartridges/{cartridge_name}/
git commit -m "upgrade(curate): governance corpus — {n} docs kept, {m} excluded

Co-Authored-By: Rai <rai@humansys.ai>"
```

**STOP HERE.** Return your summary to the orchestrator. The next phase
(`/rai-kc-build`) builds + extracts the now-scaffolded `{cartridge_name}`.

## Output

| Item | Destination |
|------|-------------|
| Curated corpus | `work/upgrade/corpus-curation.yaml` |
| Next | `/rai-kc-build` (governance cartridge) |

## Quality Checklist

- [ ] Vendored/agent dirs pruned; legacy `.raise/docs/` included
- [ ] Empty RaiSE templates skipped
- [ ] Every candidate classified by content, not just location
- [ ] raw-source / reference / noise excluded by default
- [ ] Developer confirmed the corpus before extraction (HITL)
- [ ] Corpus paths prefixed for cartridge-dir resolution

## References

- Next: `/rai-kc-build`
- Pipeline: `upgrade.yaml` phase `curate-corpus`
- Extraction engine: `raise_core/cartridges/extract.py`, `corpus_analyzer.py`
