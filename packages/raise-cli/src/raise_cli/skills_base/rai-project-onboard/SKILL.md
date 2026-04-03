---
name: rai-project-onboard
description: >
  Guide brownfield project onboarding through discovery and conversation. Analyzes
  existing codebase, detects conventions, fills governance templates with discovered
  and conversational content, and builds the knowledge graph. Use after rai init --detect
  on an existing project.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: "rai init --detect"
  raise.next: "session-start"
  raise.gate: "4-dimensional coverage gate"
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.inputs: |
    - project_root: path, required, argument
  raise.outputs: |
    - governance_docs: file_path[] (governance/*.md)
    - knowledge_graph: file_path (.raise/rai/memory/index.json)
  raise.visibility: public
---

# Project Onboard

## Purpose

Guide brownfield project onboarding by combining codebase discovery with conversation. Analyze what exists, ask what code can't tell us, fill 6 governance templates. Gate: 4-dimensional coverage check.

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through every step, show discovery results, confirm each doc
- **Ha**: Run discovery, present summary, collect gaps in one exchange
- **Ri**: Discovery + 1 exchange + write all docs + build graph

## Context

**When to use:** After `rai init --detect` on an existing project with source code.

**When to skip:** Greenfield project → `/rai-project-create`. Not initialized → `rai init --detect` first. Governance already filled.

**Key difference from `/rai-project-create`:** Starts from WHAT EXISTS (discovery), then asks WHY. Create starts from WHAT YOU WANT.

**Inputs:** Project with `rai init --detect` completed, existing codebase.

## Steps

### Step 1: Verify Prerequisites

```bash
ls .raise/manifest.yaml 2>/dev/null || echo "MISSING"
ls governance/prd.md governance/vision.md governance/guardrails.md 2>/dev/null | wc -l
grep -ciE "must-|should-" governance/guardrails.md 2>/dev/null || echo "0"
```

| Result | Action |
|--------|--------|
| Manifest + 6 files + conventions detected | Continue |
| No manifest | Stop: "Run `rai init --detect` first." |
| No conventions in guardrails | Suggest re-running with `--detect` flag |
| No source code | Suggest `/rai-project-create` instead |

<verification>
Manifest exists, governance templates exist, conventions detected.
</verification>

### Step 2: Run Discovery

If `/rai-discover` has not been run yet (no `work/discovery/components-validated.json`), run it now. It handles the full pipeline: detect → extract → describe → document → build graph.

If already run, skip to Step 3 — discovery data is available.

Also auto-read existing project documentation (README, ARCHITECTURE, CONTRIBUTING, etc.) to pre-populate governance fields. No need to ask — always read what's available.

<verification>
Discovery complete. Existing docs read.
</verification>

### Step 3: Fill Governance Gaps

Present what discovery + docs already covered. Ask ONLY for unfilled fields:
- **Vision:** description, who uses it, why it exists
- **Capabilities:** 3-5 core things it does → 5-8 RF-XX requirements
- **Architecture gaps:** external actors/systems, interfaces, branch model

<verification>
All governance fields covered (from discovery + docs + conversation).
</verification>

### Step 4: Write 6 Governance Docs

Same parser contracts as `/rai-project-create`:
- `vision.md`: `| **{Bold Name}** | {description} |`
- `prd.md`: `### RF-XX: Title`
- `guardrails.md`: MERGE detected conventions (don't overwrite), YAML frontmatter `type: guardrails`
- `backlog.md`: `# Backlog: {name}`, `| E{N} | ... |`
- `system-context.md`: external interfaces table
- `system-design.md`: components from DISCOVERED modules (enriched by discovery)

Update `.raise/manifest.yaml` with branch configuration.

<verification>
All 6 docs written. Detected conventions preserved in guardrails.
</verification>

### Step 5: 4-Dimensional Coverage Gate

```bash
rai graph build
```

| Gate | Check | Pass criteria |
|------|-------|---------------|
| G1: Governance structure | Parser-extractable content per doc | ≥2 outcomes, ≥3 RF-XX, ≥3 guardrails, ≥1 epic |
| G2: Module coverage | Discovered modules in governance | ≥80% modules referenced |
| G3: Doc coverage | Docs read → governance elements | 100% of docs read contributed |
| G4: Traceability | Guardrails→RF-XX, RF-XX→body text | ≥80% linked |

Present gate results. If PARTIAL (1-2 items): fix specific items. If FAIL: fix docs, rebuild.

<verification>
All 4 gate dimensions pass (or user accepts documented exceptions).
</verification>

### Step 6: Summary

```
## Project Onboarded: {project_name}
Discovery: {N} modules, {N} components, {N} conventions
Governance: {N} outcomes, {N} requirements, {N} guardrails, {N} epics
Graph: {total} governance nodes
Next: /rai-session-start
```

## Output

| Item | Destination |
|------|-------------|
| Governance docs | `governance/` (6 files) |
| Knowledge graph | `.raise/rai/memory/index.json` |
| Next | `/rai-session-start` |

## Quality Checklist

- [ ] Discovery run before asking questions (code-first, not conversation-first)
- [ ] Existing docs checked before asking user (minimize redundant questions)
- [ ] Detected conventions MERGED into guardrails (not overwritten)
- [ ] Parser contracts followed exactly (same as `/rai-project-create`)
- [ ] 4-dimensional gate checked (not just node count)
- [ ] NEVER overwrite `guardrails.md` conventions from `--detect`

## References

- Prerequisite: `rai init --detect`
- Sibling: `/rai-project-create` (greenfield)
- Discovery: `/rai-discover` (unified pipeline)
- Parser sources: `src/raise_cli/governance/parsers/*.py`
- Next: `/rai-session-start`
