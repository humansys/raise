---
name: rai-docs-update
description: Sync module docs with knowledge graph. Use when architecture docs drift.
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: per-story
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.1.1"
  raise.visibility: public
---

# Docs Update

## Purpose

Close the coherence loop between code and architecture docs. Compare knowledge graph truth against module doc frontmatter, update drifted fields, and optionally refresh narrative sections. Since 2.1.0 (S15884.2), this also drives Layer 2 — synthesizing a `flowchart TD` C4-shaped diagram + narrative per module into a delimited `rai:auto` region (ADR-146), gated through the same HITL review as the rest of this skill.

No LLM call happens inside `raise_cli` — the CLI layer (`rai docs architecture ...`) only assembles input, validates dialect, and writes/reads regions. Step 3.5 below is the one place synthesis happens: one agent turn, consuming a pre-packed bundle.

## Mastery Levels (ShuHaRi)

- **Shu**: Present every diff, ask before every change
- **Ha**: Batch frontmatter changes with single HITL gate, narrative only for structural changes
- **Ri**: Autonomous frontmatter updates, HITL only for narrative

## Context

**When to use:** After stories that changed code structure, during `/rai-story-close`, after discovery refresh.

**When to skip:** Stories that only changed tests/docs/non-code. No graph available.

**Inputs:** Knowledge graph (`.raise/rai/memory/index.json`), module docs (`governance/architecture/modules/*.md`).

## Steps

### Step 1: Build Graph & Identify Affected Modules

```bash
rai graph build
```

Read `.raise/rai/personal/last-diff.json` for changed modules. If no diff or no affected_modules, check all modules.

**Layer 2 work set (S15884.2):** for each module doc under `governance/architecture/modules/*.md` that carries a `rai:auto` region, compute the current bundle fingerprint and compare it to the region's stored `src`:

```bash
rai docs architecture bundle --module mod-{package}--{name} --format json   # inspect, or just diff via status:
rai docs architecture status
```

`{package}` is the doc's own `package:` frontmatter field (e.g. `raise-cli`, `raise-server`) — module ids are package-qualified since RAISE-16033, so `mod-{name}` alone will not resolve.

`rai docs architecture status` reports fresh/stale per doc without needing to hand-parse fingerprints. **Layer 2's work set = fingerprint-changed docs** — a subset of `affected_modules` above, since graph churn that does not change the semantic bundle (e.g. only volatile fields moved) is filtered out here, before any synthesis cost is incurred. Docs with no `rai:auto` region yet (the 22 pre-existing module docs) are eligible for first insertion — treat them as part of the work set too when their frontmatter-level `affected_modules` diff says they changed.

<verification>
Module list identified for comparison. Layer 2 work set (fingerprint-changed or first-insertion docs) identified separately from the frontmatter-only `affected_modules` list.
</verification>

### Step 2: Compare Frontmatter Per Module

Use `raise_graph_context` MCP tool with module_id="mod-{package}--{name}", `cwd="{project_or_worktree_path}"`. If MCP tools are not available, fall back to: `rai graph context mod-{package}--{name} --format json`

Compare doc-declared vs code-truth:

| Doc field | Graph truth | Comparison |
|-----------|------------|------------|
| `depends_on` | `code_imports` | Sort both, compare sets |
| `depended_by` | Reverse lookup from other modules | Computed |
| `public_api` | `code_exports` | Sort both, compare sets |
| `components` | `code_components` | Direct number |

**Fields the skill MUST NOT touch:** `purpose`, `constraints`, `status`, `entry_points`, `name`, `type`.

<verification>
Drifted fields identified per module.
</verification>

### Step 3: HITL Gate — Apply Frontmatter

Present drift report:
```
### mod-raise-cli--memory
  depends_on: [config] → [config, schemas]  (added: schemas)
  components: 30 → 34
```

Ask: "Apply frontmatter updates to N modules? [y/n/selective]"

Apply changes to YAML frontmatter only — preserve all other content and field ordering.

<verification>
Frontmatter updates applied (or skipped by user).
</verification>

### Step 3.5: Layer 2 Synthesis (NEW, S15884.2)

