---
name: rai-skill-create
description: Create a new skill through guided conversation. Use to add skills to the framework.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: meta
  raise.frequency: on-demand
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: internal
---

# Skill Create

## Purpose

Guide creation of a new RaiSE skill through conversation and CLI, producing a complete ADR-040-compliant SKILL.md — no TODO placeholders.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; ask at each stage
- **Ha**: Collapse steps when intent is clear; infer lifecycle
- **Ri**: Create skill families in a single pass

## Context

**When to use:** Creating a new skill or customizing a builtin for a skill set.

**When to skip:** Managing skill sets (use `/rai-skillset-manage`). Editing an existing skill directly.

**Inputs:** What the skill should do. Optionally: `--set` for skill set target.

## Steps

### Step 1: Understand Purpose

Ask: *"What does this skill do? What problem does it solve?"*

If customizing a builtin for a skill set, read it first:

```bash
cat .claude/skills/{name}/SKILL.md
```

<verification>Purpose statable in one sentence.</verification>

### Step 2: Derive and Validate Name

Pattern: `rai-{domain}-{action}` (framework) or `{team}-{action}` (team skills).

```bash
rai skill check-name {chosen-name}
```

<verification>`rai skill check-name` passes.</verification>

### Step 3: Determine Lifecycle Position

| Field | Options |
|-------|---------|
| `work_cycle` | `story` · `epic` · `discovery` · `session` · `utility` · `meta` |
| `frequency` | `per-story` · `per-epic` · `per-project` · `per-session` · `on-demand` |

Default: `utility`, `on-demand` if unclear.

<verification>Metadata fields set.</verification>

### Step 4: Discover CLI Tools and References

```bash
rai --help
rai {group} --help
rai skill list --format json
```

Read 2-3 reference skills with same `work_cycle`.

<verification>CLI tools known. References read.</verification>

### Step 5: Write SKILL.md

ADR-040 contract: 7 sections, ≤150 body lines. HITL review before writing.

```bash
# Standalone (default)
mkdir -p .claude/skills/{name}

# In a skill set
mkdir -p .raise/skills/{set}/{name}

# Customize builtin into a set
rai skill scaffold {name} --set {set} --from-builtin
```

<verification>No TODO placeholders.</verification>

### Step 6: Validate and Deploy

```bash
rai skill validate {path-to-SKILL.md}
```

If in a skill set, remind: *"To deploy: `rai init --skill-set {set}`"*

<verification>`rai skill validate` exits 0.</verification>

## Output

| Item | Destination |
|------|-------------|
| SKILL.md | `.claude/skills/{name}/` or `.raise/skills/{set}/{name}/` |
| Deploy hint | `rai init --skill-set {set}` (if in set) |

## Quality Checklist

- [ ] Purpose before naming
- [ ] Name validated with `rai skill check-name`
- [ ] ADR-040: 7 sections, ≤150 lines
- [ ] No TODO placeholders
- [ ] Deploy reminder when in skill set

## References

- ADR-040: `dev/decisions/adr-040-skill-contract.md`
- Skill sets: `/rai-skillset-manage`, `rai skill set --help`
- CLI: `rai skill scaffold --help`
