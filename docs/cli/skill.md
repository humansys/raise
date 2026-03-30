---
title: rai skill
description: Manage RaiSE skills — list, validate, scaffold, sync, and skill sets.
---

Manage RaiSE skills. Skills are structured workflows (SKILL.md files) that guide AI agents through development lifecycle phases.

## `rai skill list`

List all skills in the skill directory. Shows skills grouped by lifecycle with version and description.

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai skill list
rai skill list --format json
```

---

## `rai skill validate`

Validate skill structure against the RaiSE schema. Checks frontmatter, required fields, sections, and naming conventions.

| Argument | Description |
|----------|-------------|
| `PATH` | Path to skill file or directory (optional — validates all if omitted) |

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
# Validate all skills
rai skill validate

# Validate specific skill
rai skill validate .claude/skills/rai-story-start/SKILL.md
```

**Exit codes:** 0 all valid, 1 validation errors found.

---

## `rai skill check-name`

Check a proposed skill name against naming conventions. Validates `{domain}-{action}` pattern, checks for conflicts with existing skills or CLI commands, and verifies the lifecycle domain.

| Argument | Description |
|----------|-------------|
| `NAME` | Proposed skill name (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai skill check-name story-validate
```

---

## `rai skill scaffold`

Create a new skill from template. Generates a `SKILL.md` file with proper structure.

| Argument | Description |
|----------|-------------|
| `NAME` | Skill name to create (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--lifecycle` | `-l` | Lifecycle: `session`, `epic`, `story`, `discovery`, `utility`, `meta`. Inferred from name if not set |
| `--after` | | Skill that should come before this one |
| `--before` | | Skill that should come after this one |
| `--set` | | Skill set to create in (creates in `.raise/skills/{set}/`) |
| `--from-builtin` | | Copy from deployed builtin skill as starting point (requires `--set`) |
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
# Create a new story skill
rai skill scaffold story-validate

# With lifecycle and ordering
rai skill scaffold story-validate --lifecycle story --after story-implement --before story-close

# Create in a skill set from a builtin
rai skill scaffold story-validate --set my-team --from-builtin
```

---

## `rai skill sync`

Check skill freshness against installed package version. Reports which skills are current, outdated, or have conflicts.

| Flag | Short | Description |
|------|-------|-------------|
| `--path` | `-p` | Project path |

```bash
rai skill sync
rai skill sync --path /path/to/project
```

**Exit codes:** 0 all current, 1 updates available.

---

## `rai skill set create`

Create a new skill set from builtins. Copies all builtin skills to `.raise/skills/<name>/` as a starting base for customization.

| Argument | Description |
|----------|-------------|
| `NAME` | Skill set name (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--empty` | | Create empty set (no builtins copied) |
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
# Create from builtins
rai skill set create my-team

# Create empty set
rai skill set create my-team --empty
```

---

## `rai skill set list`

List all skill sets in `.raise/skills/`.

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai skill set list
```

---

## `rai skill set diff`

Compare a skill set against builtins. Shows which skills are added, modified, or unchanged.

| Argument | Description |
|----------|-------------|
| `NAME` | Skill set name to compare (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--format` | `-f` | Output format: `human`, `json`. Default: `human` |

```bash
rai skill set diff my-team
```

**See also:** [`rai init --skill-set`](init.md/
