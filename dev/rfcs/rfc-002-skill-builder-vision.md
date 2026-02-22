# RFC-002: Skill Builder — CLI Knowledge as Compilation Target

> **Status:** Draft — Vision Document
> **Date:** 2026-02-21
> **Context:** SES-234 ontological analysis, RAISE-242, ADR-038, RFC-001
> **Relates to:** RAISE-242 (Skill Ecosystem), RAISE-247 (CLI Ontology)

---

## The Problem

RaiSE skills today carry **68% ceremony overhead**. A typical lifecycle skill (story-design,
story-plan, etc.) spends 4-5 CLI calls on mechanical work before doing anything that
requires inference:

```
Step 0:    rai memory emit-work ... --event start      ← telemetry
Step 0.1:  rai memory query "..."                      ← context loading
Step 0.2:  rai memory context mod-X                    ← context loading
Step N:    [actual design/planning work]                ← inference
Step N+1:  rai memory emit-work ... --event complete   ← telemetry
```

Each CLI call costs ~200-500ms in process invocation plus ~200 tokens of agent inference
to read the instruction, generate the command, execute it, and interpret the output.
That's **~1,000 tokens and ~2 seconds** wasted per skill invocation on work that requires
zero judgment.

Three solutions were considered:

| Approach | Problem |
|----------|---------|
| Make the CLI smarter (`rai skill prepare`) | Couples skills to CLI — custom skills break |
| Make skills leaner (remove ceremony) | Loses telemetry and context — quality drops |
| Make the skill *builder* smarter | Skills come out correct without coupling |

## The Insight

The ceremony is correct — it's just in the wrong place. Telemetry, context loading,
and prerequisite checks are legitimate concerns. They shouldn't be removed. They should
be **generated correctly by the tool that creates skills**, not maintained by hand in
every skill.

This is a compiler pattern:

```
Skill intent (what the skill does)
  → Skill Builder (knows CLI ontology, conventions, anti-patterns)
    → Complete SKILL.md (correct frontmatter, correct CLI calls, correct ceremony)
      → Skill Validator (verifies the output before distribution)
```

The Skill Builder is the single point where CLI knowledge lives. When the CLI changes
(RAISE-247 renames `memory` → `graph`), the builder updates once. When hooks (RFC-001)
eliminate the need for `emit-work` in skills, the builder stops generating those lines.
Individual skills don't need to change — they get regenerated.

## What the Skill Builder Knows

### 1. CLI Ontology (from ADR-038)

The complete command taxonomy:

```
graph:   build, validate, query, context, list, viz, extract
pattern: add, reinforce
signal:  emit (work, session, calibration)
session: start, context, close
discover: scan, analyze, drift
skill:   list, validate, check-name, scaffold
backlog: auth, pull, push, status
release: check, publish, list
```

For each command: when to use it, what parameters it takes, what output to expect.

### 2. Ceremony Patterns (by skill type)

| work_cycle | Ceremony needed |
|-----------|-----------------|
| `story` | emit-work start/complete, query patterns, load module context |
| `epic` | emit-work start/complete, query patterns, load module context |
| `session` | session start/close (no emit-work — session commands handle it) |
| `discovery` | discover scan/analyze, graph build |
| `utility` | none — utility skills have no lifecycle |
| `meta` | none — meta skills operate on skills themselves |

The builder generates ceremony based on `work_cycle` declaration. A custom skill with
`work_cycle: utility` gets no ceremony. A custom skill with `work_cycle: story` gets
the same ceremony as built-in story skills.

### 3. Anti-Patterns

Things the builder prevents and the validator catches:

- `emit-work` inside a session skill (session commands already emit)
- `add-session` anywhere (redundant with `session close`)
- `add-calibration` + `emit-calibration` in the same skill (pick one)
- `graph build` without checking if graph exists first
- Missing `--event complete` when `--event start` is present (orphan signals)
- Hardcoded story/epic IDs instead of `{story_id}` template variables
- CLI commands from old ontology (`rai memory` instead of `rai graph`)

