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
  raise.version: "2.0.0"
  raise.visibility: internal
---

# Skill Create

## Purpose

Guide the creation of a new RaiSE skill through conversation and CLI composition, producing a complete ADR-040-compliant SKILL.md with real content — no TODO placeholders.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps sequentially; ask explicit questions at each stage
- **Ha**: Collapse steps when user provides detailed upfront intent; infer lifecycle metadata when domain is clear
- **Ri**: Create skill families in a single pass; propose decomposition when scope is too broad

## Context

**When to use:** Creating a new skill or converting an ad-hoc workflow into a repeatable process.

**When to skip:** Modifying an existing skill (edit SKILL.md directly). Writing CLI commands in `src/`.

**Inputs:** What the skill should do. Optionally: lifecycle position.

## Steps

### Step 1: Understand Purpose

Ask: *"What does this skill do? What problem does it solve and when would someone reach for it?"*

Extract: **What** (core action), **Why** (problem solved), **When** (trigger).

If scope covers multiple distinct workflows: propose decomposition into 2-3 focused skills.

<verification>
Purpose statable in one sentence.
</verification>

### Step 2: Derive and Validate Name

Naming pattern: `rai-{domain}-{action}`. Propose 2-3 candidates, then validate:

```bash
rai skill check-name {chosen-name}
```

Known domains: `debug`, `discover`, `docs`, `epic`, `framework`, `project`, `research`, `session`, `skill`, `story`. If domain is new, confirm intent.

<verification>
`rai skill check-name` passes with no errors.
</verification>

### Step 3: Determine Lifecycle Position

| Metadata | Options |
|----------|---------|
| `work_cycle` | `story` · `epic` · `discovery` · `session` · `utility` · `meta` |
| `frequency` | `per-story` · `per-epic` · `per-project` · `per-session` · `as-needed` · `on-demand` |
| `fase` | Story: 3–8 · Epic: 2–4 · Discovery: 1–5 · Utility/meta: `"0"` |
| `visibility` | `public` (distributed with rai) · `internal` (project-specific) |

If lifecycle is unclear: default to `utility`, `as-needed`, `"0"`. Adjust after.

<verification>
All metadata fields have values.
</verification>

### Step 4: Discover CLI Tools and Reference Skills

Drill into groups relevant to the skill's domain:

```bash
rai --help                            # all command groups
rai {group} --help                    # subcommands (groups related to work_cycle)
rai {group} {subcommand} --help       # flags (commands to include in skill steps)
```

List skills and read 2-3 with the same `work_cycle` or adjacent lifecycle position:

```bash
rai skill list --format json
```

Classify pattern: pure inference (0% CLI) · hybrid (20–50%) · CLI-heavy (50–70%).

<verification>
CLI tools known. 2-3 reference skills read. Pattern type determined.
</verification>

### Step 5: Design and Write SKILL.md

Infer RaiSE integrations from lifecycle metadata — present rationale, don't ask:

| Integration | Include when | Command |
|-------------|-------------|---------|
| Telemetry start/end | `work_cycle` is `story` or `epic` | `rai signal emit-work` |
| Context loading | skill queries prior learnings | `rai graph query` |
| Architectural context | skill modifies specific modules | `rai graph context mod-{name}` |
| Pattern persistence | skill produces learnings | `rai pattern add` |
| HITL checkpoint | always | pause after analysis, before writes |

Write using ADR-040 contract (7 sections, ≤150 body lines). Present design summary for HITL review before writing.

**Target directory** depends on whether creating for a skill set:
- Default: `.claude/skills/{name}/SKILL.md`
- With `--set`: `.raise/skills/{set}/{name}/SKILL.md`
- Customize builtin: `rai skill scaffold {name} --set {set} --from-builtin`

```bash
# Default (no skill set)
mkdir -p .claude/skills/{name}
# Write .claude/skills/{name}/SKILL.md using Write tool

# With skill set
mkdir -p .raise/skills/{set}/{name}
# Write .raise/skills/{set}/{name}/SKILL.md using Write tool
```

<verification>
No TODO placeholders. CLI commands verified against --help output. Verification in every step.
</verification>

<if-blocked>
Write fails → run `mkdir -p .claude/skills/{name}` first.
</if-blocked>

### Step 6: Validate, Index, and Present

```bash
rai skill validate .claude/skills/{name}/SKILL.md
rai graph build
rai graph query "{name}" --types skill --format compact
```

<verification>
`rai skill validate` exits 0. Skill appears in graph query. Present: name, path, lifecycle, steps, status.
</verification>

## Output

| Item | Destination |
|------|-------------|
| SKILL.md | `.claude/skills/{name}/SKILL.md` (default) or `.raise/skills/{set}/{name}/SKILL.md` (with --set) |
| Validation | `rai skill validate` passes |
| Graph index | `rai graph build` run — skill queryable |

## Quality Checklist

- [ ] Purpose statable in one sentence before naming
- [ ] Name validated with `rai skill check-name` before writing
- [ ] 2-3 reference skills read for domain patterns
- [ ] RaiSE integrations inferred from lifecycle metadata (not asked)
- [ ] ADR-040 contract followed: 7 sections, ≤150 body lines
- [ ] Graph indexed after writing (`rai graph build`)
- [ ] NEVER leave TODO placeholders in generated SKILL.md
- [ ] NEVER hardcode CLI commands — discover via `rai --help` at creation time

## References

- Contract: `src/rai_cli/skills_base/contract-template.md`
- Preamble: `src/rai_cli/skills_base/preamble.md`
- ADR-040: `dev/decisions/adr-040-skill-contract.md`
- Naming: PAT-E-216 · Auto-discovery: PAT-E-264
