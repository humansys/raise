---
name: rai-story-design
description: Create lean story spec for human review and AI alignment. Use before story plan.
model: opus

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "4"
  raise.prerequisites: project-backlog
  raise.next: story-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.5.0"
  raise.visibility: public
  raise.output_type: story-design
  raise.inputs: |
    - story_md: file_path, required, previous_skill
    - scope_md: file_path, optional, previous_skill
  raise.outputs: |
    - design_artifact: artifact_store, primary
    - design_md: file_path, rendered_view
  raise.aspects: introspection
  raise.introspection:
    phase: story.design
    context_source: scope doc
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 5
    tier1_queries:
      - "patterns for {affected_modules} design decisions"
      - "prior designs for similar scope in {phase}"
      - "risks and lessons from related epics"
raise.mastery:
  shu: "Follow all steps, include examples for every story"
  ha: "Adjust depth to complexity, but never skip the gemba walk"
  ri: "Custom spec patterns for specialized domains"
---

# Story Design

## Purpose

Create a lean story specification optimized for both human review (clear intent) and AI alignment (accurate code generation).

## Mastery Levels (ShuHaRi)

See `raise.mastery` in frontmatter.

## Context

**When to use:** Before planning ANY story. Design is never optional — it is the gemba walk that prevents duplicate components, wasted effort, and wrong approaches.

**Inputs:** Story from backlog, User Story artifact (`story.md` from `/rai-story-start`), epic scope/design documents.

## Steps

### PRIME — HARD CONSTRAINT (blocks all subsequent work)

**FORBIDDEN:** You MUST NOT use grep, find, Glob, or Read to explore code UNTIL you have executed at least one `rai graph query`. Your first queries are this skill's tier1 queries (frontmatter `raise.introspection.tier1_queries`) — run them now using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, or the CLI fallback:
```bash
rai graph query "{query}"
```
0 results is valid — the constraint lifts when the queries have run, not when they return results.

**Report:** In your final output, list every graph query you executed and its result count.

Then, before Step 1:

1. **Code orientation**: Load SA-ranked code symbols for the current branch using the `raise_session_context` MCP tool with sections="code_context", `cwd="{project_or_worktree_path}"`.
   If MCP tools are not available, fall back to:
   ```bash
   rai session context -s code_context -p .
   ```
   Returns ~20 symbols ranked by structural proximity to active work modules. Empty result is valid — branch name may not match any module. Use these symbols as starting points for code exploration, not as exhaustive scope.
2. **Backlog transition** — engine owned (RAISE-15034):
   Transition to design status is performed by the pipeline engine via `apply_phase_transition`.
   No skill-initiated transition call required or allowed.
   **Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

### Step 1: Assess Complexity

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| Components | 1-2 | 3-4 | 5+ |
| Story points | <5 | 5-8 | >8 |
| External integrations | 0-1 | 2-3 | 4+ |
| Algorithm complexity | Trivial | Custom logic | Novel |

| Result | Action |
|--------|--------|
| Simple | Lean design — core sections, quick gemba walk |
| Moderate | Core sections + examples |
| Complex | Full spec with all sections |

> **JIT**: Before assessing complexity, query graph for patterns from similar stories
> → `aspects/introspection.md § JIT Protocol`

**Risk gate:** If story is marked HIGH RISK in epic scope, discuss risks before designing — name concerns, failure modes, and scope boundaries.

**UX gate:** If story touches human interaction (workflows, prompts, DX), recommend `/rai-research` first (~10 min).

**Integration gate:** If story name includes "dogfood", "E2E", or "integration", OR if epic has separate client/server stories developed with mocks — AC MUST include at least one scenario that runs with **real infrastructure** (docker compose, actual DB, real HTTP calls). Unit tests with mocks cannot catch cross-component contract mismatches (auth headers, payload validation, parameter limits).

**Frontend DoR gate** (`is_frontend=true` only — skip for backend-only stories): Every screen referenced by this story (`screen_refs`) must be present in the prototype / living-design-system (`prototype_screens`). Formally: `screen_refs ⊆ prototype_screens`. If any referenced screen is absent, the story is **NOT ready** — extend the prototype first (add the missing screen faithful to existing tokens/components), then return to design. This is a lightweight DoR in Mike Cohn's sense ("sufficiently far along, not done") — **not** a pixel-final stage-gate and **not** BDUF. Skill-prose only; no new CLI verbs per ADR-125 / RAISE-10923.

