---
name: rai-story-review
description: Extract learnings and persist patterns from completed story. Use after implementation.

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
  raise.version: "2.4.0"
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
    max_tier1_queries: 2
    max_jit_queries: 3
    tier1_queries:
      - "evaluation patterns for {affected_modules}"
      - "process patterns from recent stories"
---

# Story Review

## Purpose

Reflect on the completed story to extract learnings, persist patterns, reinforce behavioral signals, and emit calibration telemetry.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, answer all checkpoint questions with specific examples
- **Ha**: Adapt depth to story complexity, batch small story reviews
- **Ri**: Custom review patterns, integrate with team retrospectives

## Context

**When to use:** After implementation is complete and tests pass. Before `/rai-story-close`.

**Inputs:** Completed story, progress log, passing test suite.

## Steps

> **PRIME**: Before Step 1, follow PRIME protocol in `aspects/introspection.md`.
> Chain read: read ALL previous story learning records (story-design, story-plan, story-implement). This provides the aggregate view for the retrospective.

### Step 1: Verify Tests Pass

Determine which test command to run using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command` — if set, use it directly (configuration over convention)
2. **Detect language** from `project.project_type` in manifest, or scan file extensions of changed files (`git diff --name-only`)
3. **Map language to default** using the table below

```yaml
# .raise/manifest.yaml — example
project:
  test_command: "cargo test --quiet"   # explicit override, highest priority
  project_type: rust
```

| Language | Extensions | Default Test Command |
|----------|-----------|----------------------|
| Python | `.py`, `.pyi` | `uv run pytest --tb=short` |
| TypeScript | `.ts`, `.tsx` | `npx vitest run` or `npm test` |
| JavaScript | `.js`, `.jsx` | `npx vitest run` or `npm test` |
| C# | `.cs` | `dotnet test --verbosity quiet` |
| Go | `.go` | `go test ./...` |
| PHP | `.php` | `vendor/bin/phpunit` |
| Dart | `.dart` | `flutter test` |
| Unknown | — | Ask developer |

The table is a **fallback** — `project.test_command` always wins when present.

| Condition | Action |
|-----------|--------|
| Tests green | Continue |
| Tests failing | Fix first — review requires green tests |

<verification>
Project language detected. Tests passing with appropriate runner.
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

### Step 3: Aggregate Learning Records

Read learning records produced during this story's lifecycle:
- `.raise/rai/learnings/rai-story-design/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-story-plan/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-story-implement/{work_id}/record.yaml`

If any record is missing (silent node or execution gap), note it and continue — missing records are valid signal.

Produce aggregate summary with these metrics:

| Metric | Calculation | What it tells us |
|--------|-------------|-----------------|
| **Acceptance rate** | Patterns voted +1 / total patterns primed | Are PRIME queries returning useful context? |
| **Gap rate** | Total gaps / total JIT queries | Is the graph missing knowledge we need? |
| **Pattern utility** | Patterns +1 / (patterns +1 + patterns -1) | Are stored patterns helping or misleading? |

Include the aggregate in the retrospective (Step 5).

<verification>
Learning records read (or missing noted). Metrics calculated. Aggregate ready for retrospective.
</verification>

### Step 4: Persist Patterns & Reinforce

> **JIT**: Before persisting patterns, query graph for existing patterns to avoid duplicates
> → `aspects/introspection.md § JIT Protocol`

**Add new patterns** worth preserving across sessions:

```bash
rai pattern add "Pattern description" -c "context,keywords" -t process --from S{N}.{M}
```

Types: `process`, `technical`, `architecture`, `codebase`.

**Reinforce existing patterns** — evaluate behavioral patterns loaded at session start:

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

### Step 5: Document Retrospective

Create `work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md` with:
- Summary (story ID, dates, estimated vs actual time)
- What went well / what to improve
- Heutagogical checkpoint answers
- Improvements applied
- Patterns added/reinforced
- **Learning chain summary** (from Step 3): records found/missing, aggregate metrics, notable gaps, downstream enrichments

<verification>
Retrospective document created with learning chain summary.
</verification>

### Step 6: Emit Calibration Telemetry

```bash
rai signal emit-calibration S{N}.{M} --size {XS|S|M|L} --estimated {minutes} --actual {minutes}
```

This feeds the velocity tracking system for future estimation accuracy.

<verification>
Calibration event recorded (or skipped if CLI unavailable).
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md` |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Calibration | Via `rai signal emit-calibration` |
| Next | `/rai-story-close` |

> **LEARN**: After completing Step 6, follow LEARN protocol in `aspects/introspection.md`.
> Record path: `.raise/rai/learnings/rai-story-review/{work_id}/record.yaml`

## Quality Checklist

- [ ] Project language detected before running tests
- [ ] Tests pass with language-appropriate runner (gate)
- [ ] Heutagogical checkpoint answered with specific examples
- [ ] New patterns persisted via `rai pattern add`
- [ ] Behavioral patterns reinforced via `rai pattern reinforce`
- [ ] Calibration telemetry emitted
- [ ] Retrospective document created
- [ ] NEVER skip pattern reinforce — scoring system depends on it (RAISE-170)
- [ ] NEVER give vague checkpoint answers — be specific with concrete examples

## References

- Previous: `/rai-story-implement`
- Next: `/rai-story-close`
- Pattern scoring: RAISE-170 (temporal decay + Wilson scorer)
