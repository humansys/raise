---
title: Custom Skillsets
description: How to create language-specific skill overlays using the RaiSE skillset system.
---

Skillsets are collections of skill overlays that customize verification commands for a specific tech stack. Instead of editing base skills, you create minimal overlay files that replace only the sections that differ.

## How It Works

Base skills use a **manifest-first pattern**: they read tool commands from `.raise/manifest.yaml`, fall back to language detection, then to hardcoded defaults. Skillset overlays skip the detection chain entirely — they provide explicit commands for your stack.

```
Base skill (language-agnostic)
  └── reads manifest → detects language → defaults

Skillset overlay (stack-specific)
  └── explicit commands, no detection needed
```

## Creating a Skillset

### 1. Scaffold the directory

```bash
rai skill set create my-stack --empty
```

This creates `.raise/skills/my-stack/` — an empty skillset ready for overlays.

### 2. Add overlay files

Create a subdirectory for each skill you want to customize, with a `SKILL.md` inside:

```
.raise/skills/my-stack/
  rai-story-implement/SKILL.md
  rai-bugfix/SKILL.md
  rai-story-plan/SKILL.md
```

### 3. Write the overlay

Each overlay needs frontmatter identifying what it replaces, plus the replacement content:

```yaml
---
name: rai-story-implement
overlay: my-stack
replaces: Step 3 (Verify Task)
description: Stack-specific verification commands.
---
```

Then the replacement section with your explicit commands.

### 4. Verify

```bash
rai skill set list    # shows your skillset and skill count
rai skill set diff    # compares overlays against base skills
```

## Example: Python (raise-dev)

The `raise-dev` skillset provides Python-specific verification:

```markdown
## Verification Commands

After each RED-GREEN-REFACTOR cycle, run:

​```bash
# Tests
uv run pytest --tb=short -x

# Lint
uv run ruff check

# Type check
uv run pyright
​```
```

## Example: TypeScript (raise-dev-ts)

The `raise-dev-ts` skillset demonstrates the same pattern for TypeScript:

```markdown
## Verification Commands

After each RED-GREEN-REFACTOR cycle, run:

​```bash
# Tests
npx vitest run

# Lint
npx eslint src/

# Type check
npx tsc --noEmit
​```
```

## Gate Configuration

Gates (test, lint, type check, coverage) also read from the manifest. Configure them in `.raise/manifest.yaml`:

```yaml
project:
  project_type: python          # or typescript, go, etc.
  test_command: "uv run pytest --tb=short"
  lint_command: "uv run ruff check"
  type_check_command: "uv run pyright"
```

When manifest commands are set, all gates and manifest-aware skills use them automatically — no skillset overlay needed for basic configuration. Overlays are for when you want to provide additional context beyond just the command (e.g., TDD workflow guidance, error handling instructions).

## When to Use What

| Need | Solution |
|------|----------|
| Change test/lint/type commands | Set `project.*_command` in `manifest.yaml` |
| Stack-specific workflow guidance | Create a skillset with overlays |
| Team conventions and patterns | Skillset + custom skills |

## Available Skillsets

List all skillsets in your project:

```bash
rai skill set list
```

Compare an overlay against its base skill:

```bash
rai skill set diff
```
