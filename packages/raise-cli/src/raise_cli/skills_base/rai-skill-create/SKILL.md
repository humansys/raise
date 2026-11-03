---
name: rai-skill-create
description: Create a new skill through guided conversation. Use to add a skill to your project or to the framework.
model: sonnet

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
  raise.visibility: public
---

# Skill Create

## Purpose

Guide creation of a new RaiSE skill through conversation and CLI, producing a complete, contract-compliant SKILL.md — no TODO placeholders.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; ask at each stage
- **Ha**: Collapse steps when intent is clear; infer lifecycle
- **Ri**: Create skill families in a single pass

## Context

**When to use:** Creating a new skill or customizing a builtin for a skill set.

**When to skip:** Managing skill sets (use `/rai-skillset-manage`). Editing an existing skill directly.

**Inputs:** What the skill should do. Optionally: `--set` for skill set target.

**Where am I?** Glob `packages/raise-cli/src/raise_cli/skills_base/__init__.py`:

| Result | Meaning |
|--------|---------|
| Present | Framework repo (raise-commons): `rai-` names, lifecycle table applies |
| Absent | Team project: `{team}-{action}` names, lifecycle set silently |

## Steps

### Step 1: Understand Purpose

Ask: *"What does this skill do? What problem does it solve?"*

If customizing a builtin for a skill set, read `.claude/skills/{name}/SKILL.md` first (Read tool — `Bash(rai:*)` does not cover `cat`).

<verification>Purpose statable in one sentence.</verification>

### Step 2: Derive and Validate Name

Team project: `{team}-{action}` (e.g. `kg-design`); never propose `rai-`. Framework repo: `rai-{domain}-{action}`.

```bash
rai skill check-name {chosen-name}
```

`rai skill check-name` prints `WARN Domain is not a standard lifecycle` for any team domain. Expected: exit 0 is the pass.

<verification>`rai skill check-name` exits 0.</verification>

### Step 3: Determine Lifecycle Position

| Field | Options |
|-------|---------|
| `work_cycle` | `story` · `epic` · `discovery` · `session` · `utility` · `meta` |
| `frequency` | `per-story` · `per-epic` · `per-project` · `per-session` · `on-demand` |

Team project: `work_cycle: utility`, `frequency: on-demand`, set without asking (what `rai skill scaffold` infers). Framework repo: choose from the table; default `utility`, `on-demand` if unclear.

<verification>Metadata fields set.</verification>

### Step 4: Leverage RaiSE

Discover what the CLI offers:

```bash
rai --help
rai {group} --help
rai skill list --format json
```

From the purpose in Step 1, propose as defaults the capabilities that fit:

| If the skill... | Propose |
|-----------------|---------|
| reads code or docs for context | `rai graph query "{topic}"` before grep or find |
| produces a document | `rai docs publish` |
| learns something reusable | `rai pattern add` |
| needs the work item's context | `rai graph query "{KEY}" --types backlog` — the graph, not a live tracker call |

A skill never changes a work item's status: the workflow engine owns the work item's lifecycle. The skill reads context and produces artifacts.

Check usage before wiring any of them in:

```bash
rai docs publish --help
rai pattern add --help
```

Add `"Bash(rai:*)"` to the skill's `allowed-tools`. Read 1-2 skills in `.claude/skills/` with the same `work_cycle` as exemplars.

<verification>Fitting capabilities proposed and confirmed. Exemplars read.</verification>

### Step 5: Write SKILL.md

Contract: 7 sections, ≤150 body lines. HITL review before writing.

**CLI command convention:** Commands that rai doctor should validate go in ` ```bash ` blocks only. Inline backtick is for human-readable prose and is **not** validated.

```bash
# Team project (default): generates the 7-section contract, then fill it
rai skill scaffold {name}

# Manual standalone
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
- [ ] 7 sections, ≤150 lines
- [ ] RaiSE capabilities proposed (Step 4)
- [ ] No TODO placeholders
- [ ] Deploy reminder when in skill set

## References

- Contract: `rai skill scaffold` generates it, `rai skill validate` enforces it (ADR-040; in raise-commons: `governance/adrs/v1/adr-040-skill-contract.md`)
- Skill sets: `/rai-skillset-manage`, `rai skill set --help`
- CLI: `rai skill scaffold --help`