### 4. Frontmatter Convention

The builder ensures complete, consistent frontmatter:

```yaml
metadata:
  raise.work_cycle: story|epic|session|discovery|utility|meta
  raise.frequency: per-story|per-epic|per-session|per-project|on-demand
  raise.fase: "1"-"N"|"meta"
  raise.prerequisites: comma-separated skill names
  raise.next: next skill in chain
  raise.gate: gate-code|gate-design|""
  raise.adaptable: "true"|"false"
  raise.version: semver
  raise.visibility: public|internal
```

### 5. Structural Conventions

- Required sections: Purpose, Context, Steps, Output
- ShuHaRi levels in Context section
- Step numbering: Step 0.x for ceremony, Step 1+ for substance
- HITL checkpoints after significant work
- Template variables: `{story_id}`, `{epic_id}`, `{module_name}`

## Relationship with RAISE-242

RAISE-242 currently scopes two stories:

1. **rai-skill-create** — "Inference skill that generates new skills with full content
   using existing CLI tools (scaffold, validate, check-name) and existing skills as
   reference patterns"
2. **rai-bugfix** — First skill created with rai-skill-create

This vision **expands the scope of story 1** (rai-skill-create). The original scope
assumes the skill creator just generates content (Purpose, Steps, ShuHaRi). This vision
adds:

- CLI ontology knowledge (which commands to use and when)
- Ceremony generation (automatic based on work_cycle)
- Anti-pattern prevention (validator catches mistakes)
- Frontmatter generation (complete and consistent)

The original RAISE-242 description says "No CLI code changes needed." This vision
challenges that — the **validator** needs new semantic checks beyond structural
validation.

### Proposed RAISE-242 revision

| Original | Revised |
|----------|---------|
| rai-skill-create generates content | rai-skill-create generates content + correct CLI usage |
| rai skill validate checks structure | rai skill validate checks structure + CLI semantics |
| No CLI code changes | Validator gets semantic rules (CLI anti-pattern checks) |
| Skills as reference patterns | Skills + CLI ontology as reference patterns |

Story breakdown:

1. **S1: Semantic validator** — Extend `rai skill validate` with CLI semantic checks
   (anti-patterns, orphan signals, old ontology commands). CLI code change.
2. **S2: rai-skill-create skill** — Inference skill that generates new skills using
   scaffold + CLI ontology knowledge + semantic validator as gate. Skill content, no CLI.
3. **S3: rai-debug (was rai-bugfix)** — First skill created with rai-skill-create.
   Validates the builder works. Skill content, no CLI.

## What This Does NOT Include

- **`rai skill prepare` / `rai skill run`** — Rejected. Couples skills to CLI.
- **Skill runtime / execution engine** — The agent remains the executor. Skills remain
  markdown instructions.
- **Automatic ceremony elimination via hooks** — That's RFC-001's job. When hooks land,
  the builder stops generating ceremony lines. Skills get leaner over time without
  manual updates.
- **Skill marketplace / distribution** — That's a separate concern (parking lot item).

## Evolution Path

```
Today:     scaffold (template) + validate (structure) + manual content
RAISE-242: skill-create (inference content) + validate (structure + semantics)
RFC-001:   hooks eliminate ceremony → builder stops generating it → skills get leaner
Future:    skill-create becomes the primary way ALL skills are authored
```

The Skill Builder is the leverage point. It absorbs complexity so skills stay simple.
When the CLI changes, the builder changes. When conventions evolve, the builder evolves.
Individual skills — whether built-in or custom — remain pure process instructions that
any agent can execute.

## References

- RAISE-242: Skill Ecosystem (Jira epic)
- RAISE-247: CLI Ontology Restructuring (Jira epic)
- ADR-038: CLI Ontology Restructuring (decision record)
- RFC-001: Extensibility Architecture (hooks, gates, providers)
- SES-234: Ontological analysis session (2026-02-21)
- Parking lot: "Skill compression for Ri level" (SES-135)
- Parking lot: "RaiSE Hub — curated skill marketplace" (SES-213)
