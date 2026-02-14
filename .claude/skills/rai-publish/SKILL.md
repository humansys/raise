---
name: rai-publish
description: >
  Guide the human through a structured release workflow with quality gates,
  version bumping, changelog management, and PyPI publishing via GitHub Actions.

license: MIT

metadata:
  raise.work_cycle: meta
  raise.frequency: as-needed
  raise.fase: "release"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Publish: Guided Release Workflow

## Purpose

Guide the human through a structured release workflow with quality gates, version bumping, changelog management, and PyPI publishing via GitHub Actions.

## Context

**When to use:**
- When ready to publish a new version to PyPI
- When you want to verify release readiness
- Before creating a release tag

**Inputs required:**
- Clean working tree (no uncommitted changes)
- Passing quality gates

**Output:**
- Version bumped in pyproject.toml and __init__.py
- CHANGELOG.md updated with versioned section
- Git commit + tag created
- Push triggers GitHub Actions for PyPI upload

## Steps

### Step 1: Review Changes Since Last Release

```bash
# Show last tag and changes since
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
echo "Last release: $LAST_TAG"

if [ "$LAST_TAG" != "none" ]; then
    git log "$LAST_TAG"..HEAD --oneline
else
    git log --oneline -20
fi
```

Present a summary of what changed. This helps the human decide the bump type.

### Step 2: Suggest Bump Type

Based on the changes, suggest a bump type:

| Change Type | Suggested Bump |
|-------------|---------------|
| Breaking changes | `major` |
| New features | `minor` |
| Bug fixes only | `patch` |
| Pre-release iteration | `alpha`, `beta`, or `rc` |
| Pre-release to stable | `release` |

Present suggestion and ask for confirmation:
> "Based on the changes, I suggest a **minor** bump (new features, no breaking changes). Agree?"

### Step 3: Run Quality Gates

```bash
rai publish check
```

If any gates fail, stop and help fix them before proceeding.

### Step 4: Sync Public Skills to Distribution

```bash
# Filter skills for PyPI distribution (exclude internal skills)
python scripts/sync-skills.py
```

This syncs only public skills from `.claude/skills/` to `src/rai_cli/skills_base/`, excluding internal tools (rai-framework-sync, rai-publish). Check the output confirms 22 public skills synced.

If changes were made, commit them:
```bash
git add src/rai_cli/skills_base/
git commit -m "chore: sync public skills for distribution"
```

### Step 5: Execute Release (Dry Run First)

```bash
# Show what will happen
rai publish release --bump {type} --dry-run
```

Present the plan. Ask for confirmation before executing.

### Step 6: Execute Release

```bash
rai publish release --bump {type}
```

This will:
1. Bump version in pyproject.toml and __init__.py
2. Update CHANGELOG.md (promote [Unreleased] to versioned section)
3. Create release commit
4. Create version tag
5. Push to origin (triggers GitHub Actions for PyPI upload)

### Step 7: Verify

```bash
# Check GitHub Actions
echo "Verify release at: https://github.com/humansys-io/raise-commons/actions"
```

## Notes

- **Never publishes directly to PyPI** — GitHub Actions handles that via Trusted Publishers
- The `release.yml` workflow triggers on `v*` tags
- Use `--skip-check` only in emergencies (requires explicit confirmation)
- `--dry-run` is always safe and shows the full plan

## References

- CLI: `rai publish check`, `rai publish release`
- GitHub Actions: `.github/workflows/release.yml`
- Research: `work/research/RES-PUBLISH-001/`
