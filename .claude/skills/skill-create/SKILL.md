---
name: skill-create
description: >
  Create new RaiSE skills with proper framework integration, ontological
  consistency, and awareness of the toolkit. Use when adding new workflow
  automation to the framework.

license: MIT

metadata:
  raise.work_cycle: framework
  raise.frequency: as-needed
  raise.fase: "meta"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
---

# Create: RaiSE Skill

## Purpose

Create new RaiSE skills with full framework integration. Skills are AI-executed process guides that leverage the RaiSE toolkit, follow ontological principles, and integrate with memory and telemetry.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps. Use templates. Check ontology patterns.

**Ha (破)**: Adapt templates for domain. Skip redundant checks for familiar patterns.

**Ri (離)**: Create skill families with shared abstractions. Design new workflow patterns.

## Context

**When to use:**
- Adding new workflow automation
- Creating domain-specific process guides
- Extending the skill ecosystem

**When to skip:**
- One-off tasks (just do them)
- CLI-only features (no AI orchestration needed)
- Existing skill covers the need

**Inputs required:**
- Skill purpose and name
- Which lifecycle it belongs to (session/epic/feature/discovery/utility)
- Key steps to accomplish

**Output:**
- Complete SKILL.md with frontmatter
- Telemetry hook configured
- Registered in skill index

## Framework Assets (Reference)

### CLI Toolkit

Skills can invoke these deterministic tools:

```
raise
├── init                    # Project initialization
├── session                 # Workflow lifecycle
│   ├── start               # Begin session
│   └── close               # End session
├── memory                  # All persistent knowledge
│   ├── query               # Query concepts
│   ├── build               # Rebuild index
│   ├── add-pattern         # Store learned pattern
│   ├── add-calibration     # Store estimation data
│   ├── add-session         # Store session record
│   ├── emit-work           # Emit lifecycle event
│   ├── emit-session        # Emit session event
│   └── emit-calibration    # Emit calibration event
├── skill                   # Skill management
│   ├── list                # List all skills
│   ├── validate            # Validate skill structure
│   ├── check-name          # Check naming conventions
│   └── scaffold            # Create new skill from template
├── discover                # Codebase analysis
│   ├── scan                # Extract symbols
│   ├── build               # Build graph
│   └── drift               # Check drift
└── profile                 # Developer identity
    └── show                # Display profile
```

### Skill Ecosystem

Existing skills that new skills can reference or complement:

| Lifecycle | Skills |
|-----------|--------|
| Session | `session-start` → `session-close` |
| Epic | `epic-start` → `epic-design` → `epic-plan` → `epic-close` |
| Feature | `story-start` → `story-design` → `story-plan` → `story-implement` → `story-review` → `story-close` |
| Discovery | `discover-start` → `discover-scan` → `discover-validate` → `discover-document` |
| Utility | `research`, `debug`, `framework-sync` |
| Meta | `skill-create` (this skill) |

### Directory Structure

```
.raise/                     # Framework engine
├── scripts/                # Hook scripts
│   └── log-skill-complete.sh
├── rai/
│   ├── memory/             # Patterns, calibration, sessions
│   ├── telemetry/          # Signals
│   └── identity/           # Rai's identity docs

.claude/
└── skills/                 # Skill definitions
    └── {skill-name}/
        └── SKILL.md

work/                       # Active work
└── epics/                  # Epic/story scopes

framework/                  # Public framework docs
└── reference/              # Constitution, glossary
```

### Ontology Patterns (Apply These)

Query memory for details: `raise memory query "ontology cli design"`

| Pattern | Principle |
|---------|-----------|
| PAT-130 | **Conceptual Clarity:** One concept, one location |
| PAT-131 | **Taxonomic Consistency:** Natural hierarchies |
| PAT-132 | **Naming Alignment:** Skill name = CLI name if both exist |
| PAT-133 | **Minimal Commitment:** No empty structures |
| PAT-134 | **Domain-Centric:** Organize by domain, not layer |
| PAT-135 | **Orthogonality:** Independent concepts, independent modules |
| PAT-136 | **Audit Checklist:** Validate before shipping |

