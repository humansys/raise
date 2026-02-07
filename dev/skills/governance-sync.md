# Governance Sync Skill

> **Purpose**: Promote artifacts from `work/` to `governance/` after gates pass

---

## Overview

This skill automates the promotion of work artifacts to governance status after they pass validation gates. It ensures the governance index stays in sync with actual artifacts.

## Trigger

- Manual invocation after gate passes
- Automatic trigger from gate success (future)

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `source_path` | string | Yes | Path to artifact in `work/` |
| `target_level` | enum | Yes | `solution` or `project` |
| `artifact_type` | enum | Yes | `vision`, `guardrails`, `design`, `decision` |
| `version` | semver | Yes | Version to assign |
| `project_name` | string | No | Required if level is `project` |

## Steps

### 1. Validate Source Artifact

```
- Verify source file exists in work/
- Verify gate has passed (check gate output or ask user)
- Validate artifact structure matches expected type
```

**Verification**: Source file exists and gate status is "passed"

> **Si no puedes continuar**: Gate not passed → Run gate first. File not found → Check path.

### 2. Determine Target Path

```
Solution level:
  work/proposals/vision.md → governance/vision.md
  work/proposals/adr-*.md → governance/decisions/adr-*.md

Project level:
  work/projects/{name}/vision.md → governance/vision.md
  work/projects/{name}/design.md → governance/design.md
```

**Verification**: Target path is determined and parent directory exists

### 3. Copy Artifact to Governance

```bash
cp work/{source} governance/{target}
```

**Verification**: File exists at target path with correct content

### 4. Update Governance Index

Add entry to `governance/index.yaml`:

```yaml
artifacts:
  - path: {relative_path}
    level: {solution|project}
    type: {artifact_type}
    version: {version}
    status: approved
    approved_date: {today}
```

**Verification**: Index contains new entry with correct metadata

### 5. Clean Up Work Directory (Optional)

```bash
# Mark as promoted or remove
mv work/{source} work/{source}.promoted
# OR
rm work/{source}
```

**Verification**: Source file handled according to policy

## Output

- Artifact copied to `governance/`
- `governance/index.yaml` updated
- Promotion logged

## Example Usage

```
/dev/governance-sync \
  --source work/proposals/adr-011.md \
  --level solution \
  --type decision \
  --version 1.0.0
```

---

*Internal tool for framework maintainers. Not part of injected framework.*
