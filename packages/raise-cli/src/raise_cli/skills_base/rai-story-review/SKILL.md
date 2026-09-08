---
name: rai-story-review
description: Extract learnings and persist patterns from completed story. Use after implementation.
model: opus

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "7"
  raise.prerequisites: story-implement
  raise.next: story-close
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.6.0"
  raise.visibility: public
  raise.inputs: |
    - tests_passing: boolean, required, cli
  raise.outputs: |
    - retrospective_md: file_path, next_skill
    - patterns: list, cli
  raise.aspects: introspection
  raise.introspection:
    phase: story.review
    context_source: all story artifacts
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "evaluation patterns for {affected_modules}"
      - "process patterns from recent stories"
      - "related work items for {story_key} --types backlog"
raise.mastery:
  shu: "Follow all steps, answer all checkpoint questions with specific examples"
  ha: "Adapt depth to story complexity, batch small story reviews"
  ri: "Custom review patterns, integrate with team retrospectives"
---

# Story Review

## Purpose

Reflect on the completed story to extract learnings, persist patterns, reinforce behavioral signals, and emit calibration telemetry.

## Mastery Levels (ShuHaRi)

See `raise.mastery` in frontmatter.

## Context

**When to use:** After implementation is complete and tests pass. Before `/rai-story-close`.

**Inputs:** Completed story, progress log, passing test suite.

## Steps

### PRIME — HARD CONSTRAINT (blocks all subsequent work)

**FORBIDDEN:** You MUST NOT use grep, find, Glob, or Read to explore code UNTIL you have executed at least one `rai graph query`. Your first queries are this skill's tier1 queries (frontmatter `raise.introspection.tier1_queries`) — run them now using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, or the CLI fallback:
```bash
rai graph query "{query}"
```
0 results is valid — the constraint lifts when the queries have run, not when they return results.

**Report:** In your final output, list every graph query you executed and its result count.

### Step 1: Verify Tests Pass

Trust the end-of-story scoped gate from `/rai-story-implement` Step 5 — do **not** re-run
the full suite here. Review requires that scoped gates passed; after `/rai-mr-create`
synchronizes and admits the branch, GitLab selects and runs integration jobs.

```bash
# Confirm the implement-complete signal was emitted for the current HEAD
rai signal query story "{story_id}" --event complete --phase implement \
  --session-id "${RAISE_CC_SESSION_ID}" --latest --fields commit 2>/dev/null
```

| Condition | Action |
|-----------|--------|
| Signal found for current HEAD | ✓ Tests already verified — continue |
| Signal missing or stale commit | Run scoped package gate: `rai gate check gate-tests --scope packages/<pkg>/` |
| Scoped gate fails | Fix before reviewing — review requires green tests |

<verification>
Implement-complete signal confirmed for current HEAD (or scoped gate re-run and passing).
</verification>

### Step 1a: Architecture Review Checklist & Attestation

Run the AR checklist and write the attestation marker that `/rai-story-close`'s
`gate-ar-story` gate verifies. This is the only place the checklist runs —
story-close does not re-run it, it only checks that this marker exists
(RAISE-14277 / ADR-130: attestation and verification must not be the same
actor at the same instant — the gate was previously self-attestable because
close both created and checked the marker in one command).

1. **P1 — Structural drift**: `rai drift check packages/<changed-module>/`
   Review output: orphaned symbols? dead public APIs?
2. **P2 — Beck-R2**: Does this story add necessary complexity only?
   No speculative abstractions, no unused parameters, no dead branches.
3. **P3 — Convention**: Naming, module placement, public API surface
   consistent with codebase?
4. **P4 — Product alignment**: Read `governance/prd.md` and `governance/vision.md`
   (graceful degradation: if absent or placeholder-only, mark N/A and continue).
   Does the delivered story stay within the design doc's Problem/Value framing,
   contradicting no PRD requirement or Vision outcome?

After confirming all four, write the branch-and-session-scoped attestation
marker via the centralized writer (D1 — never hand-roll this path in bash):

```bash
rai gate ar-attest --gate gate-ar-story
```

Do **not** run the `gate-ar-story` gate here, and do **not** remove the
marker afterward — verification happens later, in `/rai-story-close`, against
this same marker. Touching and removing it in the same step would recreate
the self-attestation bypass this fixes.

