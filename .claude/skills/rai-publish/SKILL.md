---
name: rai-publish
description: >
  Guide the human through a structured release workflow with quality gates,
  version bumping, changelog management, and PyPI publishing via GitHub Actions.
disable-model-invocation: true

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

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, explain each gate and action
- **Ha**: Skip explanations, focus on decisions (bump type, changelog entries)
- **Ri**: Minimal prompts — present summary, confirm, execute

## Context

**When to use:** When ready to publish a new version to PyPI, verify release readiness, or create a release tag.

**Inputs:** Clean working tree (no uncommitted changes), passing quality gates.

## Steps

### Step 1: Review Changes Since Last Release

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
echo "Last release: $LAST_TAG"
[ "$LAST_TAG" != "none" ] && git log "$LAST_TAG"..HEAD --oneline || git log --oneline -20
```

Present a summary of what changed to help decide bump type.

### Step 2: Suggest Bump Type

| Change Type | Suggested Bump |
|-------------|---------------|
| Breaking changes | `major` |
| New features | `minor` |
| Bug fixes only | `patch` |
| Pre-release iteration | `alpha`, `beta`, or `rc` |
| Pre-release to stable | `release` |

Present suggestion and ask for confirmation.

### Step 3: Run Quality Gates

```bash
rai release check
```

If any gates fail, stop and help fix them before proceeding.

### Step 4: Sync Public Skills

```bash
python scripts/sync-skills.py
```

If changes, commit: `git commit -m "chore: sync public skills for distribution"`

### Step 5: Dry Run Release

```bash
rai release publish --bump {type} --dry-run
```

Present the plan. Ask for confirmation before executing.

### Step 6: Execute Release

```bash
rai release publish --bump {type}
```

Bumps version, updates CHANGELOG.md, creates commit + tag, pushes to origin.

### Step 7: Verify

Direct to GitHub Actions: `https://github.com/humansys/raise/actions`

## Output

| Item | Destination |
|------|-------------|
| Version bumped | `pyproject.toml`, `__init__.py` |
| Changelog updated | `CHANGELOG.md` |
| Release commit + tag | Git history |
| PyPI upload | Triggered via GitHub Actions |

## Quality Checklist

- [ ] All quality gates pass before release
- [ ] Public skills synced to distribution
- [ ] Dry run reviewed and confirmed by human
- [ ] NEVER publish directly to PyPI — GitHub Actions handles it
- [ ] NEVER skip gates without explicit human confirmation

## References

- CLI: `rai release check`, `rai release publish`
- GitHub Actions: `.github/workflows/release.yml`
- Sync script: `scripts/sync-skills.py`
