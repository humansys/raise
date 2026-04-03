---
name: rai-skillset-manage
description: Manage skill sets via CLI. Use to create, compare, or customize skill sets.

license: MIT

metadata:
  raise.work_cycle: meta
  raise.frequency: on-demand
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-skill-create"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Skillset Manage

## Purpose

Guide teams through skill set lifecycle — create, inspect, compare, and maintain — using `rai skill set` CLI for all observable operations.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; explain each CLI output
- **Ha**: Skip detection when user states intent; batch operations
- **Ri**: Proactive drift detection; suggest set updates after raise-cli upgrades

## Context

**When to use:** Setting up a team skill set, checking what changed after an upgrade, or onboarding a new team member to existing sets.

**When to skip:** Creating/editing individual skills (use `/rai-skill-create`).

**Inputs:** Optional: skill set name, intent (create/inspect/diff).

## Steps

### Step 1: Detect Existing Skill Sets

```bash
rai skill set list --format json
```

**If sets exist**, present them and ask:

> "Found skill sets: [{names}]. What would you like to do?
> 1. Create a new skill set
> 2. Inspect/diff an existing set
> 3. Add or customize a skill in a set (→ /rai-skill-create)"

**If no sets**, propose creation:

> "No skill sets yet. A skill set lets your team customize RaiSE skills.
> Want to create one? I'll copy all builtins as a starting base."

<verification>
Context established. User intent identified.
</verification>

### Step 2: Execute Action

**Create new set:**

1. Ask for set name (suggest: team name, project name, or role — e.g., `backend-team`)
2. Ask: *"Copy builtins as base, or start empty?"*
3. Execute:

```bash
# Full set from builtins (recommended)
rai skill set create {name}

# Or empty set
rai skill set create {name} --empty
```

4. Show result and next steps.

**Inspect/diff existing set:**

```bash
rai skill set diff {name}
```

Present summary: *"{N} added, {M} modified, {K} unchanged vs builtins."*

If modified skills exist, offer: *"Want to review the changes? Or customize another skill?"*

<verification>
CLI command executed successfully. User sees output.
</verification>

### Step 3: Guide Next Steps

After creation or inspection, present the workflow:

> **Your skill set is ready.** Here's the workflow:
> 1. Customize skills: edit `.raise/skills/{set}/{name}/SKILL.md` or use `/rai-skill-create --set {set}`
> 2. Add new skills: `/rai-skill-create --set {set}`
> 3. Deploy to IDE: `rai init --skill-set {set}`
> 4. Check drift after upgrades: `rai skill set diff {set}`
> 5. Commit and share: `git add .raise/skills/{set}/ && git commit`

<verification>
User understands the full workflow. Next action is clear.
</verification>

### Step 4: Deploy (Optional)

If user wants to deploy immediately:

```bash
rai init --skill-set {name}
```

Confirm: *"Deployed {set} to .claude/skills/. Your team's skills are now active."*

<verification>
Deployment successful. Skills active in IDE.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Skill set directory | `.raise/skills/{name}/` |
| Deployment | `.claude/skills/` (via `rai init --skill-set`) |
| Next | `/rai-skill-create --set {name}` for customization |

## Quality Checklist

- [ ] Always run `rai skill set list` before proposing actions
- [ ] All mutations via `rai skill set` CLI (never mkdir/cp directly)
- [ ] Present diff summary after create (shows all unchanged = clean copy)
- [ ] Remind about `rai init --skill-set` for deployment
- [ ] Remind about git commit for team sharing

## References

- CLI: `rai skill set create/list/diff --help`
- Skill creation: `/rai-skill-create --set {name}`
- Deployment: `rai init --skill-set {name}`
- Research: `work/research/skill-set-patterns/`
