---
name: rai-skill-create
description: >
  Guided skill creation through conversation and CLI composition. Walks through
  purpose definition, naming, lifecycle positioning, reference pattern reading,
  content design, writing, and validation. Produces a complete SKILL.md.

license: MIT

metadata:
  raise.work_cycle: meta
  raise.frequency: on-demand
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Skill Create: Guided Skill Authoring

## Purpose

Guide the creation of a new RaiSE skill through conversation, composing existing CLI tools (`rai skill check-name`, `rai skill list`, `rai skill validate`) with inferential pattern matching. The intelligence is in the conversation design — understanding intent, reading reference skills for domain patterns, and producing a complete SKILL.md with real content (not scaffold TODOs).

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all 8 steps in sequence. Ask explicit questions at each stage. Show reference skill excerpts when designing content.

**Ha (破)**: Collapse steps when the user provides detailed upfront intent. Infer lifecycle metadata when domain is clear.

**Ri (離)**: Create skill families (multi-skill sequences) in a single pass. Propose skill decomposition when scope is too broad.

## Context

**When to use:**
- Creating a new skill for the RaiSE ecosystem
- When someone says "I want a skill that does X"
- When converting an ad-hoc workflow into a repeatable skill

**When NOT to use:**
- Modifying an existing skill (edit the SKILL.md directly)
- Creating CLI commands (skills orchestrate, CLI executes)
- Writing source code in `src/` (skills are pure Markdown)

**Inputs required:**
- A rough idea of what the skill should do
- Optionally: which lifecycle it belongs to (story, epic, utility, etc.)

**Output:**
- A complete `.claude/skills/rai-{name}/SKILL.md` that passes `rai skill validate`
- No TODO placeholders — all sections filled with real content

## Steps

### Step 1: Understand Skill Purpose

Start with a conversation to understand what the skill should do. This is the most important step — everything else follows from a clear purpose.

**Ask:**
> "What should this skill do? Describe the problem it solves and when someone would reach for it."