Runs *after* Step 3 so the bundle and frontmatter agree with each other. For each doc in the Layer 2 work set identified in Step 1:

1. **Read the bundle** — the entire synthesis input, one payload, no follow-up graph queries:
   ```bash
   rai docs architecture bundle --module mod-{package}--{name} --format json
   ```
2. **Synthesize in one turn** — a `flowchart TD` diagram using C4-shaped `subgraph` conventions (boundary = subgraph, element = node, relationship = labeled edge) plus a short narrative paragraph. This is the only LLM call in the entire pipeline (D-S2) — no multi-turn refinement, no per-node calls. `flowchart`+`subgraph` is the **only** allowed dialect; do not emit `C4Context`/`C4Container`/`C4Component`/`architecture-beta` — they are rejected by the next step and were never confirmed to render on all four targets (RAISE-15886 T4).
3. **Validate the dialect before writing anything:**
   ```bash
   rai docs architecture validate --stdin <<< "$SYNTHESIZED_MARKDOWN"
   ```
   A non-zero exit means the synthesis produced a disallowed dialect — retry synthesis in the same turn (re-shape the same content as flowchart), do not write rejected content.
4. **Check for hand-tampering before staging** — if this reports a content-hash mismatch, a human edited inside the region since the last run. Surface that warning in the Step 4 diff below rather than silently overwriting:
   ```bash
   rai docs architecture region check --file governance/architecture/modules/{name}.md
   ```
5. **Stage the write with `--dry-run`** — this computes the would-be diff (idempotent by construction: an unchanged bundle against an unchanged `src` stages as "unchanged", no write pending) but **writes nothing to disk**:
   ```bash
   rai docs architecture region write \
     --file governance/architecture/modules/{name}.md \
     --id c4-component --src <bundle-fingerprint-from-step-1> \
     --stdin --dry-run <<< "$SYNTHESIZED_MARKDOWN"
   ```

Region diffs produced here are staged only — `--dry-run` guarantees no code path in this step touches disk. They flow into Step 4's existing HITL gate as the diff to review, same as frontmatter and narrative changes. Step 4 issues the real (non-dry-run) `region write` call — that is the only point in the whole pipeline that commits generated content to disk.

<verification>
Work-set docs have a synthesized flowchart+narrative region diff staged via `--dry-run` (or skipped where the bundle was unchanged — the common case in steady state). Nothing written to disk yet.
</verification>

### Step 4: Narrative Review (if triggered)

**Trigger A (full review):** New/removed modules, major dependency changes (>2), significant API changes (>5).

**Trigger B (targeted scan):** For any frontmatter change, scan prose for stale hardcoded values (old counts, removed dependency names, removed API names). These are mechanical text fixes.