> **Example (E11478):** S5 (analytics dashboard) references the `dashboard` screen — that screen exists in the prototype → **ready**, proceed. S4 (subscription apply flow) references the `apply` screen — that screen is **not yet** in the prototype → **NOT ready**; extend the prototype with the apply screen first, then re-evaluate S4.

<verification>
Complexity assessed. Risk/UX/Integration/Frontend-DoR gates evaluated.
</verification>

### Step 2: Gemba Walk (mandatory — do not skip)

Go to the actual code. Design without reading the code is guessing.

1. **Read what exists**: Open and read the files/modules that this story will touch. Understand the current state before proposing changes.
2. **Search for duplicates**: Grep for similar functionality, components, or patterns that already exist. Before creating anything new, verify it doesn't exist already.
3. **Check best practices**: Look at how similar problems are solved in the codebase. Follow established patterns rather than inventing new ones.
4. **Map dependencies**: Identify what depends on the code you'll change, and what the changed code depends on.
5. **Legacy sweep (mandatory)**: If this story introduces a V2 of something — new class, new module, new pattern that supersedes an existing one — answer **in the design doc** the question *"what V1 becomes orphaned when V2 lands?"*. Three valid answers: (a) *"nothing — this is net-new"* (state it explicitly); (b) *"V1 at `file:line` — deletion plan is X"* (commit-level plan included); (c) *"V1 coexists because Y"* (explain why keeping V1 is correct). No implicit answers. This exists because RCA s2092.1 showed refactors cierran declarados done sin barrer V1 (R1/R3/R5 · pattern `refactor-declared-done-without-sweep`).

```bash
# Example gemba commands
grep -r "similar_function" packages/  # Does this already exist?
grep -r "class SimilarModel" packages/ # Duplicate models?
```

> **JIT**: For deeper code exploration beyond the orientation map, use the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"` or fall back to CLI:
> ```bash
> rai graph query "symbol_name" --types symbol --limit 10
> rai graph query "module_name" --module mod-raise-cli--session
> rai graph query "callers of function_name" --types symbol
> ```
> Use `--file path/to/file.py` to scope results to a specific file.

**Portfolio context** — fail-open:

```bash
rai portfolio suggest "$JIRA_KEY" 2>/dev/null || true
```

If the command produces output, add a `## Portfolio Context` section to the design doc with the raw output — include `components_touched` and `change_mode` to cross-check the gemba walk findings. If the story has no portfolio profile (empty output), retry with the parent epic key:

```bash
rai portfolio suggest "$EPIC_KEY" 2>/dev/null || true
```

If neither call produces output, continue without portfolio context — do not block.

| Finding | Action |
|---------|--------|
| Similar component exists | Reuse or extend it — do NOT create a duplicate |
| No established pattern | Document the new pattern as a design decision |
| Multiple approaches found | List them in Step 4 with trade-offs |

**Drift Risk Check** — for each module this story will touch:

1. If `governance/drift-hotspots.json` exists: check if the module appears in the top-10 ranked modules — note rank and signal count.
2. Check `governance/drift-catalog.md` §1 (AG1–AG6): does the story scope risk any of these?
   - **AG4** (context-window planning): does the change fan out across >3 modules with unresolved coupling edges?
   - **AG2** (clone amplification): are you duplicating logic that exists elsewhere?
3. Flag risks in this design doc's Approach section as signals — not blockers. "No drift risk identified" is always valid.

Graceful degradation: if `governance/drift-hotspots.json` is absent, skip step 1 silently and proceed to step 2.

<verification>
Code has been read. No duplicate components will be created. Existing patterns identified. Legacy sweep answered explicitly in design doc. Drift risk checked (hotspots rank noted if available; AG4/AG2 assessed).
</verification>

### Step 3: Frame What & Why (informed by gemba)

Load `story.md` (from `/rai-story-start`) if it exists — use its User Story as starting frame.

Read `governance/prd.md` and `governance/vision.md` (graceful degradation: if absent or placeholder-only, continue without blocking). Problem and Value must be consistent with PRD requirements and Vision outcomes when those documents have content.

> **JIT**: Before framing problem and value, query graph for prior designs with similar scope
> → `aspects/introspection.md § JIT Protocol`

- **Problem**: What gap does this fill? (1-2 sentences)
- **Value**: Why does this matter? (1-2 sentences, measurable or observable)

<verification>
Can explain to non-technical stakeholder in 30 seconds.
</verification>

### Step 4: Describe Approach (lean principles)