## Steps

### Step 1: Define Skill Identity

Answer these questions:

1. **Name:** What's the `{domain}-{action}` pattern?
   - Examples: `session-close`, `story-plan`, `discover-scan`

2. **Lifecycle:** Which lifecycle does it belong to?
   - Session / Epic / Feature / Discovery / Utility / Meta

3. **Position:** Where in the lifecycle?
   - What skill comes before? (`prerequisites`)
   - What skill comes after? (`next`)

4. **Purpose:** One sentence describing what it does.

**Verify naming with CLI:**

```bash
# Check name follows pattern, no conflicts, known lifecycle
raise skill check-name {skill-name}
```

This validates:
- ✓ Follows `{domain}-{action}` pattern
- ✓ No conflict with existing skills
- ✓ No CLI command conflict (PAT-132)
- ✓ Domain is a known lifecycle

**Verification:** `raise skill check-name` returns valid.

### Step 2: Check Ontology Compliance

Before creating, verify against patterns:

```bash
# Query ontology patterns
raise memory query "ontology naming" --types pattern --limit 5
```

**Checklist (PAT-136):**

- [ ] **Conceptual Clarity:** Does this concept already exist elsewhere?
- [ ] **Taxonomic Consistency:** Is the domain correct for this skill?
- [ ] **Naming Alignment:** If CLI exists, names match?
- [ ] **Minimal Commitment:** Is this skill necessary? Could existing skill cover it?
- [ ] **Domain-Centric:** Named for what user does, not implementation?

**Verification:** All checklist items addressed.

### Step 3: Scaffold the Skill

Use the CLI to create the skill with proper structure:

```bash
# Create skill with inferred lifecycle
raise skill scaffold {skill-name}

# Or specify lifecycle and positioning explicitly
raise skill scaffold {skill-name} --lifecycle {lifecycle} --after {previous-skill} --before {next-skill}
```

This creates:
- `.claude/skills/{skill-name}/` directory
- `SKILL.md` with valid frontmatter, sections, and telemetry hook

**Verification:** Skill directory and SKILL.md created.

### Step 4: Customize SKILL.md

Edit the scaffolded SKILL.md to add:
- Description of what the skill does
- Context (when to use, when to skip, inputs, outputs)
- Detailed steps with verification criteria
- Output table

Reference this template for structure:

```markdown
---
name: {skill-name}
description: >
  {One to three sentence description of what the skill does and when to use it.}

license: MIT

metadata:
  raise.work_cycle: {session|epic|story|discovery|utility|meta}
  raise.frequency: {per-session|per-epic|per-story|as-needed}
  raise.fase: "{number or 'meta'}"
  raise.prerequisites: "{previous-skill or empty}"
  raise.next: "{next-skill or empty}"
  raise.gate: "{validation-gate or empty}"
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# {Action}: {Domain}

## Purpose

{What this skill accomplishes. One paragraph.}

## Mastery Levels (ShuHaRi)

**Shu (守)**: {Beginner behavior — follow all steps}

**Ha (破)**: {Intermediate — which steps can be adapted}

**Ri (離)**: {Expert — create variations}

## Context

**When to use:**
- {Trigger condition 1}
- {Trigger condition 2}

**When to skip:**
- {Skip condition 1}
- {Skip condition 2}

**Inputs required:**
- {Required input 1}
- {Required input 2}

**Output:**
- {Artifact 1}
- {Artifact 2}

## Steps

### Step 1: {Action}

{Description of what to do.}

```bash
# CLI command if applicable
raise {command}
```

**Verification:** {How to know this step succeeded.}

> **If you can't continue:** {Recovery action.}

### Step 2: {Action}

{Repeat pattern...}

## Output

| Item | Destination |
|------|-------------|
| {Output 1} | {Where it goes} |
| {Output 2} | {Where it goes} |

## Notes

{Any additional guidance, patterns, or references.}

## References

- Previous: `/{previous-skill}`
- Next: `/{next-skill}`
- Related: `{other relevant skills or docs}`
```

