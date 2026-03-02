---
name: rai-skill-create
description: >
  Guided skill creation with skill set management. Detects existing sets,
  offers to create/extend them, then walks through design and validation.

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

Guide creation of RaiSE skills through conversation and CLI. Detects skill sets, offers team-level management, produces ADR-040-compliant SKILL.md.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; ask at each stage
- **Ha**: Collapse steps when intent is clear; infer lifecycle
- **Ri**: Manage full skill sets; create families in one pass

## Context

**When to use:** Creating a skill, customizing a builtin for your team, or setting up a skill set.

**When to skip:** Editing an existing skill directly.

## Steps

### Step 0: Detect Skill Sets and Determine Target

```bash
ls -d .raise/skills/*/ 2>/dev/null || echo "No skill sets found"
```

**Sets exist** → ask: (1) create in existing set, (2) new set, (3) standalone in `.claude/skills/`

**No sets** → ask: (1) new skill set for your team, (2) standalone

**If "new set":**

1. Ask set name (e.g., "my-company")
2. Ask: *"Copy all builtins as base to customize?"*
3. If yes, for each builtin: `rai skill scaffold {name} --set {set-name} --from-builtin`
4. Confirm creation, then ask: *"Customize an existing skill or create a new one?"*

**If "customize builtin" in existing set:**

```bash
rai skill scaffold {builtin-name} --set {set-name} --from-builtin
```

Record `target_set` for Step 5.

<verification>
Target determined: standalone, existing set, or new set created.
</verification>

### Step 1: Understand Purpose

Ask: *"What does this skill do? What problem does it solve?"*

If customizing a builtin, read it first:

```bash
cat .raise/skills/{set}/{name}/SKILL.md   # or .claude/skills/{name}/SKILL.md
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
# Standalone
mkdir -p .claude/skills/{name}

# In a skill set
mkdir -p .raise/skills/{set}/{name}
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

- [ ] Skill sets detected before asking what to create
- [ ] Purpose before naming
- [ ] Name validated with CLI
- [ ] ADR-040: 7 sections, ≤150 lines
- [ ] No TODO placeholders
- [ ] Deploy reminder when in skill set

## References

- ADR-040: `dev/decisions/adr-040-skill-contract.md`
- CLI: `rai skill scaffold --help`, `rai init --skill-set --help`