> **JIT**: Before describing approach, query graph for implementation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Document WHAT you're building and WHY this approach (not detailed HOW):
- Solution approach (1-2 sentences)
- Components affected (list with change type: create/modify/delete)

**Lean design gates** — challenge every component before committing:

- **KISS**: Is this the simplest approach that works? If not, simplify.
- **DRY**: Does this duplicate logic that exists elsewhere (gemba walk should have found it)?
- **YAGNI**: Are you building for a real requirement or a hypothetical one? Cut speculative features.
- **MVP**: What is the smallest version that delivers the value from Step 3? Build that, not more.

**For refactoring:** grep all call sites of the target. A half-migration is worse than none.

**For data mutations:** What happens when inputs reference missing entities? Declare the strategy explicitly: reject with error, skip + report count, partial success with warnings. Silent drops are semantic bugs.

**Storage migration gate:** If this story replaces a storage mechanism (file → SQLite, JSON → DB, YAML → table), answer for every public function of the replaced module: *"What did callers get on (a) missing data and (b) corrupt data before? What will they get after?"* Common silent contract breaks:
- `FileNotFoundError` → empty result (callers catching the exception silently get nothing)
- `ValueError`/`JSONDecodeError` → `ValidationError` (callers expecting `None` on corrupt data now get an exception)
- File mtime → no equivalent (staleness checks break silently)

Declare the contract explicitly in the Approach section and add an AC for each broken contract you identify. Skip this gate if the story does not replace a storage mechanism.

Also run — advisory ⚠ if stale or missing:

```bash
rai schema sum check
```

If stale, update:

```bash
rai schema sum update
```

**Schema version coordination check:** If this story adds a `_V{N}_DDL` migration, verify that the next version number is not already taken by the dev branch:

```bash
# Current branch version
grep "^SCHEMA_VERSION" packages/raise-cli/src/raise_cli/storage/schema.py

# Dev branch version — RAISE-17066: declared, never inferred — CI env > registered worktree target > manifest. Fail loud.
DEV_BRANCH="${RAISE_DEVELOPMENT_BRANCH:-$(rai worktree context --field merge_target 2>/dev/null || true)}"
[ -n "$DEV_BRANCH" ] || DEV_BRANCH="$(rai manifest env | python3 -c "import json,sys; print(json.load(sys.stdin)['branches']['development'])")"
[ -n "$DEV_BRANCH" ] || { echo "ERROR: cannot resolve target branch — set branches.development in .raise/manifest.yaml"; exit 1; }
git show "${DEV_BRANCH}:packages/raise-cli/src/raise_cli/storage/schema.py" | grep "^SCHEMA_VERSION"
```

If the two versions diverge (feature branch has V18, dev branch already at V19), assign migrations starting from `max(both) + 1`. Document the chosen version in the design. Skipping this check when branches diverge causes migration number collisions at merge time — a ~30 min fix that cannot be automated away.

**Value preservation gate:** Before finalizing components, ask: "What domain knowledge does this layer provide that a generic pass-through wouldn't?" If the answer is "none", the design may be over-abstracted. If the answer involves config/resolution/mapping that an existing pattern handles differently, check where that responsibility lives in the proven pattern.

**Supply Chain Gate** — For each NEW external dependency introduced by this story, evaluate supply chain health before committing:

- **PyPI version history** — stable releases? frequent yanks?
- **Download count** — established package or niche?
- **Last release date** — actively maintained?
- **Maintainer count** — bus factor (single point of failure)?
- **Yank history** — has this package had yanked versions in the past?
- **Alternative evaluation** — can we implement this ourselves in <50 LOC? Is there a lighter alternative?
- **Isolation strategy** — is the dependency confined to a single module, or does it leak across the codebase?

Document findings in the design doc's Approach section. This is a guide, not a hard block — an informed risk decision is valid.

**Skip rule:** Well-known, widely-adopted packages (pydantic, fastapi, pytest, requests, httpx, typer, rich, click, and similar) are N/A — their supply chain health is already established. Use human judgment for the boundary.

> See pattern BASE-056: *Consumer reputation ≠ package stability — verify supply chain independently* (will be registered in RAISE-586).

For complex stories, add: scenarios (Gherkin), algorithm pseudocode, constraints, testing strategy.

<verification>
Approach is concrete enough to envision examples. Value preservation gate passed.
</verification>

### Step 5: Create Examples (MOST IMPORTANT)

**This section drives AI code generation accuracy more than any other.**