**Extract from the answer:**
- **What:** The core action (analyze, generate, validate, guide, etc.)
- **Why:** The problem it solves (what's painful without it)
- **When:** The trigger conditions (after X, when Y happens, before Z)
- **Who:** Who benefits (the developer, the team, a stakeholder)

**If the scope is too broad** (covers multiple distinct workflows):
> "This sounds like it could be 2-3 separate skills. A skill should do one thing well. Want to decompose it?"

**Verification:** You can state the skill's purpose in one sentence.

> **If you can't continue:** Purpose vague → Ask: "Give me a concrete example. When was the last time you needed this?"

### Step 2: Derive and Validate Name

Derive a name from the purpose, then validate it with the CLI.

**Naming convention:** `rai-{domain}-{action}`
- Domain: the area it operates in (story, epic, discover, debug, session, etc.)
- Action: what it does (create, review, sync, start, close, etc.)

**Derive 2-3 candidate names** from the purpose and present them:
> "Based on the purpose, I suggest: `rai-{domain}-{action1}`, `rai-{domain}-{action2}`. Preference?"

**Validate the chosen name:**

```bash
rai skill check-name {chosen-name}
```

**Check for:**
- Follows `{domain}-{action}` pattern
- No conflict with existing skills
- No CLI command conflict
- Domain is standard or intentionally new

**If the domain is not standard** (warning from check-name):
> "Domain '{domain}' is new. Existing domains: debug, discover, docs, epic, framework, project, research, session, skill, story. Is this intentional, or should we use an existing domain?"

**Verification:** `rai skill check-name` passes with no errors.

> **If you can't continue:** Name conflict → Try alternative names. Name too generic → Make it more specific.

### Step 3: Determine Lifecycle Position

Establish where this skill fits in the RaiSE workflow.

**Ask about each metadata field:**

**work_cycle** — Which lifecycle does this skill belong to?

| Value | Meaning | Examples |
|-------|---------|---------|
| `story` | Part of the story lifecycle | story-design, story-plan, story-implement |
| `epic` | Part of the epic lifecycle | epic-design, epic-plan, epic-close |
| `discovery` | Part of the codebase discovery pipeline | discover-start, discover-scan |
| `session` | Session management | session-start, session-close |
| `utility` | Standalone, use anytime | debug, research, docs-update |
| `meta` | About the framework itself | framework-sync, publish, skill-create |

**frequency** — How often is this skill used?

| Value | Meaning |
|-------|---------|
| `per-story` | Once per story |
| `per-epic` | Once per epic |
| `per-project` | Once per project |
| `per-session` | Once per session |
| `as-needed` | When the situation calls for it |
| `on-demand` | Triggered by user request |

**fase** — Position in the lifecycle sequence (number for ordered skills, `"0"` for unordered):

```
Story lifecycle:  3(start) → 4(design) → 5(plan) → 6(implement) → 7(review) → 8(close)
Epic lifecycle:   2(start) → 3(design) → 4(plan) → epic-close
Discovery:        1(start) → 2(scan) → 3(validate) → 5(document)
Utility:          "0" (no fixed position)
```

**prerequisites** — What must exist before this skill runs? (skill name without `rai-` prefix, or empty)

**next** — What skill typically follows? (skill name without `rai-` prefix, or empty)

**gate** — What quality gate applies? (gate filename, or empty)

**visibility** — `public` (distributed with `rai` package) or `internal` (project-specific)

**Verification:** All metadata fields have values.

> **If you can't continue:** Lifecycle unclear → Default to `work_cycle: utility`, `frequency: as-needed`, `fase: "0"`. Adjust later.

### Step 4: Discover CLI Tools and Read Reference Skills

Two sources of grounding: the CLI itself (what tools exist) and reference skills (how they're used in practice).

#### 4a: Discover Available CLI Tools

Run `rai --help` to see all command groups. Then, for groups relevant to the new skill's domain, drill into subcommands:

```bash
rai --help
rai {group} --help           # e.g., rai memory --help
rai {group} {subcommand} --help  # e.g., rai memory emit-work --help
```

Each `--help` provides: description, context, examples, arguments, and options. This is enough to understand what a command does and when to use it — no guessing needed.

**Drill-down heuristic:** Start with `rai --help` for the full map. Go one level deeper (`rai {group} --help`) for groups related to the new skill's `work_cycle`. Go two levels deep (`rai {group} {subcommand} --help`) only for commands you're considering including in the skill's steps.

#### 4b: Read Reference Skills

**List all skills:**

```bash
rai skill list --format json
```

**Select 2-3 reference skills** based on:
1. **Same domain** — skills in the same `work_cycle` (e.g., other story-cycle skills)
2. **Similar pattern** — skills with similar structure (conversational vs CLI-heavy vs hybrid)
3. **Adjacent lifecycle** — the skill's `prerequisites` and `next` neighbors

**Read each reference skill:**

Read the SKILL.md files of the selected reference skills using the Read tool. Focus on:
- **Which CLI commands they use**, in which step, and for what purpose
- How they structure their Steps (what makes a good step)
- How they balance CLI commands vs inference
- How they handle verification and blockers
- What sections they include beyond the standard set

The reference skills show CLI commands in context — how real skills compose them into workflows. Combined with the `--help` output from 4a, you have both the **catalog** (what exists) and the **usage patterns** (how and when to use it).

#### 4c: Classify Pattern

| Pattern | CLI % | Inference % | Examples |
|---------|:-----:|:-----------:|---------|
| Pure inference | 0% | 100% | rai-debug, rai-problem-shape |
| Hybrid | 20-50% | 50-80% | rai-discover-start, rai-story-design |
| CLI-heavy | 50-70% | 30-50% | rai-publish, rai-session-close |

**Determine which pattern the new skill follows** and note it for Step 5.

**Verification:** CLI tools discovered; 2-3 reference skills read; pattern type determined.

> **If you can't continue:** No similar skills exist → This is a new domain. Use rai-debug (pure inference) or rai-discover-start (hybrid) as structural references.

### Step 5: Design Skill Content

Design each section of the SKILL.md through conversation, using the reference patterns from Step 4.

**Design each section in order:**

#### 5a: Purpose (2-3 sentences)
- What it does and why it exists
- One-line core principle if applicable

#### 5b: Mastery Levels (ShuHaRi)
- **Shu**: Follow all steps, full guidance
- **Ha**: Adapt depth, skip where confident
- **Ri**: Create custom patterns, extend beyond the skill

#### 5c: Context
- **When to use** (3-5 trigger conditions)
- **When NOT to use** or **When to skip** (2-3 anti-patterns)
- **Inputs required** (what must exist before running)
- **Output** (what the skill produces)

#### 5d: Steps (the core logic)
Design the step sequence. Each step needs:
- **Clear action** — what to do (CLI command, inference task, or conversation)
- **Verification** — how to confirm the step succeeded
- **Blocker** — what to do if it can't continue

**Step design heuristics:**
- Start with context loading (query memory, read prerequisites)
- End with telemetry (emit-work) and summary
- CLI commands go in fenced code blocks
- HITL checkpoints after significant work
- Each step should be independently resumable

**Step numbering convention:**
- `Step 0`, `Step 0.1`, `Step 0.5` — prerequisites, context loading
- `Step 1` through `Step N` — core logic
- Final step — summary and next steps

#### 5e: RaiSE Integration Points

Based on the `work_cycle`, `fase`, and `prerequisites` determined in Step 3, **Rai infers** which RaiSE integrations the new skill needs and writes them into the steps automatically. The user doesn't need to know what these are — Rai decides based on the skill's position in the ecosystem.

**Decision matrix — Rai applies this, not the user:**

| Integration | When to include | How |
|-------------|----------------|-----|
| **Telemetry** (emit-work) | `work_cycle` is `story` or `epic` | Add `Step 0: Emit Start` and final `Step N: Emit Complete` using `rai memory emit-work` |
| **Context loading** (memory query) | `work_cycle` is `story`, `epic`, or skill queries prior learnings | Add `Step 0.5: Query Context` with `rai memory query` targeting domain keywords |
| **Architectural context** | Skill modifies code in specific modules | Add `Step 0.6: Load Architectural Context` with `rai memory context mod-{name}` |
| **Prerequisite verification** | `prerequisites` is not empty | Add `Step 0.1: Verify Prerequisites` that checks the prerequisite artifact exists |
| **HITL checkpoints** | Always (RaiSE default) | Insert pause points after analysis, before writes, after destructive operations |
| **Pattern persistence** | Skill produces learnings (review, retrospective, research) | Include `rai memory add-pattern` step near the end |

**How to apply:**

1. Read the metadata from Step 3
2. Match against the matrix above
3. Generate the corresponding boilerplate steps using the CLI commands and patterns from the reference skills read in Step 4
4. Weave them into the step sequence at the correct positions (Step 0.x for setup, final steps for teardown)

**Present the integration decisions to the user as rationale, not as questions:**

> "Since this is a story-lifecycle skill at fase 6, I'll include:
> - Telemetry at start/end (`rai memory emit-work story`)
> - Context loading (`rai memory query` for relevant patterns)
> - Prerequisite verification (checks that the plan exists)
> - HITL checkpoint after the main work
>
> These are standard for story-cycle skills — they enable session continuity, pattern learning, and progress tracking across the RaiSE workflow."

**Only ask if ambiguous** — for example, if `work_cycle: utility` but the skill clearly produces learnings, ask:
> "This skill generates insights during execution. Should it persist patterns to memory (`rai memory add-pattern`) so future sessions can learn from them?"

**CLI commands reference for generated steps:**

```bash
# Telemetry
rai memory emit-work {story|epic} {WORK_ID} --event {start|complete} --phase {phase_name}

# Context loading
rai memory query "{domain keywords}" --types pattern,guardrail --limit 5

# Architectural context
rai memory context mod-{module_name}

# Prerequisite check
ls {expected_artifact_path} 2>/dev/null || echo "ERROR: Run {prerequisite_skill} first"

# Pattern persistence
rai memory add-pattern "Description" -c "context,keywords" -t {process|technical|architecture} --from {work_id}
```

#### 5f: Output
- Artifact locations (file paths)
- Telemetry events
- Gate references
- Next skill in the chain

**Present the complete design for HITL review before writing:**

> "Here's the skill design. Review before I write it:
> - Purpose: [...]
> - Steps: [N steps — brief list]
> - Pattern: [inference/hybrid/CLI-heavy]
> - Reference skills used: [list]"

**Verification:** User approves the design.

> **If you can't continue:** User wants changes → Adjust design. Major rethink → Return to Step 1.

### Step 6: Write Complete SKILL.md

Write the full SKILL.md file: frontmatter + all body sections.

**Frontmatter template:**

```yaml
---
name: {name}
description: >
  {2-3 sentence description from Step 5a. Must match what
  rai skill list will show. First sentence is the key.}

license: MIT

metadata:
  raise.work_cycle: {from Step 3}
  raise.frequency: {from Step 3}
  raise.fase: "{from Step 3}"
  raise.prerequisites: "{from Step 3}"
  raise.next: "{from Step 3}"
  raise.gate: "{from Step 3}"
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: {from Step 3}
---
```

**Body sections in order:**

1. `# {Title}: {Subtitle}` — H1 heading
2. `## Purpose` — from Step 5a
3. `## Mastery Levels (ShuHaRi)` — from Step 5b
4. `## Context` — from Step 5c
5. `## Steps` — from Step 5d (each step as `### Step N: Title`)
6. `## Output` — from Step 5e
7. `## Notes` — design philosophy, integration notes, tips (optional but recommended)
8. `## References` — related skills, docs, templates

**Write the file:**

Create the directory and file at `.claude/skills/{name}/SKILL.md` using the Write tool.

**Quality checks before writing:**
- No TODO or placeholder text anywhere
- CLI commands use correct syntax (verify against `--help` if unsure)
- Verification gates are specific (not "it works")
- Blocker guidance is actionable (not "ask someone")
- Description in frontmatter matches the Purpose section

**Verification:** File written at `.claude/skills/{name}/SKILL.md`.

> **If you can't continue:** Write fails → Check directory exists. Create with `mkdir -p .claude/skills/{name}/`.

### Step 7: Validate

Run the validator to check structure and conventions.

```bash
rai skill validate .claude/skills/{name}/SKILL.md
```

**Expected:** `✓ All checks passed`

**If validation fails:**
1. Read the specific error messages
2. Fix each issue in the SKILL.md
3. Re-validate until clean

**Common validation issues:**
- Missing required frontmatter fields
- Description too short or missing
- Missing required sections (Purpose, Context, Steps, Output)
- Name doesn't match directory name

**Verification:** `rai skill validate` exits 0 with all checks passed.

> **If you can't continue:** Persistent validation errors → Read `rai skill validate --help` for schema details. Compare against a known-good skill (e.g., rai-debug).

### Step 8: Present Summary and Next Steps

Present what was created and what to do next.

**Display:**

```markdown
## Skill Created: {name}

**File:** `.claude/skills/{name}/SKILL.md`
**Lifecycle:** {work_cycle} / {frequency}
**Pattern:** {inference/hybrid/CLI-heavy} (~{N}% CLI / ~{M}% inference)

### Sections
- Purpose: {one-line summary}
- Steps: {N} steps
- Validation: passed

### Reference Skills Used
- {skill 1} — {what was borrowed}
- {skill 2} — {what was borrowed}

### Next Steps
1. **Test it:** Run `/{name}` to invoke the skill and verify the flow
2. **Iterate:** Adjust steps based on real usage
3. **Register:** The skill is auto-discovered — no registration needed (PAT-E-264)
```

**Verification:** Summary displayed; user knows how to use and iterate.

## Output

| Item | Destination |
|------|-------------|
| Complete SKILL.md | `.claude/skills/{name}/SKILL.md` |
| Validation | `rai skill validate` passes |
| Summary | Displayed to user |

## Notes

### Orchestration, Not Generation

This skill composes existing CLI tools with conversational guidance. It does NOT:
- Modify any file in `src/`
- Create CLI commands
- Register skills anywhere (auto-discovery handles that)

The value is in the conversation: understanding intent, reading patterns, designing steps, and producing content that another AI agent can follow accurately.

### Skill Quality Heuristics

A good SKILL.md:
- Can be understood by reading Purpose + Context alone (<2 min)
- Has steps that are independently resumable
- Uses CLI for deterministic operations, inference for creative ones
- Includes verification at every step (not just the end)
- States explicit blockers ("If you can't continue")

A bad SKILL.md:
- Has TODO placeholders
- Mixes CLI and inference without clear separation
- Has steps that depend on implicit context
- Skips verification ("it should work")
- Over-specifies implementation ("use for loop to iterate")

### Naming Philosophy

Skill names optimize for developer UX — what they'd naturally type — over philosophical accuracy. The meaning lives in the documentation, not in the command name (PAT-E-216).

`git commit` not `git crystallize-intent`.

### Pattern Diversity

Skills range from 0% CLI (rai-debug) to ~60% CLI (rai-discover-start). There is no single correct balance. Match the pattern to the task:
- **Pure inference** — analysis, review, decision-making
- **Hybrid** — guided workflows with validation checkpoints
- **CLI-heavy** — pipeline orchestration, data transformation

## References

- CLI tools: `rai skill check-name`, `rai skill list`, `rai skill validate`
- Skill schema: `src/rai_cli/skills/schema.py`
- Scaffold command: `rai skill scaffold` (generates template with TODOs — this skill replaces that workflow)
- Auto-discovery: PAT-E-264 (skills discovered from `.claude/skills/*/SKILL.md`)
- Naming: PAT-E-216 (optimize for developer UX)
- Complement: Edit SKILL.md directly for modifications