<verification>
AR checklist (P1/P2/P3) completed. Attestation marker written for
`/rai-story-close` to verify.
</verification>

### Step 1.5: Frontend Visual & A11y Verification (frontend stories only)

> **Skip entirely for non-frontend stories.** Gate condition: `is_frontend=true`. If the story touched no rendered UI, proceed directly to Step 2.

After confirming tests pass, open the implemented UI in a real browser and verify fidelity against the prototype/living-design-system. This closes the gap ADR-125 identified: jsdom unit tests cannot catch layout overflow, active-class mismatches, or missing ARIA attributes on real DOM.

**Tooling:** Chrome DevTools MCP (`browser_navigate`, `browser_snapshot`, `browser_evaluate`) or Playwright MCP (`browser_navigate`, `browser_snapshot`). Both are registered per project. Use whichever is available in session.

#### Visual Fidelity Checklist

- [ ] Navigate to the relevant route/component (`browser_navigate`)
- [ ] Prototype classnames present: every class specified in the design prototype/living-design-system appears on the rendered elements (`browser_snapshot` or DevTools inspector)
- [ ] Active/selected states correct: toggles, tabs, segments render the correct active-class on selection
- [ ] Layout: no overflow, truncation, or stacking collapse not present in the prototype

#### A11y Checklist (basic — not a full WCAG audit)

- [ ] Dialog/modal has `role="dialog"` and `aria-labelledby` pointing to its heading
- [ ] Focus trap: Tab key cycles within an open dialog; Escape closes it
- [ ] Toast/notification uses `aria-live="polite"` (or `aria-live="assertive"` for errors)
- [ ] Interactive controls have accessible names (visible button text or `aria-label`)

**On failure:** Treat as a blocking defect. Fix in the current story branch before continuing to Step 2. Do not defer to a follow-up issue unless the defect is explicitly out of scope for this story (document why).

**Reference:** ADR-125 (frontend fidelity gate — E11478 post-mortem: drawer overflow and segment active-class missed by jsdom, caught only in browser walk).

<verification>
Frontend visual/a11y verification complete (or step skipped — non-frontend story). Any defects found are fixed or explicitly deferred with justification.
</verification>

### Step 2: Gather Data & Reflect

> **JIT**: Before reflecting on development process, query graph for evaluation patterns
> → `aspects/introspection.md § JIT Protocol`

Review the story development: actual vs estimated time, blockers, plan deviations.

**Heutagogical checkpoint** — answer with specific examples:
1. What did you learn?
2. What would you change about the process?
3. Are there improvements for the framework?
4. What are you more capable of now?

Identify concrete improvements to skills, guardrails, or templates. Apply small improvements immediately; create issues for complex ones.

<verification>
All four questions answered. Improvements identified (or celebrated that none needed).
</verification>

### Step 3: Persist Patterns & Reinforce

> **JIT**: Before persisting patterns, query graph for existing patterns to avoid duplicates
> → `aspects/introspection.md § JIT Protocol`

**Pattern writing guidelines** — before composing pattern content:
- Structure: action + context + reason (e.g., "Use singleton for DB connections to avoid pool exhaustion under concurrent requests")
- Length: 100-300 chars ideal. If > 500, consider splitting into 2 patterns
- Be specific: "Validate JWT expiry before DB query" > "Always validate tokens"
- No narrative: state the insight directly, not the story of how you found it
- Bad example: "We found that using a singleton pattern works better because in our testing we saw that multiple connections caused issues"
- Good example: "Use singleton pattern for DB connections to avoid connection pool exhaustion under concurrent requests"

**Add new patterns** worth preserving across sessions. Use `raise_pattern_add` MCP tool with `cwd="{project_or_worktree_path}"`, content="Pattern description", context="context,keywords", pattern_type="process", from_story="S{N}.{M}".

If MCP tools are not available, fall back to:
```bash
rai pattern add "Pattern description" -c "context,keywords" -t process --from S{N}.{M}
```

Types: `process`, `technical`, `architecture`, `codebase`.

**Reinforce existing patterns** — evaluate behavioral patterns loaded at session start. Use `raise_pattern_reinforce` MCP tool with pattern_id={pattern_id}, vote={1|0|-1}, from_story="S{N}.{M}", `cwd="{project_or_worktree_path}"`.

