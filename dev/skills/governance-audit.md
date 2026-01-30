# Governance Audit Skill

> **Purpose**: Detect drift between governance artifacts and codebase reality

---

## Overview

This skill performs periodic or on-demand audits to detect "golden data drift" - when governance claims no longer reflect the actual state of the codebase or project.

## Trigger

- Manual invocation (recommended: weekly or before major releases)
- CI/CD pipeline (optional)

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `scope` | enum | No | `full`, `solution`, `project`, `decisions` (default: `full`) |
| `fix` | boolean | No | Attempt automatic fixes (default: `false`) |
| `report_path` | string | No | Path for audit report (default: stdout) |

## Audit Checks

### 1. Index Consistency

Verify `governance/index.yaml` matches actual files:

```
For each entry in index:
  - Does file exist at path?
  - Does version in file match index?
  - Is status accurate?

For each file in governance/:
  - Is it listed in index?
```

**Output**: List of orphaned files, missing entries, version mismatches

### 2. Reference Integrity

Verify relationships are valid:

```
For each relationship in index:
  - Does 'from' artifact exist?
  - Does 'to' artifact exist?
  - Is relationship type still accurate?
```

**Output**: List of broken references

### 3. Governance-to-Code Alignment

Verify governance claims match codebase:

```
For guardrails.md:
  - Are claimed technologies actually used?
  - Are claimed patterns actually implemented?

For solution/vision.md:
  - Does codebase structure match claimed architecture?
  - Are integrations still accurate?
```

**Output**: List of claim-vs-reality mismatches

### 4. Staleness Detection

Identify potentially stale artifacts:

```
For each artifact:
  - When was it last modified?
  - Has related code changed significantly since?
  - Are there TODOs or FIXMEs referencing it?
```

**Output**: List of potentially stale artifacts with evidence

## Steps

### 1. Load Governance Index

```
- Read governance/index.yaml
- Parse artifacts and relationships
```

**Verification**: Index loaded successfully

> **Si no puedes continuar**: Index malformed → Run index repair first.

### 2. Run Audit Checks

```
- Execute each check type based on scope
- Collect findings
- Categorize by severity: error, warning, info
```

**Verification**: All checks completed

### 3. Generate Report

```markdown
# Governance Audit Report
Date: {date}
Scope: {scope}

## Summary
- Errors: {count}
- Warnings: {count}
- Info: {count}

## Findings

### Errors
{list of errors}

### Warnings
{list of warnings}

### Recommendations
{prioritized list of actions}
```

**Verification**: Report generated

### 4. Apply Fixes (if --fix)

```
- Update index for simple issues (missing entries, version mismatches)
- Flag complex issues for manual review
```

**Verification**: Fixes applied, complex issues flagged

## Output

- Audit report (stdout or file)
- Updated index (if --fix)
- Exit code: 0 (clean), 1 (warnings), 2 (errors)

## Example Usage

```bash
# Full audit, report to stdout
/dev/governance-audit

# Solution-only audit with fixes
/dev/governance-audit --scope solution --fix

# CI/CD integration
/dev/governance-audit --report-path audit-report.md
```

---

*Internal tool for framework maintainers. Not part of injected framework.*
