---
title: Create a Custom Skill
description: How to create a RaiSE skill — SKILL.md structure, frontmatter, naming conventions, and skill sets.
---

Skills are structured instructions that guide your AI assistant through repeatable workflows. Each skill is a SKILL.md file with YAML frontmatter and markdown sections.

## Skill Structure

A skill lives in its own directory under `.claude/skills/` (project-level) or is distributed from `src/rai_cli/skills_base/` (framework-level).

```
.claude/skills/
  my-custom-skill/
    SKILL.md
```

## Required Frontmatter

Every SKILL.md starts with YAML frontmatter:

```yaml
---
name: rai-my-skill
description: >
  One-paragraph description of what this skill does and when to use it.

license: MIT

metadata:
  raise.work_cycle: utility       # utility | epic | story | session
  raise.frequency: as-needed      # always | as-needed | once
  raise.fase: "0"                 # ShuHaRi phase
  raise.prerequisites: ""         # Required prior skills
  raise.next: ""                  # Suggested next skill
  raise.gate: ""                  # Gate to check before running
  raise.adaptable: "true"         # Can be customized per project
  raise.version: "2.2.3"          # Framework version
  raise.visibility: public        # public | private
---
```

## Required Sections

After frontmatter, include these markdown sections:

1. **Purpose** — What the skill does and why it exists
2. **Context** — When to use, when to skip, inputs needed, time boxing
3. **Steps** — Numbered steps with `<verification>` blocks after each
4. **Output** — What artifacts the skill produces
5. **Quality Checklist** — Verification criteria as a checkbox list

### Verification Blocks

Each step should end with a verification gate:

```markdown
### Step 1: Do the Thing

Instructions for this step.

<verification>
Expected outcome that confirms step completion.
</verification>

<if-blocked>
What to do if this step fails.
</if-blocked>
```

## Naming Conventions

Skill names follow `{domain}-{action}` pattern:
- `rai-story-start` — story domain, start action
- `rai-debug` — utility domain, single action
- `rai-discover-scan` — discovery domain, scan action

Validate a name before creating:

```bash
rai skill check-name my-skill-name
```

## Scaffold a Skill

Use the CLI to generate the skeleton:

```bash
rai skill scaffold my-custom-skill
```

This creates the directory and a SKILL.md template with all required sections.

## Skill Sets

Skill sets let teams customize which skills are active:

```bash
# List available skill sets
rai skill set list

# Create a custom set
rai skill set create my-team-set

# Compare sets
rai skill set diff default my-team-set
```

## Validate

Check that your skill meets structural requirements:

```bash
rai skill validate my-custom-skill
```

This verifies frontmatter fields, required sections, and naming conventions.