If MCP tools are not available, fall back to:
```bash
rai pattern reinforce {pattern_id} --vote {1|0|-1} --from S{N}.{M}
```

| Vote | Meaning |
|:----:|---------|
| `1` | Implementation followed the pattern |
| `0` | Pattern not relevant to this story (does NOT count toward evaluations) |
| `-1` | Implementation contradicted the pattern |

Only evaluate patterns you consciously considered. `0` is correct for most patterns in any story.

<verification>
New patterns persisted. Behavioral patterns evaluated (or explicitly skipped).
</verification>

### Step 4: Document Retrospective

Publish retrospective to local path and docs adapter via:

Use `raise_docs_write` MCP tool with doc_type="story", title="S{N}.{M}: {story-name} — Retrospective", content="# Retrospective: S{N}.{M} — {story-name}\n\n**Dates:** {start-date} → {end-date}\n...\n\n## Summary\n...\n\n## What went well\n...\n\n## What to improve\n...\n\n## Heutagogical Checkpoint\n...\n\n## Improvements applied\n...\n\n## Patterns added / reinforced\n...", output_path="work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write story \
  --title "S{N}.{M}: {story-name} — Retrospective" \
  --stdin \
  --output-path work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md << 'EOF'
# Retrospective: S{N}.{M} — {story-name}

**Dates:** {start-date} → {end-date}
**Estimated:** {estimated} | **Actual:** {actual}

## Summary
{summary}

## What went well
{went-well}

## What to improve
{to-improve}

## Heutagogical Checkpoint
1. **What did I learn?** {answer}
2. **What would I change about the process?** {answer}
3. **Framework improvements?** {answer}
4. **More capable of now?** {answer}

## Improvements applied
{improvements}

## Patterns added / reinforced
{patterns}
EOF
```

<verification>
Retrospective persisted locally and published via docs adapter.
</verification>

### Step 5: Emit Structured Retro Artifact

Emit the retrospective as a structured artifact so `story.yaml`'s `close.validates` (RAISE-11088) can prove — in SQLite, issue-scoped by construction — that a retrospective exists for THIS story before `/rai-story-close` is allowed to complete. A repo-wide file glob would be satisfied by ANY story's retrospective already in the repo; this sqlite record cannot be.

```
raise_artifact_emit(
    artifact_type="retro",
    story_id="{story_key}",
    content=<JSON with fields: patterns_learned (list[str]), reinforcements (list[str]), velocity_ratio (optional float), notes (optional str)>,
    cwd="{project_or_worktree_path}"
)
```

**CRITICAL — identifier mismatch risk (same hazard as RAISE-11147's `implement` fix):** `story_id` here MUST be `{story_key}` — the pipeline's **issue key** (the same value passed to `pipeline_start`, e.g. `"RAISE-1281"`), **NOT** the `S{N}.{M}` convention used by this step's `raise_docs_write` `output_path` above. `story.yaml`'s sqlite validate branch looks up `artifact_store.exists(run["issue_id"], "retro")`, and `run["issue_id"]` is always the Jira key. Emitting with `S{N}.{M}` instead would make the sqlite lookup never find the artifact, turning `close` into a permanent `artifact_missing` deadlock.

**Note:** The CLI fallback for artifact emission was removed in v3.0.0. MCP tool `raise_artifact_emit` is required. If MCP tools are not available, skip structured artifact emission — the pipeline will require it before `close` can complete.

<verification>
Retro artifact emitted to SQLite, keyed by the story's issue key.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md` (local) + docs adapter (type: story) |
| Retro artifact | SQLite (`artifact_type=retro`, keyed by issue key) |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Signal | WorkLifecycle event emitted (start on entry, complete here) |

Backlog transition to review status is engine-owned (RAISE-15034):
Engine performs the transition via `apply_phase_transition` at phase completion.
No skill-initiated transition call required or allowed.
**Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] NEVER skip pattern reinforce — scoring system depends on it (RAISE-170)
- [ ] NEVER give vague checkpoint answers — be specific with concrete examples

## References

- Previous: `/rai-story-implement`
- Next: `/rai-story-close`
- Pattern scoring: RAISE-170 (temporal decay + Wilson scorer)