**Trigger C (region diffs, S15884.2):** Any `rai:auto` region staged in Step 3.5 via `--dry-run` — diagram inserted, replaced, or flagged with a hand-tampering warning. This is **the same HITL gate as Trigger A/B, not a second gate** — region diffs are bounded to one block per doc (ADR-146's whole point), so they are cheap to review alongside the mechanical text fixes.

Present proposed changes as diff — mechanical text fixes and the `--dry-run` region previews together. Ask: "Apply these changes? [y/n/selective]"

**Only after approval**, commit each approved region by re-running Step 3.5's exact command WITHOUT `--dry-run`:
```bash
rai docs architecture region write \
  --file governance/architecture/modules/{name}.md \
  --id c4-component --src <bundle-fingerprint-from-step-1> \
  --stdin <<< "$SYNTHESIZED_MARKDOWN"
```
This is the one and only point in the pipeline that calls `path.write_text` on a module doc for generated region content (AC8) — **no code path writes and publishes generated region content without this gate**: `--dry-run` in Step 3.5 never touches disk, and this call only runs after a human said yes.

<verification>
Narrative changes applied or no triggers found. Region diffs (if any) reviewed through this same gate, then committed to disk via the non-dry-run `region write` call — never before approval.
</verification>

### Step 5: Rebuild & Summarize

If any changes applied:
```bash
rai graph build
```

For each module updated in this run, re-publish to docs adapter:

Use `raise_docs_write` MCP tool with doc_type="architecture-module", title="{name}", content="existing governance/architecture/modules/{name}.md contents (updated)", output_path="governance/architecture/modules/{name}.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write architecture-module \
  --title "{name}" \
  --stdin \
  --output-path governance/architecture/modules/{name}.md << EOF
$(cat governance/architecture/modules/{name}.md)
EOF
```

Note: heredoc without quotes so `$(cat ...)` expands the updated file content.

**Pre-flight check (D-S7, AC11):** before publishing any doc whose body now contains a mermaid fence, verify the target Confluence space has the Mermaid macro app installed and licensed. If the capability check fails, stop with an actionable message — do not publish a page that will render as an unknown-macro error. This does not touch the `mermaid_macro=False` fallback branch (that stays a follow-up story); it only adds the pre-flight check in front of the existing hard-`True` publish path.

Present summary: modules checked, frontmatter updated, narrative updated, regions written, graph rebuilt.

<verification>
Graph reflects updated docs. Updated modules published via docs adapter (mermaid pre-flight passed). Coherence loop closed.
</verification>

### Step 6: Freshness Gate (NEW, S15884.2)

Close the loop by proving no doc was left stale:

```bash
rai gate check gate-docs-architecture-fresh
```

This is read-only and LLM-free (D-S4) — it recomputes each region's bundle fingerprint and compares to the stored `src`, nothing more. A failure here means a doc changed upstream (graph) after Step 3.5 ran, or Step 4's HITL gate rejected a region diff that Step 3.5 staged — either resolve by re-running from Step 1, or note the rejection and move on if the human explicitly declined the update.

<verification>
`gate-docs-architecture-fresh` passes (or its failure is understood and acknowledged — not silently ignored).
</verification>

## Output

| Item | Destination |
|------|-------------|
| Updated frontmatter | `governance/architecture/modules/*.md` (local) + docs adapter (type: architecture-module) |
| Narrative changes | `governance/architecture/modules/*.md` (with HITL) + docs adapter |
| Generated `rai:auto` regions (S15884.2) | `governance/architecture/modules/*.md`, delimited per ADR-146, with HITL via Step 4 |
| Freshness verdict | `rai gate check gate-docs-architecture-fresh` output |
| Summary | Displayed |

## Quality Checklist

- [ ] Graph built fresh before comparison (not stale data)
- [ ] Only machine-owned fields updated (depends_on, depended_by, public_api, components)
- [ ] Human-owned fields preserved (purpose, constraints, status, entry_points)
- [ ] HITL gate before any writes — present diff first (region diffs included, Trigger C)
- [ ] Graph rebuilt after changes to close coherence loop
- [ ] NEVER modify purpose or constraints without explicit human request
- [ ] Generated content lives ONLY inside `rai:auto` markers — never write body prose outside them (ADR-146)
- [ ] Synthesized diagrams are `flowchart TD` + `subgraph` only — never C4Context/Container/Component/architecture-beta (validated by `rai docs architecture validate`, not just discouraged here)
- [ ] `rai docs architecture region check` run before overwriting an existing region — hand-tampering warnings surfaced, not silently clobbered
- [ ] Region writes staged via `--dry-run` in Step 3.5 (no disk write) and committed via the same command WITHOUT `--dry-run` only after Step 4 approves
- [ ] `gate-docs-architecture-fresh` checked at the end (Step 6) — no doc left stale

## References

- ADR-025: Incremental Coherence — Graph Diffing and AI-Driven Doc Regeneration
- ADR-146: Machine-Owned Narrative Regions — delimiter format, idempotence, orphan handling
- Module docs: `governance/architecture/modules/*.md`
- Graph: `.raise/rai/memory/index.json`
- Graph context: Use `raise_graph_context` MCP tool with module_id="mod-{package}--{name}". If MCP tools are not available, fall back to: `rai graph context mod-{package}--{name} --format json`
- Layer 2 CLI surface: `rai docs architecture bundle|validate|status`, `rai docs architecture region write|check` — no LLM call anywhere under `packages/raise-cli/` (AC12); synthesis is Step 3.5's single agent turn