**Verification:** SKILL.md created with all sections.

### Step 5: Validate Skill Structure

Use the CLI to validate the skill:

```bash
raise skill validate .claude/skills/{skill-name}/
```

This checks:
- ✓ Frontmatter is valid YAML
- ✓ Required fields present (name, description, metadata)
- ✓ Required sections exist (Purpose, Context, Steps, Output)
- ✓ Name follows `{domain}-{action}` pattern
- ⚠ Hook script paths (warns if not found)

**Verification:** `raise skill validate` returns no errors.

### Step 6: Update Skill Catalog

Update the skill listing in relevant documentation:

1. **MEMORY.md** — If this skill is fundamental to workflow
2. **CLAUDE.md** — If this skill should appear in system reminder
3. **Session hooks** — If auto-invoked by Anthropic settings

```bash
# Check current skill count in session-start
grep -c "^-" .claude/skills/session-start/SKILL.md | head -1
```

**Verification:** Skill cataloged where appropriate.

### Step 7: Test the Skill

Invoke the skill to verify it works:

```
/{skill-name}
```

**Check:**
- Does the skill load correctly?
- Are all steps executable?
- Does the hook fire on completion?
- Does telemetry emit?

**Verification:** Skill executes successfully.

### Step 8: Add Pattern to Memory

Record this skill creation as a pattern if it introduces new workflow:

```bash
raise memory add-pattern "{Brief description of the pattern}" -c "{context tags}" -t process --from "{feature-id}"
```

**Verification:** Pattern recorded (optional — only for novel patterns).

## Output

| Item | Destination |
|------|-------------|
| SKILL.md | `.claude/skills/{skill-name}/SKILL.md` |
| Hook config | Embedded in SKILL.md frontmatter |
| Catalog update | MEMORY.md and/or CLAUDE.md |
| Telemetry | `.raise/rai/personal/telemetry/signals.jsonl` |

## Skill Naming Conventions

| Pattern | Examples | Use For |
|---------|----------|---------|
| `{domain}-start` | `session-start`, `epic-start` | Begin lifecycle |
| `{domain}-close` | `session-close`, `story-close` | End lifecycle |
| `{domain}-{phase}` | `story-design`, `story-plan` | Lifecycle phases |
| `{domain}-{action}` | `discover-scan`, `discover-validate` | Domain operations |
| `{verb}` | `research`, `debug` | Standalone utilities |

## Common Anti-patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| `do-thing` (verb-noun) | Inconsistent with `{domain}-{action}` | Use `thing-do` |
| `the-skill` | Generic naming | Be specific: `feature-validate` |
| Duplicate concept | Overlaps existing skill | Extend existing or merge |
| No lifecycle position | Orphan skill | Document prerequisites/next |
| No telemetry hook | Invisible completion | Add Stop hook |

## Notes

### Why Skills Over CLI Commands

Skills are for AI-executed processes with judgment. CLI is for deterministic operations.

| Skill | CLI |
|-------|-----|
| Multi-step with decisions | Single operation |
| Requires context | Context-free |
| Adapts to situation | Same behavior always |
| Produces artifacts + judgment | Produces data |

### Extending Existing Skills

Before creating new skill, check if you can:
1. Add a step to existing skill
2. Create a variation (skill-for-X)
3. Compose existing skills

New skill is warranted when the workflow is distinct enough to warrant separate invocation.

## References

- Skill structure: `.claude/skills/story-start/SKILL.md` (template example)
- Hook scripts: `.raise/scripts/`
- Ontology patterns: `raise memory query "ontology"`
- CLI toolkit: `raise --help`