Provide concrete, runnable examples:
1. **API/CLI usage** — how the story is invoked
2. **Expected output** — success + error cases
3. **Data structures** — key models, schemas, types

Use concrete values (not placeholders), correct syntax (not pseudocode), consistent with codebase style.

<verification>
Examples are concrete, runnable, and cover success + error paths.
</verification>

<if-blocked>
Can't envision examples → approach not concrete enough, return to Step 3.
</if-blocked>

### Step 6: Define Acceptance Criteria

> **JIT**: Before defining acceptance criteria, query graph for testing patterns and quality standards
> → `aspects/introspection.md § JIT Protocol`

If `story.md` has Gherkin AC, reference them here — refine, don't duplicate. If no `story.md`, define from scratch:

- **MUST**: Required for completion (3-5 items, specific and testable)
- **SHOULD**: Nice-to-have (1-3 items)
- **MUST NOT**: Explicit anti-requirements

All criteria must be observable outcomes traceable to value from Step 2.

<verification>
Criteria are specific, testable, and traceable. Spec reviewable in <5 minutes.
</verification>

## Output

After completing all steps, persist the design to the artifact store and render a Markdown view:

### 1. Emit structured artifact (primary — canonical source)

Call `raise_artifact_emit` with the design content as structured JSON. The artifact store is the source of truth.

```
raise_artifact_emit(
    artifact_type="design",
    story_id="{story_id}",
    content=<JSON string with fields: problem, value, approach, components, decisions,
             acceptance_criteria, examples, complexity, dependencies, legacy_sweep,
             drift_risks, testing_strategy, open_questions>
             cwd="{project_or_worktree_path}"
)
```

Field reference for the `content` JSON:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `problem` | string | yes | What gap does this fill |
| `value` | string | yes | Why it matters (measurable) |
| `approach` | string | yes | Solution approach |
| `components` | list of `{name, change, purpose}` | yes | Files affected (`change`: create/modify/delete) |
| `decisions` | list of `{id, title, rationale, body?}` | yes | Design decisions (body for extended rationale) |
| `acceptance_criteria` | list of `{id, description, severity?, verifiable?, test_link?}` | yes | `severity`: must (default), should, must_not |
| `examples` | list of `{title, language?, code, explanation?}` | no | Concrete runnable examples |
| `complexity` | "simple" / "moderate" / "complex" | no | From Step 1 assessment |
| `dependencies` | list of `{description, blocks?}` | no | What this story depends on |
| `legacy_sweep` | string | no | What V1 becomes orphaned (mandatory answer from Step 2) |
| `drift_risks` | list of `{id, description, mitigation?}` | no | From drift risk check in Step 2 |
| `testing_strategy` | list of `{layer, name, purpose}` | no | Key test scenarios |
| `open_questions` | list of strings | no | Questions deferred to plan phase |

**Note:** The CLI fallback for artifact emission was removed in v3.0.0. MCP tool `mcp__rai-workspace__raise_artifact_emit` is required (primary path above). If MCP is unavailable, skip structured artifact emission.

### 2. Render Markdown view (derived — for human review)

Publish rendered Markdown via CLI for human readability, git diff, and Confluence:

Use `raise_docs_write` MCP tool with doc_type="story-design", title="S{N}.{M}: {story-name} design", content="[rendered Markdown from artifact store content]", output_path="work/epics/e{N}-{name}/stories/s{N}.{M}-design.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `Story design write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write story-design \
  --title "S{N}.{M}: {story-name} design" \
  --stdin \
  --output-path work/epics/e{N}-{name}/stories/s{N}.{M}-design.md << 'EOF'
[rendered Markdown from artifact store content]
EOF
```
**If exit code != 0, stop immediately** — do not proceed.

The Markdown file is a **rendered view**, not the source of truth. It is generated from the artifact content. If the artifact store and the file ever diverge, the artifact store wins.

### 3. Emit lifecycle signal

| Item | Destination |
|------|-------------|
| Design artifact | SQLite artifact store (primary) |
| Design Markdown | `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` (rendered view) |
| Signal | WorkLifecycle event emitted (start on entry, complete here) |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] NEVER over-specify HOW — trust AI for implementation details
- [ ] NEVER skip examples — they are the most important section
- [ ] Supply chain risk evaluated for new external dependencies (or N/A)

## References

- Next: `/rai-story-plan`
- Risk assessment: design is not optional
- UX research gate: `/rai-research` before UX stories
- Value preservation gate: domain intelligence over abstraction
